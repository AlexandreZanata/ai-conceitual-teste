# H-MIXD smoke — STAG + curated programming mix

Wave W knowledge-in-training: TinyStories **STAG** curriculum + **mix_frac=0.1** curated programming tokens (PSF / Rust book licenses). Teacher remains TinyStories. Hold-out: curated source ids ∩ prog eval prompt ids = ∅. PROMOTE iff story teacher_lp ≥ control−ε **and** prog PPL ↓.
Mode: `MIXD smoke: live STAG curriculum + curated prog mix_frac vs story-only; TinyStories teacher; prog PPL on hold-out YAML`; steps=`30`; cpu_threads=`14`; licenses=`['PSF', 'CC-BY-SA / MIT Apache-2.0']`.

**Decision: PROMOTE (story ≥ STAG−ε and prog PPL ↓ vs story-only; mix_frac=0.1)**

## Means

| arm | mean story teacher_lp | mean prog PPL |
|-----|----------------------|---------------|
| H-STAG-CTRL | -17.0327 | 34143.300 |
| H-MIXD | -16.8221 | 31988.407 |

Commands: tooling purged after KILL (`nano:mixd*` removed). Report retained for evidence.
