# Wave AV0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-av/SESSION.md`  
> Module: `nano_lm/src/av_session_ops.py` · Runner: `npm run nano:av:session`  
> Parent: [au-freeze.md](au-freeze.md) (Wave AV reopened explicitly via lab-book reopen)

## Decision

**PROMOTE** — Freeze AV packs: product-ship charter · external-para protocol (N≥20 ≠ AU) · NANOGEN6 hyp (true continue; **span-fallback ≠ gen IQ**) · real-eval protocol. **Not** a CTX/SMART/FAST/APP clone · **not** NANOGEN5+rename.  
Anti-FP signed. Generative claim locked until AV3 PROMOTE.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| Product-ship charter | 1 | DECODE content · external para · FH0 · modes · KB · latency (AV1) |
| External-para protocol | 20 | held-out ≠ AU · no bank stuffing (AV1) |
| NANOGEN6 hypothesis | 1 | refuse-or-continue · span-fallback = PEAK/LOOKUP credit only (AV3) |
| True gen judge | 1 | span-fallback ≠ gen · telemetry ≠ content_ok (AV3) |
| Real-eval protocol | 1 | live ask · eval=prod · anti-FP (AV4) |
| Ask battery | 8 | frozen live rows (scored at AV4) |

## Cited AU locks

AU-FREEZE, AU-REAL-EVAL, H-NANOGEN5, H-PRODHARD, H-SHIPREAL

## Product-ship bars

- para_hit_min: **0.7** (AU PRODHARD baseline 1.0)  
- false_hit_max: **0**  
- external_para_min_n: **20**  
- decode_gibberish_neq_content_ok: **True**  
- default_ask_near_miss: **ABSTAIN**  
- eval_eq_prod_ask: **True**  
- modes: LOOKUP · PEAK · DECODE · ABSTAIN  
- no re-SEMFIX/ADVSAFE unless PRODSHIP fails

## Post-AU debts (frozen)

| id | bar |
|----|-----|
| decode_content_ok | usable_or_abstain; gibberish≠content_ok |
| external_human_para | para_hit_min on external held-out set |
| false_hit_zero | false_hit_max=0 |
| mode_ui_always | modes_visible 4/4 |
| kb_holes_honest | kb_holes_publish; no overclaim |
| latency_publish | latency_publish True |

## External-para protocol

- held_out: **True**  
- bank_stuff_forbidden: **True**  
- neq_au_pack: **True**  
- min_n: **20**  
- path: `nano:z:ask --wrap --semwrap`  

| id | parent |
|----|--------|
| AV-PARA-01 | add |
| AV-PARA-02 | add |
| AV-PARA-03 | add |
| AV-PARA-04 | add |
| AV-PARA-05 | add |
| AV-PARA-06 | add |
| AV-PARA-07 | add |
| AV-PARA-08 | add |
| AV-PARA-09 | add |
| AV-PARA-10 | add |
| AV-PARA-11 | add |
| AV-PARA-12 | add |
| AV-PARA-13 | add |
| AV-PARA-14 | add |
| AV-PARA-15 | add |
| AV-PARA-16 | add |
| AV-PARA-17 | add |
| AV-PARA-18 | add |
| AV-PARA-19 | add |
| AV-PARA-20 | add |

## NANOGEN6 hypothesis (one idea)

One idea: refuse-or-continue DECODE with fallback labeling — score only novel readable continue tokens; truncate-to-retrieved-span must label PEAK/LOOKUP fallback (zero gen credit); gibberish → ABSTAIN; wall_ms/n_new ≠ content_ok; not a NANOGEN5 5.5 truncate-bar clone; bar = true_continue_ablated PROMOTE else HOLD

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
- gen_claim_rule: only if AV3 H-NANOGEN6 PROMOTE (true_continue_ablated; span-fallback ≠ gen credit)  
- mini_agi_rule: forbidden while NANOGEN6 HOLD

## Ask battery (ids)

| id | kind | expect_mode |
|----|------|-------------|
| AV-ASK-01 | known_lookup | LOOKUP |
| AV-ASK-02 | ood_abstain | ABSTAIN |
| AV-ASK-03 | near_miss | ABSTAIN |
| AV-ASK-04 | labeled_peak | PEAK |
| AV-ASK-05 | decode_content | DECODE |
| AV-ASK-06 | junk_trap | ABSTAIN |
| AV-ASK-07 | human_para | LOOKUP |
| AV-ASK-08 | decode_gibberish_bar | DECODE |

## SAFE ≠ quality

SAFE / ADVSAFE false-hit score ≠ answer quality; SAFE = no wrong gold only (anti-FP); gold-substring / gibberish-tail / truncate-to-span ≠ generative PROMOTE

## Anti-FP (signed)

LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; eval path = prod ask path; generative bar = AV3 only; no vanity re-SEMFIX/ADVSAFE unless PRODSHIP fails; no Wave AW invent; no CTX/SMART/FAST clone; no NANOGEN6 = NANOGEN5+rename

## North star

Nano generative / mini-AGI-inspired ≤5M: ship Caminho A (PRODSHIP + SHIPUI2) now; true ablated DECODE (H-NANOGEN6) without span-fallback-as-IQ before generative or mini-AGI claim

## Ship lock (until AV PROMOTE)

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM

## Validate

```bash
npm run nano:av:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`); near-miss maps to ABSTAIN alias.  
Artifacts (gitignored): `results/nano-lm/wave-av/av0_session.json` · `results/nano-lm/wave-av/trials/AV-*.json`.  
Contract: `nano_lm/tests/test_av_session.py`.

## Claims

- AV packs frozen for Wave AV — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM**.  
- Generative PROMOTE only via later **AV3 H-NANOGEN6** true_continue_ablated (span-fallback ≠ gen credit).  
- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · gold-substring PROMOTE · truncate-to-span as gen · DECODE telemetry-only content_ok · eval↔prod gap · mini-AGI claim early · Wave AW invent · CTX/SMART/FAST/APP clone · NANOGEN5+rename · bank stuffing · vanity re-SEMFIX.

Next: **AV1 H-PRODSHIP** — accept Caminho A; close DECODE content debt; publish external para · FH · p50/p99 · KB.
