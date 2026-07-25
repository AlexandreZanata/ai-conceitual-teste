# Official nano-LM recipes (frozen claims)

> Tip-stack: **H-STAG′** / **H-EARLY** / **H-POOL**.  
> Packs are delivery envelopes — not tip replacements.  
> Deploy: [H-DEPL](formal-hdepl-policy.md) · Domain: [H-DOM](formal-hdom-howto.md) · [H-PROG](formal-hprog-programming.md) · [H-BTC](formal-hbtc-bitcoin.md).  
> Lab: `.local/pesquisa.md` · Card: [champion-card.md](champion-card.md)

## Deploy one-liners

| Goal | Use | Do not claim |
|------|-----|----------------|
| **Fastest serve** | **H-PACK** (SERVE/SROUTE path) | OOD elongated to 256 ([XFER2](archive/hxfer2-transfer.md) **KILL**) |
| **Quality@wall serve** | **H-QPACK** (FLAYB) | OOD / transfer (XFER **KILL**) |
| **Cheaper train steps** | **H-TPACK** (PRE3) | e2e without **H-AMORT** n≥4 |
| **Official train tip** | **H-STAG′** (PRE3 via [TIPD](formal-htipd-vs-hstag.md)) | Revert without new formal |
| **E2E train wall** | **H-AMORT** (cache/n + PRE3) | ETRAIN N=1 (purged KILL) |

## Formal evidence

| Recipe | Doc | Wave U / V |
|--------|-----|------------|
| PACK | [formal-hpack-vs-hearly.md](formal-hpack-vs-hearly.md) | [DOM](formal-hdom-howto.md) **PROMOTE** howto; [PROG](formal-hprog-programming.md) **PROMOTE** prog; [BTC](formal-hbtc-bitcoin.md) **PROMOTE** btc; [EFF](formal-heff-efficiency.md) **PROMOTE** wall↓/tok/s↑; [XFER2](archive/hxfer2-transfer.md) **KILL** ood_long; [BUD](formal-hbud-budget.md); [DEPL](formal-hdepl-policy.md) |
| QPACK | [formal-hqpack-vs-hpool.md](formal-hqpack-vs-hpool.md) | [XFER](archive/hxfer-transfer.md) KILL; BUD; DEPL in-dist only |
| TPACK / tip | [formal-htpack-vs-hstag.md](formal-htpack-vs-hstag.md) | [TIPD](formal-htipd-vs-hstag.md) **PROMOTE** STAG′; [AMORT](formal-hamort-vs-hstag.md) |

## Policy (budget + deploy)

Under tip wall/GFLOPs ceilings ([BUD](formal-hbud-budget.md)): PACK + QPACK + TPACK **SURVIVE**.  
Runnable routes ([DEPL](formal-hdepl-policy.md)): speed→PACK (incl. prog/btc @128); quality→QPACK iff in-dist; train→TPACK; REJECT ood_long / QPACK-OOD.  
Domain probe ([DOM](formal-hdom-howto.md)): PACK tip gate holds on procedural howto @128.  
Wave W programming ([H-PROG formal](formal-hprog-programming.md)): PACK tip gate holds on prog @128.  
Wave W bitcoin ([H-BTC formal](formal-hbtc-bitcoin.md)): PACK tip gate holds on btc @128.  
Wave W mix ([H-MIXD](archive/hmixd-mix.md)): formal **KILL** (story teacher_lp regress; tooling purged).  
Wave W efficiency ([H-EFF formal](formal-heff-efficiency.md)): PACK SERVE wall↓ and tok/s↑ vs Phase B on prog+btc at quality floor (recipe freeze; no new genes). TPACK/AMORT remain story-train-only.  
DEPL (D3): speed→PACK still covers prog/btc @128; REJECT unchanged for ood_long / QPACK-OOD.  
Wave W close-out: [wave-w-summary.md](wave-w-summary.md) (**COMPLETE**).  
Wave X+: [H-TCHR formal](formal-htchr-code-teacher.md) / [H-QT formal](formal-hqt-quantize.md) / [H-GENC formal](formal-hgenc-genome.md) **PROMOTE**; [H-RAG](archive/hrag-retrieve.md) / [H-CTX](archive/hctx-long-window.md) / [H-CKD](archive/hckd-code-kd.md) / [H-QCTX](archive/hqctx-born-attn.md) / [H-QCOMP](archive/hqcomp-shadow-kv.md) / [H-Q-QUBITKV](archive/hqubitkv-critical-kv.md) / [H-GENQ-ABS](archive/hgenq-amplitude.md) / [H-DIST](archive/hdist-distill.md) / [H-Q-SLOT](archive/hqslot-slots.md) / [H-Q-INTERF](archive/hqinterf-interference.md) / [H-ABS-REV](archive/habsrev-reverse.md) / [H-Q-ANNEAL](archive/hqanneal-anneal.md) / [H-ABS-SPIRAL](archive/habsspiral-spiral.md) / [H-Q-GROVER](archive/hqgrover-grover.md) / [H-Q-TUNNEL](archive/hqtunnel-tunnel.md) / [H-Q-BELL](archive/hqbell-bell.md) **KILL**; next **H-ABS-ORACLE1** (`.local/pesquisa.md`).
