#!/usr/bin/env bash
#
# fetch_seed_corpora.sh -- download real example inputs (seed corpora) for each
# SUT into seed_corpora/<sut>/, for use as the initial population of
# `elfuzz direct`. Each SUT folder gets a SOURCE.txt recording provenance.
#
# Sources are public test suites of the respective parsers. We fetch with
# shallow + sparse git clones (only the needed subtree, no full history) and
# select up to MAX_FILES valid inputs of the right extension, skipping files
# larger than MAX_BYTES so the corpus stays light.
#
# Usage:
#   tools/fetch_seed_corpora.sh [sut ...]      # default: all SUTs
#   MAX_FILES=500 MAX_BYTES=200000 tools/fetch_seed_corpora.sh jsoncpp
#
set -uo pipefail

cd "$(dirname "$(readlink -f "$0")")/.."
ROOT="$PWD"
DEST_ROOT="$ROOT/seed_corpora"
MAX_FILES="${MAX_FILES:-500}"
MAX_BYTES="${MAX_BYTES:-200000}"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

ALL_SUTS=(jsoncpp libxml2 re2 librsvg cvc5 sqlite3 cpython3)
SUTS=("$@"); [ ${#SUTS[@]} -eq 0 ] && SUTS=("${ALL_SUTS[@]}")

# All human-readable output goes to stderr so it never pollutes the paths/counts
# returned via stdout command-substitution.
log() { printf '[fetch] %s\n' "$*" >&2; }

# fetch_sparse <url> <subdir> <name> -> echoes the local path to <subdir> on stdout
fetch_sparse() {
    local url="$1" subdir="$2" name="$3" dir="$TMP_ROOT/$3"
    if [ ! -d "$dir" ]; then
        log "cloning $url ($subdir)"
        git clone --depth 1 --filter=blob:none --no-checkout "$url" "$dir" >&2 2>/dev/null || { log "clone failed: $url"; return 1; }
        git -C "$dir" sparse-checkout init --cone >/dev/null 2>&1
        git -C "$dir" sparse-checkout set "$subdir" >/dev/null 2>&1
        git -C "$dir" checkout >/dev/null 2>&1 || { log "checkout failed: $url"; return 1; }
    fi
    [ -d "$dir/$subdir" ] || { log "subdir missing: $subdir in $url"; return 1; }
    echo "$dir/$subdir"
}

# copy_into <destdir> <ext> <max> <start>  (stdin: NUL-separated src paths)
#   copies valid (non-empty, <= MAX_BYTES) files as NNNN.<ext> starting at
#   index <start>; echoes the resulting count. Does NOT clear destdir.
copy_into() {
    local destdir="$1" ext="$2" max="$3" i="${4:-0}"
    mkdir -p "$destdir"
    local f sz
    while IFS= read -r -d '' f; do
        [ "$i" -ge "$max" ] && break
        [ -f "$f" ] || continue
        sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
        [ "$sz" -gt 0 ] && [ "$sz" -le "$MAX_BYTES" ] || continue
        cp "$f" "$(printf '%s/%04d.%s' "$destdir" "$i" "$ext")"
        i=$((i+1))
    done
    echo "$i"
}

write_source() { printf '%s\n' "$@" > "$DEST_ROOT/$SUT/SOURCE.txt"; }

# --------------------------------------------------------------------------
fetch_jsoncpp() {  # JSON (two sources to reach a useful count)
    local dest="$DEST_ROOT/jsoncpp" i=0 d
    rm -rf "$dest"; mkdir -p "$dest"
    d=$(fetch_sparse https://github.com/nst/JSONTestSuite test_parsing jsontestsuite) && \
        i=$(find "$d" -name 'y_*.json' -print0 | sort -z | copy_into "$dest" json "$MAX_FILES" "$i")
    if [ "${i:-0}" -lt "$MAX_FILES" ]; then
        d=$(fetch_sparse https://github.com/json-schema-org/JSON-Schema-Test-Suite tests jsonschema) && \
            i=$(find "$d" -name '*.json' -print0 | sort -z | copy_into "$dest" json "$MAX_FILES" "$i")
    fi
    write_source "JSON seed corpus for jsoncpp" \
        "nst/JSONTestSuite                       test_parsing/y_*.json (valid-accepted)   [MIT]" \
        "json-schema-org/JSON-Schema-Test-Suite  tests/**/*.json (valid JSON instances)   [MIT]"
    echo "${i:-0}"
}

fetch_libxml2() {  # XML
    local dest="$DEST_ROOT/libxml2" i=0 d
    rm -rf "$dest"; mkdir -p "$dest"
    d=$(fetch_sparse https://github.com/GNOME/libxml2 test libxml2) && \
        i=$(find "$d" -type f -name '*.xml' -print0 | sort -z | copy_into "$dest" xml "$MAX_FILES")
    write_source "XML seed corpus for libxml2" "GNOME/libxml2   test/**/*.xml   [MIT]"
    echo "${i:-0}"
}

fetch_librsvg() {  # SVG
    local dest="$DEST_ROOT/librsvg" i=0 d
    rm -rf "$dest"; mkdir -p "$dest"
    d=$(fetch_sparse https://github.com/GNOME/librsvg rsvg librsvg) && \
        i=$(find "$d" -type f -name '*.svg' -print0 | sort -z | copy_into "$dest" svg "$MAX_FILES")
    write_source "SVG seed corpus for librsvg" "GNOME/librsvg   rsvg/**/*.svg (reftest fixtures)   [LGPL-2.1]"
    echo "${i:-0}"
}

fetch_cvc5() {  # SMT-LIB v2
    local dest="$DEST_ROOT/cvc5" i=0 d
    rm -rf "$dest"; mkdir -p "$dest"
    d=$(fetch_sparse https://github.com/cvc5/cvc5 test/regress/cli/regress0 cvc5) || \
        d=$(fetch_sparse https://github.com/cvc5/cvc5 test/regress/regress0 cvc5)
    [ -n "${d:-}" ] && i=$(find "$d" -type f -name '*.smt2' -print0 | sort -z | copy_into "$dest" smt2 "$MAX_FILES")
    write_source "SMT-LIB v2 seed corpus for cvc5" \
        "cvc5/cvc5   test/regress/.../regress0/**/*.smt2 (small regressions)   [BSD-3-Clause]"
    echo "${i:-0}"
}

fetch_cpython3() {  # Python
    local dest="$DEST_ROOT/cpython3" i=0 d
    rm -rf "$dest"; mkdir -p "$dest"
    d=$(fetch_sparse https://github.com/python/cpython Lib cpython) && \
        i=$(find "$d" -type f -name '*.py' -print0 | sort -z | copy_into "$dest" py "$MAX_FILES")
    write_source "Python 3 seed corpus for cpython3" "python/cpython   Lib/**/*.py (stdlib modules)   [PSF License]"
    echo "${i:-0}"
}

fetch_re2() {  # regex (.re) -- extract patterns from rust-lang/regex testdata
    local dest="$DEST_ROOT/re2" d
    rm -rf "$dest"; mkdir -p "$dest"
    d=$(fetch_sparse https://github.com/rust-lang/regex testdata regexdata) || { echo 0; return; }
    local n
    n=$(python3 - "$d" "$dest" "$MAX_FILES" <<'PY'
import os, re, sys
src, dest, mx = sys.argv[1], sys.argv[2], int(sys.argv[3])
pats, seen = [], set()
rx = re.compile(r"""^\s*regex\s*=\s*(['"])(.*)\1\s*$""")
for root,_,files in os.walk(src):
    for fn in sorted(files):
        if not fn.endswith(('.toml','.txt')): continue
        for line in open(os.path.join(root,fn), encoding='utf-8', errors='replace'):
            m = rx.match(line)
            if m and m.group(2) and m.group(2) not in seen:
                seen.add(m.group(2)); pats.append(m.group(2))
for i,p in enumerate(pats[:mx]):
    open(os.path.join(dest, f"{i:04d}.re"), "w", encoding="utf-8").write(p)
print(len(pats[:mx]))
PY
)
    write_source "Regex seed corpus for re2" \
        "rust-lang/regex   testdata/**/*.toml -> 'regex = ...' patterns (RE2-compatible)   [MIT/Apache-2.0]"
    echo "${n:-0}"
}

fetch_sqlite3() {  # SQL -- extract statements from sqllogictest .test files
    local dest="$DEST_ROOT/sqlite3" d
    rm -rf "$dest"; mkdir -p "$dest"
    d=$(fetch_sparse https://github.com/gregrahn/sqllogictest test sqllogictest) || { echo 0; return; }
    local n
    n=$(python3 - "$d" "$dest" "$MAX_FILES" <<'PY'
import os, sys
src, dest, mx = sys.argv[1], sys.argv[2], int(sys.argv[3])
out = 0
for root,_,files in os.walk(src):
    for fn in sorted(files):
        if not fn.endswith('.test'): continue
        lines = open(os.path.join(root,fn), encoding='utf-8', errors='replace').read().splitlines()
        i = 0
        while i < len(lines) and out < mx:
            ln = lines[i].strip()
            if ln.startswith('statement') or ln.startswith('query'):
                i += 1; sql = []
                while i < len(lines) and lines[i].strip() not in ('', '----'):
                    sql.append(lines[i]); i += 1
                body = "\n".join(sql).strip()
                if body and not body.startswith('#'):
                    if not body.rstrip().endswith(';'): body += ';'
                    open(os.path.join(dest, f"{out:04d}.sql"), "w", encoding="utf-8").write(body + "\n")
                    out += 1
            else:
                i += 1
        if out >= mx: break
    if out >= mx: break
print(out)
PY
)
    write_source "SQL seed corpus for sqlite3" \
        "gregrahn/sqllogictest   test/**/*.test -> extracted SQL statements/queries   [public-domain test data]"
    echo "${n:-0}"
}

mkdir -p "$DEST_ROOT"
declare -A COUNTS
for SUT in "${SUTS[@]}"; do
    log "=== $SUT ==="
    case "$SUT" in
        jsoncpp)  COUNTS[$SUT]=$(fetch_jsoncpp) ;;
        libxml2)  COUNTS[$SUT]=$(fetch_libxml2) ;;
        re2)      COUNTS[$SUT]=$(fetch_re2) ;;
        librsvg)  COUNTS[$SUT]=$(fetch_librsvg) ;;
        cvc5)     COUNTS[$SUT]=$(fetch_cvc5) ;;
        sqlite3)  COUNTS[$SUT]=$(fetch_sqlite3) ;;
        cpython3) COUNTS[$SUT]=$(fetch_cpython3) ;;
        *) log "unknown SUT: $SUT"; continue ;;
    esac
    log "$SUT -> ${COUNTS[$SUT]:-0} files in seed_corpora/$SUT/"
done

echo "==================== summary ===================="
for SUT in "${SUTS[@]}"; do printf '  %-9s %s files\n' "$SUT" "${COUNTS[$SUT]:-0}"; done
echo "  dest: $DEST_ROOT"
