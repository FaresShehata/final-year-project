import sys
import os

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

triage_dir = sys.argv[1]

bugs = {}

for rep in range(1, 11):
    for benchmark in BENCHMARKS:
        if benchmark not in bugs:
            bugs[benchmark] = {}
        for fuzzer in FUZZERS:
            if fuzzer not in bugs[benchmark]:
                bugs[benchmark][fuzzer] = set()
            triage_file = os.path.join(triage_dir, str(rep), f"{benchmark}_{fuzzer}.txt")
            if not os.path.exists(triage_file):
                continue
            with open(triage_file, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    bugs[benchmark][fuzzer].update([item.strip() for item in line.split(",")])

for benchmark in BENCHMARKS:
    for fuzzer in FUZZERS:
        rest = set()
        for other_fuzzer in FUZZERS:
            if fuzzer == other_fuzzer:
                continue
            rest.update(bugs[benchmark][other_fuzzer])
        with open(os.path.join(PWD, "results", f"unique_{benchmark}_{fuzzer}.txt"), "w") as f:
            for bug in bugs[benchmark][fuzzer]:
                if bug not in rest:
                    f.write(f"{bug}\n")
