# Wave AN0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · Session: `.local/wave-an/SESSION.md`  
> Module: `nano_lm/src/an_session_ops.py` · Runner: `npm run nano:an:session`  
> Parent: [am-freeze.md](am-freeze.md) (Wave AN reopened explicitly via lab-book reopen 2026-07-27)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AN model/stack.  
Questions are **not** verbatim copies of AB…AM HITL-01…10.  
Topics: BIP-39 ENT=192 → 18 words · BIP-32 child-number bytes · BIP-141 witnessScript ≤10000 · `a.remove(x)` · `range` · `__dict__` · Rust tuples/arrays · tuple structs · REST headers · RFC 791 Total Length bits.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AN-HITL-01…03 |
| howto | 5 | AN-HITL-04…08 |
| long-doc | 2 | AN-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AN-HITL-01 | known-ask | bip-0039 |
| AN-HITL-02 | known-ask | bip-0032 |
| AN-HITL-03 | known-ask | bip-0141 |
| AN-HITL-04 | howto | python-tutorial-datastructures |
| AN-HITL-05 | howto | python-tutorial-control |
| AN-HITL-06 | howto | python-tutorial-classes |
| AN-HITL-07 | howto | rust-book-ch03-02 |
| AN-HITL-08 | howto | rust-book-ch05-01 |
| AN-HITL-09 | long-doc | bitcoin-rest |
| AN-HITL-10 | long-doc | rfc791 |

## Dual-arm rubric (AN)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.  
Ablation: at least one later stage must report peak-ablated gen before claiming smarter LM.

## Validate

```bash
npm run nano:an:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + GENERATE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-an/an0_session.json` · `results/nano-lm/wave-an/trials/AN-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_an_session.py`.

## Claims

- Held-out scoped app assist HITL set (13th pack) — **not** open chat LM.  
- Default ship claim until proven otherwise still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AO · PROMOTE LOOKUP-only as generative IQ.

Next: **AN1 H-GENEDGE** — **DONE HOLD** → [formal-hgenedge-genedge.md](formal-hgenedge-genedge.md). **AN2 H-CTXEDGE** — **DONE PROMOTE** → [formal-hctxedge-ctxedge.md](formal-hctxedge-ctxedge.md). **AN3 H-SMARTEDGE** — **DONE PROMOTE** → [formal-hsmartedge-smartedge.md](formal-hsmartedge-smartedge.md). **AN4 H-FASTEDGE** — **DONE PROMOTE** → [formal-hfastedge-fastedge.md](formal-hfastedge-fastedge.md). **AN5 H-APPEDGE** — **DONE PROMOTE** → [formal-happedge-appedge.md](formal-happedge-appedge.md). Next **AN6 AN-HITL-10**.
