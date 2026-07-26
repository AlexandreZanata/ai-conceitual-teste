# H-CTXULTRA — triple-doc beyond CTXMAX (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AF1 · Session: `.local/wave-af/SESSION.md`  
> Parent: **H-CTXMAX** · **H-SEMWRAP** / **H-ASKFAST** · Pack: AF0 held-out asks  
> Module: `nano_lm/src/ctxultra_ops.py` · Runner: `npm run nano:ctxultra` (`nano:af:ctxultra`)

## Hypothesis

Serve each held-out AF ask under **triple curated sources** with **ROLL/SUMCACHE at K=7** (deeper than CTXMAX dual K=5) — proving **mean L_eff ↑ vs CTXMAX 31043.2** and ≥ **7**/10 long usable without STREAM / naive flat CTX.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ 7.0 |
| usable | **10**/10 | ≥ **7**/10 |
| FALSE_HIT | **0**/10 | any → **KILL** |
| mean sources | **3.0** | ≥ **3** |
| mean L_eff (combined) | **56965** | > CTXMAX **31043.2** |
| mean slices | **21.0** | ≥ **7** (K_ultra) |
| mean active | **352** | ≤ 352 |
| FIX count | **0** | — |
| Decision | **PROMOTE** | usable ∧ L_eff↑ ∧ triple-doc ∧ quality |

## Frontier EVAL (Cursor)

| Trial | Score | error? | Notes (3 bullets) |
|-------|------:|:------:|-------------------|
| AF-HITL-01 | 9 | no | BIP definition correct · audience named · wrap TRUE_HIT |
| AF-HITL-02 | 9 | no | BIP 9 named · matches Core bips.md · no false cite |
| AF-HITL-03 | 9 | no | scalar+compound · matches Rust book · short |
| AF-HITL-04 | 9 | no | Point + `__init__` · fields set · pasteable |
| AF-HITL-05 | 9 | no | prints 0,1,2 · endpoint rule · correct |
| AF-HITL-06 | 9 | no | `add` returns sum · minimal · product wrap ok |
| AF-HITL-07 | 9 | no | ownership vs GC · compile-time · two sentences |
| AF-HITL-08 | 9 | no | `struct User` · `name: String` · valid Rust |
| AF-HITL-09 | 9 | no | P2P download+validate · Core README · honest |
| AF-HITL-10 | 9 | no | TLS handshake keys+params · RFC 8446 · plain |

**Running mean:** 9.0 · **Errors:** 0/10 · **FIX actions:** 0 (no score < 8)

## Finding

1. Every AF0 trial pairs secondary + tertiary curated sources with the primary (triple-doc).  
2. Combined mean L_eff **56965** > CTXMAX **31043**; mean slices **21** (7×3) vs CTXMAX **10**.  
3. All 10 asks TRUE_HIT via wrap/SEMWRAP (scoped assist — **not** open chat).  
4. Forbidden unused: STREAM · KVCACHE-Q · GENCACHE · naive CTX.

## Reproduce

```bash
npm run nano:af:session
npm run nano:ctxultra
# alias: npm run nano:af:ctxultra
```

## Artifacts

- Summary: `results/nano-lm/wave-af/ctxultra_summary.json`  
- Trials: `results/nano-lm/wave-af/trials/AF-CTXULTRA-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_ctxultra.py`

Next: **AF2 H-SMARTULTRA** — ASK→EVAL→FIX×10 before AF3.
