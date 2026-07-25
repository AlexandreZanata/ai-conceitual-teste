"""Prompt transforms for H-GENC genomes (stride window + optional Jaccard fill)."""

from __future__ import annotations

from pathlib import Path

__all__ = [
    "stride_window",
    "jaccard",
    "top_k_chunks",
    "load_prog_chunks",
    "apply_genc_prompt",
]


def stride_window(text: str, *, stride: int, chunk_len: int) -> str:
    """
    GIVEN prompt text and stride/chunk gene
    WHEN selecting a serve window
    THEN keep the last min(len, max(chunk_len, stride)) chars (char surrogate).
    """
    n = max(int(chunk_len), int(stride))
    n = max(1, n)
    if len(text) <= n:
        return text
    return text[-n:]


def jaccard(a: str, b: str) -> float:
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / float(len(ta | tb))


def top_k_chunks(query: str, chunks: list[str], k: int) -> list[str]:
    """Return top-k chunks by Jaccard (k≤0 → empty)."""
    kk = int(k)
    if kk < 1 or not chunks:
        return []
    scored = sorted(
        ((jaccard(query, c), i, c) for i, c in enumerate(chunks)),
        key=lambda t: (-t[0], t[1]),
    )
    return [c for _, _, c in scored[:kk]]


def load_prog_chunks(root: Path, *, max_chunks: int = 256, win: int = 256) -> list[str]:
    """Load short programming curated windows (empty if missing)."""
    prog = root / "programming"
    if not prog.is_dir():
        return []
    out: list[str] = []
    for path in sorted(prog.rglob("*.md")) + sorted(prog.rglob("*.txt")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i in range(0, len(text), win):
            piece = text[i : i + win].strip()
            if len(piece) >= 40:
                out.append(piece)
            if len(out) >= int(max_chunks):
                return out
    return out


def apply_genc_prompt(
    task: str,
    *,
    k_retrieve: int,
    chunks: list[str],
    stride: int,
    chunk_len: int,
) -> str:
    """
    GIVEN task prompt and retrieve/stride genes
    WHEN building decode context
    THEN optional Jaccard prepend + stride window (not a RAG PROMOTE claim).
    """
    filled = task
    hits = top_k_chunks(task, chunks, int(k_retrieve))
    if hits:
        filled = "\n\n".join(hits) + "\n\n" + task
    return stride_window(filled, stride=int(stride), chunk_len=int(chunk_len))
