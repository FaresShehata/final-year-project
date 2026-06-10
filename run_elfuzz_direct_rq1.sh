#!/usr/bin/env bash
#
# run_elfuzz_direct_rq1.sh -- end-to-end ELFuzz-DIRECT pipeline for a single SUT:
#
#   1. direct            (elfuzz_direct, small model)  -> LLM generates inputs directly
#   2. minimize          (elfuzz_direct)               -> minimize the seed corpus
#   3. run rq1.seed_cov  (elfuzz_direct)               -> seed coverage
#   4. run rq1.afl       (elfuzz_direct)               -> AFL++ campaign
#
# Unlike the fuzzer pipeline (run_elfuzz_rq1.sh), `direct` produces the seed
# tarball itself (at extradata/seeds/raw/<SUT>/elfuzz_direct/), so there is no
# separate `produce` step -- `produce` is a no-op for elfuzz_direct.
#

set -euo pipefail

# ============================== CHOICES ====================================
SUT="jsoncpp"             # jsoncpp | libxml2 | re2 | librsvg | cvc5 | sqlite3 | cpython3

# --- direct: LLM directly synthesizes test inputs ---
DIRECT_TOTAL_TIME=18000    # wall-clock budget in seconds (-tt)
DIRECT_ITERATIONS=1000    # max iterations (-n); whichever of time/iters hits first wins
TGI_WAIT=60               # seconds to wait for the TGI server to become ready (-w)
USE_SMALL_MODEL=1         # 1 = Qwen2.5-Coder-1.5B (fits the 12GB GPU); 0 = CodeLlama-13b
DIRECT_RESUME="${DIRECT_RESUME:-0}"  # 1 = resume from the last completed gen (run: DIRECT_RESUME=1 ./run_elfuzz_direct_rq1.sh)

# --- run rq1.afl: AFL++ fuzzing campaign ---
AFL_TIME=18060           # seconds per campaign (-t); the paper uses 86400 (24h)
AFL_REPEAT=1              # repeats per fuzzer x benchmark (-r)
AFL_PARALLEL=1            # parallel campaigns (-j)

# --- identifiers ---
FUZZER="elfuzz_direct"    # fuzzer name for minimize / rq1
ELFUZZ="${ELFUZZ:-elfuzz}"  # elfuzz CLI (override: ELFUZZ=/path/to/elfuzz ./run_elfuzz_direct_rq1.sh)
# ===========================================================================

# Always operate from the project root (where this script lives).
cd "$(dirname "$(readlink -f "$0")")"

# --- Timestamped teeing -----------------------------------------------------
# Mirror everything (stdout + stderr) to the terminal AND a timestamped log
# file, with each line prefixed by the wall-clock time. Uses moreutils `ts`
# when available, otherwise a pure-bash fallback.
mkdir -p logs
LOG="logs/run_direct_${SUT}_$(date +%Y%m%d_%H%M%S).log"
# Strip ANSI colour (SGR) escape codes from the file copy only -- the live
# terminal keeps its colours, but the log stays readable (the gen banners and
# tqdm progress bars would otherwise litter it with \x1b[..m sequences).
_strip_ansi='s/\x1b\[[0-9;]*m//g'
if command -v ts >/dev/null 2>&1; then
    exec > >(ts "[%Y-%m-%d %H:%M:%S]" | tee >(sed -u "$_strip_ansi" >> "$LOG")) 2>&1
else
    exec > >(
        while IFS= read -r _line; do
            printf '[%s] %s\n' "$(date "+%Y-%m-%d %H:%M:%S")" "$_line"
        done | tee >(sed -u "$_strip_ansi" >> "$LOG")
    ) 2>&1
fi
echo "Logging to $LOG"
# ---------------------------------------------------------------------------

STAGE=""
trap 'echo >&2; echo "ERROR: pipeline failed during stage [${STAGE}] (exit $?)" >&2' ERR

PIPE_START=$(date +%s)
stage() {
    STAGE="$1"
    echo
    echo "############################################################"
    echo "# $1"
    echo "# $(date "+%Y-%m-%d %H:%M:%S")"
    echo "############################################################"
}

stage "1/4 direct -- ${FUZZER} on ${SUT}, ${DIRECT_TOTAL_TIME}s budget"
SMALL_MODEL_FLAG=()
[ "$USE_SMALL_MODEL" = "1" ] && SMALL_MODEL_FLAG=(--use-small-model)
DIRECT_RESUME_FLAG=()
[ "$DIRECT_RESUME" = "1" ] && DIRECT_RESUME_FLAG=(--resume)
"$ELFUZZ" direct -n "$DIRECT_ITERATIONS" -tt "$DIRECT_TOTAL_TIME" \
    -w "$TGI_WAIT" "${SMALL_MODEL_FLAG[@]}" "${DIRECT_RESUME_FLAG[@]}" "$SUT"

stage "2/4 minimize -- ${FUZZER} on ${SUT}"
"$ELFUZZ" minimize -T "$FUZZER" "$SUT"

stage "3/4 rq1.seed_cov -- ${FUZZER} on ${SUT}"
"$ELFUZZ" run rq1.seed_cov -T "$FUZZER" "$SUT"

stage "4/4 rq1.afl -- ${FUZZER} on ${SUT}, ${AFL_TIME}s, repeat=${AFL_REPEAT}, parallel=${AFL_PARALLEL}"
"$ELFUZZ" run rq1.afl -T "$FUZZER" -t "$AFL_TIME" -r "$AFL_REPEAT" -j "$AFL_PARALLEL" "$SUT"

STAGE="done"
echo
echo "############################################################"
echo "# Pipeline complete for ${SUT} in $(( $(date +%s) - PIPE_START ))s"
echo "############################################################"
