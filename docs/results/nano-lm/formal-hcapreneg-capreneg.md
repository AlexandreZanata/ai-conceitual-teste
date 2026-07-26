# H-CAPRENEG — named size+budget after GENPLUS HOLD (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §5 AI1b · Session: `.local/wave-ai/SESSION.md`  
> Parent: **H-GENPLUS** HOLD (gen 4.0) · Pack: AI0 held-out asks  
> Module: `nano_lm/src/capreneg_ops.py` · Runner: `npm run nano:capreneg` (`nano:ai:capreneg`)

## Hypothesis

After GENPLUS HOLD under the **≤5M** hard law, formally propose **CAP-125M** (ceiling **130M** for the GPT-Neo-125M HF class) with a named decode-only budget (**no train**, wall ≤ **600s**, VRAM ≤ **8GB**) and prove **gen mean ≥ 5.0** on dual-arm AI0 asks — else **HOLD** and keep ≤5M.

## Named proposal

| Field | Value |
|-------|-------|
| Proposal id | **CAP-125M** |
| Proposed max params | **130_000_000** |
| Probe | `EleutherAI/gpt-neo-125M` (measured **125_198_592**) |
| Champion (≤5M) | **3_348_928** |
| Budget | decode-only · wall ≤600s · VRAM ≤8GB · `weight_update=false` |

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP on ≤5M product |
| GENERATE mean | **4.0** | ≥ **5.0** to PROMOTE size raise |
| FALSE_HIT | **0**/10 | any → **KILL** |
| proposal_ok | **true** | probe ≤ proposed ceiling |
| budget_ok | **true** | wall≈13s · VRAM peak≈0.33GB |
| FIX attempts | **10**/10 | re-probe; **0** score lifts |
| Decision | **HOLD** | gen &lt; 5 → **keep ≤5M hard** |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AI-CAPRENEG-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · ≠ gen IQ · ≠ size claim |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10

## Frontier EVAL — GENERATE arm (PROBE-125M+GROUNDED)

| Trial | Score | error? | Notes |
|-------|------:|:------:|-------|
| AI-CAPRENEG-GEN-HITL-01…10 | 4 | yes | Fluent-ish web/HTML drift · gold not contained · wall_ms>0 · n_new>0 |

**GEN mean:** 4.0 · does **not** beat GENPLUS 4.0 · **not** open chat IQ

### Cursor EVAL bullets

1. 125M probe is more fluent than the ≤5M TinyStories student, but still misses curated golds.  
2. Grounded context does not yield exact/phrase gold hits under honest scoring.  
3. Size alone (≤130M decode probe) does **not** unlock gen≥5 → do not raise hard cap.

## Finding

1. LOOKUP product path holds (mean **9.0**).  
2. Named CAP-125M proposal + budget are valid and within machine limits.  
3. Gen remains **4.0** → **HOLD**; **≤5M hard law stays**.  
4. Ship claim remains **AF packaged stack**.  
5. Next: **AI2 H-CTXPUSH** (longer ctx beyond CTXLIFT).

## Reproduce

```bash
npm run nano:ai:session
npm run nano:capreneg
# alias: npm run nano:ai:capreneg
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ai/capreneg_summary.json`  
- Trials: `AI-CAPRENEG-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_capreneg.py`

Next: **AI2 H-CTXPUSH** (**DONE — PROMOTE** — see [formal-hctxpush-ctxpush.md](formal-hctxpush-ctxpush.md)). Next: **AI3 H-SMARTPUSH**.
