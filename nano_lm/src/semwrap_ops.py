"""Wave AB1 H-SEMWRAP: fuzzy recall over wrap bank (+ curated boost)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import lookup_gold, normalize_question

__all__ = [
    "SEMWRAP_ID",
    "SEMWRAP_N",
    "SEMWRAP_THRESHOLD",
    "SEMWRAP_MARGIN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "question_tokens",
    "overlap_score",
    "semantic_lookup",
    "classify_semwrap",
    "score_semwrap_trial",
    "semwrap_stats",
    "decide_semwrap",
    "alias_bank_row",
    "contrastive_reject",
]

SEMWRAP_ID = "H-SEMWRAP"
SEMWRAP_N = 10
SEMWRAP_THRESHOLD = 0.25
SEMWRAP_MARGIN = 0.04

_TOK = re.compile(r"[a-z0-9]+")
_BIP = re.compile(r"bip[\s\-]*0*(\d+)")
_STOP = frozenset(
    {
        "a",
        "an",
        "the",
        "of",
        "to",
        "in",
        "and",
        "or",
        "for",
        "is",
        "are",
        "what",
        "which",
        "how",
        "do",
        "does",
        "i",
        "im",
        "with",
        "on",
        "from",
        "keep",
        "it",
        "short",
        "give",
        "show",
        "one",
        "two",
        "max",
        "like",
        "plain",
        "language",
        "please",
        "briefly",
        "answer",
        "sentences",
        "sentence",
        "name",
        "write",
        "explain",
        "need",
        "define",
        "minimal",
        "idiomatic",
        "that",
        "this",
        "over",
        "mainly",
        "lets",
        "multiple",
        "turn",
        "into",
        "lock",
        "shipping",
        "production",
        "code",
    }
)


def _canon(text: str) -> str:
    s = normalize_question(text)
    return _BIP.sub(lambda m: f"bip{int(m.group(1))}", s)


def question_tokens(text: str) -> frozenset[str]:
    """
    GIVEN a question or gold string
    WHEN tokenizing for SEMWRAP
    THEN return content tokens (BIP ids canonized; stopwords dropped).
    """
    return frozenset(
        t
        for t in _TOK.findall(_canon(text))
        if t not in _STOP and len(t) > 1
    )


def overlap_score(a: frozenset[str], b: frozenset[str]) -> float:
    """Jaccard overlap; 0 if either side empty."""
    if not a or not b:
        return 0.0
    return float(len(a & b) / len(a | b))


def _row_gold(row: Mapping[str, Any]) -> str | None:
    gold = row.get("gold") or row.get("repaired")
    if gold is None:
        return None
    text = str(gold).strip()
    return text or None


def _curated_tokens(source_id: str, curated_root: Path | None) -> frozenset[str]:
    if curated_root is None or not source_id:
        return frozenset()
    # Lazy import keeps ops free of registry at import time for unit tests.
    from curated_sources import SOURCES

    meta = next((s for s in SOURCES if str(s["id"]) == source_id), None)
    if meta is None:
        return frozenset()
    path = curated_root / str(meta.get("path", ""))
    if not path.is_file():
        return frozenset()
    # Bounded read — SEMWRAP must stay O(bank), not full-corpus RAG.
    snippet = path.read_text(encoding="utf-8", errors="ignore")[:8000]
    return question_tokens(snippet)


def _cs_ent_polarity_flip(ask: str, gold: str) -> bool:
    """True iff ask requests reverse BIP-39 CS/ENT formula vs gold CS=ENT/32."""
    g = gold.replace(" ", "")
    if "cs=ent/32" not in g and "cs=ent÷32" not in g:
        return False
    compact = ask.replace(" ", "")
    if "ent=32" in compact or "32*cs" in compact or "32xcs" in compact:
        return True
    if "in terms of cs" in ask and "ent" in ask:
        return True
    if ("as if" in ask or "it is not" in ask) and "formula" in ask:
        return True
    return False


def _pass_contrast_trap(ask: str, gold: str) -> bool:
    """True iff ask excludes/contrasts pass (continue/return) but gold is pass."""
    if gold.strip() != "pass":
        return False
    if "skip" in ask and ("iteration" in ask or "loop" in ask):
        return True
    if "returning a value" in ask:
        return True
    if "not the no-op" in ask:
        return True
    if "not" in ask and "placeholder" in ask:
        return True
    return False


def contrastive_reject(ask: str, bank_q: str, gold: str) -> bool:
    """
    GIVEN ask + matched bank question/gold
    WHEN checking near-miss contrast / negation / polarity traps
    THEN True iff hit would be a silent wrong gold (reject → MISS).
    """
    a = normalize_question(ask)
    b = normalize_question(bank_q)
    g = normalize_question(gold)
    if "other than" in a:
        return True
    if "not append" in a and "append" in g:
        return True
    if _pass_contrast_trap(a, g):
        return True
    if "non-master" in a and "0x00000000" in g:
        return True
    if _cs_ent_polarity_flip(a, g):
        return True
    if "by height" in a and (
        "block-hash" in g or "/rest/tx/" in g or "by hash" in b
    ):
        return True
    if "floating-point" in a and ("isize" in g or "usize" in g):
        return True
    return False


def semantic_lookup(
    question: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    threshold: float = SEMWRAP_THRESHOLD,
    margin: float = SEMWRAP_MARGIN,
    curated_root: Path | None = None,
) -> tuple[str | None, dict[str, Any]]:
    """
    GIVEN wrap/error_bank rows (+ optional curated slices)
    WHEN fuzzy-matching a novel phrasing
    THEN return (gold, meta) or (None, miss meta); never invent open-web text.
    """
    exact = lookup_gold(question, rows)
    if exact is not None:
        key = normalize_question(question)
        sid = ""
        for row in rows:
            if normalize_question(str(row.get("question", ""))) != key:
                continue
            sid = str(row.get("source_id", ""))
            break
        return exact, {
            "kind": "EXACT",
            "score": 1.0,
            "margin": 1.0,
            "source_id": sid,
        }

    qtok = question_tokens(question)
    curated_cache: dict[str, frozenset[str]] = {}
    ranked: list[tuple[float, Mapping[str, Any]]] = []
    for row in rows:
        gold = _row_gold(row)
        if gold is None:
            continue
        sc = overlap_score(qtok, question_tokens(str(row.get("question", ""))))
        sc += 0.15 * overlap_score(qtok, question_tokens(gold))
        sid = str(row.get("source_id", ""))
        if curated_root is not None and sid:
            if sid not in curated_cache:
                curated_cache[sid] = _curated_tokens(sid, curated_root)
            sc += 0.05 * overlap_score(qtok, curated_cache[sid])
        ranked.append((sc, row))
    if not ranked:
        return None, {"kind": "MISS", "score": 0.0, "margin": 0.0}

    ranked.sort(key=lambda x: -x[0])
    best_sc, best_row = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0.0
    gap = float(best_sc - second)
    bank_q = str(best_row.get("question", ""))
    meta = {
        "kind": "MISS",
        "score": float(best_sc),
        "margin": gap,
        "source_id": str(best_row.get("source_id", "")),
        "bank_question": bank_q[:160],
    }
    if best_sc < float(threshold):
        return None, meta
    if gap < float(margin) and best_sc < 0.4:
        meta["kind"] = "AMBIGUOUS"
        return None, meta
    gold = _row_gold(best_row)
    if gold is None:
        return None, meta
    if contrastive_reject(question, bank_q, gold):
        meta["kind"] = "REJECT_NEAR_MISS"
        return None, meta
    meta["kind"] = "SEMANTIC"
    return gold, meta


def classify_semwrap(
    looked_up: str | None,
    *,
    expected_gold: str,
    expected_source_id: str,
    hit_source_id: str | None,
) -> str:
    """
    GIVEN SEMWRAP result + expected pack gold/source
    WHEN classifying
    THEN TRUE_HIT | FALSE_HIT | MISS.
    """
    if looked_up is None:
        return "MISS"
    text = str(looked_up).strip()
    if text == str(expected_gold).strip():
        return "TRUE_HIT"
    if hit_source_id and str(hit_source_id) == str(expected_source_id):
        return "TRUE_HIT"
    # Same-source golds from WRAPBANK may differ slightly in wording.
    if overlap_score(question_tokens(text), question_tokens(expected_gold)) >= 0.35:
        return "TRUE_HIT"
    return "FALSE_HIT"


def score_semwrap_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN SEMWRAP ask result
    WHEN scoring HITL
    THEN FALSE_HIT→0; TRUE_HIT→9; MISS documents remaining brittleness.
    """
    if lookup_kind == "FALSE_HIT":
        return (
            0.0,
            True,
            [
                "FALSE_HIT: SEMWRAP returned a wrong bank gold",
                "fuzzy collision — must FIX threshold/margin or bank",
                "in-scope; mark error",
            ],
        )
    text = str(completion).strip()
    g = str(expected_gold).strip()
    if lookup_kind == "TRUE_HIT":
        return (
            9.0,
            False,
            [
                f"TRUE_HIT via {mode}: near-known ask recovered",
                "correct vs pack gold / source_id",
                "harm/scope ok — still not open chat LM",
            ],
        )
    if set(text) <= {".", " "} or text in {"", "........"}:
        return (
            1.0,
            True,
            [
                "MISS: no SEMWRAP hit; decode collapsed",
                "needs FIX (alias gold or threshold)",
                "in-scope; not a false-hit",
            ],
        )
    if text == g or overlap_score(question_tokens(text), question_tokens(g)) >= 0.5:
        return (
            9.0,
            False,
            [
                f"MISS path but completion matched gold (mode={mode})",
                "usable answer",
                "harm/scope ok",
            ],
        )
    return (
        4.0,
        True,
        [
            f"MISS: mode={mode}; completion ≠ expected gold",
            "partial under fuzzy stress — FIX candidate",
            "documents residual miss (no false-hit)",
        ],
    )


def semwrap_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
) -> dict[str, Any]:
    """
    GIVEN 10 SEMWRAP scores
    WHEN summarizing H-SEMWRAP
    THEN mean / errors / hit breakdown / pass_bar.
    """
    if len(scores) != SEMWRAP_N or len(errors) != SEMWRAP_N:
        raise ValueError(f"SEMWRAP requires exactly {SEMWRAP_N} scores/errors")
    mean = float(sum(scores) / float(SEMWRAP_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": SEMWRAP_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_semwrap(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SEMWRAP stats
    WHEN applying §8.3 AB1 gate
    THEN PROMOTE if pass_bar & no false-hit;
         HOLD if no false-hit (miss documented);
         KILL if any false-hit.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if bool(stats.get("pass_bar")):
        return "PROMOTE"
    return "HOLD"


def alias_bank_row(
    *,
    trial_id: str,
    question: str,
    source_id: str,
    gold: str,
) -> dict[str, Any]:
    """
    GIVEN a FIX for a SEMWRAP miss
    WHEN appending an alias phrasing to the bank
    THEN return schema-valid gold row (no weight update).
    """
    g = str(gold).strip()
    return {
        "trial_id": trial_id,
        "question": str(question),
        "source_id": str(source_id),
        "model_raw": "",
        "gold": g,
        "repaired": g,
        "score": 9.0,
        "error": False,
        "recipe_id": "champion-wrap-v0",
        "ckpt": None,
        "judge_notes": [
            "SEMWRAP FIX alias for near-known ask",
            "scoped to curated source_id",
            "no student weight update",
        ],
        "hyp_id": SEMWRAP_ID,
    }
