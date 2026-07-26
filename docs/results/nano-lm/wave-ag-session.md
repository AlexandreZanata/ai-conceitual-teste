# Wave AG0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-ag/SESSION.md`  
> Module: `nano_lm/src/ag_session_ops.py` · Runner: `npm run nano:ag:session`  
> Parent: [af-freeze.md](af-freeze.md) (Wave AG reopened explicitly via lab-book §5)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AG model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE/AF HITL-01…10.  
Topics: hardened index threshold · BIP-39 ENT=128 checksum/words · 64-byte Schnorr · `list.extend` · `readlines` · immutable assign error · JSON-RPC Content-Type · REST blockhashbyheight · OP_RETURN commitment · CBOR acronym.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AG-HITL-01…03 |
| howto | 5 | AG-HITL-04…08 |
| long-doc | 2 | AG-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AG-HITL-01 | known-ask | bip-0032 |
| AG-HITL-02 | known-ask | bip-0039 |
| AG-HITL-03 | known-ask | bip-0340 |
| AG-HITL-04 | howto | python-tutorial-datastructures |
| AG-HITL-05 | howto | python-tutorial-io |
| AG-HITL-06 | howto | rust-book-ch03 |
| AG-HITL-07 | howto | bitcoin-json-rpc |
| AG-HITL-08 | howto | bitcoin-rest |
| AG-HITL-09 | long-doc | bip-0141 |
| AG-HITL-10 | long-doc | rfc8949 |

## Dual-arm rubric (AG)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.

## Validate

```bash
npm run nano:ag:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AG5).  
Artifacts (gitignored): `results/nano-lm/wave-ag/ag0_session.json` · `results/nano-lm/wave-ag/trials/AG-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ag_session.py`.

## Claims

- Held-out scoped app assist HITL set — **not** open chat LM.  
- Default ship claim until AG6 still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AH · PROMOTE LOOKUP-only as generative IQ.

Next: **AG1 H-ANTIFP** (**DONE** — see [formal-hantifp-antifp.md](formal-hantifp-antifp.md)). **AG2 H-CTXREAL** (**DONE** — see [formal-hctxreal-ctxreal.md](formal-hctxreal-ctxreal.md)). **AG3 H-SMARTREAL** (**DONE — HOLD** — see [formal-hsmartreal-smartreal.md](formal-hsmartreal-smartreal.md)). **AG4 H-FASTREAL** (**DONE — PROMOTE** — see [formal-hfastreal-fastreal.md](formal-hfastreal-fastreal.md)). **AG5 H-APPREAL** (**DONE — HOLD** — see [formal-happreal-appreal.md](formal-happreal-appreal.md)). **AG6 AG-HITL-10** (**DONE — HOLD** — see [wave-ag-hitl.md](wave-ag-hitl.md)). Next wave stage: **AG7 AG-REPORT**.
