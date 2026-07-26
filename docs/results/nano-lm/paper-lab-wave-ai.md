# Paper-lab — Wave AI (push dual-arm · longer/faster/smarter/apps)

> Companion to [wave-ai-summary.md](wave-ai-summary.md). English lab note.  
> **Status: COMPLETE + FROZEN** · Final HITL: [wave-ai-hitl.md](wave-ai-hitl.md) · Freeze: [ai-freeze.md](ai-freeze.md) · Parent: [ah-freeze.md](ah-freeze.md) · Ship: **AF packaged stack**

## Question

After AH froze lift dual-arm with gen still below 5, can an **eighth** held-out 10 push **context**, **speed**, **cite/gen**, and **apps** beyond AH without false-positive “smarter LM” or open-chat claims — and without raising ≤5M?

## Answer

**Partially — as systems pushes; not as open chat.** Wave AI promotes CTXPUSH and FASTPUSH; HOLDs GENPLUS, SMARTPUSH, APPPUSH, CAPRENEG (≤5M stays), and final AI-HITL-10 on gen<5. Ship claim remains the **AF packaged stack**.

| Stage | Observation |
|-------|-------------|
| H-GENPLUS | Grounded QPFB2; gen 4.0 → HOLD |
| H-CAPRENEG | CAP-125M probe; keep ≤5M → HOLD |
| H-CTXPUSH | Hexa-doc L_eff 162851 > CTXLIFT → PROMOTE |
| H-SMARTPUSH | Hexa-hop cite 10/10; gen 4.0 → HOLD |
| H-FASTPUSH | Hot wall 10.7 < FASTLIFT 11.6 → PROMOTE |
| H-APPPUSH | Apps expose LOOKUP\|GENERATE + DEPL-AI → HOLD |
| AI-HITL-10 | Final L=9.0 G=4.0 → HOLD; ship=AF |
| AI-FREEZE | Locked; no Wave AJ invent without reopen |

## Anti-FP takeaway

LOOKUP mean 9.0 with GENERATE mean 1.0–4.0 must **HOLD** intelligence claims. Telemetry (`mode`, `wall_ms`, `n_new`) is mandatory. Peak gen across AI stays **4.0**.

## Takeaway one-liner

**AI = ctx+speed push under anti-FP; gen still HOLD; ship stays AF packaged stack — not open chat.**

## Cite

- [wave-ai-summary.md](wave-ai-summary.md) · [wave-ai-hitl.md](wave-ai-hitl.md) · [ai-freeze.md](ai-freeze.md) · [wave-ah-summary.md](wave-ah-summary.md)  
- Formals: GENPLUS · CAPRENEG · CTXPUSH · SMARTPUSH · FASTPUSH · APPPUSH  
- Deploy: [depl-ai.md](depl-ai.md) · Apps: [apppush-known.md](apppush-known.md) · [apppush-howto.md](apppush-howto.md) · [apppush-longdoc.md](apppush-longdoc.md)  
- Recipes: [RECIPES.md](RECIPES.md) · Card: [champion-card.md](champion-card.md)
