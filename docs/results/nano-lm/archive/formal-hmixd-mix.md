# Formal H-MIXD — STAG + curated programming mix

Source: `results/nano-lm/formal-hmixd/formal.json`
Wall clock: 198.0s

Wave W knowledge-in-training: TinyStories **STAG** curriculum + **mix_frac=0.1** curated programming tokens (PSF / Rust book licenses). Teacher remains TinyStories. Hold-out: curated source ids ∩ prog eval prompt ids = ∅. PROMOTE iff story teacher_lp ≥ control−ε **and** prog PPL ↓.
Mode: `MIXD formal: live STAG curriculum + curated prog mix_frac vs story-only; TinyStories teacher; fit≠eval story prompts`; steps=`120`; cpu_threads=`14`; licenses=`['PSF', 'CC-BY-SA / MIT Apache-2.0']`.

**Decision: KILL (story teacher_lp regress vs STAG control: -13.6013 < -13.2775−0.05)**

## Means

| arm | mean story teacher_lp | mean prog PPL |
|-----|----------------------|---------------|
| H-STAG-CTRL | -13.2775 | 45927.336 |
| H-MIXD | -13.6013 | 14737.158 |

Commands: tooling purged after KILL (`nano:mixd*` / `nano:formal:hmixd*` removed). Report retained for evidence.
