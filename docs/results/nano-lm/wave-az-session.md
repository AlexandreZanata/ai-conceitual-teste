# Wave AZ0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-az/SESSION.md`  
> Module: `nano_lm/src/az_session_ops.py` · Runner: `npm run nano:az:session`  
> Parent: [ay-freeze.md](ay-freeze.md) (Wave AZ reopened explicitly via lab-book reopen after AY-FREEZE)

## Decision

**PROMOTE** — Freeze AZ packs: held-out intent FP (N≥12 · div·sub·wrong-slot ≠ AY named) · over-refuse gold (`a.clear()` LOOKUP) · H-PRODGEN metrics charter · gen stance **defer** (CAPCHECK closed; **H-NANOGEN10**; **not** NANOGEN10=NANOGEN9+rename) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  
Anti-FP signed. Generative claim locked until AZ3 true-continue.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Product-gen charter | 1 | held-out FH0 · no over-refuse · AY hold · modes · KB · latency · DECODE law (AZ1) |
| Held-out FP protocol | 12 | div·sub·wrong-slot ≠ AY named (AZ1) |
| Over-refuse protocol | 3 | exact clear gold → LOOKUP (AZ1) |
| Gen stance | 1 | **defer** · CAPCHECK closed · H-NANOGEN10 named · NANOGEN6·7 HOLD · NANOGEN8·9 DEFER cited (AZ3) |
| True gen judge | 1 | span-fallback ≠ gen · rename forbidden (AZ3) |
| Real-eval protocol | 1 | live ask · eval=prod · anti-FP (AZ4) |
| Ask battery | 9 | frozen live rows (scored at AZ4) |

## Cited AY locks

AY-FREEZE, AY-REAL-EVAL, H-NANOGEN9, H-PRODINT, H-SHIPAY

## Product-gen bars

- heldout_false_hit_max: **0**  
- overrefuse_miss_max: **0**  
- named_intent_false_hit_max: **0**  
- hard_natural_para_hit_min: **0.7**  
- false_hit_max: **0**  
- heldout_fp_min_n: **12**  
- heldout_fp_classes_min: **3**  
- overrefuse_min_n: **3**  
- decode_gibberish_neq_content_ok: **True**  
- default_ask_intent_mismatch: **ABSTAIN**  
- default_ask_exact_gold: **LOOKUP**  
- eval_eq_prod_ask: **True**  
- named_fh_neq_heldout: **True**  
- bank_stuff_forbidden: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no vanity reopen PRODINT/SHIPAY unless PRODGEN fails

## Post-AY debts (frozen)

| id | bar |
|----|-----|
| heldout_false_hit_zero | heldout_false_hit_max=0 |
| overrefuse_exact_gold | overrefuse_miss_max=0 |
| ay_named_intent_hold | named_intent_false_hit_max=0 hold |
| hard_natural_hold | hard_natural_para_hit_min hold |
| false_hit_zero | false_hit_max=0 |
| latency_publish | latency_publish True |
| kb_holes_publish | kb_holes_publish True |
| mode_ui_always | modes_visible 4/4 |
| decode_content_law | decode_gibberish_neq_content_ok True |
| gen_defer_stance | gen_stance=defer; nanogen10_rename_forbidden |

## Held-out FP protocol

- held_out: **True**  
- bank_stuff_forbidden: **True**  
- neq_ay_named_intent: **True**  
- intent_mismatch_is_false_hit: **True**  
- wrong_slot_is_false_hit: **True**  
- live_fp_id: **AZ-HFP-01**  
- min_n: **12**  
- path: `nano:z:ask --wrap --semwrap`  

| id | class | expect_mode |
|----|-------|-------------|
| AZ-HFP-01 | ops_div | ABSTAIN |
| AZ-HFP-02 | ops_div | ABSTAIN |
| AZ-HFP-03 | ops_div | ABSTAIN |
| AZ-HFP-04 | ops_div | ABSTAIN |
| AZ-HFP-05 | ops_sub | ABSTAIN |
| AZ-HFP-06 | ops_sub | ABSTAIN |
| AZ-HFP-07 | ops_sub | ABSTAIN |
| AZ-HFP-08 | ops_sub | ABSTAIN |
| AZ-HFP-09 | wrong_slot | ABSTAIN |
| AZ-HFP-10 | wrong_slot | ABSTAIN |
| AZ-HFP-11 | wrong_slot | ABSTAIN |
| AZ-HFP-12 | wrong_slot | ABSTAIN |

## Over-refuse protocol

- exact_gold_must_lookup: **True**  
- overrefuse_is_miss: **True**  
- live_orf_id: **AZ-ORF-01**  
- min_n: **3**  

| id | class | expect_mode | gold |
|----|-------|-------------|------|
| AZ-ORF-01 | exact_clear | LOOKUP | `a.clear()` |
| AZ-ORF-02 | exact_clear | LOOKUP | `a.clear()` |
| AZ-ORF-03 | exact_clear | LOOKUP | `a.clear()` |

## Gen stance (frozen)

- stance: **defer**  
- named_hyp: **H-NANOGEN10**  
- named_prod: **H-PRODGEN**  
- named_ship: **H-SHIPAZ**  
- capcheck: **closed**  
- nanogen10_rename_forbidden: **True**  
- az3_gate: `true_continue → PROMOTE else HOLD/DEFER`  

No real new train/data/arch method ready at AZ0; NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand; CAPCHECK stays closed; prefer product ship (held-out FH 0 + no over-refuse) + honest paper over vanity NANOGEN10 clone; AZ3 PROMOTE only under true_continue else HOLD/DEFER

## True gen judge

- span_fallback_neq_gen: True  
- nanogen10_rename_forbidden: True  
- scoring: `short_answer_f1_or_hitl_true_continue_only`  
- promote_bar: `true_continue else HOLD/DEFER`

## Real-eval protocol

- live_ask_battery: True  
- eval_eq_prod_ask: True  
- intent_mismatch_is_false_hit: True  
- exact_gold_abstain_is_miss: True  
- named_fh_neq_heldout: True  
- gen_claim_rule: only if AZ3 H-NANOGEN10 PROMOTE (true_continue; real new method; never NANOGEN9+rename; span-fallback ≠ gen)  
- mini_agi_rule: forbidden while gen stance defer or NANOGEN10 HOLD/DEFER

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| AZ-ASK-01 | known_lookup | LOOKUP |
| AZ-ASK-02 | ood_abstain | ABSTAIN |
| AZ-ASK-03 | near_miss | ABSTAIN |
| AZ-ASK-04 | labeled_peak | PEAK |
| AZ-ASK-05 | decode_content | DECODE |
| AZ-ASK-06 | junk_trap | ABSTAIN |
| AZ-ASK-07 | heldout_intent_fp | ABSTAIN |
| AZ-ASK-08 | overrefuse_gold | LOOKUP |
| AZ-ASK-09 | ay_named_hold | ABSTAIN |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); named-class FH 0 ≠ held-out generalization; intent-mismatch LOOKUP = false-hit; exact-gold ABSTAIN = product miss; gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; intent-mismatch LOOKUP = false-hit (div/sub/wrong-slot held-out); exact-gold ABSTAIN = miss (a.clear()); truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; pack/named FH 0 ≠ held-out coverage; generative bar = AZ3 only under real new method; no NANOGEN10 = NANOGEN9+rename; no CTX/SMART/FAST clone; no invent Wave BA without lab-book reopen; prefer HOLD/defer over fake PROMOTE

## North star

Nano generative / mini-AGI-inspired ≤5M: ship/harden Caminho A (held-out FH 0 + no over-refuse + hold AY/AX + SHIPAZ); true continue only after a real new method beats NANOGEN6·7 HOLD · NANOGEN8·9 DEFER — else HOLD/defer; never NANOGEN10 = NANOGEN9+rename

## Ship lock (until AZ gen PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

## Validate

```bash
npm run nano:az:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; held-out FP + over-refuse probes are **recorded** (AZ1 scores FH=0 / miss=0).  
Artifacts (gitignored): `results/nano-lm/wave-az/az0_session.json` · `results/nano-lm/wave-az/trials/AZ-*.json`.  
Contract: `nano_lm/tests/test_az_session.py`.

## Claims

- AY packs frozen for Wave AZ — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked**.  
- Generative PROMOTE only via later **AZ3 H-NANOGEN10** true_continue under a real new method (never NANOGEN9+rename; span-fallback ≠ gen).  
- Forbidden: LOOKUP-as-IQ · held-out FP as hit · over-refuse as win · peak-as-open-chat · SAFE-as-quality · named FH as held-out coverage · gold-substring PROMOTE · span-fallback as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · NANOGEN10 rename · CTX/SMART/FAST/APP clone · bank stuffing · vanity reopen.

Next: **AZ1 H-PRODGEN** — close held-out FH + over-refuse on Caminho A; publish human-para · FH · p50/p99 · KB · modes.
