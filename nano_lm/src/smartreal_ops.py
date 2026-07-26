"""Wave AG3 H-SMARTREAL: smarter retrieve + real gen EVAL (dual-arm)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ag_session_ops import AG0_PACK
from antifp_ops import classify_arm, extract_telemetry
from ctxreal_ops import (
    quaternary_for,
    secondary_for,
    tertiary_for,
)
from smartmax_ops import cite_ok, route_smartmax
from servealign_ops import SERVEALIGN_ID
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTREAL_ID",
    "SMARTREAL_N",
    "SMARTREAL_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_quad_hop_cues",
    "route_smartreal",
    "cite_ok",
    "score_smartreal_lookup",
    "score_smartreal_gen",
    "smartreal_stats",
    "decide_smartreal",
]

SMARTREAL_ID = "H-SMARTREAL"
SMARTREAL_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §5 AG3 — or honest HOLD
MIN_CITE_OK = 8
# Parent open-decode baseline (Wave AA H-SERVEALIGN).
SERVEALIGN_MEAN = 3.4

# Quad-hop adversarial paraphrases of AG0 (sec+ter+quat distractors).
SMARTREAL_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AG-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "secondary_source": "bip-0039",
        "tertiary_source": "bip-0141",
        "quaternary_source": "rfc8949",
        "parent_question": AG0_PACK[0]["question"],
        "paraphrase": (
            "skip BIP-39 mnemonic checksum and SegWit/CBOR side-quests — "
            "BIP-32 hardened child index threshold hex??"
        ),
        "gold": AG0_PACK[0]["gold"],
    },
    {
        "id": "AG-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "secondary_source": "bip-0032",
        "tertiary_source": "bip-0340",
        "quaternary_source": "rfc8949",
        "parent_question": AG0_PACK[1]["question"],
        "paraphrase": (
            "ignore HD hardened indices + Schnorr sizes — BIP-39 ENT=128: "
            "checksum bits and word count??"
        ),
        "gold": AG0_PACK[1]["gold"],
    },
    {
        "id": "AG-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "secondary_source": "bip-0141",
        "tertiary_source": "bip-0032",
        "quaternary_source": "rfc8949",
        "parent_question": AG0_PACK[2]["question"],
        "paraphrase": (
            "not SegWit OP_RETURN and not BIP-32 paths — BIP-340 Schnorr "
            "sig size + curve, one sentence pls"
        ),
        "gold": AG0_PACK[2]["gold"],
    },
    {
        "id": "AG-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "secondary_source": "python-tutorial-classes",
        "tertiary_source": "python-tutorial-io",
        "quaternary_source": "python-tutorial-intro",
        "parent_question": AG0_PACK[3]["question"],
        "paraphrase": (
            "forget Point class / readlines / add() — extend list nums from "
            "iterable more, one method call??"
        ),
        "gold": AG0_PACK[3]["gold"],
    },
    {
        "id": "AG-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-io",
        "secondary_source": "python-tutorial-datastructures",
        "tertiary_source": "python-tutorial-classes",
        "quaternary_source": "python-tutorial-control",
        "parent_question": AG0_PACK[4]["question"],
        "paraphrase": (
            "skip list.extend and class fluff — open text file f: read all "
            "remaining lines into a list, one call??"
        ),
        "gold": AG0_PACK[4]["gold"],
    },
    {
        "id": "AG-HITL-06",
        "app_id": "howto",
        "source_id": "rust-book-ch03",
        "secondary_source": "rust-book-ch03-02",
        "tertiary_source": "rust-book-ch04-01",
        "quaternary_source": "rfc8949",
        "parent_question": AG0_PACK[5]["question"],
        "paraphrase": (
            "ignore scalar/compound types + ownership essay — without mut, "
            "assign twice to x: which compile error??"
        ),
        "gold": AG0_PACK[5]["gold"],
    },
    {
        "id": "AG-HITL-07",
        "app_id": "howto",
        "source_id": "bitcoin-json-rpc",
        "secondary_source": "bitcoin-rest",
        "tertiary_source": "bitcoin-core-readme",
        "quaternary_source": "rfc8949",
        "parent_question": AG0_PACK[6]["question"],
        "paraphrase": (
            "not REST blockhashbyheight and not Core P2P README — JSON-RPC "
            "curl examples Content-Type??"
        ),
        "gold": AG0_PACK[6]["gold"],
    },
    {
        "id": "AG-HITL-08",
        "app_id": "howto",
        "source_id": "bitcoin-rest",
        "secondary_source": "bitcoin-json-rpc",
        "tertiary_source": "bitcoin-developer-notes",
        "quaternary_source": "rfc8949",
        "parent_question": AG0_PACK[7]["question"],
        "paraphrase": (
            "skip JSON-RPC Content-Type + developer-notes — REST path for "
            "block hash by height with encodings??"
        ),
        "gold": AG0_PACK[7]["gold"],
    },
    {
        "id": "AG-HITL-09",
        "app_id": "long-doc",
        "source_id": "bip-0141",
        "secondary_source": "bip-0340",
        "tertiary_source": "bitcoin-core-readme",
        "quaternary_source": "rfc8949",
        "parent_question": AG0_PACK[8]["question"],
        "paraphrase": (
            "ignore Schnorr BIP-340 and CBOR — BIP-141 coinbase witness "
            "commitment starts with which opcode??"
        ),
        "gold": AG0_PACK[8]["gold"],
    },
    {
        "id": "AG-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8949",
        "secondary_source": "rfc8446",
        "tertiary_source": "rfc791",
        "quaternary_source": "python-tutorial-datastructures",
        "parent_question": AG0_PACK[9]["question"],
        "paraphrase": (
            "not TLS 1.3 handshake and not IP TTL — RFC 8949: expand CBOR "
            "acronym in plain words??"
        ),
        "gold": AG0_PACK[9]["gold"],
    },
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTREAL_PACK
    if len(rows) != SMARTREAL_N:
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
    rows = pack if pack is not None else SMARTREAL_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_quad_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTREAL pack
    WHEN checking quad-hop distractor wiring
    THEN True iff every row maps sec/ter/quat via CTXREAL and ≥8 carry cues.
    """
    cues = (
        "bip-39",
        "mnemonic",
        "segwit",
        "cbor",
        "schnorr",
        "hardened",
        "point",
        "readlines",
        "add(",
        "ownership",
        "scalar",
        "rest",
        "json-rpc",
        "content-type",
        "op_return",
        "tls",
        "ttl",
        "skip ",
        "ignore ",
        "forget ",
        "not ",
    )
    rows = pack if pack is not None else SMARTREAL_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        sec = str(item.get("secondary_source", ""))
        ter = str(item.get("tertiary_source", ""))
        quat = str(item.get("quaternary_source", ""))
        if sec != secondary_for(sid):
            return False
        if ter != tertiary_for(sid):
            return False
        if quat != quaternary_for(sid):
            return False
        if len({sid, sec, ter, quat}) != 4:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def route_smartreal(completion: str, *, mode: str) -> tuple[str, str]:
    return route_smartmax(completion, mode=mode)


def score_smartreal_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    expected_source_id: str,
    hit_source_id: str | None,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN LOOKUP paraphrase ask
    WHEN Cursor EVAL
    THEN (score, error, notes, cite_ok); LOOKUP ≠ gen IQ.
    """
    from semwrap_ops import score_semwrap_trial

    text, route = route_smartreal(completion, mode=mode)
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
        "SMARTREAL LOOKUP paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartreal_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (QPFB2+BEAMKV)
    WHEN Cursor EVAL completion vs gold
    THEN score text (not TRUE_HIT→9); require gen telemetry.
    """
    from servealign_ops import score_open_completion

    score, err, notes = score_open_completion(completion, expected_gold)
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        "SMARTREAL gen QPFB2+BEAMKV — Cursor scores completion",
        f"baseline {SERVEALIGN_ID} mean={SERVEALIGN_MEAN}",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen telemetry fail"]
    return float(score), bool(err), notes


def smartreal_stats(
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
    if len(lookup_scores) != SMARTREAL_N or len(gen_scores) != SMARTREAL_N:
        raise ValueError(f"SMARTREAL requires {SMARTREAL_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTREAL_N))
    g_mean = float(sum(gen_scores) / float(SMARTREAL_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTREAL_N,
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
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartreal(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTREAL dual-arm stats
    WHEN applying pesquisa §5 AG3 gate
    THEN KILL if false-hit; PROMOTE if lookup+cite+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    lookup_ok = bool(stats.get("pass_lookup")) and bool(stats.get("pass_cite"))
    if lookup_ok and bool(stats.get("pass_gen")):
        return "PROMOTE"
    if lookup_ok:
        return "HOLD"
    return "HOLD"
