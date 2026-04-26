import importlib
import json
import logging
import os
import os.path
import random
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import Any
import concurrent.futures

import click as clk

logger = logging.getLogger(__file__)


@dataclass(frozen=True)
class Elite:
    batch_id: int
    edges: frozenset[str]
    size_bytes: int


def _parse_cov_file(path: str) -> frozenset[str]:
    edges: set[str] = set()
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                edges.add(line.split(":", 1)[0].strip())
    except FileNotFoundError:
        return frozenset()
    return frozenset(edges)


_CODE_FENCE_RE = re.compile(r"^```[a-zA-Z0-9_-]*\s*\n|\n```\s*$")


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        # Remove the first fence line.
        t = t.split("\n", 1)[1] if "\n" in t else ""
    # Remove trailing fence if present.
    t = re.sub(r"\n```\s*$", "", t.strip())
    return t.strip()


def _sanitize_output(target: str, text: str) -> str:
    t = _strip_code_fences(text)
    t = t.strip("\ufeff")

    # If the model still emitted chatter, trim to the most likely payload.
    if target == "jsoncpp":
        if "{" in t and "}" in t:
            t = t[t.find("{") : t.rfind("}") + 1]
        elif "[" in t and "]" in t:
            t = t[t.find("[") : t.rfind("]") + 1]
    elif target in ("libxml2", "librsvg"):
        if "<" in t:
            t = t[t.find("<") :]
    elif target == "re2":
        t = t.splitlines()[0].strip() if t.splitlines() else t.strip()
    elif target == "cvc5":
        if "(" in t:
            t = t[t.find("(") :]
    elif target == "sqlite3":
        # Keep as-is; SQL scripts can be multiline.
        pass
    elif target == "cpython3":
        # Keep as-is.
        pass
    return t.strip()


def _prompt_for_target(target: str, *, size_limit: int, parents: list[str]) -> str:
    parent_section = ""
    if parents:
        truncated: list[str] = []
        for p in parents[:3]:
            p = p.strip()
            if not p:
                continue
            if len(p) > 600:
                p = p[:600] + "\n"
            truncated.append(p)
        if truncated:
            parent_section = (
                "\n\nSome previously high-coverage examples (for inspiration; do NOT copy verbatim):\n"
                + "\n\n---\n\n".join(truncated)
            )

    common = (
        "Return only the input text/bytes. No markdown, no code fences, no explanation. "
        f"Keep it under {size_limit} bytes when encoded as UTF-8." + parent_section
    )

    match target:
        case "jsoncpp":
            return (
                "Generate ONE standalone JSON document (UTF-8). It must be syntactically valid JSON. "
                "Use diverse structures (objects/arrays/numbers/strings/escaping), and sometimes nesting.\n\n" + common
            )
        case "libxml2":
            return (
                "Generate ONE standalone XML document (UTF-8). It must be well-formed (matching tags). "
                "Prolog is optional. Occasionally use attributes, entities, and CDATA.\n\n" + common
            )
        case "librsvg":
            return (
                "Generate ONE standalone SVG document (UTF-8). It must be well-formed XML with <svg> root, include the SVG namespace, "
                "and use varied elements/attributes (paths, gradients, transforms, text, shapes).\n\n" + common
            )
        case "re2":
            return (
                "Generate ONE RE2-compatible regular expression (ASCII only). Prefer a single line. "
                "Use alternation, groups, char classes, and quantifiers.\n\n" + common
            )
        case "sqlite3":
            return (
                "Generate ONE SQLite SQL script (UTF-8). Include a mix of CREATE TABLE, INSERT, SELECT, UPDATE/DELETE, and transactions. "
                "Keep statements varied and relatively short.\n\n" + common
            )
        case "cpython3":
            return (
                "Generate ONE Python 3 program (UTF-8). It must be syntactically valid. Use varied features (functions/classes, comprehensions, exceptions, "
                "string/bytes operations, imports, f-strings).\n\n" + common
            )
        case "cvc5":
            return (
                "Generate ONE SMT-LIB2 script. Start with (set-logic ...) and end with (check-sat). Include declarations and asserts; keep it valid SMT-LIB2.\n\n"
                + common
            )
        case _:
            return "Generate ONE standalone input (UTF-8).\n\n" + common



def _random_completion(text: str) -> tuple[str, str]:
    lines = text.split("\n")
    if len(lines) > 2:
        cut = random.randint(1, len(lines) - 1)
        return "\n".join(lines[:cut]), "\n".join(lines[cut:])
    elif len(text) > 2:
        cut = random.randint(1, len(text) - 1)
        return text[:cut], text[cut:]
    return text, ""


def _random_fim(text: str) -> tuple[str, str, str]:
    lines = text.split("\n")
    if len(lines) >= 3:
        start = random.randint(1, len(lines) - 2)
        end = random.randint(start + 1, len(lines) - 1)
        return "\n".join(lines[:start]) + "\n", "\n".join(lines[end:]), "\n".join(lines[start:end])
    elif len(text) >= 3:
        start = random.randint(1, len(text) - 2)
        end = random.randint(start + 1, len(text) - 1)
        return text[:start], text[end:], text[start:end]
    return text, "", ""


def _random_crossover(text1: str, text2: str) -> tuple[str, str]:
    lines1 = text1.split("\n")
    lines2 = text2.split("\n")
    if len(lines1) > 2 and len(lines2) > 2:
        cut1 = random.randint(1, len(lines1) - 1)
        cut2 = random.randint(1, len(lines2) - 1)
        return "\n".join(lines1[:cut1]) + "\n", "\n".join(lines2[cut2:])
    elif len(text1) > 2 and len(text2) > 2:
        cut1 = random.randint(1, len(text1) - 1)
        cut2 = random.randint(1, len(text2) - 1)
        return text1[:cut1], text2[cut2:]
    return text1, ""


def _generate_one_input(
    provider: Any,
    rng: random.Random,
    target_name: str,
    size_limit: int,
    elites: list[Elite],
    out_dir: str,
    seed_dir: str | None,
) -> bytes:
    parents = _pick_parent_text(rng=rng, elites=elites, out_dir=out_dir, seed_dir=seed_dir)
    
    strategies = ["inspiration", "complete", "infilled", "lmsplice"]
    strategy = rng.choice(strategies)

    if strategy == "inspiration" or not parents:
        prompt = _prompt_for_target(target_name, size_limit=size_limit, parents=parents)
        prefix = ""
        suffix = ""
    else:
        p1 = parents[0]
        if strategy == "complete":
            prefix, _ = _random_completion(p1)
            suffix = ""
            prompt = provider.build_prompt("complete", prefix, suffix)
        elif strategy == "infilled":
            prefix, suffix, _ = _random_fim(p1)
            prompt = provider.build_prompt("infilled", prefix, suffix)
        elif strategy == "lmsplice":
            p2 = parents[1] if len(parents) > 1 else p1
            prefix, suffix = _random_crossover(p1, p2)
            prompt = provider.build_prompt("lmsplice", prefix, suffix)
        else:
            prompt = _prompt_for_target(target_name, size_limit=size_limit, parents=parents)
            prefix = ""
            suffix = ""

    text = ""
    for attempt in range(3):
        res = provider.generate_completion(prompt, max_new_tokens=1200)
        raw_text = (res.get("generated_text") if isinstance(res, dict) else None) or ""
        
        if strategy in ("complete", "infilled", "lmsplice") and parents:
            clean_raw = _strip_code_fences(raw_text)
            full_text = prefix + clean_raw + suffix
            text = full_text.strip("﻿").strip()
        else:
            text = _sanitize_output(target_name, raw_text)
        
        data = text.encode("utf-8", errors="replace")
        if data and len(data) <= size_limit:
            break
        
        if strategy not in ("complete", "infilled", "lmsplice") or not parents:
            prompt = prompt + f"\n\nIMPORTANT: Your previous output was too large or empty. Output MUST be <= {size_limit} bytes UTF-8."

    data = text.encode("utf-8", errors="replace")
    if len(data) > size_limit:
        data = data[:size_limit]
        
    return data


def _pick_parent_text(
    *,
    rng: random.Random,
    elites: list[Elite],
    out_dir: str,
    seed_dir: str | None,
) -> list[str]:
    parents: list[str] = []

    if elites:
        elite = rng.choice(elites)
        elite_dir = os.path.join(out_dir, str(elite.batch_id))
        try:
            files = [
                os.path.join(elite_dir, f) for f in os.listdir(elite_dir) if os.path.isfile(os.path.join(elite_dir, f))
            ]
        except FileNotFoundError:
            files = []
        rng.shuffle(files)
        for f in files[:2]:
            try:
                parents.append(open(f, "rb").read(4096).decode("utf-8", errors="replace"))
            except Exception:
                continue

    if seed_dir and len(parents) < 2:
        try:
            seed_files = [
                os.path.join(seed_dir, f) for f in os.listdir(seed_dir) if os.path.isfile(os.path.join(seed_dir, f))
            ]
        except FileNotFoundError:
            seed_files = []
        rng.shuffle(seed_files)
        for f in seed_files[: 2 - len(parents)]:
            try:
                parents.append(open(f, "rb").read(4096).decode("utf-8", errors="replace"))
            except Exception:
                continue

    return parents


def _update_elites(
    *,
    elites: list[Elite],
    batch_id: int,
    edges: frozenset[str],
    size_bytes: int,
    max_elites: int,
) -> list[Elite]:
    if not edges:
        return elites

    # Discard if dominated by an existing elite.
    for e in elites:
        if edges <= e.edges:
            return elites

    # Remove any elites dominated by this candidate.
    new_elites = [e for e in elites if not (e.edges < edges)]
    new_elites.append(Elite(batch_id=batch_id, edges=edges, size_bytes=size_bytes))

    if max_elites > 0 and len(new_elites) > max_elites:
        # Keep best by (edge_count, smaller_size).
        new_elites.sort(key=lambda x: (len(x.edges), -x.size_bytes), reverse=True)
        new_elites = new_elites[:max_elites]

    return new_elites


def _write_elites_json(path: str, elites: list[Elite]) -> None:
    try:
        with open(path, "w") as f:
            json.dump(
                [
                    {
                        "batch_id": e.batch_id,
                        "edge_count": len(e.edges),
                        "size_bytes": e.size_bytes,
                    }
                    for e in elites
                ],
                f,
                indent=2,
            )
    except Exception as e:
        logger.debug(f"Failed to write elites json: {e}")


def _make_provider() -> Any:
    backend = os.environ.get("ELMFUZZ_LLM_BACKEND", "huggingface")
    model_id = os.environ.get("ELMINPUTS_MODEL_ID")
    endpoint = os.environ.get("ELMINPUTS_ENDPOINT")

    if backend == "copilot":
        if not model_id:
            model_id = os.environ.get("ELMFUZZ_COPILOT_MODEL", "gpt-4.1")
    else:
        if not model_id:
            model_id = os.environ.get("ELMFUZZ_INPUTS_MODEL_ID", "codellama/CodeLlama-13b-hf")
        if not endpoint:
            endpoint = os.environ.get("ELMFUZZ_TGI_ENDPOINT")
        if not endpoint:
            raise RuntimeError(
                "ELMINPUTS_ENDPOINT (or ELMFUZZ_TGI_ENDPOINT) is required when ELMFUZZ_LLM_BACKEND=huggingface"
            )

    llm_provider = importlib.import_module("llm_provider")
    return llm_provider.create_provider(backend, model_id=model_id, endpoint=endpoint)


@clk.command()
@clk.option("--function", "-g", type=str, required=False, default=None)
@clk.option(
    "--working-dir", "-d", type=clk.Path(exists=True, file_okay=False, dir_okay=True), required=False, default="."
)
@clk.option("--num", "-n", type=int, required=False, default=-1)
@clk.option("--time-limit", "-t", type=int, required=False, default=-1, help="Time limit in seconds")
@clk.option("--force", "-f", is_flag=True, required=False, default=False)
@clk.option("--batch-size", "-b", type=int, required=False, default=1000)
@clk.option("--para-num", "-j", type=int, required=False, default=1)
@clk.option("--afl-dir", "-a", type=str, required=False, default="/usr/bin")
@clk.option("--callback", "-cb", type=str, required=False, default=None)
@clk.option("--debug-level", "-v", type=clk.Choice(["DEBUG", "INFO"]), required=False, default="INFO")
@clk.option("--size-limit", "-s", type=int, required=False, default=2048)
@clk.option("--race-mode", "-r", is_flag=True, required=False, default=False)
@clk.option("--stat-file", "-sf", type=clk.File("w"), required=False, default="-")
@clk.option("--batch-timeout", "-q", type=int, required=False, default=-1)
@clk.option("--check-point", "-c", type=int, required=False, default=-1)
def main(
    function: str | None,
    working_dir: str,
    num: int,
    time_limit: int,
    force: bool,
    batch_size: int,
    para_num: int,
    afl_dir: str,
    callback: str | None,
    debug_level: str,
    size_limit: int,
    race_mode: bool,
    stat_file: Any,
    batch_timeout: int,
    check_point: int,
):
    del function, callback, stat_file, para_num

    match debug_level:
        case "INFO":
            logging.basicConfig(level=logging.INFO)
        case "DEBUG":
            logging.basicConfig(level=logging.DEBUG)
        case _:
            raise ValueError("Invalid debug level")

    target_name = os.path.basename(working_dir).split("_")[0]
    out_dir = os.path.join(working_dir, "out")
    os.makedirs(out_dir, exist_ok=True)

    if not force and os.path.exists(os.path.join(working_dir, "sum.cov")):
        logger.warning("Coverage file already exists. Add --force to overwrite it.")
        return

    sys.path.insert(0, working_dir)

    cov_module = importlib.import_module("get_cov")
    if hasattr(cov_module, "m_batch_size"):
        cov_module.m_batch_size = batch_size

    seed_dir = os.environ.get("ELMINPUTS_SEED_DIR")
    if seed_dir:
        seed_dir = os.path.abspath(seed_dir)

    max_elites = int(os.environ.get("ELMINPUTS_MAX_ELITES", "50"))

    provider = _make_provider()

    overall_start_time = datetime.now()
    time_sum = 0.0
    batch = 0
    generated = 0
    elites: list[Elite] = []

    # Note: enforce time_limit based on generation time only (like existing drivers).
    left = num if num > 0 else (2**32 - 1)

    with TemporaryDirectory(prefix="elminputs_", ignore_cleanup_errors=True) as td:
        while left > 0:
            elapsed = datetime.now() - overall_start_time
            logger.info(f"Total elapsed time: {elapsed}")
            logger.info(f"Batch {batch} ({batch_size} per batch)")
            logger.info(f'Generated so far: {generated} / {num if num > 0 else "inf"}')
            logger.info(f'Time sum: {time_sum:.2f} / {time_limit if time_limit > 0 else "inf"}')

            if time_limit > 0 and time_sum > time_limit:
                break

            batch_start = time.time()
            batch_dir = os.path.join(td, str(batch))
            os.makedirs(batch_dir, exist_ok=True)

            rng = random.Random(batch ^ int(time.time()))

            batch_count = min(batch_size, left)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=para_num) as executor:
                futures = {}
                for i in range(batch_count):
                    task_rng = random.Random(rng.randint(0, 2**32 - 1))
                    f = executor.submit(
                        _generate_one_input,
                        provider,
                        task_rng,
                        target_name,
                        size_limit,
                        elites,
                        out_dir,
                        seed_dir,
                    )
                    futures[f] = i

                for f in concurrent.futures.as_completed(futures):
                    i = futures[f]
                    
                    current_batch_time = time.time() - batch_start
                    
                    if time_limit > 0 and (time_sum + current_batch_time) > time_limit:
                        for pending_f in futures:
                            if not pending_f.done():
                                pending_f.cancel()
                        continue

                    if batch_timeout > 0 and current_batch_time > batch_timeout:
                        logger.info("Batch timeout reached; stopping batch early")
                        for pending_f in futures:
                            if not pending_f.done():
                                pending_f.cancel()
                        continue

                    try:
                        data = f.result()
                        with open(os.path.join(batch_dir, f"{i}.seed"), "wb") as out_f:
                            out_f.write(data)
                        generated += 1
                        left -= 1
                    except Exception as e:
                        logger.debug(f"Generation error: {e}")

            time_sum += time.time() - batch_start

            if race_mode:
                logger.warning("Race mode enabled; skipping coverage collection")
            else:
                try:
                    cov_module.get_cov_conc(
                        working_dir,
                        td,
                        td,
                        1,
                        1,
                        batch,
                        os.path.join(afl_dir, "afl-showmap"),
                    )
                except Exception as e:
                    logger.debug(f"Coverage collection failed for batch {batch}: {e}")

            cov_path = os.path.join(td, f"{batch}.cov")
            edges = _parse_cov_file(cov_path)
            size_bytes = 0
            for fn in os.listdir(batch_dir):
                try:
                    size_bytes += os.path.getsize(os.path.join(batch_dir, fn))
                except OSError:
                    pass

            elites = _update_elites(
                elites=elites,
                batch_id=batch,
                edges=edges,
                size_bytes=size_bytes,
                max_elites=max_elites,
            )
            _write_elites_json(os.path.join(working_dir, "elites.json"), elites)

            try:
                os.rename(batch_dir, os.path.join(out_dir, str(batch)))
            except Exception:
                # Fallback across filesystems.
                import shutil

                shutil.move(batch_dir, os.path.join(out_dir, str(batch)))

            batch += 1


if __name__ == "__main__":
    main()
