# Wave AO0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · Session: `.local/wave-ao/SESSION.md`  
> Module: `nano_lm/src/ao_session_ops.py` · Runner: `npm run nano:ao:session`  
> Parent: [an-freeze.md](an-freeze.md) (Wave AO reopened explicitly via lab-book reopen 2026-07-27)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AO model/stack.  
Questions are **not** verbatim copies of AB…AN HITL-01…10.  
Topics: BIP-39 ENT=224 → 21 words · BIP-32 version bytes · BIP-141 witness program ≤40 · `a.count(x)` · `while` · `super` · Rust unsigned prefix `u` · `struct` keyword · REST full block · RFC 791 TTL bits.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AO-HITL-01…03 |
| howto | 5 | AO-HITL-04…08 |
| long-doc | 2 | AO-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AO-HITL-01 | known-ask | bip-0039 |
| AO-HITL-02 | known-ask | bip-0032 |
| AO-HITL-03 | known-ask | bip-0141 |
| AO-HITL-04 | howto | python-tutorial-datastructures |
| AO-HITL-05 | howto | python-tutorial-control |
| AO-HITL-06 | howto | python-tutorial-classes |
| AO-HITL-07 | howto | rust-book-ch03-02 |
| AO-HITL-08 | howto | rust-book-ch05-01 |
| AO-HITL-09 | long-doc | bitcoin-rest |
| AO-HITL-10 | long-doc | rfc791 |

## Dual-arm rubric (AO)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.  
Ablation: at least one later stage must report peak-ablated gen before claiming smarter LM.

## Validate

```bash
npm run nano:ao:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + GENERATE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-ao/ao0_session.json` · `results/nano-lm/wave-ao/trials/AO-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ao_session.py`.

## Claims

- Held-out scoped app assist HITL set (14th pack) — **not** open chat LM.  
- Default ship claim until proven otherwise still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AP · PROMOTE LOOKUP-only as generative IQ.

Next: **AO1 H-GENCORE** — **DONE HOLD** → [formal-hgencore-gencore.md](formal-hgencore-gencore.md). **AO2 H-CTXCORE PROMOTE** → [formal-hctxcore-ctxcore.md](formal-hctxcore-ctxcore.md). **AO3 H-SMARTCORE PROMOTE** → [formal-hsmartcore-smartcore.md](formal-hsmartcore-smartcore.md). **AO4 H-FASTCORE PROMOTE** → [formal-hfastcore-fastcore.md](formal-hfastcore-fastcore.md). Next **AO5 H-APPCORE**.
