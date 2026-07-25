# Nano Wave Y — cache + long/infinite context (in progress)

> Lab: `.local/pesquisa.md`. Spine: PFB / QT / PACK.  
> Deploy: [RECIPES.md](RECIPES.md) · [champion-card.md](champion-card.md).

**Status: ACTIVE** · X+ closed → [wave-x-summary.md](wave-x-summary.md).

## PROMOTE (this wave)

| ID | Claim | Evidence |
|----|-------|----------|
| **H-BEAMKV** | Shared prompt KV across PFB K beams; wall↓ vs indep prefills; dual gate vs QT | [smoke](hbeamkv-beamkv.md) · [formal](formal-hbeamkv-beamkv.md) |

## Queued

H-TCACHE · H-PFB256 · H-ROLL / H-STREAM · H-SUMCACHE / H-KVCACHE-Q · H-GENCACHE (after ≥1 long-ctx PROMOTE).

## Doctrine reminder

Every long-context hyp inherits PFB dual gate. Cache = measurable hit-rate / wall↓ / teacher_forwards↓. Do not revive X+ KILL catalog.
