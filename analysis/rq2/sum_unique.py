import os
import pandas as pd

BENCHMARKS = [
    "libxml2",
    "cpython3",
    "sqlite3",
]

FUZZERS = [
    "elm",
    "grmr",
    "isla",
    "islearn",
    "glade",
    "elfuzz_direct",
]

PWD = os.path.dirname(os.path.abspath(__file__))

with pd.ExcelWriter(os.path.join(PWD, "results", "unique.xlsx")) as writer:
    df = pd.DataFrame(columns=FUZZERS, index=BENCHMARKS)
    for benchmark in BENCHMARKS:
        for fuzzer in FUZZERS:
            unique_file = os.path.join(PWD, "results", f"unique_{benchmark}_{fuzzer}.txt")
            if not os.path.exists(unique_file):
                continue
            with open(unique_file, "r") as f:
                lines = f.readlines()
                df.loc[benchmark, fuzzer] = len(lines)
    df.to_excel(writer)
