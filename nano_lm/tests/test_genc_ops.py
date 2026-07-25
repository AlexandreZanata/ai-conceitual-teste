"""Contract: H-GENC gene clamp/mutate + BUD/Pareto decide."""

from __future__ import annotations

import random

from genc_ops import (
    EPS_LP,
    POP_MAX,
    clamp_genc_gene,
    decide_hgenc,
    dominates_code_wall,
    mutate_genc_gene,
    parent_genc_gene,
    pareto_front_indices,
    random_genc_gene,
    under_bud_wall,
)


def _m(story: float, code: float, wall: float) -> dict[str, float]:
    return {
        "mean_story_lp": story,
        "mean_code_lp": code,
        "mean_wall_ms": wall,
    }


def test_given_raw_when_clamp_then_codebook() -> None:
    g = clamp_genc_gene(
        {
            "k_retrieve": 9,
            "chunk_len": 50,
            "stride": 20,
            "quant_bits": 4,
            "exit_depth": 9,
        }
    )
    assert g["k_retrieve"] == 2
    assert g["chunk_len"] == 64
    assert g["stride"] == 16
    assert g["quant_bits"] == 8
    assert g["exit_depth"] == 2


def test_given_parent_when_read_then_pack_defaults() -> None:
    g = parent_genc_gene()
    assert g["k_retrieve"] == 0
    assert g["quant_bits"] == 16
    assert g["exit_depth"] == 2


def test_given_mutate_when_many_then_stays_clamped() -> None:
    rng = random.Random(0)
    g = parent_genc_gene()
    for _ in range(40):
        g = mutate_genc_gene(g, rng)
        assert g == clamp_genc_gene(g)
    assert POP_MAX == 8
    assert isinstance(random_genc_gene(rng), dict)


def test_given_wall_over_when_bud_then_false() -> None:
    assert under_bud_wall(10.0, 12.0)
    assert not under_bud_wall(13.0, 12.0)


def test_given_better_code_same_wall_when_dominate_then_true() -> None:
    a = _m(-10.0, -12.0, 20.0)
    b = _m(-10.0, -13.0, 20.0)
    assert dominates_code_wall(a, b)
    assert not dominates_code_wall(b, a)


def test_given_points_when_pareto_then_non_dominated() -> None:
    pts = [
        _m(0, -10.0, 30.0),
        _m(0, -9.0, 40.0),
        _m(0, -11.0, 20.0),
        _m(0, -10.5, 35.0),
    ]
    front = pareto_front_indices(pts)
    assert 1 in front
    assert 2 in front
    assert 3 not in front


def test_given_code_up_under_bud_when_decide_then_promote() -> None:
    out = decide_hgenc(
        parent=_m(-14.0, -16.0, 22.0),
        best=_m(-14.0, -15.5, 20.0),
        n_rows=4,
    )
    assert out.startswith("PROMOTE")
    assert "code↑" in out


def test_given_code_drop_when_decide_then_kill() -> None:
    out = decide_hgenc(
        parent=_m(-14.0, -16.0, 22.0),
        best=_m(-14.0, -16.0 - EPS_LP - 0.2, 10.0),
        n_rows=4,
    )
    assert out.startswith("KILL")
    assert "code_lp" in out


def test_given_wall_over_bud_when_decide_then_kill() -> None:
    out = decide_hgenc(
        parent=_m(-14.0, -16.0, 22.0),
        best=_m(-13.9, -15.5, 40.0),
        n_rows=4,
    )
    assert out.startswith("KILL")
    assert "BUD" in out or "wall" in out.lower()


def test_given_no_win_when_decide_then_kill() -> None:
    out = decide_hgenc(
        parent=_m(-14.0, -16.0, 22.0),
        best=_m(-14.0, -16.0, 22.0),
        n_rows=4,
    )
    assert out.startswith("KILL")
    assert "no code" in out.lower() or "wall" in out.lower()
