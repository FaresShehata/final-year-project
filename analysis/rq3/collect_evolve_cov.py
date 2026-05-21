import sys
import os
import pandas as pd
import json

PWD = os.path.realpath(os.path.dirname(__file__))

EVOLVE_RECORD_DIR = sys.argv[1]

FUZZERS = [
    "elm", "alt", "nocomp", "noinf", "nospl"
]

BENCHMARKS = [
    "cpython3", "cvc5", "jsoncpp", "librsvg", "libxml2", "re2", "sqlite3"
]

if __name__ == '__main__':
    with pd.ExcelWriter(os.path.join(PWD, "results", "rq3_evolve_cov.xlsx")) as writer:
        for benchmark in BENCHMARKS:
            df = pd.DataFrame(columns=FUZZERS, index=range(1, 51))
            for fuzzer in FUZZERS:
                record_dir = os.path.join(EVOLVE_RECORD_DIR, fuzzer, benchmark)
                if os.path.exists(os.path.join(record_dir, f"gen1", "logs", "elites.json")):
                    for i in range(1, 51):
                        with open(os.path.join(record_dir, f"gen{i}", "logs", "elites.json"), "r") as f:
                            elites = json.load(f)
                        edges = set()
                        for elite, [subedges, _count] in elites.items():
                            edges.update(subedges)
                        df.loc[i, fuzzer] = len(edges)
                else:
                    record = {}
                    for i in range(0, 50):
                        with open(os.path.join(record_dir, f"gen{i}", "logs", "coverage.json"), "r") as f:
                            previous_cov_record = json.load(f)["CodeLlama-13b-hf"]
                        record[i] = previous_cov_record
                    for i in range(1, 51):
                        chosen = [(int(file.split("-")[0].removesuffix("_CodeLlama").removeprefix("gen")),
                                   file.split("-")[-1].removesuffix(".py").removeprefix("hf_"))
                                  for file in os.listdir(os.path.join(record_dir, f"gen{i}", "seeds"))]
                        edges = set()
                        for gen, id in chosen:
                            edges.update(record[gen][id])
                        df.loc[i, fuzzer] = len(edges)
            df.to_excel(writer, sheet_name=benchmark, index=True, header=True)
