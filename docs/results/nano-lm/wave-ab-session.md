# Wave AB0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.3 · §11 · Session: `.local/wave-ab/SESSION.md`  
> Module: `nano_lm/src/ab_session_ops.py` · Runner: `npm run nano:ab:session`  
> Parent: [aa-freeze.md](aa-freeze.md) (Wave AB reopened explicitly via §8.3)

## Decision

**PROMOTE** — Freeze **10 real HITL questions** (source_id + app_id + gold) for every AB model/stack.  
**Status: COMPLETE** (AB0). **AB1–AB3 PROMOTE** — SEMWRAP · ASKFAST · LONGAPP ([formal-hlongapp-longapp.md](formal-hlongapp-longapp.md)). Next: **AB4 H-ASKSMART**.

## Mix (§11.5)

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 4 | AB-HITL-01…04 |
| howto | 3 | AB-HITL-05…07 |
| long-doc | 3 | AB-HITL-08…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AB-HITL-01 | known-ask | bip-0039 |
| AB-HITL-02 | known-ask | bip-0340 |
| AB-HITL-03 | known-ask | python-tutorial-datastructures |
| AB-HITL-04 | known-ask | rust-book-ch04-01 |
| AB-HITL-05 | howto | python-tutorial-io |
| AB-HITL-06 | howto | rust-book-ch05-01 |
| AB-HITL-07 | howto | bitcoin-json-rpc |
| AB-HITL-08 | long-doc | bip-0141 |
| AB-HITL-09 | long-doc | bitcoin-core-readme |
| AB-HITL-10 | long-doc | bitcoin-doc-bips |

## Validate

```bash
npm run nano:ab:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AB6).  
Artifacts (gitignored): `results/nano-lm/wave-ab/ab0_session.json` · `results/nano-lm/wave-ab/trials/AB-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ab_session.py`.

## Claims

- Scoped app assist HITL set — **not** open chat LM.  
- Default demo until AB6 still **H-ZWRAP + H-WRAPBANK**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF revival.
