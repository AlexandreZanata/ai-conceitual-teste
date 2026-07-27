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
| Wave AK4 H-FASTMORE | [formal-hfastmore-fastmore.md](formal-hfastmore-fastmore.md) **PROMOTE** (`npm run nano:fastmore`) — GENTRUE peak-fast; hot 3.8 < FASTPEAK 5.0; next AK5 H-APPMORE |
| Wave AK5 H-APPMORE | [formal-happmore-appmore.md](formal-happmore-appmore.md) **PROMOTE** (`npm run nano:appmore`) — 3 apps + DEPL-AK; L=8.33 G=9.0; next AK6 AK-HITL-10 |
| Wave AK6 AK-HITL-10 | [wave-ak-hitl.md](wave-ak-hitl.md) **PROMOTE** (`npm run nano:ak:hitl`) — final dual-arm L=9.0 G=9.0; next AK7 AK-REPORT |
| Wave AK7 AK-REPORT | [wave-ak-summary.md](wave-ak-summary.md) **PROMOTE** (`npm run nano:ak:report`) — public closeout + paper-lab |
| Wave AK8 AK-FREEZE | [ak-freeze.md](ak-freeze.md) · [formal-hakfreeze-ak-freeze.md](formal-hakfreeze-ak-freeze.md) **PROMOTE** (`npm run nano:ak:freeze`) — COMPLETE+FROZEN; no Wave AL without reopen |
| Wave AL0 SESSION | [wave-al-session.md](wave-al-session.md) **PROMOTE** (`npm run nano:al:session`) — freeze 10 held-out ≠ AB…AK; next AL1 H-GENFRESH |
| Wave AL1 H-GENFRESH | [formal-hgenfresh-genfresh.md](formal-hgenfresh-genfresh.md) **HOLD** (`npm run nano:genfresh`) — ablated gen 4.0; peak_only_lift; next AL2 H-CTXFRESH |
| Wave AL2 H-CTXFRESH | [formal-hctxfresh-ctxfresh.md](formal-hctxfresh-ctxfresh.md) **PROMOTE** (`npm run nano:ctxfresh`) — nona K=19; L_eff 200344 > CTXMORE; next AL3 H-SMARTFRESH |
| Wave AL3 H-SMARTFRESH | [formal-hsmartfresh-smartfresh.md](formal-hsmartfresh-smartfresh.md) **PROMOTE** (`npm run nano:smartfresh`) — nona-hop cite+gen; L/G 9.0/9.0; next AL4 H-FASTFRESH |
| Wave AL4 H-FASTFRESH | [formal-hfastfresh-fastfresh.md](formal-hfastfresh-fastfresh.md) **PROMOTE** (`npm run nano:fastfresh`) — cue-first peak-fast; hot ~0.2≪FASTMORE 3.8; next AL5 H-APPFRESH |
| Wave AL5 H-APPFRESH | [formal-happfresh-appfresh.md](formal-happfresh-appfresh.md) **PROMOTE** (`npm run nano:appfresh`) — 3 apps + DEPL-AL; L/G 8.33/9.0; next AL6 AL-HITL-10 |
| Wave AL6 AL-HITL-10 | [wave-al-hitl.md](wave-al-hitl.md) **PROMOTE** (`npm run nano:al:hitl`) — final dual-arm L/G 9.0/9.0; next AL7 AL-REPORT |
| Wave AL7 AL-REPORT | [wave-al-summary.md](wave-al-summary.md) · [paper-lab-wave-al.md](paper-lab-wave-al.md) **PROMOTE** (`npm run nano:al:report`) — public summary + paper-lab; next AL8 AL-FREEZE |
| Wave AL8 AL-FREEZE | [al-freeze.md](al-freeze.md) · [formal-halfreeze-al-freeze.md](formal-halfreeze-al-freeze.md) **PROMOTE** (`npm run nano:al:freeze`) — COMPLETE+FROZEN; Wave AM reopened via lab-book |
| Wave AM0 SESSION | [wave-am-session.md](wave-am-session.md) **PROMOTE** (`npm run nano:am:session`) — freeze 10 held-out ≠ AB…AL; next AM1 H-GENTRUTH |
| Wave AM1 H-GENTRUTH | [formal-hgentruth-gentruth.md](formal-hgentruth-gentruth.md) **HOLD** (`npm run nano:gentruth`) — ablated gen 4.0; peak_only_lift; next AM2 H-CTXNEXT |
| Wave AM2 H-CTXNEXT | [formal-hctxnext-ctxnext.md](formal-hctxnext-ctxnext.md) **PROMOTE** (`npm run nano:ctxnext`) — deca K=21; L_eff 213147 > CTXFRESH; next AM3 H-SMARTNEXT |
| Wave AM3 H-SMARTNEXT | [formal-hsmartnext-smartnext.md](formal-hsmartnext-smartnext.md) **PROMOTE** (`npm run nano:smartnext`) — deca-hop cite+gen; L/G 9.0/9.0; next AM4 H-FASTNEXT |
| Wave AM4 H-FASTNEXT | [formal-hfastnext-fastnext.md](formal-hfastnext-fastnext.md) **PROMOTE** (`npm run nano:fastnext`) — hot 0.17≪FASTFRESH 0.2; next AM5 H-APPNEXT |
| Wave AM5 H-APPNEXT | [formal-happnext-appnext.md](formal-happnext-appnext.md) **PROMOTE** (`npm run nano:appnext`) — 3 apps+DEPL-AM; SERVE gen 9.0; next AM6 AM-HITL-10 |
| Wave AM6 AM-HITL-10 | [wave-am-hitl.md](wave-am-hitl.md) **PROMOTE** (`npm run nano:am:hitl`) — final dual-arm L/G 9.0/9.0; next AM7 AM-REPORT |
| Wave AM7 AM-REPORT | [wave-am-summary.md](wave-am-summary.md) · [paper-lab-wave-am.md](paper-lab-wave-am.md) **PROMOTE** (`npm run nano:am:report`) — public summary + anti-FP; next AM8 AM-FREEZE |
| Wave AM8 AM-FREEZE | [am-freeze.md](am-freeze.md) · [formal-hamfreeze-am-freeze.md](formal-hamfreeze-am-freeze.md) **PROMOTE** (`npm run nano:am:freeze`) — COMPLETE+FROZEN; no Wave AN without reopen |
| Wave AN0 SESSION | [wave-an-session.md](wave-an-session.md) **PROMOTE** (`npm run nano:an:session`) — freeze 10 held-out ≠ AB…AM; next AN1 H-GENEDGE |
| Wave AN1 H-GENEDGE | [formal-hgenedge-genedge.md](formal-hgenedge-genedge.md) **HOLD** (`npm run nano:genedge`) — ablated gen 4.0; peak_only_lift; next AN2 H-CTXEDGE |
| Wave AN2 H-CTXEDGE | [formal-hctxedge-ctxedge.md](formal-hctxedge-ctxedge.md) **PROMOTE** (`npm run nano:ctxedge`) — L_eff 242448 > CTXNEXT 213147; next AN3 H-SMARTEDGE |
| Wave AN3 H-SMARTEDGE | [formal-hsmartedge-smartedge.md](formal-hsmartedge-smartedge.md) **PROMOTE** (`npm run nano:smartedge`) — undeca-hop cite+gen 9.0/9.0; next AN4 H-FASTEDGE |
| Wave AN4 H-FASTEDGE | [formal-hfastedge-fastedge.md](formal-hfastedge-fastedge.md) **PROMOTE** (`npm run nano:fastedge`) — hot 0.05≪FASTNEXT 0.17; next AN5 H-APPEDGE |
| Wave AN5 H-APPEDGE | [formal-happedge-appedge.md](formal-happedge-appedge.md) **PROMOTE** (`npm run nano:appedge`) — 3 apps+DEPL-AN; SERVE gen 9.0; next AN6 AN-HITL-10 |
| Wave AN6 AN-HITL-10 | [wave-an-hitl.md](wave-an-hitl.md) **PROMOTE** (`npm run nano:an:hitl`) — final dual-arm L/G 9.0/9.0; next AN7 AN-REPORT |
| Wave AN7 AN-REPORT | [wave-an-summary.md](wave-an-summary.md) **PROMOTE** (`npm run nano:an:report`) · [paper-lab-wave-an.md](paper-lab-wave-an.md); next AN8 AN-FREEZE |
| Wave AN8 AN-FREEZE | [an-freeze.md](an-freeze.md) · [formal-hanfreeze-an-freeze.md](formal-hanfreeze-an-freeze.md) **PROMOTE** (`npm run nano:an:freeze`) — COMPLETE+FROZEN; no Wave AO without reopen |
| Wave AO0 SESSION | [wave-ao-session.md](wave-ao-session.md) **PROMOTE** (`npm run nano:ao:session`) — freeze 10 held-out ≠ AB…AN; next AO1 H-GENCORE |
| Wave AO1 H-GENCORE | [formal-hgencore-gencore.md](formal-hgencore-gencore.md) **HOLD** (`npm run nano:gencore`) — ablated gen 4.0; peak_only_lift; next AO2 H-CTXCORE |
| Wave AO2 H-CTXCORE | [formal-hctxcore-ctxcore.md](formal-hctxcore-ctxcore.md) **PROMOTE** (`npm run nano:ctxcore`) — dodeca K=25; L_eff 253105 > CTXEDGE; next AO3 H-SMARTCORE |
| Wave AO3 H-SMARTCORE | [formal-hsmartcore-smartcore.md](formal-hsmartcore-smartcore.md) **PROMOTE** (`npm run nano:smartcore`) — dodeca-hop cite 10/10; gen peak 9.0; next AO4 H-FASTCORE |
| Wave AO4 H-FASTCORE | [formal-hfastcore-fastcore.md](formal-hfastcore-fastcore.md) **PROMOTE** (`npm run nano:fastcore`) — warm wall 0.06 < FASTEDGE 0.10; next AO5 H-APPCORE |
| Wave AO5 H-APPCORE | [formal-happcore-appcore.md](formal-happcore-appcore.md) **PROMOTE** (`npm run nano:appcore`) — 3 apps+DEPL-AO; SERVE gen 9.0; next AO6 AO-HITL-10 |
| Wave AO6 AO-HITL-10 | [wave-ao-hitl.md](wave-ao-hitl.md) **PROMOTE** (`npm run nano:ao:hitl`) — final dual-arm L/G 9.0/9.0; next AO7 AO-REPORT |
| Wave AO7 AO-REPORT | [wave-ao-summary.md](wave-ao-summary.md) **PROMOTE** (`npm run nano:ao:report`) · [paper-lab-wave-ao.md](paper-lab-wave-ao.md); next AO8 AO-FREEZE |
| Wave AO8 AO-FREEZE | [ao-freeze.md](ao-freeze.md) · [formal-haofreeze-ao-freeze.md](formal-haofreeze-ao-freeze.md) **PROMOTE** (`npm run nano:ao:freeze`) — COMPLETE+FROZEN; Wave AP reopened via lab-book |
| Wave AP0 SESSION | [wave-ap-session.md](wave-ap-session.md) **PROMOTE** (`npm run nano:ap:session`) — freeze 10 held-out ≠ AB…AO; next AP1 H-GENBASE |
| Wave AP1 H-GENBASE | [formal-hgenbase-genbase.md](formal-hgenbase-genbase.md) **HOLD** (`npm run nano:genbase`) — ablated gen 4.0; peak_only_lift; next AP2 H-CTXBASE |
| Wave AP2 H-CTXBASE | [formal-hctxbase-ctxbase.md](formal-hctxbase-ctxbase.md) **PROMOTE** (`npm run nano:ctxbase`) — L_eff 274198 > CTXCORE; next AP3 H-SMARTBASE |
| Wave AP3 H-SMARTBASE | [formal-hsmartbase-smartbase.md](formal-hsmartbase-smartbase.md) **PROMOTE** (`npm run nano:smartbase`) — L/G 9.0/9.0; next AP4 H-FASTBASE |
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
**Wave AK COMPLETE + FROZEN:** AK0 [SESSION PROMOTE](wave-ak-session.md) · AK1 [H-GENTRUE HOLD](formal-hgentrue-gentrue.md) · AK2 [H-CTXMORE PROMOTE](formal-hctxmore-ctxmore.md) · AK3 [H-SMARTMORE PROMOTE](formal-hsmartmore-smartmore.md) · AK4 [H-FASTMORE PROMOTE](formal-hfastmore-fastmore.md) · AK5 [H-APPMORE PROMOTE](formal-happmore-appmore.md) · AK6 [AK-HITL-10 PROMOTE](wave-ak-hitl.md) (`npm run nano:ak:hitl`) · AK7 [AK-REPORT PROMOTE](wave-ak-summary.md) (`npm run nano:ak:report`) · AK8 [AK-FREEZE PROMOTE](ak-freeze.md) (`npm run nano:ak:freeze`) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AL reopened via lab-book.
**Wave AL COMPLETE + FROZEN:** AL0 [SESSION PROMOTE](wave-al-session.md) (`npm run nano:al:session`) · AL1 [H-GENFRESH HOLD](formal-hgenfresh-genfresh.md) (`npm run nano:genfresh`) · AL2 [H-CTXFRESH PROMOTE](formal-hctxfresh-ctxfresh.md) (`npm run nano:ctxfresh`) — L_eff 200344; AL3 [H-SMARTFRESH PROMOTE](formal-hsmartfresh-smartfresh.md) (`npm run nano:smartfresh`) — cite+gen 9.0/9.0; AL4 [H-FASTFRESH PROMOTE](formal-hfastfresh-fastfresh.md) (`npm run nano:fastfresh`) — hot ~0.2≪FASTMORE; AL5 [H-APPFRESH PROMOTE](formal-happfresh-appfresh.md) (`npm run nano:appfresh`) — apps+DEPL-AL; AL6 [AL-HITL-10 PROMOTE](wave-al-hitl.md) (`npm run nano:al:hitl`) — L/G 9.0/9.0; AL7 [AL-REPORT PROMOTE](wave-al-summary.md) (`npm run nano:al:report`) · [paper-lab-wave-al.md](paper-lab-wave-al.md); AL8 [AL-FREEZE PROMOTE](al-freeze.md) (`npm run nano:al:freeze`) · [formal-halfreeze-al-freeze.md](formal-halfreeze-al-freeze.md) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AM reopened via lab-book.  
**Wave AM COMPLETE + FROZEN:** AM0 [SESSION PROMOTE](wave-am-session.md) (`npm run nano:am:session`) · AM1 [H-GENTRUTH HOLD](formal-hgentruth-gentruth.md) (`npm run nano:gentruth`) — ablated gen 4.0; peak_only_lift · AM2 [H-CTXNEXT PROMOTE](formal-hctxnext-ctxnext.md) (`npm run nano:ctxnext`) — L_eff 213147 · AM3 [H-SMARTNEXT PROMOTE](formal-hsmartnext-smartnext.md) (`npm run nano:smartnext`) — cite+gen 9.0/9.0 · AM4 [H-FASTNEXT PROMOTE](formal-hfastnext-fastnext.md) (`npm run nano:fastnext`) — hot 0.17≪FASTFRESH · AM5 [H-APPNEXT PROMOTE](formal-happnext-appnext.md) (`npm run nano:appnext`) — SERVE gen 9.0 · AM6 [AM-HITL-10 PROMOTE](wave-am-hitl.md) (`npm run nano:am:hitl`) — L/G 9.0/9.0 · AM7 [AM-REPORT PROMOTE](wave-am-summary.md) (`npm run nano:am:report`) · [paper-lab-wave-am.md](paper-lab-wave-am.md); AM8 [AM-FREEZE PROMOTE](am-freeze.md) (`npm run nano:am:freeze`) · [formal-hamfreeze-am-freeze.md](formal-hamfreeze-am-freeze.md) — ship claim remains **AF packaged stack**; ≤5M stays; Wave AN reopened via lab-book.
**Wave AN COMPLETE + FROZEN:** AN0 [SESSION PROMOTE](wave-an-session.md) (`npm run nano:an:session`) — freeze 10 held-out ≠ AB…AM · AN1 [H-GENEDGE HOLD](formal-hgenedge-genedge.md) (`npm run nano:genedge`) — ablated gen 4.0; peak_only_lift · AN2 [H-CTXEDGE PROMOTE](formal-hctxedge-ctxedge.md) (`npm run nano:ctxedge`) — L_eff 242448 · AN3 [H-SMARTEDGE PROMOTE](formal-hsmartedge-smartedge.md) (`npm run nano:smartedge`) — cite+gen 9.0/9.0 · AN4 [H-FASTEDGE PROMOTE](formal-hfastedge-fastedge.md) (`npm run nano:fastedge`) — hot 0.05≪0.17 · AN5 [H-APPEDGE PROMOTE](formal-happedge-appedge.md) (`npm run nano:appedge`) — SERVE gen 9.0 · AN6 [AN-HITL-10 PROMOTE](wave-an-hitl.md) (`npm run nano:an:hitl`) — L/G 9.0/9.0 · AN7 [AN-REPORT PROMOTE](wave-an-summary.md) (`npm run nano:an:report`) · [paper-lab-wave-an.md](paper-lab-wave-an.md); AN8 [AN-FREEZE PROMOTE](an-freeze.md) (`npm run nano:an:freeze`) · [formal-hanfreeze-an-freeze.md](formal-hanfreeze-an-freeze.md) — COMPLETE+FROZEN; no Wave AO without reopen.
**Wave AO COMPLETE + FROZEN:** AO0 [SESSION PROMOTE](wave-ao-session.md) (`npm run nano:ao:session`) — freeze 10 held-out ≠ AB…AN · AO1 [H-GENCORE HOLD](formal-hgencore-gencore.md) (`npm run nano:gencore`) — ablated gen 4.0; peak_only_lift · AO2 [H-CTXCORE PROMOTE](formal-hctxcore-ctxcore.md) (`npm run nano:ctxcore`) — L_eff 253105 > CTXEDGE · AO3 [H-SMARTCORE PROMOTE](formal-hsmartcore-smartcore.md) (`npm run nano:smartcore`) — L/G 9.0/9.0 · AO4 [H-FASTCORE PROMOTE](formal-hfastcore-fastcore.md) (`npm run nano:fastcore`) — warm 0.06 < FASTEDGE 0.10 · AO5 [H-APPCORE PROMOTE](formal-happcore-appcore.md) (`npm run nano:appcore`) — SERVE gen 9.0 · AO6 [AO-HITL-10 PROMOTE](wave-ao-hitl.md) (`npm run nano:ao:hitl`) — L/G 9.0/9.0 · AO7 [AO-REPORT PROMOTE](wave-ao-summary.md) (`npm run nano:ao:report`) · [paper-lab-wave-ao.md](paper-lab-wave-ao.md); AO8 [AO-FREEZE PROMOTE](ao-freeze.md) (`npm run nano:ao:freeze`) · [formal-haofreeze-ao-freeze.md](formal-haofreeze-ao-freeze.md) — ship claim remains **AF packaged stack**; ≤5M stays; no Wave AP without reopen.
**Wave AP OPEN:** AP0 [SESSION PROMOTE](wave-ap-session.md) (`npm run nano:ap:session`) — freeze 10 held-out ≠ AB…AO · AP1 [H-GENBASE HOLD](formal-hgenbase-genbase.md) (`npm run nano:genbase`) — ablated gen 4.0; peak_only_lift · AP2 [H-CTXBASE PROMOTE](formal-hctxbase-ctxbase.md) (`npm run nano:ctxbase`) — L_eff 274198 > CTXCORE · AP3 [H-SMARTBASE PROMOTE](formal-hsmartbase-smartbase.md) (`npm run nano:smartbase`) — L/G 9.0/9.0; next AP4 H-FASTBASE.
