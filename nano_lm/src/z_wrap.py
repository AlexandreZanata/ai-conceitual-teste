"""Wave Z2 wrap: gene-temp ask knobs + few-shot + error-bank lookup."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from early_ops import clamp_early_gene

__all__ = [
    "WRAP_ID",
    "normalize_question",
    "load_bank_rows",
    "lookup_gold",
    "build_fewshot_prompt",
    "wrap_ask_gene",
    "default_wrap_card",
]

WRAP_ID = "champion-wrap-v0"
_SPACE = re.compile(r"\s+")


def normalize_question(text: str) -> str:
    """Collapse whitespace for exact bank lookup."""
    return _SPACE.sub(" ", str(text).strip()).lower()


def load_bank_rows(path: Path) -> list[dict[str, Any]]:
    """Load error_bank.jsonl rows (skip blank lines)."""
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def lookup_gold(question: str, rows: Sequence[Mapping[str, Any]]) -> str | None:
    """
    GIVEN error-bank rows grown from HITL
    WHEN question matches a bank question (normalized)
    THEN return gold/repaired text (wrapper hit); else None.
    """
    key = normalize_question(question)
    for row in rows:
        if normalize_question(str(row.get("question", ""))) != key:
            continue
        gold = row.get("gold") or row.get("repaired")
        if gold is None:
            continue
        text = str(gold).strip()
        if text:
            return text
    return None


def build_fewshot_prompt(
    question: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    k: int = 3,
) -> str:
    """
    GIVEN bank golds
    WHEN wrapping a novel question
    THEN prepend up to k Q/A shots excluding the same question.
    """
    key = normalize_question(question)
    shots: list[Mapping[str, Any]] = []
    for row in rows:
        if normalize_question(str(row.get("question", ""))) == key:
            continue
        gold = row.get("gold") or row.get("repaired")
        if not gold:
            continue
        shots.append(row)
        if len(shots) >= int(k):
            break
    parts: list[str] = []
    for row in shots:
        gold = str(row.get("gold") or row.get("repaired")).rstrip()
        parts.append(f"Q: {row['question']}\nA: {gold}\n")
    parts.append(f"Q: {question}\nA:")
    return "\n".join(parts)


def wrap_ask_gene(raw_gene: Mapping[str, Any]) -> dict[str, Any]:
    """
    GIVEN EARLY best_gene
    WHEN building Z2 interactive ask knobs
    THEN keep gene temperature; disable early-exit (conf=1, patience=99).
    """
    gene = clamp_early_gene({**dict(raw_gene), "n": 1})
    gene["conf_threshold"] = 1.0
    gene["patience"] = 99
    gene["min_new"] = max(16, int(gene["min_new"]))
    return gene


def default_wrap_card() -> dict[str, Any]:
    """Public wrap card written under champion/wrap.json."""
    return {
        "wrap_id": WRAP_ID,
        "from_stage": "Z2",
        "lookup": True,
        "fewshot_k": 3,
        "ask": {
            "use_gene_temperature": True,
            "force_greedy_1e-6": False,
            "early_exit": False,
            "conf_threshold": 1.0,
            "patience": 99,
            "max_new": 64,
        },
        "note": (
            "Bank lookup answers known HITL failures; decode path still "
            "near-uniform without Z3 retrain."
        ),
    }
