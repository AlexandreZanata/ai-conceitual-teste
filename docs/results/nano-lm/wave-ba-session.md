# Wave BA0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8 · Session: `.local/wave-ba/SESSION.md`  
> Module: `nano_lm/src/ba_session_ops.py` · Runner: `npm run nano:ba:session`  
> Parent: [az-freeze.md](az-freeze.md) (Wave BA reopened explicitly via lab-book reopen after AZ-FREEZE)

## Decision

**PROMOTE** — Freeze BA packs: BA-FOREVER (N≥15 · pow·mod·max·sort·len + paraphrases ≠ AZ) · AZ hold (div·sub·BIP FH0 · `a.clear()` LOOKUP) · §1 anti-FP scoreboard · ctx/speed baselines from AZ · gen stance **defer** (CAPCHECK closed; **H-NANOGEN11**; M1|M2|M3 named; **not** NANOGEN11=NANOGEN10+rename) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked until BA4 true-continue.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Scoreboard charter | 1 | forever FH0 · AZ hold · live ask · ctx/speed · modes · DECODE law (BA1) |
| BA-FOREVER protocol | 15 | pow·mod·max·sort·len + paraphrases (BA1) |
| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |
| Ctx/speed baselines | 1 | AZ PRODGEN p50/p99 · content bars (BA2/BA3) |
| Gen stance | 1 | **defer** · CAPCHECK closed · H-NANOGEN11 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER cited (BA4) |
| True gen judge | 1 | span-fallback ≠ gen · rename forbidden (BA4) |
| Real-eval protocol | 1 | live ask · eval=prod · OK|FP|MISS|ABSTAIN-OK (BA5) |
| Ask battery | 10 | frozen live rows (scored at BA5) |

## Cited AZ locks

AZ-FREEZE, AZ-REAL-EVAL, H-NANOGEN10, H-PRODGEN, H-SHIPAZ

## Scoreboard bars

- forever_false_hit_max: **0**  
- az_hold_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- forever_min_n: **15**  
- forever_classes_min: **5**  
- decode_gibberish_neq_content_ok: **True**  
- default_ask_intent_mismatch: **ABSTAIN**  
- default_ask_exact_gold: **LOOKUP**  
- eval_eq_prod_ask: **True**  
- pack_pass_neq_forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- l_eff_alone_forbidden: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no vanity reopen PRODGEN/SHIPAZ unless REALGAIN fails

## Post-AZ debts (frozen)

| id | bar |
|----|-----|
| forever_false_hit_zero | forever_false_hit_max=0 |
| az_hold_zero | az_hold_false_hit_max=0; overrefuse_miss_max=0 |
| overrefuse_exact_gold | overrefuse_miss_max=0 |
| live_ask_scoreboard | live_ask_scored True |
| speed_baseline_publish | speed_baseline_published True |
| ctx_baseline_publish | ctx_baseline_published True |
| mode_ui_always | modes_visible 4/4 |
| decode_content_law | decode_gibberish_neq_content_ok True |
| gen_defer_stance | gen_stance=defer; nanogen11_rename_forbidden |
| paraphrase_eval_rule | paraphrase_required True; bank_stuff_forbidden |

## BA-FOREVER protocol

- held_out: **True**  
- forever: **True**  
- bank_stuff_forbidden: **True**  
- paraphrase_required: **True**  
- neq_az_heldout: **True**  
- live_fp_id: **BA-FH-01**  
- min_n: **15**  
- path: `nano:z:ask --wrap --semwrap`  

| id | class | expect_mode |
|----|-------|-------------|
| BA-FH-01 | ops_pow | ABSTAIN |
| BA-FH-02 | ops_pow | ABSTAIN |
| BA-FH-03 | ops_pow | ABSTAIN |
| BA-FH-04 | ops_mod | ABSTAIN |
| BA-FH-05 | ops_mod | ABSTAIN |
| BA-FH-06 | ops_mod | ABSTAIN |
| BA-FH-07 | ops_max | ABSTAIN |
| BA-FH-08 | ops_max | ABSTAIN |
| BA-FH-09 | ops_max | ABSTAIN |
| BA-FH-10 | list_sort | ABSTAIN |
| BA-FH-11 | list_sort | ABSTAIN |
| BA-FH-12 | list_sort | ABSTAIN |
| BA-FH-13 | list_len | ABSTAIN |
| BA-FH-14 | list_len | ABSTAIN |
| BA-FH-15 | list_len | ABSTAIN |

## AZ hold protocol

- heldout_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- heldout_n: **12**  
- overrefuse_n: **3**  
- regression_hold: **True**  

## Speed baseline (from AZ PRODGEN)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.02575** | **0.04586** |
| DECODE | **11.37002** | **13.25987** |
| ABSTAIN | **95.44715** | **119.44308** |

- quality_regress_forbidden: **True**  
- ba2_gate: `speed PROMOTE only if §1 anti-FP bars hold`

## Context baseline

- l_eff_alone_insufficient: **True**  
- content_bars_required: **True**  
- ba3_gate: `H-CTXREAL2 PROMOTE only if content_ok + no new intent FP + p50/p99 published + modes visible`

## Gen stance (frozen)

- stance: **defer**  
- allowed: M1 · M2 · M3 · defer  
- named_hyp: **H-NANOGEN11**  
- named_realgain: **H-REALGAIN**  
- named_fast: **H-FASTREAL**  
- named_ctx: **H-CTXREAL2**  
- capcheck: **closed**  
- nanogen11_rename_forbidden: **True**  
- ba4_gate: `true_continue → PROMOTE else HOLD/DEFER`  

No real new train/data/arch method ready at BA0; NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand; CAPCHECK stays closed; prefer forever anti-FP (H-REALGAIN) + ctx/speed measure + honest paper over vanity NANOGEN11 clone; BA4 PROMOTE only under true_continue else HOLD/DEFER

## True gen judge

- span_fallback_neq_gen: True  
- nanogen11_rename_forbidden: True  
- scoring: `short_answer_f1_or_hitl_true_continue_only`  
- promote_bar: `true_continue else HOLD/DEFER`

## Real-eval protocol

- live_ask_battery: True  
- eval_eq_prod_ask: True  
- score_labels: OK · FP · MISS · ABSTAIN-OK  
- pack_pass_neq_forever: True  
- gen_claim_rule: only if BA4 H-NANOGEN11 PROMOTE (true_continue; real new method M1|M2|M3; never NANOGEN10+rename; span-fallback ≠ gen)  
- mini_agi_rule: forbidden while gen stance defer or NANOGEN11 HOLD/DEFER

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| BA-ASK-01 | known_lookup | LOOKUP |
| BA-ASK-02 | ood_abstain | ABSTAIN |
| BA-ASK-03 | near_miss | ABSTAIN |
| BA-ASK-04 | labeled_peak | PEAK |
| BA-ASK-05 | decode_content | DECODE |
| BA-ASK-06 | junk_trap | ABSTAIN |
| BA-ASK-07 | forever_intent_fp | ABSTAIN |
| BA-ASK-08 | overrefuse_gold | LOOKUP |
| BA-ASK-09 | az_hold_div | ABSTAIN |
| BA-ASK-10 | forever_list_fp | ABSTAIN |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ forever held-out generalization; intent-mismatch LOOKUP = false-hit (pow/mod/max/sort/len); exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (BA-FOREVER pow/mod/max/sort/len); exact-gold ABSTAIN = miss (a.clear()); AZ hold div·sub·BIP FH must stay 0; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack PASS with forever FP = PACK THEATER; generative bar = BA4 only under real new method; no NANOGEN11 = NANOGEN10+rename; no CTX/SMART/FAST clone; no invent Wave BB without lab-book reopen; prefer HOLD/defer over fake PROMOTE

## North star

Nano generative / mini-AGI-inspired ≤5M: real intelligence scoreboard (BA-FOREVER FH 0 + AZ hold + live ask) + measurable context & speed on prod path + one honest generative method (M1|M2|M3) — else HOLD/DEFER; never pack theater · never LOOKUP-as-IQ · never NANOGEN11 = NANOGEN10+rename

## Ship lock (until BA gen PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

## Validate

```bash
npm run nano:ba:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; BA-FOREVER + AZ hold probes are **recorded** (BA1 scores forever FH=0 / AZ hold=0).  
Artifacts (gitignored): `results/nano-lm/wave-ba/ba0_session.json` · `results/nano-lm/wave-ba/trials/BA-*.json`.  
Contract: `nano_lm/tests/test_ba_session.py`.

## Claims

- AZ packs frozen for Wave BA — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**.  
- Generative PROMOTE only via later **BA4 H-NANOGEN11** true_continue under a real new method (M1|M2|M3; never NANOGEN10+rename; span-fallback ≠ gen).  
- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · over-refuse as win · peak-as-open-chat · SAFE-as-quality · L_eff as sole ctx win · warm-cache as sole speed win · gold-substring PROMOTE · span-fallback as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · NANOGEN11 rename · CTX/SMART/FAST clone · bank stuffing · vanity reopen.

Next: **BA1 H-REALGAIN** — drive forever FH → 0 via gate; hold AZ bars; live ask scoreboard OK|FP|MISS|ABSTAIN-OK.
