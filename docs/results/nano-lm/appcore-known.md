# app-known — scoped nano app (APPCORE)

> Wave AO5 **H-APPCORE** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXCORE → H-FASTCORE → H-APPCORE`
> Claim: scoped known-ask exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `known-ask` — dual-arm LOOKUP + GENERATE on AO0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED+GENCORE_PEAK | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:appcore -- --app app-known
npm run nano:appcore
```

## AO stack

- H-GENCORE · H-CTXCORE · H-SMARTCORE · H-FASTCORE · H-APPCORE

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
