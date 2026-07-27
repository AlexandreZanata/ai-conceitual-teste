# H-GENCORE — true gen via peak ablation (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §3 AO1 · Session: `.local/wave-ao/SESSION.md`  
> Parent: **AO0 SESSION** PROMOTE · Pack: AO0 held-out asks  
> Module: `nano_lm/src/gencore_ops.py` · Runner: `npm run nano:gencore` (`nano:ao:gencore`)

## Hypothesis

Chase **smarter GENERATE** on AO0 with **peak ablation** + **stricter gen label**: gate on **ablated** (`peak_off`) completions only; log extractive `peak_on` as comparison — never PROMOTE LOOKUP or peak tautology as open-chat IQ. Gen mean ≥ **5.0** **or** honest **HOLD**.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean (**ablated**) | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| GENERATE peak_on mean | **9.0** | anti-FP compare only — **not** smarter-LM gate |
| peak_only_lift | **true** | peak≥5 ∧ ablated&lt;5 → must **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used (compare) | **10**/10 | AO-aware spans; labeled extractive |
| FIX attempts | **1** (TTL peak cue) | ablated gate unchanged |
| Decision | **HOLD** | lookup ok; ablated gen &lt; 5 (honest) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AO-GENCORE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (ablated = gate)

| Trial | Ablated | Peak | error? | Notes |
|-------|--------:|-----:|:------:|-------|
| AO-GENCORE-GEN-HITL-01 | 4 | 9 | yes | TinyStories drift · peak `21` |
| AO-GENCORE-GEN-HITL-02 | 4 | 9 | yes | drift · peak `4` |
| AO-GENCORE-GEN-HITL-03 | 4 | 9 | yes | drift · peak `40` |
| AO-GENCORE-GEN-HITL-04 | 4 | 9 | yes | drift · peak `a.count(x)` |
| AO-GENCORE-GEN-HITL-05 | 4 | 9 | yes | drift · peak `while` |
| AO-GENCORE-GEN-HITL-06 | 4 | 9 | yes | drift · peak `super` |
| AO-GENCORE-GEN-HITL-07 | 4 | 9 | yes | drift · peak `u` |
| AO-GENCORE-GEN-HITL-08 | 4 | 9 | yes | drift · peak `struct` |
| AO-GENCORE-GEN-HITL-09 | 4 | 9 | yes | drift · peak REST block path |
| AO-GENCORE-GEN-HITL-10 | 4 | 9 | yes | drift · peak `8` (TTL bits) |

**Ablated mean:** 4.0 · **Peak mean:** 9.0 · `peak_only_lift=true`

### Cursor EVAL bullets

1. Ablated completions are TinyStories drift — not usable answers.  
2. Peak arm hits exact AO0 golds via extractive spans — labeled ≠ open-chat IQ.  
3. Gate must HOLD on ablated&lt;5; LOOKUP 9.0 is product retrieve only.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. Ablated true-gen mean **4.0** &lt; 5 → **HOLD** (same honesty bar as GENEDGE/GENTRUTH).  
3. Peak compare mean **9.0** proves extractive lift only — not smarter LM PROMOTE.  
4. Ship claim remains **AF packaged stack**.  
5. Optional **AO1b H-CAPCHECK** skipped (size hypothesis unused) → next **AO2 H-CTXCORE**.

## Reproduce

```bash
npm run nano:ao:session
npm run nano:gencore
# alias: npm run nano:ao:gencore
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ao/gencore_summary.json`  
- Trials: `AO-GENCORE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_gencore.py`

Next: **AO2 H-CTXCORE** — **DONE PROMOTE** → [formal-hctxcore-ctxcore.md](formal-hctxcore-ctxcore.md). Next **AO3 H-SMARTCORE**.
