#!/usr/bin/env bash
#
# Compile the report (main.tex) to main.pdf.
#
# Usage:
#   ./build.sh          Build main.pdf (runs all passes + bibliography).
#   ./build.sh clean     Remove build artifacts (incl. main.pdf).
#   ./build.sh watch     Rebuild automatically on file changes (latexmk only).
#
# -shell-escape is enabled so the `svg` package can call inkscape when SVG
# figures (e.g. the timeline) are included.

set -euo pipefail

# Always operate relative to this script's directory, so it works from anywhere.
cd "$(dirname "$0")"

MAIN=main
FLAGS=(-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error)

have() { command -v "$1" >/dev/null 2>&1; }

case "${1:-build}" in
    clean)
        if have latexmk; then
            latexmk -C "$MAIN.tex"
        fi
        # Remove anything latexmk doesn't track (subdir aux files, svg cache).
        rm -f "$MAIN".{aux,bbl,blg,log,out,toc,lof,lot,fls,fdb_latexmk,synctex.gz} "$MAIN.pdf"
        find . -name '*.aux' -delete
        rm -rf svg-inkscape
        echo "Cleaned build artifacts."
        ;;

    watch)
        if ! have latexmk; then
            echo "error: 'watch' requires latexmk, which is not installed." >&2
            exit 1
        fi
        latexmk -pdf -pvc "${FLAGS[@]}" "$MAIN.tex"
        ;;

    build)
        if have latexmk; then
            # latexmk runs pdflatex/bibtex as many times as needed.
            latexmk -pdf "${FLAGS[@]}" "$MAIN.tex"
        else
            # Manual fallback: pdflatex -> bibtex -> pdflatex x2 for references.
            echo "latexmk not found; using manual pdflatex/bibtex sequence." >&2
            pdflatex "${FLAGS[@]}" "$MAIN.tex"
            bibtex "$MAIN" || true   # tolerate first-run citation warnings
            pdflatex "${FLAGS[@]}" "$MAIN.tex"
            pdflatex "${FLAGS[@]}" "$MAIN.tex"
        fi
        echo "Built $(pwd)/$MAIN.pdf"
        ;;

    *)
        echo "Usage: $0 [build|clean|watch]" >&2
        exit 1
        ;;
esac
