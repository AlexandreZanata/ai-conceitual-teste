#!/usr/bin/env bash
# Build nano-LM archive paper (quantun-ia-style pipeline, minimal).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER="$ROOT/paper"
BUNDLE=0
if [[ "${1:-}" == "--bundle" ]]; then BUNDLE=1; fi

command -v pdflatex >/dev/null 2>&1 || {
  echo "pdflatex not found — install texlive-latex-base texlive-latex-recommended" >&2
  exit 1
}

cd "$PAPER"
pdflatex -interaction=nonstopmode main.tex
if command -v bibtex >/dev/null 2>&1; then
  bibtex main || true
fi
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
echo "OK: $PAPER/main.pdf"

if [[ "$BUNDLE" -eq 1 ]]; then
  mkdir -p "$ROOT/dist/arxiv"
  tar -czf "$ROOT/dist/arxiv/nano-lm-paper.tar.gz" \
    -C "$PAPER" main.tex references.bib arxiv_metadata.yaml README.md sections tables
  if [[ -f "$PAPER/main.pdf" ]]; then
    cp "$PAPER/main.pdf" "$ROOT/dist/arxiv/nano-lm-paper.pdf"
  fi
  echo "OK: $ROOT/dist/arxiv/nano-lm-paper.tar.gz"
fi
