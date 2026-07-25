"""Contract: H-DEPL deploy policy vs BUD survivors."""

from __future__ import annotations

from depl_ops import choose_recipe, decide_hdepl, scenario_ok


def _all_survive() -> dict[str, str]:
    return {
        "H-PACK": "SURVIVE (wall+GFLOPs budgets + win)",
        "H-QPACK": "SURVIVE (wall+GFLOPs budgets + win)",
        "H-TPACK": "SURVIVE (ms/step budget + win)",
    }


def test_given_speed_when_choose_then_pack() -> None:
    assert choose_recipe(goal="speed", in_dist=True, ood_long=False) == "H-PACK"


def test_given_speed_ood_long_when_choose_then_reject() -> None:
    assert choose_recipe(goal="speed", in_dist=False, ood_long=True).startswith(
        "REJECT"
    )


def test_given_quality_ood_when_choose_then_reject() -> None:
    assert choose_recipe(goal="quality", in_dist=False).startswith("REJECT")


def test_given_quality_in_dist_when_choose_then_qpack() -> None:
    assert choose_recipe(goal="quality", in_dist=True) == "H-QPACK"


def test_given_train_when_choose_then_tpack() -> None:
    assert choose_recipe(goal="train", in_dist=True) == "H-TPACK"


def test_given_all_survive_when_decide_then_promote() -> None:
    out = decide_hdepl(_all_survive())
    assert out.startswith("PROMOTE")
    assert "speed_in_dist→H-PACK" in out
    assert "quality_ood→REJECT" in out


def test_given_pack_kill_when_decide_then_kill_speed() -> None:
    v = _all_survive()
    v["H-PACK"] = "KILL (wall over tip budget)"
    out = decide_hdepl(v)
    assert out.startswith("KILL")
    assert "speed_in_dist" in out


def test_given_reject_when_scenario_ok_then_true() -> None:
    assert scenario_ok("REJECT (QPACK requires in-dist)", _all_survive())


def test_given_missing_bud_when_decide_then_needs() -> None:
    assert decide_hdepl({}).startswith("needs H-PACK")
