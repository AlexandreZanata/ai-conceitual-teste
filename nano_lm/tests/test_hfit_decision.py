"""
Contract: H-FIT decision promotes only when teacher_lp beats H-SEL.
GIVEN equal-budget SEL control
WHEN H-FIT mean_lp is compared
THEN PROMOTE iff strictly greater than H-SEL; else KILL/hold.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hyp_fit import FITNESS_KIND
from matrix_report_lib import decision


def test_given_module_when_import_then_fitness_kind_teacher_lp():
    assert FITNESS_KIND == "teacher_lp"


def test_given_missing_hsel_when_hfit_then_needs_control():
    s = {"mean_lp": -16.0}
    assert decision("H-FIT", s, {}) == "needs H-SEL control"


def test_given_better_than_hsel_when_hfit_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9}
    assert decision("H-FIT", s, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hfit_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2}
    assert decision("H-FIT", s, stats) == "KILL / hold (≤ H-SEL)"
