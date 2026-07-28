# Wave BB0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8 · Session: `.local/wave-bb/SESSION.md`  
> Module: `nano_lm/src/bb_session_ops.py` · Runner: `npm run nano:bb:session`  
> Parent: [ba-freeze.md](ba-freeze.md) (Wave BB reopened explicitly via lab-book reopen after BA-FREEZE)

## Decision

**PROMOTE** — Freeze BB packs: BB-FOREVER (N≥15 · min·xor·absdiff·and·or + paraphrases ≠ BA/AZ) · BA-FOREVER hold (pow·mod·max·sort·len FH0) · AZ hold (div·sub·BIP FH0 · `a.clear()` LOOKUP) · §1 anti-FP scoreboard · ctx/speed baselines from BA · gen stance **defer** (CAPCHECK closed; **H-NANOGEN12**; M1|M2|M3 named; **not** NANOGEN12=NANOGEN11+rename) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked until BB4 true-continue.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Scoreboard charter | 1 | BB FH0 · BA/AZ hold · live ask · ctx/speed · modes · DECODE law (BB1) |
| BB-FOREVER protocol | 15 | min·xor·absdiff·and·or + paraphrases (BB1) |
| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |
| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |
| Ctx/speed baselines | 1 | BA FASTREAL p50/p99 · CTXREAL2 content (BB2/BB3) |
| Gen stance | 1 | **defer** · CAPCHECK closed · H-NANOGEN12 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER cited (BB4) |
| True gen judge | 1 | span-fallback ≠ gen · rename forbidden (BB4) |
| Real-eval protocol | 1 | live ask · eval=prod · OK|FP|MISS|ABSTAIN-OK (BB5) |
| Ask battery | 12 | frozen live rows (scored at BB5) |

## Cited BA locks

BA-FREEZE, BA-REAL-EVAL, H-CTXREAL2, H-FASTREAL, H-NANOGEN11, H-REALGAIN

## Scoreboard bars

- bb_forever_false_hit_max: **0**  
- ba_forever_false_hit_max: **0**  
- az_hold_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- bb_forever_min_n: **15**  
- bb_forever_classes_min: **5**  
- decode_gibberish_neq_content_ok: **True**  
- default_ask_intent_mismatch: **ABSTAIN**  
- default_ask_exact_gold: **LOOKUP**  
- eval_eq_prod_ask: **True**  
- pack_pass_neq_forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- l_eff_alone_forbidden: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no vanity reopen REALGAIN/FASTREAL/CTXREAL2 unless INTENTGEN fails

## Post-BA debts (frozen)

| id | bar |
|----|-----|
| bb_forever_false_hit_zero | bb_forever_false_hit_max=0 |
| ba_forever_hold_zero | ba_forever_false_hit_max=0 |
| az_hold_zero | az_hold_false_hit_max=0; overrefuse_miss_max=0 |
| overrefuse_exact_gold | overrefuse_miss_max=0 |
| live_ask_scoreboard | live_ask_scored True |
| speed_baseline_publish | speed_baseline_published True |
| ctx_baseline_publish | ctx_baseline_published True |
| mode_ui_always | modes_visible 4/4 |
| decode_content_law | decode_gibberish_neq_content_ok True |
| gen_defer_stance | gen_stance=defer; nanogen12_rename_forbidden |
| paraphrase_eval_rule | paraphrase_required True; bank_stuff_forbidden |

## BB-FOREVER protocol

- held_out: **True**  
- forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- neq_az_heldout: **True**  
- live_fp_id: **BB-FH-01**  
- min_n: **15**  
- path: `nano:z:ask --wrap --semwrap`  

| id | class | expect_mode |
|----|-------|-------------|
| BB-FH-01 | ops_min | ABSTAIN |
| BB-FH-02 | ops_min | ABSTAIN |
| BB-FH-03 | ops_min | ABSTAIN |
| BB-FH-04 | ops_xor | ABSTAIN |
| BB-FH-05 | ops_xor | ABSTAIN |
| BB-FH-06 | ops_xor | ABSTAIN |
| BB-FH-07 | ops_absdiff | ABSTAIN |
| BB-FH-08 | ops_absdiff | ABSTAIN |
| BB-FH-09 | ops_absdiff | ABSTAIN |
| BB-FH-10 | ops_and | ABSTAIN |
| BB-FH-11 | ops_and | ABSTAIN |
| BB-FH-12 | ops_and | ABSTAIN |
| BB-FH-13 | ops_or | ABSTAIN |
| BB-FH-14 | ops_or | ABSTAIN |
| BB-FH-15 | ops_or | ABSTAIN |

## BA hold protocol

- forever_false_hit_max: **0**  
- heldout_n: **15**  
- regression_hold: **True**  

## AZ hold protocol

- heldout_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- heldout_n: **12**  
- overrefuse_n: **3**  
- regression_hold: **True**  

## Speed baseline (from BA FASTREAL)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.00948000160860829** | **0.016213351700571366** |
| DECODE | **12.682843498623697** | **17.01244352661888** |
| ABSTAIN | **95.4394950022106** | **125.30305242056787** |

- quality_regress_forbidden: **True**  
- bb2_gate: `speed PROMOTE only if §1 anti-FP bars hold (incl BB-FOREVER)`

## Context baseline

- l_eff_alone_insufficient: **True**  
- content_bars_required: **True**  
- bb3_gate: `H-CTXHOLD PROMOTE only if content_ok + no new intent FP (incl BB-FOREVER) + p50/p99 published + modes visible`

## Gen stance (frozen)

- stance: **defer**  
- allowed: M1 · M2 · M3 · defer  
- named_hyp: **H-NANOGEN12**  
- named_intentgen: **H-INTENTGEN**  
- named_fast: **H-FASTHOLD**  
- named_ctx: **H-CTXHOLD**  
- capcheck: **closed**  
- nanogen12_rename_forbidden: **True**  
- bb4_gate: `true_continue → PROMOTE else HOLD/DEFER`  

No real new train/data/arch method ready at BB0; NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER stand; CAPCHECK stays closed; prefer compositional anti-FP (H-INTENTGEN) + ctx/speed hold + honest paper over vanity NANOGEN12 clone; BB4 PROMOTE only under true_continue else HOLD/DEFER

## True gen judge

- span_fallback_neq_gen: True  
- nanogen12_rename_forbidden: True  
- scoring: `short_answer_f1_or_hitl_true_continue_only`  
- promote_bar: `true_continue else HOLD/DEFER`

## Real-eval protocol

- live_ask_battery: True  
- eval_eq_prod_ask: True  
- score_labels: OK · FP · MISS · ABSTAIN-OK  
- pack_pass_neq_forever: True  
- gen_claim_rule: only if BB4 H-NANOGEN12 PROMOTE (true_continue; real new method M1|M2|M3; never NANOGEN11+rename; span-fallback ≠ gen)  
- mini_agi_rule: forbidden while gen stance defer or NANOGEN12 HOLD/DEFER

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| BB-ASK-01 | known_lookup | LOOKUP |
| BB-ASK-02 | ood_abstain | ABSTAIN |
| BB-ASK-03 | near_miss | ABSTAIN |
| BB-ASK-04 | labeled_peak | PEAK |
| BB-ASK-05 | decode_content | DECODE |
| BB-ASK-06 | junk_trap | ABSTAIN |
| BB-ASK-07 | bb_forever_intent_fp | ABSTAIN |
| BB-ASK-08 | overrefuse_gold | LOOKUP |
| BB-ASK-09 | az_hold_div | ABSTAIN |
| BB-ASK-10 | ba_forever_hold | ABSTAIN |
| BB-ASK-11 | bb_forever_xor_fp | ABSTAIN |
| BB-ASK-12 | bb_forever_absdiff_fp | ABSTAIN |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (min/xor/absdiff/and/or); BA-FOREVER PASS with BB-FOREVER FP = PACK THEATER; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BB-FOREVER min/xor/absdiff/and/or → add); exact-gold ABSTAIN = miss (a.clear()); BA-FOREVER pow·mod·max·sort·len FH must stay 0; AZ hold div·sub·BIP FH must stay 0; BA PASS with BB FP = PACK THEATER; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = BB4 only under real new method; no NANOGEN12 = NANOGEN11+rename; no CTX/SMART/FAST clone; no invent Wave BC without lab-book reopen; prefer HOLD/defer over fake PROMOTE

## North star

Nano generative / mini-AGI-inspired ≤5M: compositional anti-FP (BB-FOREVER FH 0 + BA-FOREVER hold + AZ hold + live ask) + measurable context & speed on prod path + one honest generative method (M1|M2|M3) — else HOLD/DEFER; never pack theater · never LOOKUP-as-IQ · never NANOGEN12 = NANOGEN11+rename

## Ship lock (until BA gen PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

## Validate

```bash
npm run nano:bb:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; BB-FOREVER + AZ hold probes are **recorded** (BB1 scores forever FH=0 / AZ hold=0).  
Artifacts (gitignored): `results/nano-lm/wave-bb/bb0_session.json` · `results/nano-lm/wave-bb/trials/BA-*.json`.  
Contract: `nano_lm/tests/test_bb_session.py`.

## Claims

- BA packs frozen for Wave BB — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**.  
- Generative PROMOTE only via later **BB4 H-NANOGEN12** true_continue under a real new method (M1|M2|M3; never NANOGEN11+rename; span-fallback ≠ gen).  
- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · over-refuse as win · peak-as-open-chat · SAFE-as-quality · L_eff as sole ctx win · warm-cache as sole speed win · gold-substring PROMOTE · span-fallback as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · NANOGEN12 rename · CTX/SMART/FAST clone · bank stuffing · vanity reopen.

Next: **BB1 H-INTENTGEN** — drive forever FH → 0 via gate; hold AZ bars; live ask scoreboard OK|FP|MISS|ABSTAIN-OK.
