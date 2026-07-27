# Wave AP0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · Session: `.local/wave-ap/SESSION.md`  
> Module: `nano_lm/src/ap_session_ops.py` · Runner: `npm run nano:ap:session`  
> Parent: [ao-freeze.md](ao-freeze.md) (Wave AP reopened explicitly via lab-book reopen 2026-07-27)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AP model/stack.  
Questions are **not** verbatim copies of AB…AO HITL-01…10.  
Topics: BIP-39 CS=ENT/32 · BIP-32 master fingerprint 0x00000000 · BIP-141 P2WPKH · `a.append(x)` · `pass` · `issubclass` · Rust indexing ints `isize or usize` · struct update `..` · REST tx by hash · RFC 791 Protocol bits.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AP-HITL-01…03 |
| howto | 5 | AP-HITL-04…08 |
| long-doc | 2 | AP-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AP-HITL-01 | known-ask | bip-0039 |
| AP-HITL-02 | known-ask | bip-0032 |
| AP-HITL-03 | known-ask | bip-0141 |
| AP-HITL-04 | howto | python-tutorial-datastructures |
| AP-HITL-05 | howto | python-tutorial-control |
| AP-HITL-06 | howto | python-tutorial-classes |
| AP-HITL-07 | howto | rust-book-ch03-02 |
| AP-HITL-08 | howto | rust-book-ch05-01 |
| AP-HITL-09 | long-doc | bitcoin-rest |
| AP-HITL-10 | long-doc | rfc791 |

## Dual-arm rubric (AP)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.  
Ablation: at least one later stage must report peak-ablated gen before claiming smarter LM.

## Validate

```bash
npm run nano:ap:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + GENERATE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-ap/ap0_session.json` · `results/nano-lm/wave-ap/trials/AP-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ap_session.py`.

## Claims

- Held-out scoped app assist HITL set (15th pack) — **not** open chat LM.  
- Default ship claim until proven otherwise still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AQ · PROMOTE LOOKUP-only as generative IQ.

Next: **AP1 H-GENBASE** — **DONE HOLD** → [formal-hgenbase-genbase.md](formal-hgenbase-genbase.md). **AP2 H-CTXBASE** — **DONE PROMOTE** → [formal-hctxbase-ctxbase.md](formal-hctxbase-ctxbase.md). **AP3 H-SMARTBASE** — **DONE PROMOTE** → [formal-hsmartbase-smartbase.md](formal-hsmartbase-smartbase.md). **AP4 H-FASTBASE** — **DONE PROMOTE** → [formal-hfastbase-fastbase.md](formal-hfastbase-fastbase.md). Next **AP5 H-APPBASE**.
