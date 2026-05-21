from statistics import mean
import pandas as pd
import os

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

quantiles = [0.25, 0.5, 0.75]

with pd.ExcelWriter(os.path.join(PWD, "results", "rq2_time_to_trigger.xlsx")) as writer:
    for benchmark in BENCHMARKS:
        to_record = pd.DataFrame(columns=FUZZERS, index=quantiles)
        for fuzzer in FUZZERS:
            sequences = []
            for rep in range(1, 11):
                rep_file = os.path.join(PWD, "results", f"rq2_bug_count_10_min_{rep}.xlsx")
                if not os.path.exists(rep_file):
                    continue
                df = pd.read_excel(rep_file, sheet_name=benchmark)
                if fuzzer not in df.columns:
                    continue
                if "elm" in df.columns and not pd.isna(df.loc[24, "elm"]):
                    max_value = df.loc[24, "elm"]
                else:
                    max_value = df[fuzzer].max()
                if pd.isna(max_value):
                    continue
                quantile_values = [max_value * q for q in quantiles]  # type: ignore
                sequence = []
                current_quantile_idx = 0
                for ten_min in range(145):
                    current_value = df.loc[ten_min, fuzzer]
                    if pd.isna(current_value):
                        continue
                    if current_value >= quantile_values[current_quantile_idx]:  # type: ignore
                        sequence.append(ten_min * 10)
                        current_quantile_idx += 1
                        if current_quantile_idx == len(quantiles):
                            break
                for i in range(current_quantile_idx, len(quantiles)):
                    sequence.append(-1)
                sequences.append(sequence)
            if not sequences:
                for quantile in quantiles:
                    to_record.loc[quantile, fuzzer] = "NEVER"
                continue
            for i, values in enumerate(zip(*sequences)):
                valid = [s for s in values if s != -1]
                quantile = quantiles[i]
                if len(valid) == 0:
                    to_record.loc[quantile, fuzzer] = "NEVER"
                else:
                    to_record.loc[quantile, fuzzer] = sum(valid) / len(valid)
        to_record.to_excel(writer, sheet_name=benchmark)