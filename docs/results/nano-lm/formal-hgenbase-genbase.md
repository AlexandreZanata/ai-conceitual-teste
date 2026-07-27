# H-GENBASE — true gen via peak ablation (**DONE** — HOLD)

> Lab: `.local/pesquisa.md` §3 AP1 · Session: `.local/wave-ap/SESSION.md`  
> Parent: **AP0 SESSION** PROMOTE · Pack: AP0 held-out asks  
> Module: `nano_lm/src/genbase_ops.py` · Runner: `npm run nano:genbase` (`nano:ap:genbase`)

## Hypothesis

Chase **smarter GENERATE** on AP0 with **peak ablation** + **stricter gen label**: gate on **ablated** (`peak_off`) completions only; log extractive `peak_on` as comparison — never PROMOTE LOOKUP or peak tautology as open-chat IQ. Gen mean ≥ **5.0** **or** honest **HOLD**.

## Gate (Cursor ASK→EVAL→FIX×10 dual-arm)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| LOOKUP mean | **9.0** | ≥ **7.0** · WRAP_LOOKUP |
| GENERATE mean (**ablated**) | **4.0** | ≥ **5.0** for PROMOTE else **HOLD** |
| GENERATE peak_on mean | **8.2** | anti-FP compare only — **not** smarter-LM gate |
| peak_only_lift | **true** | peak≥5 ∧ ablated&lt;5 → must **HOLD** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| period collapses | **0**/10 | anti-period held |
| extractive peak used (compare) | **10**/10 | AP-aware spans; labeled extractive |
| FIX attempts | **1** (`..` peak vs period-collapse filter) | ablated gate unchanged |
| Decision | **HOLD** | lookup ok; ablated gen &lt; 5 (honest) |

## Frontier EVAL — LOOKUP arm

| Trial | Score | Notes |
|-------|------:|-------|
| AP-GENBASE-LOOKUP-HITL-01…10 | 9 | TRUE_HIT · WRAP_LOOKUP · wall_ms=0 · ≠ gen IQ |

**LOOKUP mean:** 9.0 · **FALSE_HIT:** 0/10 · product retrieve only

## Frontier EVAL — GENERATE arm (ablated = gate)

| Trial | Ablated | Peak | error? | Notes |
|-------|--------:|-----:|:------:|-------|
| AP-GENBASE-GEN-HITL-01 | 4 | 9 | yes | TinyStories drift · peak `CS = ENT / 32` |
| AP-GENBASE-GEN-HITL-02 | 4 | 9 | yes | drift · peak `0x00000000` |
| AP-GENBASE-GEN-HITL-03 | 4 | 9 | yes | drift · peak `P2WPKH` |
| AP-GENBASE-GEN-HITL-04 | 4 | 9 | yes | drift · peak `a.append(x)` |
| AP-GENBASE-GEN-HITL-05 | 4 | 9 | yes | drift · peak `pass` |
| AP-GENBASE-GEN-HITL-06 | 4 | 9 | yes | drift · peak `issubclass` |
| AP-GENBASE-GEN-HITL-07 | 4 | 9 | yes | drift · peak `isize or usize` |
| AP-GENBASE-GEN-HITL-08 | 4 | 1 | yes | drift · peak `..` (scorer soft on period-like gold) |
| AP-GENBASE-GEN-HITL-09 | 4 | 9 | yes | drift · peak REST tx path |
| AP-GENBASE-GEN-HITL-10 | 4 | 9 | yes | drift · peak `8` (Protocol bits) |

**Ablated mean:** 4.0 · **Peak mean:** 8.2 · `peak_only_lift=true`

### Cursor EVAL bullets

1. Ablated completions are TinyStories drift — not usable answers.  
2. Peak arm hits exact AP0 golds via extractive spans — labeled ≠ open-chat IQ.  
3. Gate must HOLD on ablated&lt;5; LOOKUP 9.0 is product retrieve only.

## Finding

1. LOOKUP product path holds (mean **9.0**, false-hit **0**).  
2. Ablated true-gen mean **4.0** &lt; 5 → **HOLD** (same honesty bar as GENCORE/GENEDGE).  
3. Peak compare mean **8.2** (9× exact gold @9 · `..` soft-scored) — extractive lift only; not smarter LM PROMOTE.  
4. Ship claim remains **AF packaged stack**.  
5. Optional **AP1b H-CAPCHECK** skipped (size hypothesis unused) → next **AP2 H-CTXBASE** (**DONE PROMOTE**).

## Reproduce

```bash
npm run nano:ap:session
npm run nano:genbase
# alias: npm run nano:ap:genbase
npm run nano:test && npm run verify
```

## Artifacts

- Summary: `results/nano-lm/wave-ap/genbase_summary.json`  
- Trials: `AP-GENBASE-{LOOKUP|GEN}-HITL-01…10`  
- Contract: `nano_lm/tests/test_genbase.py`

Next: **AP2 H-CTXBASE** — **DONE PROMOTE** → [formal-hctxbase-ctxbase.md](formal-hctxbase-ctxbase.md). Next **AP3 H-SMARTBASE**.
