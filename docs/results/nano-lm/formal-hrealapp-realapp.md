# H-REALAPP — packaged scoped apps (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.3 AB5 · Session: `.local/wave-ab/SESSION.md`  
> Stacks: **app-known** (ZWRAP→SEMWRAP→ASKFAST) · **app-longdoc** (LONGAPP/ROLL/SUMCACHE)  
> Module: `nano_lm/src/realapp_ops.py` · Runner: `npm run nano:realapp`

## Hypothesis

Packaging **≥1** runnable scoped app (one-pager + command + DEPL honesty) with Cursor **ASK→EVAL→FIX×10 per app** yields a shippable product path without open-chat claims.

## Gate (Cursor ASK→EVAL→FIX×10 / app)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **2** | ≥ **1** |
| apps PROMOTE | **2**/2 | ≥1 PROMOTE · 0 KILL |
| mean across apps | **8.85** | quality ≥7 · errors ≤3 / app |
| app-known mean | **8.7** | SERVE in-scope · honest OOS refuse |
| app-longdoc mean | **9.0** | L_eff≫W ctx + SEMWRAP |
| false-hit | **0** | KILL if any |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | product ∧ no KILL |

## Finding

1. **app-known** serves known-ask + howto via ASKFAST/SEMWRAP; long-doc asks get honest out-of-scope refuse (FIX×3).  
2. **app-longdoc** serves the full pack with LONGAPP windows + wrap; usable curated L_eff≫W.  
3. Product claim stays **scoped packaged apps**, not open chat LM.  
4. Default demo spine remains H-ZWRAP + H-WRAPBANK (+ AB stack) until AB6 final HITL.

## Reproduce

```bash
npm run nano:realapp
npm run nano:realapp -- --app app-known
npm run nano:realapp -- --app app-longdoc
```

## Artifacts

- Summary: `results/nano-lm/wave-ab/realapp_summary.json`  
- One-pagers: [app-known.md](app-known.md) · [app-longdoc.md](app-longdoc.md)  
- Trials: `AB-REALAPP-KNOWN-HITL-01…10` · `AB-REALAPP-LONGDOC-HITL-01…10`  
- Contract: `nano_lm/tests/test_realapp.py`

Next: **AB6 AB-HITL-10** (**DONE** — see [wave-ab-hitl.md](wave-ab-hitl.md)). Next wave stage: **AB7 AB-REPORT**.
