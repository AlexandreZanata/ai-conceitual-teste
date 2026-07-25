"""H-TCACHE: memoize teacher LPs by completion id within PFB BoN.

KEY: (role, prompt, continuation)
TTL: request/BoN scope (in-memory; cleared per smoke/formal run)
INVALIDATE WHEN: new BoN session / new memo instance
STALE OK: no — scores are deterministic for frozen teachers
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from pfb2_ops import K2_BEAMS
from pfb_ops import EPS_LP, MIN_UNIQUE, PFB_TEMP, decide_hpfb

__all__ = [
    "K2_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "MIN_FORWARD_DROP",
    "TeacherLpMemo",
    "decide_htcache",
]

MIN_FORWARD_DROP = 0.30


@dataclass
class TeacherLpMemo:
    """In-BoN memo for story/code teacher mean log-probs."""

    _store: dict[tuple[str, str, str], float] = field(default_factory=dict)
    hits: int = 0
    misses: int = 0

    def get_or_compute(
        self,
        role: str,
        prompt: str,
        continuation: str,
        compute: Callable[[], float],
    ) -> float:
        key = (str(role), str(prompt), str(continuation))
        if key in self._store:
            self.hits += 1
            return float(self._store[key])
        self.misses += 1
        val = float(compute())
        self._store[key] = val
        return val

    @property
    def forwards(self) -> int:
        return int(self.misses)

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return float(self.hits) / float(total) if total else 0.0


def decide_htcache(
    *,
    parent_story: float,
    parent_code: float,
    tcache_story: float,
    tcache_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    tcache_wall: float,
    naive_wall: float,
    tcache_forwards: float,
    naive_forwards: float,
    identical: bool,
) -> str:
    """
    GIVEN EARLY parent vs TCACHE PFB2 + naive score forwards/wall
    WHEN deciding H-TCACHE
    THEN dual-gate like PFB2; teacher_forwards↓ ≥30%; wall↓ or =.
    """
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=tcache_story,
        pfb_code=tcache_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=K2_BEAMS,
        identical=identical,
    )
    labeled = raw.replace("ABS-PFB k=", "TCACHE k=", 1).replace(
        "PFB never", "TCACHE never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    naive_f = float(naive_forwards)
    tc_f = float(tcache_forwards)
    if naive_f <= 0.0:
        return "KILL (naive teacher_forwards missing)"
    drop = (naive_f - tc_f) / naive_f
    if drop < float(MIN_FORWARD_DROP):
        return (
            f"KILL (teacher_forwards drop {drop:.2%} < "
            f"{float(MIN_FORWARD_DROP):.0%}; {tc_f:.0f} vs {naive_f:.0f})"
        )
    if float(tcache_wall) > float(naive_wall):
        return (
            f"KILL (score wall {float(tcache_wall):.1f} > naive "
            f"{float(naive_wall):.1f})"
        )
    return labeled.replace(
        "code↑ story≥parent−ε)",
        "code↑ story≥parent−ε; forwards↓≥30%; wall≤naive)",
        1,
    )
