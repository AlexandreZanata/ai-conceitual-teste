"""Wave AH3 H-SMARTLIFT: smarter cite + gen beyond SMARTREAL (dual-arm)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ah_session_ops import AH0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN, strip_stop
from ctxlift_ops import (
    quaternary_for,
    quinary_for,
    secondary_for,
    tertiary_for,
)
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTLIFT_ID",
    "SMARTLIFT_N",
    "SMARTLIFT_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SMARTREAL_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_penta_hop_cues",
    "cite_ok",
    "score_smartlift_lookup",
    "score_smartlift_gen",
    "smartlift_stats",
    "decide_smartlift",
]

SMARTLIFT_ID = "H-SMARTLIFT"
SMARTLIFT_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §5 AH3 — or honest HOLD
MIN_CITE_OK = 8
# Parent Wave AG SMARTREAL open-gen mean under score_open_completion.
SMARTREAL_GEN_MEAN = 4.0

# Penta-hop adversarial paraphrases of AH0 (sec+ter+quat+quin distractors).
SMARTLIFT_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AH-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "secondary_source": "bip-0032",
        "tertiary_source": "bip-0340",
        "quaternary_source": "bip-0141",
        "quinary_source": "rfc8949",
        "parent_question": AH0_PACK[0]["question"],
        "paraphrase": (
            "skip BIP-32 hardened indices + Schnorr + SegWit/CBOR — "
            "BIP-39 empty-passphrase mnemonic→seed UTF-8 salt string??"
        ),
        "gold": AH0_PACK[0]["gold"],
    },
    {
        "id": "AH-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "secondary_source": "bip-0141",
        "tertiary_source": "bip-0032",
        "quaternary_source": "bip-0039",
        "quinary_source": "rfc8446",
        "parent_question": AH0_PACK[1]["question"],
        "paraphrase": (
            "ignore SegWit OP_RETURN + HD paths + BIP-39 salt + TLS — "
            "BIP-340 key prefixing stops which attack on additive tweaks??"
        ),
        "gold": AH0_PACK[1]["gold"],
    },
    {
        "id": "AH-HITL-03",
        "app_id": "known-ask",
        "source_id": "rust-book-ch03-02",
        "secondary_source": "rust-book-ch03",
        "tertiary_source": "rust-book-ch04-01",
        "quaternary_source": "rust-book-ch05-01",
        "quinary_source": "rfc8949",
        "parent_question": AH0_PACK[2]["question"],
        "paraphrase": (
            "not mut/shadowing + not ownership heap + not struct update + "
            "not CBOR — list Rust's four primary scalar types??"
        ),
        "gold": AH0_PACK[2]["gold"],
    },
    {
        "id": "AH-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "secondary_source": "python-tutorial-classes",
        "tertiary_source": "python-tutorial-io",
        "quaternary_source": "python-tutorial-intro",
        "quinary_source": "python-tutorial-control",
        "parent_question": AH0_PACK[3]["question"],
        "paraphrase": (
            "forget Point/self + f-strings + add() + pass — remove and "
            "return last item of list a, one method call??"
        ),
        "gold": AH0_PACK[3]["gold"],
    },
    {
        "id": "AH-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "secondary_source": "python-tutorial-intro",
        "tertiary_source": "python-tutorial-classes",
        "quaternary_source": "python-tutorial-datastructures",
        "quinary_source": "python-tutorial-io",
        "parent_question": AH0_PACK[4]["question"],
        "paraphrase": (
            "skip add() + self + list.pop + readlines — empty Python "
            "function body keyword??"
        ),
        "gold": AH0_PACK[4]["gold"],
    },
    {
        "id": "AH-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "secondary_source": "python-tutorial-datastructures",
        "tertiary_source": "python-tutorial-control",
        "quaternary_source": "python-tutorial-intro",
        "quinary_source": "python-tutorial-io",
        "parent_question": AH0_PACK[5]["question"],
        "paraphrase": (
            "ignore list.pop + pass + add() + open() — inside instance "
            "method, what does self refer to??"
        ),
        "gold": AH0_PACK[5]["gold"],
    },
    {
        "id": "AH-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch04-01",
        "secondary_source": "rust-book-ch03-02",
        "tertiary_source": "rust-book-ch05-01",
        "quaternary_source": "rust-book-ch03",
        "quinary_source": "rfc8949",
        "parent_question": AH0_PACK[6]["question"],
        "paraphrase": (
            "skip scalar types + struct update + mut assign + CBOR — "
            "ownership: where store unknown-size data at compile time??"
        ),
        "gold": AH0_PACK[6]["gold"],
    },
    {
        "id": "AH-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "secondary_source": "rust-book-ch04-01",
        "tertiary_source": "rust-book-ch03-02",
        "quaternary_source": "rust-book-ch03",
        "quinary_source": "rfc8446",
        "parent_question": AH0_PACK[7]["question"],
        "paraphrase": (
            "not ownership heap + not scalar types + not mut + not TLS — "
            "name Rust syntax filling remaining struct fields (..other)??"
        ),
        "gold": AH0_PACK[7]["gold"],
    },
    {
        "id": "AH-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "secondary_source": "bitcoin-json-rpc",
        "tertiary_source": "bitcoin-core-readme",
        "quaternary_source": "bitcoin-developer-notes",
        "quinary_source": "bitcoin-doc-bips",
        "parent_question": AH0_PACK[8]["question"],
        "paraphrase": (
            "ignore JSON-RPC Content-Type + P2P README + indent notes + "
            "BIP-9 docs — REST mainnet TCP port shared with JSON-RPC??"
        ),
        "gold": AH0_PACK[8]["gold"],
    },
    {
        "id": "AH-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8949",
        "secondary_source": "rfc8446",
        "tertiary_source": "rfc791",
        "quaternary_source": "bip-0001",
        "quinary_source": "bitcoin-core-readme",
        "parent_question": AH0_PACK[9]["question"],
        "paraphrase": (
            "not TLS handshake + not IP TTL + not BIP purpose + not Core "
            "P2P — RFC 8949 CBOR obsoletes which RFC number??"
        ),
        "gold": AH0_PACK[9]["gold"],
    },
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTLIFT_PACK
    if len(rows) != SMARTLIFT_N:
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
    rows = pack if pack is not None else SMARTLIFT_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_penta_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTLIFT pack
    WHEN checking penta-hop distractor wiring
    THEN True iff every row maps CTXLIFT companions and ≥8 carry cues.
    """
    cues = (
        "bip-32",
        "hardened",
        "schnorr",
        "segwit",
        "cbor",
        "tls",
        "ttl",
        "ownership",
        "scalar",
        "struct",
        "heap",
        "mut",
        "pop",
        "pass",
        "self",
        "add(",
        "readlines",
        "json-rpc",
        "content-type",
        "rest",
        "bip-9",
        "skip ",
        "ignore ",
        "forget ",
        "not ",
    )
    rows = pack if pack is not None else SMARTLIFT_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        sec = str(item.get("secondary_source", ""))
        ter = str(item.get("tertiary_source", ""))
        quat = str(item.get("quaternary_source", ""))
        quin = str(item.get("quinary_source", ""))
        if sec != secondary_for(sid):
            return False
        if ter != tertiary_for(sid):
            return False
        if quat != quaternary_for(sid):
            return False
        if quin != quinary_for(sid):
            return False
        if len({sid, sec, ter, quat, quin}) != 5:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def score_smartlift_lookup(
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
        "SMARTLIFT LOOKUP penta paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartlift_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (QPFB2+BEAMKV+anti-period)
    WHEN Cursor EVAL completion vs gold
    THEN open-completion rubric (not ASKSMART floor-5); require gen telemetry.
    """
    from servealign_ops import score_open_completion

    text = strip_stop(completion)
    score, err, notes = score_open_completion(text, expected_gold)
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        "SMARTLIFT gen ASKSMART polish — Cursor scores completion",
        f"beat SMARTREAL gen={SMARTREAL_GEN_MEAN} / SERVEALIGN={SERVEALIGN_MEAN}",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen telemetry fail"]
    return float(score), bool(err), notes


def smartlift_stats(
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
    if len(lookup_scores) != SMARTLIFT_N or len(gen_scores) != SMARTLIFT_N:
        raise ValueError(f"SMARTLIFT requires {SMARTLIFT_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTLIFT_N))
    g_mean = float(sum(gen_scores) / float(SMARTLIFT_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTLIFT_N,
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
        "smartreal_gen_mean": SMARTREAL_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_smartreal_gen": g_mean > SMARTREAL_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartlift(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTLIFT dual-arm stats
    WHEN applying pesquisa §5 AH3 gate
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
