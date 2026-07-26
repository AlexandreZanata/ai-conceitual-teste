# app-longdoc — scoped nano app (APPFRESH)

> Wave AL5 **H-APPFRESH** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXFRESH → H-FASTFRESH → H-APPFRESH`
> Claim: scoped long-doc exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `long-doc` — dual-arm LOOKUP + GENERATE on AL0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED+GENFRESH_PEAK | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:appfresh -- --app app-longdoc
npm run nano:appfresh
```

## AL stack

- H-GENFRESH · H-CTXFRESH · H-SMARTFRESH · H-FASTFRESH · H-APPFRESH

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
