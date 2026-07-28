# Primary paper narrative — Nano-LM archive (W–BA)

**Status:** Locked for archive draft v0.1 (Wave BA evidence).  
**Paper entry:** `paper/main.tex`  
**Audience:** Workshop / arXiv (cs.LG + cs.CL)  
**Pattern:** Same discipline as quantun-ia (`docs/paper_narrative.md` there).

---

## Headline claim

Under a hard **≤5M** student budget, **labeled known-ask + refuse + mode honesty** delivers real, measurable product gains (anti-FP, context content, prod-path speed). **True novel generative continue** remains **HOLD/DEFER**. Do **not** claim unlabeled open chat, GPT-class, or mini-AGI unlock.

---

## In-scope evidence (cite in main paper)

| Layer | Cite |
|-------|------|
| Tips | H-STAG′ · H-EARLY · H-POOL |
| Recipes | PACK/QT · QPFB2+BEAMKV/TCACHE/SCORERAM · ROLL/SUMCACHE/GPFB4-LONG |
| Product doctrine | Wave Z: PFB ≠ interactive LM · H-ZWRAP |
| Ship stack | AF packaged + AQ product + AS trust + STRICT ablated DECODE |
| Anti-FP | H-PRODGEN · H-REALGAIN · BA-FOREVER · live ask batteries |
| Speed / context | H-FASTREAL · H-CTXREAL2 (content bars; L_eff alone ≠ win) |
| Generative honesty | NANOGEN6·7 HOLD · NANOGEN8–11 DEFER · `n_true_continue=0` |

Public mirrors: `docs/results/nano-lm/{RECIPES,champion-card,*-freeze,wave-*-summary,paper-lab-wave-*}.md`.

---

## Deferred / out of headline

| Item | Why |
|------|-----|
| Mini-AGI / open chat language | true_continue unmet |
| CTX/SMART/FAST/APP letter clones as discovery | engineering republish without new hole |
| LOOKUP / SAFE scores as IQ | anti-FP law |
| Span-fallback / PEAK as generative unlock | fake lift |
| Soft-revive STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX | lab freeze |

---

## Negative results (must cite)

See [`docs/negative_results.md`](negative_results.md).

Highlights: Wave Z raw HITL FAIL; ZPREF KILL; NANOGEN HOLD/DEFER series; pack-green / forever-FP audit (pre-BA).

---

## Publication pipeline

```bash
cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
# optional:
npm run paper:build
```

Narrative enforcement (future): contract test that `paper/sections/*.tex` do not claim open chat / true-continue unlock while NANOGEN DEFER stands.

---

## Related

- [`paper/README.md`](../paper/README.md)
- [`docs/arxiv.md`](arxiv.md)
- Lab book: `.local/pesquisa.md`
- quantun-ia reference pipeline: `/data/dev/projects/webstorm/quantun-ia/paper/`
