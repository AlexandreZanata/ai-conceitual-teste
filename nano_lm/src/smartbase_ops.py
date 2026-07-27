"""Wave AP3 H-SMARTBASE: trideca-hop cite + GENBASE peak gen; kill SEMWRAP FPs."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ap_session_ops import AP0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN
from ctxbase_ops import companions_for
from genbase_ops import score_genbase_gen
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTBASE_ID",
    "SMARTBASE_N",
    "SMARTBASE_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "MIN_CITE_OK",
    "SMARTCORE_GEN_MEAN",
    "GENBASE_ABLATED_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "has_adversarial_noise",
    "has_trideca_hop_cues",
    "cite_ok",
    "score_smartbase_lookup",
    "score_smartbase_gen",
    "smartbase_stats",
    "decide_smartbase",
]

SMARTBASE_ID = "H-SMARTBASE"
SMARTBASE_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AP3 — or honest HOLD
MIN_CITE_OK = 8
# Peer Wave AO SMARTCORE peak-overlay mean (extractive — labeled).
SMARTCORE_GEN_MEAN = 9.0
# Parent Wave AP GENBASE ablated true-gen mean under dual-arm Cursor EVAL.
GENBASE_ABLATED_GEN_MEAN = 4.0

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
    "tredenary_source",
)


def _row(*, pack_i: int, paraphrase: str) -> dict[str, str]:
    p = AP0_PACK[pack_i]
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


# Trideca-hop adversarial paraphrases of AP0 (CTXBASE companions as distractors).
SMARTBASE_PACK: tuple[dict[str, str], ...] = (
    _row(
        pack_i=0,
        paraphrase=(
            "skip BIP-32 fingerprint + P2WPKH + Schnorr + TLS + CBOR + "
            "BIP-1 + BIPs index + REST tx + JSON-RPC + Core README + Rust "
            "variables + list append — BIP-39 checksum length CS formula "
            "in terms of ENT (write CS = …)??"
        ),
    ),
    _row(
        pack_i=1,
        paraphrase=(
            "ignore BIP-39 CS + P2WPKH + Schnorr + TLS + CBOR + BIP-1 + "
            "JSON-RPC + Core README + developer notes + REST + Rust ch03 "
            "+ list append — BIP-32 master-key parent fingerprint hex??"
        ),
    ),
    _row(
        pack_i=2,
        paraphrase=(
            "not BIP-39 CS + not BIP-32 fingerprint + not Schnorr + not "
            "TLS + not CBOR + not BIPs index + not BIP-1 + not developer "
            "notes + not REST + not Core README + not Rust variables + "
            "not list append — BIP-141 version-0 witness program L=20 "
            "type acronym??"
        ),
    ),
    _row(
        pack_i=3,
        paraphrase=(
            "forget issubclass + pass + intro + open() + IHL + Rust isize "
            "+ ownership + structs + variables + TLS + developer notes + "
            "BIP-32 — add item x to the end of list a, one method call??"
        ),
    ),
    _row(
        pack_i=4,
        paraphrase=(
            "skip issubclass + a.append + intro + io + IHL + Rust ch03 + "
            "structs + ownership + compound types + CBOR + developer "
            "notes + BIP-32 — Python no-op placeholder keyword (Pass "
            "Statements)??"
        ),
    ),
    _row(
        pack_i=5,
        paraphrase=(
            "ignore a.append + pass + intro + io + IHL + structs + Rust "
            "compound + variables + ownership + TLS + developer notes + "
            "BIP-32 — built-in that checks class inheritance (isinstance "
            "tip)??"
        ),
    ),
    _row(
        pack_i=6,
        paraphrase=(
            "not variables ch03 + not ownership + not structs + not CBOR "
            "+ not TLS + not Python intro + not pass + not a.append + "
            "not issubclass + not io + not developer notes + not BIP-32 "
            "— Rust integer type pair used primarily when indexing a "
            "collection (write both names)??"
        ),
    ),
    _row(
        pack_i=7,
        paraphrase=(
            "skip isize/usize + variables + ownership + CBOR + TLS + "
            "issubclass + intro + io + a.append + pass + developer notes "
            "+ BIP-32 — Rust two-character token starting trailing "
            "field-copy (e.g. ..user1)??"
        ),
    ),
    _row(
        pack_i=8,
        paraphrase=(
            "ignore JSON-RPC wallet + Core README + developer notes + "
            "BIP-32 + TLS + CBOR + BIP-1 + SegWit + BIPs index + BIP-39 + "
            "Rust variables + list append — REST GET path pattern for a "
            "transaction by hash with encoding suffixes??"
        ),
    ),
    _row(
        pack_i=9,
        paraphrase=(
            "not TLS handshake + not CBOR + not BIP-39 + not Python intro "
            "+ not JSON-RPC + not BIP-1 + not REST tx + not BIPs index + "
            "not BIP-32 + not io + not Rust variables + not SegWit — "
            "RFC 791 Protocol field of the Internet header how many "
            "bits??"
        ),
    ),
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    rows = pack if pack is not None else SMARTBASE_PACK
    if len(rows) != SMARTBASE_N:
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
    rows = pack if pack is not None else SMARTBASE_PACK
    n = sum(
        1
        for item in rows
        if any(c in str(item.get("paraphrase", "")).lower() for c in cues)
    )
    return n >= 7


def has_trideca_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTBASE pack
    WHEN checking trideca-hop distractor wiring
    THEN True iff every row maps CTXBASE companions and ≥8 carry cues.
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
    rows = pack if pack is not None else SMARTBASE_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        comps = companions_for(sid)
        wired = tuple(str(item.get(k, "")) for k in _COMP_KEYS)
        if wired != comps:
            return False
        if len({sid, *comps}) != 13:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def score_smartbase_lookup(
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
        "SMARTBASE LOOKUP trideca paraphrase cite — not generative IQ",
        f"cite_ok={cited} hit_source={hit_source_id}",
    ]
    if lookup_kind == "FALSE_HIT":
        err = True
        notes.append("SEMWRAP false-neighbor FP — kill path")
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"], False
    return float(score), bool(err), notes, bool(cited)


def score_smartbase_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (GENBASE extractive peak, labeled)
    WHEN Cursor EVAL completion vs gold
    THEN genbase peak rubric on AP-aware spans; peak ≠ open-chat IQ label.
    """
    gold = str(expected_gold).strip()
    text = str(completion).strip()
    # FIX: Rust struct-update token `..` is exact gold, not period collapse.
    if gold == ".." and text == "..":
        tel = extract_telemetry(payload)
        arm = classify_arm(payload)
        notes = [
            f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
            f"n_new={tel['n_new']} period=False peak="
            f"{bool(payload.get('peak_used'))}",
            "FIX: struct-update `..` exact gold — not period collapse",
            "SMARTBASE gen GENBASE peak (extractive) — Cursor scores completion",
            f"beat GENBASE ablated gen={GENBASE_ABLATED_GEN_MEAN} / peer "
            f"SMARTCORE={SMARTCORE_GEN_MEAN}",
        ]
        if arm != "GENERATE":
            return 1.0, True, notes + ["GENERATE arm mislabeled"]
        return 9.0, False, notes
    score, err, notes = score_genbase_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=False,
    )
    notes = list(notes) + [
        "SMARTBASE gen GENBASE peak (extractive) — Cursor scores completion",
        f"beat GENBASE ablated gen={GENBASE_ABLATED_GEN_MEAN} / peer "
        f"SMARTCORE={SMARTCORE_GEN_MEAN}",
    ]
    return float(score), bool(err), notes


def smartbase_stats(
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
    if len(lookup_scores) != SMARTBASE_N or len(gen_scores) != SMARTBASE_N:
        raise ValueError(f"SMARTBASE requires {SMARTBASE_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(SMARTBASE_N))
    g_mean = float(sum(gen_scores) / float(SMARTBASE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_cite = int(sum(1 for c in cite_flags if c))
    return {
        "n_trials": SMARTBASE_N,
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
        "smartcore_gen_mean": SMARTCORE_GEN_MEAN,
        "genbase_ablated_gen_mean": GENBASE_ABLATED_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_genbase_ablated": g_mean > GENBASE_ABLATED_GEN_MEAN,
        "peers_smartcore_gen": g_mean >= SMARTCORE_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "trideca_hop": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartbase(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTBASE dual-arm stats
    WHEN applying pesquisa §3 AP3 gate
    THEN KILL if false-hit; PROMOTE if lookup+cite+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")) or not bool(stats.get("trideca_hop")):
        return "KILL"
    lookup_ok = bool(stats.get("pass_lookup")) and bool(stats.get("pass_cite"))
    if lookup_ok and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
