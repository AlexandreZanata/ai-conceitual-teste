# Wave AL0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §3 · Session: `.local/wave-al/SESSION.md`  
> Module: `nano_lm/src/al_session_ops.py` · Runner: `npm run nano:al:session`  
> Parent: [ak-freeze.md](ak-freeze.md) (Wave AL reopened explicitly via lab-book reopen 2026-07-26)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AL model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE/AF/AG/AH/AI/AJ/AK HITL-01…10.  
Topics: BIP-39 ENT=256 → 24 words · BIP-32 parent fingerprint bytes · BIP-141 flag `0x01` · `a.reverse()` · `match` · `delattr` · Boolean **1** byte · unit-like structs · REST deploymentinfo · RFC 791 TTL bits.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AL-HITL-01…03 |
| howto | 5 | AL-HITL-04…08 |
| long-doc | 2 | AL-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AL-HITL-01 | known-ask | bip-0039 |
| AL-HITL-02 | known-ask | bip-0032 |
| AL-HITL-03 | known-ask | bip-0141 |
| AL-HITL-04 | howto | python-tutorial-datastructures |
| AL-HITL-05 | howto | python-tutorial-control |
| AL-HITL-06 | howto | python-tutorial-classes |
| AL-HITL-07 | howto | rust-book-ch03-02 |
| AL-HITL-08 | howto | rust-book-ch05-01 |
| AL-HITL-09 | long-doc | bitcoin-rest |
| AL-HITL-10 | long-doc | rfc791 |

## Dual-arm rubric (AL)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.

## Validate

```bash
npm run nano:al:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + GENERATE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-al/al0_session.json` · `results/nano-lm/wave-al/trials/AL-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_al_session.py`.

## Claims

- Held-out scoped app assist HITL set (11th pack) — **not** open chat LM.  
- Default ship claim until proven otherwise still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AM · PROMOTE LOOKUP-only as generative IQ.

Next: **AL1 H-GENFRESH** — **DONE HOLD** → [formal-hgenfresh-genfresh.md](formal-hgenfresh-genfresh.md). **AL2 H-CTXFRESH** — **DONE PROMOTE** → [formal-hctxfresh-ctxfresh.md](formal-hctxfresh-ctxfresh.md). **AL3 H-SMARTFRESH** — **DONE PROMOTE** → [formal-hsmartfresh-smartfresh.md](formal-hsmartfresh-smartfresh.md). **AL4 H-FASTFRESH** — **DONE PROMOTE** → [formal-hfastfresh-fastfresh.md](formal-hfastfresh-fastfresh.md). **AL5 H-APPFRESH** — **DONE PROMOTE** → [formal-happfresh-appfresh.md](formal-happfresh-appfresh.md). **AL6 AL-HITL-10** — **DONE PROMOTE** → [wave-al-hitl.md](wave-al-hitl.md). Next: **AL7 AL-REPORT**.
