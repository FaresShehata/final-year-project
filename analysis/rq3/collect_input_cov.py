import os
import sys
import subprocess
import tempfile
import itertools
import pandas as pd
from tqdm import tqdm

PWD = os.path.realpath(os.path.dirname(__file__))

NOFS_INPUT_COV_DIR = sys.argv[1]

OTHER_VAR_FUZZERS = [
    "nocomp", "noinf", "nospl"
]

ELF_FUZZER = "elm"
NOFS_FUZZER = "alt"

BENCHMARKS = [
    "cpython3", "cvc5", "jsoncpp", "librsvg", "libxml2", "re2", "sqlite3"
]

ELF_SEED_COV_FILE = os.path.join(PWD, os.path.pardir, "rq1", "results", "seed_cov.xlsx")

if __name__ == '__main__':
    data = {}
    with tempfile.TemporaryDirectory() as tmpdir:
        for benchmark, var_fuzzer in tqdm(list(itertools.product(BENCHMARKS, OTHER_VAR_FUZZERS)), desc="Other var fuzzers"):
            tarball = os.path.join(PWD, "eval_results", f"{benchmark}_{var_fuzzer}.tar.zst")
            sum_file = f"{benchmark}_{var_fuzzer}/sum.cov"
            cmd = [
                "tar", "--zstd", "-C", tmpdir, "-xf", tarball, sum_file
            ]
            subprocess.run(cmd, check=True)
            with open(os.path.join(tmpdir, sum_file), "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
                data[f"{benchmark}_{var_fuzzer}"] = len(lines)

    for benchmark in BENCHMARKS:
        df = pd.read_excel(ELF_SEED_COV_FILE, sheet_name=benchmark, header=0, index_col=0)
        data[f"{benchmark}_elm"] = df.loc[0, "elm"]

    for benchmark in BENCHMARKS:
        with open(os.path.join(NOFS_INPUT_COV_DIR, f"{benchmark}_{NOFS_FUZZER}/count"), "r") as f:
            data[f"{benchmark}_{NOFS_FUZZER}"] = int(f.read().strip())
    df = pd.DataFrame(columns=OTHER_VAR_FUZZERS + [ELF_FUZZER, NOFS_FUZZER], index=BENCHMARKS)
    for benchmark, fuzzer in itertools.product(BENCHMARKS, OTHER_VAR_FUZZERS + [ELF_FUZZER, NOFS_FUZZER]):
        df.loc[benchmark, fuzzer] = data[f"{benchmark}_{fuzzer}"]
    df.to_excel(os.path.join(PWD, "results", "rq3_ablation.xlsx"), index=True, header=True)
