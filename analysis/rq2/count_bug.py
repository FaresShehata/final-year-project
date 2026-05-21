import os
import pandas as pd

PWD = os.path.dirname(os.path.abspath(__file__))

FUZZERS = ["elm", "grmr", "isla", "islearn", "glade", "elfuzz_direct"]
BENCHMARKS = ["libxml2", "cpython3", "sqlite3"]

with pd.ExcelWriter(os.path.join(PWD, f"results", f"rq2_count_bug.xlsx")) as writer:
    for benchmark in BENCHMARKS:
        df = pd.DataFrame(columns=FUZZERS, index=list(range(25)))
        for fuzzer in FUZZERS:
            df.loc[0, fuzzer] = 0
            for hour in range(1, 25):
                acc = []
                for rep in range(1, 11):
                    rep_file = os.path.join(PWD, f"results", f"rq2_count_bug_{rep}.xlsx")
                    if not os.path.exists(rep_file):
                        continue
                    rep_df = pd.read_excel(rep_file, sheet_name=benchmark, header=0, index_col=0)
                    if fuzzer not in rep_df.columns or hour not in rep_df.index:
                        continue
                    val = rep_df.loc[hour, fuzzer]
                    if pd.isna(val):
                        continue
                    acc.append(val)
                if acc:
                    df.loc[hour, fuzzer] = sum(acc) / len(acc)
        df.to_excel(writer, sheet_name=benchmark)
