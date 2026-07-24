# H-MIX protocol — PRUN ckpt ⊕ LAY decode

Stack **train util** H-PRUN checkpoint with **decode util** H-LAY genes (frozen EARLY tip knobs inside LAY). Same PRUN student for both rows.
This is a **protocol note**, not a compose tip H-ID (compose branch SYS→JOINT→CACHE→CAP closed).
PROTOCOL iff lp ≥ PRUN−ε and wall < PRUN; else KILL (do not stack).
Note: `protocol stack; not a tip H-ID`.

| family | mean teacher_lp | Δ lp | mean wall_ms | Δ wall | mean est GFLOPs | Δ GFLOPs | n |
|--------|-----------------|------|--------------|--------|-----------------|----------|---|
| H-PRUN | -16.0305 | — | 87 | — | 6.251 | — | 3 |
| H-MIX | -16.0305 | +0.0000 | 48 | -38 | 6.251 | +0.000 | 3 |

**Decision: PROTOCOL (PRUN ckpt ⊕ LAY; not a tip H-ID)**

Champion tips stay on separate axes: train **H-STAG** (+ optional PRUN), decode **H-EARLY** / **H-POOL** (+ optional LAY). Do not invent H-MIX tip.

Commands: `npm run nano:mix` → `npm run nano:mix:report`.
