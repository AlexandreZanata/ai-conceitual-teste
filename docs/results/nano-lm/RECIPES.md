# Official nano-LM recipes (frozen claims)

> Tip-stack: **H-STAG′** / **H-EARLY** / **H-POOL**.  
> Deploy: [H-DEPL](formal-hdepl-policy.md) · **DEPL-Y freeze:** [wave-z-depl-y.md](wave-z-depl-y.md) · Domains: [DOM](formal-hdom-howto.md) / [PROG](formal-hprog-programming.md) / [BTC](formal-hbtc-bitcoin.md).  
> Lab: `.local/pesquisa.md` · Card: [champion-card.md](champion-card.md) · Y: [wave-y-summary.md](wave-y-summary.md) · Z: [wave-z-summary.md](wave-z-summary.md) · AA: [wave-aa-summary.md](wave-aa-summary.md)

## Deploy one-liners (DEPL-Y frozen)

| Goal | L / scope | Use | Do not claim |
|------|-----------|-----|----------------|
| **Fastest serve** | @128 | **H-PACK** + **H-QT** int8 n=1 | ood_long / STREAM |
| **Code-smart (prog)** | @128 | **H-ABS-QPFB2** + **BEAMKV / TCACHE / SCORERAM** | GPFB K=2 / STREAM / KVCACHE-Q |
| **Code-smart (btc)** | @128 | **H-ABS-BPFB** | — |
| **Long context** | L>128 | **H-ROLL / H-SUMCACHE / H-GPFB4-LONG** (+ **H-PFB256**) | STREAM / KVCACHE-Q / GENCACHE / naive CTX |
| **GENC ∘ PFB** | serve genome | **H-ABS-GPFB4** (K=4 only) | GPFB K=2 (**KILL**) |
| **Known-ask HITL** | demo Q&A | **`--wrap` / `--semwrap`** (`champion-wrap-v0`) — **H-ZWRAP** + **H-WRAPBANK** + **H-SEMWRAP** | open chat LM / ZERR-as-chat |
| **Story-safe CE** | train artifact | **H-ZERR** (`zerr-qpfb2-v0`) | interactive Q&A without wrap |
| **Cheaper train steps** | train | **H-TPACK** + **H-AMORT** | ETRAIN N=1 / MIXD |
| **Quality@wall** | in-harness | **H-QPACK** | QPACK OOD (XFER **KILL**) |

## Formal evidence (survivors)

| Recipe | Formal |
|--------|--------|
| PACK / domains / EFF | [hpack](formal-hpack-vs-hearly.md) · [prog](formal-hprog-programming.md) · [btc](formal-hbtc-bitcoin.md) · [eff](formal-heff-efficiency.md) |
| QT | [formal-hqt-quantize.md](formal-hqt-quantize.md) |
| PFB family | [pfb](formal-hpfb-pfb.md) · [pfb2](formal-hpfb2-pfb2.md) · [qpfb2](formal-hqpfb2-qpfb2.md) · [bpfb](formal-hbpfb-bpfb.md) · [gpfb4](formal-hgpfb4-gpfb4.md) |
| Wave Y cache / long | [beamkv](formal-hbeamkv-beamkv.md) · [tcache](formal-htcache-tcache.md) · [scoreram](formal-hscoreram-scoreram.md) · [pfb256](formal-hpfb256-pfb256.md) · [roll](formal-hroll-roll.md) · [sumcache](formal-hsumcache-sumcache.md) · [gpfb4long](formal-hgpfb4long-gpfb4long.md) |
| TCHR / GENC | [tchr](formal-htchr-code-teacher.md) · [genc](formal-hgenc-genome.md) |
| Train | [tpack](formal-htpack-vs-hstag.md) · [amort](formal-hamort-vs-hstag.md) · [TIPD](formal-htipd-vs-hstag.md) |
| Wave Z HITL / DEPL-Y | [hitl](wave-z-hitl.md) · [z4](wave-z-hitl-z4.md) · [depl-y](wave-z-depl-y.md) · [paper-lab](paper-lab-wave-z.md) |
| Wave AA wrap bank | [WRAPBANK](formal-hwrapbank-wrapbank.md) **PROMOTE** |
| Wave AA paraphrase | [PARA](formal-hpara-para.md) **HOLD** (0 false-hit; exact-match brittle) |
| Wave AA open decode | [SERVEALIGN](formal-hservealign-servealign.md) **HOLD** (beats Z1; not pass bar) |
| Wave AA preference | [ZPREF](formal-hzpref-zpref.md) **KILL** (story < parent−ε) |
| Wave AA doc sync | [DEPL-DOC](formal-hdepldoc-depl-doc.md) **PROMOTE** |
| Wave AA REPORT | [wave-aa-summary.md](wave-aa-summary.md) · [paper-lab-wave-aa.md](paper-lab-wave-aa.md) **PROMOTE** (`npm run nano:aa:report`) |
| Wave AA FREEZE | [aa-freeze.md](aa-freeze.md) **PROMOTE** (`npm run nano:aa:freeze`) — Wave AB only via §8.3 reopen |
| Wave AB0 SESSION | [wave-ab-session.md](wave-ab-session.md) **PROMOTE** (`npm run nano:ab:session`) — 10 real HITL Qs frozen |
| Wave AB1 SEMWRAP | [formal-hsemwrap-semwrap.md](formal-hsemwrap-semwrap.md) **PROMOTE** (`npm run nano:semwrap`) — fuzzy near-known ask |
| Wave AB2 ASKFAST | [formal-haskfast-askfast.md](formal-haskfast-askfast.md) **PROMOTE** (`npm run nano:askfast`) — wall↓≥20% compose |
| Wave AB3 LONGAPP | [formal-hlongapp-longapp.md](formal-hlongapp-longapp.md) **PROMOTE** (`npm run nano:longapp`) — L_eff≫W curated |
| Wave AB4 ASKSMART | [formal-hasksmart-asksmart.md](formal-hasksmart-asksmart.md) **PROMOTE** (`npm run nano:asksmart`) — >SERVEALIGN 3.4 |
| Wave AB5 REALAPP | [formal-hrealapp-realapp.md](formal-hrealapp-realapp.md) **PROMOTE** (`npm run nano:realapp`) — app-known + app-longdoc |
| Wave AB6 HITL-10 | [wave-ab-hitl.md](wave-ab-hitl.md) **PROMOTE** (`npm run nano:ab:hitl`) — final mean 9.0 |
| Wave AB7 REPORT | [wave-ab-summary.md](wave-ab-summary.md) **PROMOTE** (`npm run nano:ab:report`) — COMPLETE |
| Wave AB-FREEZE | [ab-freeze.md](ab-freeze.md) **PROMOTE** (`npm run nano:ab:freeze`) — no Wave AC invent |
| Wave AC0 SESSION | [wave-ac-session.md](wave-ac-session.md) **PROMOTE** (`npm run nano:ac:session`) — 10 held-out HITL Qs |
| Wave AC1 CTXPLUS | [formal-hctxplus-ctxplus.md](formal-hctxplus-ctxplus.md) **PROMOTE** (`npm run nano:ctxplus`) — L_eff 20523>AB; usable 10/10 |
| Wave AC2 SMARTPLUS | [formal-hsmartplus-smartplus.md](formal-hsmartplus-smartplus.md) **PROMOTE** (`npm run nano:smartplus`) — hard paraphrase; false-hit 0 |
| Wave AC3 FASTPLUS | [formal-hfastplus-fastplus.md](formal-hfastplus-fastplus.md) **PROMOTE** (`npm run nano:fastplus`) — e2e≪AB; wall_drop 100% |
| Wave AC4 APPPLUS | [formal-happplus-appplus.md](formal-happplus-appplus.md) **PROMOTE** (`npm run nano:appplus`) — app-howto + known/longdoc green |
| Wave AC5 HITL-10 | [wave-ac-hitl.md](wave-ac-hitl.md) **PROMOTE** (`npm run nano:ac:hitl`) — final mean 9.0 |
| Wave AC6 REPORT | [wave-ac-summary.md](wave-ac-summary.md) **PROMOTE** (`npm run nano:ac:report`) — COMPLETE |
| Wave AC-FREEZE | [ac-freeze.md](ac-freeze.md) **PROMOTE** (`npm run nano:ac:freeze`) — no Wave AD invent |
| Wave AD0 SESSION | [wave-ad-session.md](wave-ad-session.md) **PROMOTE** (`npm run nano:ad:session`) — 10 held-out HITL Qs |
| Wave AD1 HARDPARA | [formal-hhardpara-hardpara.md](formal-hhardpara-hardpara.md) **PROMOTE** (`npm run nano:hardpara`) — **H-HARDPARA**; false-hit 0 |
| Wave AD2 COMPOSE | [formal-hcompose-compose.md](formal-hcompose-compose.md) **PROMOTE** (`npm run nano:compose`) — dual-source; usable 10/10 |
| Wave AD3 ROUTEPLUS | [formal-hrouteplus-routeplus.md](formal-hrouteplus-routeplus.md) **PROMOTE** (`npm run nano:routeplus`) — route+OOS 10/10 |
| Wave AD4 DEPLPLUS | [formal-hdeplplus-deplplus.md](formal-hdeplplus-deplplus.md) **PROMOTE** (`npm run nano:deplplus`) — pages 4/4 · smoke 9.0 |
| Wave AD5 HITL-10 | [wave-ad-hitl.md](wave-ad-hitl.md) **PROMOTE** (`npm run nano:ad:hitl`) — **AD-HITL-10** mean 9.0 · errors 0/10 |
| Wave AD6 REPORT | [wave-ad-summary.md](wave-ad-summary.md) · [paper-lab-wave-ad.md](paper-lab-wave-ad.md) **PROMOTE** (`npm run nano:ad:report`) |
| Wave AD-FREEZE | [ad-freeze.md](ad-freeze.md) **PROMOTE** (`npm run nano:ad:freeze`) — no Wave AE invent without reopen |
| Wave AE0 SESSION | [wave-ae-session.md](wave-ae-session.md) **PROMOTE** (`npm run nano:ae:session`) — 10 held-out HITL Qs (4th set) |
| Wave AE1 CTXMAX | [formal-hctxmax-ctxmax.md](formal-hctxmax-ctxmax.md) **PROMOTE** (`npm run nano:ctxmax`) — multi-doc K=5; L_eff↑ vs CTXPLUS |
| Wave AE2 SMARTMAX | [formal-hsmartmax-smartmax.md](formal-hsmartmax-smartmax.md) **PROMOTE** (`npm run nano:smartmax`) — multi-hop cite; false-hit 0 |
| Wave AE3 FASTMAX | [formal-hfastmax-fastmax.md](formal-hfastmax-fastmax.md) **PROMOTE** (`npm run nano:fastmax`) — hot e2e ≪ FASTPLUS |
| Wave AE4 APPMAX | [formal-happmax-appmax.md](formal-happmax-appmax.md) **PROMOTE** (`npm run nano:appmax`) — howto↑ + app-route + DEPL-AE |
| Wave AE5 AE-HITL-10 | [wave-ae-hitl.md](wave-ae-hitl.md) **PROMOTE** (`npm run nano:ae:hitl`) — final pack mean 9.0 |
| Wave AE6 AE-REPORT | [wave-ae-summary.md](wave-ae-summary.md) **PROMOTE** (`npm run nano:ae:report`) — paper-lab + FIX log |
| Wave AE-FREEZE | [ae-freeze.md](ae-freeze.md) **PROMOTE** (`npm run nano:ae:freeze`) — no Wave AF invent without reopen |
| Wave AF0 SESSION | [wave-af-session.md](wave-af-session.md) **PROMOTE** (`npm run nano:af:session`) — 10 held-out HITL Qs (5th set) |
| Wave AF1 CTXULTRA | [formal-hctxultra-ctxultra.md](formal-hctxultra-ctxultra.md) **PROMOTE** (`npm run nano:ctxultra`) — triple-doc K=7; L_eff↑ vs CTXMAX |
| Wave AF2 SMARTULTRA | [formal-hsmartultra-smartultra.md](formal-hsmartultra-smartultra.md) **PROMOTE** (`npm run nano:smartultra`) — triple-hop cite≥8; false-hit 0 |
| Wave AF3 FASTULTRA | [formal-hfastultra-fastultra.md](formal-hfastultra-fastultra.md) **PROMOTE** (`npm run nano:fastultra`) — hot e2e ↓ vs FASTMAX |
| Wave AF4 APPULTRA | [formal-happultra-appultra.md](formal-happultra-appultra.md) **PROMOTE** (`npm run nano:appultra`) — howto↑ + compose 5th + DEPL-AF |
| Wave AF5 AF-HITL-10 | [wave-af-hitl.md](wave-af-hitl.md) **PROMOTE** (`npm run nano:af:hitl`) — final pack mean 9.0 |
| Wave AF6 AF-REPORT | [wave-af-summary.md](wave-af-summary.md) · [paper-lab-wave-af.md](paper-lab-wave-af.md) **PROMOTE** (`npm run nano:af:report`) |
| Wave AF7 AF-FREEZE | [af-freeze.md](af-freeze.md) **PROMOTE** (`npm run nano:af:freeze`) — no Wave AG invent without reopen |
| Wave AG0 SESSION | [wave-ag-session.md](wave-ag-session.md) **PROMOTE** (`npm run nano:ag:session`) — 10 held-out HITL Qs (6th set; dual-arm) |
| Wave AH0 SESSION | [wave-ah-session.md](wave-ah-session.md) **PROMOTE** (`npm run nano:ah:session`) — 10 held-out HITL Qs (7th set; dual-arm; next AH1 H-GENLIFT) |
| Wave AH1 H-GENLIFT | [formal-hgenlift-genlift.md](formal-hgenlift-genlift.md) **HOLD** (`npm run nano:genlift`) — anti-period gen lift; L=9.0 G=4.0; next AH2 H-CTXLIFT |
| Wave AH2 H-CTXLIFT | [formal-hctxlift-ctxlift.md](formal-hctxlift-ctxlift.md) **PROMOTE** (`npm run nano:ctxlift`) — penta-doc K=11; L_eff↑ vs CTXREAL |
| Wave AH3 H-SMARTLIFT | [formal-hsmartlift-smartlift.md](formal-hsmartlift-smartlift.md) **HOLD** (`npm run nano:smartlift`) — cite 10/10; L=9.0 G=4.0 |
| Wave AH4 H-FASTLIFT | [formal-hfastlift-fastlift.md](formal-hfastlift-fastlift.md) **PROMOTE** (`npm run nano:fastlift`) — hot 11.6&lt;FASTREAL 16.1 |
| Wave AH5 H-APPLIFT | [formal-happlift-applift.md](formal-happlift-applift.md) **HOLD** (`npm run nano:applift`) — expose+DEPL; G=1.0 |
| Wave AH6 AH-HITL-10 | [wave-ah-hitl.md](wave-ah-hitl.md) **HOLD** (`npm run nano:ah:hitl`) — L=9.0 G=1.0 |
| Wave AH7 AH-REPORT | [wave-ah-summary.md](wave-ah-summary.md) **PROMOTE** (`npm run nano:ah:report`) — + [paper-lab-wave-ah.md](paper-lab-wave-ah.md) |
| Wave AH8 AH-FREEZE | [ah-freeze.md](ah-freeze.md) **PROMOTE** (`npm run nano:ah:freeze`) — lock; Wave AI reopened via lab-book §5 |
| Wave AI0 SESSION | [wave-ai-session.md](wave-ai-session.md) **PROMOTE** (`npm run nano:ai:session`) — 10 held-out HITL Qs (8th set; dual-arm) |
| Wave AI1 H-GENPLUS | [formal-hgenplus-genplus.md](formal-hgenplus-genplus.md) **HOLD** (`npm run nano:genplus`) — grounded QPFB2 gen push; L=9.0 G=4.0 |
| Wave AI1b H-CAPRENEG | [formal-hcapreneg-capreneg.md](formal-hcapreneg-capreneg.md) **HOLD** (`npm run nano:capreneg`) — CAP-125M probe; gen 4.0; **keep ≤5M** |
| Wave AI2 H-CTXPUSH | [formal-hctxpush-ctxpush.md](formal-hctxpush-ctxpush.md) **PROMOTE** (`npm run nano:ctxpush`) — hexa-doc K=13; L_eff=162851 > CTXLIFT |
| Wave AI3 H-SMARTPUSH | [formal-hsmartpush-smartpush.md](formal-hsmartpush-smartpush.md) **HOLD** (`npm run nano:smartpush`) — hexa-hop cite; L=9.0 G=4.0 |
| Wave AI4 H-FASTPUSH | [formal-hfastpush-fastpush.md](formal-hfastpush-fastpush.md) **PROMOTE** (`npm run nano:fastpush`) — gen hot 10.7&lt;FASTLIFT 11.6 |
| Wave AI5 H-APPPUSH | [formal-happpush-apppush.md](formal-happpush-apppush.md) **HOLD** (`npm run nano:apppush`) — 3 apps + DEPL-AI; L=8.33 G=4.0 |
| Wave AI6 AI-HITL-10 | [wave-ai-hitl.md](wave-ai-hitl.md) **HOLD** (`npm run nano:ai:hitl`) — final dual-arm L=9.0 G=4.0 |
| Wave AI7 AI-REPORT | [wave-ai-summary.md](wave-ai-summary.md) **PROMOTE** (`npm run nano:ai:report`) — public summary + [paper-lab-wave-ai.md](paper-lab-wave-ai.md) |
| Wave AI8 AI-FREEZE | [ai-freeze.md](ai-freeze.md) **PROMOTE** (`npm run nano:ai:freeze`) — COMPLETE + FROZEN; Wave AJ reopened via lab-book §6 |
| Wave AJ0 SESSION | [wave-aj-session.md](wave-aj-session.md) **PROMOTE** (`npm run nano:aj:session`) — freeze 10 held-out ≠ AB…AI; next AJ1 H-GENPEAK |
| Wave AJ1 H-GENPEAK | [formal-hgenpeak-genpeak.md](formal-hgenpeak-genpeak.md) **PROMOTE** (`npm run nano:genpeak`) — grounded+extractive peak; L=9.0 G=9.0; next AJ2 H-CTXPEAK |
| Wave AJ2 H-CTXPEAK | [formal-hctxpeak-ctxpeak.md](formal-hctxpeak-ctxpeak.md) **PROMOTE** (`npm run nano:ctxpeak`) — hepta-doc K=15; L_eff=177809 > CTXPUSH; next AJ3 H-SMARTPEAK |
| Wave AJ3 H-SMARTPEAK | [formal-hsmartpeak-smartpeak.md](formal-hsmartpeak-smartpeak.md) **PROMOTE** (`npm run nano:smartpeak`) — hepta-hop cite+GENPEAK; L=9.0 G=9.0; next AJ4 H-FASTPEAK |
| Wave AJ4 H-FASTPEAK | [formal-hfastpeak-fastpeak.md](formal-hfastpeak-fastpeak.md) **PROMOTE** (`npm run nano:fastpeak`) — peak-fast hot ~5.0ms < FASTPUSH 10.7; next AJ5 H-APPPEAK |
| Wave AJ5 H-APPPEAK | [formal-happpeak-apppeak.md](formal-happpeak-apppeak.md) **PROMOTE** (`npm run nano:apppeak`) — 3 apps + DEPL-AJ; L=8.3 G=9.0 > APPPUSH; next AJ6 AJ-HITL-10 |
| Wave AJ6 AJ-HITL-10 | [wave-aj-hitl.md](wave-aj-hitl.md) **PROMOTE** (`npm run nano:aj:hitl`) — final dual-arm L=9.0 G=9.0; next AJ7 AJ-REPORT |
| Wave AJ7 AJ-REPORT | [wave-aj-summary.md](wave-aj-summary.md) · [paper-lab-wave-aj.md](paper-lab-wave-aj.md) **PROMOTE** (`npm run nano:aj:report`) — public closeout + anti-FP; next AJ8 AJ-FREEZE |
| Wave AJ8 AJ-FREEZE | [aj-freeze.md](aj-freeze.md) · [formal-hajfreeze-aj-freeze.md](formal-hajfreeze-aj-freeze.md) **PROMOTE** (`npm run nano:aj:freeze`) — COMPLETE+FROZEN; Wave AK reopened via lab-book |
| Wave AK0 SESSION | [wave-ak-session.md](wave-ak-session.md) **PROMOTE** (`npm run nano:ak:session`) — freeze 10 held-out ≠ AB…AJ; next AK1 H-GENTRUE |
| Wave AK1 H-GENTRUE | [formal-hgentrue-gentrue.md](formal-hgentrue-gentrue.md) **HOLD** (`npm run nano:gentrue`) — ablated gen 4.0; peak_only_lift; next AK2 H-CTXMORE |
| Wave AK2 H-CTXMORE | [formal-hctxmore-ctxmore.md](formal-hctxmore-ctxmore.md) **PROMOTE** (`npm run nano:ctxmore`) — octa K=17; L_eff 188984 > CTXPEAK; next AK3 H-SMARTMORE |
| Wave AK3 H-SMARTMORE | [formal-hsmartmore-smartmore.md](formal-hsmartmore-smartmore.md) **PROMOTE** (`npm run nano:smartmore`) — octa-hop cite+GENTRUE peak; L=9.0 G=9.0; next AK4 H-FASTMORE |
| Wave AG1 H-ANTIFP | [formal-hantifp-antifp.md](formal-hantifp-antifp.md) **PROMOTE** (`npm run nano:antifp`) — LOOKUP≠gen IQ; dual-arm telemetry |
| Wave AG2 H-CTXREAL | [formal-hctxreal-ctxreal.md](formal-hctxreal-ctxreal.md) **PROMOTE** (`npm run nano:ctxreal`) — quad-doc K=9; L_eff↑ vs CTXULTRA |
| Wave AG3 H-SMARTREAL | [formal-hsmartreal-smartreal.md](formal-hsmartreal-smartreal.md) **HOLD** (`npm run nano:smartreal`) — cite 10/10; gen 4.0 &lt;5 |


## Policy

**DEPL-Y:** speed@128→PACK/QT; code@128→QPFB2+BEAMKV/TCACHE/SCORERAM; long→ROLL/SUMCACHE/GPFB4-LONG; HITL→H-ZWRAP(+WRAPBANK); CE→H-ZERR≠chat; **REJECT** STREAM / KVCACHE-Q / GENCACHE / GPFB-K=2 / ood_long PACK / MIXD.  
Wave W: [wave-w-summary.md](wave-w-summary.md). Wave X+ KILLs: [wave-x-summary.md](wave-x-summary.md) → [`archive/`](archive/).  
**Wave Y COMPLETE:** [wave-y-summary.md](wave-y-summary.md). **Wave Z COMPLETE:** [wave-z-hitl.md](wave-z-hitl.md) — PFB ≠ interactive LM; wrap + error-bank. **NO-REOPEN:** [lab-freeze.md](lab-freeze.md).  
**Wave AA COMPLETE:** AA0 [H-WRAPBANK PROMOTE](formal-hwrapbank-wrapbank.md); AA1 [H-PARA HOLD](formal-hpara-para.md); AA2 [H-SERVEALIGN HOLD](formal-hservealign-servealign.md); AA3 [H-ZPREF KILL](formal-hzpref-zpref.md); AA4 [H-DEPL-DOC PROMOTE](formal-hdepldoc-depl-doc.md); AA5 [AA-REPORT PROMOTE](wave-aa-summary.md); AA6 [AA-FREEZE PROMOTE](aa-freeze.md).  
**Wave AB COMPLETE + FROZEN:** AB0–AB7 **PROMOTE** · AB-FREEZE — [wave-ab-summary.md](wave-ab-summary.md) · [ab-freeze.md](ab-freeze.md).  
**Wave AC COMPLETE + FROZEN:** AC0–AC6 **PROMOTE** · AC-FREEZE — [wave-ac-summary.md](wave-ac-summary.md) · [ac-freeze.md](ac-freeze.md) · [paper-lab-wave-ac.md](paper-lab-wave-ac.md) · **H-CTXPLUS** · **H-SMARTPLUS** · **H-FASTPLUS** · **H-APPPLUS** · [AC-HITL-10](wave-ac-hitl.md).
**Wave AD COMPLETE + FROZEN:** AD0–AD6 **PROMOTE** · AD-FREEZE — [wave-ad-summary.md](wave-ad-summary.md) · [ad-freeze.md](ad-freeze.md) · [paper-lab-wave-ad.md](paper-lab-wave-ad.md) · **H-HARDPARA** · **H-COMPOSE** · **H-ROUTEPLUS** · **H-DEPLPLUS** · [AD-HITL-10](wave-ad-hitl.md).  
**Wave AE COMPLETE + FROZEN:** AE0–AE6 **PROMOTE** · AE-FREEZE — [wave-ae-summary.md](wave-ae-summary.md) · [ae-freeze.md](ae-freeze.md) · [paper-lab-wave-ae.md](paper-lab-wave-ae.md) · **H-CTXMAX** · **H-SMARTMAX** · **H-FASTMAX** · **H-APPMAX** · [AE-HITL-10](wave-ae-hitl.md).  
**Wave AF COMPLETE + FROZEN:** AF0–AF6 **PROMOTE** · AF-FREEZE — [wave-af-summary.md](wave-af-summary.md) · [af-freeze.md](af-freeze.md) · [paper-lab-wave-af.md](paper-lab-wave-af.md) · **H-CTXULTRA** · **H-SMARTULTRA** · **H-FASTULTRA** · **H-APPULTRA** · [AF-HITL-10](wave-af-hitl.md) (ship claim = **AF packaged stack**).  
**Wave AG COMPLETE + FROZEN:** AG0 [SESSION PROMOTE](wave-ag-session.md) · AG1 [H-ANTIFP PROMOTE](formal-hantifp-antifp.md) · AG2 [H-CTXREAL PROMOTE](formal-hctxreal-ctxreal.md) · AG3 [H-SMARTREAL HOLD](formal-hsmartreal-smartreal.md) · AG4 [H-FASTREAL PROMOTE](formal-hfastreal-fastreal.md) · AG5 [H-APPREAL HOLD](formal-happreal-appreal.md) · AG6 [AG-HITL-10 HOLD](wave-ag-hitl.md) · AG7 [AG-REPORT PROMOTE](wave-ag-summary.md) · [paper-lab-wave-ag.md](paper-lab-wave-ag.md) · AG8 [AG-FREEZE PROMOTE](ag-freeze.md) (`npm run nano:ag:freeze`) — ship claim remains **AF packaged stack**; Wave AH reopened via lab-book §5.
**Wave AH COMPLETE + FROZEN:** AH0 [SESSION PROMOTE](wave-ah-session.md) · AH1 [H-GENLIFT HOLD](formal-hgenlift-genlift.md) · AH2 [H-CTXLIFT PROMOTE](formal-hctxlift-ctxlift.md) · AH3 [H-SMARTLIFT HOLD](formal-hsmartlift-smartlift.md) · AH4 [H-FASTLIFT PROMOTE](formal-hfastlift-fastlift.md) · AH5 [H-APPLIFT HOLD](formal-happlift-applift.md) · AH6 [AH-HITL-10 HOLD](wave-ah-hitl.md) · AH7 [AH-REPORT PROMOTE](wave-ah-summary.md) · [paper-lab-wave-ah.md](paper-lab-wave-ah.md) · AH8 [AH-FREEZE PROMOTE](ah-freeze.md) (`npm run nano:ah:freeze`) — ship claim remains **AF packaged stack**; Wave AI reopened via lab-book §5.
**Wave AI COMPLETE + FROZEN:** AI0 [SESSION PROMOTE](wave-ai-session.md) · AI1 [H-GENPLUS HOLD](formal-hgenplus-genplus.md) · AI1b [H-CAPRENEG HOLD](formal-hcapreneg-capreneg.md) · AI2 [H-CTXPUSH PROMOTE](formal-hctxpush-ctxpush.md) · AI3 [H-SMARTPUSH HOLD](formal-hsmartpush-smartpush.md) · AI4 [H-FASTPUSH PROMOTE](formal-hfastpush-fastpush.md) · AI5 [H-APPPUSH HOLD](formal-happpush-apppush.md) · AI6 [AI-HITL-10 HOLD](wave-ai-hitl.md) · AI7 [AI-REPORT PROMOTE](wave-ai-summary.md) · [paper-lab-wave-ai.md](paper-lab-wave-ai.md) · AI8 [AI-FREEZE PROMOTE](ai-freeze.md) (`npm run nano:ai:freeze`) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AJ reopened via lab-book §6.  
**Wave AJ COMPLETE + FROZEN:** AJ0 [SESSION PROMOTE](wave-aj-session.md) (`npm run nano:aj:session`) · AJ1 [H-GENPEAK PROMOTE](formal-hgenpeak-genpeak.md) (`npm run nano:genpeak`) · AJ2 [H-CTXPEAK PROMOTE](formal-hctxpeak-ctxpeak.md) (`npm run nano:ctxpeak`) · AJ3 [H-SMARTPEAK PROMOTE](formal-hsmartpeak-smartpeak.md) (`npm run nano:smartpeak`) · AJ4 [H-FASTPEAK PROMOTE](formal-hfastpeak-fastpeak.md) (`npm run nano:fastpeak`) · AJ5 [H-APPPEAK PROMOTE](formal-happpeak-apppeak.md) (`npm run nano:apppeak`) · AJ6 [AJ-HITL-10 PROMOTE](wave-aj-hitl.md) (`npm run nano:aj:hitl`) · AJ7 [AJ-REPORT PROMOTE](wave-aj-summary.md) (`npm run nano:aj:report`) · AJ8 [AJ-FREEZE PROMOTE](aj-freeze.md) (`npm run nano:aj:freeze`) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AK reopened via lab-book.  
**Wave AK OPEN:** AK0 [SESSION PROMOTE](wave-ak-session.md) (`npm run nano:ak:session`) · AK1 [H-GENTRUE HOLD](formal-hgentrue-gentrue.md) (`npm run nano:gentrue`) · AK2 [H-CTXMORE PROMOTE](formal-hctxmore-ctxmore.md) (`npm run nano:ctxmore`) · AK3 [H-SMARTMORE PROMOTE](formal-hsmartmore-smartmore.md) (`npm run nano:smartmore`) — octa cite L=9.0 G=9.0 peak; next **AK4 H-FASTMORE**; ship claim remains **AF packaged stack**; ≤5M stays; do not invent Wave AL.
