# Wave Z — HITL product eval (**COMPLETE**)

> Lab: `.local/pesquisa.md` §9.  
> Public report: [wave-z-hitl.md](wave-z-hitl.md) · Paper-lab: [paper-lab-wave-z.md](paper-lab-wave-z.md)  
> Champion export: `results/nano-lm/wave-z/models/champion/` (gitignored weights).

**Status: COMPLETE** · Thesis: **PFB recipes ≠ interactive LM; wrap + error-bank loop** (claim **H-ZWRAP**).

## Stage queue

| Stage | ID | Status | Notes |
|------:|----|--------|-------|
| Z0 | **EXPORT** | **DONE** | `champion-qpfb2-v0` = H-ABS-QPFB2 |
| Z1 | **HITL-10** | **DONE — FAIL** | mean **1.0**, errors **10**/10 → [wave-z-hitl-z1.md](wave-z-hitl-z1.md) |
| Z2 | MANUAL×10 | **DONE — PASS** | mean **9.0**; `champion-wrap-v0` → [wave-z-hitl-z2.md](wave-z-hitl-z2.md) |
| Z3 | **H-ZERR** | **DONE — PROMOTE** | bank CE; story −14.56 ≥ parent−ε → [wave-z-zerr.md](wave-z-zerr.md) |
| Z4 | HITL-10 verify | **DONE — PASS** | A/B mean **9.0**; C mean **1.0**; claim **H-ZWRAP** → [wave-z-hitl-z4.md](wave-z-hitl-z4.md) |
| Z5 | LOOP / SERVEALIGN | **SKIP** | Not needed for known-ask wrap product |
| Z5c | **DEPL-Y** | **DONE — FROZEN** | 128 vs long routes → [wave-z-depl-y.md](wave-z-depl-y.md) |
| **Z6** | REPORT | **DONE** | [wave-z-hitl.md](wave-z-hitl.md) · [paper-lab-wave-z.md](paper-lab-wave-z.md) |

## Product

| Goal | Use |
|------|-----|
| Known-ask HITL | **H-ZWRAP** `--wrap` LOOKUP |
| @128 code | QPFB2 + BEAMKV/TCACHE/SCORERAM |
| Long | ROLL / SUMCACHE / GPFB4-LONG |
| Forbidden | STREAM / KVCACHE-Q / GENCACHE / GPFB-K=2 / ZERR-as-chat |

```bash
npm run nano:z:z6
npm run nano:z:ask -- --wrap --question "…"
```

## Doctrine

- Judge = frontier chat model (not ≤5M self-grade).  
- **Known-ask product** = **H-ZWRAP** LOOKUP; **H-ZERR** = story-safe CE only.  
- Forbidden: STREAM / KVCACHE-Q / GENCACHE / GPFB K=2 / MIXD retrain.  
- Live checklist: `.local/wave-z/SESSION.md` (archive of HITL block).
