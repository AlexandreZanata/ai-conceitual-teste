# DEPL-AM — AM packaged deploy (**H-APPNEXT**)

> Wave AM5 **H-APPNEXT** · Inherit AL apps + AM next spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:appnext -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:appnext -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:appnext -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AM stack

- H-GENTRUTH · H-CTXNEXT · H-SMARTNEXT · H-FASTNEXT · H-APPNEXT

## Run

```bash
npm run nano:appnext
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AM6 gen bar.
