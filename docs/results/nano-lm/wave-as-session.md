# Wave AS0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-as/SESSION.md`  
> Module: `nano_lm/src/as_session_ops.py` · Runner: `npm run nano:as:session`  
> Parent: [ar-freeze.md](ar-freeze.md) (Wave AS reopened explicitly via lab-book reopen 2026-07-27)

## Decision

**PROMOTE** — Freeze product-trust packs (ADVSAFE-20 citing AR-ADVREG-01/05 · PARAEXT2-20 · ASKABSTAIN charter · SEMFIX hyp · NANOGEN3 hyp · metrics protocol). **Not** a CTX/SMART/FAST/APP clone.  
PARAEXT2 paraphrases are **disjoint** from AQ-PARA and AR-EXT exact text. Anti-FP signed.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| ADVSAFE-20 | 20 | adversary reopen; cite AR-ADVREG-01/05 (AS3) |
| PARAEXT2-20 | 20 | fresh paraphrases ≠ AQ/AR-EXT (AS4) |
| ASKABSTAIN charter | 1 | default `nano:z:ask` → ABSTAIN (AS1) |
| SEMFIX hypothesis | 1 | negation/contrast/margin (AS2) |
| metrics protocol | 1 | p50/p99 + KB holes (AS5) |
| NANOGEN3 hypothesis | 1 | ablated ≥5.0 generative gate (AS7) |

## PARAEXT2-20 (ids)

| id | source_id |
|----|-----------|
| AS-EXT2-01 | python-tutorial-intro |
| AS-EXT2-02 | prog:g01 |
| AS-EXT2-03 | python-tutorial-control |
| AS-EXT2-04 | rust-book-ch03 |
| AS-EXT2-05 | bip-0001 |
| AS-EXT2-06 | bip-0032 |
| AS-EXT2-07 | bip-0141 |
| AS-EXT2-08 | python-tutorial-classes |
| AS-EXT2-09 | bip-0039 |
| AS-EXT2-10 | bip-0340 |
| AS-EXT2-11 | python-tutorial-datastructures |
| AS-EXT2-12 | python-tutorial-io |
| AS-EXT2-13 | rust-book-ch03-02 |
| AS-EXT2-14 | rust-book-ch04-01 |
| AS-EXT2-15 | rust-book-ch05-01 |
| AS-EXT2-16 | bitcoin-json-rpc |
| AS-EXT2-17 | bitcoin-rest |
| AS-EXT2-18 | bitcoin-doc-bips |
| AS-EXT2-19 | bip-0039 |
| AS-EXT2-20 | rfc791 |

## ADVSAFE-20 (ids)

| id | kind | parent_id | source_id |
|----|------|-----------|-----------|
| AS-ADVSAFE-01 | near-miss | AR-ADVREG-01 | bip-0039 |
| AS-ADVSAFE-02 | near-miss | AR-ADVREG-02 | bip-0032 |
| AS-ADVSAFE-03 | near-miss | AR-ADVREG-03 | bip-0141 |
| AS-ADVSAFE-04 | near-miss | AR-ADVREG-04 | python-tutorial-datastructures |
| AS-ADVSAFE-05 | near-miss | AR-ADVREG-05 | python-tutorial-control |
| AS-ADVSAFE-06 | near-miss | AR-ADVREG-06 | rust-book-ch03-02 |
| AS-ADVSAFE-07 | near-miss | AR-ADVREG-07 | bip-0340 |
| AS-ADVSAFE-08 | near-miss | AR-ADVREG-08 | bitcoin-rest |
| AS-ADVSAFE-09 | ood | — | ood:sports |
| AS-ADVSAFE-10 | ood | — | ood:cooking |
| AS-ADVSAFE-11 | ood | — | ood:finance |
| AS-ADVSAFE-12 | ood | — | ood:medicine |
| AS-ADVSAFE-13 | ood | — | ood:history |
| AS-ADVSAFE-14 | ood | — | ood:math |
| AS-ADVSAFE-15 | trap | — | trap:lookup-as-iq |
| AS-ADVSAFE-16 | trap | — | trap:peak-as-agi |
| AS-ADVSAFE-17 | trap | — | trap:safe-as-quality |
| AS-ADVSAFE-18 | trap | — | trap:period |
| AS-ADVSAFE-19 | trap | — | trap:empty |
| AS-ADVSAFE-20 | trap | — | trap:wrong-gold |

## Required parent citations

AR-ADVREG-01, AR-ADVREG-05

## ASKABSTAIN charter

- paths: `['nano:z:ask', 'apps ask']`  
- trigger: DECODE junk / OOD / miss on default ask (not only stage runner)  
- action: `NO_ANSWER` → `mode=ABSTAIN`  
- rule: ABSTAIN on default ask is product honesty — not generative IQ

## SEMFIX hypothesis (one idea)

One idea: SEMWRAP margin + negation/contrast gate — refuse LOOKUP when ask polarity flips gold (reverse formula, continue≠pass) or near-miss margin is below threshold; AR-ADVREG-01/05 class must stay FH=0

## NANOGEN3 hypothesis (one idea)

One idea: ablated DECODE with bank-grounded short continuation plus ASKABSTAIN refuse-junk on default ask path — score only mode=DECODE; beat NANOGEN2 ablated 4.3; bar = ablated≥5.0

## Metrics protocol

- paths: LOOKUP · PEAK · DECODE · ABSTAIN  
- metrics: p50_wall_ms, p99_wall_ms  
- KB: coverage_pct, hole_list  
- complete product-KB claim forbidden

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP)

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; generative bar = AS7 only; abstain must land on default ask path (not runner-only)

## North star

Nano generative / mini-AGI-inspired ≤5M: fix product trust on default ask path now; ablated DECODE mean ≥5.0 (H-NANOGEN3) before generative or mini-AGI claim

## Validate

```bash
npm run nano:as:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-as/as0_session.json` · `results/nano-lm/wave-as/trials/AS-*.json`.  
Contract: `nano_lm/tests/test_as_session.py`.

## Claims

- Product-trust packs frozen for Wave AS — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer**.  
- Generative PROMOTE only via later **AS7 H-NANOGEN3** ablated bar ≥5.0.  
- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · mini-AGI claim early · Wave AT invent · CTX/SMART/FAST/APP clone without named product hole · bank stuffing.

Next: **AS1–AS6** DONE PROMOTE. **AS7 H-NANOGEN3** — **DONE HOLD** → [formal-hnanogen3-nanogen3.md](formal-hnanogen3-nanogen3.md) (ablated **4.3**). **AS8 AS-DUAL-HITL** — **DONE PROMOTE** → [wave-as-dual-hitl.md](wave-as-dual-hitl.md). **AS9 AS-REPORT** — **DONE PROMOTE** → [wave-as-summary.md](wave-as-summary.md) · [paper-lab-wave-as.md](paper-lab-wave-as.md). Next: **AS10 AS-FREEZE**.
