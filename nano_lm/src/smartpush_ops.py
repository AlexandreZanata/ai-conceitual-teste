"""Wave AI3 H-SMARTPUSH: hexa-hop cite + gen beyond SMARTLIFT (dual-arm)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ai_session_ops import AI0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN
from ctxpush_ops import (
    quaternary_for,
    quinary_for,
    secondary_for,
    senary_for,
    tertiary_for,
)
from genplus_ops import score_genplus_gen
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTPUSH_ID",
    "SMARTPUSH_N",
    "SMARTPUSH_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SMARTLIFT_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_hexa_hop_cues",
    "cite_ok",
    "score_smartpush_lookup",
    "score_smartpush_gen",
    "smartpush_stats",
    "decide_smartpush",
]

SMARTPUSH_ID = "H-SMARTPUSH"
SMARTPUSH_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §5 AI3 — or honest HOLD
MIN_CITE_OK = 8
# Parent Wave AH SMARTLIFT open-gen mean under dual-arm Cursor EVAL.
SMARTLIFT_GEN_MEAN = 4.0


def _row(
    *,
    pack_i: int,
    paraphrase: str,
) -> dict[str, str]:
    p = AI0_PACK[pack_i]
    sid = str(p["source_id"])
    return {
        "id": str(p["id"]),
        "app_id": str(p["app_id"]),
        "source_id": sid,
        "secondary_source": secondary_for(sid),
        "tertiary_source": tertiary_for(sid),
        "quaternary_source": quaternary_for(sid),
        "quinary_source": quinary_for(sid),
        "senary_source": senary_for(sid),
        "parent_question": str(p["question"]),
        "paraphrase": paraphrase,
        "gold": str(p["gold"]),
    }


# Hexa-hop adversarial paraphrases of AI0 (sec+ter+quat+quin+sen distractors).
SMARTPUSH_PACK: tuple[dict[str, str], ...] = (
    _row(
        pack_i=0,
        paraphrase=(
            "skip BIP-39 salt + Schnorr batch + SegWit P2WPKH + TLS + CBOR — "
            "BIP-32 serialization before Base58: how many bytes??"
        ),
    ),
    _row(
        pack_i=1,
        paraphrase=(
            "ignore SegWit P2WPKH + BIP-32 bytes + BIP-39 + TLS + CBOR — "
            "BIP-340 (R,s) mainly enables which verification speedup??"
        ),
    ),
    _row(
        pack_i=2,
        paraphrase=(
            "not BIP-32 paths + not Schnorr batch + not BIP-39 + not TLS + "
            "not CBOR — BIP-141 v0/20-byte program type acronym??"
        ),
    ),
    _row(
        pack_i=3,
        paraphrase=(
            "forget issubclass + open() + add() + elif + IP TTL — insert x "
            "at front of list a, one method call??"
        ),
    ),
    _row(
        pack_i=4,
        paraphrase=(
            "skip add() + self/issubclass + list.insert + readlines + TTL — "
            "elif expands to which two-word phrase??"
        ),
    ),
    _row(
        pack_i=5,
        paraphrase=(
            "ignore list.insert + elif/else if + add() + open() + TTL — "
            "built-in that checks subclass relationship??"
        ),
    ),
    _row(
        pack_i=6,
        paraphrase=(
            "skip mut assign + ownership LIFO + struct update + CBOR + TLS — "
            "Rust default floating-point type??"
        ),
    ),
    _row(
        pack_i=7,
        paraphrase=(
            "not f64 default + not struct update + not mut + not CBOR + "
            "not TLS — expand LIFO for stack push/pop??"
        ),
    ),
    _row(
        pack_i=8,
        paraphrase=(
            "ignore JSON-RPC Content-Type + Core README + indent notes + "
            "TLS + CBOR — REST GET path for chaininfo JSON only??"
        ),
    ),
    _row(
        pack_i=9,
        paraphrase=(
            "not BIP-32 bytes + not BIP-39 salt + not SegWit + not TLS + "
            "not CBOR — BIP-1 three Type header values, comma-separated??"
        ),
    ),
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTPUSH_PACK
    if len(rows) != SMARTPUSH_N:
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
    rows = pack if pack is not None else SMARTPUSH_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_hexa_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTPUSH pack
    WHEN checking hexa-hop distractor wiring
    THEN True iff every row maps CTXPUSH companions and ≥8 carry cues.
    """
    cues = (
        "bip-39",
        "bip-32",
        "schnorr",
        "segwit",
        "p2wpkh",
        "cbor",
        "tls",
        "ttl",
        "ownership",
        "lifo",
        "f64",
        "mut",
        "insert",
        "elif",
        "issubclass",
        "self",
        "add(",
        "readlines",
        "json-rpc",
        "content-type",
        "rest",
        "skip ",
        "ignore ",
        "forget ",
        "not ",
    )
    rows = pack if pack is not None else SMARTPUSH_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        sec = str(item.get("secondary_source", ""))
        ter = str(item.get("tertiary_source", ""))
        quat = str(item.get("quaternary_source", ""))
        quin = str(item.get("quinary_source", ""))
        sen = str(item.get("senary_source", ""))
        if sec != secondary_for(sid):
            return False
        if ter != tertiary_for(sid):
            return False
        if quat != quaternary_for(sid):
            return False
        if quin != quinary_for(sid):
            return False
        if sen != senary_for(sid):
            return False
        if len({sid, sec, ter, quat, quin, sen}) != 6:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def score_smartpush_lookup(
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
        "SMARTPUSH LOOKUP hexa paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartpush_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (grounded QPFB2 beyond SMARTLIFT)
    WHEN Cursor EVAL completion vs gold
    THEN genplus containment rubric; require gen telemetry.
    """
    score, err, notes = score_genplus_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
    )
    notes = list(notes) + [
        "SMARTPUSH gen grounded polish — Cursor scores completion",
        f"beat SMARTLIFT gen={SMARTLIFT_GEN_MEAN} / SERVEALIGN={SERVEALIGN_MEAN}",
    ]
    return float(score), bool(err), notes


def smartpush_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    cite_flags: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    n_fix: int,
) -> dict[str, Any]:
    if len(lookup_scores) != SMARTPUSH_N or len(gen_scores) != SMARTPUSH_N:
        raise ValueError(f"SMARTPUSH requires {SMARTPUSH_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTPUSH_N))
    g_mean = float(sum(gen_scores) / float(SMARTPUSH_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTPUSH_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_cite_ok": n_cite,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_fix": int(n_fix),
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "min_cite_ok": MIN_CITE_OK,
        "smartlift_gen_mean": SMARTLIFT_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_smartlift_gen": g_mean > SMARTLIFT_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartpush(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTPUSH dual-arm stats
    WHEN applying pesquisa §5 AI3 gate
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
