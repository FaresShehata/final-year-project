#!/usr/bin/env python3
"""Pool curator for `elfuzz direct` single-pool evolution.

Two modes:

* ``--bootstrap``: ingest the *initial* candidates coverage map and seed the
  pool (``$pool_dir/inputs/`` + ``$pool_dir/index.json``) from candidates with
  non-empty coverage.
* default: ingest a per-generation candidates coverage map, apply the
  add/replace/discard decision rule for each candidate against the current
  pool, and update the pool in place. Writes ``decisions.json`` summarising
  every candidate's fate.

The candidates tree is shaped to match the existing per-generator coverage
contract: ``<candidates_dir>/<MODEL_TOKEN>/<cand_id>/input_<cand_id><ext>``.
Coverage JSON is therefore ``{ MODEL_TOKEN: { cand_id: [edge, ...] } }``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys


def superior_than(edges1: set[str], edges2: set[str]) -> bool:
    """edges1 strictly Pareto-dominates edges2 (strict superset, more edges)."""
    return len(edges1) > len(edges2) and (
        (not edges2) or edges2.issubset(edges1)
    )


def equal_to(edges1: set[str], edges2: set[str]) -> bool:
    return edges1 == edges2


def parse_edges(raw: list[str]) -> set[str]:
    return set(e.split(":", 1)[0] for e in raw)


def load_index(index_path: str) -> dict[str, dict]:
    if not os.path.exists(index_path):
        return {}
    with open(index_path, "r") as f:
        raw = json.load(f)
    return raw


def save_index(index_path: str, index: dict[str, dict]) -> None:
    tmp = index_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(index, f)
    os.replace(tmp, index_path)


def find_candidate_file(candidates_dir: str, model_token: str, cand_id: str) -> str | None:
    cdir = os.path.join(candidates_dir, model_token, cand_id)
    if not os.path.isdir(cdir):
        return None
    files = [
        f for f in os.listdir(cdir) if os.path.isfile(os.path.join(cdir, f))
    ]
    if not files:
        return None
    files.sort()
    return os.path.join(cdir, files[0])


def allocate_id(pool_dir: str) -> str:
    counter_path = os.path.join(pool_dir, "next_id")
    if os.path.exists(counter_path):
        with open(counter_path, "r") as f:
            n = int(f.read().strip() or "0")
    else:
        n = 0
    new_id = f"input_{n:08d}"
    with open(counter_path, "w") as f:
        f.write(str(n + 1))
    return new_id


def copy_to_pool(
    pool_dir: str, src: str, ext: str
) -> tuple[str, str]:
    """Copy *src* into the pool under a fresh id; return (new_id, new_path)."""
    new_id = allocate_id(pool_dir)
    dst = os.path.join(pool_dir, "inputs", f"{new_id}{ext}")
    shutil.copyfile(src, dst)
    return new_id, dst


def remove_from_pool(pool_dir: str, input_id: str, ext: str) -> None:
    p = os.path.join(pool_dir, "inputs", f"{input_id}{ext}")
    try:
        os.remove(p)
    except FileNotFoundError:
        pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pool-dir", required=True, help="Path to $ELMFUZZ_RUNDIR/pool")
    p.add_argument("--candidates-dir", required=True,
                   help="Path holding <MODEL_TOKEN>/<cand_id>/<file> subtree")
    p.add_argument("--covfile", required=True, help="Coverage JSON to ingest")
    p.add_argument("--model-token", default="direct")
    p.add_argument("--input-extension", required=True)
    p.add_argument("--decisions-out", default=None,
                   help="Write a JSON summary of decisions here")
    p.add_argument("--bootstrap", action="store_true",
                   help="Seed the pool from scratch (initial generation)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    pool_dir = args.pool_dir
    os.makedirs(os.path.join(pool_dir, "inputs"), exist_ok=True)
    index_path = os.path.join(pool_dir, "index.json")

    with open(args.covfile, "r") as f:
        cov_raw = json.load(f)

    cov = {
        cand_id: parse_edges(edges)
        for cand_id, edges in cov_raw.get(args.model_token, {}).items()
    }

    decisions: dict[str, dict] = {}

    if args.bootstrap:
        index: dict[str, dict] = {}
        for cand_id, edges in cov.items():
            src = find_candidate_file(args.candidates_dir, args.model_token, cand_id)
            if src is None:
                decisions[cand_id] = {"action": "discard", "reason": "missing-file"}
                continue
            if not edges:
                decisions[cand_id] = {"action": "discard", "reason": "no-coverage"}
                continue
            new_id, _ = copy_to_pool(pool_dir, src, args.input_extension)
            size = os.path.getsize(src) or 1
            index[new_id] = {"edges": sorted(edges), "size": size}
            decisions[cand_id] = {"action": "add", "new_id": new_id}
        save_index(index_path, index)
        added = sum(1 for d in decisions.values() if d["action"] == "add")
        discarded = sum(1 for d in decisions.values() if d["action"] == "discard")
        print(f"[direct_curate] bootstrap: added={added} discarded={discarded} "
              f"pool_size={len(index)}", file=sys.stderr)
    else:
        index_raw = load_index(index_path)
        # working sets
        index: dict[str, dict] = {
            k: {"edges": set(v["edges"]), "size": v["size"]}
            for k, v in index_raw.items()
        }
        pool_union: set[str] = set()
        for v in index.values():
            pool_union.update(v["edges"])

        added = replaced = discarded = 0

        # Stable processing order — sorted by candidate id.
        for cand_id in sorted(cov.keys()):
            edges = cov[cand_id]
            src = find_candidate_file(args.candidates_dir, args.model_token, cand_id)
            if src is None:
                decisions[cand_id] = {"action": "discard", "reason": "missing-file"}
                discarded += 1
                continue
            if not edges:
                decisions[cand_id] = {"action": "discard", "reason": "no-coverage"}
                discarded += 1
                continue

            size = os.path.getsize(src) or 1

            new_edges_added = edges - pool_union
            if new_edges_added:
                new_id, _ = copy_to_pool(pool_dir, src, args.input_extension)
                index[new_id] = {"edges": set(edges), "size": size}
                pool_union.update(edges)
                evicted: list[str] = []
                # Evict any pool inputs strictly dominated by the new one.
                # Skip the just-added entry.
                for pid, pv in list(index.items()):
                    if pid == new_id:
                        continue
                    if superior_than(edges, pv["edges"]) or (
                        equal_to(edges, pv["edges"]) and size < pv["size"]
                    ):
                        remove_from_pool(pool_dir, pid, args.input_extension)
                        del index[pid]
                        evicted.append(pid)
                decisions[cand_id] = {
                    "action": "add",
                    "new_id": new_id,
                    "evicted": evicted,
                    "new_edges": len(new_edges_added),
                }
                added += 1
                continue

            # Find best (largest dominated-edge-gap) existing input to replace.
            best_target: str | None = None
            best_gap = -1
            for pid, pv in index.items():
                if superior_than(edges, pv["edges"]):
                    gap = len(edges) - len(pv["edges"])
                    if gap > best_gap:
                        best_gap = gap
                        best_target = pid
                elif equal_to(edges, pv["edges"]) and size < pv["size"]:
                    gap = max(best_gap, 0)
                    if best_target is None or gap > best_gap:
                        best_gap = gap
                        best_target = pid

            if best_target is not None:
                remove_from_pool(pool_dir, best_target, args.input_extension)
                del index[best_target]
                new_id, _ = copy_to_pool(pool_dir, src, args.input_extension)
                index[new_id] = {"edges": set(edges), "size": size}
                # pool_union may shrink if removed target had unique edges
                # that the replacement still covers (it does by superset).
                # Recompute defensively.
                pool_union = set()
                for v in index.values():
                    pool_union.update(v["edges"])
                decisions[cand_id] = {
                    "action": "replace",
                    "new_id": new_id,
                    "old_id": best_target,
                }
                replaced += 1
            else:
                decisions[cand_id] = {"action": "discard", "reason": "redundant"}
                discarded += 1

        # serialise sets back to lists
        out = {
            k: {"edges": sorted(v["edges"]), "size": v["size"]}
            for k, v in index.items()
        }
        save_index(index_path, out)
        print(f"[direct_curate] gen: added={added} replaced={replaced} "
              f"discarded={discarded} pool_size={len(index)}", file=sys.stderr)

    if args.decisions_out:
        with open(args.decisions_out, "w") as f:
            json.dump(decisions, f)

    return 0


if __name__ == "__main__":
    sys.exit(main())
