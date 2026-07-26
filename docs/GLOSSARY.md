# Glossary — nano generative LM (active)

> Full EvoGen survival terms: [`archive/evogen/GLOSSARY.md`](archive/evogen/GLOSSARY.md).

| Term | Meaning |
|------|---------|
| **Student** | ≤5M param causal LM under study (not a “coding agent”) |
| **Teacher** | Frozen larger LM scoring completions (TinyStories-33M on story harness) |
| **Code teacher** | Frozen tiny public code LM scoring prog/btc completions (`code_teacher_lp`; H-TCHR: `bigcode/tiny_starcoder_py`) |
| **Story teacher** | TinyStories-33M; never silently swapped with the code teacher |
| **Tip** | Official champion decode/train config (STAG′, EARLY, POOL) |
| **Recipe** | Deployable pack (PACK serve-fast, TPACK+AMORT train, QPACK quality) |
| **Domain pack** | Held-out prompt set (howto, code, bitcoin, …) for capacity/transfer |
| **Curated KB** | Public official corpora under `nano_lm/data/curated/` |
| **Dual gate** | Quality (teacher_lp / domain metric) **and** wall/GFLOPs |
| **H-QT** | Int8 weight-only quantized student serve (Linear; skip tied lm_head) |
| **H-CKD** | Soft-KD from code teacher (smoke **KILL**; see archive) |
| **H-QCTX** | Born-rule amplitude attention @ long L (smoke **KILL**; see archive) |
| **H-QCOMP** | Classical-shadow KV sketch (smoke PROMOTE → formal **KILL**; see archive) |
| **H-Q-QUBITKV** | Critical KV + residual sketch (smoke **KILL**; see archive) |
| **H-GENC** | Genetic context/serve genome under BUD (smoke+formal **PROMOTE**) |
| **H-GENQ-ABS** | Amplitude/measurement genetics vs GENC (smoke+formal **KILL**; see archive) |
| **H-DIST** | Shared-vocab Neo KD on curated prog (smoke **KILL**; see archive) |
| **H-Q-SLOT** | K curated slots + measure commit (smoke **KILL**; see archive) |
| **H-Q-INTERF** | Dual-teacher α-BoN score interference (smoke **KILL**; see archive) |
| **H-ABS-REV** | Time-reversed KV prefill (smoke **KILL**; see archive) |
| **H-Q-ANNEAL** | Per-token T(t)/conf(t) cooling on EARLY (smoke **KILL**; see archive) |
| **H-ABS-SPIRAL** | Hilbert-curve absolute position remap (smoke **KILL**; see archive) |
| **H-Q-GROVER** | R-round next-token mass amplify p∝p² (smoke **KILL**; see archive) |
| **H-Q-TUNNEL** | Tiny ε leak past causal MASK (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-BELL** | Distant (i,i+τ) K/V mean couple (smoke **KILL**; identity vs EARLY; see archive) |
| **H-ABS-ORACLE1** | 1-bit sha256 parity marker vs RAG prepend (smoke **KILL**; code↓ vs EARLY; see archive) |
| **H-ABS-DNA** | Codon-like 3-mer BPE packs (smoke **KILL**; story↓; see archive) |
| **H-ABS-DEBATE** | Dual early-exit halves + BoN commit (smoke **KILL**; identity; see archive) |
| **H-ABS-HOLO** | 4-bit KV + RFF holographic checksum (smoke **KILL**; code↓ vs EARLY−ε; see archive) |
| **H-ABS-PHASE** | 2D rotary / complex e^{iθ} on Q/K (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-ENTPOS** | Low-rank bilinear pos⊗tok attn bias (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-MEASURE** | Mid-decode RAG slot measure/commit (smoke **KILL**; code↓ vs EARLY−ε; see archive) |
| **H-Q-TELE** | Mid-layer residual RAG teleport (smoke **KILL**; identity vs EARLY; see archive) |
| **H-Q-WIGNER** | Signed top-k logit quasi-prob (smoke **KILL**; identity vs EARLY; see archive) |
| **H-ABS-CHRONO** | Acausal KD soft-label shuffle (smoke **KILL**; code↓ vs EARLY; see archive) |
| **H-ABS-MIRROR** | Anti-teacher (1−p) margin (smoke PROMOTE / formal **KILL** story↓; see archive) |
| **H-ABS-CBON** | Code-teacher BoN commit (smoke **KILL**; code↑ story↓; see archive) |
| **H-ABS-CSAFE** | Story-constrained code BoN (smoke **KILL**; low elig story↓; see archive) |
| **H-ABS-PFB** | Parent-fallback story-floor code BoN (smoke+formal **PROMOTE**) |
| **H-ABS-QPFB** | PFB on QT-int8 student (smoke+formal **PROMOTE**) |
| **H-ABS-PFB2** | PFB with K=2 (smoke+formal **PROMOTE**; wall↓ vs k=4) |
| **H-ABS-QPFB2** | PFB K=2 on QT-int8 (smoke+formal **PROMOTE**; wall↓ vs QPFB k=4) |
| **H-ABS-BPFB** | PFB K=2 on bitcoin pack (smoke+formal **PROMOTE**; domain transfer) |
| **H-ABS-GPFB** | GENC∘PFB2 (smoke **KILL**; archive/hgpfb-gpfb.md) |
| **H-ABS-GPFB4** | GENC∘PFB K=4 (smoke+formal **PROMOTE**; formal-hgpfb4-gpfb4.md) |
| **H-ZWRAP** | Known-ask HITL via `--wrap` **WRAP_LOOKUP** over error_bank golds (not open chat) |
| **H-WRAPBANK** | Expand wrap/error_bank golds + HITL×10; no weight update (Wave AA0 **PROMOTE**) |
| **H-PARA** | Paraphrase stress on wrap; no false-hit; HOLD documents exact-match brittleness (AA1) |
| **H-ZPREF** | Prefer gold≻raw (DPO-lite); AA3 **KILL** — story < parent−ε (wrap still ok) |
| **H-DEPL-DOC** | One-pager sync to DEPL-Y + Wave AA outcomes (AA4 **PROMOTE**) |
| **AA-REPORT** | Wave AA public closeout (summary + paper-lab + wrap smoke; **PROMOTE**) |
| **AA-FREEZE** | Wave AA NO-REOPEN lock after report; Wave AB only via explicit §8.3 reopen (**PROMOTE**) |
| **AB0-SESSION** | Freeze 10 real HITL asks (source_id + app_id) for Wave AB (**PROMOTE**) |
| **H-SEMWRAP** | Fuzzy/semantic recall over wrap bank (+ curated boost); AB1 **PROMOTE** (mean 9.0; 0 false-hit) |
| **H-ASKFAST** | SEMWRAP+QT+ask completion cache; AB2 **PROMOTE** (wall↓100% vs raw QT ask) |
| **H-LONGAPP** | ROLL/SUMCACHE on curated long docs; AB3 **PROMOTE** (10/10 usable; L_eff≫W) |
| **H-CTXPLUS** | Multi-slice ROLL/SUMCACHE on held-out docs; AC1 **PROMOTE** (L_eff 20523>AB; usable 10/10) |
| **H-SMARTPLUS** | Hard-paraphrase SEMWRAP+ASKSMART; AC2 **PROMOTE** (mean 9.0; false-hit 0) |
| **H-FASTPLUS** | ASKFAST+cache on held-out asks; AC3 **PROMOTE** (e2e≪AB; wall_drop 100%) |
| **H-APPPLUS** | Packaged apps + **app-howto**; AC4 **PROMOTE** (3/3 apps; mean 8.6) |
| **AC-HITL-10** | Final Wave AC pack verify on declared stack; AC5 **PROMOTE** (mean 9.0 · errors 0/10) |
| **AC-REPORT** | Public Wave AC closeout + FIX scoreboard; AC6 **PROMOTE** — [wave-ac-summary.md](results/nano-lm/wave-ac-summary.md) |
| **AC-FREEZE** | Lock Wave AC outcomes; no Wave AD invent; **PROMOTE** — [ac-freeze.md](results/nano-lm/ac-freeze.md) |
| **AD0-SESSION** | Freeze 10 held-out HITL asks (≠ AB ≠ AC) for Wave AD (**PROMOTE**) |
| **H-HARDPARA** | Adversarial paraphrase SEMWRAP+SMARTPLUS; AD1 **PROMOTE** (mean 9.0; false-hit 0) |
| **H-COMPOSE** | Dual-source CTXPLUS compose; AD2 **PROMOTE** (usable 10/10; sources 2.0) |
| **H-ASKSMART** | Anti-period QPFB2+BEAMKV + constrained SEMWRAP FIX; AB4 **PROMOTE** (mean 8.7 > SERVEALIGN 3.4) |
| **H-REALAPP** | Packaged `app-known` + `app-longdoc` one-pagers; AB5 **PROMOTE** (mean 8.85 · DEPL honest) |
| **AB-HITL-10** | Final Wave AB pack verify on declared stack; AB6 **PROMOTE** (mean 9.0 · errors 0/10) |
| **AB-REPORT** | Public Wave AB closeout + FIX scoreboard; AB7 **PROMOTE** — [wave-ab-summary.md](results/nano-lm/wave-ab-summary.md) |
| **AB-FREEZE** | Lock Wave AB outcomes; no Wave AC invent; **PROMOTE** — [ab-freeze.md](results/nano-lm/ab-freeze.md) |
| **H-SERVEALIGN** | QPFB2+BEAMKV open decode HITL; AA2 **HOLD** (beats Z1; not product bar) |
| **PROMOTE / KILL** | Smoke+formal decision vs parent tip/recipe |

Never call evolutionary individuals “coding agents.”
