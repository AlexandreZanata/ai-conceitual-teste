"""Contracts for P02 data foundation behaviours."""

from __future__ import annotations

from pathlib import Path

from n32.data.clean import clean_document, redact_pii, repetition_ok
from n32.data.dedup import exact_dedup, normalize
from n32.data.io_utils import append_jsonl, sha256_text
from n32.data.sources import REJECTED, SOURCES, assert_all_licences_known
from n32.data.tokenize import encode_doc, train_tokenizer


def test_all_registered_sources_have_known_licences() -> None:
    assert_all_licences_known()
    assert all(s.licence for s in SOURCES)


def test_tinystories_is_explicitly_rejected() -> None:
    names = " ".join(r["source"].lower() for r in REJECTED)
    assert "tinystories" in names


def test_redact_pii_masks_email_and_key() -> None:
    text = "Contact a@b.com with key sk-abcdefghijklmnopqr"
    out = redact_pii(text)
    assert "a@b.com" not in out
    assert "sk-abcdefghijklmnopqr" not in out
    assert "[EMAIL]" in out


def test_clean_drops_too_short() -> None:
    cleaned, reason = clean_document("too short", "fineweb_edu", set())
    assert cleaned is None
    assert reason == "length"


def test_clean_keeps_well_formed_prose() -> None:
    parts = [
        f"Educational sentence number {i} explains a unique scientific idea clearly."
        for i in range(1, 40)
    ]
    text = "\n".join(parts)
    cleaned, reason = clean_document(text, "fineweb_edu", set())
    assert reason == "keep"
    assert cleaned is not None
    assert len(cleaned) >= 200


def test_repetition_filter_drops_looped_lines() -> None:
    line = "Repeat me now."
    text = "\n".join([line] * 40)
    assert repetition_ok(text) is False


def test_exact_dedup_removes_normalized_duplicates(tmp_path: Path) -> None:
    src = tmp_path / "in.jsonl"
    out = tmp_path / "out.jsonl"
    docs = [
        {"id": "1", "source_id": "x", "text": "Hello World", "bytes": 11},
        {"id": "2", "source_id": "x", "text": "hello   world", "bytes": 13},
        {
            "id": "3",
            "source_id": "x",
            "text": "Different document content here.",
            "bytes": 32,
        },
    ]
    append_jsonl(src, docs)
    report = exact_dedup(src, out)
    assert report["kept"] == 2
    assert report["dropped"] == 1


def test_tokenizer_appends_eot_and_fits_uint16(tmp_path: Path) -> None:
    sample = tmp_path / "sample.jsonl"
    append_jsonl(
        sample,
        [
            {
                "id": "a",
                "source_id": "x",
                "text": "hello world " * 50,
                "bytes": 600,
            }
        ],
    )
    tok_path = tmp_path / "tok.json"
    tok = train_tokenizer([sample], tok_path, vocab_size=500)
    ids = encode_doc(tok, "hello world")
    assert ids[-1] == tok.token_to_id("<|endoftext|>")
    assert max(ids) < 65536


def test_contamination_detects_13gram_overlap() -> None:
    grams = {"one two three four five six seven eight nine ten eleven twelve thirteen"}
    prefix = [
        f"Unique educational preface sentence {i} ends properly." for i in range(1, 20)
    ]
    body = "one two three four five six seven eight nine ten eleven twelve thirteen"
    suffix = [
        f"Unique educational closing sentence {i} ends properly." for i in range(1, 20)
    ]
    text = "\n".join(prefix + [body] + suffix)
    cleaned, reason = clean_document(text, "fineweb_edu", grams)
    assert cleaned is None
    assert reason == "contamination"


def test_normalize_collapses_whitespace() -> None:
    assert normalize("A  B\nC") == "a b c"
    assert sha256_text(normalize("A  B")) == sha256_text(normalize("a b"))


def test_exact_dedup_respects_max_kept_bytes(tmp_path: Path) -> None:
    from n32.data.dedup import exact_dedup

    src = tmp_path / "in.jsonl"
    out = tmp_path / "out.jsonl"
    docs = [
        {
            "id": str(i),
            "source_id": "x",
            "text": f"Unique educational document number {i} with enough text.",
            "bytes": 100,
        }
        for i in range(20)
    ]
    append_jsonl(src, docs)
    report = exact_dedup(src, out, max_kept_bytes=250)
    assert report["capped"] is True
    assert report["kept"] <= 3
    assert report["kept_bytes"] >= 250
