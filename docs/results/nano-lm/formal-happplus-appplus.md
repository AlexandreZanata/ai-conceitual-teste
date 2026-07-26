# H-APPPLUS — app-howto + known/longdoc (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8.5 AC4 · §12.1 · Session: `.local/wave-ac/SESSION.md`  
> Parent: **H-REALAPP** · Pack: AC0 held-out asks · New: **app-howto**  
> Module: `nano_lm/src/appplus_ops.py` · Runner: `npm run nano:appplus`

## Hypothesis

Ship a stronger **`app-howto`** surface (ASKSMART ± SEMWRAP) while keeping **app-known** and **app-longdoc** green on the held-out AC pack — DEPL honesty, no open-chat claim.

## Gate (Cursor ASK→EVAL→FIX×10 / app)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| apps packaged | **3** | ≥ 3 (known + longdoc + howto) |
| apps PROMOTE | **3**/3 | howto ∧ known ∧ longdoc green · 0 KILL |
| mean across apps | **8.6** | quality ≥7 · errors ≤3 / app |
| app-known mean | **8.6** | SERVE known+howto · honest OOS on long-doc |
| app-longdoc mean | **9.0** | full pack + LONGAPP ctx |
| app-howto mean | **8.3** | SERVE howto only · honest OOS else |
| false-hit | **0** | KILL if any |
| open-chat claim | **rejected** | DEPL honesty |
| Decision | **PROMOTE** | product ∧ no KILL |

## Finding

1. **app-howto** is a first-class packaged app with one-pager + npm route.  
2. Known/longdoc stay PROMOTE on the held-out AC set (not only AB).  
3. Out-of-scope asks get honest refuse (FIX routing) — not wrap leak.  
4. Claim remains scoped packaged apps — **not** open chat LM.

## Reproduce

```bash
npm run nano:appplus
npm run nano:appplus -- --app app-howto
npm run nano:appplus -- --app app-known
npm run nano:appplus -- --app app-longdoc
```

## Artifacts

- Summary: `results/nano-lm/wave-ac/appplus_summary.json`  
- One-pagers: [app-howto.md](app-howto.md) · [app-known.md](app-known.md) · [app-longdoc.md](app-longdoc.md)  
- Trials: `AC-APPPLUS-{KNOWN,LONGDOC,HOWTO}-HITL-01…10`  
- Contract: `nano_lm/tests/test_appplus.py`

Next: **AC5 AC-HITL-10** (**DONE** — see [wave-ac-hitl.md](wave-ac-hitl.md)). Next wave stage: **AC6 AC-REPORT**.
