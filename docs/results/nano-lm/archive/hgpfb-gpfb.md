# H-ABS-GPFB — GENC∘PFB2 (**KILL**)

> Smoke **KILL**. Do not claim GENC∘PFB2 (K=2) as a free compose. Tooling purged.

Wave X absurd sandbox: freeze H-GENC smoke best genome (prompt stride/retrieve + exit + quant); serial decode on GENC ctx for beam parity; PFB commit K=2 with parent-fallback; wall↓ vs same-run k=4. Parent = GENC-serial n=1 (same genome).

Frozen: K2=2; K4=4; PFB_TEMP=0.8; ε_lp=0.05; max_new=32; seeds=3; gene0=`{k_retrieve:1, chunk_len:32, stride:32, quant_bits:16, exit_depth:1}`.

## Smoke

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-GENC-serial n=1 | -12.9634 | -15.8878 | 19 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-GPFB k=4 | -12.7501 | -15.0023 | 54 | 4.000 | 0.50 | 0.25 | 12 |
| H-ABS-GPFB k=2 | -12.8182 | -16.1024 | 46 | 2.000 | 0.25 | 0.17 | 12 |

**Decision: KILL (code_lp -16.1024 ≤ parent -15.8878)**

K=2 failed the code↑ gate (Δ≈−0.21) despite story≈parent and wall↓ vs k=4. Same-run **k=4** did lift code (Δ≈+0.89) and story, but that is a different H-ID (full PFB under GENC), not the PFB2 efficiency claim under test.

## Lesson

GENC∘PFB2 does **not** inherit PFB2’s dual-gate: aggressive GENC exit + K=2 leaves too little eligible diversity (elig≈0.25, switch≈0.17) so the commit often stays near-parent or worse on code. PFB under GENC may still be worth a **separate** k=4 H-ID later — do not smuggle it in by weakening this gate. Do not revive tip-compose / INTERF / CBON.

Commands (purged): were `npm run nano:gpfb` / `nano:gpfb:report` / `nano:formal:hgpfb`.
