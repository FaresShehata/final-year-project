#!/usr/bin/env python3
"""Generate the initial flat input population for `elfuzz direct` mode.

Writes ``<output_dir>/input_NNNNNNNN.<ext>`` (no collection nesting).
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm_provider import create_provider
from direct_common import (
    build_direct_prompt,
    fewshot_delim,
    initial_stop,
    postprocess_copilot,
)


def load_corpus(corpus_dir: str, max_files: int = 512, max_chars: int = 800) -> list[str]:
    """Load real example inputs for few-shot priming / direct seeding.

    Skips files larger than ``max_chars`` so few-shot prompts stay small, and
    returns ``[]`` when the dir is missing/empty (callers fall back to the
    no-corpus path).
    """
    if not corpus_dir or not os.path.isdir(corpus_dir):
        return []
    out: list[str] = []
    for name in sorted(os.listdir(corpus_dir)):
        p = os.path.join(corpus_dir, name)
        if not os.path.isfile(p):
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                t = f.read(max_chars + 1)
        except OSError:
            continue
        t = t.strip()
        if t and len(t) <= max_chars:
            out.append(t)
        if len(out) >= max_files:
            break
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--backend", choices=["huggingface", "copilot"], required=True)
    p.add_argument("-M", "--model", required=True, help="Model name/id passed to LLMProvider")
    p.add_argument(
        "-E",
        "--endpoint",
        default=None,
        help="Endpoint URL (HuggingFace TGI backend); ignored for Copilot",
    )
    p.add_argument("--num-initial-inputs", type=int, required=True)
    p.add_argument("--input-extension", required=True)
    p.add_argument("--format-name", required=True)
    p.add_argument("--format-description", required=True)
    p.add_argument(
        "--hf-initial-prefix",
        default="",
        help="Bare prefix fed to the HuggingFace model (often empty); the "
        "in-output prime for the format.",
    )
    p.add_argument(
        "--seed-corpus",
        default="",
        help="Directory of real example inputs; used for few-shot priming and "
        "to directly seed a few guaranteed in-format inputs.",
    )
    p.add_argument("--few-shot-k", type=int, default=3,
                   help="Number of corpus examples to show the model per call.")
    p.add_argument("--seed-copies", type=int, default=16,
                   help="How many real corpus examples to copy directly into the "
                        "initial set (guaranteed in-format).")
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("-j", "--jobs", type=int, default=16)
    return p.parse_args()


def generate_one(
    provider,
    backend: str,
    fmt_name: str,
    fmt_desc: str,
    hf_initial_prefix: str,
    temperature: float,
    max_new_tokens: int,
    ext: str = "",
    examples: list[str] | None = None,
) -> str:
    prompt = build_direct_prompt(
        provider,
        backend,
        "initial",
        prefix=hf_initial_prefix,
        suffix="",
        fmt_name=fmt_name,
        fmt_desc=fmt_desc,
        ext=ext,
        examples=examples,
    )
    res = provider.generate_completion(
        prompt,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        stop=initial_stop(provider, backend, examples),
    )
    text = res.get("generated_text", "") or ""
    if backend == "copilot":
        return postprocess_copilot(text)
    # HF: trim at the few-shot delimiter if the model emitted it, then prepend
    # the in-output prime.
    if examples:
        text = text.split(fewshot_delim(provider), 1)[0]
    return hf_initial_prefix + text


def main() -> int:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    provider = create_provider(
        args.backend,
        model_id=args.model,
        endpoint=args.endpoint,
    )

    corpus = load_corpus(args.seed_corpus)
    n = args.num_initial_inputs
    n_copies = min(len(corpus), max(0, args.seed_copies)) if corpus else 0
    k = min(args.few_shot_k, len(corpus)) if corpus else 0
    print(
        f"[direct_initial] generating {n} initial inputs into {args.output_dir} "
        f"(corpus={len(corpus)} examples from {args.seed_corpus or '<none>'}; "
        f"{n_copies} copied directly, {n - n_copies} via LLM, few-shot k={k})",
        file=sys.stderr,
        flush=True,
    )

    written = 0
    # 1. Seed a few real examples directly so the pool always has in-format seeds.
    for content in (random.sample(corpus, n_copies) if n_copies else []):
        out_path = os.path.join(
            args.output_dir, f"input_{written:08d}{args.input_extension}"
        )
        with open(out_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(content)
        written += 1

    # 2. LLM-generate the remainder, few-shot-primed from the corpus when present.
    failures = 0
    n_gen = n - written
    if n_gen > 0:
        with ThreadPoolExecutor(max_workers=args.jobs) as ex:
            futs = []
            for _ in range(n_gen):
                examples = random.sample(corpus, k) if k else None
                futs.append(ex.submit(
                    generate_one,
                    provider,
                    args.backend,
                    args.format_name,
                    args.format_description,
                    args.hf_initial_prefix,
                    args.temperature,
                    args.max_new_tokens,
                    args.input_extension,
                    examples,
                ))
            idx = written
            for fut in as_completed(futs):
                out_path = os.path.join(
                    args.output_dir, f"input_{idx:08d}{args.input_extension}"
                )
                idx += 1
                try:
                    content = fut.result()
                except Exception as exc:
                    failures += 1
                    print(f"[direct_initial] LLM call failed: {exc}", file=sys.stderr)
                    content = ""
                with open(out_path, "w", encoding="utf-8", errors="replace") as f:
                    f.write(content)

    if failures:
        print(f"[direct_initial] WARNING: {failures} LLM calls failed", file=sys.stderr)
    print(f"[direct_initial] wrote {n} inputs to {args.output_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
