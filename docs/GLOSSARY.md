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
| **H-ROUTEPLUS** | Cross-app APPPLUS route + honest OOS; AD3 **PROMOTE** (route/OOS 10/10) |
| **H-DEPLPLUS** | AC+AD DEPL one-pagers + smoke; AD4 **PROMOTE** (pages 4/4; mean 9.0) |
| **AD-HITL-10** | Final AD pack HITL on declared stack; AD5 **PROMOTE** (mean 9.0; errors 0/10) |
| **AD-REPORT** | Public Wave AD closeout + paper-lab; AD6 **PROMOTE** |
| **AD-FREEZE** | Lock AD outcomes; no Wave AE invent without lab-book reopen; AD7 **PROMOTE** |
| **AE0-SESSION** | Freeze 10 held-out HITL asks (≠ AB ≠ AC ≠ AD) for Wave AE (**PROMOTE**) |
| **H-CTXMAX** | Multi-doc K=5 ROLL/SUMCACHE; L_eff↑ vs CTXPLUS; AE1 **PROMOTE** (mean 9.0; usable 10/10) |
| **H-SMARTMAX** | Multi-hop para + primary cite beyond HARDPARA/COMPOSE; AE2 **PROMOTE** (mean 9.0; cite 10/10) |
| **H-FASTMAX** | ASKFAST+cache hot serve; e2e ↓ vs FASTPLUS; AE3 **PROMOTE** (mean 9.0; hot e2e ≪ 0.29 ms) |
| **H-APPMAX** | Packaged apps + howto↑ + **app-route** + DEPL-AE; AE4 **PROMOTE** (4/4 apps; mean 8.725) |
| **AE-HITL-10** | Final AE pack verify; AE5 **PROMOTE** (mean 9.0; errors 0; held-out ok) |
| **AE-REPORT** | Public wave summary + paper-lab + FIX log; AE6 **PROMOTE** |
| **AE-FREEZE** | Lock AE outcomes; no Wave AF invent without reopen; AE7 **PROMOTE** |
| **AF0-SESSION** | Freeze 10 held-out HITL asks (≠ AB ≠ AC ≠ AD ≠ AE) for Wave AF (**PROMOTE**) |
| **H-CTXULTRA** | Triple-doc K=7 ROLL/SUMCACHE; L_eff↑ vs CTXMAX; AF1 **PROMOTE** (mean 9.0; usable 10/10) |
| **H-SMARTULTRA** | Triple-hop SEMWRAP cite beyond SMARTMAX; AF2 **PROMOTE** (mean 9.0; cite 10/10; false-hit 0) |
| **H-FASTULTRA** | ASKFAST+key-peek hot serve; e2e ↓ vs FASTMAX; AF3 **PROMOTE** (mean 9.0; hot e2e ≪ 0.034 ms) |
| **H-APPULTRA** | Stronger apps + howto↑ + **app-compose** 5th + DEPL-AF; AF4 **PROMOTE** (5/5 apps; mean 8.86) |
| **AF-HITL-10** | Final verify on declared AF stack; AF5 **PROMOTE** (mean 9.0; errors 0/10) |
| **AF-REPORT** | Public Wave AF summary + paper-lab + FIX log; AF6 **PROMOTE** |
| **AF-FREEZE** | Lock AF outcomes; no Wave AG invent without reopen; AF7 **PROMOTE** |
| **H-ASKSMART** | Anti-period QPFB2+BEAMKV + constrained SEMWRAP FIX; AB4 **PROMOTE** (mean 8.7 > SERVEALIGN 3.4) |
| **H-REALAPP** | Packaged `app-known` + `app-longdoc` one-pagers; AB5 **PROMOTE** (mean 8.85 · DEPL honest) |
| **AB-HITL-10** | Final Wave AB pack verify on declared stack; AB6 **PROMOTE** (mean 9.0 · errors 0/10) |
| **AB-REPORT** | Public Wave AB closeout + FIX scoreboard; AB7 **PROMOTE** — [wave-ab-summary.md](results/nano-lm/wave-ab-summary.md) |
| **AB-FREEZE** | Lock Wave AB outcomes; no Wave AC invent; **PROMOTE** — [ab-freeze.md](results/nano-lm/ab-freeze.md) |
| **H-SERVEALIGN** | QPFB2+BEAMKV open decode HITL; AA2 **HOLD** (beats Z1; not product bar) |
| **H-ABSTAIN** | Refuse junk DECODE (OOD/miss) → `NO_ANSWER` / `mode=ABSTAIN`; AR1 **PROMOTE** (OOD abstain 1.0 · FH 0) |
| **H-SHIPDEMO** | Ship/demo always shows `LOOKUP\|PEAK\|DECODE\|ABSTAIN`; AR2 **PROMOTE** (4/4 modes visible) |
| **H-PARAEXT** | External paraphrase SEMWRAP (≠ AQ-PARA); AR3 **HOLD** (hit 0.65 < 0.70 · FH 0) |
| **H-ADVREG** | Adversary regression (≠ AQ-ADV) + SAFE≠quality; AR4 **KILL** (FH 2/20 near-miss · mean not IQ) |
| **H-NANOGEN2** | Ablated DECODE lift vs H-NANOGEN 4.0; AR5 **HOLD** (ablated 4.3 < 5.0 · peak/bank compare only) |
| **AR-DUAL-HITL** | Final product+gen HITL; AR6 **HOLD** (core ABSTAIN/SHIPDEMO/apps pass · soft PARAEXT/ADVREG · gen locked) |
| **AR-REPORT** | Public Wave AR closeout + paper-lab; AR7 **PROMOTE** — [wave-ar-summary.md](results/nano-lm/wave-ar-summary.md) |
| **AR-FREEZE** | Lock Wave AR outcomes; Wave AS requires lab-book reopen; **PROMOTE** — [ar-freeze.md](results/nano-lm/ar-freeze.md) |
| **AS0-SESSION** | Freeze ADVSAFE (cite AR-ADVREG-01/05) · PARAEXT2 · ASKABSTAIN · SEMFIX · NANOGEN3 · metrics; AS0 **PROMOTE** — [wave-as-session.md](results/nano-lm/wave-as-session.md) |
| **H-ASKABSTAIN** | Wire ABSTAIN into default `nano:z:ask` / apps; AS1 **PROMOTE** (OOD abstain 1.0 · FH 0) — [formal-haskabstain-askabstain.md](results/nano-lm/formal-haskabstain-askabstain.md) |
| **H-SEMFIX** | SEMWRAP negation/contrast/margin; AS2 **PROMOTE** (ADVREG-01/05 FH 0) — [formal-hsemfix-semfix.md](results/nano-lm/formal-hsemfix-semfix.md) |
| **H-ADVSAFE** | Adversary regression after SEMFIX; AS3 **PROMOTE** (ADVSAFE-20 FH **0**/20 · SAFE≠quality) — [formal-hadvsafe-advsafe.md](results/nano-lm/formal-hadvsafe-advsafe.md) |
| **H-PARAEXT2** | External paraphrase after SEMFIX; AS4 **PROMOTE** (hit **0.80** · FH 0) — [formal-hparaext2-paraext2.md](results/nano-lm/formal-hparaext2-paraext2.md) |
| **H-METRICS** | Latency tetrad(+ABSTAIN) p50/p99 + KB holes; AS5 **PROMOTE** — [formal-hmetrics-metrics.md](results/nano-lm/formal-hmetrics-metrics.md) |
| **H-SHIPUI** | Ask+ship/demo mode labels 4/4; AS6 **PROMOTE** — [formal-hshipui-shipui.md](results/nano-lm/formal-hshipui-shipui.md) |
| **H-NANOGEN3** | Ablated DECODE vs NANOGEN2 4.3; AS7 **HOLD** (ablated **4.3** · peak_only) — [formal-hnanogen3-nanogen3.md](results/nano-lm/formal-hnanogen3-nanogen3.md) |
| **AS-DUAL-HITL** | Product pillars + gen gate; AS8 **PROMOTE** (gen locked) — [wave-as-dual-hitl.md](results/nano-lm/wave-as-dual-hitl.md) |
| **AS-REPORT** | Public summary + paper-lab; AS9 **PROMOTE** — [wave-as-summary.md](results/nano-lm/wave-as-summary.md) · [paper-lab-wave-as.md](results/nano-lm/paper-lab-wave-as.md) |
| **AS-FREEZE** | Lock AS outcomes; AS10 **PROMOTE** — [as-freeze.md](results/nano-lm/as-freeze.md) · [formal-hasfreeze-as-freeze.md](results/nano-lm/formal-hasfreeze-as-freeze.md) |
| **AT0-SESSION** | Freeze PRODREG suite · SHIPAPP · NANOGEN4 hyp · real-eval; AT0 **PROMOTE** — [wave-at-session.md](results/nano-lm/wave-at-session.md) |
| **H-PRODREG** | Caminho A product regression (para · FH · p50/p99 · KB · modes · abstain); AT1 **PROMOTE** — [formal-hprodreg-prodreg.md](results/nano-lm/formal-hprodreg-prodreg.md) |
| **H-SHIPAPP** | Human ask/apps/ship-demo always show `LOOKUP\|PEAK\|DECODE\|ABSTAIN`; AT2 **PROMOTE** — [formal-hshipapp-shipapp.md](results/nano-lm/formal-hshipapp-shipapp.md) |
| **H-NANOGEN4** | Ablated DECODE lift vs NANOGEN3 4.3 via snippet-prefix; AT3 **PROMOTE** (ablated **5.5**) — [formal-hnanogen4-nanogen4.md](results/nano-lm/formal-hnanogen4-nanogen4.md) |
| **AT-REAL-EVAL** | Product + gen + live ask battery; AT4 **PROMOTE** — [wave-at-real-eval.md](results/nano-lm/wave-at-real-eval.md) |
| **AT-REPORT** | Public summary + paper-lab; AT5 **PROMOTE** — [wave-at-summary.md](results/nano-lm/wave-at-summary.md) · [paper-lab-wave-at.md](results/nano-lm/paper-lab-wave-at.md) |
| **AT-FREEZE** | Lock Wave AT outcomes; no Wave AU without reopen; AT6 **PROMOTE** — [at-freeze.md](results/nano-lm/at-freeze.md) · [formal-hatfreeze-at-freeze.md](results/nano-lm/formal-hatfreeze-at-freeze.md) |
| **AU0-SESSION** | Freeze product-debt · human-para · NANOGEN5 hyp · strict judge · real-eval; AU0 **PROMOTE** — [wave-au-session.md](results/nano-lm/wave-au-session.md) |
| **H-PRODHARD** | Close live-audit debts on default ask (near-miss ABSTAIN · human para · PEAK usable); AU1 **PROMOTE** — [formal-hprodhard-prodhard.md](results/nano-lm/formal-hprodhard-prodhard.md) |
| **PROMOTE / KILL** | Smoke+formal decision vs parent tip/recipe |

Never call evolutionary individuals “coding agents.”
