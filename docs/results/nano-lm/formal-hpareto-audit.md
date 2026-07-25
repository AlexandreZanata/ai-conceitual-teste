# Formal H-PARETO — efficiency audit (report-only)

Source: `results/nano-lm/formal-hpareto/formal.json`
Wall clock: 0.006s

Fit≠eval already enforced inside each scanned formal. FLAG iff tok/s↑ and GFLOPs > tip·(1+δ), δ=`0.05`. Instrumentation gate — not a tip H-ID.
n_pairs=`14` n_flagged=`1` mode=`formal-corpus efficiency audit (report-only)`.

| util | control | source | Δ tok/s | Δ GFLOPs | util GFLOPs | tip GFLOPs | verdict |
|------|---------|--------|---------|----------|-------------|------------|---------|
| H-BAT | H-EARLY | `formal-hbat/formal.json` | +2283.9 | +0.000 | 0.900 | 0.900 | KEEP |
| H-CBAT | H-BAT | `formal-hcbat/formal.json` | +1471.0 | +3.647 | 11.057 | 7.410 | FLAG |
| H-CHBAT | H-CBAT | `formal-hchbat/formal.json` | +1826.1 | -3.647 | 7.410 | 11.057 | KEEP |
| H-CPOOLB | H-POOLB | `formal-hcpoolb/formal.json` | +3594.7 | +0.892 | 51.568 | 50.676 | KEEP |
| H-FCPOOLB | H-CPOOLB | `formal-hfcpoolb/formal.json` | +286.5 | -0.297 | 43.682 | 43.979 | KEEP |
| H-FLAYB | H-FCPOOLB | `formal-hflayb/formal.json` | +1080.1 | +0.000 | 43.682 | 43.682 | KEEP |
| H-FUSEB | H-CHBAT | `formal-hfuseb/formal.json` | +442.1 | +0.000 | 7.410 | 7.410 | KEEP |
| H-GALL | H-GRAPH | `formal-hgall/formal.json` | -572.3 | +0.000 | 7.410 | 7.410 | KEEP |
| H-GRAPH | H-LAYB | `formal-hgraph/formal.json` | +1087.9 | +0.000 | 7.410 | 7.410 | KEEP |
| H-GRAPHF | H-FLAYB | `formal-hgraphf/formal.json` | +1134.5 | +0.000 | 43.682 | 43.682 | KEEP |
| H-LAYB | H-FUSEB | `formal-hlayb/formal.json` | +1001.8 | +0.000 | 7.410 | 7.410 | KEEP |
| H-POOLB | H-POOL | `formal-hpoolb/formal.json` | +3040.3 | +0.000 | 11.614 | 11.614 | KEEP |
| H-ROUTE | H-GRAPHF | `formal-hroute/formal.json` | +452.7 | -2.577 | 41.016 | 43.593 | KEEP |
| H-SERVE | H-EARLY | `formal-hserve/formal.json` | +2124.2 | +0.000 | 7.393 | 7.393 | KEEP |

**Decision:** PROMOTE (Pareto audit live; 1 flagged)

Flagged utils (do not claim GFLOPs efficiency): **H-CBAT**.

Tips / SERVE / ROUTE unchanged as tips. Wave R measurement hygiene.

Commands: `npm run nano:formal:hpareto` → `npm run nano:formal:hpareto:report`.
