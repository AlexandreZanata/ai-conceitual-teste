# Curated public corpora (nano KB)

> Downloaded blobs live under `nano_lm/data/curated/` (gitignored except this tree’s docs).  
> Fetch: `npm run nano:curated` (`download_curated.py --no-proxy` by default in npm script).

## Domains

| Domain | Sources (official / public) | Use |
|--------|----------------------------|-----|
| **bitcoin** | Core README + developer-notes + `doc/bips.md`; BIPs 1, 32, 39, 141, 340 | Frontier money/protocol text |
| **programming** | Python tutorial (intro, control, datastructures, classes); Rust book ch03–04 | Code/docs language |
| **frontier** | IETF RFC 791, RFC 8446 (TLS 1.3), RFC 8949 (CBOR, truncated) | Systems / crypto protocol English |

Registry: `nano_lm/src/curated_sources.py` (URL + license + path).  
Manifest after download: `nano_lm/data/curated/manifest.json`.

## Phase E expansion (2026-07-25)

| Step | Added ids | Cap |
|------|-----------|-----|
| E1 | `python-tutorial-datastructures`, `python-tutorial-classes`, `rust-book-ch03-02`, `rust-book-ch04-01` | ≤2MB/domain |
| E2 | `bitcoin-doc-bips`, `bip-0039`, `bip-0141`, `bip-0340` | license in registry |
| E3 | `rfc8949` (`max_bytes=150000`) | truncate; do not mirror whole IETF |

Eval YAML packs (prog/btc) unchanged this session — E5 deferred.

## Rules

- Public URLs only; record license in registry.
- Cap large RFCs via `max_bytes`.
- TinyStories remains the **story teacher**; domain packs use curated text for eval (Wave W).
- Programming eval pack: `nano_lm/prompts/prog_prompts.yaml` → `npm run nano:prog` / `nano:formal:hprog` ([formal](../../docs/results/nano-lm/formal-hprog-programming.md)).
- Bitcoin eval pack: `nano_lm/prompts/btc_prompts.yaml` → `npm run nano:btc` / `nano:formal:hbtc` ([formal](../../docs/results/nano-lm/formal-hbtc-bitcoin.md); MIT + BSD-2-Clause).
- Train mix (**H-MIXD**): formal **KILL** — tooling purged (`nano:mixd*` removed); see [hmixd-mix.md](../../docs/results/nano-lm/hmixd-mix.md). Never train on eval YAML ids.
- Do not commit multi-MB blobs — regenerate via `nano:curated`.
- Wave W close-out: [wave-w-summary.md](../../docs/results/nano-lm/wave-w-summary.md).
