"""RPS niche helpers for H-RPS: cyclic dominance over 3 niches."""

from __future__ import annotations

from typing import Sequence


NICHES = (0, 1, 2)  # rock, paper, scissors


def rps_beats(a: int, b: int) -> int:
    """
    GIVEN niches a, b in {0,1,2}
    WHEN comparing cyclic dominance
    THEN 1 if a beats b, -1 if b beats a, 0 if tie.
    Rule: each niche beats the previous (mod 3).
    """
    if a not in NICHES or b not in NICHES:
        raise ValueError("rps_beats: niche must be in {0,1,2}")
    if a == b:
        return 0
    return 1 if (a - b) % 3 == 1 else -1


def niche_adjusted_fitness(
    raw_fits: Sequence[float],
    niches: Sequence[int],
    *,
    bonus: float = 0.1,
) -> list[float]:
    """
    GIVEN raw fitness and niche tags
    WHEN applying RPS contests
    THEN each score = raw + bonus * (# opponents this niche beats).
    """
    n = len(raw_fits)
    if n != len(niches):
        raise ValueError("niche_adjusted_fitness: length mismatch")
    out: list[float] = []
    for i in range(n):
        wins = sum(
            1
            for j in range(n)
            if j != i and rps_beats(niches[i], niches[j]) == 1
        )
        out.append(float(raw_fits[i]) + bonus * wins)
    return out


def niche_collapsed(niches: Sequence[int]) -> bool:
    """True iff population has fewer than 2 distinct niches."""
    return len(set(niches)) < 2


def mutate_niche(niche: int, rng_roll: float, *, p_mut: float = 0.2) -> int:
    """
    GIVEN current niche and a Uniform[0,1] roll
    WHEN mutating
    THEN with prob p_mut jump to a different niche; else keep.
    """
    if not 0.0 <= p_mut <= 1.0:
        raise ValueError("mutate_niche: p_mut must be in [0,1]")
    if niche not in NICHES:
        raise ValueError("mutate_niche: bad niche")
    if rng_roll >= p_mut:
        return niche
    # Deterministic alternate: pick next niche (not random — caller supplies roll only for gate)
    return (niche + 1) % 3
