# DEPL-AI — AI packaged deploy (**H-APPPUSH**)

> Wave AI5 **H-APPPUSH** · Inherit AF/AH apps + AI push spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:apppush -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:apppush -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:apppush -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AI stack

- H-GENPLUS · H-CTXPUSH · H-SMARTPUSH · H-FASTPUSH · H-APPPUSH

## Run

```bash
npm run nano:apppush
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AI6 gen bar.
