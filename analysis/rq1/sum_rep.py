# TODO: Should consider the seed coverage

import sys
import pandas as pd
import os

root = sys.argv[1]
update_mode = len(sys.argv) > 2 and sys.argv[2] == "update"


PWD = os.path.realpath(os.path.dirname(__file__))

REP = 10

FUZZERS = ["elm", "grmr", "glade", "isla", "islearn", "elfuzz_direct"]
BENCHMARKS = ["jsoncpp", "re2", "sqlite3", "cpython3", "libxml2", "librsvg", "cvc5"]

def compute_mean(data: list[list]) -> list:
    transpose = list(zip(*data))
    assert len(transpose) == 24, f"{len(transpose)=}"
    sizes = [len(item) for item in transpose]
    assert all(size == sizes[0] for size in sizes), f"{sizes=}"
    return [sum(item) / len(item) for item in transpose]

def collect_benchmark(benchmark, df, rep):
    def collect_fuzzer(fuzzer) -> list:
        result = []
        try:
            with open(f"{root}/afl_cov_exp/{rep}/{benchmark}_{fuzzer}/default/plot_data") as f:
                lines = f.readlines()
                last_time_point = 0
                for line in lines[1:]:
                    tokens = line.split(",")
                    time = int(tokens[0])
                    cov = int(tokens[-1])
                    if time - last_time_point >= 3600:
                        last_time_point += 3600
                        result.append(cov)
        except FileNotFoundError:
            print(f"Warning: {rep}/{benchmark}_{fuzzer} missing")
            return []
        return result
    for fuzzer in FUZZERS:
        if benchmark in ["jsoncpp", "re2"] and fuzzer == "islearn":
            continue
        r = collect_fuzzer(fuzzer)
        if not r:
            continue
        m = r
        for i in range(min(len(m), 24)):
            df.loc[i + 1, fuzzer] = m[i]

for rep in range(1, REP + 1):
    if update_mode:
        for benchmark in BENCHMARKS:
            df = pd.read_excel(f"{PWD}/results/rq1_sum_{rep}.xlsx", sheet_name=benchmark, index_col=0, header=0)
            df = df.reindex(columns=FUZZERS)
            collect_benchmark(benchmark, df, rep)
            with pd.ExcelWriter(f"{PWD}/results/rq1_sum_{rep}.xlsx", engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=benchmark)
    else:
        with pd.ExcelWriter(f"{PWD}/results/rq1_sum_{rep}.xlsx") as writer:
            for benchmark in BENCHMARKS:
                df = pd.DataFrame(columns=FUZZERS, index=range(1, 25))
                df.index.name = "Time (h)"
                collect_benchmark(benchmark, df, rep)
                df.to_excel(writer, sheet_name=benchmark)