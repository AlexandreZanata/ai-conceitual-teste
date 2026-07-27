# Wave AW0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-aw/SESSION.md`  
> Module: `nano_lm/src/aw_session_ops.py` · Runner: `npm run nano:aw:session`  
> Parent: [av-freeze.md](av-freeze.md) (Wave AW reopened explicitly via lab-book reopen after AV-FREEZE)

## Decision

**PROMOTE** — Freeze AW packs: product-keep charter · pressure-para protocol (N≥20 ≠ AV/AU) · NANOGEN7 TAC hyp (teacher-anchored novel continue; **span-fallback ≠ gen IQ**) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone · **not** NANOGEN6+rename.  
Anti-FP signed. Generative claim locked until AW3 PROMOTE.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Product-keep charter | 1 | DECODE content · pressure para · FH0 · modes · KB · latency (AW1) |
| Pressure-para protocol | 20 | held-out ≠ AV/AU · no bank stuffing (AW1) |
| NANOGEN7 hypothesis | 1 | teacher-anchored continue (TAC) · span-fallback = PEAK/LOOKUP credit only (AW3) |
| True gen judge | 1 | span-fallback ≠ gen · telemetry ≠ content_ok (AW3) |
| Real-eval protocol | 1 | live ask · eval=prod · anti-FP (AW4) |
| Ask battery | 8 | frozen live rows (scored at AW4) |

## Cited AV locks

AV-FREEZE, AV-REAL-EVAL, H-NANOGEN6, H-PRODSHIP, H-SHIPUI2

## Product-keep bars

- para_hit_min: **0.7** (AV PRODSHIP baseline; pressure ≠ AV/AU)  
- false_hit_max: **0**  
- pressure_para_min_n: **20**  
- decode_gibberish_neq_content_ok: **True**  
- default_ask_near_miss: **ABSTAIN**  
- eval_eq_prod_ask: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no re-SEMFIX/ADVSAFE unless PRODKEEP fails

## Post-AV debts (frozen)

| id | bar |
|----|-----|
| product_regression_hold | regression_hold vs AV PRODSHIP/SHIPUI2 |
| pressure_human_para | para_hit_min on pressure held-out set |
| false_hit_zero | false_hit_max=0 |
| mode_ui_always | modes_visible 4/4 |
| true_continue_unmet | tac_method_distinct; true_continue_ablated gate |
| span_fallback_neq_gen | span_fallback_neq_gen True |

## Pressure-para protocol

- held_out: **True**  
- bank_stuff_forbidden: **True**  
- neq_av_pack: **True**  
- neq_au_pack: **True**  
- min_n: **20**  
- path: `nano:z:ask --wrap --semwrap`  

| id | parent |
|----|--------|
| AW-PARA-01 | add |
| AW-PARA-02 | add |
| AW-PARA-03 | add |
| AW-PARA-04 | add |
| AW-PARA-05 | add |
| AW-PARA-06 | add |
| AW-PARA-07 | add |
| AW-PARA-08 | add |
| AW-PARA-09 | add |
| AW-PARA-10 | add |
| AW-PARA-11 | add |
| AW-PARA-12 | add |
| AW-PARA-13 | add |
| AW-PARA-14 | add |
| AW-PARA-15 | add |
| AW-PARA-16 | add |
| AW-PARA-17 | add |
| AW-PARA-18 | add |
| AW-PARA-19 | add |
| AW-PARA-20 | add |

## NANOGEN7 hypothesis (one idea)

One idea: teacher-anchored novel continue (TAC) — DECODE may emit only tokens that are novel vs retrieved span (no contiguous span copy) AND in code-teacher top-k at that step; pure span copy → label PEAK (zero gen credit); no novel teacher-consistent continue → ABSTAIN; wall_ms/n_new ≠ content_ok; not a NANOGEN6 refuse-or-continue rename; bar = true_continue_ablated PROMOTE else HOLD

## True gen judge

- span_fallback_neq_gen: True  
- gold_substring_insufficient: True  
- gibberish_tail_fails: True  
- telemetry_neq_content_ok: True  
- scoring: `short_answer_f1_or_hitl_true_continue_only`  
- promote_bar: `true_continue_ablated else HOLD`

## Real-eval protocol

- live_ask_battery: True  
- eval_eq_prod_ask: True  
- span_fallback_neq_gen: True  
- gen_claim_rule: only if AW3 H-NANOGEN7 PROMOTE (true_continue_ablated; TAC; span-fallback ≠ gen credit)  
- mini_agi_rule: forbidden while NANOGEN7 HOLD

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| AW-ASK-01 | known_lookup | LOOKUP |
| AW-ASK-02 | ood_abstain | ABSTAIN |
| AW-ASK-03 | near_miss | ABSTAIN |
| AW-ASK-04 | labeled_peak | PEAK |
| AW-ASK-05 | decode_content | DECODE |
| AW-ASK-06 | junk_trap | ABSTAIN |
| AW-ASK-07 | human_para | LOOKUP |
| AW-ASK-08 | decode_gibberish_bar | DECODE |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring / gibberish-tail / truncate-to-span ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = AW3 only; no vanity re-SEMFIX/ADVSAFE unless PRODKEEP fails; no Wave AX invent; no CTX/SMART/FAST clone; no NANOGEN7 = NANOGEN6+rename; TAC ≠ refuse-or-continue clone

## North star

Nano generative / mini-AGI-inspired ≤5M: hold Caminho A (PRODKEEP + SHIPKEEP); true ablated DECODE via H-NANOGEN7 TAC (teacher-anchored novel continue) without span-fallback-as-IQ before generative or mini-AGI claim

## Ship lock (until AV PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM

## Validate

```bash
npm run nano:aw:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`); near-miss maps to ABSTAIN alias.  
Artifacts (gitignored): `results/nano-lm/wave-aw/aw0_session.json` · `results/nano-lm/wave-aw/trials/AW-*.json`.  
Contract: `nano_lm/tests/test_aw_session.py`.

## Claims

- AV packs frozen for Wave AW — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM**.  
- Generative PROMOTE only via later **AW3 H-NANOGEN7** true_continue_ablated (span-fallback ≠ gen credit).  
- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · gold-substring PROMOTE · truncate-to-span as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · Wave AX invent · CTX/SMART/FAST/APP clone · NANOGEN6+rename · bank stuffing · vanity re-SEMFIX.

Next: **AW1 H-PRODKEEP** — **DONE PROMOTE** (`npm run nano:prodkeep`) · next **AW2 H-SHIPKEEP**.
