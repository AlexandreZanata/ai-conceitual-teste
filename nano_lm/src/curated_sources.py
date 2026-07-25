"""Registry of public curated sources for nano KB expansion."""

from __future__ import annotations

from typing import Any

# Phase E session cap (pesquisa): ≤2MB per domain per expansion session.
SESSION_DOMAIN_CAP_BYTES = 2_000_000

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
        "id": "bitcoin-doc-bips",
        "domain": "bitcoin",
        "license": "MIT",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bitcoin/"
            "master/doc/bips.md"
        ),
        "path": "bitcoin/bips.md",
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
        "id": "bip-0039",
        "domain": "bitcoin",
        "license": "BSD-2-Clause",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bips/"
            "master/bip-0039.mediawiki"
        ),
        "path": "bitcoin/bip-0039.mediawiki",
    },
    {
        "id": "bip-0141",
        "domain": "bitcoin",
        "license": "BSD-2-Clause",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bips/"
            "master/bip-0141.mediawiki"
        ),
        "path": "bitcoin/bip-0141.mediawiki",
    },
    {
        "id": "bip-0340",
        "domain": "bitcoin",
        "license": "BSD-2-Clause",
        "url": (
            "https://raw.githubusercontent.com/bitcoin/bips/"
            "master/bip-0340.mediawiki"
        ),
        "path": "bitcoin/bip-0340.mediawiki",
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
        "id": "python-tutorial-datastructures",
        "domain": "programming",
        "license": "PSF",
        "url": "https://docs.python.org/3/tutorial/datastructures.html",
        "path": "programming/python-tutorial-datastructures.html",
    },
    {
        "id": "python-tutorial-classes",
        "domain": "programming",
        "license": "PSF",
        "url": "https://docs.python.org/3/tutorial/classes.html",
        "path": "programming/python-tutorial-classes.html",
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
        "id": "rust-book-ch03-02",
        "domain": "programming",
        "license": "CC-BY-SA / MIT Apache-2.0",
        "url": (
            "https://raw.githubusercontent.com/rust-lang/book/"
            "main/src/ch03-02-data-types.md"
        ),
        "path": "programming/rust-ch03-02-data-types.md",
    },
    {
        "id": "rust-book-ch04-01",
        "domain": "programming",
        "license": "CC-BY-SA / MIT Apache-2.0",
        "url": (
            "https://raw.githubusercontent.com/rust-lang/book/"
            "main/src/ch04-01-what-is-ownership.md"
        ),
        "path": "programming/rust-ch04-01-ownership.md",
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
    {
        "id": "rfc8949",
        "domain": "frontier",
        "license": "IETF Trust",
        "url": "https://www.rfc-editor.org/rfc/rfc8949.txt",
        "path": "frontier/rfc8949.txt",
        "max_bytes": 150_000,
    },
]

# Phase E1–E3 expansion ids (2026-07-25 session).
PHASE_E_IDS: tuple[str, ...] = (
    "bitcoin-doc-bips",
    "bip-0039",
    "bip-0141",
    "bip-0340",
    "python-tutorial-datastructures",
    "python-tutorial-classes",
    "rust-book-ch03-02",
    "rust-book-ch04-01",
    "rfc8949",
)


def source_ids() -> list[str]:
    """Return ordered source ids from the curated registry."""
    return [str(s["id"]) for s in SOURCES]


def by_domain(domain: str) -> list[dict[str, Any]]:
    """Filter registry rows by domain key."""
    return [s for s in SOURCES if s["domain"] == domain]
