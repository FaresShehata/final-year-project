#!/bin/bash
# Per-generation pipeline for `elfuzz direct` mode.
#
# Operates on a single growing pool of inputs at $ELMFUZZ_RUNDIR/pool/.
# Each generation:
#   1. Mutates pool inputs via the LLM into per-candidate dirs.
#   2. Computes per-candidate coverage via the existing per-generator tooling.
#   3. Curates the pool: add new-coverage candidates, replace strictly inferior
#      pool inputs, discard the rest.

set -euo pipefail

prev_gen="$1"
next_gen="$2"

LLM_BACKEND="${ELMFUZZ_LLM_BACKEND:-huggingface}"
MODEL_TOKEN="direct"

if [ "$LLM_BACKEND" = "copilot" ]; then
    LLM_MODEL_NAME="${ELMFUZZ_COPILOT_MODEL:-gpt-4.1}"
    ENDPOINT_ARGS=()
else
    LLM_MODEL_NAME="${ELFUZZ_DIRECT_HF_MODEL_OVERRIDE:-$(./elmconfig.py get model.names | awk '{print $1}')}"
    raw_endpoint_pairs=$(./elmconfig.py get model.endpoints)
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
        first_pair=$(echo "$raw_endpoint_pairs" | awk '{print $1}')
        LLM_ENDPOINT=${first_pair#*:}
    fi
    ENDPOINT_ARGS=(-E "$LLM_ENDPOINT")
fi

NUM_CANDIDATES=${ELFUZZ_DIRECT_NUM_CANDIDATES_PER_GEN:-500}
EXT=${ELFUZZ_DIRECT_INPUT_EXTENSION:-.bin}
FMT_NAME="${ELFUZZ_DIRECT_FORMAT_NAME:-text}"
FMT_DESC="${ELFUZZ_DIRECT_FORMAT_DESCRIPTION:-text input}"
LOGDIR=$(./elmconfig.py get run.logdir -s GEN=${next_gen})

POOL_DIR="$ELMFUZZ_RUNDIR/pool"

COLOR_GREEN='\033[0;32m'
COLOR_RESET='\033[0m'
printf "$COLOR_GREEN"'============> %s: %6s -> %6s (direct) <============'"$COLOR_RESET"'\n' "$ELMFUZZ_RUN_NAME" "$prev_gen" "$next_gen"

mkdir -p "$ELMFUZZ_RUNDIR/${next_gen}/candidates/$MODEL_TOKEN"
mkdir -p "$LOGDIR"
mkdir -p "$POOL_DIR/inputs"

_step_start() { echo "[do_gen_direct] step: $1  ($(date '+%H:%M:%S'))"; _STEP_T=$(date +%s); }
_step_end()   { echo "[do_gen_direct] done in $(( $(date +%s) - _STEP_T ))s"; }

# ---- 1. Pool sanity check -------------------------------------------------
pool_size=$(find "$POOL_DIR/inputs" -maxdepth 1 -type f | wc -l)
if [ "$pool_size" -eq 0 ]; then
    echo "ERROR: pool is empty at $POOL_DIR/inputs; cannot mutate"
    exit 1
fi
echo "[do_gen_direct] pool size = $pool_size"

# ---- 2. LLM mutation ------------------------------------------------------
_step_start "LLM mutation ($NUM_CANDIDATES candidates)"
candidates_root="$ELMFUZZ_RUNDIR/${next_gen}/candidates"
output_dir="$candidates_root/$MODEL_TOKEN"

python direct_mutate.py \
    --backend "$LLM_BACKEND" \
    -M "$LLM_MODEL_NAME" \
    "${ENDPOINT_ARGS[@]}" \
    --pool-dir "$POOL_DIR/inputs" \
    --output-dir "$output_dir" \
    -n "$NUM_CANDIDATES" \
    --input-extension "$EXT" \
    --format-name "$FMT_NAME" \
    --format-description "$FMT_DESC"

_step_end

# ---- 3. Coverage collection ----------------------------------------------
_step_start "coverage collection"

if [ "${TYPE:-}" = "fuzzbench" ] || [ "${TYPE:-}" = "oss-fuzz" ] || [ "${TYPE:-}" = "docker" ]; then
    # getcov_fuzzbench.py uses shutil.move on the input; stage a copy so the
    # persistent candidates tree survives.
    cov_staging="$ELMFUZZ_RUNDIR/${next_gen}/.cov_staging"
    rm -rf "$cov_staging"
    mkdir -p "$cov_staging"
    cp -r "$candidates_root/$MODEL_TOKEN" "$cov_staging/$MODEL_TOKEN"
    python getcov_fuzzbench.py \
        --image elmfuzz/"$PROJECT_NAME" \
        --input "$cov_staging" \
        --covfile "${LOGDIR}/coverage.json"
    rm -rf "$cov_staging"
else
    python getcov.py -O "${LOGDIR}/coverage.json" "$candidates_root"
fi

_step_end

# ---- 4. Pool curation -----------------------------------------------------
_step_start "pool curation"
python direct_curate.py \
    --pool-dir "$POOL_DIR" \
    --candidates-dir "$candidates_root" \
    --covfile "${LOGDIR}/coverage.json" \
    --model-token "$MODEL_TOKEN" \
    --input-extension "$EXT" \
    --decisions-out "${LOGDIR}/decisions.json"
_step_end

# ---- 5. Stamp -------------------------------------------------------------
mkdir -p "$ELMFUZZ_RUNDIR/stamps"
touch "$ELMFUZZ_RUNDIR/stamps/${next_gen}.stamp"
