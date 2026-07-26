"""Wave AD1 H-HARDPARA: adversarial paraphrase + light noise on SEMWRAP+SMARTPLUS."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ad_session_ops import AD0_PACK
from asksmart_ops import is_period_collapse, strip_stop
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "HARDPARA_ID",
    "HARDPARA_N",
    "HARDPARA_PACK",
    "MIN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "paraphrase_collides_parents",
    "has_adversarial_noise",
    "route_hardpara",
    "score_hardpara_trial",
    "hardpara_stats",
    "decide_hardpara",
]

HARDPARA_ID = "H-HARDPARA"
HARDPARA_N = 10
MIN_MEAN = 7.0  # §13.1 AD1

# Adversarial paraphrases of AD0 (normalize ≠ parent; light noise; same gold).
HARDPARA_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AD-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "parent_question": AD0_PACK[0]["question"],
        "paraphrase": (
            "bIP-340 locks Schnorr sigs — over which elliptic curve exactly? "
            "one short line pls"
        ),
        "gold": AD0_PACK[0]["gold"],
    },
    {
        "id": "AD-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0141",
        "parent_question": AD0_PACK[1]["question"],
        "paraphrase": (
            "SegWit (BIP141): scripts+signatures move into which structure? "
            "keep it practical"
        ),
        "gold": AD0_PACK[1]["gold"],
    },
    {
        "id": "AD-HITL-03",
        "app_id": "known-ask",
        "source_id": "python-tutorial-datastructures",
        "parent_question": AD0_PACK[2]["question"],
        "paraphrase": (
            "py lists — which method appends ONE item to the end?? "
            "(tutorial data-structures)"
        ),
        "gold": AD0_PACK[2]["gold"],
    },
    {
        "id": "AD-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-io",
        "parent_question": AD0_PACK[3]["question"],
        "paraphrase": (
            "python: open a text file for reading with a `with` context mgr — "
            "tiny snippet pls"
        ),
        "gold": AD0_PACK[3]["gold"],
    },
    {
        "id": "AD-HITL-05",
        "app_id": "howto",
        "source_id": "rust-book-ch04-01",
        "parent_question": AD0_PACK[4]["question"],
        "paraphrase": (
            "Rust book ch4: ownership is a set of rules that govern what "
            "(memory-wise)? one sentence"
        ),
        "gold": AD0_PACK[4]["gold"],
    },
    {
        "id": "AD-HITL-06",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "parent_question": AD0_PACK[5]["question"],
        "paraphrase": (
            "rust sketch only: struct User with field email: String"
        ),
        "gold": AD0_PACK[5]["gold"],
    },
    {
        "id": "AD-HITL-07",
        "app_id": "long-doc",
        "source_id": "bitcoin-developer-notes",
        "parent_question": AD0_PACK[6]["question"],
        "paraphrase": (
            "btc Core C++ style notes: how many spaces for block indent "
            "(namespaces excluded)?"
        ),
        "gold": AD0_PACK[6]["gold"],
    },
    {
        "id": "AD-HITL-08",
        "app_id": "long-doc",
        "source_id": "rfc8949",
        "parent_question": AD0_PACK[7]["question"],
        "paraphrase": (
            "RFC8949 = CBOR — it obsoletes which earlier RFC number?"
        ),
        "gold": AD0_PACK[7]["gold"],
    },
    {
        "id": "AD-HITL-09",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "parent_question": AD0_PACK[8]["question"],
        "paraphrase": (
            "RFC 791 Internet Protocol transmits what blocks between hosts?"
        ),
        "gold": AD0_PACK[8]["gold"],
    },
    {
        "id": "AD-HITL-10",
        "app_id": "long-doc",
        "source_id": "bitcoin-core-readme",
        "parent_question": AD0_PACK[9]["question"],
        "paraphrase": (
            "Bitcoin Core README: joins which P2P net and fully verifies what?"
        ),
        "gold": AD0_PACK[9]["gold"],
    },
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN HARDPARA pack
    WHEN checking hard-paraphrase rule
    THEN True iff every paraphrase normalize-key ≠ parent question.
    """
    rows = pack if pack is not None else HARDPARA_PACK
    if len(rows) != HARDPARA_N:
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
    rows = pack if pack is not None else HARDPARA_PACK
    bad: list[str] = []
    for item in rows:
        p = normalize_question(str(item.get("paraphrase", "")))
        parent = normalize_question(str(item.get("parent_question", "")))
        if p == parent:
            bad.append(str(item.get("id", "")))
    return bad


def has_adversarial_noise(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN HARDPARA pack
    WHEN checking adversarial stress markers
    THEN True iff ≥5 paraphrases carry informal/noise cues
         (?? / pls / btc / py / rust sketch / RFC digits glued).
    """
    cues = ("??", "pls", "btc", "py ", "py-", "rust ", "rfc", "bIP", "segwit")
    rows = pack if pack is not None else HARDPARA_PACK
    n = 0
    for item in rows:
        low = str(item.get("paraphrase", "")).lower()
        if any(c.lower() in low for c in cues):
            n += 1
    return n >= 5


def route_hardpara(completion: str, *, mode: str) -> tuple[str, str]:
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


def score_hardpara_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    route: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN HARDPARA adversarial paraphrase ask
    WHEN scoring HITL
    THEN FALSE_HIT→0; TRUE_HIT→9; MISS/period documented as errors.
    """
    from semwrap_ops import score_semwrap_trial

    text, _r = route_hardpara(completion, mode=mode)
    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=text,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + [
        f"route={route}",
        "HARDPARA adversarial paraphrase — SEMWRAP+SMARTPLUS; not open chat",
    ]
    if route == "PERIOD_BLOCK" and not err:
        return 1.0, True, notes + ["FIX: period collapse under hard para"]
    return score, err, notes


def hardpara_stats(
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
    GIVEN 10 HARDPARA scores
    WHEN summarizing AD1
    THEN mean≥7 · false-hit≈0 gates.
    """
    if len(scores) != HARDPARA_N or len(errors) != HARDPARA_N:
        raise ValueError(
            f"HARDPARA requires exactly {HARDPARA_N} scores/errors"
        )
    mean = float(sum(scores) / float(HARDPARA_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": HARDPARA_N,
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


def decide_hardpara(stats: Mapping[str, Any]) -> str:
    """
    GIVEN HARDPARA stats
    WHEN applying §8.6 / §13.1 AD1 gate
    THEN PROMOTE if mean≥7 ∧ false-hit=0 ∧ quality;
         HOLD if false-hit=0 but soft-fail; KILL if false-hit.
    """
    if not bool(stats.get("pass_false_hit")):
        return "KILL"
    if bool(stats.get("pass_mean")) and bool(stats.get("pass_quality")):
        return "PROMOTE"
    return "HOLD"
