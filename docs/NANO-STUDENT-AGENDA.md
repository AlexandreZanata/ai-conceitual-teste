# Nano Student + Teacher — Research Agenda

> Lab: `nano_lm/`. Caps: ≤80 / ≤200 / cyclo ≤10.  
> EvoGen: frozen [`archive/evogen/`](archive/evogen/README.md).  
> **Wave status / next actions:** `.local/pesquisa.md` (source of truth).

## Tips / recipes

**H-STAG′** · **H-EARLY** · **H-POOL**  
Serve-fast: **H-PACK** + **QT**. Code-smart: **QPFB2** / **BPFB** / **GPFB4**. Long: **ROLL** / SUMCACHE / GPFB4-LONG. Train: **TPACK**+**AMORT**.  
HITL: **H-ZWRAP** (+ **H-WRAPBANK** + **H-SEMWRAP**). Story-CE: **H-ZERR** ≠ chat.  
**DEPL-Y:** [`wave-z-depl-y.md`](results/nano-lm/wave-z-depl-y.md) · One-pager: [`RECIPES.md`](results/nano-lm/RECIPES.md) · Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Waves (index)

| Band | Status | Where |
|------|--------|-------|
| W–Z | COMPLETE | `docs/results/nano-lm/wave-*-summary.md` · `lab-freeze.md` |
| AA–BG | COMPLETE + FROZEN | `docs/results/nano-lm/*-freeze.md` |
| **BH** | **ACTIVE** | BH0 [SESSION PROMOTE](results/nano-lm/wave-bh-session.md) (`npm run nano:bh:session`) — IQ battery plan · gold holes · BA…BG/AZ hold · Track A++ util · gen stance SKIP (H-NANOGEN18); BH1 [H-IQBAT PROMOTE](results/nano-lm/formal-hiqbat-iqbat.md) (`npm run nano:iq-battery`); next BH2 H-GOLDFIX; ship AF+AQ+AS trust + STRICT ablated DECODE; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16·17 SKIP; ≤5M |
| Active / reopen | **only** lab book | `.local/pesquisa.md` |

Do **not** invent the next wave letter without explicit lab-book reopen.  
Ship claim until gen PROMOTE: **AF + AQ + AS + STRICT ablated DECODE** — not unlabeled open chat / not mini-AGI unlocked.

Teachers: TinyStories-33M + `bigcode/tiny_starcoder_py` ([TCHR](results/nano-lm/formal-htchr-code-teacher.md)).  
KILL tooling purged → [`results/nano-lm/archive/`](results/nano-lm/archive/).

## Reproduce essentials

```bash
npm run nano:curated
npm run nano:z:ask -- --wrap --semwrap --question "…"
npm run nano:bf:freeze   # or parent freeze named in pesquisa.md
npm run paper:build
npm run nano:test && npm run verify
```
