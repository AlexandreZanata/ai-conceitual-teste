# H-ABS-REV smoke — time-reversed prefill (**KILL**)

> Smoke **KILL**. Do not claim code IQ from reverse-prefill KV. Tooling purged.

Wave X ABS sandbox: reverse prompt token ids for **chunked KV prefill only** (B=32), then generate forward under EARLY. Parent = forward-chunk EARLY (same B) on prog@128. ≠ INTERF α-BoN, ≠ MIXD, ≠ CKD.

Frozen: ε=0.05; chunk_size=32; seeds=3; max_new=32; prog pack.

**Decision: KILL (code_lp -19.2446 < parent−ε -16.3192)**

## Arms

| arm | mean story_lp | mean code_lp | mean wall_ms | n |
|-----|---------------|--------------|--------------|---|
| H-EARLY forward-prefill | -14.8854 | -16.2692 | 26 | 12 |
| H-ABS-REV reverse-prefill | -14.8041 | -19.2446 | 12 | 12 |

## Lesson

Reverse-prefill was faster (wall↓) and held story≈parent, but **hurt** `code_teacher_lp` (Δ ≈ −2.98 vs parent−ε). Reading the prompt end→start into KV is not a free code-IQ lift vs forward prefill. Next E.1: **H-Q-ANNEAL** (annealing exit-depth/temp schedule) — not another prefill reorder / INTERF mix.

Commands (purged): were `npm run nano:absrev` / `nano:formal:habsrev*`.
