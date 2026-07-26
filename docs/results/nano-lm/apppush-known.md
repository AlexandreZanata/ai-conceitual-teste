# app-known — scoped nano app (APPPUSH)

> Wave AI5 **H-APPPUSH** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXPUSH → H-FASTPUSH → H-APPPUSH`
> Claim: scoped known-ask exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `known-ask` — dual-arm LOOKUP + GENERATE on AI0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED wrap path | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:apppush -- --app app-known
npm run nano:apppush
```

## AI stack

- H-GENPLUS · H-CTXPUSH · H-SMARTPUSH · H-FASTPUSH · H-APPPUSH

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
