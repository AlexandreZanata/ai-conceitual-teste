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
| **AE** | **OPEN** | AE0–AE3 [FASTMAX PROMOTE](results/nano-lm/formal-hfastmax-fastmax.md) · next H-APPMAX |

Teachers: TinyStories-33M + `bigcode/tiny_starcoder_py` ([TCHR](results/nano-lm/formal-htchr-code-teacher.md)).  
KILL tooling purged → [`results/nano-lm/archive/`](results/nano-lm/archive/).
