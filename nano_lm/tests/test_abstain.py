"""Contract: Wave AR1 H-ABSTAIN — refuse junk DECODE (pesquisa §5)."""

from __future__ import annotations

from abstain_ops import (
    ABSTAIN_ID,
    ABSTAIN_KNOWN_ASK,
    ABSTAIN_OOD_PACK,
    ABSTAIN_THESIS,
    MIN_OOD_ABSTAIN_RATE,
    NO_ANSWER,
    abstain_stats,
    apply_abstain,
    decide_abstain,
    is_false_hit_completion,
    is_junk_decode,
    mode_labeled,
    should_abstain,
)


def test_given_contract_when_constants_then_match_ar1() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AR1 — OOD abstain↑ · FH 0 · modes labeled
    assert ABSTAIN_ID == "H-ABSTAIN"
    assert NO_ANSWER == "NO_ANSWER"
    assert MIN_OOD_ABSTAIN_RATE == 0.8
    assert len(ABSTAIN_OOD_PACK) >= 6
    assert "ABSTAIN" in ABSTAIN_THESIS
    assert "named add" in ABSTAIN_KNOWN_ASK


def test_given_period_collapse_when_junk_then_true() -> None:
    assert is_junk_decode("........") is True
    assert is_junk_decode("") is True
    assert is_junk_decode("   ") is True
    assert is_junk_decode("....") is True


def test_given_story_sludge_when_junk_then_true() -> None:
    sludge = (
        " �!. followed back at� everything even really finally getting "
        "That really now looking To just something quickly� which"
    )
    assert is_junk_decode(sludge) is True


def test_given_tinystories_let_and_when_junk_then_true() -> None:
    # GIVEN TinyStories sludge with accidental "let and"
    # WHEN is_junk_decode (bare "let " must not false-exempt)
    # THEN refuse — product ABSTAIN path stays honest
    sludge = (
        " decided. grabbed just doing!; almost something\". m. just asked "
        "really two some one one To.. this really. let and -. and; decided "
        "for! everything wasn so. asked so grabbed grabbed some seemed"
    )
    assert is_junk_decode(sludge) is True


def test_given_real_code_when_junk_then_false() -> None:
    assert is_junk_decode("def add(a, b):\n    return a + b") is False
    assert is_junk_decode("Hardened keys use indices >= 2^31.") is False
    assert is_junk_decode("fn main() { let x = 1; println!(x); }") is False


def test_given_decode_junk_when_should_abstain_then_true() -> None:
    assert should_abstain(raw_mode="QT+EARLY n=1", completion="........")
    assert should_abstain(raw_mode="WRAP_DECODE", completion="........")
    assert not should_abstain(
        raw_mode="WRAP_LOOKUP", completion="def add(a, b):\n    return a + b"
    )


def test_given_junk_payload_when_apply_then_no_answer() -> None:
    out = apply_abstain(
        {"mode": "QT+EARLY n=1", "completion": "........", "wall_ms": 11.0}
    )
    assert out["abstained"] is True
    assert out["completion"] == NO_ANSWER
    assert out["mode"] == "NO_ANSWER"
    assert out["product_mode"] == "ABSTAIN"
    assert mode_labeled(out) is True


def test_given_lookup_when_apply_then_keep_gold() -> None:
    gold = "def add(a, b):\n    return a + b"
    out = apply_abstain(
        {"mode": "WRAP_LOOKUP", "completion": gold, "wall_ms": 0.0}
    )
    assert out["abstained"] is False
    assert out["completion"] == gold
    assert out["product_mode"] == "LOOKUP"


def test_given_ood_gold_when_false_hit_then_true() -> None:
    assert (
        is_false_hit_completion(
            completion="CS = ENT / 32",
            product_mode="DECODE",
            bank_golds=["CS = ENT / 32"],
        )
        is True
    )
    assert (
        is_false_hit_completion(
            completion=NO_ANSWER,
            product_mode="ABSTAIN",
            bank_golds=["CS = ENT / 32"],
        )
        is False
    )


def test_given_ready_when_decide_then_promote() -> None:
    stats = abstain_stats(
        ood_abstained=[True] * 8,
        known_lookup_ok=True,
        n_false_hit=0,
        modes_labeled=True,
    )
    assert stats["pass_ood_abstain"] is True
    assert decide_abstain(stats) == "PROMOTE"


def test_given_low_abstain_when_decide_then_kill() -> None:
    stats = abstain_stats(
        ood_abstained=[True, False, False, False, False],
        known_lookup_ok=True,
        n_false_hit=0,
        modes_labeled=True,
    )
    assert decide_abstain(stats).startswith("KILL")
    assert "abstain_rate" in decide_abstain(stats)
