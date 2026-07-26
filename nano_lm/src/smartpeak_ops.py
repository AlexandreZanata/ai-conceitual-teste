"""Wave AJ3 H-SMARTPEAK: hepta-hop cite + GENPEAK gen beyond SMARTPUSH."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aj_session_ops import AJ0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN
from ctxpeak_ops import companions_for
from genpeak_ops import score_genpeak_gen
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTPEAK_ID",
    "SMARTPEAK_N",
    "SMARTPEAK_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SMARTPUSH_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_hepta_hop_cues",
    "cite_ok",
    "score_smartpeak_lookup",
    "score_smartpeak_gen",
    "smartpeak_stats",
    "decide_smartpeak",
]

SMARTPEAK_ID = "H-SMARTPEAK"
SMARTPEAK_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AJ3 — or honest HOLD
MIN_CITE_OK = 8
# Parent Wave AI SMARTPUSH open-gen mean under dual-arm Cursor EVAL.
SMARTPUSH_GEN_MEAN = 4.0

_COMP_KEYS = (
    "secondary_source",
    "tertiary_source",
    "quaternary_source",
    "quinary_source",
    "senary_source",
    "septenary_source",
)


def _row(*, pack_i: int, paraphrase: str) -> dict[str, str]:
    p = AJ0_PACK[pack_i]
    sid = str(p["source_id"])
    comps = companions_for(sid)
    row: dict[str, str] = {
        "id": str(p["id"]),
        "app_id": str(p["app_id"]),
        "source_id": sid,
        "parent_question": str(p["question"]),
        "paraphrase": paraphrase,
        "gold": str(p["gold"]),
    }
    for key, comp in zip(_COMP_KEYS, comps, strict=True):
        row[key] = comp
    return row


# Hepta-hop adversarial paraphrases of AJ0 (CTXPEAK companions as distractors).
SMARTPEAK_PACK: tuple[dict[str, str], ...] = (
    _row(
        pack_i=0,
        paraphrase=(
            "skip BIP-32 depth + SegWit P2WSH + Schnorr + TLS + CBOR + BIP-1 — "
            "BIP-39 ENT must be a multiple of how many bits??"
        ),
    ),
    _row(
        pack_i=1,
        paraphrase=(
            "ignore BIP-39 salt + P2WSH + Schnorr + TLS + CBOR + BIP-1 — "
            "BIP-32 extended-key depth field: how many bytes??"
        ),
    ),
    _row(
        pack_i=2,
        paraphrase=(
            "not BIP-39 + not BIP-32 depth + not Schnorr + not TLS + not CBOR "
            "+ not BIPs index — BIP-141 v0/32-byte witness program acronym??"
        ),
    ),
    _row(
        pack_i=3,
        paraphrase=(
            "forget isinstance + continue + intro + open() + IHL + Rust i32 — "
            "preferred queue type, give module.class??"
        ),
    ),
    _row(
        pack_i=4,
        paraphrase=(
            "skip isinstance + deque + intro + io + IHL + Rust ch03 — "
            "statement that skips the rest of the current loop iteration??"
        ),
    ),
    _row(
        pack_i=5,
        paraphrase=(
            "ignore deque + continue + intro + io + IHL + field init — "
            "built-in that checks an instance's type??"
        ),
    ),
    _row(
        pack_i=6,
        paraphrase=(
            "not ownership ch03 + not mut borrow + not field init + not CBOR "
            "+ not TLS + not Python intro — Rust default integer type??"
        ),
    ),
    _row(
        pack_i=7,
        paraphrase=(
            "skip i32 default + ownership + borrow + CBOR + TLS + isinstance — "
            "Rust syntax for username instead of username: username??"
        ),
    ),
    _row(
        pack_i=8,
        paraphrase=(
            "ignore REST chaininfo + Core README + developer notes + BIP-32 + "
            "TLS + CBOR — JSON-RPC path when multiple wallets are loaded??"
        ),
    ),
    _row(
        pack_i=9,
        paraphrase=(
            "not TLS handshake + not CBOR + not BIP-39 + not Python intro + "
            "not JSON-RPC wallet + not BIP-1 — RFC 791 IHL expands to??"
        ),
    ),
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTPEAK_PACK
    if len(rows) != SMARTPEAK_N:
        return False
    for item in rows:
        p = normalize_question(str(item.get("paraphrase", "")))
        parent = normalize_question(str(item.get("parent_question", "")))
        if not p or not parent or p == parent:
            return False
    return True


def has_adversarial_noise(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    cues = ("??", "pls", "skip ", "ignore ", "forget ", "not ")
    rows = pack if pack is not None else SMARTPEAK_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_hepta_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTPEAK pack
    WHEN checking hepta-hop distractor wiring
    THEN True iff every row maps CTXPEAK companions and ≥8 carry cues.
    """
    cues = (
        "bip-39",
        "bip-32",
        "schnorr",
        "segwit",
        "p2wsh",
        "cbor",
        "tls",
        "ihl",
        "deque",
        "isinstance",
        "continue",
        "i32",
        "field init",
        "ownership",
        "borrow",
        "wallet",
        "json-rpc",
        "rest",
        "skip ",
        "ignore ",
        "forget ",
        "not ",
    )
    rows = pack if pack is not None else SMARTPEAK_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        comps = companions_for(sid)
        wired = tuple(str(item.get(k, "")) for k in _COMP_KEYS)
        if wired != comps:
            return False
        if len({sid, *comps}) != 7:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def score_smartpeak_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    expected_source_id: str,
    hit_source_id: str | None,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """LOOKUP paraphrase ask — cite_ok; LOOKUP ≠ gen IQ."""
    from semwrap_ops import score_semwrap_trial

    text, route = route_smartmax(completion, mode=mode)
    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=text,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    cited = cite_ok(
        expected_source_id=expected_source_id,
        hit_source_id=hit_source_id,
        lookup_kind=lookup_kind,
    )
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']} route={route}",
        "SMARTPEAK LOOKUP hepta paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartpeak_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (GENPEAK grounded+extractive peak)
    WHEN Cursor EVAL completion vs gold
    THEN genpeak containment rubric; require gen telemetry.
    """
    score, err, notes = score_genpeak_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
    )
    notes = list(notes) + [
        "SMARTPEAK gen GENPEAK peak — Cursor scores completion",
        f"beat SMARTPUSH gen={SMARTPUSH_GEN_MEAN} / SERVEALIGN={SERVEALIGN_MEAN}",
    ]
    return float(score), bool(err), notes


def smartpeak_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    cite_flags: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    n_fix: int,
    n_peak: int,
) -> dict[str, Any]:
    if len(lookup_scores) != SMARTPEAK_N or len(gen_scores) != SMARTPEAK_N:
        raise ValueError(f"SMARTPEAK requires {SMARTPEAK_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTPEAK_N))
    g_mean = float(sum(gen_scores) / float(SMARTPEAK_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTPEAK_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_cite_ok": n_cite,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_fix": int(n_fix),
        "n_peak": int(n_peak),
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "min_cite_ok": MIN_CITE_OK,
        "smartpush_gen_mean": SMARTPUSH_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_smartpush_gen": g_mean > SMARTPUSH_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartpeak(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTPEAK dual-arm stats
    WHEN applying pesquisa §3 AJ3 gate
    THEN KILL if false-hit; PROMOTE if lookup+cite+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    lookup_ok = bool(stats.get("pass_lookup")) and bool(stats.get("pass_cite"))
    if lookup_ok and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
