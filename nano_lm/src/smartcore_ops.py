"""Wave AO3 H-SMARTCORE: dodeca-hop cite + GENCORE peak gen; kill SEMWRAP FPs."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ao_session_ops import AO0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN
from ctxcore_ops import companions_for
from gencore_ops import score_gencore_gen
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTCORE_ID",
    "SMARTCORE_N",
    "SMARTCORE_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SMARTEDGE_GEN_MEAN",
    "GENCORE_ABLATED_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_dodeca_hop_cues",
    "cite_ok",
    "score_smartcore_lookup",
    "score_smartcore_gen",
    "smartcore_stats",
    "decide_smartcore",
]

SMARTCORE_ID = "H-SMARTCORE"
SMARTCORE_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AO3 — or honest HOLD
MIN_CITE_OK = 8
# Peer Wave AN SMARTEDGE peak-overlay mean (extractive — labeled).
SMARTEDGE_GEN_MEAN = 9.0
# Parent Wave AO GENCORE ablated true-gen mean under dual-arm Cursor EVAL.
GENCORE_ABLATED_GEN_MEAN = 4.0

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
    "duodenary_source",
)


def _row(*, pack_i: int, paraphrase: str) -> dict[str, str]:
    p = AO0_PACK[pack_i]
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


# Dodeca-hop adversarial paraphrases of AO0 (CTXCORE companions as distractors).
SMARTCORE_PACK: tuple[dict[str, str], ...] = (
    _row(
        pack_i=0,
        paraphrase=(
            "skip BIP-32 version bytes + SegWit witness L + Schnorr + TLS + "
            "CBOR + BIP-1 + BIPs index + REST block + JSON-RPC + Core README "
            "+ Rust variables — BIP-39 with 224-bit ENT: how many mnemonic "
            "words??"
        ),
    ),
    _row(
        pack_i=1,
        paraphrase=(
            "ignore BIP-39 word count + P2WSH L + Schnorr + TLS + CBOR + "
            "BIP-1 + JSON-RPC + Core README + developer notes + REST + "
            "Rust ch03 — BIP-32 extended-key serialization: version field "
            "byte count??"
        ),
    ),
    _row(
        pack_i=2,
        paraphrase=(
            "not BIP-39 words + not BIP-32 version + not Schnorr + not TLS + "
            "not CBOR + not BIPs index + not BIP-1 + not developer notes + "
            "not REST + not Core README + not Rust variables — BIP-141 "
            "maximum witness program length L in bytes??"
        ),
    ),
    _row(
        pack_i=3,
        paraphrase=(
            "forget super + while + intro + open() + IHL + Rust compound + "
            "ownership + structs + variables + TLS + developer notes — "
            "count how many times value x appears in list a, one method "
            "call??"
        ),
    ),
    _row(
        pack_i=4,
        paraphrase=(
            "skip super + a.count + intro + io + IHL + Rust ch03 + structs "
            "+ ownership + compound types + CBOR + developer notes — which "
            "keyword starts a loop that repeats while a condition is true??"
        ),
    ),
    _row(
        pack_i=5,
        paraphrase=(
            "ignore a.count + while + intro + io + IHL + structs + Rust "
            "compound + variables + ownership + TLS + developer notes — "
            "built-in proxy for cooperative multiple inheritance??"
        ),
    ),
    _row(
        pack_i=6,
        paraphrase=(
            "not variables ch03 + not ownership + not structs + not CBOR + "
            "not TLS + not Python intro + not while + not a.count + not "
            "super + not io + not developer notes — Rust letter that "
            "prefixes unsigned integer type names??"
        ),
    ),
    _row(
        pack_i=7,
        paraphrase=(
            "skip unsigned prefix + variables + ownership + CBOR + TLS + "
            "super + intro + io + a.count + while + developer notes — "
            "Rust keyword that starts a struct type definition??"
        ),
    ),
    _row(
        pack_i=8,
        paraphrase=(
            "ignore JSON-RPC wallet + Core README + developer notes + "
            "BIP-32 + TLS + CBOR + BIP-1 + SegWit + BIPs index + BIP-39 + "
            "Rust variables — REST GET path pattern for a full block by "
            "hash with encoding suffixes??"
        ),
    ),
    _row(
        pack_i=9,
        paraphrase=(
            "not TLS handshake + not CBOR + not BIP-39 + not Python intro + "
            "not JSON-RPC + not BIP-1 + not REST block + not BIPs index + "
            "not BIP-32 + not io + not Rust variables — RFC 791 Time to "
            "Live TTL field how many bits??"
        ),
    ),
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTCORE_PACK
    if len(rows) != SMARTCORE_N:
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
    rows = pack if pack is not None else SMARTCORE_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_dodeca_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTCORE pack
    WHEN checking dodeca-hop distractor wiring
    THEN True iff every row maps CTXCORE companions and ≥8 carry cues.
    """
    cues = (
        "bip-39",
        "bip-32",
        "schnorr",
        "segwit",
        "witness",
        "cbor",
        "tls",
        "ihl",
        "a.count",
        "while",
        "super",
        "unsigned",
        "struct",
        "ownership",
        "wallet",
        "json-rpc",
        "rest",
        "ttl",
        "skip ",
        "ignore ",
        "forget ",
        "not ",
    )
    rows = pack if pack is not None else SMARTCORE_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        comps = companions_for(sid)
        wired = tuple(str(item.get(k, "")) for k in _COMP_KEYS)
        if wired != comps:
            return False
        if len({sid, *comps}) != 12:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def score_smartcore_lookup(
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
        "SMARTCORE LOOKUP dodeca paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if lookup_kind == "FALSE_HIT":
        err = True
        notes.append("SEMWRAP false-neighbor FP — kill path")
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartcore_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (GENCORE extractive peak, labeled)
    WHEN Cursor EVAL completion vs gold
    THEN gencore peak rubric on AO-aware spans; peak ≠ open-chat IQ label.
    """
    score, err, notes = score_gencore_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=False,
    )
    notes = list(notes) + [
        "SMARTCORE gen GENCORE peak (extractive) — Cursor scores completion",
        f"beat GENCORE ablated gen={GENCORE_ABLATED_GEN_MEAN} / peer "
        f"SMARTEDGE={SMARTEDGE_GEN_MEAN}",
    ]
    return float(score), bool(err), notes


def smartcore_stats(
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
    if len(lookup_scores) != SMARTCORE_N or len(gen_scores) != SMARTCORE_N:
        raise ValueError(f"SMARTCORE requires {SMARTCORE_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTCORE_N))
    g_mean = float(sum(gen_scores) / float(SMARTCORE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTCORE_N,
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
        "smartedge_gen_mean": SMARTEDGE_GEN_MEAN,
        "gencore_ablated_gen_mean": GENCORE_ABLATED_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_gencore_ablated": g_mean > GENCORE_ABLATED_GEN_MEAN,
        "peers_smartedge_gen": g_mean >= SMARTEDGE_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "dodeca_hop": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartcore(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTCORE dual-arm stats
    WHEN applying pesquisa §3 AO3 gate
    THEN KILL if false-hit; PROMOTE if lookup+cite+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")) or not bool(stats.get("dodeca_hop")):
        return "KILL"
    lookup_ok = bool(stats.get("pass_lookup")) and bool(stats.get("pass_cite"))
    if lookup_ok and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
