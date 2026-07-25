"""H-GRAPH: CUDA graph capture under LAYB decode; wall vs H-LAYB."""

from __future__ import annotations

from typing import Any, Mapping

from lat_ops import EPS_LP
from layb_ops import LAYB_CHUNK

__all__ = ["decide_hgraph", "GRAPH_CHUNK", "EPS_LP", "capture_seq_graphs"]

GRAPH_CHUNK = LAYB_CHUNK


def decide_hgraph(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-GRAPH vs H-LAYB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and wall < LAYB; else KILL.
    """
    tip = stats.get("H-LAYB")
    if tip is None:
        return "needs H-LAYB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-LAYB)"
    if float(s["mean_wall"]) >= float(tip["mean_wall"]):
        return "KILL (no wall win vs H-LAYB)"
    return "PROMOTE (CUDA graph under LAYB decode)"


def capture_seq_graphs(
    model: Any,
    *,
    batch: int,
    t0: int,
    t_max: int,
    device: Any,
    vocab: int,
) -> dict[int, tuple[Any, Any, Any, Any, Any]]:
    """
    GIVEN CUDA model and seq length range [t0, t_max]
    WHEN capturing full-depth last-token forward graphs
    THEN return T → (graph, static_ids, static_mask, static_pos, static_logits).
    """
    import torch

    if device.type != "cuda":
        raise ValueError("capture_seq_graphs requires CUDA")
    cache: dict[int, tuple[Any, Any, Any, Any, Any]] = {}
    for t in range(int(t0), int(t_max) + 1):
        s_ids = torch.zeros(batch, t, dtype=torch.long, device=device)
        s_mask = torch.zeros(batch, t, dtype=torch.long, device=device)
        s_pos = torch.zeros(batch, t, dtype=torch.long, device=device)
        s_out = torch.zeros(batch, vocab, dtype=torch.float32, device=device)
        stream = torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(2):
                with torch.no_grad():
                    logits = model(
                        s_ids, attention_mask=s_mask, position_ids=s_pos
                    ).logits[:, -1, :].float()
                    s_out.copy_(logits)
        torch.cuda.current_stream().wait_stream(stream)
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            with torch.no_grad():
                logits = model(
                    s_ids, attention_mask=s_mask, position_ids=s_pos
                ).logits[:, -1, :].float()
                s_out.copy_(logits)
        cache[t] = (graph, s_ids, s_mask, s_pos, s_out)
    return cache
