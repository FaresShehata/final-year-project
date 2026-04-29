#!/usr/bin/env python3
"""Generate initial seed inputs directly with the LLM.

This replaces base generator modules for the elfuzz gen flow. It generates
raw-format inputs (e.g., JSON/XML) and writes them under:
  <rundir>/initial/seeds/seed_XXXX/input_0000.<ext>

Usage: python3 scripts/init_generate_llm_seeds.py <rundir> [--num N]
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from elmconfig import ELMFuzzConfig
from llm_provider import create_provider, LLMProvider


@dataclass(frozen=True)
class FormatInfo:
    label: str
    extension: str
    prompt: str


def _extract_generator_name(module_path: Path) -> Optional[str]:
    try:
        text = module_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    match = re.search(r"^\s*def\s+(generate_[A-Za-z0-9_]+)\s*\(", text, re.MULTILINE)
    if match:
        return match.group(1)
    return None


def _infer_format(func_name: str) -> FormatInfo:
    name = func_name.lower()
    if "json" in name:
        return FormatInfo("JSON", ".json", _prompt_for("JSON document"))
    if "xml" in name:
        return FormatInfo("XML", ".xml", _prompt_for("XML document"))
    if "svg" in name:
        return FormatInfo("SVG", ".svg", _prompt_for("SVG document"))
    if "smtlib" in name or "smt2" in name or "smt" in name:
        return FormatInfo("SMT-LIB", ".smt2", _prompt_for("SMT-LIB v2 script"))
    if "regex" in name or "re2" in name:
        return FormatInfo("regex", ".re", _prompt_for("regular expression"))
    if "sqlite" in name or "sql" in name:
        return FormatInfo("SQL", ".sql", _prompt_for("SQL script"))
    if "python" in name or "py" in name:
        return FormatInfo("Python", ".py", _prompt_for("Python 3 program"))
    if "png" in name or "image" in name:
        return FormatInfo("PNG", ".png", _prompt_for("PNG file"))
    return FormatInfo("data", ".dat", _prompt_for("data file"))


def _prompt_for(kind: str) -> str:
    return (
        f"Generate a valid {kind}. "
        "Output only the raw file contents with no markdown, no code fences, and no explanation. "
        "Do not include any preamble or meta text. "
        "output:\n"
    )


def _seed_dir_name(fmt: FormatInfo) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", fmt.label.lower()).strip("_")
    return f"seed_{slug or 'seed'}"


def _strip_preamble(text: str) -> str:
    lines = text.splitlines()
    while lines:
        first = lines[0].strip().lower()
        if first.startswith("the output should be") or first.startswith("output should be"):
            lines.pop(0)
            continue
        break
    return "\n".join(lines).lstrip()


def _trim_to_format_start(text: str, fmt: FormatInfo) -> str:
    if not text:
        return text
    if fmt.extension == ".json":
        start_candidates = [pos for pos in (text.find("{"), text.find("[")) if pos != -1]
        if start_candidates:
            return text[min(start_candidates) :].lstrip()
    if fmt.extension in {".xml", ".svg"}:
        start = text.find("<")
        if start != -1:
            return text[start:].lstrip()
    if fmt.extension == ".smt2":
        start = text.find("(")
        if start != -1:
            return text[start:].lstrip()
    return text.lstrip()


def _sanitize_output(text: str, fmt: FormatInfo) -> str:
    cleaned = text.strip()
    if "```" in cleaned:
        match = re.search(r"```(?:\w+)?\s*\n(.*?)```", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()
        else:
            cleaned = cleaned.replace("```", "").strip()
    cleaned = _strip_preamble(cleaned)
    cleaned = _trim_to_format_start(cleaned, fmt)
    return cleaned


def _load_seed_modules(args) -> Iterable[Path]:
    seeds = args.run.seeds or []
    for seed in seeds:
        yield Path(seed)


def _get_endpoint(args, model: str) -> Optional[str]:
    if os.environ.get("ACCESS_INFO"):
        return os.environ.get("ACCESS_INFO")
    endpoints = args.model.endpoints
    if isinstance(endpoints, dict):
        return endpoints.get(model)
    return None


def _generation_params(config: ELMFuzzConfig) -> tuple[float, int, float]:
    conf = config.config or {}
    gen = conf.get("cli", {}).get("geninputs_group_parallel", {}).get("gen", {})
    temperature = float(gen.get("temperature", 0.2))
    max_new_tokens = int(gen.get("max_new_tokens", 2048))
    repetition_penalty = float(gen.get("repetition_penalty", 1.1))
    return temperature, max_new_tokens, repetition_penalty


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate initial LLM seeds for elfuzz gen.")
    parser.add_argument("rundir", type=str, help="ELMFuzz run directory (preset/<benchmark>)")
    parser.add_argument(
        "--num",
        type=int,
        default=int(os.environ.get("ELMFUZZ_INIT_SEED_COUNT", "20")),
        help="Number of initial seeds to generate",
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=["huggingface", "copilot"],
        default=os.environ.get("ELMFUZZ_LLM_BACKEND", "huggingface"),
        help="LLM backend to use",
    )
    parser.add_argument("--model", type=str, default=None, help="Override model name for seed generation")
    parser.add_argument("--max-retries", type=int, default=2, help="Retries per seed if output is empty")
    cli_args = parser.parse_args()

    os.environ.setdefault("ELMFUZZ_RUNDIR", cli_args.rundir)

    config = ELMFuzzConfig()
    args = config.parse_args([])

    model_names = args.model.names or []
    if not model_names:
        print("No model names configured; cannot generate seeds", file=sys.stderr)
        return 2

    model = cli_args.model or model_names[0]
    endpoint = None
    if cli_args.backend == "huggingface":
        endpoint = _get_endpoint(args, model)
        if not endpoint:
            print(f"No endpoint configured for model {model}", file=sys.stderr)
            return 2

    provider: LLMProvider = create_provider(
        cli_args.backend,
        model_id=model,
        endpoint=endpoint,
        request_timeout_s=float(os.environ.get("ELMFUZZ_HF_TIMEOUT", "120")),
    )

    temperature, max_new_tokens, repetition_penalty = _generation_params(config)

    seed_root = Path(cli_args.rundir) / "initial" / "seeds"
    seed_root.mkdir(parents=True, exist_ok=True)

    seed_modules = list(_load_seed_modules(args))
    if not seed_modules:
        print("No run.seeds configured; cannot infer input format", file=sys.stderr)
        return 2

    seed_counters: dict[str, int] = {}
    for module_path in seed_modules:
        func_name = _extract_generator_name(module_path)
        if not func_name:
            print(f"Skipping seed module without generator: {module_path}", file=sys.stderr)
            continue
        fmt = _infer_format(func_name)
        prompt = fmt.prompt

        seed_dir = seed_root / _seed_dir_name(fmt)
        seed_dir.mkdir(parents=True, exist_ok=True)
        seed_index = seed_counters.get(seed_dir.name, 0)

        for _ in range(cli_args.num):
            out_path = seed_dir / f"input_{seed_index:04d}{fmt.extension}"

            generated = ""
            for attempt in range(cli_args.max_retries + 1):
                res = provider.generate_completion(
                    prompt,
                    temperature=temperature,
                    max_new_tokens=max_new_tokens,
                    repetition_penalty=repetition_penalty,
                    stop=None,
                )
                if "generated_text" in res:
                    generated = _sanitize_output(res.get("generated_text", ""), fmt)
                if generated:
                    break
                if attempt < cli_args.max_retries:
                    continue
            if not generated:
                print(f"Failed to generate seed {seed_index:04d} for {fmt.label}", file=sys.stderr)
                continue

            out_path.write_text(generated, encoding="utf-8")
            print(f"Seeded {fmt.label}: {out_path}")
            seed_index += 1

        seed_counters[seed_dir.name] = seed_index

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
