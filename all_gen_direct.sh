#!/bin/bash
# Outer orchestration loop for `elfuzz direct` mode.
#
# Single growing pool of inputs at $ELMFUZZ_RUNDIR/pool/. The initial step
# uses the LLM to generate inputs from scratch; per-generation steps mutate
# the pool, evaluate per-input coverage, and add/replace/discard candidates.

set -euo pipefail

if [ "$#" -eq 1 ]; then
    start_gen=-1
elif [ "$#" -eq 2 ]; then
    start_gen=$2
else
    echo "Usage: $0 rundir [start_gen]"
    exit 1
fi

export ELMFUZZ_RUNDIR="$1"
export ELMFUZZ_RUN_NAME=$(basename "$ELMFUZZ_RUNDIR")

if [ -n "${NUM_GENERATIONS:-}" ]; then
    num_gens=${NUM_GENERATIONS}
else
    num_gens=$(./elmconfig.py get run.num_generations)
fi
last_gen=$((num_gens - 1))

genout_dir=$(./elmconfig.py get run.genoutput_dir -s GEN=. -s MODEL=.)
export ENDPOINTS=$(./elmconfig.py get model.endpoints)
export TYPE=$(./elmconfig.py get type)
export PROJECT_NAME=$(./elmconfig.py get project_name)
genout_dir=$(realpath -m "$genout_dir")

LLM_BACKEND="${ELMFUZZ_LLM_BACKEND:-huggingface}"

# Warn on retired env vars so users update their configs.
for retired in \
    ELFUZZ_DIRECT_NUM_INITIAL_COLLECTIONS \
    ELFUZZ_DIRECT_NUM_VARIANTS \
    ELFUZZ_DIRECT_INPUTS_PER_COLLECTION ; do
    if [ -n "${!retired:-}" ]; then
        echo "[all_gen_direct] WARNING: $retired is no longer used in single-pool mode; ignoring." >&2
        echo "[all_gen_direct]          Set ELFUZZ_DIRECT_NUM_INITIAL_INPUTS / ELFUZZ_DIRECT_NUM_CANDIDATES_PER_GEN instead." >&2
    fi
done

NUM_INITIAL_INPUTS=${ELFUZZ_DIRECT_NUM_INITIAL_INPUTS:-1000}
INPUT_EXTENSION=${ELFUZZ_DIRECT_INPUT_EXTENSION:-.bin}
HF_INITIAL_PREFIX=${ELFUZZ_DIRECT_HF_INITIAL_PREFIX:-}
FMT_NAME=${ELFUZZ_DIRECT_FORMAT_NAME:-text}
FMT_DESC=${ELFUZZ_DIRECT_FORMAT_DESCRIPTION:-text input}
MODEL_TOKEN="direct"

if [ "$LLM_BACKEND" = "copilot" ]; then
    LLM_MODEL_NAME="${ELMFUZZ_COPILOT_MODEL:-gpt-4.1}"
    INITIAL_ENDPOINT_ARGS=()
else
    LLM_MODEL_NAME="${ELFUZZ_DIRECT_HF_MODEL_OVERRIDE:-$(./elmconfig.py get model.names | awk '{print $1}')}"
    LLM_ENDPOINT=""
    for pair in $ENDPOINTS ; do
        name=${pair%%:*}
        url=${pair#*:}
        if [ "$name" = "$LLM_MODEL_NAME" ]; then
            LLM_ENDPOINT="$url"
            break
        fi
    done
    if [ -z "$LLM_ENDPOINT" ]; then
        first_pair=$(echo "$ENDPOINTS" | awk '{print $1}')
        LLM_ENDPOINT=${first_pair#*:}
    fi
    INITIAL_ENDPOINT_ARGS=(-E "$LLM_ENDPOINT")
fi

should_clean=$(./elmconfig.py get run.clean)
if [ -d "$genout_dir" ]; then
    if [ "$should_clean" = "True" ]; then
        echo "Removing generated outputs in $genout_dir"
        rm -rf "$genout_dir"
    else
        echo "Generated output directory $genout_dir already exists; exiting."
        echo "Set run.clean to True to remove existing rundirs."
        exit 1
    fi
fi
if [ "$start_gen" -eq -1 ]; then
    for pat in "gen*" "initial" "stamps" "pool"; do
        if compgen -G "$ELMFUZZ_RUNDIR"/$pat > /dev/null; then
            if [ "$should_clean" = "True" ]; then
                echo "Removing existing rundir(s):" "$ELMFUZZ_RUNDIR"/$pat
                rm -rf "$ELMFUZZ_RUNDIR"/$pat
            else
                echo "Found existing rundir(s):" "$ELMFUZZ_RUNDIR"/$pat
                echo "Set run.clean to True to remove existing rundirs."
                exit 1
            fi
        fi
    done
fi

if [ "$TYPE" = "fuzzbench" ]; then
    python prepare_fuzzbench.py
elif [ "$TYPE" = "oss-fuzz" ]; then
    python prepare_fuzzbench.py -d /home/appuser/oss-fuzz -t oss-fuzz
elif [ "$TYPE" = "docker" ]; then
    python prepare_fuzzbench.py -t docker
fi

_run_gen() {
    local prev="$1" next="$2" gen_num="$3"
    local t_start
    t_start=$(date +%s)
    echo "================================================================"
    echo "[all_gen_direct] Generation $gen_num / $num_gens  ($prev -> $next)  started at $(date '+%H:%M:%S')"
    echo "================================================================"
    ./do_gen_direct.sh "$prev" "$next"
    local t_end elapsed
    t_end=$(date +%s)
    elapsed=$(( t_end - t_start ))
    echo "[all_gen_direct] Generation $gen_num / $num_gens  done in ${elapsed}s"
}

_bootstrap_pool() {
    mkdir -p "$ELMFUZZ_RUNDIR/initial/inputs"
    mkdir -p "$ELMFUZZ_RUNDIR/initial/candidates/$MODEL_TOKEN"
    mkdir -p "$ELMFUZZ_RUNDIR/initial/logs"
    mkdir -p "$ELMFUZZ_RUNDIR/pool/inputs"
    mkdir -p "$ELMFUZZ_RUNDIR/stamps"

    echo "===================================================================="
    echo "Generating initial seed corpus via LLM ($LLM_BACKEND, $LLM_MODEL_NAME)"
    echo "  $NUM_INITIAL_INPUTS inputs (flat)"
    echo "===================================================================="
    local t_init
    t_init=$(date +%s)

    python direct_initial.py \
        --output-dir "$ELMFUZZ_RUNDIR/initial/inputs" \
        --backend "$LLM_BACKEND" \
        -M "$LLM_MODEL_NAME" \
        "${INITIAL_ENDPOINT_ARGS[@]}" \
        --num-initial-inputs "$NUM_INITIAL_INPUTS" \
        --input-extension "$INPUT_EXTENSION" \
        --format-name "$FMT_NAME" \
        --format-description "$FMT_DESC" \
        --hf-initial-prefix "$HF_INITIAL_PREFIX"

    # Wrap each initial input into its own per-candidate dir so coverage
    # tooling produces one entry per input.
    echo "[all_gen_direct] wrapping initial inputs for per-input coverage"
    local idx=0
    for f in "$ELMFUZZ_RUNDIR"/initial/inputs/*; do
        [ -f "$f" ] || continue
        local cid
        cid=$(printf 'cand_%08d' "$idx")
        mkdir -p "$ELMFUZZ_RUNDIR/initial/candidates/$MODEL_TOKEN/$cid"
        cp "$f" "$ELMFUZZ_RUNDIR/initial/candidates/$MODEL_TOKEN/$cid/input_$(printf '%08d' "$idx")${INPUT_EXTENSION}"
        idx=$((idx + 1))
    done

    echo "[all_gen_direct] computing initial coverage"
    if [ "${TYPE:-}" = "fuzzbench" ] || [ "${TYPE:-}" = "oss-fuzz" ] || [ "${TYPE:-}" = "docker" ]; then
        local cov_staging="$ELMFUZZ_RUNDIR/initial/.cov_staging"
        rm -rf "$cov_staging"
        mkdir -p "$cov_staging"
        cp -r "$ELMFUZZ_RUNDIR/initial/candidates/$MODEL_TOKEN" "$cov_staging/$MODEL_TOKEN"
        python getcov_fuzzbench.py \
            --image elmfuzz/"$PROJECT_NAME" \
            --input "$cov_staging" \
            --covfile "$ELMFUZZ_RUNDIR/initial/logs/coverage.json"
        rm -rf "$cov_staging"
    else
        python getcov.py -O "$ELMFUZZ_RUNDIR/initial/logs/coverage.json" \
            "$ELMFUZZ_RUNDIR/initial/candidates"
    fi

    echo "[all_gen_direct] seeding pool from initial coverage"
    python direct_curate.py \
        --pool-dir "$ELMFUZZ_RUNDIR/pool" \
        --candidates-dir "$ELMFUZZ_RUNDIR/initial/candidates" \
        --covfile "$ELMFUZZ_RUNDIR/initial/logs/coverage.json" \
        --model-token "$MODEL_TOKEN" \
        --input-extension "$INPUT_EXTENSION" \
        --decisions-out "$ELMFUZZ_RUNDIR/initial/logs/decisions.json" \
        --bootstrap

    touch "$ELMFUZZ_RUNDIR/stamps/initial.stamp"

    echo "[all_gen_direct] Initial corpus done in $(( $(date +%s) - t_init ))s"
}

if [ "$start_gen" -eq -1 ]; then
    _bootstrap_pool
    _run_gen initial gen0 0
    for i in $(seq 0 $last_gen); do
        _run_gen "gen$i" "gen$((i+1))" "$((i+1))"
    done
else
    if [ "$start_gen" -eq 0 ]; then
        real_start_gen=0
        _run_gen initial gen0 0
    else
        real_start_gen=$((start_gen-1))
    fi
    for i in $(seq $real_start_gen $last_gen); do
        _run_gen "gen$i" "gen$((i+1))" "$((i+1))"
    done
fi
