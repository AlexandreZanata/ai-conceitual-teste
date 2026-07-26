# Wave AD0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.6 · §13 · Session: `.local/wave-ad/SESSION.md`  
> Module: `nano_lm/src/ad_session_ops.py` · Runner: `npm run nano:ad:session`  
> Parent: [ac-freeze.md](ac-freeze.md) (Wave AD reopened explicitly via §8.6)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AD model/stack.  
Questions are **not** verbatim copies of AB-HITL-01…10 or AC-HITL-01…10.

## Mix (§13.5)

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AD-HITL-01…03 |
| howto | 3 | AD-HITL-04…06 |
| long-doc | 4 | AD-HITL-07…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AD-HITL-01 | known-ask | bip-0340 |
| AD-HITL-02 | known-ask | bip-0141 |
| AD-HITL-03 | known-ask | python-tutorial-datastructures |
| AD-HITL-04 | howto | python-tutorial-io |
| AD-HITL-05 | howto | rust-book-ch04-01 |
| AD-HITL-06 | howto | rust-book-ch05-01 |
| AD-HITL-07 | long-doc | bitcoin-developer-notes |
| AD-HITL-08 | long-doc | rfc8949 |
| AD-HITL-09 | long-doc | rfc791 |
| AD-HITL-10 | long-doc | bitcoin-core-readme |

## Validate

```bash
npm run nano:ad:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AD5).  
Artifacts (gitignored): `results/nano-lm/wave-ad/ad0_session.json` · `results/nano-lm/wave-ad/trials/AD-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ad_session.py`.

## Claims

- Held-out scoped app assist HITL set — **not** open chat LM.  
- Default ship claim until AD5 still **AC packaged stack** on AB+AC spine.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AE.

Next: **AD1–AD5 DONE**. **AD6 AD-REPORT** (**DONE** — see [wave-ad-summary.md](wave-ad-summary.md)). Next wave stage: **AD7 AD-FREEZE**.
