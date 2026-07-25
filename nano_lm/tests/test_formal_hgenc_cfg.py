"""Contract: formal H-GENC cfg points at dedicated out dir."""

from __future__ import annotations

from pathlib import Path

from run_formal_hgenc import formal_cfg


def test_given_formal_cfg_when_read_then_out_is_formal_hgenc() -> None:
    c = formal_cfg()
    out = Path(c["out"])
    assert out.name == "formal-hgenc"
    assert "seeds" in c
    assert "early_dir" in c
    assert "ckpt_dir" in c
