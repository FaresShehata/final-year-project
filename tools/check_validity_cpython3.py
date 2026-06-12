#!/usr/bin/env python3
"""Report how many inputs in the cpython3 final pool are valid Python.

An input is counted as *valid* (i.e. accepted by CPython's front-end) when
``compile(src, name, 'exec')`` succeeds. This is exactly the check CPython
performs before executing a file, so it answers "would the interpreter accept
this input?" without actually running it (no arbitrary code is executed).

SyntaxWarnings (e.g. ``'is' with a literal``, invalid escape sequences) are
suppressed: they are warnings on otherwise-valid code, not syntax errors, so
such inputs still compile and count as valid.

Usage:
    tools/check_validity_cpython3.py [POOL_DIR] [--list-invalid]

POOL_DIR defaults to results/elfuzz_direct_cpython3/pool/inputs (resolved
relative to the repository root, so the script runs from anywhere).
"""
import argparse
import os
import sys
import warnings
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_POOL = os.path.join(REPO_ROOT, "results/elfuzz_direct_cpython3/pool/inputs")


def is_valid_python(src: bytes):
    """Return (ok, reason). ok=True if src compiles; reason is the error message."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            compile(src, "<pool-input>", "exec")
            return True, None
        except SyntaxError as e:
            return False, e.msg or "SyntaxError"
        except ValueError as e:
            # e.g. source contains a null byte
            return False, f"ValueError: {e}"


def pool_files(pool_dir: str):
    for name in sorted(os.listdir(pool_dir)):
        if name.startswith(".") or name == "README.md":
            continue
        path = os.path.join(pool_dir, name)
        if os.path.isfile(path):
            yield path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pool_dir", nargs="?", default=DEFAULT_POOL,
                    help="directory of pool inputs (default: %(default)s)")
    ap.add_argument("--list-invalid", action="store_true",
                    help="print the path of every rejected input")
    args = ap.parse_args()

    if not os.path.isdir(args.pool_dir):
        print(f"error: pool dir not found: {args.pool_dir}", file=sys.stderr)
        return 1

    valid = 0
    invalid = 0
    reasons = Counter()
    invalid_files = []
    for path in pool_files(args.pool_dir):
        with open(path, "rb") as f:
            src = f.read()
        ok, reason = is_valid_python(src)
        if ok:
            valid += 1
        else:
            invalid += 1
            reasons[reason] += 1
            invalid_files.append(path)

    total = valid + invalid
    if total == 0:
        print(f"no inputs found in {args.pool_dir}", file=sys.stderr)
        return 1

    pct = 100.0 * valid / total
    print(f"cpython3 final pool: {valid}/{total} valid Python ({pct:.1f}%), "
          f"{invalid} invalid")
    print(f"  pool: {args.pool_dir}")
    print(f"  criterion: compile(src, '<f>', 'exec') succeeds (SyntaxWarnings ignored)")
    if reasons:
        print("  top rejection reasons:")
        for reason, count in reasons.most_common(10):
            print(f"    {count:>5}  {reason}")
    if args.list_invalid:
        print("  invalid inputs:")
        for path in invalid_files:
            print(f"    {os.path.relpath(path, REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
