# Wave AU0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-au/SESSION.md`  
> Module: `nano_lm/src/au_session_ops.py` · Runner: `npm run nano:au:session`  
> Parent: [at-freeze.md](at-freeze.md) (Wave AU reopened explicitly via lab-book reopen)

## Decision

**PROMOTE** — Freeze AU packs: product-debt suite (live-audit) · human-para protocol · NANOGEN5 hyp (strict F1/HITL judge; **not** gold-substring) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked until AU3 PROMOTE.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Product-debt suite | 1 | near-miss on ask · human para · PEAK usable · usability (AU1) |
| Human-para protocol | 8 | held-out rewrites · no bank stuffing (AU1) |
| NANOGEN5 hypothesis | 1 | gibberish-tail gate · strict ≥5.5 vs NANOGEN4 5.5 (AU3) |
| Strict gen judge | 1 | gold-substring insufficient · F1/HITL (AU3) |
| Real-eval protocol | 1 | live ask · eval=prod · anti-FP (AU4) |
| Ask battery | 7 | frozen live rows (scored at AU4) |

## Cited AT locks

AT-FREEZE, AT-REAL-EVAL, H-NANOGEN4, H-PRODREG, H-SHIPAPP

## Product-debt bars

- para_hit_min: **0.7** (AS PARAEXT2 baseline 0.80)  
- false_hit_max: **0** (AS ADVSAFE 0/20)  
- default_ask_near_miss: **ABSTAIN**  
- peak_usable_or_abstain: **True**  
- eval_eq_prod_ask: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no re-SEMFIX/ADVSAFE unless PRODHARD fails

## Live-audit debts (frozen)

| id | bar |
|----|-----|
| near_miss_default_ask | ABSTAIN on near_miss; FH=0 |
| human_para_heldout | para_hit_min on held-out human set |
| peak_usable_span | readable_span_or_abstain |
| answer_usability | mode_and_usable_when_claimed |

## Human-para protocol

- held_out: **True**  
- bank_stuff_forbidden: **True**  
- min_n: **8**  
- path: `nano:z:ask --wrap --semwrap`  

| id | parent |
|----|--------|
| AU-PARA-01 | add |
| AU-PARA-02 | add |
| AU-PARA-03 | add |
| AU-PARA-04 | add |
| AU-PARA-05 | add |
| AU-PARA-06 | add |
| AU-PARA-07 | add |
| AU-PARA-08 | add |

## NANOGEN5 hypothesis (one idea)

One idea: ablated DECODE with snippet-prefix + gibberish-tail gate (truncate/refuse when continuation leaves retrieved-span readability) scored by short-answer F1/HITL — gold-substring alone insufficient; beat archived NANOGEN4 ablated 5.5 under STRICT judge; bar = strict_ablated≥5.5 else HOLD

## Strict gen judge

- gold_substring_insufficient: True  
- gibberish_tail_fails: True  
- scoring: `short_answer_f1_or_hitl`  
- promote_bar: `strict_ablated≥5.5`

## Real-eval protocol

- live_ask_battery: True  
- eval_eq_prod_ask: True  
- gen_claim_rule: only if AU3 H-NANOGEN5 PROMOTE (strict_ablated≥5.5)  
- mini_agi_rule: forbidden while NANOGEN5 HOLD

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| AU-ASK-01 | known_lookup | LOOKUP |
| AU-ASK-02 | ood_abstain | ABSTAIN |
| AU-ASK-03 | near_miss | ABSTAIN |
| AU-ASK-04 | labeled_peak | PEAK |
| AU-ASK-05 | decode_smoke | DECODE |
| AU-ASK-06 | junk_trap | ABSTAIN |
| AU-ASK-07 | human_para | LOOKUP |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; no gibberish-tail PROMOTE; eval path = prod ask path; generative bar = AU3 only; no vanity re-SEMFIX/ADVSAFE unless PRODHARD fails; no Wave AV invent; no CTX/SMART/FAST clone

## North star

Nano generative / mini-AGI-inspired ≤5M: harden Caminho A under live human metrics now (PRODHARD + SHIPREAL); strict ablated DECODE (H-NANOGEN5) before generative or mini-AGI claim

## Ship lock (until AU PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix) — not unlabeled open chat LM

## Validate

```bash
npm run nano:au:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`); near-miss maps to ABSTAIN alias.  
Artifacts (gitignored): `results/nano-lm/wave-au/au0_session.json` · `results/nano-lm/wave-au/trials/AU-*.json`.  
Contract: `nano_lm/tests/test_au_session.py`.

## Claims

- AU packs frozen for Wave AU — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix) — not unlabeled open chat LM**.  
- Generative PROMOTE only via later **AU3 H-NANOGEN5** strict ablated bar ≥5.5.  
- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · gold-substring PROMOTE · gibberish-tail pass · eval↔prod gap · mini-AGI claim early · Wave AV invent · CTX/SMART/FAST/APP clone · bank stuffing · vanity re-SEMFIX.

Next: **AU1 H-PRODHARD** — close live-audit debts on default ask.
