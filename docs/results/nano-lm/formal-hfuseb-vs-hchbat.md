# Formal H-FUSEB vs H-CHBAT (FUSE under CHBAT batch)

Source: `results/nano-lm/formal-hfuseb/formal.json`
Wall clock: 10.1s

Shared formal B2 + EARLY + formal KVSEL threshold. Fit≠eval.
Dual-budget FLASH⊕KVSEL gate on CHBAT path vs always-on CHBAT.
Mode: `dual-budget FUSE under CHBAT; n=1 near-greedy; long eval`. Kill if |Δlp| > ε or no tok/s/wall win.
n_prompts=8 chunk_size=`256` budgets=`[16, 64]` target_tokens=`128`.
Selected `kv_threshold` per seed: `[0, 32, 32]`.

| family | mean teacher_lp | Δ lp | mean tok/s | Δ tok/s | mean wall_ms/prompt | Δ wall | n |
|--------|-----------------|------|------------|---------|---------------------|--------|---|
| H-CHBAT | -13.9851 | — | 3419.1 | — | 6 | — | 3 |
| H-FUSEB | -13.9851 | +0.0000 | 3861.2 | +442.1 | 2 | -4 | 3 |

**Decision:** PROMOTE (FUSE under CHBAT batch)

Throughput util on CHBAT axis — does not replace H-EARLY / H-CHBAT tips.

Commands: `npm run nano:formal:hfuseb` → `npm run nano:formal:hfuseb:report`.
