# Official nano-LM recipes (frozen claims)

> Tip-stack: **H-STAG′** / **H-EARLY** / **H-POOL**.  
> Deploy: [H-DEPL](formal-hdepl-policy.md) · Domains: [DOM](formal-hdom-howto.md) / [PROG](formal-hprog-programming.md) / [BTC](formal-hbtc-bitcoin.md).  
> Lab: `.local/pesquisa.md` (**Wave Y**) · Card: [champion-card.md](champion-card.md) · Y: [wave-y-summary.md](wave-y-summary.md) · X+: [wave-x-summary.md](wave-x-summary.md)

## Deploy one-liners

| Goal | Use | Do not claim |
|------|-----|----------------|
| **Fastest serve** | **H-PACK** + **H-QT** int8 n=1 | ood_long / OOD@256 without Wave Y formal |
| **Code-smart serve (prog)** | **H-ABS-QPFB2** + cache stack (+ **H-PFB256** / **H-ROLL** / **H-SUMCACHE** long) | CBON / CSAFE-max-story / GPFB K=2 / STREAM |
| **Code-smart serve (btc)** | **H-ABS-BPFB** | — |
| **GENC ∘ PFB** | **H-ABS-GPFB4** (K=4 only) | GPFB K=2 (**KILL**) |
| **Cheaper train steps** | **H-TPACK** + **H-AMORT** | ETRAIN N=1 |
| **Quality@wall (in-harness)** | **H-QPACK** | QPACK OOD (XFER **KILL**) |

## Formal evidence (survivors)

| Recipe | Formal |
|--------|--------|
| PACK / domains / EFF | [hpack](formal-hpack-vs-hearly.md) · [prog](formal-hprog-programming.md) · [btc](formal-hbtc-bitcoin.md) · [eff](formal-heff-efficiency.md) |
| QT | [formal-hqt-quantize.md](formal-hqt-quantize.md) |
| PFB family | [pfb](formal-hpfb-pfb.md) · [pfb2](formal-hpfb2-pfb2.md) · [qpfb2](formal-hqpfb2-qpfb2.md) · [bpfb](formal-hbpfb-bpfb.md) · [gpfb4](formal-hgpfb4-gpfb4.md) |
| Wave Y cache / long | [beamkv](formal-hbeamkv-beamkv.md) · [tcache](formal-htcache-tcache.md) · [scoreram](formal-hscoreram-scoreram.md) · [pfb256](formal-hpfb256-pfb256.md) · [roll](formal-hroll-roll.md) · [sumcache](formal-hsumcache-sumcache.md) |
| TCHR / GENC | [tchr](formal-htchr-code-teacher.md) · [genc](formal-hgenc-genome.md) |
| Train | [tpack](formal-htpack-vs-hstag.md) · [amort](formal-hamort-vs-hstag.md) · [TIPD](formal-htipd-vs-hstag.md) |

## Policy

DEPL: speed→PACK/QT; code-smart→QPFB2/BPFB (+BEAMKV/TCACHE/SCORERAM/PFB256/ROLL/SUMCACHE/GPFB4-LONG); GENC∘PFB→GPFB4; quality→QPACK in-dist; **REJECT** ood_long / QPACK-OOD / revived X+ KILLs / STREAM / KVCACHE-Q / GENCACHE.
Wave W: [wave-w-summary.md](wave-w-summary.md). Wave X+ KILLs: [wave-x-summary.md](wave-x-summary.md) → [`archive/`](archive/).
**Wave Y COMPLETE:** [wave-y-summary.md](wave-y-summary.md). **Wave Z ACTIVE:** [wave-z-summary.md](wave-z-summary.md) — Z1 HITL-10 **FAIL**; next Z2 MANUAL×10 — [wave-z-hitl-z1.md](wave-z-hitl-z1.md).
