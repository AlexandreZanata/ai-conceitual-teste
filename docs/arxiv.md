# arXiv submission guide — Nano-LM archive paper

Submit `paper/` to [arXiv](https://arxiv.org) (`cs.LG` + `cs.CL`).
Workflow patterned after quantun-ia `docs/arxiv.md`.

---

## Prerequisites

- arXiv account with endorsement for `cs.LG` or `cs.CL`
- Narrative lock reviewed: [`docs/paper_narrative.md`](paper_narrative.md)
- Negatives reviewed: [`docs/negative_results.md`](negative_results.md)
- Metadata reviewed: `paper/arxiv_metadata.yaml`
- Local PDF build green

---

## Step 1 — Build PDF

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
# → paper/main.pdf
```

Or: `npm run paper:build`

---

## Step 2 — Bundle sources

```bash
mkdir -p dist/arxiv
tar -czf dist/arxiv/nano-lm-paper.tar.gz \
  -C paper main.tex references.bib arxiv_metadata.yaml README.md \
  sections tables
```

Include `main.pdf` as reference copy if desired (arXiv prefers sources).

---

## Step 3 — Upload

1. [arxiv.org/submit](https://arxiv.org/submit)
2. Upload `dist/arxiv/nano-lm-paper.tar.gz` or TeX tree
3. Copy title / abstract / authors / categories from `paper/arxiv_metadata.yaml`
4. Comments: link GitHub + note Wave BA archive freeze

---

## Step 4 — Record ID

After moderation, set in `paper/arxiv_metadata.yaml`:

```yaml
arxiv_id: "XXXX.XXXXX"
```

Update `paper/README.md` checklist and commit.

---


## Thesis (Track A++ · H-SHIPPUB)

Publish as a **selective retriever** + refuse product under ≤5M — not an open generative LM / mini-AGI unlock. Cite H-UNARYINT · H-SHIPUSE2 · AF+AQ+AS STRICT ablated DECODE.

## Honesty checklist (before submit)

- [ ] Abstract does **not** claim open chat / GPT-class / true-continue unlock
- [ ] NANOGEN HOLD/DEFER stated
- [ ] Anti-FP / forever held-out mentioned
- [ ] Negative results section or pointer present
- [ ] Ship claim STRICT wording matches freeze docs
