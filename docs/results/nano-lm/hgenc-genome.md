# H-GENC smoke — genetic context/serve genome under BUD

Wave X genetics (narrow): evolve `{k_retrieve, chunk_len, stride, quant_bits, exit_depth}` (pop≤6, gens=2, fit≠eval) under BUD wall ceiling. Parent = PACK/EARLY default genome on prog@128. Gate: story+code ≥ parent−ε, wall≤BUD parent, and (code↑ or wall↓). Not tip-compose; retrieve gene ≠ RAG PROMOTE claim.
Mode: `GENC: evolve context/serve knobs vs PACK/EARLY parent on prog@128`; mechanism=`genetic serve genome {k_retrieve,chunk_len,stride,quant_bits,exit_depth} under BUD; fit≠eval; Pareto vs PACK/EARLY`; pack=`{'name': 'prog', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/prog_prompts.yaml'}`; max_new=`32`; n_chunks=`256`; cpu_threads=`14`.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (GENC under BUD; code↑+wall↓)**

Best gene (seed0): `{"chunk_len": 32, "exit_depth": 1, "k_retrieve": 1, "quant_bits": 16, "stride": 32}`

## Arms (eval holdout)

| arm | mean story_teacher_lp | mean code_teacher_lp | mean wall_ms | weight_bytes | n |
|-----|-----------------------|----------------------|--------------|--------------|---|
| PACK/EARLY parent | -15.5667 | -16.8288 | 7 | 13920008 | 6 |
| H-GENC best | -13.8025 | -16.1764 | 5 | 13920008 | 6 |

Tips unchanged. Wave X GENC (context/serve genome).

Commands: `npm run nano:genc` → `npm run nano:genc:report`.
