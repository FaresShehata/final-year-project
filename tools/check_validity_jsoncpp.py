#!/usr/bin/env python3
"""Report how many inputs in the jsoncpp final pool are well-formed JSON.

An input is counted as *valid* when it parses as a single complete JSON
document (``json.loads`` succeeds). The JSON grammar requires exactly one
top-level value, so a truncated document or one with trailing/garbage content
(common after line-boundary mutation) is rejected.

This uses Python's strict RFC-8259 parser as a dependency-free proxy for "would
jsoncpp accept this?". jsoncpp's reader can be marginally more lenient (it can
be configured to allow comments, for instance), so this is a conservative
check; structurally broken inputs (e.g. unbalanced braces) are rejected by both.

Usage:
    tools/check_validity_jsoncpp.py [POOL_DIR] [--list-invalid]

POOL_DIR defaults to results/elfuzz_direct_jsoncpp/pool/inputs (resolved
relative to the repository root, so the script runs from anywhere).
"""
import argparse
import json
import os
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_POOL = os.path.join(REPO_ROOT, "results/elfuzz_direct_jsoncpp/pool/inputs")


def is_valid_json(data: bytes):
    """Return (ok, reason). ok=True if data is one well-formed JSON document."""
    try:
        json.loads(data)  # json.loads accepts bytes (UTF-8/16/32 autodetected)
        return True, None
    except json.JSONDecodeError as e:
        # e.msg drops the position, so distinct offsets collapse to one reason.
        return False, e.msg
    except UnicodeDecodeError:
        return False, "UnicodeDecodeError"


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
            data = f.read()
        ok, reason = is_valid_json(data)
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
    print(f"jsoncpp final pool: {valid}/{total} well-formed JSON ({pct:.1f}%), "
          f"{invalid} invalid")
    print(f"  pool: {args.pool_dir}")
    print(f"  criterion: json.loads parses one complete JSON document")
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
