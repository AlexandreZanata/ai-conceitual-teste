# Wave AE0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-ae/SESSION.md`  
> Module: `nano_lm/src/ae_session_ops.py` · Runner: `npm run nano:ae:session`  
> Parent: [ad-freeze.md](ad-freeze.md) (Wave AE reopened explicitly via lab-book §5)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AE model/stack.  
Questions are **not** verbatim copies of AB-HITL-01…10, AC-HITL-01…10, or AD-HITL-01…10.  
Topics differ from prior waves (xprv/xpub · PBKDF2 params · 32-byte keys · list-as-queue · shadowing · f-strings · REST tx path · RPC cookie · IP TTL · wtxid).

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AE-HITL-01…03 |
| howto | 3 | AE-HITL-04…06 |
| long-doc | 4 | AE-HITL-07…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AE-HITL-01 | known-ask | bip-0032 |
| AE-HITL-02 | known-ask | bip-0039 |
| AE-HITL-03 | known-ask | bip-0340 |
| AE-HITL-04 | howto | python-tutorial-datastructures |
| AE-HITL-05 | howto | rust-book-ch03 |
| AE-HITL-06 | howto | python-tutorial-io |
| AE-HITL-07 | long-doc | bitcoin-rest |
| AE-HITL-08 | long-doc | bitcoin-json-rpc |
| AE-HITL-09 | long-doc | rfc791 |
| AE-HITL-10 | long-doc | bip-0141 |

## Validate

```bash
npm run nano:ae:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AE5).  
Artifacts (gitignored): `results/nano-lm/wave-ae/ae0_session.json` · `results/nano-lm/wave-ae/trials/AE-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ae_session.py`.

## Claims

- Held-out scoped app assist HITL set — **not** open chat LM.  
- Default ship claim until AE5 still **AD packaged stack** on AC/APPPLUS.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AF.

Next: **AE1–AE6 DONE**. **AE7 AE-FREEZE** (**DONE** — see [ae-freeze.md](ae-freeze.md)). Wave **AE COMPLETE + FROZEN**.
