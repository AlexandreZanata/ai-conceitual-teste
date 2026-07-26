# Wave AF0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-af/SESSION.md`  
> Module: `nano_lm/src/af_session_ops.py` · Runner: `npm run nano:af:session`  
> Parent: [ae-freeze.md](ae-freeze.md) (Wave AF reopened explicitly via lab-book §5)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AF model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE HITL-01…10.  
Topics differ from AE (BIP purpose · BIP-9 soft-forks · Rust scalar/compound · Point class · `range(3)` · `add` · ownership · `struct User` · Core P2P validate · TLS 1.3 handshake).

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AF-HITL-01…03 |
| howto | 5 | AF-HITL-04…08 |
| long-doc | 2 | AF-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AF-HITL-01 | known-ask | bip-0001 |
| AF-HITL-02 | known-ask | bitcoin-doc-bips |
| AF-HITL-03 | known-ask | rust-book-ch03-02 |
| AF-HITL-04 | howto | python-tutorial-classes |
| AF-HITL-05 | howto | python-tutorial-control |
| AF-HITL-06 | howto | python-tutorial-intro |
| AF-HITL-07 | howto | rust-book-ch04-01 |
| AF-HITL-08 | howto | rust-book-ch05-01 |
| AF-HITL-09 | long-doc | bitcoin-core-readme |
| AF-HITL-10 | long-doc | rfc8446 |

## Validate

```bash
npm run nano:af:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AF5).  
Artifacts (gitignored): `results/nano-lm/wave-af/af0_session.json` · `results/nano-lm/wave-af/trials/AF-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_af_session.py`.

## Claims

- Held-out scoped app assist HITL set — **not** open chat LM.  
- Default ship claim until AF5 still **AE packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AG · PROMOTE without FIX.

Next: **AF1 H-CTXULTRA** (**DONE** — see [formal-hctxultra-ctxultra.md](formal-hctxultra-ctxultra.md)). Next wave stage: **AF2 H-SMARTULTRA**.
