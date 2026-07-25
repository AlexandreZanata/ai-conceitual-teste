"""Registry of public curated sources for nano KB expansion."""

from __future__ import annotations

from typing import Any

# Official / widely cited public URLs only (raw text, MIT/BSD/CC where noted).
SOURCES: list[dict[str, Any]] = [
    {
        "id": "bitcoin-core-readme",
        "domain": "bitcoin",
        "license": "MIT",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bitcoin/"
            "master/README.md"
        ),
        "path": "bitcoin/README.md",
    },
    {
        "id": "bitcoin-developer-notes",
        "domain": "bitcoin",
        "license": "MIT",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bitcoin/"
            "master/doc/developer-notes.md"
        ),
        "path": "bitcoin/developer-notes.md",
    },
    {
        "id": "bip-0001",
        "domain": "bitcoin",
        "license": "BSD-2-Clause",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bips/"
            "master/bip-0001.mediawiki"
        ),
        "path": "bitcoin/bip-0001.mediawiki",
    },
    {
        "id": "bip-0032",
        "domain": "bitcoin",
        "license": "BSD-2-Clause",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bips/"
            "master/bip-0032.mediawiki"
        ),
        "path": "bitcoin/bip-0032.mediawiki",
    },
    {
        "id": "python-tutorial-intro",
        "domain": "programming",
        "license": "PSF",
        "url": "https://docs.python.org/3/tutorial/introduction.html",
        "path": "programming/python-tutorial-introduction.html",
    },
    {
        "id": "python-tutorial-control",
        "domain": "programming",
        "license": "PSF",
        "url": "https://docs.python.org/3/tutorial/controlflow.html",
        "path": "programming/python-tutorial-controlflow.html",
    },
    {
        "id": "rust-book-ch03",
        "domain": "programming",
        "license": "CC-BY-SA / MIT Apache-2.0",
        "url": (
            "https://raw.githubusercontent.com/rust-lang/book/"
            "main/src/ch03-01-variables-and-mutability.md"
        ),
        "path": "programming/rust-ch03-01-variables.md",
    },
    {
        "id": "rfc8446",
        "domain": "frontier",
        "license": "IETF Trust",
        "url": "https://www.rfc-editor.org/rfc/rfc8446.txt",
        "path": "frontier/rfc8446.txt",
        "max_bytes": 200_000,
    },
    {
        "id": "rfc791",
        "domain": "frontier",
        "license": "IETF Trust",
        "url": "https://www.rfc-editor.org/rfc/rfc791.txt",
        "path": "frontier/rfc791.txt",
        "max_bytes": 120_000,
    },
]


def source_ids() -> list[str]:
    """Return ordered source ids from the curated registry."""
    return [str(s["id"]) for s in SOURCES]


def by_domain(domain: str) -> list[dict[str, Any]]:
    """Filter registry rows by domain key."""
    return [s for s in SOURCES if s["domain"] == domain]
