# Wave AQ0 — SESSION freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §5 · Session: `.local/wave-aq/SESSION.md`  
> Module: `nano_lm/src/aq_session_ops.py` · Runner: `npm run nano:aq:session`  
> Parent: [ap-freeze.md](ap-freeze.md) (Wave AQ reopened explicitly via lab-book reopen 2026-07-27)

## Decision

**PROMOTE** — Freeze product-science eval packs (paraphrase-20 · adversary-20 · latency triad · KB coverage · mode charter). **Not** a CTX/SMART/FAST/APP clone.  
Packs are **disjoint** from AP-HITL verbatim question text.

## Mix

| Pack | N | Purpose |
|------|--:|---------|
| paraphrase-20 | 20 | human rewrites of known golds (AQ1) |
| adversary-20 | 20 | near-miss · OOD · trap (AQ2) |
| latency triad | 3 paths | LOOKUP · PEAK · DECODE p50/p99 (AQ3) |
| KB coverage | snapshot | % + explicit holes (AQ4) |
| mode charter | 3 | UI must show LOOKUP\|PEAK\|DECODE (AQ5) |

## Paraphrase-20 (ids)

| id | source_id |
|----|-----------|
| AQ-PARA-01 | python-tutorial-intro |
| AQ-PARA-02 | prog:g01 |
| AQ-PARA-03 | python-tutorial-control |
| AQ-PARA-04 | rust-book-ch03 |
| AQ-PARA-05 | bip-0001 |
| AQ-PARA-06 | bip-0032 |
| AQ-PARA-07 | bip-0141 |
| AQ-PARA-08 | python-tutorial-classes |
| AQ-PARA-09 | bip-0039 |
| AQ-PARA-10 | bip-0340 |
| AQ-PARA-11 | python-tutorial-datastructures |
| AQ-PARA-12 | python-tutorial-io |
| AQ-PARA-13 | rust-book-ch03-02 |
| AQ-PARA-14 | rust-book-ch04-01 |
| AQ-PARA-15 | rust-book-ch05-01 |
| AQ-PARA-16 | bitcoin-json-rpc |
| AQ-PARA-17 | bitcoin-rest |
| AQ-PARA-18 | bitcoin-doc-bips |
| AQ-PARA-19 | bip-0039 |
| AQ-PARA-20 | rfc791 |

## Adversary-20 (ids)

| id | kind | source_id |
|----|------|-----------|
| AQ-ADV-01 | near-miss | bip-0039 |
| AQ-ADV-02 | near-miss | bip-0032 |
| AQ-ADV-03 | near-miss | bip-0141 |
| AQ-ADV-04 | near-miss | python-tutorial-datastructures |
| AQ-ADV-05 | near-miss | python-tutorial-control |
| AQ-ADV-06 | near-miss | rust-book-ch03-02 |
| AQ-ADV-07 | near-miss | bip-0340 |
| AQ-ADV-08 | near-miss | bitcoin-rest |
| AQ-ADV-09 | ood | ood:sports |
| AQ-ADV-10 | ood | ood:cooking |
| AQ-ADV-11 | ood | ood:finance |
| AQ-ADV-12 | ood | ood:medicine |
| AQ-ADV-13 | ood | ood:history |
| AQ-ADV-14 | ood | ood:math |
| AQ-ADV-15 | trap | trap:lookup-as-iq |
| AQ-ADV-16 | trap | trap:peak-as-agi |
| AQ-ADV-17 | trap | trap:bank-key |
| AQ-ADV-18 | trap | trap:period |
| AQ-ADV-19 | trap | trap:empty |
| AQ-ADV-20 | trap | trap:wrong-gold |

## Latency triad protocol

| Path | Rule |
|------|------|
| LOOKUP | `wall_ms` may be 0 |
| PEAK | `wall_ms` > 0 when claiming gen work; labeled extractive |
| DECODE | `wall_ms` > 0 and `n_new` > 0 |

Publish p50/p99 in **AQ3 H-LATP**; no silent regress vs FASTBASE hot.

## Mode charter (anti-FP)

Every ASK / demo / HITL trial MUST log exactly one of `LOOKUP` · `PEAK` · `DECODE` (aliases mapped in ops).

## KB coverage snapshot

- curated covered: **22** / **22** (100.0%)  
- complete product KB claim: **forbidden**  
- holes:
- open-world chat / unbounded general knowledge
- languages beyond Python + Rust (bank scope)
- BIPs / RFCs not present in curated+bank golds
- math proofs and multi-step symbolic reasoning
- live web retrieval / tool-use agency
- unlabeled PEAK sold as DECODE IQ (anti-FP)

## Validate

```bash
npm run nano:aq:session
# optional: --skip-ask
npm run nano:test && npm run verify
```

Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE (`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  
Artifacts (gitignored): `results/nano-lm/wave-aq/aq0_session.json` · `results/nano-lm/wave-aq/trials/AQ-*.json`.  
Contract: `nano_lm/tests/test_aq_session.py`.

## Claims

- Product-science packs frozen for Wave AQ — **not** open chat LM.  
- Ship claim until generative gate clears: **AF packaged stack + AQ product layer**.  
- Generative PROMOTE only via later **AQ6 H-NANOGEN** ablated bar.  
- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · Wave AR invent · CTX/SMART/FAST/APP clone without named product hole.

Next: **AQ1 H-PARAHIT** — **DONE PROMOTE** → [formal-hparahit-parahit.md](formal-hparahit-parahit.md). **AQ2 H-ADVFP** — **DONE PROMOTE** → [formal-hadvfp-advfp.md](formal-hadvfp-advfp.md). **AQ3 H-LATP** — **DONE PROMOTE** → [formal-hlatp-latp.md](formal-hlatp-latp.md). **AQ4 H-KBCOV** — **DONE PROMOTE** → [formal-hkbcov-kbcov.md](formal-hkbcov-kbcov.md). **AQ5 H-MODEUI** — **DONE PROMOTE** → [formal-hmodeui-modeui.md](formal-hmodeui-modeui.md). Next: **AQ6 H-NANOGEN**.
