# Nano Student + Teacher — Research Agenda

> Lab: `nano_lm/`. Caps: ≤80 / ≤200 / cyclo ≤10.  
> EvoGen: frozen [`archive/evogen/`](archive/evogen/README.md).

## Tips / recipes

**H-STAG′** · **H-EARLY** · **H-POOL**  
Serve-fast: **H-PACK** + **QT**. Code-smart: **QPFB2** / **BPFB** / **GPFB4**. Long: **ROLL** / SUMCACHE / GPFB4-LONG. Train: **TPACK**+**AMORT**.  
HITL: **H-ZWRAP** (+ **H-WRAPBANK** + **H-SEMWRAP**). Story-CE: **H-ZERR** ≠ chat.  
**DEPL-Y:** [`wave-z-depl-y.md`](results/nano-lm/wave-z-depl-y.md) · One-pager: [`RECIPES.md`](results/nano-lm/RECIPES.md) · Card: [`champion-card.md`](results/nano-lm/champion-card.md).

## Waves

| Wave | Status | Summary |
|------|--------|---------|
| W | **COMPLETE** | [wave-w-summary.md](results/nano-lm/wave-w-summary.md) |
| X+ | **COMPLETE** | [wave-x-summary.md](results/nano-lm/wave-x-summary.md) — PFB family **PROMOTE**; QI/ABS **KILL** |
| **Y** | **COMPLETE** | [wave-y-summary.md](results/nano-lm/wave-y-summary.md) — PFB256/ROLL/SUMCACHE/GPFB4-LONG **PROMOTE**; STREAM/KVCACHE-Q/GENCACHE **KILL** |
| **Z** | **COMPLETE** | [wave-z-hitl.md](results/nano-lm/wave-z-hitl.md) — PFB ≠ interactive LM; **H-ZWRAP** · freeze [lab-freeze.md](results/nano-lm/lab-freeze.md) |
| **AA** | **COMPLETE** + **FROZEN** | AA0–AA6 (**AA-FREEZE PROMOTE**) — [wave-aa-summary.md](results/nano-lm/wave-aa-summary.md) · [aa-freeze.md](results/nano-lm/aa-freeze.md) |
| **AB** | **COMPLETE + FROZEN** | AB0–AB7 **PROMOTE** · [ab-freeze.md](results/nano-lm/ab-freeze.md) · [wave-ab-summary.md](results/nano-lm/wave-ab-summary.md) |
| **AC** | **COMPLETE + FROZEN** | [ac-freeze.md](results/nano-lm/ac-freeze.md) · [wave-ac-summary.md](results/nano-lm/wave-ac-summary.md) |
| **AD** | **COMPLETE + FROZEN** | [ad-freeze.md](results/nano-lm/ad-freeze.md) · [wave-ad-summary.md](results/nano-lm/wave-ad-summary.md) |
| **AE** | **COMPLETE + FROZEN** | [wave-ae-summary.md](results/nano-lm/wave-ae-summary.md) · [ae-freeze.md](results/nano-lm/ae-freeze.md) · [paper-lab-wave-ae.md](results/nano-lm/paper-lab-wave-ae.md) |
| **AF** | **COMPLETE + FROZEN** | ship claim **AF packaged stack** · [af-freeze.md](results/nano-lm/af-freeze.md) · [wave-af-summary.md](results/nano-lm/wave-af-summary.md) |
| **AG** | **COMPLETE + FROZEN** | [ag-freeze.md](results/nano-lm/ag-freeze.md) · [wave-ag-summary.md](results/nano-lm/wave-ag-summary.md) |
| **AH** | **COMPLETE + FROZEN** | [ah-freeze.md](results/nano-lm/ah-freeze.md) · [wave-ah-summary.md](results/nano-lm/wave-ah-summary.md) |
| **AI** | **COMPLETE + FROZEN** | [ai-freeze.md](results/nano-lm/ai-freeze.md) · [wave-ai-summary.md](results/nano-lm/wave-ai-summary.md) |
| **AJ** | **COMPLETE + FROZEN** | AJ0–AJ8 **PROMOTE** · [aj-freeze.md](results/nano-lm/aj-freeze.md) · [wave-aj-summary.md](results/nano-lm/wave-aj-summary.md) · [formal-hajfreeze-aj-freeze.md](results/nano-lm/formal-hajfreeze-aj-freeze.md) |
| **AK** | **COMPLETE + FROZEN** | AK0…AK7 DONE · AK8 [AK-FREEZE PROMOTE](results/nano-lm/ak-freeze.md) (`npm run nano:ak:freeze`) — ship remains **AF packaged stack**; ≤5M stays; Wave AL reopened via lab-book |
| **AL** | **COMPLETE + FROZEN** | AL0 [SESSION PROMOTE](results/nano-lm/wave-al-session.md) · AL1 [H-GENFRESH HOLD](results/nano-lm/formal-hgenfresh-genfresh.md) · AL2 [H-CTXFRESH PROMOTE](results/nano-lm/formal-hctxfresh-ctxfresh.md) · AL3 [H-SMARTFRESH PROMOTE](results/nano-lm/formal-hsmartfresh-smartfresh.md) · AL4 [H-FASTFRESH PROMOTE](results/nano-lm/formal-hfastfresh-fastfresh.md) · AL5 [H-APPFRESH PROMOTE](results/nano-lm/formal-happfresh-appfresh.md) · AL6 [AL-HITL-10 PROMOTE](results/nano-lm/wave-al-hitl.md) · AL7 [AL-REPORT PROMOTE](results/nano-lm/wave-al-summary.md) · AL8 [AL-FREEZE PROMOTE](results/nano-lm/al-freeze.md) (`npm run nano:al:freeze`) · [formal-halfreeze-al-freeze.md](results/nano-lm/formal-halfreeze-al-freeze.md) — ship remains **AF packaged stack**; ≤5M stays; Wave AM reopened via lab-book |
| **AM** | **COMPLETE + FROZEN** | AM0 [SESSION PROMOTE](results/nano-lm/wave-am-session.md) · AM1 [H-GENTRUTH HOLD](results/nano-lm/formal-hgentruth-gentruth.md) · AM2 [H-CTXNEXT PROMOTE](results/nano-lm/formal-hctxnext-ctxnext.md) (`npm run nano:ctxnext`) — L_eff 213147 · AM3 [H-SMARTNEXT PROMOTE](results/nano-lm/formal-hsmartnext-smartnext.md) (`npm run nano:smartnext`) — cite+gen 9.0/9.0 · AM4 [H-FASTNEXT PROMOTE](results/nano-lm/formal-hfastnext-fastnext.md) (`npm run nano:fastnext`) — hot 0.17≪FASTFRESH · AM5 [H-APPNEXT PROMOTE](results/nano-lm/formal-happnext-appnext.md) (`npm run nano:appnext`) — SERVE gen 9.0 · AM6 [AM-HITL-10 PROMOTE](results/nano-lm/wave-am-hitl.md) (`npm run nano:am:hitl`) — L/G 9.0/9.0 · AM7 [AM-REPORT PROMOTE](results/nano-lm/wave-am-summary.md) (`npm run nano:am:report`) · [paper-lab-wave-am.md](results/nano-lm/paper-lab-wave-am.md); AM8 [AM-FREEZE PROMOTE](results/nano-lm/am-freeze.md) (`npm run nano:am:freeze`) · [formal-hamfreeze-am-freeze.md](results/nano-lm/formal-hamfreeze-am-freeze.md) — ship remains **AF packaged stack**; ≤5M stays; Wave AN reopened via lab-book |
| **AN** | **OPEN** | AN0 [SESSION PROMOTE](results/nano-lm/wave-an-session.md) (`npm run nano:an:session`) · AN1 [H-GENEDGE HOLD](results/nano-lm/formal-hgenedge-genedge.md) (`npm run nano:genedge`) — ablated gen 4.0; peak_only_lift; next AN2 H-CTXEDGE |

Teachers: TinyStories-33M + `bigcode/tiny_starcoder_py` ([TCHR](results/nano-lm/formal-htchr-code-teacher.md)).  
KILL tooling purged → [`results/nano-lm/archive/`](results/nano-lm/archive/).
