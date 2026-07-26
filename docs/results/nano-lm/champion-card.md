# Champion card — tip-stack + official recipes

> Compose closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** **KILL**).  
> Deploy: [RECIPES.md](RECIPES.md) · **DEPL-Y frozen:** [wave-z-depl-y.md](wave-z-depl-y.md). Lab: `.local/pesquisa.md` (**Z COMPLETE** · **Wave AA COMPLETE** · **Wave AB COMPLETE + FROZEN** · **Wave AC COMPLETE + FROZEN** · **Wave AD COMPLETE + FROZEN**).  
> Wave X+ close-out: [wave-x-summary.md](wave-x-summary.md) · Wave Y: [wave-y-summary.md](wave-y-summary.md) · Wave Z: [wave-z-summary.md](wave-z-summary.md) · Wave AA: [wave-aa-summary.md](wave-aa-summary.md) · Wave AB0: [wave-ab-session.md](wave-ab-session.md) · HITL: [wave-z-hitl.md](wave-z-hitl.md) · WRAPBANK: [formal-hwrapbank-wrapbank.md](formal-hwrapbank-wrapbank.md) · PARA: [formal-hpara-para.md](formal-hpara-para.md) · SERVEALIGN: [formal-hservealign-servealign.md](formal-hservealign-servealign.md) · ZPREF: [formal-hzpref-zpref.md](formal-hzpref-zpref.md) · DEPL-DOC: [formal-hdepldoc-depl-doc.md](formal-hdepldoc-depl-doc.md).

## Official tips

| Tip | Role | Formal |
|-----|------|--------|
| **H-STAG′** | Train (PRE3/RETIP) | [TIPD](formal-htipd-vs-hstag.md) · parent [H-STAG](formal-hstag-vs-hcurl2.md) |
| **H-EARLY** | Decode speed | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| **H-POOL** | Decode quality@wall | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

## Official recipes (priority order)

| # | Recipe | Pack | Evidence |
|---|--------|------|----------|
| 1 | **Serve-fast @128** | **H-PACK** (+ **H-QT** int8) | [PACK](formal-hpack-vs-hearly.md) · [DOM](formal-hdom-howto.md) · [PROG](formal-hprog-programming.md) · [BTC](formal-hbtc-bitcoin.md) · [EFF](formal-heff-efficiency.md) · [QT](formal-hqt-quantize.md) · [DEPL](formal-hdepl-policy.md) |
| 2 | **Code-smart @128** | **H-ABS-QPFB2** + **BEAMKV / TCACHE / SCORERAM** | [PFB](formal-hpfb-pfb.md) · [PFB2](formal-hpfb2-pfb2.md) · [QPFB2](formal-hqpfb2-qpfb2.md) · [BPFB](formal-hbpfb-bpfb.md) · [GPFB4](formal-hgpfb4-gpfb4.md) · [BEAMKV](formal-hbeamkv-beamkv.md) · [TCACHE](formal-htcache-tcache.md) · [SCORERAM](formal-hscoreram-scoreram.md) |
| 3 | **Long ctx (L>128)** | **ROLL / SUMCACHE / GPFB4-LONG** (+ **PFB256**) | [PFB256](formal-hpfb256-pfb256.md) · [ROLL](formal-hroll-roll.md) · [SUMCACHE](formal-hsumcache-sumcache.md) · [GPFB4-LONG](formal-hgpfb4long-gpfb4long.md) |
| 4 | **Train-step / e2e** | **H-TPACK** + **AMORT** | [tpack](formal-htpack-vs-hstag.md) · [amort](formal-hamort-vs-hstag.md) · [TIPD](formal-htipd-vs-hstag.md) |
| 5 | **Serve-quality** (in-harness) | **H-QPACK** | [formal](formal-hqpack-vs-hpool.md) · OOD XFER **KILL** → [archive](archive/hxfer-transfer.md) |
| 6 | **Known-ask HITL** | **H-ZWRAP** (`--wrap`) + **H-WRAPBANK** + **H-SEMWRAP** (`--semwrap`) | [Z4](wave-z-hitl-z4.md) · [WRAPBANK](formal-hwrapbank-wrapbank.md) · [SEMWRAP](formal-hsemwrap-semwrap.md) · [DEPL-Y](wave-z-depl-y.md) |

## Tip scoreboard

| ID | teacher_lp | wall_ms | Status |
|----|------------|---------|--------|
| **H-STAG′** | **−12.49** | — | official train (TIPD) |
| H-STAG (parent) | −13.28 | — | control |
| **H-EARLY** | **−11.83** | **65** | official fast |
| **H-POOL** | **−11.69** | **70** | official quality |

## Teachers / genetics

| ID | Role | Formal |
|----|------|--------|
| **H-TCHR** | Dual teacher (story + `tiny_starcoder_py`) | [formal-htchr-code-teacher.md](formal-htchr-code-teacher.md) **PROMOTE** |
| **H-GENC** | Serve genome under BUD | [formal-hgenc-genome.md](formal-hgenc-genome.md) **PROMOTE** |

## Commands

```bash
npm run nano:curated
npm run nano:pack && npm run nano:formal:hpack
npm run nano:qt && npm run nano:formal:hqt
npm run nano:qpfb2 && npm run nano:formal:hqpfb2
npm run nano:beamkv && npm run nano:formal:hbeamkv
npm run nano:tcache && npm run nano:formal:htcache
npm run nano:scoreram && npm run nano:formal:hscoreram
npm run nano:pfb256 && npm run nano:formal:hpfb256
npm run nano:roll && npm run nano:formal:hroll
npm run nano:sumcache && npm run nano:formal:hsumcache
npm run nano:gpfb4long && npm run nano:formal:hgpfb4long
npm run nano:z:export && npm run nano:z:ask -- --wrap --question "…"
npm run nano:wrapbank
npm run nano:ab:session
npm run nano:semwrap
npm run nano:askfast
npm run nano:longapp
npm run nano:asksmart
npm run nano:realapp
npm run nano:ab:hitl
npm run nano:ab:report
npm run nano:ab:freeze
npm run nano:ac:session
npm run nano:ctxplus
npm run nano:smartplus
npm run nano:fastplus
npm run nano:appplus
npm run nano:para
npm run nano:zpref
npm run nano:depl-doc
npm run nano:servealign
npm run nano:z:z4 -- --arms A,B,C
npm run nano:z:depl-y
npm run nano:z:z6
npm run nano:bpfb && npm run nano:formal:hbpfb
npm run nano:gpfb4 && npm run nano:formal:hgpfb4
npm run nano:tchr && npm run nano:formal:htchr
npm run nano:genc && npm run nano:formal:hgenc
```

## Wave Z product claims (honest)

| Goal | Use | Never claim |
|------|-----|-------------|
| Known-ask HITL demo | **`--wrap` LOOKUP** (`champion-wrap-v0`) — **H-ZWRAP** + **H-WRAPBANK** | Open generative chat LM |
| Story-safe CE ckpt | **H-ZERR** (`zerr-qpfb2-v0`) | ZERR fixes interactive Q&A (Z4 arm C FAIL) |

Evidence: [wave-z-hitl.md](wave-z-hitl.md) · [wave-z-hitl-z4.md](wave-z-hitl-z4.md) · [wave-z-depl-y.md](wave-z-depl-y.md).

## Waves

Wave W **COMPLETE** — [wave-w-summary.md](wave-w-summary.md) (PROG/BTC/EFF **PROMOTE**; MIXD **KILL**).  
Wave X+ **COMPLETE** — [wave-x-summary.md](wave-x-summary.md) (PFB family **PROMOTE**; RAG/CTX/Q*/… **KILL** → [`archive/`](archive/)).  
**Wave Y COMPLETE** — [wave-y-summary.md](wave-y-summary.md) (GPFB4-LONG **PROMOTE**; STREAM/KVCACHE-Q/GENCACHE **KILL**).  
**Wave Z COMPLETE** — [wave-z-hitl.md](wave-z-hitl.md) (PFB ≠ interactive LM; **H-ZWRAP** + error-bank) · [wave-z-summary.md](wave-z-summary.md) · [paper-lab-wave-z.md](paper-lab-wave-z.md) · [lab-freeze.md](lab-freeze.md).  
**Wave AA COMPLETE** — AA0 **H-WRAPBANK PROMOTE** · AA1 **H-PARA HOLD** · AA2 **H-SERVEALIGN HOLD** · AA3 **H-ZPREF KILL** · AA4 **H-DEPL-DOC PROMOTE** · AA5 **AA-REPORT PROMOTE** · AA6 **AA-FREEZE PROMOTE** — [wave-aa-summary.md](wave-aa-summary.md) · [aa-freeze.md](aa-freeze.md).  
**Wave AB COMPLETE + FROZEN** — [wave-ab-summary.md](wave-ab-summary.md) · [ab-freeze.md](ab-freeze.md) · [paper-lab-wave-ab.md](paper-lab-wave-ab.md).  
**Wave AC COMPLETE + FROZEN** — **H-CTXPLUS** · **H-SMARTPLUS** · **H-FASTPLUS** · **H-APPPLUS** · [wave-ac-summary.md](wave-ac-summary.md) · [ac-freeze.md](ac-freeze.md) · [paper-lab-wave-ac.md](paper-lab-wave-ac.md) · [wave-ac-hitl.md](wave-ac-hitl.md) · [formal-hctxplus-ctxplus.md](formal-hctxplus-ctxplus.md) · [formal-hsmartplus-smartplus.md](formal-hsmartplus-smartplus.md) · [formal-hfastplus-fastplus.md](formal-hfastplus-fastplus.md) · [formal-happplus-appplus.md](formal-happplus-appplus.md).
**Wave AD COMPLETE + FROZEN** — **H-HARDPARA** · **H-COMPOSE** · **H-ROUTEPLUS** · **H-DEPLPLUS** · [AD-HITL-10](wave-ad-hitl.md) · [wave-ad-summary.md](wave-ad-summary.md) · [ad-freeze.md](ad-freeze.md) · [paper-lab-wave-ad.md](paper-lab-wave-ad.md).  
**Wave AE OPEN** — AE0 [SESSION PROMOTE](wave-ae-session.md) · AE1 [H-CTXMAX PROMOTE](formal-hctxmax-ctxmax.md) · AE2 [H-SMARTMAX PROMOTE](formal-hsmartmax-smartmax.md) · AE3 [H-FASTMAX PROMOTE](formal-hfastmax-fastmax.md) · AE4 [H-APPMAX PROMOTE](formal-happmax-appmax.md) · next **AE-HITL-10** (ship claim = AD stack until AE5).

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).
