# Wave AM0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · Session: `.local/wave-am/SESSION.md`  
> Module: `nano_lm/src/am_session_ops.py` · Runner: `npm run nano:am:session`  
> Parent: [al-freeze.md](al-freeze.md) (Wave AM reopened explicitly via lab-book reopen 2026-07-26)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AM model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE/AF/AG/AH/AI/AJ/AK/AL HITL-01…10.  
Topics: BIP-39 ENT=160 → 15 words · BIP-32 key-data bytes · BIP-141 P2WPKH witness stack size · `a.index(x)` · loop `else` · `setattr` · Rust `char` bytes · struct **fields** · REST mempool contents · RFC 791 IHL bits.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AM-HITL-01…03 |
| howto | 5 | AM-HITL-04…08 |
| long-doc | 2 | AM-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AM-HITL-01 | known-ask | bip-0039 |
| AM-HITL-02 | known-ask | bip-0032 |
| AM-HITL-03 | known-ask | bip-0141 |
| AM-HITL-04 | howto | python-tutorial-datastructures |
| AM-HITL-05 | howto | python-tutorial-control |
| AM-HITL-06 | howto | python-tutorial-classes |
| AM-HITL-07 | howto | rust-book-ch03-02 |
| AM-HITL-08 | howto | rust-book-ch05-01 |
| AM-HITL-09 | long-doc | bitcoin-rest |
| AM-HITL-10 | long-doc | rfc791 |

## Dual-arm rubric (AM)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.  
Ablation: at least one later stage must report peak-ablated gen before claiming smarter LM.

## Validate

```bash
npm run nano:am:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + GENERATE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-am/am0_session.json` · `results/nano-lm/wave-am/trials/AM-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_am_session.py`.

## Claims

- Held-out scoped app assist HITL set (12th pack) — **not** open chat LM.  
- Default ship claim until proven otherwise still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AN · PROMOTE LOOKUP-only as generative IQ.

Next: **AM1 H-GENTRUTH** — smarter usable gen + dual-arm ASK→EVAL→FIX ×10 + ablation honesty.
