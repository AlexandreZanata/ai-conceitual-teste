# Wave Z — DEPL-Y freeze (**DONE** — PROMOTE)

> Lab: `.local/pesquisa.md` §8 #4 · Evidence: Wave Y formals + Z4 HITL  
> Policy module: `nano_lm/src/depl_y_ops.py` · Runner: `npm run nano:z:depl-y`

## Decision

**PROMOTE** — deploy routes frozen on [RECIPES.md](RECIPES.md) + [champion-card.md](champion-card.md).

## Frozen routes (128 vs long)

| Goal | Use | Never |
|------|-----|-------|
| Fastest @128 | **H-PACK** + **H-QT** int8 n=1 | ood_long / STREAM |
| Code-smart @128 | **H-ABS-QPFB2** + **BEAMKV / TCACHE / SCORERAM** | GPFB K=2 · STREAM |
| Code-smart @btc | **H-ABS-BPFB** | — |
| Long ctx (L>128) | **H-ROLL / H-SUMCACHE / H-GPFB4-LONG** (+ **H-PFB256**) | STREAM · KVCACHE-Q · GENCACHE · naive CTX |
| Known-ask HITL | **`--wrap` LOOKUP** (`champion-wrap-v0`) — **H-ZWRAP** | open chat LM |
| Story-safe CE | **H-ZERR** (`zerr-qpfb2-v0`) | ZERR-as-chat |
| Train steps | **H-TPACK** + **H-AMORT** | MIXD |
| Quality@wall | **H-QPACK** in-dist only | QPACK OOD |

## L-gate

| Intent | L | Result |
|--------|--:|--------|
| `code_128` | ≤128 | route OK |
| `code_128` | >128 | **REJECT** → use `long_ctx` |
| `long_ctx` | ≤128 | **REJECT** → use `code_128` |
| `speed_128` | >128 | **REJECT** (PACK forbids ood_long) |

## Forbidden (do not reopen)

`STREAM` · `KVCACHE-Q` · `GENCACHE` · `GPFB_K2` · `ood_long_pack` · `naive_CTX` · `MIXD` · `open_chat_lm` · `zerr_as_chat`

## Validation

```bash
npm run nano:z:depl-y
# optional: --skip-ask
```

Wrap smoke: Z1-01 question → `WRAP_LOOKUP` with `def add` (product path).  
Artifact: `results/nano-lm/wave-z/depl_y_freeze.json` (gitignored).  
Contract: `nano_lm/tests/test_depl_y.py`.

Next: **Z6 REPORT** — **DONE** → [`wave-z-hitl.md`](wave-z-hitl.md). Wave Z **COMPLETE**.
