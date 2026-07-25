# H-ABS-BPFB smoke — PFB K=2 on bitcoin pack; wall↓ vs k=4

Decision: **PROMOTE (ABS-BPFB k=2 unique≈2.00 elig≈1.08 switch≈0.58; code↑ story≥parent−ε; wall↓ vs BPFB k=4)**

Parent: `H-EARLY n=1 greedy on B2 (BTC pack)` · k2=2 · k4=4 · temp=0.8 · pack=`{'name': 'btc', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/btc_prompts.yaml'}` · mechanism: `PFB commit K=2 on bitcoin pack; domain-transfer gate`

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY-BTC n=1 | -16.2016 | -21.0271 | 22 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-BPFB k=4 | -15.4279 | -12.9656 | 77 | 4.000 | 1.67 | 0.58 | 12 |
| H-ABS-BPFB k=2 | -15.3830 | -12.9150 | 52 | 2.000 | 1.08 | 0.58 | 12 |

Tips unchanged. Wave X ABS-BPFB (PFB2→BTC domain transfer).

Reproduce:
`npm run nano:bpfb` → `npm run nano:bpfb:report`

Next formal:
`npm run nano:formal:hbpfb` → `npm run nano:formal:hbpfb:report`
