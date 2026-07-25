# Formal H-QT — int8 weight-only PACK/EARLY serve

Source: `results/nano-lm/formal-hqt/formal.json`
Wall clock: 10.7s

Wave X quantized serve: replace student `nn.Linear` weights with **int8** + per-out-channel scale; dequant to activation dtype at decode (weights frozen otherwise). Parent = fp H-EARLY (PACK tip control) on prog@128. Gate: story_lp ≥ parent−ε and (wall↓ or weight_bytes↓).
Mode: `QT: int8 weight-only EARLY serve vs fp on prog@128 (PACK tip)`; mechanism=`int8 weight-only Linear (skip lm_head; dequant to act dtype)`; pack=`{'name': 'prog', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/prog_prompts.yaml'}`; max_new=`32`; cpu_threads=`14`.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (int8 weight-only serve; lp ≥ parent−ε; wall↓+mem↓)**

## Arms

| arm | mean story_teacher_lp | mean code_teacher_lp | mean wall_ms | weight_bytes | n |
|-----|-----------------------|----------------------|--------------|--------------|---|
| H-EARLY fp | -10.3233 | -14.1457 | 24 | 13920008 | 12 |
| H-QT int8 | -10.3233 | -14.1457 | 12 | 13629704 | 12 |

Tips unchanged. Wave X quantized PACK serve.

Commands: `npm run nano:formal:hqt` → `npm run nano:formal:hqt:report`.
