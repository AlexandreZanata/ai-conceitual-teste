# app-howto — scoped nano app (APPPEAK)

> Wave AJ5 **H-APPPEAK** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXPEAK → H-FASTPEAK → H-APPPEAK`
> Claim: scoped howto exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `howto` — dual-arm LOOKUP + GENERATE on AJ0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QPFB2+GROUNDED+PEAK | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:apppeak -- --app app-howto
npm run nano:apppeak
```

## AJ stack

- H-GENPEAK · H-CTXPEAK · H-SMARTPEAK · H-FASTPEAK · H-APPPEAK

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
