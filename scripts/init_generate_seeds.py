#!/usr/bin/env python3
"""Initialize seed directories by running generator modules found under
<rundir>/initial/seeds/. For each seed module (a .py file that exposes a
function named `generate_*`) this script will call `driver.py` to produce
concrete input files with an inferred extension (e.g. .json for
`generate_json`).

Usage: python3 scripts/init_generate_seeds.py <rundir> [--num N]
"""
import runpy
import subprocess
import sys
import os
from pathlib import Path


def infer_suffix(func_name: str) -> str:
    n = func_name.lower()
    if "json" in n:
        return ".json"
    if "xml" in n:
        return ".xml"
    if "sql" in n or "sqlite" in n:
        return ".sqlite"
    if "png" in n or "image" in n:
        return ".png"
    return ".dat"


def find_generator(module_path: Path):
    try:
        spec = runpy.run_path(str(module_path))
    except Exception:
        return None
    for k in spec:
        if k.startswith("generate_") and callable(spec[k]):
            return k
    return None


def run_driver(module_path: Path, func_name: str, outdir: Path, num: int, suffix: str):
    outdir.mkdir(parents=True, exist_ok=True)
    # create a dummy seed input file
    seed_input = outdir / "seed_input.txt"
    seed_input.write_text("0")
    output_prefix = str(outdir / "input")
    cmd = [
        sys.executable,
        os.path.join(os.getcwd(), "driver.py"),
        str(module_path),
        func_name,
        "-n",
        str(num),
        "-o",
        output_prefix,
        "-s",
        suffix,
        "-i",
        str(seed_input),
        "-t",
        "10",
        "-S",
        "5242880",
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def quarantine_generator_module(module_path: Path, outdir: Path):
    """Move generator module out of the seed dir so LLM mutation doesn't pick it as a seed."""
    quarantine_dir = outdir / "_generator"
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    target = quarantine_dir / module_path.name
    if target.exists():
        return
    module_path.rename(target)
    seed_input = outdir / "seed_input.txt"
    if seed_input.exists():
        seed_input.rename(quarantine_dir / seed_input.name)


def main():
    if len(sys.argv) < 2:
        print("Usage: init_generate_seeds.py <rundir> [--num N]")
        sys.exit(1)
    rundir = Path(sys.argv[1])
    num = 20
    if "--num" in sys.argv:
        try:
            num = int(sys.argv[sys.argv.index("--num") + 1])
        except Exception:
            pass

    seed_root = rundir / "initial" / "seeds"
    if not seed_root.exists():
        print("No initial seeds at", seed_root)
        return

    for entry in seed_root.iterdir():
        # We expect seed directories (copied by all_gen_inputs.sh). Inside,
        # look for .py modules that export a generate_* function.
        if entry.is_dir():
            py_files = list(entry.glob("*.py"))
            if not py_files:
                continue
            for m in py_files:
                func = find_generator(m)
                if not func:
                    continue
                suffix = infer_suffix(func)
                try:
                    run_driver(m, func, entry, num, suffix)
                    quarantine_generator_module(m, entry)
                except subprocess.CalledProcessError as e:
                    print("Driver failed for", m, "->", e)
                break


if __name__ == "__main__":
    main()
