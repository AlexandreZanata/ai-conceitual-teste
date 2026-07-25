"""Contract: curated public source registry is non-empty and well-formed."""

from curated_sources import SOURCES, by_domain, source_ids


def test_given_registry_when_list_ids_then_unique_nonempty() -> None:
    ids = source_ids()
    assert len(ids) >= 6
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
