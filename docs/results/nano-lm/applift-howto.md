# app-howto — scoped nano app (APPLIFT)

> Wave AH5 **H-APPLIFT** · Spine: `H-SEMWRAP → H-ASKFAST → H-CTXLIFT → H-FASTLIFT → H-APPLIFT`
> Claim: scoped howto exposes LOOKUP vs GENERATE arms — not open chat LM

## Job

Surface `howto` — dual-arm LOOKUP + GENERATE on AH0.

## Arms

| Arm | Mode family | IQ claim |
|-----|-------------|----------|
| LOOKUP | WRAP_LOOKUP / SEMWRAP / ASKFAST | product retrieve — not IQ |
| GENERATE | QT+EARLY wrap=False | wall_ms>0 · Cursor-scored |

## Run

```bash
npm run nano:applift -- --app app-howto
npm run nano:applift
```

## AH stack

- H-GENLIFT · H-CTXLIFT · H-SMARTLIFT · H-FASTLIFT · H-APPLIFT

## Honesty

- Not an open chat LM.
- LOOKUP scores ≠ generative IQ.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF revival.
