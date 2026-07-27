# DEPL-AP — AP packaged deploy (**H-APPBASE**)

> Wave AP5 **H-APPBASE** · Inherit AO apps + AP base spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:appbase -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:appbase -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:appbase -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AP stack

- H-GENBASE · H-CTXBASE · H-SMARTBASE · H-FASTBASE · H-APPBASE

## Run

```bash
npm run nano:appbase
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack until AP6 HITL bar.
