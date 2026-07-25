# H-Q-TUNNEL smoke — tiny ε leak past causal MASK (**KILL**)

> Smoke **KILL**. Do not claim dual-gate win from wall↓ with identical continuations. Tooling purged. False formal PROMOTE (ε=1e-03 identity) discarded.

Wave X QI sandbox: patch GPT-Neo `_attn` so future keys get `score+log(ε)` instead of −∞ (ignore HF additive causal mask that would cancel the leak). Parent = strict-causal H-EARLY on prog@128. ≠ GROVER, ≠ SPIRAL, ≠ QCTX Born-rule.

Frozen: ε=0.05; max_new=32; seeds=3; prog pack; identity gate on story+code means.

**Decision: KILL (identity vs parent; tunnel had no effect)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | mean leak_budget | n |
|-----|---------------|--------------|--------------|------------------|---|
| H-EARLY causal | -14.8854 | -16.2692 | 21 | 0.0000 | 12 |
| H-Q-TUNNEL ε=5e-02 | -14.8854 | -16.2692 | 8 | 0.8803 | 12 |

## Lesson

Leaky causal attn moved logits slightly but **greedy EARLY continuations matched parent** (all 12 rows identical text), so story/code teacher LPs were identity. Wall↓ is warm-cache / order artifact — not a quality win. Tiny ε future-key tunnel is not a free EARLY upgrade. Next E.1: **H-Q-BELL** (distant-token correlated KV) — not another mask leak / GROVER amplify / SPIRAL.

Commands (purged): were `npm run nano:tunnel` / `nano:formal:htunnel*`.
