"""Licence-clean source registry for N32 pretraining data.

Every entry carries id, url, licence, sha256 (filled after fetch), expected_bytes,
and attribution_required. Unknown licences are forbidden.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Source:
    id: str
    url: str
    licence: str
    expected_bytes: int
    attribution_required: bool
    sha256: str = ""
    hf_repo: str = ""
    hf_files: tuple[str, ...] = ()
    share_target_tokens: int = 0
    notes: str = ""


# Target mixture from docs/pipeline/P02-data-foundation.md §2.
SOURCES: tuple[Source, ...] = (
    Source(
        id="fineweb_edu",
        url="https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu",
        licence="ODC-By 1.0",
        expected_bytes=15_000_000_000,
        attribution_required=True,
        hf_repo="HuggingFaceFW/fineweb-edu",
        hf_files=tuple(f"sample/10BT/{i:03d}_00000.parquet" for i in range(14)),
        share_target_tokens=4_000_000_000,
        notes="sample-10BT all shards; widened FineWeb-Edu after Stack auth deferral",
    ),
    Source(
        id="cosmopedia_v2",
        url="https://huggingface.co/datasets/HuggingFaceTB/cosmopedia-v2",
        licence="Apache-2.0",
        expected_bytes=3_000_000_000,
        attribution_required=False,
        hf_repo="HuggingFaceTB/cosmopedia-v2",
        hf_files=(),  # resolved at fetch time
        share_target_tokens=600_000_000,
    ),
    Source(
        id="wikipedia_en",
        url="https://huggingface.co/datasets/wikimedia/wikipedia",
        licence="CC-BY-SA-3.0",
        expected_bytes=2_000_000_000,
        attribution_required=True,
        hf_repo="wikimedia/wikipedia",
        hf_files=(),
        share_target_tokens=400_000_000,
        notes="config 20231101.en",
    ),
    Source(
        id="tech_docs_seed",
        url="https://github.com/bitcoin/bitcoin + docs.python.org + IETF RFCs",
        licence="MIT/BSD-2-Clause/PSF-2.0/IETF Trust",
        expected_bytes=2_000_000,
        attribution_required=True,
        share_target_tokens=280_000_000,
        notes="Seed URLs in docs/DATA-PROVENANCE.md §3; extended in fetch",
    ),
    Source(
        id="arxiv_cs",
        url="https://huggingface.co/datasets/gfissore/arxiv-abstracts-2021",
        licence="arXiv non-exclusive distribution",
        expected_bytes=500_000_000,
        attribution_required=True,
        hf_repo="gfissore/arxiv-abstracts-2021",
        hf_files=(),
        share_target_tokens=120_000_000,
    ),
)


# Explicitly rejected — never download.
REJECTED: tuple[dict[str, str], ...] = (
    {
        "source": "roneneldan/TinyStories",
        "reason": "Children fiction corpus that caused prior failure; banned by P02 §7",
        "date": "2026-07-30",
    },
    {
        "source": "unfiltered CommonCrawl / FineWeb without edu filter",
        "reason": "P02 §2: quality-starved models lose BPB on unfiltered crawl",
        "date": "2026-07-30",
    },
    {
        "source": "bigcode/the-stack-v2 (unfiltered)",
        "reason": "Requires per-file permissive filter + HF gate; deferred until auth available",
        "date": "2026-07-30",
    },
)


def sources_by_id() -> dict[str, Source]:
    return {s.id: s for s in SOURCES}


def sources_as_dicts() -> list[dict]:
    return [asdict(s) for s in SOURCES]


def assert_all_licences_known(sources: tuple[Source, ...] = SOURCES) -> None:
    for src in sources:
        if not src.licence or src.licence.lower() in {"unknown", "none", "n/a"}:
            raise ValueError(f"unknown licence for source {src.id}")
