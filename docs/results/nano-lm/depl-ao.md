# DEPL-AO — AO packaged deploy (**H-APPCORE**)

> Wave AO5 **H-APPCORE** · Inherit AN apps + AO core spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:appcore -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:appcore -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:appcore -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AO stack

- H-GENCORE · H-CTXCORE · H-SMARTCORE · H-FASTCORE · H-APPCORE

## Run

```bash
npm run nano:appcore
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AO6 HITL bar.
