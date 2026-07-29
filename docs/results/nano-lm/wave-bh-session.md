# Wave BH0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 · Session: `.local/wave-bh/SESSION.md`  
> Module: `nano_lm/src/bh_session_ops.py` · Runner: `npm run nano:bh:session`  
> Parent: [bg-freeze.md](bg-freeze.md) (Wave BH reopened explicitly via lab-book reopen after BG-FREEZE)

## Decision

**PROMOTE** — Freeze BH packs: IQ battery v0 plan (schema · mix ≥40 · Novel_FP=0 · gold MISS=0) · gold holes (Rust MISS · add truncation) · BA…BG-FOREVER hold · AZ hold · Track A++ utilization · §1 anti-FP scoreboard · ctx/speed baselines from BG · gen stance **SKIP** (CAPCHECK closed; **H-NANOGEN18**; M1|M2|M3 named; **not** NANOGEN18 without method plan) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked (BH6 SKIP without method plan).

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Scoreboard charter | 1 | IQ · gold MISS · BA…BG/AZ hold · live ask · ctx/speed · util · modes |
| IQ battery plan | seed 13 / target ≥40 | schema + mix + Novel_FP=0 (BH1) |
| Gold holes | 2 | Rust LOOKUP · full add body (BH2) |
| BA…BF hold protocols | 6 | forever FH0 regression |
| BG hold protocol | 1 | abs·factorial·upper·all FH0 |
| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |
| Track A++ utilization | 1 | demo · recipes · paper + IQ cite (BH3) |
| Ctx/speed baselines | 1 | BG FASTBG p50/p99 · CTXBG content (BH4/BH5) |
| Gen stance | 1 | **SKIP** · CAPCHECK closed · H-NANOGEN18 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16·17 SKIP cited (BH6) |
| True gen judge | 1 | span-fallback ≠ gen · rename forbidden (BH6) |
| Real-eval protocol | 1 | IQ + live ask · eval=prod · OK|FP|MISS|ABSTAIN-OK (BH7) |
| Ask battery | 19 | frozen live rows (scored at BH7) |

## Cited BG locks

BG-FREEZE, BG-REAL-EVAL, H-CTXBG, H-FASTBG, H-NANOGEN17, H-SHIPPUB, H-UNARYINT

## Scoreboard bars

- iq_battery_min_n: **40**  
- novel_fp_max: **0**  
- gold_miss_max: **0**  
- gold_rust_miss_max: **0**  
- gold_add_truncation_miss_max: **0**  
- ba…bg forever false_hit_max: **0**  
- az_hold_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- truncated_gold_is_miss: **True**  
- pack_pass_neq_iq: **True**  
- iq_battery_plan_frozen: **True**  
- gold_holes_frozen: **True**  
- utilization_track_frozen: **True**  
- decode_gibberish_neq_content_ok: **True**  
- eval_eq_prod_ask: **True**  
- bank_stuff_forbidden: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  

## Post-BG debts (frozen)

| id | bar |
|----|-----|
| iq_battery_v0 | iq_battery_min_n≥40; Novel_FP=0 |
| rust_gold_miss | gold_rust_miss_max=0 |
| add_truncation_miss | gold_add_truncation_miss_max=0 |
| ba_forever_hold_zero | ba_forever_false_hit_max=0 |
| bb_forever_hold_zero | bb_forever_false_hit_max=0 |
| bc_forever_hold_zero | bc_forever_false_hit_max=0 |
| bd_forever_hold_zero | bd_forever_false_hit_max=0 |
| be_forever_hold_zero | be_forever_false_hit_max=0 |
| bf_forever_hold_zero | bf_forever_false_hit_max=0 |
| bg_forever_hold_zero | bg_forever_false_hit_max=0 |
| az_hold_zero | az_hold_false_hit_max=0; overrefuse_miss_max=0 |
| live_ask_scoreboard | live_ask_scored True |
| speed_baseline_publish | speed_baseline_published True |
| ctx_baseline_publish | ctx_baseline_published True |
| mode_ui_always | modes_visible 4/4 |
| decode_content_law | decode_gibberish_neq_content_ok True |
| gen_skip_stance | gen_stance=skip; nanogen18_without_plan_forbidden |
| utilization_track_a_plus_plus | utilization_track_frozen True |

## IQ battery protocol

- version: **v0**  
- artifact: `docs/results/nano-lm/iq-battery-v0.jsonl`  
- runner: `npm run nano:iq-battery`  
- mix total ≥ **40** (gold≥8 · para≥8 · adversary≥10 · novel≥10 · ood≥4 · gen≥3)  
- promote: Novel_FP=0 · gold MISS=0 · Forever FH=0  
- bh1_gate: `≥40 probes · Novel_FP=0 baseline · runner published`

| id | split | expect |
|----|-------|--------|
| IQ-2026-07-29-001 | gold | LOOKUP |
| IQ-2026-07-29-002 | gold | LOOKUP |
| IQ-2026-07-29-003 | gold | LOOKUP |
| IQ-2026-07-29-004 | gold | LOOKUP |
| IQ-2026-07-29-005 | forever | ABSTAIN |
| IQ-2026-07-29-006 | forever | ABSTAIN |
| IQ-2026-07-29-007 | forever | ABSTAIN |
| IQ-2026-07-29-008 | adversary | ABSTAIN |
| IQ-2026-07-29-009 | adversary | ABSTAIN |
| IQ-2026-07-29-010 | novel | ABSTAIN |
| IQ-2026-07-29-011 | novel | ABSTAIN |
| IQ-2026-07-29-012 | ood | ABSTAIN |
| IQ-2026-07-29-013 | gen | ABSTAIN |

## Gold holes

| id | family | expect | live_mode |
|----|--------|--------|-----------|
| BH-GOLD-01 | rust_gold | LOOKUP | ABSTAIN |
| BH-GOLD-02 | binary_add | LOOKUP | LOOKUP |

- bh2_gate: `H-GOLDFIX: Rust LOOKUP + full add body; BA…BG FH=0; Novel_FP=0`

## BA / BB / BC / BD / BE / BF / BG / AZ hold

- BA heldout_n: **15**  
- BB heldout_n: **15**  
- BC heldout_n: **18**  
- BD heldout_n: **12**  
- BE heldout_n: **12**  
- BF heldout_n: **12**  
- BG heldout_n: **12**  
- AZ heldout_n: **12** · overrefuse_n: **3**  

## Track A++ utilization

- gpt_claim_forbidden: **True**  
- iq_battery_cited_in_paper: **True**  
- bh3_gate: `Track A++ done before utilization PROMOTE (H-SHIPIQ)`

| # | checklist |
|--:|-----------|
| 1 | demo smoke: npm run nano:z:ask -- --wrap --semwrap |
| 2 | RECIPES + champion-card operator sync |
| 3 | paper:build claim = selective retriever + refuse ≤5M + IQ battery |
| 4 | modes always LOOKUP|PEAK|DECODE|ABSTAIN |
| 5 | H-SHIPPUB hold; deepen utilization + paper surface to IQ claim |

## Speed baseline (from BG FASTBG)

| Path | p50 wall_ms | p99 wall_ms |
|------|------------:|------------:|
| LOOKUP | **0.0** | **0.0** |
| PEAK | **0.020638000023609493** | **0.028944830004320465** |
| DECODE | **10.507157999995798** | **10.882093060029092** |
| ABSTAIN | **87.36960300001329** | **110.29079292000351** |

- quality_regress_forbidden: **True**  
- bh4_gate: `speed PROMOTE only if IQ anti-FP bars hold (Novel_FP=0 · gold MISS=0 · BA…BG FH=0)`

## Context baseline

- l_eff_alone_insufficient: **True**  
- content_bars_required: **True**  
- bh5_gate: `H-CTXBH PROMOTE only if content_ok + IQ anti-FP hold (Novel_FP=0 · gold MISS=0) + p50/p99 published + modes visible`

## Gen stance (frozen)

- stance: **skip** (SKIP)  
- allowed: M1 · M2 · M3 · skip  
- named_hyp: **H-NANOGEN18**  
- named_iqbat: **H-IQBAT**  
- named_goldfix: **H-GOLDFIX**  
- named_shipiq: **H-SHIPIQ**  
- named_fast: **H-FASTBH**  
- named_ctx: **H-CTXBH**  
- capcheck: **closed**  
- nanogen18_rename_forbidden: **True**  
- bh6_gate: `SKIP stage (no written M1|M2|M3 plan at BH0)`  

No written M1|M2|M3 method plan at BH0; H-NANOGEN17 already SKIP — stop rule forbids empty NANOGEN18 letter; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16·17 SKIP stand; CAPCHECK stays closed; prefer IQ battery (H-IQBAT) + gold repair (H-GOLDFIX) + Track A++ publish (H-SHIPIQ) over vanity NANOGEN18 rename; BH6 = SKIP stage

## True gen judge

- span_fallback_neq_gen: True  
- nanogen18_rename_forbidden: True  
- scoring: `short_answer_f1_or_hitl_true_continue_only`  
- promote_bar: `true_continue else SKIP (no empty DEFER letter)`

## Real-eval protocol

- iq_battery_required: True  
- live_ask_battery: True  
- eval_eq_prod_ask: True  
- read_completion_text: True  
- truncated_gold_is_miss: True  
- score_labels: OK · FP · MISS · ABSTAIN-OK  
- pack_pass_neq_iq: True  
- gen_claim_rule: only if BH6 H-NANOGEN18 PROMOTE (true_continue; written M1|M2|M3 plan; never NANOGEN17+rename; span-fallback ≠ gen) — else SKIP gen claim  
- mini_agi_rule: forbidden while gen stance skip or NANOGEN18 SKIP/HOLD/DEFER

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| BH-ASK-01 | known_lookup_add | LOOKUP |
| BH-ASK-02 | gold_rust_miss | LOOKUP |
| BH-ASK-03 | ood_abstain | ABSTAIN |
| BH-ASK-04 | near_miss | ABSTAIN |
| BH-ASK-05 | labeled_peak | PEAK |
| BH-ASK-06 | decode_content | DECODE |
| BH-ASK-07 | junk_trap | ABSTAIN |
| BH-ASK-08 | bg_forever_hold | ABSTAIN |
| BH-ASK-09 | bg_forever_transform | ABSTAIN |
| BH-ASK-10 | overrefuse_gold | LOOKUP |
| BH-ASK-11 | az_hold_div | ABSTAIN |
| BH-ASK-12 | ba_forever_hold | ABSTAIN |
| BH-ASK-13 | bb_forever_hold | ABSTAIN |
| BH-ASK-14 | bc_forever_hold | ABSTAIN |
| BH-ASK-15 | bd_forever_hold | ABSTAIN |
| BH-ASK-16 | be_forever_hold | ABSTAIN |
| BH-ASK-17 | bf_forever_hold | ABSTAIN |
| BH-ASK-18 | utilization_smoke | LOOKUP |
| BH-ASK-19 | novel_cube | ABSTAIN |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); pack FH 0 ≠ IQ battery intelligence; truncated gold LOOKUP (def add without body) = PRODUCT MISS; exact-gold Rust ABSTAIN = PRODUCT MISS; BA…BG forever PASS without IQ novel = PACK THEATER; over-refuse sold as safe = FALSE TRUST; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncated gold = MISS (add body required); Rust exact-gold ABSTAIN = MISS; unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); BA…BG forever FH must stay 0; AZ hold must stay 0; BA…BG PASS without IQ novel = PACK THEATER; Novel_FP>0 → no intelligence PROMOTE; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; read completion text; generative bar = BH6 only under written method plan; no NANOGEN18 without M1|M2|M3 plan; no CTX/SMART/FAST clone; no invent Wave BI without lab-book reopen; prefer IQ battery growth + class gates over bank stuffing; prefer HOLD/SKIP over fake PROMOTE

## North star

Nano generative / mini-AGI-inspired ≤5M: versioned IQ battery (gold/para/forever/adversary/novel/ood/gen) + gold repair (Rust MISS · add truncation) + ship/utilize/publish AF+AQ+AS stack + measurable context & speed + one honest generative method (M1|M2|M3) — else SKIP gen; never pack theater · never LOOKUP-as-IQ · never NANOGEN18 without method plan

## Ship lock (until BH gen PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

## Validate

```bash
npm run nano:bh:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Ask-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; gold holes (Rust ABSTAIN · add truncation) are **recorded** (BH2 scores MISS=0); BA…BG/AZ hold probes are **recorded**.  
Artifacts (gitignored): `results/nano-lm/wave-bh/bh0_session.json` · `results/nano-lm/wave-bh/trials/BH-*.json`.  
Contract: `nano_lm/tests/test_bh_session.py`.

## Claims

- BG packs frozen for Wave BH — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**.  
- Generative PROMOTE only via later **BH6 H-NANOGEN18** true_continue under a real new method (M1|M2|M3; written M1|M2|M3 plan — else SKIP stop rule).  
- Forbidden: LOOKUP-as-IQ · pack theater · truncated gold as OK · over-refuse as win · peak-as-open-chat · SAFE-as-quality · L_eff as sole ctx win · warm-cache as sole speed win · gold-substring PROMOTE · span-fallback as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · NANOGEN18 without plan · CTX/SMART/FAST clone · bank stuffing · vanity reopen · invent Wave BI.

Next: **BH1 H-IQBAT** — materialize iq-battery-v0.jsonl (≥40 probes) + `npm run nano:iq-battery`; publish scoreboard; Novel_FP=0 baseline; no pack theater.
