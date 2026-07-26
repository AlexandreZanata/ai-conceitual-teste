# Wave AH0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-ah/SESSION.md`  
> Module: `nano_lm/src/ah_session_ops.py` · Runner: `npm run nano:ah:session`  
> Parent: [ag-freeze.md](ag-freeze.md) (Wave AH reopened explicitly via lab-book §5)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AH model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE/AF/AG HITL-01…10.  
Topics: BIP-39 empty-passphrase salt · BIP-340 related-key / key prefixing · Rust four scalar types · `list.pop()` · `pass` empty body · `self` instance · heap for unknown size · struct update syntax · REST/JSON-RPC port 8332 · RFC 8949 obsoletes 7049.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AH-HITL-01…03 |
| howto | 5 | AH-HITL-04…08 |
| long-doc | 2 | AH-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AH-HITL-01 | known-ask | bip-0039 |
| AH-HITL-02 | known-ask | bip-0340 |
| AH-HITL-03 | known-ask | rust-book-ch03-02 |
| AH-HITL-04 | howto | python-tutorial-datastructures |
| AH-HITL-05 | howto | python-tutorial-control |
| AH-HITL-06 | howto | python-tutorial-classes |
| AH-HITL-07 | howto | rust-book-ch04-01 |
| AH-HITL-08 | howto | rust-book-ch05-01 |
| AH-HITL-09 | long-doc | bitcoin-rest |
| AH-HITL-10 | long-doc | rfc8949 |

## Dual-arm rubric (AH)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.

## Validate

```bash
npm run nano:ah:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AH6).  
Artifacts (gitignored): `results/nano-lm/wave-ah/ah0_session.json` · `results/nano-lm/wave-ah/trials/AH-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ah_session.py`.

## Claims

- Held-out scoped app assist HITL set (7th pack) — **not** open chat LM.  
- Default ship claim until AH6 still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AI · PROMOTE LOOKUP-only as generative IQ.

Next: **AH1 H-GENLIFT** (**DONE — HOLD** — see [formal-hgenlift-genlift.md](formal-hgenlift-genlift.md)). **AH2 H-CTXLIFT** (**DONE — PROMOTE** — see [formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md)). **AH3 H-SMARTLIFT** (**DONE — HOLD** — see [formal-hsmartlift-smartlift.md](formal-hsmartlift-smartlift.md)). **AH4 H-FASTLIFT** (**DONE — PROMOTE** — see [formal-hfastlift-fastlift.md](formal-hfastlift-fastlift.md)). **AH5 H-APPLIFT** (**DONE — HOLD** — see [formal-happlift-applift.md](formal-happlift-applift.md)). **AH6 AH-HITL-10** (**DONE — HOLD** — see [wave-ah-hitl.md](wave-ah-hitl.md)). Next: **AH7 AH-REPORT**.
