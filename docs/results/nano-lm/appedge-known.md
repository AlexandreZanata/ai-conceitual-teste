# app-known — scoped nano app (APPEDGE)

> Wave AN5 **H-APPEDGE** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXEDGE → H-FASTEDGE → H-APPEDGE`
> Claim: scoped known-ask exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `known-ask` — dual-arm LOOKUP + GENERATE on AN0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED+GENEDGE_PEAK | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:appedge -- --app app-known
npm run nano:appedge
```

## AN stack

- H-GENEDGE · H-CTXEDGE · H-SMARTEDGE · H-FASTEDGE · H-APPEDGE

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
