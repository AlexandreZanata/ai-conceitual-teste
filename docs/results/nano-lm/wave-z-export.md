# Wave Z0 — champion export (**DONE**)

Freeze code-smart stack **H-ABS-QPFB2** as `champion-qpfb2-v0`:

| Field | Value |
|-------|--------|
| recipe_id | `champion-qpfb2-v0` |
| family | H-ABS-QPFB2 |
| seed | 0 |
| qt_bits | 8 |
| pfb_k | 2 (never K=2 pathology / GPFB-K=2) |
| ckpt source | `results/nano-lm/formal-hdeck-b4/B2_seed0.pt` |
| gene source | `results/nano-lm/formal-hearly/HEARLY_seed0_train.json` |
| out | `results/nano-lm/wave-z/models/champion/` |

Ask path for HITL smoke: **QT + EARLY n=1** (no teacher self-grade). Full PFB BoN remains the formal eval recipe; interactive ask does not load code teacher.

Reproduce:

```bash
npm run nano:z:export
npm run nano:z:ask -- --question "Write a Python function that returns a+b." --trial Z0-smoke
```

Next: **Z1 HITL-10** — see `.local/pesquisa.md` §9.4 + `.local/wave-z/SESSION.md`.
