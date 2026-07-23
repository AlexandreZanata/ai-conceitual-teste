"""
Contract: Baldwin inherits genotype; Lamarck inherits phenotype.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from baldwin_inherit import assert_geno_unchanged, inherit_weights


def test_given_baldwin_when_inherit_then_genotype_not_phenotype():
    geno = {"w": torch.tensor([1.0, 2.0])}
    pheno = {"w": torch.tensor([9.0, 9.0])}
    got = inherit_weights(geno, pheno, mode="baldwin")
    assert assert_geno_unchanged(got, geno)
    assert not assert_geno_unchanged(got, pheno)


def test_given_lamarck_when_inherit_then_phenotype():
    geno = {"w": torch.tensor([1.0])}
    pheno = {"w": torch.tensor([3.0])}
    got = inherit_weights(geno, pheno, mode="lamarck")
    assert assert_geno_unchanged(got, pheno)


def test_given_unknown_mode_when_inherit_then_raises():
    try:
        inherit_weights(0, 1, mode="magic")
        raised = False
    except ValueError:
        raised = True
    assert raised
