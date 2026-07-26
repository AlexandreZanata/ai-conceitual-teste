"""Wave AG1 H-ANTIFP: forbid intelligence PROMOTE from LOOKUP-only."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "ANTIFP_ID",
    "ANTIFP_THESIS",
    "LOOKUP_MODES",
    "extract_telemetry",
    "classify_arm",
    "lookup_arm_ok",
    "gen_arm_ok",
    "intelligence_promote_allowed",
    "score_antifp_completion",
    "antifp_stats",
    "decide_antifp",
]

ANTIFP_ID = "H-ANTIFP"
ANTIFP_THESIS = (
    "Harness anti-FP: LOOKUP ≠ generative IQ; log mode/wall_ms/n_new; "
    "forbid intelligence PROMOTE from LOOKUP-only"
)

LOOKUP_MODES: frozenset[str] = frozenset(
    {"WRAP_LOOKUP", "SEMWRAP_LOOKUP"}
)


def extract_telemetry(payload: Mapping[str, Any]) -> dict[str, Any]:
    """
    GIVEN ask payload
    WHEN extracting anti-FP telemetry
    THEN return mode, wall_ms, n_new (defaults safe for missing keys).
    """
    mode = str(payload.get("mode", "") or "").strip()
    wall = payload.get("wall_ms")
    n_new = payload.get("n_new")
    try:
        wall_f = float(wall) if wall is not None else 0.0
    except (TypeError, ValueError):
        wall_f = 0.0
    try:
        n_i = int(n_new) if n_new is not None else 0
    except (TypeError, ValueError):
        n_i = 0
    return {"mode": mode, "wall_ms": wall_f, "n_new": n_i}


def classify_arm(payload: Mapping[str, Any]) -> str:
    """
    GIVEN ask telemetry
    WHEN classifying product arm
    THEN LOOKUP | GENERATE | UNKNOWN (LOOKUP never equals GENERATE).
    """
    tel = extract_telemetry(payload)
    mode = tel["mode"]
    if mode in LOOKUP_MODES:
        return "LOOKUP"
    if tel["wall_ms"] > 0.0 and tel["n_new"] > 0:
        return "GENERATE"
    if mode in {"WRAP_DECODE", "QT+EARLY n=1"}:
        return "GENERATE"
    return "UNKNOWN"


def lookup_arm_ok(payload: Mapping[str, Any]) -> bool:
    """
    GIVEN LOOKUP smoke payload
    WHEN validating anti-FP lookup contract
    THEN True iff labeled LOOKUP mode and arm class is LOOKUP.
    """
    tel = extract_telemetry(payload)
    return tel["mode"] in LOOKUP_MODES and classify_arm(payload) == "LOOKUP"


def gen_arm_ok(payload: Mapping[str, Any]) -> bool:
    """
    GIVEN generative smoke payload
    WHEN validating anti-FP generative contract
    THEN True iff arm is GENERATE with wall_ms>0 and n_new>0.
    """
    tel = extract_telemetry(payload)
    if classify_arm(payload) != "GENERATE":
        return False
    if tel["mode"] in LOOKUP_MODES:
        return False
    return tel["wall_ms"] > 0.0 and tel["n_new"] > 0


def intelligence_promote_allowed(
    *,
    lookup_logged: bool,
    gen_logged: bool,
    claim: str,
) -> bool:
    """
    GIVEN dual-arm log flags + claim text
    WHEN deciding if intelligence/smarter-model PROMOTE is allowed
    THEN False if LOOKUP-only or claim hides retrieval as generative IQ.
    """
    low = str(claim).lower()
    iq_claim = any(
        k in low
        for k in (
            "smarter",
            "intelligence",
            "open chat",
            "generative iq",
            "model iq",
        )
    )
    if not iq_claim:
        # Product LOOKUP / harness-only claims may promote without gen arm.
        return True
    if "not open chat" in low or "not generative" in low:
        if "smarter" not in low and "intelligence" not in low:
            return True
    if lookup_logged and not gen_logged:
        return False
    return bool(gen_logged)


def score_antifp_completion(
    *,
    arm: str,
    completion: str,
    gold: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN dual-arm completion
    WHEN Cursor-style EVAL (not auto TRUE_HIT→9 as generative IQ)
    THEN score text vs gold; LOOKUP hits stay labeled product-not-IQ.
    """
    text = str(completion).strip()
    g = str(gold).strip()
    if arm == "LOOKUP" and text and g and text == g:
        return (
            9.0,
            False,
            [
                "LOOKUP completion matched bank gold",
                "labeled WRAP_LOOKUP — not generative IQ",
                "product retrieval path only",
            ],
        )
    if arm == "LOOKUP" and text and g and g in text:
        return (
            8.0,
            False,
            [
                "LOOKUP completion contains gold",
                "labeled retrieval — not generative IQ",
                "in-scope product path",
            ],
        )
    if set(text) <= {".", " "} or text in {"", "........"}:
        return (
            1.0,
            True,
            [
                "completion is period collapse or empty",
                "fails correctness vs curated gold",
                "generative arm evidence — not IQ PROMOTE",
            ],
        )
    if text and g and text == g:
        return (
            7.0,
            False,
            [
                "generative completion matched gold",
                "score from text — not LOOKUP auto-9",
                "in-scope",
            ],
        )
    return (
        3.0,
        True,
        [
            "completion does not match curated gold",
            "factual miss or partial — mark error",
            f"arm={arm}; do not claim LOOKUP as gen IQ",
        ],
    )


def antifp_stats(
    *,
    lookup_ok: bool,
    gen_ok: bool,
    arms_distinct: bool,
    iq_gate_rejects_lookup_only: bool,
    iq_gate_allows_dual: bool,
    telemetry_complete: bool,
    n_lookup_trials: int,
    n_gen_trials: int,
) -> dict[str, Any]:
    """
    GIVEN smoke flags
    WHEN summarizing H-ANTIFP
    THEN pack gate inputs for decide_antifp.
    """
    return {
        "lookup_ok": bool(lookup_ok),
        "gen_ok": bool(gen_ok),
        "arms_distinct": bool(arms_distinct),
        "iq_gate_rejects_lookup_only": bool(iq_gate_rejects_lookup_only),
        "iq_gate_allows_dual": bool(iq_gate_allows_dual),
        "telemetry_complete": bool(telemetry_complete),
        "n_lookup_trials": int(n_lookup_trials),
        "n_gen_trials": int(n_gen_trials),
        "hyp_id": ANTIFP_ID,
        "thesis": ANTIFP_THESIS,
    }


def decide_antifp(stats: Mapping[str, Any]) -> str:
    """
    GIVEN antifp_stats
    WHEN applying pesquisa §5 AG1 gate
    THEN PROMOTE iff LOOKUP≠GEN labeled, raw gen arm runs, IQ gate works.
    """
    need = (
        "lookup_ok",
        "gen_ok",
        "arms_distinct",
        "iq_gate_rejects_lookup_only",
        "iq_gate_allows_dual",
        "telemetry_complete",
    )
    for key in need:
        if not bool(stats.get(key)):
            return f"KILL (antifp fail: {key})"
    if int(stats.get("n_lookup_trials", 0)) < 1:
        return "KILL (no LOOKUP smoke trial)"
    if int(stats.get("n_gen_trials", 0)) < 1:
        return "KILL (no GENERATE smoke trial)"
    return f"PROMOTE ({ANTIFP_ID}: {ANTIFP_THESIS})"
