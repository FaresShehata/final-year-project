import os
import sys

PWD = os.path.dirname(os.path.abspath(__file__))

BENCHMARKS = [
    "cpython3",
    "libxml2",
    "sqlite3"
]

FUZZERS = [
    # "elm",
    "grmr",
    "isla",
    "islearn",
    "glade",
    "elfuzz_direct"
]

for benchmark in BENCHMARKS:
    acc = set()
    for fuzzer in FUZZERS:
        unique_file = os.path.join(PWD, "results", f"unique_{benchmark}_{fuzzer}.txt")
        if not os.path.exists(unique_file):
            continue
        with open(unique_file, "r") as f:
            for line in f:
                acc.add(line.strip())
    with open(os.path.join(PWD, "results", f"failure_{benchmark}.txt"), "w") as f:
        for bug in acc:
            f.write(bug + "\n")
