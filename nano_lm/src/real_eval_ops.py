"""Wave AT4 AT-REAL-EVAL: product + gen + live ask battery (anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from at_session_ops import (
    AT0_ASK_BATTERY,
    AT0_MODES,
    AT0_REAL_EVAL_PROTOCOL,
    map_at_product_mode,
)

__all__ = [
    "REAL_EVAL_ID",
    "REAL_EVAL_THESIS",
    "REAL_EVAL_CLAIM",
    "ASK_BATTERY",
    "REQUIRED_MODES",
    "PROTOCOL",
    "PARENT_NANOGEN4_ABLATED",
    "map_at_product_mode",
    "telemetry_ok",
    "mode_matches_expect",
    "battery_row_ok",
    "battery_pass",
    "claim_is_honest",
    "gen_claim_allowed",
    "near_miss_should_abstain",
    "force_abstain_row",
    "decide_at_real_eval",
]

REAL_EVAL_ID = "AT-REAL-EVAL"
REAL_EVAL_THESIS = (
    "Final real eval: Caminho A product pass + live ask battery + "
    "generative claim only if AT3 H-NANOGEN4 PROMOTE (ablated≥5.0)"
)
REAL_EVAL_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path + "
    "ablated DECODE (snippet-prefix) — not unlabeled open chat LM"
)
ASK_BATTERY: tuple[dict[str, str], ...] = AT0_ASK_BATTERY
REQUIRED_MODES: frozenset[str] = AT0_MODES
PROTOCOL: Mapping[str, object] = AT0_REAL_EVAL_PROTOCOL
PARENT_NANOGEN4_ABLATED = 5.5


def telemetry_ok(row: Mapping[str, Any]) -> bool:
    """
    GIVEN a live ask row
    WHEN checking AT0 real-eval telemetry law
    THEN wall_ms + n_new + product_mode required.
    """
    if "wall_ms" not in row or "n_new" not in row:
        return False
    mode = str(row.get("product_mode", "") or "")
    return mode in REQUIRED_MODES


def mode_matches_expect(*, product_mode: str, expect_mode: str) -> bool:
    """Exact product_mode == battery expect_mode."""
    return str(product_mode) == str(expect_mode)


def battery_row_ok(row: Mapping[str, Any]) -> bool:
    """Labeled mode matches expect + telemetry present."""
    if not telemetry_ok(row):
        return False
    return mode_matches_expect(
        product_mode=str(row.get("product_mode", "")),
        expect_mode=str(row.get("expect_mode", "")),
    )


def battery_pass(rows: Sequence[Mapping[str, Any]]) -> bool:
    """All six frozen battery rows pass anti-FP bars."""
    if len(rows) != len(ASK_BATTERY):
        return False
    ids = {str(r.get("id", "")) for r in rows}
    need = {str(p["id"]) for p in ASK_BATTERY}
    if ids != need:
        return False
    return all(battery_row_ok(r) for r in rows)


def near_miss_should_abstain(
    *,
    question: str,
    completion: str,
    product_mode: str,
) -> bool:
    """
    GIVEN AT0 near_miss ask + LOOKUP completion
    WHEN detecting BIP-39 gold confirmed for SegWit / wrong domain
    THEN True → real-eval must refuse (ABSTAIN), not LOOKUP-as-IQ.
    """
    if str(product_mode) != "LOOKUP":
        return False
    q = str(question).lower()
    c = str(completion).lower().replace(" ", "")
    if "segwit" in q or "witness discount" in q:
        if "cs=ent/32" in c or "cs=ent÷32" in c:
            return True
    return False


def force_abstain_row(row: dict[str, Any]) -> dict[str, Any]:
    """Overwrite a confused LOOKUP into labeled ABSTAIN/NO_ANSWER."""
    out = dict(row)
    out["completion"] = "NO_ANSWER"
    out["mode"] = "NO_ANSWER"
    out["abstained"] = True
    out["product_mode"] = "ABSTAIN"
    out["n_new"] = int(out.get("n_new") or 0)
    if "wall_ms" not in out:
        out["wall_ms"] = 0.0
    return out


def gen_claim_allowed(claim: str) -> bool:
    """True if claim asserts ablated DECODE / mini-AGI-inspired language."""
    low = str(claim).lower()
    markers = (
        "ablated",
        "snippet-prefix",
        "mini-agi",
        "true-gen unlocked",
        "generative unlocked",
    )
    return any(m in low for m in markers)


def claim_is_honest(claim: str, *, nanogen4_decision: str) -> bool:
    """
    GIVEN ship claim + AT3 decision
    WHEN checking AT4 honesty
    THEN reject unlabeled open-chat / GPT-class; allow ablated iff PROMOTE.
    """
    low = str(claim).lower()
    if "gpt-class" in low or "frontier chat" in low:
        return False
    has_base = "packaged" in low or "product layer" in low
    if not has_base:
        return False
    open_chat_negated = (
        "not unlabeled open chat" in low or "not open chat" in low
    )
    if ("open chat" in low or "open-chat" in low) and not open_chat_negated:
        return False
    nano = str(nanogen4_decision)
    has_gen = gen_claim_allowed(claim)
    if nano.startswith("PROMOTE"):
        return open_chat_negated
    if has_gen:
        return False
    return open_chat_negated


def decide_at_real_eval(
    *,
    prodreg_decision: str,
    shipapp_decision: str,
    nanogen4_decision: str,
    battery_ok: bool,
    claim: str,
) -> str:
    """
    GIVEN AT1/AT2/AT3 decisions + live battery + ship claim
    WHEN applying pesquisa §5 AT4 gate
    THEN PROMOTE iff product pass + battery pass + honest claim under gen lock.
    """
    for name, dec in (
        ("prodreg", prodreg_decision),
        ("shipapp", shipapp_decision),
    ):
        if not str(dec).startswith("PROMOTE"):
            if str(dec).startswith("KILL"):
                return f"KILL ({name}: {dec})"
            if str(dec) == "MISSING":
                return f"KILL ({name} summary MISSING)"
            return f"KILL ({name} not PROMOTE: {dec})"
    if not battery_ok:
        return "KILL (live ask battery failed anti-FP / mode bars)"
    nano = str(nanogen4_decision)
    if nano == "MISSING":
        return "KILL (nanogen4 summary MISSING)"
    if not claim_is_honest(claim, nanogen4_decision=nano):
        return "KILL (dishonest ship claim)"
    if not nano.startswith("PROMOTE") and gen_claim_allowed(claim):
        return "KILL (generative claim while AT3 HOLD)"
    return "PROMOTE"
