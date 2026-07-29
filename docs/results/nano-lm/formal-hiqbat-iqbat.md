# H-IQBAT — IQ battery v0 live scoreboard (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §9 BH1 · Session: `.local/wave-bh/SESSION.md`  
> Parent: [wave-bh-session.md](wave-bh-session.md) · Battery: [`iq-battery-v0.jsonl`](iq-battery-v0.jsonl) (sha256 `7232462a9c7c0d0b`)  
> Module: `nano_lm/src/iqbat_ops.py` · Runner: `npm run nano:iq-battery`

## Hypothesis

Materialize IQ battery v0 (≥40 probes · gold/para/forever/adversary/novel/ood/gen) + live prod-path scorer (OK|FP|MISS|ABSTAIN-OK); Novel_FP=0 baseline; forever FH=0; gold MISS residual → BH2 H-GOLDFIX; not pack theater · not LOOKUP-as-IQ

## Gate

| Metric | Result | Bar |
|--------|-------:|-----|
| n probes | **50** | ≥40 |
| IQ | **0.880** | publish |
| Novel_FP | **0** | **0** |
| Forever_FH | **0** | **0** |
| adversary_FP | **0** | **0** |
| gold/para MISS | **6** | baseline (BH2 closes → 0) |
| FP_rate | **0.000** | novel/adversary 0 |
| Decision | **PROMOTE** | — |

## Mix

| Split | n |
|-------|--:|
| adversary | **10** |
| forever | **7** |
| gen | **3** |
| gold | **8** |
| novel | **10** |
| ood | **4** |
| para | **8** |

## Scores

| Label | n |
|-------|--:|
| ABSTAIN-OK | **34** |
| MISS | **6** |
| OK | **10** |

## Gold/para MISS residual (→ BH2 H-GOLDFIX)

| id | split | completion |
|----|-------|------------|
| IQ-2026-07-29-001 | gold | `def add` |
| IQ-2026-07-29-002 | gold | `NO_ANSWER` |
| IQ-2026-07-29-010 | para | `list.append — example: squares.append(x*` |
| IQ-2026-07-29-012 | para | `a.append(x)` |
| IQ-2026-07-29-013 | para | `def add` |
| IQ-2026-07-29-014 | para | `def add` |

## SAFE ≠ quality

SAFE ≠ IQ; pack FH 0 ≠ intelligence; truncated gold = MISS; exact-gold ABSTAIN = MISS; Novel_FP>0 = no IQ claim

## Anti-FP

eval=prod ask; read completion text; wrong LOOKUP = FP; truncated gold = MISS; Rust ABSTAIN = MISS; Novel_FP must be 0; forever FH must be 0; bank stuffing forbidden; pack PASS ≠ IQ

## Ship lock

AF packaged stack + AQ product layer + AS trust path + ablated DECODE (snippet-prefix + gibberish-tail STRICT) — not unlabeled open chat LM · not TAC unlocked

## Validate

```bash
npm run nano:iq-battery
npm run nano:test && npm run verify
```

Next: **BH2 H-GOLDFIX** — Rust LOOKUP + full add body; hold Novel_FP=0 · Forever_FH=0.
