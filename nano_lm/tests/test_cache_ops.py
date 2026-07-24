"""
Contract: H-CACHE dual wall decide; KV decode returns tokens.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cache_ops import decide_hcache
from decode_cache import decode_cache
from data_tiny import load_tokenizer
from student_model import build_student


def test_given_faster_quality_when_decide_then_promote():
    stats = {
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 50.0},
        "B4": {"mean_lp": -17.0, "mean_wall": 80.0},
    }
    s = {"mean_lp": -16.4, "mean_wall": 40.0}
    assert decide_hcache(s, stats).startswith("PROMOTE")


def test_given_no_wall_save_when_decide_then_kill():
    stats = {
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0},
        "B4": {"mean_lp": -17.0, "mean_wall": 80.0},
    }
    s = {"mean_lp": -16.4, "mean_wall": 45.0}
    assert "no wall save" in decide_hcache(s, stats)


def test_given_quality_drop_when_decide_then_kill():
    stats = {
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 50.0},
        "B4": {"mean_lp": -17.0, "mean_wall": 80.0},
    }
    s = {"mean_lp": -16.7, "mean_wall": 30.0}
    assert "quality drop vs H-EARLY" in decide_hcache(s, stats)


def test_given_student_when_decode_cache_then_tokens():
    tok = load_tokenizer("roneneldan/TinyStories-33M", Path("nano_lm/.cache"))
    model = build_student(tok.vocab_size).to("cpu").eval()
    out = decode_cache(
        model,
        tok,
        "Once upon a time",
        n=1,
        max_new_tokens=4,
        min_new=4,
        conf_threshold=0.99,
        patience=3,
        temperature=1.0,
        top_p=0.9,
        seed=0,
        device=torch.device("cpu"),
    )
    assert len(out.token_ids) >= 1
    assert out.wall_ms >= 0.0
