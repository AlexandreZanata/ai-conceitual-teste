# DEPL-AN — AN packaged deploy (**H-APPEDGE**)

> Wave AN5 **H-APPEDGE** · Inherit AM apps + AN edge spines
> Claim: scoped apps expose LOOKUP vs GENERATE — not open chat LM

## Routes

| Surface | App | npm |
|---------|-----|-----|
| `known-ask` | `app-known` | `npm run nano:appedge -- --app app-known` |
| `howto` | `app-howto` | `npm run nano:appedge -- --app app-howto` |
| `long-doc` | `app-longdoc` | `npm run nano:appedge -- --app app-longdoc` |

## Dual-arm law

- LOOKUP: labeled WRAP_LOOKUP / SEMWRAP — product path only.
- GENERATE: wall_ms>0 · n_new>0 · Cursor scores completion.
- Never PROMOTE smarter LM from LOOKUP-only HITL.

## AN stack

- H-GENEDGE · H-CTXEDGE · H-SMARTEDGE · H-FASTEDGE · H-APPEDGE

## Run

```bash
npm run nano:appedge
```

## Honesty

- Not an open chat LM.
- Forbidden: STREAM · KVCACHE-Q · GENCACHE · ZPREF · QI · MIXD.
- Ship claim remains AF packaged stack (AN6 HITL bar cleared — see [wave-an-hitl.md](wave-an-hitl.md)).
