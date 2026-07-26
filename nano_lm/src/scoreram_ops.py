"""H-SCORERAM: disk/RAM teacher score cache across pack prompts.

KEY: (role, prompt, continuation) — same as H-TCACHE
TTL: pack session + optional disk file
INVALIDATE WHEN: delete cache file / new PackScoreCache
STALE OK: no — frozen teachers; deterministic LPs
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from lat_ops import EPS_LP
from tcache_ops import TeacherLpMemo

__all__ = [
    "EPS_LP",
    "MIN_HIT_RATE",
    "PackScoreCache",
    "decide_hscoreram",
]

MIN_HIT_RATE = 0.50


@dataclass
class PackScoreCache:
    """RAM memo with optional disk persist across pack re-scores."""

    memo: TeacherLpMemo = field(default_factory=TeacherLpMemo)

    def get_or_compute(
        self,
        role: str,
        prompt: str,
        continuation: str,
        compute: Callable[[], float],
    ) -> float:
        return self.memo.get_or_compute(role, prompt, continuation, compute)

    def prime(self, role: str, prompt: str, continuation: str, lp: float) -> None:
        """Load a known score without counting hit/miss."""
        key = (str(role), str(prompt), str(continuation))
        self.memo._store[key] = float(lp)

    @property
    def forwards(self) -> int:
        return self.memo.forwards

    @property
    def hits(self) -> int:
        return self.memo.hits

    def hit_rate(self) -> float:
        return self.memo.hit_rate()

    def size(self) -> int:
        return len(self.memo._store)

    def save(self, path: Path) -> None:
        rows = [
            {
                "role": role,
                "prompt": prompt,
                "continuation": cont,
                "lp": float(lp),
            }
            for (role, prompt, cont), lp in self.memo._store.items()
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"entries": rows}, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> PackScoreCache:
        data = json.loads(path.read_text(encoding="utf-8"))
        cache = cls()
        for row in data.get("entries", []):
            cache.prime(
                str(row["role"]),
                str(row["prompt"]),
                str(row["continuation"]),
                float(row["lp"]),
            )
        return cache


def decide_hscoreram(
    *,
    cold_wall: float,
    warm_wall: float,
    cold_story: float,
    warm_story: float,
    cold_code: float,
    warm_code: float,
    hit_rate: float,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN cold vs warm pack score pass
    WHEN deciding H-SCORERAM
    THEN lp unchanged (±ε); warm wall↓; hit_rate ≥ MIN_HIT_RATE.
    """
    if abs(float(warm_story) - float(cold_story)) > float(eps_lp):
        return (
            f"KILL (story_lp drift {float(warm_story):.4f} vs "
            f"{float(cold_story):.4f})"
        )
    if abs(float(warm_code) - float(cold_code)) > float(eps_lp):
        return (
            f"KILL (code_lp drift {float(warm_code):.4f} vs "
            f"{float(cold_code):.4f})"
        )
    if not (float(warm_wall) < float(cold_wall)):
        return (
            f"KILL (warm wall {float(warm_wall):.1f} ≥ cold "
            f"{float(cold_wall):.1f})"
        )
    if float(hit_rate) < float(MIN_HIT_RATE):
        return (
            f"KILL (hit_rate {float(hit_rate):.2f} < {float(MIN_HIT_RATE):.2f})"
        )
    return (
        f"PROMOTE (SCORERAM warm wall↓ hit_rate={float(hit_rate):.2f}; "
        f"lp unchanged)"
    )
