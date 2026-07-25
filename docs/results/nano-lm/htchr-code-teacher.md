# H-TCHR smoke — tiny code teacher wire (prog@128)

Wave X dual-teacher wire: score H-EARLY completions on **prog@128** with frozen TinyStories story teacher **and** a named tiny code LM. Teachers are never silently swapped. Kill if code_teacher_lp is non-finite or story_lp collapses below floor. Not a code-IQ claim (that is H-CKD).
Mode: `TCHR: code_teacher_lp on EARLY prog@128 (dual vs story)`; pack=`{'name': 'prog', 'n_prompts': 4, 'target_tokens': 128, 'source': '/home/iiii/PESSOAL-PROJETOS-ALEXANDRE/ai-conceitual-teste/nano_lm/prompts/prog_prompts.yaml'}`; max_new=`32`; cpu_threads=`14`.

## Teachers

| role | hf_id | params | license |
|------|-------|--------|---------|
| story | `roneneldan/TinyStories-33M` | 33M | TinyStories |
| code | `bigcode/tiny_starcoder_py` | 164000000 | BigCode OpenRAIL-M v1 |

**Decision: PROMOTE (code teacher wired; code_teacher_lp stable on prog@128; story floor held)**

## Dual metrics (EARLY on prog@128)

| family | mean story_teacher_lp | mean code_teacher_lp | mean wall_ms | n_code_finite | n |
|--------|-----------------------|----------------------|--------------|---------------|---|
| H-EARLY | -10.1603 | -16.2692 | 22 | 12 | 12 |

Tips unchanged. Wave X code-teacher wire.

Commands: `npm run nano:tchr` → `npm run nano:tchr:report`.
