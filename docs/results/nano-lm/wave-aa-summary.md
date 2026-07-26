# Wave AA — product expansion post-freeze (**COMPLETE**)

> Lab: `.local/pesquisa.md` §8.1 · Paper-lab: [paper-lab-wave-aa.md](paper-lab-wave-aa.md)  
> Parent: Wave Z **H-ZWRAP** · DEPL-Y: [wave-z-depl-y.md](wave-z-depl-y.md)

**Status: COMPLETE** · Thesis: **Known-ask product = H-ZWRAP+H-WRAPBANK; paraphrase brittle; open decode HOLD; preference KILL; DEPL docs synced.**

## Stage scoreboard

| # | ID | Decision | Evidence |
|---|-----|----------|----------|
| AA0 | **H-WRAPBANK** | **PROMOTE** | bank 10→20; HITL mean **9.0** — [formal](formal-hwrapbank-wrapbank.md) |
| AA1 | **H-PARA** | **HOLD** | miss 10/10; false-hit **0** — [formal](formal-hpara-para.md) |
| AA2 | **H-SERVEALIGN** | **HOLD** | mean **3.4** beats Z1; not pass bar — [formal](formal-hservealign-servealign.md) |
| AA3 | **H-ZPREF** | **KILL** | story < parent−ε — [formal](formal-hzpref-zpref.md) |
| AA4 | **H-DEPL-DOC** | **PROMOTE** | one-pagers ↔ DEPL-Y — [formal](formal-hdepldoc-depl-doc.md) |

## Honest product claims

| Claim | Truth |
|-------|-------|
| Known-ask HITL | **`--wrap` WRAP_LOOKUP** + **H-WRAPBANK** golds (**H-ZWRAP**) |
| Paraphrase / novel ask | Exact-match wrap **brittle** (H-PARA HOLD) |
| Open decode (QPFB2+BEAMKV) | Beats period collapse; **not** shippable chat (H-SERVEALIGN HOLD) |
| Preference retrain | Story regresses (H-ZPREF KILL) |
| “Open chat LM ≤5M” | **False** on this stack |

## Reproduce

```bash
npm run nano:aa:report
npm run nano:z:ask -- --wrap --question "…"
npm run nano:wrapbank
npm run nano:para
npm run nano:servealign
npm run nano:zpref
npm run nano:depl-doc
```

## Do not reopen

QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · GPFB-K=2 · naive CTX · ZERR/SERVEALIGN-as-chat.
