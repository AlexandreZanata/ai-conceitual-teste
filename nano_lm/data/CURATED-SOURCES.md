# Curated public corpora (nano KB)

> Downloaded blobs live under `nano_lm/data/curated/` (gitignored except this tree’s docs).  
> Fetch: `npm run nano:curated` (`download_curated.py --no-proxy` by default in npm script).

## Domains

| Domain | Sources (official / public) | Use |
|--------|----------------------------|-----|
| **bitcoin** | Bitcoin Core README + developer-notes; selected BIPs | Frontier money/protocol text |
| **programming** | Python tutorial (docs.python.org); Rust book chapter | Code/docs language |
| **frontier** | IETF RFC 791, RFC 8446 (TLS 1.3) | Systems / crypto protocol English |

Registry: `nano_lm/src/curated_sources.py` (URL + license + path).  
Manifest after download: `nano_lm/data/curated/manifest.json`.

## Rules

- Public URLs only; record license in registry.
- Cap large RFCs via `max_bytes`.
- TinyStories remains the **story teacher**; domain packs use curated text for eval/train mix (Wave W).
- Programming eval pack: `nano_lm/prompts/prog_prompts.yaml` → `npm run nano:prog` / `nano:formal:hprog` ([formal](../../docs/results/nano-lm/formal-hprog-programming.md)).
- Bitcoin eval pack: `nano_lm/prompts/btc_prompts.yaml` → `npm run nano:btc` ([smoke](../../docs/results/nano-lm/hbtc-bitcoin.md); MIT + BSD-2-Clause).
- Do not commit multi-MB blobs — regenerate via `nano:curated`.
