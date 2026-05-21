import os
import pandas as pd
import sys

PWD = os.path.dirname(os.path.abspath(__file__))

triage_dir = sys.argv[1]

FUZZERS = ["elm", "grmr", "isla", "islearn", "glade", "elfuzz_direct"]
BENCHMARKS = ["libxml2", "cpython3", "sqlite3"]

for rep in range(1, 11):
    with pd.ExcelWriter(os.path.join(PWD, f"results", f"rq2_count_bug_{rep}.xlsx")) as writer:
        for benchmark in BENCHMARKS:
            df = pd.DataFrame(columns=FUZZERS, index=list(range(25)))
            for fuzzer in FUZZERS:
                df.loc[0, fuzzer] = 0
                acc = set()
                if not os.path.exists(os.path.join(triage_dir, str(rep), f"{benchmark}_{fuzzer}.txt")):
                    print(f"Warning: {benchmark}_{fuzzer} missing")
                    continue
                with open(os.path.join(triage_dir, str(rep), f"{benchmark}_{fuzzer}.txt")) as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[1:]):
                        bugs = line.split(",")
                        for bug in bugs:
                            acc.add(bug.strip())
                        df.loc[i + 1, fuzzer] = len(acc)
            df.to_excel(writer, sheet_name=benchmark)