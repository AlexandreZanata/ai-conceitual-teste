# Negative results — Nano-LM archive

Honest failures and non-promotions. Patterned after quantun-ia `docs/negative_results.md`.
International labs treat negatives as rigor, not weakness.

---

## Summary table

| ID / event | Hypothesis (brief) | Outcome | Lesson |
|------------|-------------------|---------|--------|
| Wave Z HITL-Z1 | Champion PFB decode answers interactive Q&A | **FAIL** mean ≈1.0, 10/10 errors | PFB ≠ interactive LM |
| H-ZPREF | Preference tip lifts story CE | **KILL** story < parent−ε | Do not ship |
| H-PARA (AA) | Paraphrase bank alone is robust | **HOLD** brittle exact-match | Need SEMWRAP+ |
| H-SERVEALIGN | Open decode alignment passes bar | **HOLD** beats Z1; not pass bar | Wrap still required |
| STREAM / KVCACHE-Q / GENCACHE | Cache tricks = product win | **KILL** | Lab freeze |
| MIXD / GPFB K=2 / naive CTX | Mix / K=2 / raw long window | **KILL** | Archive only |
| H-NANOGEN · NANOGEN2–3 | Generative unlock ≤5M | **HOLD** | true_continue unmet |
| H-NANOGEN6 · NANOGEN7 | True-continue / TAC | **HOLD** | `true_continue=0` |
| H-NANOGEN8–11 | Real new method generative lift | **DEFER** | No M1/M2/M3; not rename |
| H-ADVREG | Adversary reg as product | **KILL** (AR) | — |
| H-GEN* peak arms (many waves) | Gen mean lift via peak | **HOLD** peak_only_lift | Peak ≠ gen IQ |
| Pack-only FH 0 (pre-BA audit) | Named/AZ packs imply generalization | **Pack theater** | Forever held-out required |
| Live FP seeds | pow/mod/max→add; sort→reverse; len→junk | **FP** then closed in BA-FOREVER | Gate ≠ bank stuffing |
| DECODE no-wrap known gold | Student generates add without wrap | **ABSTAIN** / dots | Gen path dead; honest refuse OK |

---

## Foundational negative — Wave Z interactive decode

**Claim tested:** Serving champion QPFB2 as interactive LM.  
**Result:** HITL-Z1 FAIL (mean 1.0). Wrap LOOKUP (H-ZWRAP) PASS (mean 9.0).  
**Doctrine locked:** recipes optimize serve; they do not create chat intelligence.

Evidence: `docs/results/nano-lm/wave-z-hitl.md` · `wave-z-hitl-z1.md` · `wave-z-hitl-z4.md`.

---

## Generative series — HOLD / DEFER

Repeated NANOGEN waves without a real train/data/arch method produced no `true_continue` PROMOTE.
Span-fallback and gold-substring must not be scored as generative IQ.
CAPCHECK stays closed unless named reopen with ablations.

Evidence: `formal-hnanogen*.md` · Wave BA `nanogen11_summary.json` (`n_true_continue=0`).

---

## Pack theater — outside-pack false positives

**Observation (2026-07-28 live ask):** AZ/named packs looked green while novel ops still LOOKUP-matched `add` / wrong list golds.  
**Classification:** pack PASS ≠ intelligence.  
**Fix direction:** forever held-out + intent/ops gate (BA H-REALGAIN), not stuffing probe strings into the bank.

---

## Tip KILLs (lab freeze)

Must stay archived under `docs/results/nano-lm/archive/`:

| ID | Archive pointer |
|----|-----------------|
| STREAM | `archive/hstream-stream.md` |
| KVCACHE-Q | `archive/hkvcache-kvcache.md` |
| GENCACHE | `archive/hgencache-gencache.md` |
| MIXD | `archive/hmixd-mix.md` |
| GPFB K=2 | `archive/hgpfb-gpfb.md` |
| naive CTX | `archive/hctx-long-window.md` |

Validate: `npm run nano:lab-freeze`.

---

## How to cite in the paper

Main text §Results points here. Tables in `paper/tables/kill_archive.tex` and `generative_status.tex` summarize for reviewers.
