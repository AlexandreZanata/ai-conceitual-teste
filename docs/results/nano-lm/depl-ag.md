# DEPL-AG — AG packaged deploy (**H-APPREAL**)

> Wave AG5 **H-APPREAL** · Inherit AF apps + AG anti-FP dual-arm
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:appreal -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:appreal -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:appreal -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AG stack

- H-ANTIFP · H-CTXREAL · H-SMARTREAL · H-FASTREAL · H-APPREAL

## Run

```bash
npm run nano:appreal
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AG6.
