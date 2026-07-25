"""Contract: H-XFER2 score aggregates PACK and optional BPACK."""

from __future__ import annotations

from xfer2_score import verdicts_from_rows


def _row(family: str, lp: float, wall: float, tps: float, gflops: float = 10.0) -> dict:
    return {
        "family": family,
        "teacher_mean_logprob": lp,
        "mean_wall_ms": wall,
        "mean_tokens_per_s": tps,
        "mean_est_gflops": gflops,
    }


def test_given_pack_rows_when_verdicts_then_pack_only() -> None:
    pack_by = {
        "elongated": [
            _row("H-EARLY", -14.0, 12.0, 700.0),
            _row("H-SERVE", -14.0, 3.0, 2800.0),
            _row("H-SROUTE", -12.5, 6.0, 5000.0),
        ],
        "ood": [
            _row("H-EARLY", -14.0, 12.0, 700.0),
            _row("H-SERVE", -14.0, 3.0, 2800.0),
            _row("H-SROUTE", -12.5, 6.0, 5000.0),
        ],
        "ood_long": [
            _row("H-EARLY", -14.0, 12.0, 700.0),
            _row("H-SERVE", -14.0, 3.0, 2800.0),
            _row("H-SROUTE", -12.5, 6.0, 5000.0),
        ],
    }
    out = verdicts_from_rows(pack_by=pack_by)
    assert set(out) == {"H-PACK"}
    assert all(out["H-PACK"][p].startswith("PROMOTE") for p in pack_by)


def test_given_bpack_rows_when_verdicts_then_includes_bpack() -> None:
    pack_by = {
        "ood": [
            _row("H-EARLY", -14.0, 12.0, 700.0),
            _row("H-SERVE", -14.0, 3.0, 2800.0),
            _row("H-SROUTE", -12.5, 6.0, 5000.0),
        ]
    }
    bpack_by = {
        "ood": [
            _row("H-EARLY", -14.0, 12.0, 700.0, 10.0),
            _row("H-SKIP", -14.0, 4.0, 2000.0, 10.0),
            _row("H-LAYB", -14.0, 5.0, 1800.0, 10.0),
        ]
    }
    out = verdicts_from_rows(pack_by=pack_by, bpack_by=bpack_by)
    assert "H-BPACK" in out
    assert out["H-BPACK"]["ood"].startswith("PROMOTE")
