# Formal H-ABS-BPFB — PFB K=2 on BTC; wall↓ vs k=4

Decision: **PROMOTE (ABS-BPFB k=2 unique≈2.00 elig≈0.92 switch≈0.50; code↑ story≥parent−ε; wall↓ vs BPFB k=4)**

Parent: `H-EARLY n=1 greedy on B2 (BTC pack, formal genes)` · k2=2 · k4=4 · temp=0.8 · pack=`{'name': 'btc', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/btc_prompts.yaml'}` · mechanism: `PFB commit K=2 on bitcoin pack; domain-transfer gate`

| arm | mean story_lp | mean code_lp | mean wall_ms | mean unique | mean n_elig | mean switch | n |
|-----|---------------|--------------|--------------|-------------|-------------|--------------|---|
| H-EARLY-BTC n=1 | -13.4571 | -13.9197 | 24 | 1.000 | 1.00 | 0.00 | 12 |
| H-ABS-BPFB k=4 | -11.7812 | -10.0009 | 69 | 4.000 | 2.08 | 0.58 | 12 |
| H-ABS-BPFB k=2 | -12.4097 | -11.1616 | 53 | 2.000 | 0.92 | 0.50 | 12 |

Tips unchanged. Wave X ABS-BPFB (PFB2→BTC domain transfer).

Reproduce:
`npm run nano:bpfb` → `npm run nano:bpfb:report`

Next formal:
`npm run nano:formal:hbpfb` → `npm run nano:formal:hbpfb:report`
