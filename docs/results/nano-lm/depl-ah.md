# DEPL-AH — AH packaged deploy (**H-APPLIFT**)

> Wave AH5 **H-APPLIFT** · Inherit AF/AG apps + AH lift spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:applift -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:applift -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:applift -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AH stack

- H-GENLIFT · H-CTXLIFT · H-SMARTLIFT · H-FASTLIFT · H-APPLIFT

## Run

```bash
npm run nano:applift
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AH6 gen bar.
