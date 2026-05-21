import pandas as pd
import re
import os
PWD = os.path.dirname(os.path.abspath(__file__))

def convert_time(time_str) -> float:
    if time_str == "-1":
        return -1
    pattern = r"(\d+(?:\.\d+)?)(h|min|s|day)"
    matches = re.findall(pattern, time_str)
    total_seconds = 0
    for match in matches:
        value = float(match[0])
        unit = match[1]
        if unit == "h":
            total_seconds += value * 3600
        elif unit == "min":
            total_seconds += value * 60
        elif unit == "s":
            total_seconds += value
        elif unit == "day":
            total_seconds += value * 86400
    return total_seconds

FUZZERS = ["elm", "glade", "islearn"]

df = pd.read_csv(os.path.join(PWD, "record.csv"), index_col=0, header=0)
new_df = pd.DataFrame(columns=[*FUZZERS], index=df.index)

for index, row in df.iterrows():
    for fuzzer in FUZZERS:
        converted = convert_time(row[fuzzer])
        new_df.loc[str(index), fuzzer] = converted if converted > 0 else None

new_df.to_csv(os.path.join(PWD, "x_record_second.csv"), index=True)
