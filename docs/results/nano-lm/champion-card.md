# Champion card — tip-stack + official recipes

> Compose closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** **KILL**).  
> Deploy: [RECIPES.md](RECIPES.md) · **DEPL-Y frozen:** [wave-z-depl-y.md](wave-z-depl-y.md). Lab: `.local/pesquisa.md` (**Z COMPLETE** · **Wave AA COMPLETE** · **Wave AB COMPLETE + FROZEN** · **Wave AC COMPLETE + FROZEN** · **Wave AD COMPLETE + FROZEN** · **Wave AE COMPLETE + FROZEN** · **Wave AF COMPLETE + FROZEN** · **Wave AG COMPLETE + FROZEN** · **Wave AH COMPLETE + FROZEN** · **Wave AI COMPLETE + FROZEN** — [ai-freeze.md](ai-freeze.md) · **Wave AJ COMPLETE + FROZEN** — [aj-freeze.md](aj-freeze.md) · **Wave AK COMPLETE + FROZEN** — [ak-freeze.md](ak-freeze.md) · **Wave AL COMPLETE + FROZEN** — [al-freeze.md](al-freeze.md) · **Wave AM COMPLETE + FROZEN** — [am-freeze.md](am-freeze.md) · **Wave AN COMPLETE + FROZEN** — [an-freeze.md](an-freeze.md) · **Wave AO COMPLETE + FROZEN** — [ao-freeze.md](ao-freeze.md) · **Wave AP OPEN** — [wave-ap-session.md](wave-ap-session.md)).  
**Wave AP OPEN** — AP0 [SESSION PROMOTE](wave-ap-session.md) (`npm run nano:ap:session`) — freeze 10 held-out ≠ AB…AO · AP1 [H-GENBASE HOLD](formal-hgenbase-genbase.md) (`npm run nano:genbase`) — ablated gen 4.0; peak_only_lift · AP2 [H-CTXBASE PROMOTE](formal-hctxbase-ctxbase.md) (`npm run nano:ctxbase`) — L_eff 274198 > CTXCORE · AP3 [H-SMARTBASE PROMOTE](formal-hsmartbase-smartbase.md) (`npm run nano:smartbase`) — L/G 9.0/9.0 · AP4 [H-FASTBASE PROMOTE](formal-hfastbase-fastbase.md) (`npm run nano:fastbase`) — warm 0.056 / hot 0.047 < FASTCORE · AP5 [H-APPBASE PROMOTE](formal-happbase-appbase.md) (`npm run nano:appbase`) — apps+DEPL-AP L/G 8.33/9.0; next AP6 AP-HITL-10.
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
npm run nano:af:session
npm run nano:ah:session
npm run nano:genlift
npm run nano:ctxlift
npm run nano:ctxultra
npm run nano:smartultra
npm run nano:fastultra
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
**Wave AE COMPLETE + FROZEN** — **H-CTXMAX** · **H-SMARTMAX** · **H-FASTMAX** · **H-APPMAX** · [AE-HITL-10](wave-ae-hitl.md) · [wave-ae-summary.md](wave-ae-summary.md) · [ae-freeze.md](ae-freeze.md) · [paper-lab-wave-ae.md](paper-lab-wave-ae.md) (ship claim = **AE packaged stack**).  
**Wave AF COMPLETE + FROZEN** — **H-CTXULTRA** · **H-SMARTULTRA** · **H-FASTULTRA** · **H-APPULTRA** · [AF-HITL-10](wave-af-hitl.md) · [wave-af-summary.md](wave-af-summary.md) · [af-freeze.md](af-freeze.md) · [paper-lab-wave-af.md](paper-lab-wave-af.md) (ship claim = **AF packaged stack**).
**Wave AG COMPLETE + FROZEN** — AG0 [SESSION PROMOTE](wave-ag-session.md) · AG1 [H-ANTIFP PROMOTE](formal-hantifp-antifp.md) · AG2 [H-CTXREAL PROMOTE](formal-hctxreal-ctxreal.md) · AG3 [H-SMARTREAL HOLD](formal-hsmartreal-smartreal.md) · AG4 [H-FASTREAL PROMOTE](formal-hfastreal-fastreal.md) · AG5 [H-APPREAL HOLD](formal-happreal-appreal.md) · AG6 [AG-HITL-10 HOLD](wave-ag-hitl.md) · AG7 [AG-REPORT PROMOTE](wave-ag-summary.md) · AG8 [AG-FREEZE PROMOTE](ag-freeze.md) · dual-arm anti-FP HITL (ship claim remains **AF packaged stack**).  
**Wave AH COMPLETE + FROZEN** — AH0–AH7 done · AH2 [H-CTXLIFT PROMOTE](formal-hctxlift-ctxlift.md) · AH6 [AH-HITL-10 HOLD](wave-ah-hitl.md) · AH7 [AH-REPORT PROMOTE](wave-ah-summary.md) · [paper-lab-wave-ah.md](paper-lab-wave-ah.md) · AH8 [AH-FREEZE PROMOTE](ah-freeze.md) (`npm run nano:ah:freeze`) (ship claim remains **AF packaged stack**).
**Wave AI COMPLETE + FROZEN** — AI0 [SESSION PROMOTE](wave-ai-session.md) · AI1 [H-GENPLUS HOLD](formal-hgenplus-genplus.md) · AI1b [H-CAPRENEG HOLD](formal-hcapreneg-capreneg.md) · AI2 [H-CTXPUSH PROMOTE](formal-hctxpush-ctxpush.md) · AI3 [H-SMARTPUSH HOLD](formal-hsmartpush-smartpush.md) · AI4 [H-FASTPUSH PROMOTE](formal-hfastpush-fastpush.md) · AI5 [H-APPPUSH HOLD](formal-happpush-apppush.md) · AI6 [AI-HITL-10 HOLD](wave-ai-hitl.md) · AI7 [AI-REPORT PROMOTE](wave-ai-summary.md) · [paper-lab-wave-ai.md](paper-lab-wave-ai.md) · AI8 [AI-FREEZE PROMOTE](ai-freeze.md) (`npm run nano:ai:freeze`) (ship claim remains **AF packaged stack**; ≤5M stays; Wave AJ reopened via lab-book §6).  
**Wave AJ COMPLETE + FROZEN** — AJ0 [SESSION PROMOTE](wave-aj-session.md) · AJ1 [H-GENPEAK PROMOTE](formal-hgenpeak-genpeak.md) · AJ2 [H-CTXPEAK PROMOTE](formal-hctxpeak-ctxpeak.md) · AJ3 [H-SMARTPEAK PROMOTE](formal-hsmartpeak-smartpeak.md) · AJ4 [H-FASTPEAK PROMOTE](formal-hfastpeak-fastpeak.md) · AJ5 [H-APPPEAK PROMOTE](formal-happpeak-apppeak.md) · AJ6 [AJ-HITL-10 PROMOTE](wave-aj-hitl.md) · AJ7 [AJ-REPORT PROMOTE](wave-aj-summary.md) · AJ8 [AJ-FREEZE PROMOTE](aj-freeze.md) (`npm run nano:aj:freeze`) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AK reopened via lab-book.  
**Wave AK COMPLETE + FROZEN** — AK0 [SESSION PROMOTE](wave-ak-session.md) · AK1 [H-GENTRUE HOLD](formal-hgentrue-gentrue.md) · AK2 [H-CTXMORE PROMOTE](formal-hctxmore-ctxmore.md) · AK3 [H-SMARTMORE PROMOTE](formal-hsmartmore-smartmore.md) · AK4 [H-FASTMORE PROMOTE](formal-hfastmore-fastmore.md) · AK5 [H-APPMORE PROMOTE](formal-happmore-appmore.md) · AK6 [AK-HITL-10 PROMOTE](wave-ak-hitl.md) · AK7 [AK-REPORT PROMOTE](wave-ak-summary.md) · AK8 [AK-FREEZE PROMOTE](ak-freeze.md) (`npm run nano:ak:freeze`) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AL reopened via lab-book.
**Wave AL COMPLETE + FROZEN** — AL0 [SESSION PROMOTE](wave-al-session.md) · AL1 [H-GENFRESH HOLD](formal-hgenfresh-genfresh.md) · AL2 [H-CTXFRESH PROMOTE](formal-hctxfresh-ctxfresh.md) · AL3 [H-SMARTFRESH PROMOTE](formal-hsmartfresh-smartfresh.md) · AL4 [H-FASTFRESH PROMOTE](formal-hfastfresh-fastfresh.md) · AL5 [H-APPFRESH PROMOTE](formal-happfresh-appfresh.md) · AL6 [AL-HITL-10 PROMOTE](wave-al-hitl.md) · AL7 [AL-REPORT PROMOTE](wave-al-summary.md) · AL8 [AL-FREEZE PROMOTE](al-freeze.md) (`npm run nano:al:freeze`) · [formal-halfreeze-al-freeze.md](formal-halfreeze-al-freeze.md) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AM reopened via lab-book.  
**Wave AM COMPLETE + FROZEN** — AM0 [SESSION PROMOTE](wave-am-session.md) (`npm run nano:am:session`) · AM1 [H-GENTRUTH HOLD](formal-hgentruth-gentruth.md) (`npm run nano:gentruth`) · AM2 [H-CTXNEXT PROMOTE](formal-hctxnext-ctxnext.md) (`npm run nano:ctxnext`) — L_eff 213147 · AM3 [H-SMARTNEXT PROMOTE](formal-hsmartnext-smartnext.md) (`npm run nano:smartnext`) — cite+gen 9.0/9.0 · AM4 [H-FASTNEXT PROMOTE](formal-hfastnext-fastnext.md) (`npm run nano:fastnext`) — hot 0.17≪FASTFRESH · AM5 [H-APPNEXT PROMOTE](formal-happnext-appnext.md) (`npm run nano:appnext`) — SERVE gen 9.0 · AM6 [AM-HITL-10 PROMOTE](wave-am-hitl.md) (`npm run nano:am:hitl`) — L/G 9.0/9.0 · AM7 [AM-REPORT PROMOTE](wave-am-summary.md) (`npm run nano:am:report`) · [paper-lab-wave-am.md](paper-lab-wave-am.md); AM8 [AM-FREEZE PROMOTE](am-freeze.md) (`npm run nano:am:freeze`) · [formal-hamfreeze-am-freeze.md](formal-hamfreeze-am-freeze.md) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AN reopened via lab-book.
**Wave AN COMPLETE + FROZEN** — AN0 [SESSION PROMOTE](wave-an-session.md) (`npm run nano:an:session`) · AN1 [H-GENEDGE HOLD](formal-hgenedge-genedge.md) (`npm run nano:genedge`) — ablated gen 4.0; peak_only_lift · AN2 [H-CTXEDGE PROMOTE](formal-hctxedge-ctxedge.md) (`npm run nano:ctxedge`) — L_eff 242448 · AN3 [H-SMARTEDGE PROMOTE](formal-hsmartedge-smartedge.md) (`npm run nano:smartedge`) — cite+gen 9.0/9.0 · AN4 [H-FASTEDGE PROMOTE](formal-hfastedge-fastedge.md) (`npm run nano:fastedge`) — hot 0.05≪0.17 · AN5 [H-APPEDGE PROMOTE](formal-happedge-appedge.md) (`npm run nano:appedge`) — SERVE gen 9.0 · AN6 [AN-HITL-10 PROMOTE](wave-an-hitl.md) (`npm run nano:an:hitl`) — L/G 9.0/9.0 · AN7 [AN-REPORT PROMOTE](wave-an-summary.md) (`npm run nano:an:report`) · [paper-lab-wave-an.md](paper-lab-wave-an.md); AN8 [AN-FREEZE PROMOTE](an-freeze.md) (`npm run nano:an:freeze`) · [formal-hanfreeze-an-freeze.md](formal-hanfreeze-an-freeze.md) — COMPLETE+FROZEN; Wave AO reopened via lab-book.
**Wave AO COMPLETE + FROZEN** — AO0 [SESSION PROMOTE](wave-ao-session.md) (`npm run nano:ao:session`) — freeze 10 held-out ≠ AB…AN · AO1 [H-GENCORE HOLD](formal-hgencore-gencore.md) (`npm run nano:gencore`) — ablated gen 4.0; peak_only_lift · AO2 [H-CTXCORE PROMOTE](formal-hctxcore-ctxcore.md) (`npm run nano:ctxcore`) — L_eff 253105 > CTXEDGE · AO3 [H-SMARTCORE PROMOTE](formal-hsmartcore-smartcore.md) (`npm run nano:smartcore`) — L/G 9.0/9.0 · AO4 [H-FASTCORE PROMOTE](formal-hfastcore-fastcore.md) (`npm run nano:fastcore`) — warm 0.06 < FASTEDGE 0.10 · AO5 [H-APPCORE PROMOTE](formal-happcore-appcore.md) (`npm run nano:appcore`) — SERVE gen 9.0 · AO6 [AO-HITL-10 PROMOTE](wave-ao-hitl.md) (`npm run nano:ao:hitl`) — L/G 9.0/9.0 · AO7 [AO-REPORT PROMOTE](wave-ao-summary.md) (`npm run nano:ao:report`) · [paper-lab-wave-ao.md](paper-lab-wave-ao.md); AO8 [AO-FREEZE PROMOTE](ao-freeze.md) (`npm run nano:ao:freeze`) · [formal-haofreeze-ao-freeze.md](formal-haofreeze-ao-freeze.md) — COMPLETE+FROZEN; no Wave AP without reopen.

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).
