# app-known — scoped nano app (APPMORE)

> Wave AK5 **H-APPMORE** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXMORE → H-FASTMORE → H-APPMORE`
> Claim: scoped known-ask exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `known-ask` — dual-arm LOOKUP + GENERATE on AK0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED+GENTRUE_PEAK | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:appmore -- --app app-known
npm run nano:appmore
```

## AK stack

- H-GENTRUE · H-CTXMORE · H-SMARTMORE · H-FASTMORE · H-APPMORE

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
