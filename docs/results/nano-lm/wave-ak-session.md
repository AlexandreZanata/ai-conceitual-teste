# Wave AK0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · Session: `.local/wave-ak/SESSION.md`  
> Module: `nano_lm/src/ak_session_ops.py` · Runner: `npm run nano:ak:session`  
> Parent: [aj-freeze.md](aj-freeze.md) (Wave AK reopened explicitly via lab-book reopen 2026-07-26)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AK model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE/AF/AG/AH/AI/AJ HITL-01…10.  
Topics: BIP-39 ENT 128–256 · BIP-32 chain-code bytes · BIP-141 marker `0x00` · `a.clear()` · `break` · `getattr` · Rust `bool` · struct dot notation · REST mempool info · RFC 791 Version bits.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AK-HITL-01…03 |
| howto | 5 | AK-HITL-04…08 |
| long-doc | 2 | AK-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AK-HITL-01 | known-ask | bip-0039 |
| AK-HITL-02 | known-ask | bip-0032 |
| AK-HITL-03 | known-ask | bip-0141 |
| AK-HITL-04 | howto | python-tutorial-datastructures |
| AK-HITL-05 | howto | python-tutorial-control |
| AK-HITL-06 | howto | python-tutorial-classes |
| AK-HITL-07 | howto | rust-book-ch03-02 |
| AK-HITL-08 | howto | rust-book-ch05-01 |
| AK-HITL-09 | long-doc | bitcoin-rest |
| AK-HITL-10 | long-doc | rfc791 |

## Dual-arm rubric (AK)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.

## Validate

```bash
npm run nano:ak:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + GENERATE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-ak/ak0_session.json` · `results/nano-lm/wave-ak/trials/AK-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ak_session.py`.

## Claims

- Held-out scoped app assist HITL set (10th pack) — **not** open chat LM.  
- Default ship claim until proven otherwise still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AL · PROMOTE LOOKUP-only as generative IQ.

Next: **AK1 H-GENTRUE** — **DONE HOLD** → [formal-hgentrue-gentrue.md](formal-hgentrue-gentrue.md). **AK2 H-CTXMORE** — **DONE PROMOTE** → [formal-hctxmore-ctxmore.md](formal-hctxmore-ctxmore.md). Next: **AK3 H-SMARTMORE**.
