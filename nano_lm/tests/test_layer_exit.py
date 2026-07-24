"""Contract: layer-exit forward runs fewer blocks when conf high."""

from __future__ import annotations

import torch

from layer_exit import logits_layer_exit, n_transformer_layers
from student_model import build_student


def test_given_two_layer_when_count_then_two():
    m = build_student()
    assert n_transformer_layers(m) == 2


def test_given_high_conf_when_skip_then_one_layer():
    m = build_student().eval()
    ids = torch.randint(0, 200, (1, 5))
    _logits, layers = logits_layer_exit(m, ids, max_skip=1, lay_conf=0.0)
    assert layers == 1


def test_given_impossible_conf_when_skip_then_all_layers():
    m = build_student().eval()
    ids = torch.randint(0, 200, (1, 5))
    _logits, layers = logits_layer_exit(m, ids, max_skip=1, lay_conf=0.999999)
    assert layers == 2
