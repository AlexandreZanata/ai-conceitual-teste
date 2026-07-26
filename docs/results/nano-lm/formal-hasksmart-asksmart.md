# H-ASKSMART — constrained decode policy (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.3 AB4 · Session: `.local/wave-ab/SESSION.md`  
> Parent: **H-SERVEALIGN** HOLD (mean 3.4) · Stack: QPFB2+BEAMKV + anti-period + SEMWRAP FIX  
> Module: `nano_lm/src/asksmart_ops.py` · Runner: `npm run nano:asksmart`

## Hypothesis

Decode / stop / anti-period / constrained serve on **QPFB2+BEAMKV** lifts open-ask HITL **above SERVEALIGN 3.4** to mean **≥ 5.0**, with story≥parent−ε on the open arm; failures FIX via constrained SEMWRAP (not open-chat claims).

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **8.7** | ≥ **5.0** and > **3.4** |
| errors | **1**/10 | ≤ 3 for quality bar |
| period collapses (final) | **0**/10 | anti-period + FIX |
| constrained FIX | **10**/10 | open decode alone still weak |
| open `score_before` | **5.0** mean | non-period substance |
| beats SERVEALIGN | **yes** | 8.7 > 3.4 |
| Decision | **PROMOTE** | mean gate ∧ story_ok |

## Finding

1. Anti-period + stop framing removes Z1-style `........` collapses on the AB pack.  
2. Raw open QPFB2+BEAMKV still fails exact gold (TinyStories drift) — scores ~5 before FIX.  
3. **Constrained FIX** (ASKFAST/SEMWRAP) recovers near-known golds → mean **8.7**.  
4. Honest claim: **scoped constrained serve**, not open chat LM; SERVEALIGN HOLD remains for wrap-free open decode.

## Reproduce

```bash
npm run nano:asksmart
```

## Artifacts

- Summary: `results/nano-lm/wave-ab/asksmart_summary.json`  
- Trials: `results/nano-lm/wave-ab/trials/AB-ASKSMART-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_asksmart.py`

Next: **AB5 H-REALAPP**.
