# Wave AC0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 · §12 · Session: `.local/wave-ac/SESSION.md`  
> Module: `nano_lm/src/ac_session_ops.py` · Runner: `npm run nano:ac:session`  
> Parent: [ab-freeze.md](ab-freeze.md) (Wave AC reopened explicitly via §8.5)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AC model/stack.  
Questions are **not** verbatim copies of AB-HITL-01…10.

## Mix (§12.5)

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AC-HITL-01…03 |
| howto | 3 | AC-HITL-04…06 |
| long-doc | 4 | AC-HITL-07…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AC-HITL-01 | known-ask | bip-0032 |
| AC-HITL-02 | known-ask | bip-0001 |
| AC-HITL-03 | known-ask | python-tutorial-control |
| AC-HITL-04 | howto | python-tutorial-classes |
| AC-HITL-05 | howto | python-tutorial-intro |
| AC-HITL-06 | howto | rust-book-ch03 |
| AC-HITL-07 | long-doc | rust-book-ch03-02 |
| AC-HITL-08 | long-doc | bip-0039 |
| AC-HITL-09 | long-doc | bitcoin-rest |
| AC-HITL-10 | long-doc | rfc8446 |

## Validate

```bash
npm run nano:ac:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-ac/ac0_session.json` · `results/nano-lm/wave-ac/trials/AC-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ac_session.py`.

## Claims

- Held-out scoped app assist HITL set — **not** open chat LM.  
- After AC5 **PROMOTE**: ship claim is **scoped AC packaged apps** (app-known + app-howto + app-longdoc) — still **not** open chat LM.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AD.

Next after AC0 was **AC1 H-CTXPLUS**. Final pack gate: [wave-ac-hitl.md](wave-ac-hitl.md). Public closeout: [wave-ac-summary.md](wave-ac-summary.md). **Wave AC COMPLETE + FROZEN** — [ac-freeze.md](ac-freeze.md).
