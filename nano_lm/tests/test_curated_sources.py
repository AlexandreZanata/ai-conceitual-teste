"""Contract: curated public source registry is non-empty and well-formed."""

from pathlib import Path

from curated_sources import (
    PHASE_E_IDS,
    SESSION_DOMAIN_CAP_BYTES,
    SOURCES,
    by_domain,
    source_ids,
)

CURATED = Path("nano_lm/data/curated")


def test_given_registry_when_list_ids_then_unique_nonempty() -> None:
    ids = source_ids()
    assert len(ids) >= 15
    assert len(ids) == len(set(ids))


def test_given_registry_when_filter_bitcoin_then_all_bitcoin() -> None:
    rows = by_domain("bitcoin")
    assert rows
    assert all(r["domain"] == "bitcoin" for r in rows)
    assert all(r["url"].startswith("https://") for r in rows)


def test_given_row_when_required_keys_then_present() -> None:
    for row in SOURCES:
        assert {"id", "domain", "license", "url", "path"} <= set(row)
        assert row["domain"] in {"bitcoin", "programming", "frontier"}


def test_given_phase_e_when_registry_then_ids_present() -> None:
    ids = set(source_ids())
    missing = set(PHASE_E_IDS) - ids
    assert not missing, f"missing Phase E ids: {sorted(missing)}"


def test_given_rfc8949_when_registry_then_max_bytes() -> None:
    row = next(s for s in SOURCES if s["id"] == "rfc8949")
    assert int(row["max_bytes"]) <= 150_000


def test_given_curated_disk_when_domains_then_under_session_cap() -> None:
    """Real blobs after nano:curated must stay ≤2MB/domain (Phase E cap)."""
    for domain in ("bitcoin", "programming", "frontier"):
        root = CURATED / domain
        assert root.is_dir(), f"missing curated domain dir {domain}"
        total = sum(f.stat().st_size for f in root.rglob("*") if f.is_file())
        assert total <= SESSION_DOMAIN_CAP_BYTES, (
            f"{domain}={total} exceeds {SESSION_DOMAIN_CAP_BYTES}"
        )
