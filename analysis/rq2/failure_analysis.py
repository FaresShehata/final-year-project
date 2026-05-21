import os
import sys
import re

PWD = os.path.abspath(os.path.dirname(__file__))

elfuzz_dir = sys.argv[1]

fr_adapt_dir = os.path.abspath(os.path.join(elfuzz_dir, "evaluation", "fr_adapt"))

BENCHMARKS = [
    ("cpython3", "fr_injection_patched.patch"),
    ("libxml2", "fr_injection.patch"),
    # ("sqlite3", "fr_injection_sqlite3_c_patched.diff"), # This should be manually analyzed due to amalgamation
]

class Injection:
    def __init__(self, source_file, lines):
        self.source_file = source_file
        self.content = "\n".join(lines)

    def contain(self, bug):
        pattern = re.compile(rf"FIXREVERTER\[{bug}\]")
        return pattern.search(self.content) is not None


for benchmark, patch_file in BENCHMARKS:
    print(f"Benchmark: {benchmark}")
    with open(os.path.join(PWD, "results", f"failure_{benchmark}.txt"), "r") as bug_f, \
         open(os.path.join(fr_adapt_dir, benchmark, patch_file), "r") as fr_adapt_f:

        injections = []

        current_file = None
        current_lines = []
        for line in fr_adapt_f:
            if line.strip().startswith("--- a/"):
                if current_file is not None:
                    injections.append(Injection(current_file, current_lines))
                current_file = line.strip().removeprefix("--- a/")
                current_lines = []
            else:
                current_lines.append(line)
        if current_file is not None:
            injections.append(Injection(current_file, current_lines))

        for line in bug_f:
            bug = line.strip()
            for injection in injections:
                if injection.contain(bug):
                    print(f"Bug {bug} is contained in {injection.source_file}")
