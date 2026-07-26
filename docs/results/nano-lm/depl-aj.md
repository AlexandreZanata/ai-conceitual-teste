# DEPL-AJ — AJ packaged deploy (**H-APPPEAK**)

> Wave AJ5 **H-APPPEAK** · Inherit AI apps + AJ peak spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:apppeak -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:apppeak -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:apppeak -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AJ stack

- H-GENPEAK · H-CTXPEAK · H-SMARTPEAK · H-FASTPEAK · H-APPPEAK

## Run

```bash
npm run nano:apppeak
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AJ6 gen bar.
