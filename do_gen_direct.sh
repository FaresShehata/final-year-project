#!/bin/bash
# Per-generation pipeline for `elfuzz direct` mode.
#
# Sibling of do_gen.sh, but operates on directories of inputs (collections)
# rather than Python fuzzer programs. Coverage and selection treat each
# collection (directory) as a single unit.

set -euo pipefail

prev_gen="$1"
next_gen="$2"

LLM_BACKEND="${ELMFUZZ_LLM_BACKEND:-huggingface}"
MODEL_TOKEN="direct"   # fixed token — used as the {MODEL} placeholder in paths

if [ "$LLM_BACKEND" = "copilot" ]; then
    LLM_MODEL_NAME="${ELMFUZZ_COPILOT_MODEL:-gpt-4.1}"
    ENDPOINT_ARGS=()
else
    # Pick the first registered HF model + its endpoint.
    LLM_MODEL_NAME="${ELFUZZ_DIRECT_HF_MODEL_OVERRIDE:-$(./elmconfig.py get model.names | awk '{print $1}')}"
    raw_endpoint_pairs=$(./elmconfig.py get model.endpoints)
    # endpoints are "<model>:<url>" pairs separated by spaces. Find the URL
    # for $LLM_MODEL_NAME.
    LLM_ENDPOINT=""
    for pair in $raw_endpoint_pairs ; do
        name=${pair%%:*}
        url=${pair#*:}
        if [ "$name" = "$LLM_MODEL_NAME" ]; then
            LLM_ENDPOINT="$url"
            break
        fi
    done
    if [ -z "$LLM_ENDPOINT" ]; then
        # Fall back to the first endpoint regardless of name match.
        first_pair=$(echo "$raw_endpoint_pairs" | awk '{print $1}')
        LLM_ENDPOINT=${first_pair#*:}
    fi
    ENDPOINT_ARGS=(-E "$LLM_ENDPOINT")
fi

NUM_VARIANTS=${ELFUZZ_DIRECT_NUM_VARIANTS:-20}
M=${ELFUZZ_DIRECT_INPUTS_PER_COLLECTION:-50}
EXT=${ELFUZZ_DIRECT_INPUT_EXTENSION:-.bin}
FMT_NAME="${ELFUZZ_DIRECT_FORMAT_NAME:-text}"
FMT_DESC="${ELFUZZ_DIRECT_FORMAT_DESCRIPTION:-text input}"
NUM_SELECTED=$(./elmconfig.py get run.num_selected)
LOGDIR=$(./elmconfig.py get run.logdir -s GEN=${next_gen})

COLOR_GREEN='\033[0;32m'
COLOR_RESET='\033[0m'
printf "$COLOR_GREEN"'============> %s: %6s -> %6s (direct) <============'"$COLOR_RESET"'\n' "$ELMFUZZ_RUN_NAME" "$prev_gen" "$next_gen"

mkdir -p "$ELMFUZZ_RUNDIR/${next_gen}/variants/$MODEL_TOKEN"
mkdir -p "$ELMFUZZ_RUNDIR/${next_gen}/seeds"
mkdir -p "$LOGDIR/meta"

_step_start() { echo "[do_gen_direct] step: $1  ($(date '+%H:%M:%S'))"; _STEP_T=$(date +%s); }
_step_end()   { echo "[do_gen_direct] done in $(( $(date +%s) - _STEP_T ))s"; }

# ---- 1. Seed selection ----------------------------------------------------
_step_start "seed selection"
seed_num=0
if [ "$prev_gen" = "initial" ]; then
    echo "First generation; copying initial collections to ${next_gen}/seeds"
    cp -r "$ELMFUZZ_RUNDIR"/initial/seeds/coll_* "$ELMFUZZ_RUNDIR/${next_gen}/seeds/" 2>/dev/null || true
else
    cov_file="$ELMFUZZ_RUNDIR/${prev_gen}/logs/coverage.json"
    input_elite_file="$ELMFUZZ_RUNDIR/${prev_gen}/logs/elites.json"
    output_elite_file="$ELMFUZZ_RUNDIR/${next_gen}/logs/elites.json"

    python select_seeds_direct.py -g "$prev_gen" -n "$NUM_SELECTED" \
        -c "$cov_file" -i "$input_elite_file" -o "$output_elite_file" \
        | while read cov gen model generator ; do
              src="$ELMFUZZ_RUNDIR/${gen}/variants/${model}/${generator}"
              dst="$ELMFUZZ_RUNDIR/${next_gen}/seeds/${gen}_${generator}"
              if [ -d "$src" ]; then
                  echo "Selecting $generator from $gen with $cov edges covered"
                  cp -r "$src" "$dst"
              else
                  echo "WARNING: elite source $src not found; skipping"
              fi
          done

    # No-elites fallback: if nothing was copied (either elites.json was empty
    # or all elite sources were missing), carry the previous gen's seeds
    # forward verbatim so that the loop can keep iterating.
    if [ -z "$(ls -A "$ELMFUZZ_RUNDIR/${next_gen}/seeds" 2>/dev/null)" ]; then
        echo "WARNING: no proper elites for ${next_gen}; carrying previous seeds forward"
        cp -r "$ELMFUZZ_RUNDIR/${prev_gen}/seeds"/* "$ELMFUZZ_RUNDIR/${next_gen}/seeds/" 2>/dev/null || true
    fi
fi

_step_end
seed_num=$(find "$ELMFUZZ_RUNDIR/${next_gen}/seeds" -maxdepth 1 -mindepth 1 -type d | wc -l)
if [ "$seed_num" -eq 0 ]; then
    echo "ERROR: no parent collections available for ${next_gen}; aborting"
    exit 1
fi

echo "Spawning $NUM_VARIANTS variant collections (M=$M inputs each) via $LLM_BACKEND ($LLM_MODEL_NAME)"

# ---- 3. LLM-direct mutation -----------------------------------------------
_step_start "LLM mutation ($NUM_VARIANTS variants)"
output_dir="$ELMFUZZ_RUNDIR/${next_gen}/variants/$MODEL_TOKEN"

python direct_mutate.py \
    --backend "$LLM_BACKEND" \
    -M "$LLM_MODEL_NAME" \
    "${ENDPOINT_ARGS[@]}" \
    --output-dir "$output_dir" \
    --log-dir "$LOGDIR/meta" \
    -n "$NUM_VARIANTS" \
    --inputs-per-collection "$M" \
    --input-extension "$EXT" \
    --format-name "$FMT_NAME" \
    --format-description "$FMT_DESC" \
    "$ELMFUZZ_RUNDIR/${next_gen}/seeds"/*/

_step_end
# ---- 4. Coverage collection ----------------------------------------------
_step_start "coverage collection"
# getcov_fuzzbench.py performs `shutil.move(input, ...)` which destroys the
# source directory. Stage a COPY of the variants tree so the persistent
# variants/ tree survives the run.
variants_dir="$ELMFUZZ_RUNDIR/${next_gen}/variants"

if [ "${TYPE:-}" = "fuzzbench" ] || [ "${TYPE:-}" = "oss-fuzz" ] || [ "${TYPE:-}" = "docker" ]; then
    cov_staging="$ELMFUZZ_RUNDIR/${next_gen}/.cov_staging"
    rm -rf "$cov_staging"
    mkdir -p "$cov_staging"
    cp -r "$variants_dir/$MODEL_TOKEN" "$cov_staging/$MODEL_TOKEN"
    python getcov_fuzzbench.py \
        --image elmfuzz/"$PROJECT_NAME" \
        --input "$cov_staging" \
        --covfile "${LOGDIR}/coverage.json"
    rm -rf "$cov_staging"
else
    python getcov.py -O "${LOGDIR}/coverage.json" "$variants_dir"
fi

_step_end
# ---- 5. Stamp -------------------------------------------------------------
mkdir -p "$ELMFUZZ_RUNDIR/stamps"
touch "$ELMFUZZ_RUNDIR/stamps/${next_gen}.stamp"
