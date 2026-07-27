# Wave AT0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-at/SESSION.md`  
> Module: `nano_lm/src/at_session_ops.py` · Runner: `npm run nano:at:session`  
> Parent: [as-freeze.md](as-freeze.md) (Wave AT reopened explicitly via lab-book reopen 2026-07-27)

## Decision

**PROMOTE** — Freeze AT packs: PRODREG suite (cite AS product gates) · SHIPAPP charter · NANOGEN4 hyp (retrieved-snippet prefix; **not** bank-gold) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked until AT3 PROMOTE.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| PRODREG suite | 1 | para≥0.70 · FH0 · p50/p99 · KB · modes · abstain (AT1) |
| SHIPAPP charter | 1 | human demo/apps always show 4 modes (AT2) |
| NANOGEN4 hypothesis | 1 | ablated ≥5.0 vs NANOGEN3 4.3 (AT3) |
| Real-eval protocol | 1 | live ask battery · anti-FP (AT4) |
| Ask battery | 6 | frozen live rows (scored at AT4) |

## Cited AS gates

H-ADVSAFE, H-ASKABSTAIN, H-METRICS, H-NANOGEN3, H-PARAEXT2, H-SEMFIX, H-SHIPUI

## PRODREG bars

- para_hit_min: **0.7** (AS PARAEXT2 baseline 0.80)  
- false_hit_max: **0** (AS ADVSAFE 0/20)  
- default_ask_ood: **ABSTAIN**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no re-SEMFIX/ADVSAFE unless PRODREG fails

## SHIPAPP charter

- paths: `['nano:z:ask', 'apps ask', 'ship/demo']`  
- banner: `mode=LOOKUP|PEAK|DECODE|ABSTAIN`  
- smoke: **4/4**  
- rule: every human-facing answer must show product_mode; no unlabeled

## NANOGEN4 hypothesis (one idea)

One idea: ablated DECODE with retrieved-snippet prefix conditioning (seed decode from top SEMWRAP/RAG span; student continues ≤N tokens) — no bank-gold rewrite, no peak overlay on gate score; beat NANOGEN3 ablated 4.3; bar = ablated≥5.0

## Real-eval protocol

- live_ask_battery: True  
- summary_only_forbidden: True  
- gen_claim_rule: only if AT3 H-NANOGEN4 PROMOTE (ablated≥5.0)  
- mini_agi_rule: forbidden while NANOGEN4 HOLD

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| AT-ASK-01 | known_lookup | LOOKUP |
| AT-ASK-02 | ood_abstain | ABSTAIN |
| AT-ASK-03 | near_miss | ABSTAIN |
| AT-ASK-04 | labeled_peak | PEAK |
| AT-ASK-05 | decode_smoke | DECODE |
| AT-ASK-06 | junk_trap | ABSTAIN |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; generative bar = AT3 only; no vanity re-SEMFIX/ADVSAFE unless PRODREG fails; no Wave AU invent

## North star

Nano generative / mini-AGI-inspired ≤5M: ship Caminho A (PRODREG + SHIPAPP) now; ablated DECODE mean ≥5.0 (H-NANOGEN4) before generative or mini-AGI claim

## Validate

```bash
npm run nano:at:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask; OOD path must map to ABSTAIN.  
Artifacts (gitignored): `results/nano-lm/wave-at/at0_session.json` · `results/nano-lm/wave-at/trials/AT-*.json`.  
Contract: `nano_lm/tests/test_at_session.py`.

## Claims

- AT packs frozen for Wave AT — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path**.  
- Generative PROMOTE only via later **AT3 H-NANOGEN4** ablated bar ≥5.0.  
- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · mini-AGI claim early · Wave AU invent · CTX/SMART/FAST/APP clone · bank stuffing · vanity re-SEMFIX.

Next: **AT1 H-PRODREG** — **DONE PROMOTE** → [formal-hprodreg-prodreg.md](formal-hprodreg-prodreg.md). **AT2 H-SHIPAPP** — **DONE PROMOTE** → [formal-hshipapp-shipapp.md](formal-hshipapp-shipapp.md). **AT3 H-NANOGEN4** — **DONE PROMOTE** (ablated **5.5**) → [formal-hnanogen4-nanogen4.md](formal-hnanogen4-nanogen4.md). **AT4 AT-REAL-EVAL** — **DONE PROMOTE** (battery 6/6) → [wave-at-real-eval.md](wave-at-real-eval.md). **AT5 AT-REPORT** — **DONE PROMOTE** → [wave-at-summary.md](wave-at-summary.md) · [paper-lab-wave-at.md](paper-lab-wave-at.md). **AT6 AT-FREEZE** — next.

