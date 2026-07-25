# Phase E5 — fixed eval YAML suites

Prompts committed under `nano_lm/prompts/`; curated blobs regenerable via `npm run nano:curated`.  
**H-PROG / H-BTC formal claim packs stay at g01–g04 / b01–b04** (Wave W evidence unchanged).

| Suite | Path | Ids | Role |
|-------|------|-----|------|
| Prog heldout | `e5_prog_heldout.yaml` | g05–g08 | Extra programming eval from Phase E slices |
| BTC heldout | `e5_btc_heldout.yaml` | b05–b08 | Extra bitcoin eval (BIP-39/141/340 + RPC) |
| Frontier | `frontier_prompts.yaml` | r01–r04 | RFC/systems English @128 elongation |

Registry: `nano_lm/src/eval_suites.py` · builder: `frontier_packs.py`.  
Smoke: `npm run nano:e5` (CUDA; builds all suites; one-seed PACK serve on frontier).

Ids are mutually disjoint from smoke/fit/ood/howto/prog/btc claim packs.
