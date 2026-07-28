# Wave BD0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 · Session: `.local/wave-bd/SESSION.md`  
> Module: `nano_lm/src/bd_session_ops.py` · Runner: `npm run nano:bd:session`  
> Parent: [bc-freeze.md](bc-freeze.md) (Wave BD reopened explicitly via lab-book reopen after BC-FREEZE)

## Decision

**PROMOTE** — Freeze BD packs: BD-FOREVER (N≥12 · reverse≠f-string · mul≠add · wrong-bank neighbors + paraphrases ≠ BA/BB/BC/AZ) · BA-FOREVER hold · BB-FOREVER hold · BC-FOREVER hold · AZ hold (div·sub·BIP FH0 · `a.clear()` LOOKUP) · §1 anti-FP scoreboard · ctx/speed baselines from BC · gen stance **defer** (CAPCHECK closed; **H-NANOGEN14**; M1|M2|M3 named; **not** NANOGEN14=NANOGEN13+rename) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked until BD4 true-continue.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Scoreboard charter | 1 | BD FH0 · BA/BB/BC/AZ hold · live ask · ctx/speed · modes · DECODE law (BD1) |
| BD-FOREVER protocol | 12 | reverse≠f-string · mul≠add · wrong-bank + paraphrases (BD1) |
| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |
| BB hold protocol | 1 | min·xor·absdiff·and·or FH0 regression |
| BC hold protocol | 1 | floordiv·neg·gcd·lshift·rshift·nand FH0 regression |
| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |
| Ctx/speed baselines | 1 | BC FASTLIFT p50/p99 · CTXLIFT2 content (BD2/BD3) |
| Gen stance | 1 | **defer** · CAPCHECK closed · H-NANOGEN14 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER cited (BD4) |
| True gen judge | 1 | span-fallback ≠ gen · rename forbidden (BD4) |
| Real-eval protocol | 1 | live ask · eval=prod · OK|FP|MISS|ABSTAIN-OK (BD5) |
| Ask battery | 14 | frozen live rows (scored at BD5) |

## Cited BC locks

BC-FREEZE, BC-REAL-EVAL, H-CTXLIFT2, H-FASTLIFT, H-NANOGEN13, H-OPSFAM

## Scoreboard bars

- bd_forever_false_hit_max: **0**  
- ba_forever_false_hit_max: **0**  
- bb_forever_false_hit_max: **0**  
- bc_forever_false_hit_max: **0**  
- az_hold_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- bd_forever_min_n: **12**  
- bd_forever_classes_min: **3**  
- decode_gibberish_neq_content_ok: **True**  
- default_ask_intent_mismatch: **ABSTAIN**  
- default_ask_exact_gold: **LOOKUP**  
- eval_eq_prod_ask: **True**  
- pack_pass_neq_forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- l_eff_alone_forbidden: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no vanity reopen OPSFAM/FASTLIFT/CTXLIFT2 unless SEMINT fails

## Post-BC debts (frozen)

| id | bar |
|----|-----|
| bd_forever_false_hit_zero | bd_forever_false_hit_max=0 |
| ba_forever_hold_zero | ba_forever_false_hit_max=0 |
| bb_forever_hold_zero | bb_forever_false_hit_max=0 |
| bc_forever_hold_zero | bc_forever_false_hit_max=0 |
| az_hold_zero | az_hold_false_hit_max=0; overrefuse_miss_max=0 |
| overrefuse_exact_gold | overrefuse_miss_max=0 |
| live_ask_scoreboard | live_ask_scored True |
| speed_baseline_publish | speed_baseline_published True |
| ctx_baseline_publish | ctx_baseline_published True |
| mode_ui_always | modes_visible 4/4 |
| decode_content_law | decode_gibberish_neq_content_ok True |
| gen_defer_stance | gen_stance=defer; nanogen14_rename_forbidden |
| paraphrase_eval_rule | paraphrase_required True; bank_stuff_forbidden |

## BD-FOREVER protocol

- held_out: **True**  
- forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- neq_bc_forever: **True**  
- live_fp_id: **BD-FH-01**  
- min_n: **12**  
- path: `nano:z:ask --wrap --semwrap`  

| id | class | expect_mode |
|----|-------|-------------|
| BD-FH-01 | semantic_reverse | ABSTAIN |
| BD-FH-02 | semantic_reverse | ABSTAIN |
| BD-FH-03 | semantic_reverse | ABSTAIN |
| BD-FH-04 | semantic_reverse | ABSTAIN |
| BD-FH-05 | semantic_mul | ABSTAIN |
| BD-FH-06 | semantic_mul | ABSTAIN |
| BD-FH-07 | semantic_mul | ABSTAIN |
| BD-FH-08 | semantic_mul | ABSTAIN |
| BD-FH-09 | wrong_bank_neighbor | ABSTAIN |
| BD-FH-10 | wrong_bank_neighbor | ABSTAIN |
| BD-FH-11 | wrong_bank_neighbor | ABSTAIN |
| BD-FH-12 | semantic_mul | ABSTAIN |

## BA hold protocol

- forever_false_hit_max: **0**  
- heldout_n: **15**  
- regression_hold: **True**  

## BB hold protocol

- forever_false_hit_max: **0**  
- heldout_n: **15**  
- regression_hold: **True**  

## BC hold protocol

- forever_false_hit_max: **0**  
- heldout_n: **18**  
- regression_hold: **True**  

## AZ hold protocol

- heldout_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- heldout_n: **12**  
- overrefuse_n: **3**  
- regression_hold: **True**  

## Speed baseline (from BC FASTLIFT)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.009197996405418962** | **0.04120658952160745** |
| DECODE | **10.685407502023736** | **11.968237772889552** |
| ABSTAIN | **92.71498299858649** | **130.66686314792605** |

- quality_regress_forbidden: **True**  
- bd2_gate: `speed PROMOTE only if §1 anti-FP bars hold (incl BD-FOREVER)`

## Context baseline

- l_eff_alone_insufficient: **True**  
- content_bars_required: **True**  
- bd3_gate: `H-CTXGAIN PROMOTE only if content_ok + no new intent FP (incl BD-FOREVER) + p50/p99 published + modes visible`

## Gen stance (frozen)

- stance: **defer**  
- allowed: M1 · M2 · M3 · defer  
- named_hyp: **H-NANOGEN14**  
- named_semint: **H-SEMINT**  
- named_fast: **H-FASTGAIN**  
- named_ctx: **H-CTXGAIN**  
- capcheck: **closed**  
- nanogen14_rename_forbidden: **True**  
- bd4_gate: `true_continue → PROMOTE else HOLD/DEFER`  

No real new train/data/arch method ready at BD0; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER stand; CAPCHECK stays closed; prefer semantic intent/SEMWRAP gate (H-SEMINT) + ctx/speed hold + honest paper over vanity NANOGEN14 clone; BD4 PROMOTE only under true_continue else HOLD/DEFER

## True gen judge

- span_fallback_neq_gen: True  
- nanogen14_rename_forbidden: True  
- scoring: `short_answer_f1_or_hitl_true_continue_only`  
- promote_bar: `true_continue else HOLD/DEFER`

## Real-eval protocol

- live_ask_battery: True  
- eval_eq_prod_ask: True  
- score_labels: OK · FP · MISS · ABSTAIN-OK  
- pack_pass_neq_forever: True  
- gen_claim_rule: only if BD4 H-NANOGEN14 PROMOTE (true_continue; real new method M1|M2|M3; never NANOGEN13+rename; span-fallback ≠ gen)  
- mini_agi_rule: forbidden while gen stance defer or NANOGEN14 HOLD/DEFER

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| BD-ASK-01 | known_lookup | LOOKUP |
| BD-ASK-02 | ood_abstain | ABSTAIN |
| BD-ASK-03 | near_miss | ABSTAIN |
| BD-ASK-04 | labeled_peak | PEAK |
| BD-ASK-05 | decode_content | DECODE |
| BD-ASK-06 | junk_trap | ABSTAIN |
| BD-ASK-07 | bd_forever_reverse_fp | ABSTAIN |
| BD-ASK-08 | overrefuse_gold | LOOKUP |
| BD-ASK-09 | az_hold_div | ABSTAIN |
| BD-ASK-10 | ba_forever_hold | ABSTAIN |
| BD-ASK-11 | bb_forever_hold | ABSTAIN |
| BD-ASK-12 | bc_forever_hold | ABSTAIN |
| BD-ASK-13 | bd_forever_mul_fp | ABSTAIN |
| BD-ASK-14 | bd_forever_neighbor_fp | ABSTAIN |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; semantic wrong-bank LOOKUP = false-hit (reverse→f-string · mul→add); BA+BB+BC forever PASS with BD-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; semantic wrong-bank LOOKUP = false-hit (BD-FOREVER reverse→f-string / mul→add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB+BC PASS with BD FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BD4 only under real new method; no NANOGEN14 = NANOGEN13+rename; no CTX/SMART/FAST clone; no invent Wave BE without lab-book reopen; prefer HOLD/defer over fake PROMOTE

## North star

Nano generative / mini-AGI-inspired ≤5M: semantic/wrong-bank anti-FP (BD-FOREVER FH 0 + BA/BB/BC forever hold + AZ hold + novel probes) + measurable context & speed on prod path + one honest generative method (M1|M2|M3) — else HOLD/DEFER; never pack theater · never LOOKUP-as-IQ · never NANOGEN14 = NANOGEN13+rename

## Ship lock (until BD gen PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

## Validate

```bash
npm run nano:bd:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; BD-FOREVER + BA/BB/BC/AZ hold probes are **recorded** (BD1 scores forever FH=0 / holds=0).  
Artifacts (gitignored): `results/nano-lm/wave-bd/bd0_session.json` · `results/nano-lm/wave-bd/trials/BD-*.json`.  
Contract: `nano_lm/tests/test_bd_session.py`.

## Claims

- BC packs frozen for Wave BD — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**.  
- Generative PROMOTE only via later **BD4 H-NANOGEN14** true_continue under a real new method (M1|M2|M3; never NANOGEN13+rename; span-fallback ≠ gen).  
- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · over-refuse as win · peak-as-open-chat · SAFE-as-quality · L_eff as sole ctx win · warm-cache as sole speed win · gold-substring PROMOTE · span-fallback as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · NANOGEN14 rename · CTX/SMART/FAST clone · bank stuffing · vanity reopen.

Next: **BD1 H-SEMINT** — drive forever FH → 0 via semantic intent/SEMWRAP gate; hold BA/BB/BC/AZ bars; live ask scoreboard OK|FP|MISS|ABSTAIN-OK.
