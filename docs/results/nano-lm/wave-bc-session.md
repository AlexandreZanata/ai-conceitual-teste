# Wave BC0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8 · Session: `.local/wave-bc/SESSION.md`  
> Module: `nano_lm/src/bc_session_ops.py` · Runner: `npm run nano:bc:session`  
> Parent: [bb-freeze.md](bb-freeze.md) (Wave BC reopened explicitly via lab-book reopen after BB-FREEZE)

## Decision

**PROMOTE** — Freeze BC packs: BC-FOREVER (N≥18 · floordiv·neg·gcd·lshift·rshift·nand + paraphrases ≠ BA/BB/AZ) · BA-FOREVER hold · BB-FOREVER hold · AZ hold (div·sub·BIP FH0 · `a.clear()` LOOKUP) · §1 anti-FP scoreboard · ctx/speed baselines from BB · gen stance **defer** (CAPCHECK closed; **H-NANOGEN13**; M1|M2|M3 named; **not** NANOGEN13=NANOGEN12+rename) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked until BC4 true-continue.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Scoreboard charter | 1 | BC FH0 · BA/BB/AZ hold · live ask · ctx/speed · modes · DECODE law (BC1) |
| BC-FOREVER protocol | 18 | floordiv·neg·gcd·lshift·rshift·nand + paraphrases (BC1) |
| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |
| BB hold protocol | 1 | min·xor·absdiff·and·or FH0 regression |
| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |
| Ctx/speed baselines | 1 | BB FASTHOLD p50/p99 · CTXHOLD content (BC2/BC3) |
| Gen stance | 1 | **defer** · CAPCHECK closed · H-NANOGEN13 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER cited (BC4) |
| True gen judge | 1 | span-fallback ≠ gen · rename forbidden (BC4) |
| Real-eval protocol | 1 | live ask · eval=prod · OK|FP|MISS|ABSTAIN-OK (BC5) |
| Ask battery | 13 | frozen live rows (scored at BC5) |

## Cited BB locks

BB-FREEZE, BB-REAL-EVAL, H-CTXHOLD, H-FASTHOLD, H-INTENTGEN, H-NANOGEN12

## Scoreboard bars

- bc_forever_false_hit_max: **0**  
- ba_forever_false_hit_max: **0**  
- bb_forever_false_hit_max: **0**  
- az_hold_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- bc_forever_min_n: **18**  
- bc_forever_classes_min: **6**  
- decode_gibberish_neq_content_ok: **True**  
- default_ask_intent_mismatch: **ABSTAIN**  
- default_ask_exact_gold: **LOOKUP**  
- eval_eq_prod_ask: **True**  
- pack_pass_neq_forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- l_eff_alone_forbidden: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no vanity reopen INTENTGEN/FASTHOLD/CTXHOLD unless OPSFAM fails

## Post-BB debts (frozen)

| id | bar |
|----|-----|
| bc_forever_false_hit_zero | bc_forever_false_hit_max=0 |
| ba_forever_hold_zero | ba_forever_false_hit_max=0 |
| bb_forever_hold_zero | bb_forever_false_hit_max=0 |
| az_hold_zero | az_hold_false_hit_max=0; overrefuse_miss_max=0 |
| overrefuse_exact_gold | overrefuse_miss_max=0 |
| live_ask_scoreboard | live_ask_scored True |
| speed_baseline_publish | speed_baseline_published True |
| ctx_baseline_publish | ctx_baseline_published True |
| mode_ui_always | modes_visible 4/4 |
| decode_content_law | decode_gibberish_neq_content_ok True |
| gen_defer_stance | gen_stance=defer; nanogen13_rename_forbidden |
| paraphrase_eval_rule | paraphrase_required True; bank_stuff_forbidden |

## BC-FOREVER protocol

- held_out: **True**  
- forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- neq_az_heldout: **True**  
- live_fp_id: **BC-FH-01**  
- min_n: **18**  
- path: `nano:z:ask --wrap --semwrap`  

| id | class | expect_mode |
|----|-------|-------------|
| BC-FH-01 | ops_floordiv | ABSTAIN |
| BC-FH-02 | ops_floordiv | ABSTAIN |
| BC-FH-03 | ops_floordiv | ABSTAIN |
| BC-FH-04 | ops_neg | ABSTAIN |
| BC-FH-05 | ops_neg | ABSTAIN |
| BC-FH-06 | ops_neg | ABSTAIN |
| BC-FH-07 | ops_gcd | ABSTAIN |
| BC-FH-08 | ops_gcd | ABSTAIN |
| BC-FH-09 | ops_gcd | ABSTAIN |
| BC-FH-10 | ops_lshift | ABSTAIN |
| BC-FH-11 | ops_lshift | ABSTAIN |
| BC-FH-12 | ops_lshift | ABSTAIN |
| BC-FH-13 | ops_rshift | ABSTAIN |
| BC-FH-14 | ops_rshift | ABSTAIN |
| BC-FH-15 | ops_rshift | ABSTAIN |
| BC-FH-16 | ops_nand | ABSTAIN |
| BC-FH-17 | ops_nand | ABSTAIN |
| BC-FH-18 | ops_nand | ABSTAIN |

## BA hold protocol

- forever_false_hit_max: **0**  
- heldout_n: **15**  
- regression_hold: **True**  

## BB hold protocol

- forever_false_hit_max: **0**  
- heldout_n: **15**  
- regression_hold: **True**  

## AZ hold protocol

- heldout_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- heldout_n: **12**  
- overrefuse_n: **3**  
- regression_hold: **True**  

## Speed baseline (from BB FASTHOLD)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.00948000160860829** | **0.016213351700571366** |
| DECODE | **12.682843498623697** | **17.01244352661888** |
| ABSTAIN | **95.4394950022106** | **125.30305242056787** |

- quality_regress_forbidden: **True**  
- bc2_gate: `speed PROMOTE only if §1 anti-FP bars hold (incl BC-FOREVER)`

## Context baseline

- l_eff_alone_insufficient: **True**  
- content_bars_required: **True**  
- bc3_gate: `H-CTXLIFT2 PROMOTE only if content_ok + no new intent FP (incl BC-FOREVER) + p50/p99 published + modes visible`

## Gen stance (frozen)

- stance: **defer**  
- allowed: M1 · M2 · M3 · defer  
- named_hyp: **H-NANOGEN13**  
- named_opsfam: **H-OPSFAM**  
- named_fast: **H-FASTLIFT**  
- named_ctx: **H-CTXLIFT2**  
- capcheck: **closed**  
- nanogen13_rename_forbidden: **True**  
- bc4_gate: `true_continue → PROMOTE else HOLD/DEFER`  

No real new train/data/arch method ready at BC0; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand; CAPCHECK stays closed; prefer family ops/intent gate (H-OPSFAM) + ctx/speed hold + honest paper over vanity NANOGEN13 clone; BC4 PROMOTE only under true_continue else HOLD/DEFER

## True gen judge

- span_fallback_neq_gen: True  
- nanogen13_rename_forbidden: True  
- scoring: `short_answer_f1_or_hitl_true_continue_only`  
- promote_bar: `true_continue else HOLD/DEFER`

## Real-eval protocol

- live_ask_battery: True  
- eval_eq_prod_ask: True  
- score_labels: OK · FP · MISS · ABSTAIN-OK  
- pack_pass_neq_forever: True  
- gen_claim_rule: only if BC4 H-NANOGEN13 PROMOTE (true_continue; real new method M1|M2|M3; never NANOGEN12+rename; span-fallback ≠ gen)  
- mini_agi_rule: forbidden while gen stance defer or NANOGEN13 HOLD/DEFER

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| BC-ASK-01 | known_lookup | LOOKUP |
| BC-ASK-02 | ood_abstain | ABSTAIN |
| BC-ASK-03 | near_miss | ABSTAIN |
| BC-ASK-04 | labeled_peak | PEAK |
| BC-ASK-05 | decode_content | DECODE |
| BC-ASK-06 | junk_trap | ABSTAIN |
| BC-ASK-07 | bc_forever_intent_fp | ABSTAIN |
| BC-ASK-08 | overrefuse_gold | LOOKUP |
| BC-ASK-09 | az_hold_div | ABSTAIN |
| BC-ASK-10 | ba_forever_hold | ABSTAIN |
| BC-ASK-11 | bb_forever_hold | ABSTAIN |
| BC-ASK-12 | bc_forever_gcd_fp | ABSTAIN |
| BC-ASK-13 | bc_forever_shift_fp | ABSTAIN |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (floordiv/neg/gcd/lshift/rshift/nand); BA+BB forever PASS with BC-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BC-FOREVER floordiv/neg/gcd/lshift/rshift/nand → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; BB-FOREVER min·xor·absdiff·and·or FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA+BB PASS with BC FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BC4 only under real new method; no NANOGEN13 = NANOGEN12+rename; no CTX/SMART/FAST clone; no invent Wave BD without lab-book reopen; prefer HOLD/defer over fake PROMOTE

## North star

Nano generative / mini-AGI-inspired ≤5M: family-level anti-FP (BC-FOREVER FH 0 + BA/BB forever hold + AZ hold + novel probes) + measurable context & speed on prod path + one honest generative method (M1|M2|M3) — else HOLD/DEFER; never pack theater · never LOOKUP-as-IQ · never NANOGEN13 = NANOGEN12+rename

## Ship lock (until BC gen PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

## Validate

```bash
npm run nano:bc:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; BC-FOREVER + AZ hold probes are **recorded** (BC1 scores forever FH=0 / AZ hold=0).  
Artifacts (gitignored): `results/nano-lm/wave-bc/bc0_session.json` · `results/nano-lm/wave-bc/trials/BC-*.json`.  
Contract: `nano_lm/tests/test_bc_session.py`.

## Claims

- BB packs frozen for Wave BC — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**.  
- Generative PROMOTE only via later **BC4 H-NANOGEN13** true_continue under a real new method (M1|M2|M3; never NANOGEN12+rename; span-fallback ≠ gen).  
- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · over-refuse as win · peak-as-open-chat · SAFE-as-quality · L_eff as sole ctx win · warm-cache as sole speed win · gold-substring PROMOTE · span-fallback as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · NANOGEN13 rename · CTX/SMART/FAST clone · bank stuffing · vanity reopen.

Next: **BC1 H-OPSFAM** — drive forever FH → 0 via gate; hold BA/BB/AZ bars; live ask scoreboard OK|FP|MISS|ABSTAIN-OK.
