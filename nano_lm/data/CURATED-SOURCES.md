# Curated public corpora (nano KB)

> Downloaded blobs live under `nano_lm/data/curated/` (gitignored except this tree’s docs).  
> Fetch: `npm run nano:curated` (`download_curated.py --no-proxy` by default in npm script).

## Domains

| Domain | Sources (official / public) | Use |
|--------|----------------------------|-----|
| **bitcoin** | Core README + developer-notes + `doc/bips.md` + JSON-RPC/REST docs; BIPs 1, 32, 39, 141, 340 | Frontier money/protocol text |
| **programming** | Python tutorial (intro, control, datastructures, classes, I/O); Rust book ch03–05 | Code/docs language |
| **frontier** | IETF RFC 791, RFC 8446 (TLS 1.3), RFC 8949 (CBOR, truncated) | Systems / crypto protocol English |

Registry: `nano_lm/src/curated_sources.py` (URL + license + path).  
Manifest after download: `nano_lm/data/curated/manifest.json`.

## Phase E expansion

| Step | Added | Cap / note |
|------|-------|------------|
| E1–E3 | See prior session (+9 ids) | ≤2MB/domain |
| E4 | `bitcoin-json-rpc`, `bitcoin-rest`, `python-tutorial-io`, `rust-book-ch05-01` | Core **docs** + small language samples; no git dumps |
| E5 | Eval YAML: `e5_prog_heldout.yaml`, `e5_btc_heldout.yaml`, `frontier_prompts.yaml` | Prompts in git; H-PROG/H-BTC claim packs **unchanged** |

E5 smoke: `npm run nano:e5` (build heldout/frontier; one-seed PACK serve on frontier).

## Rules

- Public URLs only; record license in registry.
- Cap large RFCs via `max_bytes`.
- TinyStories remains the **story teacher**; domain packs use curated text for eval (Wave W).
- Programming eval pack: `nano_lm/prompts/prog_prompts.yaml` → `npm run nano:prog` / `nano:formal:hprog` ([formal](../../docs/results/nano-lm/formal-hprog-programming.md)).
- Bitcoin eval pack: `nano_lm/prompts/btc_prompts.yaml` → `npm run nano:btc` / `nano:formal:hbtc` ([formal](../../docs/results/nano-lm/formal-hbtc-bitcoin.md); MIT + BSD-2-Clause).
- Train mix (**H-MIXD**): formal **KILL** — tooling purged; see [archive/hmixd-mix.md](../../docs/results/nano-lm/archive/hmixd-mix.md). Never train on eval YAML ids.
- Do not commit multi-MB blobs — regenerate via `nano:curated`.
- Wave W close-out: [wave-w-summary.md](../../docs/results/nano-lm/wave-w-summary.md).
- Wave X **H-RAG** (naive curated prepend @ decode): smoke **KILL** — [archive/hrag-retrieve.md](../../docs/results/nano-lm/archive/hrag-retrieve.md); tooling purged.
