"""Wave AE2 H-SMARTMAX: multi-hop retrieve/compose/cite beyond HARDPARA+COMPOSE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ae_session_ops import AE0_PACK
from asksmart_ops import is_period_collapse, strip_stop
from ctxmax_ops import CTXMAX_SECONDARY, secondary_for
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTMAX_ID",
    "SMARTMAX_N",
    "SMARTMAX_PACK",
    "MIN_MEAN",
    "MIN_CITE_OK",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "paraphrase_collides_parents",
    "has_adversarial_noise",
    "has_multihop_cues",
    "route_smartmax",
    "cite_ok",
    "score_smartmax_trial",
    "smartmax_stats",
    "decide_smartmax",
]

SMARTMAX_ID = "H-SMARTMAX"
SMARTMAX_N = 10
MIN_MEAN = 7.0  # pesquisa §5 AE2
MIN_CITE_OK = 7  # primary source cite quality

# Multi-hop adversarial paraphrases of AE0 (noise + secondary distractor; same gold).
SMARTMAX_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AE-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0032",
        "secondary_source": CTXMAX_SECONDARY["bip-0032"],
        "parent_question": AE0_PACK[0]["question"],
        "paraphrase": (
            "ignore BIP-39 mnemonic fluff — on BIP-32 mainnet Base58, "
            "xprv vs xpub prefixes?? short answer pls"
        ),
        "gold": AE0_PACK[0]["gold"],
    },
    {
        "id": "AE-HITL-02",
        "app_id": "known-ask",
        "source_id": "bip-0039",
        "secondary_source": CTXMAX_SECONDARY["bip-0039"],
        "parent_question": AE0_PACK[1]["question"],
        "paraphrase": (
            "not HD xprv/xpub — BIP-39 PBKDF2 seed: iteration count + PRF "
            "(HMAC?) one line"
        ),
        "gold": AE0_PACK[1]["gold"],
    },
    {
        "id": "AE-HITL-03",
        "app_id": "known-ask",
        "source_id": "bip-0340",
        "secondary_source": CTXMAX_SECONDARY["bip-0340"],
        "paraphrase": (
            "skip SegWit/wtxid side-quest: BIP-340 pubkey encoding is how "
            "many bytes??"
        ),
        "parent_question": AE0_PACK[2]["question"],
        "gold": AE0_PACK[2]["gold"],
    },
    {
        "id": "AE-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-datastructures",
        "secondary_source": CTXMAX_SECONDARY[
            "python-tutorial-datastructures"
        ],
        "parent_question": AE0_PACK[3]["question"],
        "paraphrase": (
            "py lists as FIFO queues (not classes/inheritance): why are they "
            "slow for front pops??"
        ),
        "gold": AE0_PACK[3]["gold"],
    },
    {
        "id": "AE-HITL-05",
        "app_id": "howto",
        "source_id": "rust-book-ch03",
        "secondary_source": CTXMAX_SECONDARY["rust-book-ch03"],
        "parent_question": AE0_PACK[4]["question"],
        "paraphrase": (
            "rust vars ch — not scalar/compound types: what is shadowing "
            "in one sentence?"
        ),
        "gold": AE0_PACK[4]["gold"],
    },
    {
        "id": "AE-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-io",
        "secondary_source": CTXMAX_SECONDARY["python-tutorial-io"],
        "parent_question": AE0_PACK[5]["question"],
        "paraphrase": (
            "py f-string rule (forget intro comments): start the literal "
            "how?? one short rule"
        ),
        "gold": AE0_PACK[5]["gold"],
    },
    {
        "id": "AE-HITL-07",
        "app_id": "long-doc",
        "source_id": "bitcoin-rest",
        "secondary_source": CTXMAX_SECONDARY["bitcoin-rest"],
        "parent_question": AE0_PACK[6]["question"],
        "paraphrase": (
            "not JSON-RPC cookie auth — Core REST: GET path for a tx hash "
            "with bin|hex|json suffixes?"
        ),
        "gold": AE0_PACK[6]["gold"],
    },
    {
        "id": "AE-HITL-08",
        "app_id": "long-doc",
        "source_id": "bitcoin-json-rpc",
        "secondary_source": CTXMAX_SECONDARY["bitcoin-json-rpc"],
        "parent_question": AE0_PACK[7]["question"],
        "paraphrase": (
            "skip /rest/tx — when rpcpassword unset, where is Core's "
            ".cookie RPC login file?"
        ),
        "gold": AE0_PACK[7]["gold"],
    },
    {
        "id": "AE-HITL-09",
        "app_id": "long-doc",
        "source_id": "rfc791",
        "secondary_source": CTXMAX_SECONDARY["rfc791"],
        "parent_question": AE0_PACK[8]["question"],
        "paraphrase": (
            "not TLS 1.3 / RFC8446 — RFC791 TTL: every module must do what "
            "to TTL, and why?"
        ),
        "gold": AE0_PACK[8]["gold"],
    },
    {
        "id": "AE-HITL-10",
        "app_id": "long-doc",
        "source_id": "bip-0141",
        "secondary_source": CTXMAX_SECONDARY["bip-0141"],
        "parent_question": AE0_PACK[9]["question"],
        "paraphrase": (
            "ignore BIP-340 Schnorr bytes — BIP-141: how does wtxid differ "
            "from unchanged txid??"
        ),
        "gold": AE0_PACK[9]["gold"],
    },
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTMAX pack
    WHEN checking paraphrase rule
    THEN True iff every paraphrase normalize-key ≠ parent question.
    """
    rows = pack if pack is not None else SMARTMAX_PACK
    if len(rows) != SMARTMAX_N:
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
    rows = pack if pack is not None else SMARTMAX_PACK
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
    GIVEN SMARTMAX pack
    WHEN checking adversarial stress markers
    THEN True iff ≥5 paraphrases carry informal/noise cues.
    """
    cues = ("??", "pls", "btc", "py ", "py-", "rust ", "rfc", "skip ", "ignore ")
    rows = pack if pack is not None else SMARTMAX_PACK
    n = 0
    for item in rows:
        low = str(item.get("paraphrase", "")).lower()
        if any(c.lower() in low for c in cues):
            n += 1
    return n >= 5


def has_multihop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTMAX pack
    WHEN checking compose/cite multi-hop distractors
    THEN True iff every row has CTXMAX secondary pair and ≥7 carry
         not/skip/ignore or secondary-domain distractor cues.
    """
    cues = (
        "bip-39",
        "mnemonic",
        "xprv",
        "segwit",
        "wtxid",
        "classes",
        "inheritance",
        "scalar",
        "compound",
        "intro",
        "json-rpc",
        "cookie",
        "/rest/",
        "tls",
        "rfc8446",
        "schnorr",
        "not ",
        "skip ",
        "ignore ",
        "forget ",
    )
    rows = pack if pack is not None else SMARTMAX_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        sec = str(item.get("secondary_source", ""))
        if not sid or not sec or sec != secondary_for(sid):
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 7


def route_smartmax(completion: str, *, mode: str) -> tuple[str, str]:
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


def cite_ok(
    *,
    expected_source_id: str,
    hit_source_id: str | None,
    lookup_kind: str,
) -> bool:
    """
    GIVEN primary source expectation + SEMWRAP hit
    WHEN checking cite quality
    THEN True iff TRUE_HIT and hit source matches primary (not secondary).
    """
    if lookup_kind != "TRUE_HIT":
        return False
    hit = str(hit_source_id or "").strip()
    return hit == str(expected_source_id).strip()


def score_smartmax_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    route: str,
    expected_source_id: str,
    hit_source_id: str | None,
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN SMARTMAX multi-hop paraphrase ask
    WHEN scoring HITL
    THEN (score, error, notes, cite_ok_flag).
    """
    from semwrap_ops import score_semwrap_trial

    text, _r = route_smartmax(completion, mode=mode)
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
    notes = list(notes) + [
        f"route={route}",
        f"cite_ok={cited} hit={hit_source_id} expect={expected_source_id}",
        (
            "SMARTMAX multi-hop retrieve/compose/cite — not open chat"
            if cited
            else "FIX: cite primary source under multi-hop distractor"
        ),
    ]
    if route == "PERIOD_BLOCK" and not err:
        return 1.0, True, notes + ["FIX: period collapse under smartmax"], False
    if (not cited) and not err:
        return score, True, notes, False
    return score, err, notes, cited


def smartmax_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    cites: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    n_semwrap_route: int,
    n_fix: int,
) -> dict[str, Any]:
    """
    GIVEN 10 SMARTMAX scores + cite flags
    WHEN summarizing AE2
    THEN mean≥7 · false-hit≈0 · cite≥7.
    """
    if len(scores) != SMARTMAX_N or len(errors) != SMARTMAX_N:
        raise ValueError(
            f"SMARTMAX requires exactly {SMARTMAX_N} scores/errors"
        )
    if len(cites) != SMARTMAX_N:
        raise ValueError(f"SMARTMAX requires exactly {SMARTMAX_N} cite flags")
    mean = float(sum(scores) / float(SMARTMAX_N))
    n_err = int(sum(1 for e in errors if e))
    n_cite = int(sum(1 for c in cites if c))
    return {
        "n_trials": SMARTMAX_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "n_cite_ok": n_cite,
        "n_semwrap_route": int(n_semwrap_route),
        "n_fix": int(n_fix),
        "min_mean": MIN_MEAN,
        "min_cite_ok": MIN_CITE_OK,
        "pass_mean": mean >= MIN_MEAN,
        "pass_false_hit": int(n_false_hit) == 0,
        "pass_cite": n_cite >= MIN_CITE_OK,
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean_bar": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_smartmax(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTMAX stats
    WHEN applying pesquisa §5 AE2 gate
    THEN PROMOTE if mean≥7 ∧ false-hit=0 ∧ cite≥7 ∧ quality;
         HOLD if false-hit=0 but soft-fail; KILL if false-hit.
    """
    if not bool(stats.get("pass_false_hit")):
        return "KILL"
    ok = (
        bool(stats.get("pass_mean"))
        and bool(stats.get("pass_cite"))
        and bool(stats.get("pass_quality"))
    )
    if ok:
        return "PROMOTE"
    return "HOLD"
