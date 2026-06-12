#!/usr/bin/env python3
"""Extract tidy per-SUT CSVs from an elfuzz results run, for the report's
evaluation chapter. Standard library only -- no pandas / openpyxl.

Each results run directory is expected to look like:

    <run>/
      evolution/coverage_by_generation.csv
      afl_campaign/<sut>_*_plot_data.csv
      afl_campaign/<sut>_*_fuzzer_stats.txt
      rq1/seed_cov.xlsx

Given a run directory and a tool tag (``synth`` or ``direct``), this writes into
``Report/data/<sut>/``:

  * ``<tool>_evolution.csv``  -- gen_index, population_union_edges, best_variant_edges
  * ``<tool>_afl.csv``        -- time_h, edges_found  (downsampled)
  * appends/updates a row in ``summary.csv`` keyed by tool, with the headline
    seed-coverage and final AFL statistics.

The figures in evaluation.tex read these CSVs directly via pgfplots, so adding a
new SUT/tool run is just a matter of re-running this script -- no .tex edits.

Usage:
    python extract_results.py --run "../../results/elfuzz synth jsoncpp" \
        --sut jsoncpp --tool synth
    # --sut is inferred from the run dir name if omitted.
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))

KNOWN_SUTS = ("jsoncpp", "libxml2", "re2", "librsvg", "cvc5", "sqlite3", "cpython3")


# ---------------------------------------------------------------------------
# .xlsx reading (stdlib zip + regex; openpyxl is not installed)
# ---------------------------------------------------------------------------


def _col_to_idx(col: str) -> int:
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx_sheet(path: str, sheet_name: str | None = None) -> list[list]:
    """Return a sheet as a list of rows (list of cell values).

    If *sheet_name* is given, that sheet is read; otherwise the first sheet.
    """
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        try:
            xml = z.read("xl/sharedStrings.xml").decode("utf-8", "replace")
            shared = re.findall(r"<t[^>]*>(.*?)</t>", xml, re.S)
        except KeyError:
            pass

        # Map sheet name -> r:id -> target file.
        wb = z.read("xl/workbook.xml").decode("utf-8", "replace")
        sheets = re.findall(r'<sheet[^>]*name="([^"]*)"[^>]*r:id="([^"]*)"', wb)
        rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8", "replace")
        rid_to_target = dict(
            re.findall(r'Id="([^"]*)"[^>]*Target="([^"]*)"', rels)
        )

        target = None
        if sheet_name is not None:
            for name, rid in sheets:
                if name == sheet_name:
                    target = rid_to_target.get(rid)
                    break
        if target is None and sheets:
            target = rid_to_target.get(sheets[0][1])
        if target is None:
            target = "worksheets/sheet1.xml"
        target = "xl/" + target.lstrip("/")
        sheet_xml = z.read(target).decode("utf-8", "replace")

    rows_out: list[list] = []
    for row in re.findall(r"<row[^>]*>(.*?)</row>", sheet_xml, re.S):
        cells = re.findall(
            r'<c r="([A-Z]+)\d+"(?:[^>]*t="([^"]*)")?[^>]*>(?:<v>(.*?)</v>)?', row
        )
        rowmap: dict[int, object] = {}
        for ref, t, v in cells:
            if v == "" or v is None:
                val = None
            elif t == "s":
                val = shared[int(v)]
            else:
                try:
                    fv = float(v)
                    val = int(fv) if fv.is_integer() else fv
                except ValueError:
                    val = v
            rowmap[_col_to_idx(ref)] = val
        if rowmap:
            width = max(rowmap) + 1
            rows_out.append([rowmap.get(i) for i in range(width)])
    return rows_out


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------


def extract_evolution(run: str, out_path: str) -> bool:
    """Normalise a coverage_by_generation.csv to a common schema.

    Output columns: gen_index, union_edges, best_edges.
      * union_edges = coverage held by the maintained set at that generation:
        the running pool/population union (``cumulative_union_edges``).
      * best_edges = coverage of the single strongest member that generation
        (``best_candidate_edges``).

    Both tools now share the unified header
    ``generation,gen_index,num_candidates,best_candidate_edges,gen_union_edges,
    cumulative_union_edges``; the legacy synth names are still accepted as a
    fallback for any un-converted files.
    """
    src = os.path.join(run, "evolution", "coverage_by_generation.csv")
    if not os.path.isfile(src):
        print(f"  [evolution] not found: {src}", file=sys.stderr)
        return False
    with open(src, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print(f"  [evolution] empty: {src}", file=sys.stderr)
        return False

    cols = rows[0].keys()
    # Unified schema, with the legacy synth column names as a fallback.
    union_col = "cumulative_union_edges" if "cumulative_union_edges" in cols else "population_union_edges"
    best_col = "best_candidate_edges" if "best_candidate_edges" in cols else "best_variant_edges"
    if union_col not in cols or best_col not in cols:
        print(f"  [evolution] unrecognised columns: {list(cols)}", file=sys.stderr)
        return False

    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gen_index", "union_edges", "best_edges"])
        for r in rows:
            w.writerow([r["gen_index"], r[union_col], r[best_col]])
    print(f"  [evolution] {len(rows)} gens ({union_col}, {best_col}) -> {out_path}")
    return True


def _find_plot_data(run: str) -> str | None:
    hits = glob.glob(os.path.join(run, "afl_campaign", "*plot_data.csv"))
    return hits[0] if hits else None


def extract_afl(run: str, out_path: str, max_points: int = 300) -> bool:
    src = _find_plot_data(run)
    if not src:
        print(f"  [afl] no *plot_data.csv under {run}/afl_campaign", file=sys.stderr)
        return False
    pts: list[tuple[float, int]] = []
    with open(src, newline="") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            try:
                t = float(parts[0])
                edges = int(parts[-1])  # edges_found is the last column
            except (ValueError, IndexError):
                continue
            pts.append((t, edges))
    if not pts:
        print(f"  [afl] no rows parsed from {src}", file=sys.stderr)
        return False
    # Downsample to <= max_points, always keeping the last point.
    step = max(1, len(pts) // max_points)
    sampled = pts[::step]
    if sampled[-1] != pts[-1]:
        sampled.append(pts[-1])
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_h", "edges_found"])
        for t, edges in sampled:
            w.writerow([f"{t / 3600.0:.4f}", edges])
    print(f"  [afl] {len(pts)} rows -> {len(sampled)} pts -> {out_path}")
    return True


def parse_fuzzer_stats(run: str) -> dict[str, str]:
    hits = glob.glob(os.path.join(run, "afl_campaign", "*fuzzer_stats.txt"))
    stats: dict[str, str] = {}
    if not hits:
        return stats
    with open(hits[0]) as f:
        for line in f:
            if ":" in line:
                k, _, v = line.partition(":")
                stats[k.strip()] = v.strip()
    return stats


def read_seed_cov(run: str, sut: str) -> str:
    path = os.path.join(run, "rq1", "seed_cov.xlsx")
    if not os.path.isfile(path):
        return ""
    try:
        rows = read_xlsx_sheet(path, sheet_name=sut)
    except Exception as exc:  # noqa: BLE001
        print(f"  [seed_cov] failed to read {path}: {exc}", file=sys.stderr)
        return ""
    # Layout: header row [None, 'elfuzz'], data row [0, <edges>].
    for r in rows:
        for cell in r:
            if isinstance(cell, (int, float)) and cell not in (0, 0.0):
                return str(int(cell))
    return ""


SUMMARY_FIELDS = [
    "tool",
    "seed_cov",
    "afl_edges",
    "total_edges",
    "bitmap_cvg",
    "execs",
    "execs_per_sec",
    "corpus_count",
    "crashes",
    "hangs",
]


def update_summary(out_dir: str, row: dict[str, str]) -> None:
    path = os.path.join(out_dir, "summary.csv")
    existing: dict[str, dict[str, str]] = {}
    if os.path.isfile(path):
        with open(path, newline="") as f:
            for r in csv.DictReader(f):
                existing[r["tool"]] = r
    existing[row["tool"]] = row
    # Stable order: synth first, then direct, then anything else.
    order = {"synth": 0, "direct": 1}
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        w.writeheader()
        for tool in sorted(existing, key=lambda t: (order.get(t, 99), t)):
            w.writerow({k: existing[tool].get(k, "") for k in SUMMARY_FIELDS})
    print(f"  [summary] wrote row '{row['tool']}' -> {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def infer_sut(run: str) -> str | None:
    name = os.path.basename(os.path.normpath(run)).lower()
    for s in KNOWN_SUTS:
        if s in name:
            return s
    return None


def infer_tool(run: str) -> str | None:
    name = os.path.basename(os.path.normpath(run)).lower()
    if "direct" in name:
        return "direct"
    if "synth" in name:
        return "synth"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True, help="Path to a results run directory")
    ap.add_argument("--sut", default=None, help="SUT name (inferred from --run if omitted)")
    ap.add_argument(
        "--tool", default=None, choices=["synth", "direct"],
        help="Tool tag (inferred from --run if omitted)",
    )
    ap.add_argument(
        "--out", default=None,
        help="Output base dir (default: alongside this script)",
    )
    args = ap.parse_args()

    run = args.run
    if not os.path.isdir(run):
        print(f"error: run dir not found: {run}", file=sys.stderr)
        return 1

    sut = args.sut or infer_sut(run)
    tool = args.tool or infer_tool(run)
    if not sut:
        print("error: could not infer --sut; pass it explicitly", file=sys.stderr)
        return 1
    if not tool:
        print("error: could not infer --tool; pass it explicitly", file=sys.stderr)
        return 1

    out_base = args.out or HERE
    out_dir = os.path.join(out_base, sut)
    os.makedirs(out_dir, exist_ok=True)
    print(f"Extracting {sut}/{tool} from {run}")

    extract_evolution(run, os.path.join(out_dir, f"{tool}_evolution.csv"))
    extract_afl(run, os.path.join(out_dir, f"{tool}_afl.csv"))

    stats = parse_fuzzer_stats(run)
    row = {
        "tool": tool,
        "seed_cov": read_seed_cov(run, sut),
        "afl_edges": stats.get("edges_found", ""),
        "total_edges": stats.get("total_edges", ""),
        "bitmap_cvg": stats.get("bitmap_cvg", ""),
        "execs": stats.get("execs_done", ""),
        "execs_per_sec": stats.get("execs_per_sec", ""),
        "corpus_count": stats.get("corpus_count", ""),
        "crashes": stats.get("saved_crashes", ""),
        "hangs": stats.get("saved_hangs", ""),
    }
    update_summary(out_dir, row)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
