# DEPL-AL — AL packaged deploy (**H-APPFRESH**)

> Wave AL5 **H-APPFRESH** · Inherit AK apps + AL fresh spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:appfresh -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:appfresh -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:appfresh -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AL stack

- H-GENFRESH · H-CTXFRESH · H-SMARTFRESH · H-FASTFRESH · H-APPFRESH

## Run

```bash
npm run nano:appfresh
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AL6 gen bar.
