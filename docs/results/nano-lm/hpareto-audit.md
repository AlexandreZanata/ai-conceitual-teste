# H-PARETO smoke — tok/s↑ but GFLOPs↑ beyond tip+δ

Report-only instrumentation: scan formal util/tip pairs with est. GFLOPs. FLAG iff tok/s↑ **and** GFLOPs > tip·(1+δ) with δ=`0.05`. Does not tip-paste or delete code — flags dishonest efficiency claims.
Mode: `formal-corpus efficiency audit (report-only)`; wall_s=`0.006`.

| util | control | source | Δ tok/s | Δ GFLOPs | verdict |
|------|---------|--------|---------|----------|---------|
| H-BAT | H-EARLY | `formal-hbat/formal.json` | +2283.9 | +0.000 | KEEP |
| H-CBAT | H-BAT | `formal-hcbat/formal.json` | +1471.0 | +3.647 | FLAG |
| H-CHBAT | H-CBAT | `formal-hchbat/formal.json` | +1826.1 | -3.647 | KEEP |
| H-CPOOLB | H-POOLB | `formal-hcpoolb/formal.json` | +3594.7 | +0.892 | KEEP |
| H-FCPOOLB | H-CPOOLB | `formal-hfcpoolb/formal.json` | +286.5 | -0.297 | KEEP |
| H-FLAYB | H-FCPOOLB | `formal-hflayb/formal.json` | +1080.1 | +0.000 | KEEP |
| H-FUSEB | H-CHBAT | `formal-hfuseb/formal.json` | +442.1 | +0.000 | KEEP |
| H-GALL | H-GRAPH | `formal-hgall/formal.json` | -572.3 | +0.000 | KEEP |
| H-GRAPH | H-LAYB | `formal-hgraph/formal.json` | +1087.9 | +0.000 | KEEP |
| H-GRAPHF | H-FLAYB | `formal-hgraphf/formal.json` | +1134.5 | +0.000 | KEEP |
| H-LAYB | H-FUSEB | `formal-hlayb/formal.json` | +1001.8 | +0.000 | KEEP |
| H-POOLB | H-POOL | `formal-hpoolb/formal.json` | +3040.3 | +0.000 | KEEP |
| H-ROUTE | H-GRAPHF | `formal-hroute/formal.json` | +452.7 | -2.577 | KEEP |
| H-SERVE | H-EARLY | `formal-hserve/formal.json` | +2124.2 | +0.000 | KEEP |

**Decision: PROMOTE (Pareto audit live; 1 flagged)**

Flagged utils (do not claim GFLOPs efficiency): **H-CBAT**.

Tips unchanged. Measurement hygiene (Wave R).

Commands: `npm run nano:pareto` → `npm run nano:pareto:report`.
