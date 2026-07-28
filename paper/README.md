# Nano-LM scientific archive paper

LaTeX draft consolidating discoveries from Waves W–BA of the nano generative student lab (≤5M).

Modeled after the quantun-ia paper pipeline (`paper/main.tex` + narrative + negative results).

## Build

```bash
cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
# or from repo root (if script exists):
# npm run paper:build
```

Requires: `pdflatex`, `booktabs`, `graphicx`, `hyperref`, `amsmath`.

## Structure

| Path | Purpose |
|------|---------|
| `main.tex` | Document entry |
| `sections/` | Introduction, methods, experiments, results, limitations |
| `tables/` | Frozen evidence tables (tips, anti-FP, latency, gen status, KILLs) |
| `figures/` | Optional figures (synced later) |
| `references.bib` | Bibliography |
| `arxiv_metadata.yaml` | Title, abstract, categories for arXiv |

## Narrative locks

| Doc | Role |
|-----|------|
| [`docs/paper_narrative.md`](../docs/paper_narrative.md) | Headline claims in / out of scope |
| [`docs/negative_results.md`](../docs/negative_results.md) | Honest HOLD / DEFER / KILL archive |
| [`docs/arxiv.md`](../docs/arxiv.md) | Submission workflow |
| Lab book | `.local/pesquisa.md` (private) |
| Recipes | [`docs/results/nano-lm/RECIPES.md`](../docs/results/nano-lm/RECIPES.md) |

## Headline claim (locked)

A **≤5M nano student** plus **labeled product stack** (LOOKUP / PEAK / DECODE / ABSTAIN) delivers measurable **known-ask**, **anti-FP refuse**, **context content**, and **prod-path speed** gains — while **true generative continue** under ≤5M remains **HOLD/DEFER** (not GPT-class, not unlabeled open chat).

## Submission checklist

- [x] Consolidate Waves W–BA discoveries into sections + tables
- [x] Document negative results (NANOGEN HOLD/DEFER, tip KILLs, pack-theater)
- [ ] `pdflatex` build green locally
- [ ] Cite Zenodo / GitHub release after upload
- [ ] Upload arXiv (`cs.LG` + `cs.CL`) — set `arxiv_id` in metadata

## arXiv ID

<!-- Set after upload: -->
<!-- arxiv:XXXX.XXXXX -->
