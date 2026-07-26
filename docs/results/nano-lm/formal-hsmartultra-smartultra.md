# H-SMARTULTRA — triple-hop retrieve/compose/cite (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 AF2 · Session: `.local/wave-af/SESSION.md`  
> Parent: **H-SMARTMAX** · **H-CTXULTRA** · **H-SEMWRAP** / **H-ASKSMART** · Pack: AF0 held-out asks  
> Module: `nano_lm/src/smartultra_ops.py` · Runner: `npm run nano:smartultra` (`nano:af:smartultra`)

## Hypothesis

Stress **SEMWRAP retrieve + primary-source cite** on **triple-hop adversarial paraphrases** of AF0 (secondary **and** tertiary domain distractors + informal noise) — mean ≥ 7.0 with **false-hit ≈ 0** and **cite_ok ≥ 8**/10 — beyond SMARTMAX (dual-hop · cite≥7), without open-chat claims.

## Gate (Cursor ASK→EVAL→FIX×10)

| Metric | Result | Pass bar / rule |
|--------|-------:|-----------------|
| mean score | **9.0** | ≥ **7.0** |
| FALSE_HIT | **0**/10 | any → **KILL** |
| TRUE_HIT | **10**/10 | — |
| cite_ok (primary) | **10**/10 | ≥ **8**/10 (stricter than SMARTMAX 7) |
| errors | **0**/10 | ≤ 3 |
| FIX count | **0** | — |
| SEMWRAP route | **10**/10 | compose SEMWRAP+ASKSMART |
| Decision | **PROMOTE** | mean≥7 ∧ false-hit=0 ∧ cite≥8 ∧ quality |

## Frontier EVAL (Cursor)

| Trial | Score | cite? | Notes (3 bullets) |
|-------|------:|:-----:|-------------------|
| AF-HITL-01 | 9 | yes | BIP purpose · ignore BIP-32/39 · primary bip-0001 |
| AF-HITL-02 | 9 | yes | BIP 9 · ignore BIP-1/README · primary bips.md |
| AF-HITL-03 | 9 | yes | scalar+compound · ignore ownership/vars · ch03-02 |
| AF-HITL-04 | 9 | yes | Point class · ignore queues/intro · classes |
| AF-HITL-05 | 9 | yes | range(3)→0,1,2 · ignore Point/intro · control |
| AF-HITL-06 | 9 | yes | add(a,b) · ignore range/I/O · intro |
| AF-HITL-07 | 9 | yes | ownership vs GC · ignore types/User · ch04 |
| AF-HITL-08 | 9 | yes | struct User · ignore ownership/types · ch05 |
| AF-HITL-09 | 9 | yes | Core P2P validate · ignore notes/bips · README |
| AF-HITL-10 | 9 | yes | TLS handshake · ignore RFC791/8949 · rfc8446 |

**Running mean:** 9.0 · **Errors:** 0/10 · **FIX actions:** 0

## Finding

1. All 10 triple-hop paraphrases normalize-differ from AF0 parents and recover correct golds.  
2. Secondary+tertiary distractors (BIP-32/39, README/bips, ownership/structs, RFC791/8949, …) cause **0** FALSE_HIT.  
3. Primary cite_ok **10**/10 beats SMARTMAX cite bar (7) with AF bar **8**.  
4. Forbidden unused: QI · ZPREF · MIXD · open-chat claim.

## Reproduce

```bash
npm run nano:af:session
npm run nano:smartultra
# alias: npm run nano:af:smartultra
```

## Artifacts

- Summary: `results/nano-lm/wave-af/smartultra_summary.json`  
- Trials: `results/nano-lm/wave-af/trials/AF-SMARTULTRA-HITL-01.json` … `10.json`  
- Contract: `nano_lm/tests/test_smartultra.py`

Next: **AF3 H-FASTULTRA** — ASK→EVAL→FIX×10 before AF4.
