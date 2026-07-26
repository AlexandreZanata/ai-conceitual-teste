# app-howto — scoped nano app (APPNEXT)

> Wave AM5 **H-APPNEXT** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXNEXT → H-FASTNEXT → H-APPNEXT`
> Claim: scoped howto exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `howto` — dual-arm LOOKUP + GENERATE on AM0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED+GENTRUTH_PEAK | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:appnext -- --app app-howto
npm run nano:appnext
```

## AM stack

- H-GENTRUTH · H-CTXNEXT · H-SMARTNEXT · H-FASTNEXT · H-APPNEXT

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
