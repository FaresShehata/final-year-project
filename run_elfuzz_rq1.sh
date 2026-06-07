#!/usr/bin/env bash
#
# run_elfuzz_rq1.sh -- end-to-end ELFuzz pipeline for a single SUT:
#
#   1. synth             (fuzzer.elfuzz, small model)  -> evolve input generators
#   2. produce           (elfuzz)                      -> run generators -> seed corpus
#   3. minimize          (elfuzz)                      -> minimize the corpus
#   4. run rq1.seed_cov  (elfuzz)                      -> seed coverage
#   5. run rq1.afl       (elfuzz)                      -> AFL++ campaign
#

set -euo pipefail

# ============================== CHOICES ====================================
SUT="jsoncpp"             # jsoncpp | libxml2 | re2 | librsvg | cvc5 | sqlite3 | cpython3

# --- synth: LLM-driven evolution of the input generators ---
SYNTH_TOTAL_TIME=8050     # wall-clock budget in seconds (-tt)
SYNTH_ITERATIONS=1000       # max generations (-n); whichever of time/iters hits first wins
TGI_WAIT=60               # seconds to wait for the TGI server to become ready (-w)
SYNTH_RESUME="${SYNTH_RESUME:-0}"  # 1 = resume evolution from the last completed gen (run: SYNTH_RESUME=1 ./run_elfuzz_rq1.sh)

# --- produce: run the synthesized generators into a seed corpus ---
PRODUCE_TOTAL_TIME=200    # wall-clock budget in seconds (-tt)

# --- run rq1.afl: AFL++ fuzzing campaign ---
AFL_TIME=21660             # seconds per campaign (-t); the paper uses 86400 (24h)
AFL_REPEAT=1              # repeats per fuzzer x benchmark (-r)
AFL_PARALLEL=1            # parallel campaigns (-j)

# --- identifiers  ---
TARGET="fuzzer.elfuzz"    # synth target
FUZZER="elfuzz"           # fuzzer name for produce / minimize / rq1
ELFUZZ="${ELFUZZ:-elfuzz}"  # elfuzz CLI (override: ELFUZZ=/path/to/elfuzz ./run_elfuzz_rq1.sh)
# ===========================================================================

# Always operate from the project root (where this script lives).
cd "$(dirname "$(readlink -f "$0")")"

# --- Timestamped teeing -----------------------------------------------------
# Mirror everything (stdout + stderr) to the terminal AND a timestamped log
# file, with each line prefixed by the wall-clock time. Uses moreutils `ts`
# when available, otherwise a pure-bash fallback.
mkdir -p logs
LOG="logs/run_${SUT}_$(date +%Y%m%d_%H%M%S).log"
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

# stage "1/5 synth -- ${TARGET} on ${SUT}, ${SYNTH_TOTAL_TIME}s budget, small model"
# SYNTH_RESUME_FLAG=()
# [ "$SYNTH_RESUME" = "1" ] && SYNTH_RESUME_FLAG=(--resume)
# "$ELFUZZ" synth -T "$TARGET" -n "$SYNTH_ITERATIONS" -tt "$SYNTH_TOTAL_TIME" \
#     -w "$TGI_WAIT" --use-small-model "${SYNTH_RESUME_FLAG[@]}" "$SUT"

stage "2/5 produce -- ${FUZZER} on ${SUT}, ${PRODUCE_TOTAL_TIME}s budget"
"$ELFUZZ" produce -T "$FUZZER" -tt "$PRODUCE_TOTAL_TIME" "$SUT"

stage "3/5 minimize -- ${FUZZER} on ${SUT}"
"$ELFUZZ" minimize -T "$FUZZER" "$SUT"

stage "4/5 rq1.seed_cov -- ${FUZZER} on ${SUT}"
"$ELFUZZ" run rq1.seed_cov -T "$FUZZER" "$SUT"

stage "5/5 rq1.afl -- ${FUZZER} on ${SUT}, ${AFL_TIME}s, repeat=${AFL_REPEAT}, parallel=${AFL_PARALLEL}"
"$ELFUZZ" run rq1.afl -T "$FUZZER" -t "$AFL_TIME" -r "$AFL_REPEAT" -j "$AFL_PARALLEL" "$SUT"

STAGE="done"
echo
echo "############################################################"
echo "# Pipeline complete for ${SUT} in $(( $(date +%s) - PIPE_START ))s"
echo "############################################################"
