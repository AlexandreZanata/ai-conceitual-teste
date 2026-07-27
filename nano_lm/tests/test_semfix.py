"""Contract: Wave AS2 H-SEMFIX — SEMWRAP polarity/negation (pesquisa §5)."""

from __future__ import annotations

from semfix_ops import (
    REQUIRED_PARENTS,
    SEMFIX_HYPOTHESIS,
    SEMFIX_ID,
    SEMFIX_KNOWN_CONTROLS,
    SEMFIX_TARGET_PACK,
    SEMFIX_THESIS,
    decide_semfix,
    reject_wired_for_targets,
    semfix_stats,
    target_false_hit,
)
from semwrap_ops import contrastive_reject, semantic_lookup


def test_given_contract_when_constants_then_match_as2() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS2 — AR-ADVREG-01/05 class → no wrong gold
    assert SEMFIX_ID == "H-SEMFIX"
    assert REQUIRED_PARENTS == {"AR-ADVREG-01", "AR-ADVREG-05"}
    assert len(SEMFIX_TARGET_PACK) == 2
    assert {p["id"] for p in SEMFIX_TARGET_PACK} == REQUIRED_PARENTS
    assert "negation" in SEMFIX_HYPOTHESIS.lower()
    assert "margin" in SEMFIX_HYPOTHESIS.lower()
    assert "01" in SEMFIX_THESIS or "ADVREG" in SEMFIX_THESIS
    assert len(SEMFIX_KNOWN_CONTROLS) >= 2


def test_given_advreg01_when_contrast_then_reject() -> None:
    ask = SEMFIX_TARGET_PACK[0]["ask"]
    assert "AR-ADVREG-01" in {p["id"] for p in SEMFIX_TARGET_PACK}
    item = next(p for p in SEMFIX_TARGET_PACK if p["id"] == "AR-ADVREG-01")
    assert contrastive_reject(
        item["ask"],
        "BIP-39: what is the formula for checksum length CS in terms of ENT?",
        "CS = ENT / 32",
    )
    assert ask  # pack non-empty


def test_given_advreg05_when_contrast_then_reject() -> None:
    item = next(p for p in SEMFIX_TARGET_PACK if p["id"] == "AR-ADVREG-05")
    assert contrastive_reject(
        item["ask"],
        "Which keyword is a no-op placeholder statement in Python?",
        "pass",
    )


def test_given_reject_helpers_when_targets_then_wired() -> None:
    assert reject_wired_for_targets() is True


def test_given_target_gold_when_false_hit_then_true() -> None:
    assert target_false_hit(
        item={"id": "AR-ADVREG-01"}, looked_up="CS = ENT / 32"
    )
    assert target_false_hit(item={"id": "AR-ADVREG-05"}, looked_up="pass")
    assert not target_false_hit(item={"id": "AR-ADVREG-01"}, looked_up=None)
    assert not target_false_hit(item={"id": "AR-ADVREG-05"}, looked_up=None)


def test_given_bank_when_lookup_targets_then_no_gold() -> None:
    rows = [
        {
            "question": (
                "BIP-39: what is the formula for checksum length CS in "
                "terms of ENT? (write CS = …)"
            ),
            "source_id": "bip-0039",
            "gold": "CS = ENT / 32",
        },
        {
            "question": (
                "Which keyword is a no-op placeholder statement in Python "
                "(Pass Statements)?"
            ),
            "source_id": "python-tutorial-control",
            "gold": "pass",
        },
        {
            "question": (
                "Which statement skips the rest of the current loop "
                "iteration and continues with the next?"
            ),
            "source_id": "python-tutorial-control",
            "gold": "continue",
        },
    ]
    for item in SEMFIX_TARGET_PACK:
        gold, meta = semantic_lookup(item["ask"], rows)
        assert gold is None
        assert meta["kind"] == "REJECT_NEAR_MISS"
        assert not target_false_hit(item=item, looked_up=gold)


def test_given_known_seed_when_lookup_then_still_hits() -> None:
    rows = [
        {
            "question": (
                "Write a short Python function named add that returns "
                "the sum of two integers a and b."
            ),
            "source_id": "python-tutorial-intro",
            "gold": "def add(a, b):\n    return a + b",
        }
    ]
    ctrl = SEMFIX_KNOWN_CONTROLS[0]
    gold, meta = semantic_lookup(ctrl["paraphrase"], rows)
    assert gold is not None
    assert "add" in gold
    assert meta["kind"] in {"SEMANTIC", "EXACT"}


def test_given_ready_when_decide_then_promote() -> None:
    stats = semfix_stats(
        target_outcomes=[
            {"id": "AR-ADVREG-01", "parent_id": "AR-ADVREG-01", "false_hit": False},
            {"id": "AR-ADVREG-05", "parent_id": "AR-ADVREG-05", "false_hit": False},
        ],
        known_hits=[True, True],
        reject_wired=True,
    )
    assert decide_semfix(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = semfix_stats(
        target_outcomes=[
            {"id": "AR-ADVREG-01", "parent_id": "AR-ADVREG-01", "false_hit": True},
            {"id": "AR-ADVREG-05", "parent_id": "AR-ADVREG-05", "false_hit": False},
        ],
        known_hits=[True, True],
        reject_wired=True,
    )
    assert decide_semfix(stats).startswith("KILL")
    assert "false-hit" in decide_semfix(stats)


def test_given_known_miss_when_decide_then_kill() -> None:
    stats = semfix_stats(
        target_outcomes=[
            {"id": "AR-ADVREG-01", "parent_id": "AR-ADVREG-01", "false_hit": False},
            {"id": "AR-ADVREG-05", "parent_id": "AR-ADVREG-05", "false_hit": False},
        ],
        known_hits=[True, False],
        reject_wired=True,
    )
    assert "known SEMWRAP" in decide_semfix(stats)
