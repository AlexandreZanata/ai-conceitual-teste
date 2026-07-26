# Nano Wave Y — cache + long/infinite context (**COMPLETE**)

> Lab: `.local/pesquisa.md`. Spine: PFB / QT / PACK.  
> Deploy: [RECIPES.md](RECIPES.md) · [champion-card.md](champion-card.md).

**Status: COMPLETE** · X+ closed → [wave-x-summary.md](wave-x-summary.md).  
**Next:** Wave Z **COMPLETE** — [wave-z-hitl.md](wave-z-hitl.md) (HITL product report).

## PROMOTE (this wave)

| ID | Claim | Evidence |
|----|-------|----------|
| **H-BEAMKV** | Shared prompt KV across PFB K beams; wall↓ vs indep prefills; dual gate vs QT | [smoke](hbeamkv-beamkv.md) · [formal](formal-hbeamkv-beamkv.md) |
| **H-TCACHE** | Teacher LP memo + eligible-only code forwards on PFB2; forwards↓≥30%; wall≤naive; dual gate | [smoke](htcache-tcache.md) · [formal](formal-htcache-tcache.md) |
| **H-SCORERAM** | Disk/RAM pack teacher score cache; warm wall↓; lp unchanged; hit_rate=1.0 | [smoke](hscoreram-scoreram.md) · [formal](formal-hscoreram-scoreram.md) |
| **H-PFB256** | PFB2 on prog@256 (DOM elongate; not CTX); dual gate vs EARLY@256; wall≈@128 | [smoke](hpfb256-pfb256.md) · [formal](formal-hpfb256-pfb256.md) |
| **H-ROLL** | Rolling W=128 + S=32 summary; PFB2/segment; L_eff≫W; active≤W+S | [smoke](hroll-roll.md) · [formal](formal-hroll-roll.md) |
| **H-SUMCACHE** | Hierarchical coarse‖fine‖tail; L_eff≥512; dual gate; wall≤full+slack | [smoke](hsumcache-sumcache.md) · [formal](formal-hsumcache-sumcache.md) |
| **H-GPFB4-LONG** | GPFB4 K=4 ∘ ROLL; dual gate; L_eff≫W; wall_roll≤full+slack | [smoke](hgpfb4long-gpfb4long.md) · [formal](formal-hgpfb4long-gpfb4long.md) |

## KILL (this wave)

| ID | Lesson | Archive |
|----|--------|---------|
| **H-STREAM** | parent=prev commit lifts code but story collapses across T (formal) | [archive](archive/hstream-stream.md) |
| **H-KVCACHE-Q** | QT∘PFB2 quality ok; session prefix KV did not cut TTFT vs cold | [archive](archive/hkvcache-kvcache.md) |
| **H-GENCACHE** | GA on ROLL/TTL wins mem/wall but story < QPFB2−ε (not Pareto) | [archive](archive/hgencache-gencache.md) |

## Doctrine (frozen)

Every long-context hyp inherits PFB dual gate. Cache = measurable hit-rate / wall↓ / teacher_forwards↓. Do not revive X+ KILL catalog / STREAM / session TTFT↓ / GENCACHE GA. Keep GPFB **K=4 only**.
