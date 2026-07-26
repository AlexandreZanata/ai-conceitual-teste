"""Contract: formal H-GPFB4-LONG cfg uses formal ckpts + K=4 + ROLL."""

from __future__ import annotations

from gpfb4long_ops import K_BEAMS, ROLL_TARGET
from run_formal_hgpfb4long import formal_cfg


def test_given_formal_cfg_when_read_then_gpfb4long_out() -> None:
    c = formal_cfg()
    assert "formal-hgpfb4long" in str(c["out"])
    assert c["seeds"]
    assert K_BEAMS == 4
    assert ROLL_TARGET == 384
