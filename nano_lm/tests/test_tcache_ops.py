"""Contract: H-TCACHE memo + forwards↓≥30% + wall≤naive + dual gate."""

from __future__ import annotations

from tcache_ops import MIN_FORWARD_DROP, TeacherLpMemo, decide_htcache


def test_given_memo_when_repeat_key_then_hit_no_extra_forward() -> None:
    # GIVEN TeacherLpMemo WHEN same completion scored twice THEN 1 forward
    memo = TeacherLpMemo()
    calls = {"n": 0}

    def compute() -> float:
        calls["n"] += 1
        return -3.5

    a = memo.get_or_compute("story", "p", "c", compute)
    b = memo.get_or_compute("story", "p", "c", compute)
    assert a == b == -3.5
    assert calls["n"] == 1
    assert memo.forwards == 1
    assert memo.hits == 1
    assert memo.hit_rate() == 0.5


def test_given_forwards_drop_when_decide_then_promote() -> None:
    d = decide_htcache(
        parent_story=-10.0,
        parent_code=-16.0,
        tcache_story=-9.9,
        tcache_code=-14.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.4,
        tcache_wall=40.0,
        naive_wall=50.0,
        tcache_forwards=70.0,
        naive_forwards=100.0,
        identical=False,
    )
    assert d.startswith("PROMOTE")
    assert "TCACHE" in d
    assert "forwards↓" in d


def test_given_forwards_drop_low_when_decide_then_kill() -> None:
    d = decide_htcache(
        parent_story=-10.0,
        parent_code=-16.0,
        tcache_story=-9.9,
        tcache_code=-14.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.4,
        tcache_wall=40.0,
        naive_wall=50.0,
        tcache_forwards=90.0,
        naive_forwards=100.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "teacher_forwards" in d
    assert MIN_FORWARD_DROP == 0.30


def test_given_wall_up_when_decide_then_kill() -> None:
    d = decide_htcache(
        parent_story=-10.0,
        parent_code=-16.0,
        tcache_story=-9.9,
        tcache_code=-14.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.4,
        tcache_wall=60.0,
        naive_wall=50.0,
        tcache_forwards=50.0,
        naive_forwards=100.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "wall" in d.lower()


def test_given_story_drop_when_decide_then_kill() -> None:
    d = decide_htcache(
        parent_story=-10.0,
        parent_code=-16.0,
        tcache_story=-12.0,
        tcache_code=-10.0,
        mean_unique=2.0,
        mean_elig=1.0,
        mean_switch=0.5,
        tcache_wall=40.0,
        naive_wall=50.0,
        tcache_forwards=50.0,
        naive_forwards=100.0,
        identical=False,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d
