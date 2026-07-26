# app-known — scoped nano app (APPREAL)

> Wave AG5 **H-APPREAL** · Spine: `H-SEMWRAP → H-ASKFAST → H-ANTIFP → H-APPREAL`
> Claim: scoped known-ask exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `known-ask` — dual-arm LOOKUP + GENERATE on AG0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QT+EARLY wrap=False | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:appreal -- --app app-known
npm run nano:appreal
```

## AG stack

- H-ANTIFP · H-CTXREAL · H-SMARTREAL · H-FASTREAL · H-APPREAL

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
