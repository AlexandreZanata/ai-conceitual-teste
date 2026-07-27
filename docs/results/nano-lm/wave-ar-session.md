# Wave AR0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-ar/SESSION.md`  
> Module: `nano_lm/src/ar_session_ops.py` · Runner: `npm run nano:ar:session`  
> Parent: [aq-freeze.md](aq-freeze.md) (Wave AR reopened explicitly via lab-book reopen 2026-07-27)

## Decision

**PROMOTE** — Freeze product-deepen packs (external-para-20 · advreg-20 · abstention protocol · ship-demo charter · NANOGEN2 hypothesis). **Not** a CTX/SMART/FAST/APP clone.  
Packs are **disjoint** from AQ-PARA/ADV exact text.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| external-para-20 | 20 | fresh paraphrases ≠ AQ-PARA (AR3) |
| advreg-20 | 20 | adversary regression + SAFE≠quality (AR4) |
| abstention protocol | 1 | DECODE junk → NO_ANSWER/ABSTAIN (AR1) |
| ship-demo charter | 4 modes | LOOKUP\|PEAK\|DECODE\|ABSTAIN (AR2) |
| NANOGEN2 hypothesis | 1 | ablated ≥5.0 generative gate (AR5) |

## External-para-20 (ids)

| id | source_id |
|----|-----------|
| AR-EXT-01 | python-tutorial-intro |
| AR-EXT-02 | prog:g01 |
| AR-EXT-03 | python-tutorial-control |
| AR-EXT-04 | rust-book-ch03 |
| AR-EXT-05 | bip-0001 |
| AR-EXT-06 | bip-0032 |
| AR-EXT-07 | bip-0141 |
| AR-EXT-08 | python-tutorial-classes |
| AR-EXT-09 | bip-0039 |
| AR-EXT-10 | bip-0340 |
| AR-EXT-11 | python-tutorial-datastructures |
| AR-EXT-12 | python-tutorial-io |
| AR-EXT-13 | rust-book-ch03-02 |
| AR-EXT-14 | rust-book-ch04-01 |
| AR-EXT-15 | rust-book-ch05-01 |
| AR-EXT-16 | bitcoin-json-rpc |
| AR-EXT-17 | bitcoin-rest |
| AR-EXT-18 | bitcoin-doc-bips |
| AR-EXT-19 | bip-0039 |
| AR-EXT-20 | rfc791 |

## Advreg-20 (ids)

| id | kind | source_id |
|----|------|-----------|
| AR-ADVREG-01 | near-miss | bip-0039 |
| AR-ADVREG-02 | near-miss | bip-0032 |
| AR-ADVREG-03 | near-miss | bip-0141 |
| AR-ADVREG-04 | near-miss | python-tutorial-datastructures |
| AR-ADVREG-05 | near-miss | python-tutorial-control |
| AR-ADVREG-06 | near-miss | rust-book-ch03-02 |
| AR-ADVREG-07 | near-miss | bip-0340 |
| AR-ADVREG-08 | near-miss | bitcoin-rest |
| AR-ADVREG-09 | ood | ood:sports |
| AR-ADVREG-10 | ood | ood:cooking |
| AR-ADVREG-11 | ood | ood:finance |
| AR-ADVREG-12 | ood | ood:medicine |
| AR-ADVREG-13 | ood | ood:history |
| AR-ADVREG-14 | ood | ood:math |
| AR-ADVREG-15 | trap | trap:lookup-as-iq |
| AR-ADVREG-16 | trap | trap:peak-as-agi |
| AR-ADVREG-17 | trap | trap:safe-as-quality |
| AR-ADVREG-18 | trap | trap:period |
| AR-ADVREG-19 | trap | trap:empty |
| AR-ADVREG-20 | trap | trap:wrong-gold |

## Abstention protocol

- trigger: DECODE junk on OOD/miss (TinyStories garbage, empty, period-collapse, low-grounding)  
- action: `NO_ANSWER` → `mode=ABSTAIN`  
- rule: ABSTAIN is honest product mode — not generative IQ

## Ship-demo charter (anti-FP)

Every ASK / demo / HITL trial MUST log exactly one of `LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` (aliases mapped in ops; `NO_ANSWER` → ABSTAIN).

## NANOGEN2 hypothesis (one idea)

One idea: ablated DECODE with bank-grounded short continuation plus refuse-junk gate (ABSTAIN/NO_ANSWER on OOD/miss garbage) — score only mode=DECODE; peak remains compare-only; bar = ablated≥5.0

## SAFE ≠ quality

SAFE / ADVFP / ADVREG false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)

## North star

Nano generative / mini-AGI-inspired ≤5M: product deepen now; ablated DECODE mean ≥5.0 (H-NANOGEN2) before any generative claim

## Validate

```bash
npm run nano:ar:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-ar/ar0_session.json` · `results/nano-lm/wave-ar/trials/AR-*.json`.  
Contract: `nano_lm/tests/test_ar_session.py`.

## Claims

- Product-deepen packs frozen for Wave AR — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer**.  
- Generative PROMOTE only via later **AR5 H-NANOGEN2** ablated bar ≥5.0.  
- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · mini-AGI claim early · Wave AS invent · CTX/SMART/FAST/APP clone without named product hole.

Next: **AR1 H-ABSTAIN** — **DONE PROMOTE** → [formal-habstain-abstain.md](formal-habstain-abstain.md). **AR2 H-SHIPDEMO** — **DONE PROMOTE** → [formal-hshipdemo-shipdemo.md](formal-hshipdemo-shipdemo.md). **AR3 H-PARAEXT** — **DONE HOLD** → [formal-hparaext-paraext.md](formal-hparaext-paraext.md). Next: **AR4 H-ADVREG**.
