# TODO: Should consider the seed coverage

import os
import sys
import pandas as pd

root = sys.argv[1]
update_mode = len(sys.argv) > 2 and sys.argv[2] == "update" 

REP = 10

PWD = os.path.realpath(os.path.dirname(__file__))
FUZZERS = ["elm", "grmr", "glade", "isla", "islearn", "elfuzz_direct"]
BENCHMARKS = ["jsoncpp", "re2", "sqlite3", "cpython3", "libxml2", "librsvg", "cvc5"]

def compute_mean(data: list[list]) -> list:
    transpose = list(zip(*data))
    sizes = [len(item) for item in transpose]
    assert all(size == sizes[0] for size in sizes), f"{sizes=}"
    return [sum(item) / len(item) for item in transpose]

def collect_benchmark(benchmark, df):
    def collect_fuzzer(fuzzer) -> list[list]:
        def collect_rep(rep, df) -> list:
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
                print(f"Warning: {i}/{benchmark}_{fuzzer} missing")
                return []
            return result
        result = []
        for i in range(1, REP + 1):
            r = collect_rep(i, df)
            if not r:
                continue
            result.append(r)
        return result
    for fuzzer in FUZZERS:
        if benchmark in ["jsoncpp", "re2"] and fuzzer == "islearn":
            continue
        r = collect_fuzzer(fuzzer)
        if not r:
            continue
        print(f"{benchmark}_{fuzzer}: {len(r)=} {', '.join(str(len(item)) for item in r)}")
        m = compute_mean(r)
        for i in range(min(len(m), 24)):
            df.loc[i + 1, fuzzer] = m[i]

dfs = {}
if update_mode:
    for benchmark in BENCHMARKS:
        df = pd.read_excel(f"{PWD}/results/rq1_sum.xlsx", sheet_name=benchmark, index_col=0, header=0)
        dfs[benchmark] = df.reindex(columns=FUZZERS)
with pd.ExcelWriter(f"{PWD}/results/rq1_sum.xlsx") as writer:
    for benchmark in BENCHMARKS:
        if not update_mode:
            df = pd.DataFrame(columns=FUZZERS, index=range(1, 25))
            df.index.name = "Time (h)"
        else:
            df = dfs[benchmark]
        collect_benchmark(benchmark, df)
        df.to_excel(writer, sheet_name=benchmark)