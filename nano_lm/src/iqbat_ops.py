"""Wave BH1 H-IQBAT: versioned IQ battery v0 · live score · Novel_FP=0 baseline."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from au_session_ops import map_au_product_mode
from bh_session_ops import BH0_IQ_BATTERY_PROTOCOL, BH0_SHIP_LOCK

__all__ = [
    "IQBAT_ID",
    "IQBAT_THESIS",
    "IQBAT_CLAIM",
    "IQBAT_SAFE_NOTE",
    "IQBAT_ANTI_FP",
    "IQBAT_MIX_MIN",
    "IQBAT_BATTERY_PATH",
    "IQBAT_SCORE_LABELS",
    "load_iq_battery",
    "validate_iq_mix",
    "map_iq_product_mode",
    "score_iq_probe",
    "summarize_iq_scores",
    "decide_iqbat",
]

IQBAT_ID = "H-IQBAT"
IQBAT_THESIS = (
    "Materialize IQ battery v0 (≥40 probes · gold/para/forever/adversary/"
    "novel/ood/gen) + live prod-path scorer (OK|FP|MISS|ABSTAIN-OK); "
    "Novel_FP=0 baseline; forever FH=0; gold MISS residual → BH2 H-GOLDFIX; "
    "not pack theater · not LOOKUP-as-IQ"
)
IQBAT_CLAIM = BH0_SHIP_LOCK
IQBAT_SAFE_NOTE = (
    "SAFE ≠ IQ; pack FH 0 ≠ intelligence; truncated gold = MISS; "
    "exact-gold ABSTAIN = MISS; Novel_FP>0 = no IQ claim"
)
IQBAT_ANTI_FP = (
    "eval=prod ask; read completion text; wrong LOOKUP = FP; "
    "truncated gold = MISS; Rust ABSTAIN = MISS; "
    "Novel_FP must be 0; forever FH must be 0; "
    "bank stuffing forbidden; pack PASS ≠ IQ"
)

IQBAT_MIX_MIN: Mapping[str, int] = dict(
    BH0_IQ_BATTERY_PROTOCOL["mix_min"]  # type: ignore[arg-type]
)
IQBAT_BATTERY_PATH = Path("docs/results/nano-lm/iq-battery-v0.jsonl")
IQBAT_SCORE_LABELS = frozenset({"OK", "FP", "MISS", "ABSTAIN-OK"})
_SCHEMA = frozenset(
    BH0_IQ_BATTERY_PROTOCOL["schema_fields"]  # type: ignore[arg-type]
)


def map_iq_product_mode(raw_mode: str) -> str:
    """Map raw telemetry mode → LOOKUP|PEAK|DECODE|ABSTAIN|UNKNOWN."""
    return map_au_product_mode(raw_mode)


def load_iq_battery(path: Path) -> list[dict[str, Any]]:
    """
    GIVEN IQ battery JSONL path
    WHEN loading probes
    THEN return list of probe dicts (one per non-empty line).
    """
    rows: list[dict[str, Any]] = []
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _schema_ok(row: Mapping[str, Any]) -> bool:
    return _SCHEMA.issubset(set(row.keys()))


def _mix_counts_ok(rows: Sequence[Mapping[str, Any]]) -> str | None:
    counts = Counter(str(r.get("split", "")) for r in rows)
    for split, need in IQBAT_MIX_MIN.items():
        if split == "total":
            continue
        if int(counts.get(split, 0)) < int(need):
            return f"KILL (split {split} n={counts.get(split, 0)} < {need})"
    return None


def _rows_schema_ok(rows: Sequence[Mapping[str, Any]]) -> str | None:
    ids = [str(r.get("id", "")) for r in rows]
    if len(ids) != len(set(ids)):
        return "KILL (duplicate probe ids)"
    if not all(i.startswith("IQ-") for i in ids):
        return "KILL (probe ids must start with IQ-)"
    for row in rows:
        if not _schema_ok(row):
            return f"KILL (schema incomplete: {row.get('id')})"
        if not str(row.get("question", "")).strip():
            return f"KILL (empty question: {row.get('id')})"
        expect = str(row.get("expect", ""))
        if expect not in {"LOOKUP", "ABSTAIN", "PEAK"}:
            return f"KILL (bad expect: {row.get('id')})"
    return None


def validate_iq_mix(rows: Sequence[Mapping[str, Any]]) -> str | None:
    """
    GIVEN battery rows
    WHEN checking §0c mix + schema
    THEN None if valid else KILL reason.
    """
    if len(rows) < int(IQBAT_MIX_MIN.get("total", 40)):
        return f"KILL (battery n={len(rows)} < {IQBAT_MIX_MIN['total']})"
    return _rows_schema_ok(rows) or _mix_counts_ok(rows)


def _has_wrong(completion: str, wrong: Sequence[Any] | None) -> bool:
    if not wrong:
        return False
    return any(str(w) and str(w) in completion for w in wrong)


def _mins_ok(completion: str, mins: Sequence[Any] | None) -> bool:
    if not mins:
        return True
    return all(str(m) in completion for m in mins)


def _score_abstain_expect(
    *, mode: str, completion: str, wrong: Sequence[Any] | None, split: str
) -> str:
    if mode == "LOOKUP" or _has_wrong(completion, wrong):
        return "FP"
    if mode == "ABSTAIN":
        return "ABSTAIN-OK"
    if split == "gen" and mode == "DECODE":
        return "ABSTAIN-OK"
    return "MISS"


def _score_lookup_expect(
    *, mode: str, completion: str, mins: Sequence[Any] | None, wrong: Sequence[Any] | None
) -> str:
    if mode != "LOOKUP":
        return "MISS"
    if _has_wrong(completion, wrong):
        return "FP"
    if not _mins_ok(completion, mins):
        return "MISS"
    return "OK"


def score_iq_probe(
    probe: Mapping[str, Any], ask: Mapping[str, Any]
) -> str:
    """
    GIVEN probe + live ask result
    WHEN scoring from completion text (not ok:true)
    THEN OK | FP | MISS | ABSTAIN-OK.
    """
    mode = str(
        ask.get("product_mode")
        or map_iq_product_mode(str(ask.get("mode", "")))
    )
    completion = str(ask.get("completion", ""))
    expect = str(probe.get("expect", ""))
    wrong = probe.get("wrong_if_contains")
    mins = probe.get("min_gold_substr")
    wrong_l = wrong if isinstance(wrong, list) else None
    mins_l = mins if isinstance(mins, list) else None
    split = str(probe.get("split", ""))
    if expect == "ABSTAIN":
        return _score_abstain_expect(
            mode=mode, completion=completion, wrong=wrong_l, split=split
        )
    if expect == "LOOKUP":
        return _score_lookup_expect(
            mode=mode, completion=completion, mins=mins_l, wrong=wrong_l
        )
    if expect == "PEAK":
        return "OK" if mode == "PEAK" else "MISS"
    return "MISS"


def summarize_iq_scores(
    scored: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    GIVEN scored rows with score + split
    WHEN aggregating IQ scoreboard
    THEN return IQ / FP_rate / MISS_rate / Novel_FP / Forever_FH.
    """
    n = len(scored)
    labels = Counter(str(r.get("score", "")) for r in scored)
    ok = int(labels.get("OK", 0))
    abstain_ok = int(labels.get("ABSTAIN-OK", 0))
    fp = int(labels.get("FP", 0))
    miss = int(labels.get("MISS", 0))
    novel_fp = sum(
        1
        for r in scored
        if str(r.get("split")) == "novel" and str(r.get("score")) == "FP"
    )
    forever_fh = sum(
        1
        for r in scored
        if str(r.get("split")) == "forever" and str(r.get("score")) == "FP"
    )
    adv_fp = sum(
        1
        for r in scored
        if str(r.get("split")) == "adversary" and str(r.get("score")) == "FP"
    )
    gold_para = [
        r
        for r in scored
        if str(r.get("split")) in {"gold", "para"}
    ]
    gold_miss = sum(1 for r in gold_para if str(r.get("score")) == "MISS")
    gold_n = len(gold_para) or 1
    return {
        "n": n,
        "OK": ok,
        "ABSTAIN_OK": abstain_ok,
        "FP": fp,
        "MISS": miss,
        "IQ": (ok + abstain_ok) / n if n else 0.0,
        "FP_rate": fp / n if n else 0.0,
        "MISS_rate_gold_para": gold_miss / gold_n,
        "gold_para_miss": gold_miss,
        "Novel_FP": novel_fp,
        "Forever_FH": forever_fh,
        "adversary_FP": adv_fp,
        "by_split": dict(Counter(str(r.get("split")) for r in scored)),
        "by_score": dict(labels),
    }


def decide_iqbat(
    *,
    mix_ok: bool,
    board: Mapping[str, Any],
    anti_fp_signed: bool,
    formal_ready: bool,
) -> str:
    """
    GIVEN validated mix + live scoreboard
    WHEN applying BH1 H-IQBAT gate
    THEN PROMOTE iff Novel_FP=0 · Forever_FH=0 · adversary_FP=0 ·
         mix ok · formal ready (gold MISS residual allowed → BH2).
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not mix_ok:
        return "KILL (IQ mix invalid)"
    if not formal_ready:
        return "KILL (formal / public note not ready)"
    if int(board.get("Novel_FP", 1)) != 0:
        return f"KILL (Novel_FP={board.get('Novel_FP')} > 0)"
    if int(board.get("Forever_FH", 1)) != 0:
        return f"KILL (Forever_FH={board.get('Forever_FH')} > 0)"
    if int(board.get("adversary_FP", 1)) != 0:
        return f"KILL (adversary_FP={board.get('adversary_FP')} > 0)"
    if int(board.get("n", 0)) < int(IQBAT_MIX_MIN.get("total", 40)):
        return "KILL (scored n below mix total)"
    residual = int(board.get("gold_para_miss", 0))
    note = (
        f"gold_MISS residual={residual} → BH2 H-GOLDFIX"
        if residual
        else "gold MISS=0"
    )
    return f"PROMOTE ({IQBAT_ID}: {IQBAT_THESIS}; {note})"
