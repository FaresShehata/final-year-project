import os
import pandas as pd
import sys
from tqdm import tqdm
from math import ceil

PWD = os.path.dirname(os.path.abspath(__file__))

BENCHMARKS = [
    "libxml2",
    "cpython3",
    "sqlite3"
]

FUZZERS = [
    "elm",
    "grmr",
    "isla",
    "islearn",
    "glade",
    "elfuzz_direct"
]

triage_dir = sys.argv[1]

# Unit: 10 min

timepoints = range(145)

for rep in range(1, 11):
    rep_dir = os.path.join(triage_dir, str(rep))
    if not os.path.exists(rep_dir):
        continue
    with pd.ExcelWriter(os.path.join(PWD, "results", f"rq2_bug_count_10_min_{rep}.xlsx")) as writer:
        for benchmark in tqdm(BENCHMARKS, desc=str(rep)):
            df = pd.DataFrame(index=timepoints, columns=FUZZERS)
            for fuzzer in FUZZERS:
                sequence = []
                cache_dir = os.path.join(triage_dir, str(rep), "cache")
                if not os.path.exists(cache_dir):
                    continue
                
                cache_files = {}
                for file in os.listdir(cache_dir):
                    full_path = os.path.join(cache_dir, file)
                    with open(full_path, "r") as f:
                        first_line = f.readline()
                        segs = first_line.split("/")
                        b_f = segs[-4]
                        if b_f != f"{benchmark}_{fuzzer}":
                            continue

                        tokens = segs[-1].split(",")

                        if tokens[2].startswith('time:'):
                            time_token = tokens[2]
                        elif tokens[3].startswith('time:'):
                            time_token = tokens[3]
                        else:
                            assert False, f'{f} does not have time token'

                        crash_time = ceil(int(time_token.removeprefix('time:')) / (600 * 1000))
                        assert crash_time <= 144, f'{crash_time=} is greater than 144'
                        if crash_time not in cache_files:
                            cache_files[crash_time] = []
                        cache_files[crash_time].append(full_path)
                acc = set()
                for timepoint in timepoints:
                    if timepoint not in cache_files:
                        df.loc[timepoint, fuzzer] = len(acc)
                        continue
                    for file in cache_files[timepoint]:
                        with open(file, "r") as f:
                            lines = f.readlines()
                            for line in lines[1:]:
                                acc.add(line.strip())
                    df.loc[timepoint, fuzzer] = len(acc)
            df.to_excel(writer, sheet_name=benchmark)
