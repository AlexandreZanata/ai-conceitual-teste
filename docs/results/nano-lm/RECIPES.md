# Official nano-LM recipes (frozen claims)

> Tip-stack: **H-STAG′** / **H-EARLY** / **H-POOL**.  
> Deploy: [H-DEPL](formal-hdepl-policy.md) · **DEPL-Y freeze:** [wave-z-depl-y.md](wave-z-depl-y.md) · Domains: [DOM](formal-hdom-howto.md) / [PROG](formal-hprog-programming.md) / [BTC](formal-hbtc-bitcoin.md).  
> Lab: `.local/pesquisa.md` · Card: [champion-card.md](champion-card.md) · Y: [wave-y-summary.md](wave-y-summary.md) · Z: [wave-z-summary.md](wave-z-summary.md)

## Deploy one-liners (DEPL-Y frozen)

| Goal | L / scope | Use | Do not claim |
|------|-----------|-----|----------------|
| **Fastest serve** | @128 | **H-PACK** + **H-QT** int8 n=1 | ood_long / STREAM |
| **Code-smart (prog)** | @128 | **H-ABS-QPFB2** + **BEAMKV / TCACHE / SCORERAM** | GPFB K=2 / STREAM / KVCACHE-Q |
| **Code-smart (btc)** | @128 | **H-ABS-BPFB** | — |
| **Long context** | L>128 | **H-ROLL / H-SUMCACHE / H-GPFB4-LONG** (+ **H-PFB256**) | STREAM / KVCACHE-Q / GENCACHE / naive CTX |
| **GENC ∘ PFB** | serve genome | **H-ABS-GPFB4** (K=4 only) | GPFB K=2 (**KILL**) |
| **Known-ask HITL** | demo Q&A | **`--wrap` LOOKUP** (`champion-wrap-v0`) — **H-ZWRAP** | open chat LM / ZERR-as-chat |
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

## Policy

**DEPL-Y:** speed@128→PACK/QT; code@128→QPFB2+BEAMKV/TCACHE/SCORERAM; long→ROLL/SUMCACHE/GPFB4-LONG; HITL→H-ZWRAP; CE→H-ZERR≠chat; **REJECT** STREAM / KVCACHE-Q / GENCACHE / GPFB-K=2 / ood_long PACK / MIXD.  
Wave W: [wave-w-summary.md](wave-w-summary.md). Wave X+ KILLs: [wave-x-summary.md](wave-x-summary.md) → [`archive/`](archive/).  
**Wave Y COMPLETE:** [wave-y-summary.md](wave-y-summary.md). **Wave Z COMPLETE:** [wave-z-hitl.md](wave-z-hitl.md) — PFB ≠ interactive LM; wrap + error-bank. **NO-REOPEN:** [lab-freeze.md](lab-freeze.md).
