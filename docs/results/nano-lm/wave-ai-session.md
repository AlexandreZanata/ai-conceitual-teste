# Wave AI0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-ai/SESSION.md`  
> Module: `nano_lm/src/ai_session_ops.py` · Runner: `npm run nano:ai:session`  
> Parent: [ah-freeze.md](ah-freeze.md) (Wave AI reopened explicitly via lab-book §5)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AI model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE/AF/AG/AH HITL-01…10.  
Topics: BIP-32 78-byte serialization · BIP-340 batch verification · BIP-141 P2WPKH · `list.insert(0,x)` · `elif`→else if · `issubclass` · Rust default `f64` · stack LIFO · REST `/rest/chaininfo.json` · BIP-1 three Type values.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AI-HITL-01…03 |
| howto | 5 | AI-HITL-04…08 |
| long-doc | 2 | AI-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AI-HITL-01 | known-ask | bip-0032 |
| AI-HITL-02 | known-ask | bip-0340 |
| AI-HITL-03 | known-ask | bip-0141 |
| AI-HITL-04 | howto | python-tutorial-datastructures |
| AI-HITL-05 | howto | python-tutorial-control |
| AI-HITL-06 | howto | python-tutorial-classes |
| AI-HITL-07 | howto | rust-book-ch03-02 |
| AI-HITL-08 | howto | rust-book-ch04-01 |
| AI-HITL-09 | long-doc | bitcoin-rest |
| AI-HITL-10 | long-doc | bip-0001 |

## Dual-arm rubric (AI)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.

## Validate

```bash
npm run nano:ai:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AI6).  
Artifacts (gitignored): `results/nano-lm/wave-ai/ai0_session.json` · `results/nano-lm/wave-ai/trials/AI-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_ai_session.py`.

## Claims

- Held-out scoped app assist HITL set (8th pack) — **not** open chat LM.  
- Default ship claim until AI6 still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AJ · PROMOTE LOOKUP-only as generative IQ.

Next: **AI1b–AI6** done (see formals). **AI7 AI-REPORT** (**DONE — PROMOTE** — [wave-ai-summary.md](wave-ai-summary.md) · [paper-lab-wave-ai.md](paper-lab-wave-ai.md)). Next: **AI8 AI-FREEZE**.
