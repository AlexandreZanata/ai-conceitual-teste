"""Wave AM3 H-SMARTNEXT: deca-hop cite + GENTRUTH peak gen; kill SEMWRAP FPs."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from am_session_ops import AM0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN
from ctxnext_ops import companions_for
from gentrue_ops import score_gentrue_gen
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTNEXT_ID",
    "SMARTNEXT_N",
    "SMARTNEXT_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SMARTFRESH_GEN_MEAN",
    "SMARTPUSH_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_deca_hop_cues",
    "cite_ok",
    "score_smartnext_lookup",
    "score_smartnext_gen",
    "smartnext_stats",
    "decide_smartnext",
]

SMARTNEXT_ID = "H-SMARTNEXT"
SMARTNEXT_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AM3 — or honest HOLD
MIN_CITE_OK = 8
# Peer Wave AL SMARTFRESH peak-overlay mean (extractive — labeled).
SMARTFRESH_GEN_MEAN = 9.0
# Parent Wave AI SMARTPUSH open-gen mean under dual-arm Cursor EVAL.
SMARTPUSH_GEN_MEAN = 4.0

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
)


def _row(*, pack_i: int, paraphrase: str) -> dict[str, str]:
    p = AM0_PACK[pack_i]
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


# Deca-hop adversarial paraphrases of AM0 (CTXNEXT companions as distractors).
SMARTNEXT_PACK: tuple[dict[str, str], ...] = (
    _row(
        pack_i=0,
        paraphrase=(
            "skip BIP-32 key-data + SegWit P2WPKH + Schnorr + TLS + CBOR + "
            "BIP-1 + BIPs index + REST + JSON-RPC — BIP-39 with 160-bit ENT: "
            "how many mnemonic words??"
        ),
    ),
    _row(
        pack_i=1,
        paraphrase=(
            "ignore BIP-39 word count + P2WPKH stack + Schnorr + TLS + CBOR + "
            "BIP-1 + JSON-RPC + Core README + developer notes — BIP-32 key "
            "data field: how many bytes??"
        ),
    ),
    _row(
        pack_i=2,
        paraphrase=(
            "not BIP-39 words + not BIP-32 key-data + not Schnorr + not "
            "TLS + not CBOR + not BIPs index + not BIP-1 + not developer "
            "notes + not REST — BIP-141 version-0 P2WPKH witness stack "
            "item count??"
        ),
    ),
    _row(
        pack_i=3,
        paraphrase=(
            "forget setattr + loop else + intro + open() + IHL + Rust char + "
            "ownership + struct fields + variables — return index of x in "
            "list a, one method call??"
        ),
    ),
    _row(
        pack_i=4,
        paraphrase=(
            "skip setattr + a.index + intro + io + IHL + Rust ch03 + "
            "structs + ownership + char bytes — which clause runs when a "
            "for/while ends without break??"
        ),
    ),
    _row(
        pack_i=5,
        paraphrase=(
            "ignore a.index + loop else + intro + io + IHL + struct fields + "
            "Rust types + ch03 + ownership — built-in that sets a named "
            "attribute (with getattr/delattr)??"
        ),
    ),
    _row(
        pack_i=6,
        paraphrase=(
            "not variables ch03 + not ownership + not structs + not CBOR + "
            "not TLS + not Python intro + not control + not datastructures + "
            "not classes — Rust char value size in bytes??"
        ),
    ),
    _row(
        pack_i=7,
        paraphrase=(
            "skip char bytes + ownership + variables + CBOR + TLS + "
            "setattr + intro + io + datastructures — Rust name for the "
            "pieces of data inside a struct??"
        ),
    ),
    _row(
        pack_i=8,
        paraphrase=(
            "ignore JSON-RPC wallet + Core README + developer notes + "
            "BIP-32 + TLS + CBOR + BIP-1 + SegWit + BIPs index — REST GET "
            "path for mempool contents JSON??"
        ),
    ),
    _row(
        pack_i=9,
        paraphrase=(
            "not TLS handshake + not CBOR + not BIP-39 + not Python intro + "
            "not JSON-RPC + not BIP-1 + not REST mempool + not BIPs index + "
            "not BIP-32 — RFC 791 IHL field how many bits??"
        ),
    ),
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTNEXT_PACK
    if len(rows) != SMARTNEXT_N:
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
    rows = pack if pack is not None else SMARTNEXT_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_deca_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTNEXT pack
    WHEN checking deca-hop distractor wiring
    THEN True iff every row maps CTXNEXT companions and ≥8 carry cues.
    """
    cues = (
        "bip-39",
        "bip-32",
        "schnorr",
        "segwit",
        "p2wpkh",
        "cbor",
        "tls",
        "ihl",
        "index",
        "setattr",
        "else",
        "char",
        "fields",
        "mempool",
        "ownership",
        "wallet",
        "json-rpc",
        "rest",
        "skip ",
        "ignore ",
        "forget ",
        "not ",
    )
    rows = pack if pack is not None else SMARTNEXT_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        comps = companions_for(sid)
        wired = tuple(str(item.get(k, "")) for k in _COMP_KEYS)
        if wired != comps:
            return False
        if len({sid, *comps}) != 10:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def score_smartnext_lookup(
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
        "SMARTNEXT LOOKUP deca paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if lookup_kind == "FALSE_HIT":
        err = True
        notes.append("SEMWRAP false-neighbor FP — kill path")
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartnext_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (GENTRUTH extractive peak, labeled)
    WHEN Cursor EVAL completion vs gold
    THEN gentrue peak rubric on AM-aware spans; peak ≠ open-chat IQ label.
    """
    score, err, notes = score_gentrue_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=False,
    )
    notes = list(notes) + [
        "SMARTNEXT gen GENTRUTH peak (extractive) — Cursor scores completion",
        f"beat SMARTPUSH gen={SMARTPUSH_GEN_MEAN} / peer SMARTFRESH="
        f"{SMARTFRESH_GEN_MEAN}",
    ]
    return float(score), bool(err), notes


def smartnext_stats(
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
    if len(lookup_scores) != SMARTNEXT_N or len(gen_scores) != SMARTNEXT_N:
        raise ValueError(f"SMARTNEXT requires {SMARTNEXT_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTNEXT_N))
    g_mean = float(sum(gen_scores) / float(SMARTNEXT_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTNEXT_N,
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
        "smartfresh_gen_mean": SMARTFRESH_GEN_MEAN,
        "smartpush_gen_mean": SMARTPUSH_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_smartpush_gen": g_mean > SMARTPUSH_GEN_MEAN,
        "peers_smartfresh_gen": g_mean >= SMARTFRESH_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "deca_hop": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartnext(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTNEXT dual-arm stats
    WHEN applying pesquisa §3 AM3 gate
    THEN KILL if false-hit; PROMOTE if lookup+cite+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")) or not bool(stats.get("deca_hop")):
        return "KILL"
    lookup_ok = bool(stats.get("pass_lookup")) and bool(stats.get("pass_cite"))
    if lookup_ok and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
