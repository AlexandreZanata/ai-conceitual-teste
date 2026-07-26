# Champion card — tip-stack + official recipes

> Compose closed (**H-SYS** / **H-JOINT** / **H-CACHE** / **H-CAP** **KILL**).  
> Deploy: [RECIPES.md](RECIPES.md). Lab: `.local/pesquisa.md` (**Wave Y COMPLETE** — GPFB4-LONG **PROMOTE**; next **Wave Z**).  
> Wave X+ close-out: [wave-x-summary.md](wave-x-summary.md) · Wave Y: [wave-y-summary.md](wave-y-summary.md).

## Official tips

| Tip | Role | Formal |
|-----|------|--------|
| **H-STAG′** | Train (PRE3/RETIP) | [TIPD](formal-htipd-vs-hstag.md) · parent [H-STAG](formal-hstag-vs-hcurl2.md) |
| **H-EARLY** | Decode speed | [formal-hearly-vs-b4.md](formal-hearly-vs-b4.md) |
| **H-POOL** | Decode quality@wall | [formal-hpool-vs-hdeckl.md](formal-hpool-vs-hdeckl.md) |

## Official recipes (priority order)

| # | Recipe | Pack | Evidence |
|---|--------|------|----------|
| 1 | **Serve-fast** | **H-PACK** (+ **H-QT** int8) | [PACK](formal-hpack-vs-hearly.md) · [DOM](formal-hdom-howto.md) · [PROG](formal-hprog-programming.md) · [BTC](formal-hbtc-bitcoin.md) · [EFF](formal-heff-efficiency.md) · [QT](formal-hqt-quantize.md) · [DEPL](formal-hdepl-policy.md) |
| 2 | **Code-smart serve** | **H-ABS-QPFB2** (+ **H-BEAMKV** / **H-TCACHE** / **H-SCORERAM** / **H-PFB256** / **H-ROLL** / **H-SUMCACHE** / **H-GPFB4-LONG**) | [PFB](formal-hpfb-pfb.md) · [PFB2](formal-hpfb2-pfb2.md) · [QPFB2](formal-hqpfb2-qpfb2.md) · [BPFB](formal-hbpfb-bpfb.md) · [GPFB4](formal-hgpfb4-gpfb4.md) · [BEAMKV](formal-hbeamkv-beamkv.md) · [TCACHE](formal-htcache-tcache.md) · [SCORERAM](formal-hscoreram-scoreram.md) · [PFB256](formal-hpfb256-pfb256.md) · [ROLL](formal-hroll-roll.md) · [SUMCACHE](formal-hsumcache-sumcache.md) · [GPFB4-LONG](formal-hgpfb4long-gpfb4long.md) |
| 3 | **Train-step / e2e** | **H-TPACK** + **AMORT** | [tpack](formal-htpack-vs-hstag.md) · [amort](formal-hamort-vs-hstag.md) · [TIPD](formal-htipd-vs-hstag.md) |
| 4 | **Serve-quality** (in-harness) | **H-QPACK** | [formal](formal-hqpack-vs-hpool.md) · OOD XFER **KILL** → [archive](archive/hxfer-transfer.md) |

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
npm run nano:bpfb && npm run nano:formal:hbpfb
npm run nano:gpfb4 && npm run nano:formal:hgpfb4
npm run nano:tchr && npm run nano:formal:htchr
npm run nano:genc && npm run nano:formal:hgenc
```

## Waves

Wave W **COMPLETE** — [wave-w-summary.md](wave-w-summary.md) (PROG/BTC/EFF **PROMOTE**; MIXD **KILL**).  
Wave X+ **COMPLETE** — [wave-x-summary.md](wave-x-summary.md) (PFB family **PROMOTE**; RAG/CTX/Q*/… **KILL** → [`archive/`](archive/)).  
**Wave Y COMPLETE** — [wave-y-summary.md](wave-y-summary.md) (GPFB4-LONG **PROMOTE**; STREAM/KVCACHE-Q/GENCACHE **KILL**). Next: **Wave Z**.

Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../../NANO-STUDENT-AGENDA.md).
