# Wave AJ0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §6 · Session: `.local/wave-aj/SESSION.md`  
> Module: `nano_lm/src/aj_session_ops.py` · Runner: `npm run nano:aj:session`  
> Parent: [ai-freeze.md](ai-freeze.md) (Wave AJ reopened explicitly via lab-book §6)

## Decision

**PROMOTE** — Freeze **10 held-out HITL questions** (source_id + app_id + gold) for every AJ model/stack.  
Questions are **not** verbatim copies of AB/AC/AD/AE/AF/AG/AH/AI HITL-01…10.  
Topics: BIP-39 ENT multiple-of-32 · BIP-32 depth bytes · BIP-141 P2WSH · `collections.deque` · `continue` · `isinstance` · Rust default `i32` · field init shorthand · JSON-RPC `/wallet/<walletname>/` · RFC 791 IHL.

## Mix

| app_id | Count | Trials |
|--------|------:|--------|
| known-ask | 3 | AJ-HITL-01…03 |
| howto | 5 | AJ-HITL-04…08 |
| long-doc | 2 | AJ-HITL-09…10 |

## Frozen pack (ids)

| id | app_id | source_id |
|----|--------|-----------|
| AJ-HITL-01 | known-ask | bip-0039 |
| AJ-HITL-02 | known-ask | bip-0032 |
| AJ-HITL-03 | known-ask | bip-0141 |
| AJ-HITL-04 | howto | python-tutorial-datastructures |
| AJ-HITL-05 | howto | python-tutorial-control |
| AJ-HITL-06 | howto | python-tutorial-classes |
| AJ-HITL-07 | howto | rust-book-ch03-02 |
| AJ-HITL-08 | howto | rust-book-ch05-01 |
| AJ-HITL-09 | long-doc | bitcoin-json-rpc |
| AJ-HITL-10 | long-doc | rfc791 |

## Dual-arm rubric (AJ)

| Arm | Required telemetry | EVAL rule |
|-----|--------------------|-----------|
| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; may have `wall_ms=0` | Score completion vs truth; label honestly — not “model IQ” |
| GENERATE | no wrap **or** miss→decode; `wall_ms > 0` and `n_new > 0` | Cursor scores completion; never auto-9 from gold match alone |

PROMOTE for “smarter/faster model” **forbidden** if only LOOKUP arm scored.  
Pass bars (later stages): LOOKUP mean ≥ **7.0** · GENERATE mean ≥ **5.0** else **HOLD**.

## Validate

```bash
npm run nano:aj:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Wrap smoke must keep `WRAP_LOOKUP` on the Z1 add known-ask (product claim until AJ6).  
Artifacts (gitignored): `results/nano-lm/wave-aj/aj0_session.json` · `results/nano-lm/wave-aj/trials/AJ-HITL-*.json` · `error_bank.jsonl`.  
Contract: `nano_lm/tests/test_aj_session.py`.

## Claims

- Held-out scoped app assist HITL set (9th pack) — **not** open chat LM.  
- Default ship claim until AJ6 still **AF packaged stack**.  
- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZPREF · invent Wave AK · PROMOTE LOOKUP-only as generative IQ.

Next: **AJ1 H-GENPEAK** — **DONE PROMOTE** → [formal-hgenpeak-genpeak.md](formal-hgenpeak-genpeak.md). **AJ2 H-CTXPEAK** — **DONE PROMOTE** → [formal-hctxpeak-ctxpeak.md](formal-hctxpeak-ctxpeak.md). **AJ3 H-SMARTPEAK** — **DONE PROMOTE** → [formal-hsmartpeak-smartpeak.md](formal-hsmartpeak-smartpeak.md). **AJ4 H-FASTPEAK** — **DONE PROMOTE** → [formal-hfastpeak-fastpeak.md](formal-hfastpeak-fastpeak.md). **AJ5 H-APPPEAK** — **DONE PROMOTE** → [formal-happpeak-apppeak.md](formal-happpeak-apppeak.md). **AJ6 AJ-HITL-10** — **DONE PROMOTE** → [wave-aj-hitl.md](wave-aj-hitl.md). **AJ7 AJ-REPORT** — **DONE PROMOTE** → [wave-aj-summary.md](wave-aj-summary.md) · [paper-lab-wave-aj.md](paper-lab-wave-aj.md). Next: **AJ8 AJ-FREEZE**.
