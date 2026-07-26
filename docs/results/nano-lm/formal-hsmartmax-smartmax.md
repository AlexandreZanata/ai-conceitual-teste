# H-SMARTMAX — multi-hop retrieve/compose/cite (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AE2 · Session: `.local/wave-ae/SESSION.md`  
> Parent: **H-HARDPARA** · **H-COMPOSE** · **H-SEMWRAP** / **H-ASKSMART** · Pack: AE0 held-out asks  
> Module: `nano_lm/src/smartmax_ops.py` · Runner: `npm run nano:smartmax`

## Hypothesis

Stress **SEMWRAP retrieve + primary-source cite** on **multi-hop adversarial paraphrases** of AE0 (secondary-domain distractors + informal noise) — mean ≥ 7.0 with **false-hit ≈ 0** and **cite_ok ≥ 7**/10 — beyond HARDPARA+COMPOSE, without open-chat claims.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ **7.0** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| TRUE_HIT | **10**/10 | — |
| cite_ok (primary) | **10**/10 | ≥ **7**/10 |
| errors | **0**/10 | ≤ 3 |
| FIX count | **0** | — |
| SEMWRAP route | **10**/10 | compose SEMWRAP+ASKSMART |
| Decision | **PROMOTE** | mean≥7 ∧ false-hit=0 ∧ cite≥7 ∧ quality |

## Finding

1. All 10 multi-hop paraphrases normalize-differ from AE0 parents and recover correct golds.  
2. Secondary distractors (BIP-39 vs BIP-32, REST vs RPC cookie, TLS vs IP TTL, …) do not cause FALSE_HIT.  
3. EXACT wrap hits now carry `source_id` so primary cite quality is measurable.  
4. Forbidden unused: QI · ZPREF · MIXD · open-chat claim.

## Reproduce

```bash
npm run nano:ae:session
npm run nano:smartmax
```

## Artifacts

- Summary: `results/nano-lm/wave-ae/smartmax_summary.json`  
- Trials: `results/nano-lm/wave-ae/trials/AE-SMARTMAX-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_smartmax.py`  
- Cite fix: `semwrap_ops.semantic_lookup` EXACT meta includes `source_id`

Next: **AE3 H-FASTMAX**.
