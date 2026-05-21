import os
import shutil
import sys
import tempfile
import pandas as pd

BENCHMARKS = ["jsoncpp", "libxml2", "cpython3", "librsvg", "sqlite3", "cvc5", "re2"]
FUZZERS = ["elm", "grmr", "isla", "islearn", "glade"]


PWD = os.path.realpath(os.path.dirname(__file__))

input_file = os.path.join(PWD, "results", "rq1_sum.xlsx")

with tempfile.TemporaryDirectory() as tmpdir:
    filename = os.path.join(tmpdir, "rq1_sum.xlsx")
    shutil.copy(input_file, filename)

    output_file = os.path.join(PWD, "results", "rq1_sum.xlsx")
    seed_file = os.path.join(PWD, "results", "seed_cov.xlsx")

    with pd.ExcelWriter(output_file) as writer:
        for benchmark in BENCHMARKS:
            seed_df = pd.read_excel(seed_file, sheet_name=benchmark, header=0, index_col=0)
            input_df = pd.read_excel(filename, sheet_name=benchmark, header=0, index_col=0)
            for fuzzer in FUZZERS:
                if benchmark in ["jsoncpp", "re2"] and fuzzer == "islearn":
                    continue
                seed_cov = seed_df.loc[0, fuzzer]
                input_df.loc[0, fuzzer] = seed_cov
            input_df.sort_index(inplace=True)
            input_df.to_excel(writer, sheet_name=benchmark)
