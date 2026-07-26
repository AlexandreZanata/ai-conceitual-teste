# H-KVCACHE-Q — QT∘PFB2 session prefix KV (**KILL**)

> Smoke **KILL**. Dual-gate quality held, but warm TTFT failed to beat cold full-prefill. Tooling purged.

Wave Y Y8: shared session prefix (≈256–270 toks) + QT-int8 ∘ PFB K=2; warm path reuses prefix `DynamicCache` and prefills only the task suffix; gate = dual gate **and** mean TTFT warm < cold.

## Smoke

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|---|
| H-EARLY@QT | -14.0535 | -16.6837 | 26 | 1.000 | 0.00 | 12 |
| H-KVCACHE-Q K=2 | -13.9140 | -14.4416 | 55 | 2.000 | 0.25 | 12 |

TTFT: warm=3.08 ms · cold=2.39 ms · prefix_tokens=270 · weight_bytes≈13.6MB

**Decision: KILL (ttft_warm ≥ cold; no first-token↓)**

Code↑ and story≥parent−ε under QT∘PFB2, but incremental suffix+past path did **not** reduce first-token latency vs a single full prefill on this ≤5M student (overhead dominates at nano lengths).

## Lesson

Session-persistent prefix KV is not a free TTFT win on the current nano stack. Keep **BEAMKV** (share KV across beams within one query) and **SUMCACHE/ROLL** (compress active context). Do not claim serve-session TTFT↓ without a larger prefix/model or a cheaper cache clone. Do not revive STREAM parent=prev.

Commands (purged): were `npm run nano:kvcache` / `nano:kvcache:report` / `nano:formal:hkvcache`.
