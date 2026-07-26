"""Wave AC2 H-SMARTPLUS: hard paraphrase SEMWRAP + ASKSMART routing."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ac_session_ops import AC0_PACK
from asksmart_ops import is_period_collapse, strip_stop
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTPLUS_ID",
    "SMARTPLUS_N",
    "SMARTPLUS_PACK",
    "MIN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "paraphrase_collides_parents",
    "route_smartplus",
    "score_smartplus_trial",
    "smartplus_stats",
    "decide_smartplus",
]

SMARTPLUS_ID = "H-SMARTPLUS"
SMARTPLUS_N = 10
MIN_MEAN = 7.0  # §12.1 AC2

# Hard paraphrases of AC0 (normalize ≠ parent; same gold + source_id).
SMARTPLUS_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AC-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "parent_question": AC0_PACK[0]["question"],
        "paraphrase": (
            "BIP-32 HD wallets: which child-key indices are the hardened ones? "
            "Answer briefly."
        ),
        "gold": AC0_PACK[0]["gold"],
    },
    {
        "id": "AC-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0001",
        "parent_question": AC0_PACK[1]["question"],
        "paraphrase": (
            "Define BIP for Bitcoin readers — who is the audience, in ≤2 sentences?"
        ),
        "gold": AC0_PACK[1]["gold"],
    },
    {
        "id": "AC-HITL-03",
        "app_id": "known-ask",
        "source_id": "python-tutorial-control",
        "parent_question": AC0_PACK[2]["question"],
        "paraphrase": (
            "If I run for i in range(3): print(i), which integers show up and in "
            "what order?"
        ),
        "gold": AC0_PACK[2]["gold"],
    },
    {
        "id": "AC-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "parent_question": AC0_PACK[3]["question"],
        "paraphrase": (
            "Minimal Python Point class: constructor takes x and y and stores both "
            "on self."
        ),
        "gold": AC0_PACK[3]["gold"],
    },
    {
        "id": "AC-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-intro",
        "parent_question": AC0_PACK[4]["question"],
        "paraphrase": (
            "One-line Python: a function named add that returns a plus b."
        ),
        "gold": AC0_PACK[4]["gold"],
    },
    {
        "id": "AC-HITL-06",
        "app_id": "howto",
        "source_id": "rust-book-ch03",
        "parent_question": AC0_PACK[5]["question"],
        "paraphrase": (
            "Rust one-liner: mutable integer variable x initialized to five."
        ),
        "gold": AC0_PACK[5]["gold"],
    },
    {
        "id": "AC-HITL-07",
        "app_id": "long-doc",
        "source_id": "rust-book-ch03-02",
        "parent_question": AC0_PACK[6]["question"],
        "paraphrase": (
            "Per the Rust book data-types chapter, what are the two type subsets?"
        ),
        "gold": AC0_PACK[6]["gold"],
    },
    {
        "id": "AC-HITL-08",
        "app_id": "long-doc",
        "source_id": "bip-0039",
        "parent_question": AC0_PACK[7]["question"],
        "paraphrase": (
            "BIP-39 ‘seed words’ — practically, how does entropy become a wallet seed?"
        ),
        "gold": AC0_PACK[7]["gold"],
    },
    {
        "id": "AC-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "parent_question": AC0_PACK[8]["question"],
        "paraphrase": (
            "Bitcoin Core: which flag/option enables the unauthenticated REST API?"
        ),
        "gold": AC0_PACK[8]["gold"],
    },
    {
        "id": "AC-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8446",
        "parent_question": AC0_PACK[9]["question"],
        "paraphrase": (
            "TLS 1.3 handshake (RFC 8446): in plain terms, what shared outcome is "
            "it establishing?"
        ),
        "gold": AC0_PACK[9]["gold"],
    },
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTPLUS pack
    WHEN checking hard-paraphrase rule
    THEN True iff every paraphrase normalize-key ≠ parent question.
    """
    rows = pack if pack is not None else SMARTPLUS_PACK
    if len(rows) != SMARTPLUS_N:
        return False
    for item in rows:
        p = normalize_question(str(item.get("paraphrase", "")))
        parent = normalize_question(str(item.get("parent_question", "")))
        if not p or not parent or p == parent:
            return False
    return True


def paraphrase_collides_parents(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """Return paraphrase ids that collide with their parent normalize key."""
    rows = pack if pack is not None else SMARTPLUS_PACK
    bad: list[str] = []
    for item in rows:
        p = normalize_question(str(item.get("paraphrase", "")))
        parent = normalize_question(str(item.get("parent_question", "")))
        if p == parent:
            bad.append(str(item.get("id", "")))
    return bad


def route_smartplus(completion: str, *, mode: str) -> tuple[str, str]:
    """
    GIVEN raw ask completion + mode
    WHEN applying ASKSMART stop/anti-period polish
    THEN return (cleaned_text, route_label).
    """
    cleaned = strip_stop(completion)
    mode_u = str(mode).upper()
    if "SEMWRAP" in mode_u or "ASKFAST" in mode_u or "WRAP" in mode_u:
        route = "SEMWRAP_ROUTE"
    elif is_period_collapse(cleaned):
        route = "PERIOD_BLOCK"
    else:
        route = "ASKSMART_POLISH"
    return cleaned, route


def score_smartplus_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    route: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN SMARTPLUS paraphrase ask
    WHEN scoring HITL
    THEN FALSE_HIT→0; TRUE_HIT→9; MISS/period documented as errors.
    """
    from semwrap_ops import score_semwrap_trial

    text, _r = route_smartplus(completion, mode=mode)
    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=text,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + [
        f"route={route}",
        "SMARTPLUS hard paraphrase — SEMWRAP+ASKSMART; not open chat",
    ]
    if route == "PERIOD_BLOCK" and not err:
        return 1.0, True, notes + ["FIX: period collapse under paraphrase"]
    return score, err, notes


def smartplus_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    n_semwrap_route: int,
    n_fix: int,
) -> dict[str, Any]:
    """
    GIVEN 10 SMARTPLUS scores
    WHEN summarizing AC2
    THEN mean≥7 · false-hit≈0 gates.
    """
    if len(scores) != SMARTPLUS_N or len(errors) != SMARTPLUS_N:
        raise ValueError(
            f"SMARTPLUS requires exactly {SMARTPLUS_N} scores/errors"
        )
    mean = float(sum(scores) / float(SMARTPLUS_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": SMARTPLUS_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_semwrap_route": int(n_semwrap_route),
        "n_fix": int(n_fix),
        "min_mean": MIN_MEAN,
        "pass_mean": mean >= MIN_MEAN,
        "pass_false_hit": int(n_false_hit) == 0,
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean_bar": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartplus(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTPLUS stats
    WHEN applying §8.5 / §12.1 AC2 gate
    THEN PROMOTE if mean≥7 ∧ false-hit=0 ∧ quality;
         HOLD if false-hit=0 but soft-fail; KILL if false-hit.
    """
    if not bool(stats.get("pass_false_hit")):
        return "KILL"
    if bool(stats.get("pass_mean")) and bool(stats.get("pass_quality")):
        return "PROMOTE"
    return "HOLD"
