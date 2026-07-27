"""Wave AN3 H-SMARTEDGE: undeca-hop cite + GENEDGE peak gen; kill SEMWRAP FPs."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from an_session_ops import AN0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN
from ctxedge_ops import companions_for
from genedge_ops import score_genedge_gen
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTEDGE_ID",
    "SMARTEDGE_N",
    "SMARTEDGE_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SMARTNEXT_GEN_MEAN",
    "GENEDGE_ABLATED_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_undeca_hop_cues",
    "cite_ok",
    "score_smartedge_lookup",
    "score_smartedge_gen",
    "smartedge_stats",
    "decide_smartedge",
]

SMARTEDGE_ID = "H-SMARTEDGE"
SMARTEDGE_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AN3 — or honest HOLD
MIN_CITE_OK = 8
# Peer Wave AM SMARTNEXT peak-overlay mean (extractive — labeled).
SMARTNEXT_GEN_MEAN = 9.0
# Parent Wave AN GENEDGE ablated true-gen mean under dual-arm Cursor EVAL.
GENEDGE_ABLATED_GEN_MEAN = 4.0

_COMP_KEYS = (
    "secondary_source",
    "tertiary_source",
    "quaternary_source",
    "quinary_source",
    "senary_source",
    "septenary_source",
    "octonary_source",
    "nonary_source",
    "denary_source",
    "undenary_source",
)


def _row(*, pack_i: int, paraphrase: str) -> dict[str, str]:
    p = AN0_PACK[pack_i]
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


# Undeca-hop adversarial paraphrases of AN0 (CTXEDGE companions as distractors).
SMARTEDGE_PACK: tuple[dict[str, str], ...] = (
    _row(
        pack_i=0,
        paraphrase=(
            "skip BIP-32 child number + SegWit P2WSH + Schnorr + TLS + CBOR + "
            "BIP-1 + BIPs index + REST headers + JSON-RPC + Core README — "
            "BIP-39 with 192-bit ENT: how many mnemonic words??"
        ),
    ),
    _row(
        pack_i=1,
        paraphrase=(
            "ignore BIP-39 word count + P2WSH size + Schnorr + TLS + CBOR + "
            "BIP-1 + JSON-RPC + Core README + developer notes + REST — "
            "BIP-32 child number field: how many bytes??"
        ),
    ),
    _row(
        pack_i=2,
        paraphrase=(
            "not BIP-39 words + not BIP-32 child number + not Schnorr + not "
            "TLS + not CBOR + not BIPs index + not BIP-1 + not developer "
            "notes + not REST + not Core README — BIP-141 P2WSH "
            "witnessScript maximum bytes??"
        ),
    ),
    _row(
        pack_i=3,
        paraphrase=(
            "forget __dict__ + range + intro + open() + IHL + Rust compound + "
            "ownership + tuple structs + variables + TLS — remove the first "
            "item equal to x from list a, one method call??"
        ),
    ),
    _row(
        pack_i=4,
        paraphrase=(
            "skip __dict__ + a.remove + intro + io + IHL + Rust ch03 + "
            "structs + ownership + compound types + CBOR — which built-in "
            "produces an arithmetic progression for for-loops??"
        ),
    ),
    _row(
        pack_i=5,
        paraphrase=(
            "ignore a.remove + range + intro + io + IHL + tuple structs + "
            "Rust compound + variables + ownership + TLS — instance "
            "attribute that stores writable attributes as a dictionary??"
        ),
    ),
    _row(
        pack_i=6,
        paraphrase=(
            "not variables ch03 + not ownership + not structs + not CBOR + "
            "not TLS + not Python intro + not range + not a.remove + not "
            "__dict__ + not io — Rust two primitive compound types??"
        ),
    ),
    _row(
        pack_i=7,
        paraphrase=(
            "skip compound types + variables + ownership + CBOR + TLS + "
            "__dict__ + intro + io + a.remove + range — Rust name for "
            "structs that look like tuples but carry a type name??"
        ),
    ),
    _row(
        pack_i=8,
        paraphrase=(
            "ignore JSON-RPC wallet + Core README + developer notes + "
            "BIP-32 + TLS + CBOR + BIP-1 + SegWit + BIPs index + BIP-39 — "
            "REST GET path pattern for blockheaders with encoding "
            "suffixes??"
        ),
    ),
    _row(
        pack_i=9,
        paraphrase=(
            "not TLS handshake + not CBOR + not BIP-39 + not Python intro + "
            "not JSON-RPC + not BIP-1 + not REST headers + not BIPs index + "
            "not BIP-32 + not io — RFC 791 Total Length field how many "
            "bits??"
        ),
    ),
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTEDGE_PACK
    if len(rows) != SMARTEDGE_N:
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
    rows = pack if pack is not None else SMARTEDGE_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_undeca_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTEDGE pack
    WHEN checking undeca-hop distractor wiring
    THEN True iff every row maps CTXEDGE companions and ≥8 carry cues.
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
        "a.remove",
        "range",
        "__dict__",
        "compound",
        "tuple struct",
        "ownership",
        "wallet",
        "json-rpc",
        "rest",
        "blockheader",
        "skip ",
        "ignore ",
        "forget ",
        "not ",
    )
    rows = pack if pack is not None else SMARTEDGE_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        comps = companions_for(sid)
        wired = tuple(str(item.get(k, "")) for k in _COMP_KEYS)
        if wired != comps:
            return False
        if len({sid, *comps}) != 11:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def score_smartedge_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    expected_source_id: str,
    hit_source_id: str | None,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """LOOKUP paraphrase ask — cite_ok; LOOKUP ≠ gen IQ; kill FPs."""
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
        "SMARTEDGE LOOKUP undeca paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if lookup_kind == "FALSE_HIT":
        err = True
        notes.append("SEMWRAP false-neighbor FP — kill path")
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartedge_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (GENEDGE extractive peak, labeled)
    WHEN Cursor EVAL completion vs gold
    THEN genedge peak rubric on AN-aware spans; peak ≠ open-chat IQ label.
    """
    score, err, notes = score_genedge_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=False,
    )
    notes = list(notes) + [
        "SMARTEDGE gen GENEDGE peak (extractive) — Cursor scores completion",
        f"beat GENEDGE ablated gen={GENEDGE_ABLATED_GEN_MEAN} / peer "
        f"SMARTNEXT={SMARTNEXT_GEN_MEAN}",
    ]
    return float(score), bool(err), notes


def smartedge_stats(
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
    if len(lookup_scores) != SMARTEDGE_N or len(gen_scores) != SMARTEDGE_N:
        raise ValueError(f"SMARTEDGE requires {SMARTEDGE_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTEDGE_N))
    g_mean = float(sum(gen_scores) / float(SMARTEDGE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTEDGE_N,
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
        "smartnext_gen_mean": SMARTNEXT_GEN_MEAN,
        "genedge_ablated_gen_mean": GENEDGE_ABLATED_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_genedge_ablated": g_mean > GENEDGE_ABLATED_GEN_MEAN,
        "peers_smartnext_gen": g_mean >= SMARTNEXT_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "undeca_hop": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartedge(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTEDGE dual-arm stats
    WHEN applying pesquisa §3 AN3 gate
    THEN KILL if false-hit; PROMOTE if lookup+cite+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")) or not bool(stats.get("undeca_hop")):
        return "KILL"
    lookup_ok = bool(stats.get("pass_lookup")) and bool(stats.get("pass_cite"))
    if lookup_ok and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
