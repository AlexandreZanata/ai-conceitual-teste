"""H-SUP / H-INT: classical amplitude-weighted multi-hypothesis selection."""

from __future__ import annotations

from typing import Sequence

import torch

from scorers import pick_argmax


def amplitudes_from_scores(scores: Sequence[float], temperature: float = 1.0) -> list[float]:
    """Map scores → positive amplitudes (softmax √p style via softplus+norm)."""
    t = torch.tensor(list(scores), dtype=torch.float32)
    t = t / max(temperature, 1e-6)
    # shift for stability
    t = t - t.max()
    amp = torch.exp(0.5 * t)  # |α| ∝ exp(score/2)
    amp = amp / (amp.norm(p=2) + 1e-12)
    return [float(x) for x in amp.tolist()]


def collapse_measure(amplitudes: Sequence[float], seed: int) -> int:
    """Measure: sample index with p_i = |α_i|²."""
    a = torch.tensor(list(amplitudes), dtype=torch.float32)
    probs = a * a
    probs = probs / (probs.sum() + 1e-12)
    g = torch.Generator()
    g.manual_seed(seed)
    return int(torch.multinomial(probs, 1, generator=g).item())


def interference_scores(
    base_scores: Sequence[float], embeddings: torch.Tensor
) -> list[float]:
    """
    H-INT: adjust scores by pairwise similarity (cancel similar losers).
    embeddings: [K, D] candidate summary vectors.
    """
    k = embeddings.shape[0]
    sim = torch.nn.functional.cosine_similarity(
        embeddings.unsqueeze(1), embeddings.unsqueeze(0), dim=-1
    )
    out: list[float] = []
    for i in range(k):
        penalty = 0.0
        for j in range(k):
            if i == j:
                continue
            if base_scores[j] < base_scores[i]:
                continue
            # similar + worse peer subtracts (destructive interference toy)
            penalty += float(sim[i, j].item()) * 0.1
        out.append(float(base_scores[i]) - penalty)
    return out


def select_sup(scores: Sequence[float], seed: int, temperature: float = 1.0) -> int:
    """H-SUP collapse via |α|² (not plain argmax)."""
    amp = amplitudes_from_scores(scores, temperature)
    return collapse_measure(amp, seed)


def select_int(
    scores: Sequence[float], embeddings: torch.Tensor, seed: int
) -> int:
    """H-INT then measure."""
    adj = interference_scores(scores, embeddings)
    return select_sup(adj, seed)


def select_uniform_bon(scores: Sequence[float]) -> int:
    """Ablation control: classic argmax BoN."""
    return pick_argmax(scores)
