# app-longdoc — scoped nano app (APPBASE)

> Wave AP5 **H-APPBASE** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXBASE → H-FASTBASE → H-APPBASE`
> Claim: scoped long-doc exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `long-doc` — dual-arm LOOKUP + GENERATE on AP0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED+GENBASE_PEAK | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:appbase -- --app app-longdoc
npm run nano:appbase
```

## AP stack

- H-GENBASE · H-CTXBASE · H-SMARTBASE · H-FASTBASE · H-APPBASE

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
