"""Wave AF2 H-SMARTULTRA: triple-distractor cite beyond SMARTMAX."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from af_session_ops import AF0_PACK
from ctxultra_ops import (
    CTXULTRA_SECONDARY,
    CTXULTRA_TERTIARY,
    secondary_for,
    tertiary_for,
)
from smartmax_ops import cite_ok, route_smartmax
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_wrap import normalize_question

__all__ = [
    "SMARTULTRA_ID",
    "SMARTULTRA_N",
    "SMARTULTRA_PACK",
    "MIN_MEAN",
    "MIN_CITE_OK",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "hard_paraphrase_ok",
    "paraphrase_collides_parents",
    "has_adversarial_noise",
    "has_triple_hop_cues",
    "route_smartultra",
    "cite_ok",
    "score_smartultra_trial",
    "smartultra_stats",
    "decide_smartultra",
]

SMARTULTRA_ID = "H-SMARTULTRA"
SMARTULTRA_N = 10
MIN_MEAN = 7.0  # pesquisa §5 AF2
# Stricter primary-cite bar than SMARTMAX (7).
MIN_CITE_OK = 8

# Triple-hop adversarial paraphrases of AF0 (sec+ter distractors; same gold).
SMARTULTRA_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AF-HITL-01",
        "app_id": "known-ask",
        "source_id": "bip-0001",
        "secondary_source": CTXULTRA_SECONDARY["bip-0001"],
        "tertiary_source": CTXULTRA_TERTIARY["bip-0001"],
        "parent_question": AF0_PACK[0]["question"],
        "paraphrase": (
            "skip BIP-32 xprv/xpub and BIP-39 mnemonic fluff — what is a BIP "
            "(BIP-1 purpose), who should care?? short"
        ),
        "gold": AF0_PACK[0]["gold"],
    },
    {
        "id": "AF-HITL-02",
        "app_id": "known-ask",
        "source_id": "bitcoin-doc-bips",
        "secondary_source": CTXULTRA_SECONDARY["bitcoin-doc-bips"],
        "tertiary_source": CTXULTRA_TERTIARY["bitcoin-doc-bips"],
        "parent_question": AF0_PACK[1]["question"],
        "paraphrase": (
            "ignore BIP-1 definition + Core README — which BIP does Core "
            "document for parallel soft-fork deployments??"
        ),
        "gold": AF0_PACK[1]["gold"],
    },
    {
        "id": "AF-HITL-03",
        "app_id": "known-ask",
        "source_id": "rust-book-ch03-02",
        "secondary_source": CTXULTRA_SECONDARY["rust-book-ch03-02"],
        "tertiary_source": CTXULTRA_TERTIARY["rust-book-ch03-02"],
        "parent_question": AF0_PACK[2]["question"],
        "paraphrase": (
            "not ownership ch04 and not vars-only ch03 — data-types chapter: "
            "two main groups??"
        ),
        "gold": AF0_PACK[2]["gold"],
    },
    {
        "id": "AF-HITL-04",
        "app_id": "howto",
        "source_id": "python-tutorial-classes",
        "secondary_source": CTXULTRA_SECONDARY["python-tutorial-classes"],
        "tertiary_source": CTXULTRA_TERTIARY["python-tutorial-classes"],
        "parent_question": AF0_PACK[3]["question"],
        "paraphrase": (
            "forget list queues / datastructures and intro add() — paste "
            "minimal Point with __init__(self, x, y) pls"
        ),
        "gold": AF0_PACK[3]["gold"],
    },
    {
        "id": "AF-HITL-05",
        "app_id": "howto",
        "source_id": "python-tutorial-control",
        "secondary_source": CTXULTRA_SECONDARY["python-tutorial-control"],
        "tertiary_source": CTXULTRA_TERTIARY["python-tutorial-control"],
        "parent_question": AF0_PACK[4]["question"],
        "paraphrase": (
            "skip class Point and intro fluff — for i in range(3): print(i) "
            "values in order??"
        ),
        "gold": AF0_PACK[4]["gold"],
    },
    {
        "id": "AF-HITL-06",
        "app_id": "howto",
        "source_id": "python-tutorial-intro",
        "secondary_source": CTXULTRA_SECONDARY["python-tutorial-intro"],
        "tertiary_source": CTXULTRA_TERTIARY["python-tutorial-intro"],
        "parent_question": AF0_PACK[5]["question"],
        "paraphrase": (
            "not controlflow range, not file I/O — write add(a, b) that "
            "returns the sum, one short fn"
        ),
        "gold": AF0_PACK[5]["gold"],
    },
    {
        "id": "AF-HITL-07",
        "app_id": "howto",
        "source_id": "rust-book-ch04-01",
        "secondary_source": CTXULTRA_SECONDARY["rust-book-ch04-01"],
        "tertiary_source": CTXULTRA_TERTIARY["rust-book-ch04-01"],
        "parent_question": AF0_PACK[6]["question"],
        "paraphrase": (
            "ignore scalar/compound types and struct User — why ownership "
            "exists with no GC?? two sentences"
        ),
        "gold": AF0_PACK[6]["gold"],
    },
    {
        "id": "AF-HITL-08",
        "app_id": "howto",
        "source_id": "rust-book-ch05-01",
        "secondary_source": CTXULTRA_SECONDARY["rust-book-ch05-01"],
        "tertiary_source": CTXULTRA_TERTIARY["rust-book-ch05-01"],
        "parent_question": AF0_PACK[7]["question"],
        "paraphrase": (
            "skip ownership essay + ch03 data-types — show struct User "
            "{ name: String } definition pls"
        ),
        "gold": AF0_PACK[7]["gold"],
    },
    {
        "id": "AF-HITL-09",
        "app_id": "long-doc",
        "source_id": "bitcoin-core-readme",
        "secondary_source": CTXULTRA_SECONDARY["bitcoin-core-readme"],
        "tertiary_source": CTXULTRA_TERTIARY["bitcoin-core-readme"],
        "parent_question": AF0_PACK[8]["question"],
        "paraphrase": (
            "not developer-notes, not bips.md catalog — Bitcoin Core on P2P: "
            "what with blocks and transactions??"
        ),
        "gold": AF0_PACK[8]["gold"],
    },
    {
        "id": "AF-HITL-10",
        "app_id": "long-doc",
        "source_id": "rfc8446",
        "secondary_source": CTXULTRA_SECONDARY["rfc8446"],
        "tertiary_source": CTXULTRA_TERTIARY["rfc8446"],
        "parent_question": AF0_PACK[9]["question"],
        "paraphrase": (
            "ignore RFC791 TTL and RFC8949 CBOR — TLS 1.3 handshake trying "
            "to establish what, plainly??"
        ),
        "gold": AF0_PACK[9]["gold"],
    },
)


def hard_paraphrase_ok(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTULTRA pack
    WHEN checking paraphrase rule
    THEN True iff every paraphrase normalize-key ≠ parent question.
    """
    rows = pack if pack is not None else SMARTULTRA_PACK
    if len(rows) != SMARTULTRA_N:
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
    rows = pack if pack is not None else SMARTULTRA_PACK
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
    GIVEN SMARTULTRA pack
    WHEN checking adversarial stress markers
    THEN True iff ≥7 paraphrases carry informal/noise cues.
    """
    cues = ("??", "pls", "py ", "rust ", "rfc", "skip ", "ignore ", "forget ")
    rows = pack if pack is not None else SMARTULTRA_PACK
    n = 0
    for item in rows:
        low = str(item.get("paraphrase", "")).lower()
        if any(c.lower() in low for c in cues):
            n += 1
    return n >= 7


def has_triple_hop_cues(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> bool:
    """
    GIVEN SMARTULTRA pack
    WHEN checking compose/cite triple-hop distractors
    THEN True iff every row has CTXULTRA sec+ter pairs and ≥8 carry
         dual-distractor / not-skip-ignore cues.
    """
    cues = (
        "bip-32",
        "bip-39",
        "xprv",
        "mnemonic",
        "bip-1",
        "readme",
        "ownership",
        "ch03",
        "ch04",
        "datastructures",
        "queues",
        "intro",
        "add(",
        "point",
        "range",
        "controlflow",
        "i/o",
        "file i/o",
        "scalar",
        "compound",
        "struct user",
        "developer-notes",
        "bips.md",
        "rfc791",
        "rfc8949",
        "cbor",
        "ttl",
        "not ",
        "skip ",
        "ignore ",
        "forget ",
    )
    rows = pack if pack is not None else SMARTULTRA_PACK
    n = 0
    for item in rows:
        sid = str(item.get("source_id", ""))
        sec = str(item.get("secondary_source", ""))
        ter = str(item.get("tertiary_source", ""))
        if not sid or sec != secondary_for(sid) or ter != tertiary_for(sid):
            return False
        if sec == ter or sec == sid or ter == sid:
            return False
        low = str(item.get("paraphrase", "")).lower()
        if any(c in low for c in cues):
            n += 1
    return n >= 8


def route_smartultra(completion: str, *, mode: str) -> tuple[str, str]:
    """Delegate to SMARTMAX ASKSMART route polish."""
    return route_smartmax(completion, mode=mode)


def score_smartultra_trial(
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
    GIVEN SMARTULTRA triple-hop paraphrase ask
    WHEN scoring HITL
    THEN (score, error, notes, cite_ok_flag).
    """
    from semwrap_ops import score_semwrap_trial

    text, _r = route_smartultra(completion, mode=mode)
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
            "SMARTULTRA triple-hop retrieve/compose/cite — not open chat"
            if cited
            else "FIX: cite primary under sec+ter distractors"
        ),
    ]
    if route == "PERIOD_BLOCK" and not err:
        return (
            1.0,
            True,
            notes + ["FIX: period collapse under smartultra"],
            False,
        )
    if (not cited) and not err:
        return score, True, notes, False
    return score, err, notes, cited


def smartultra_stats(
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
    GIVEN 10 SMARTULTRA scores + cite flags
    WHEN summarizing AF2
    THEN mean≥7 · false-hit≈0 · cite≥8.
    """
    if len(scores) != SMARTULTRA_N or len(errors) != SMARTULTRA_N:
        raise ValueError(
            f"SMARTULTRA requires exactly {SMARTULTRA_N} scores/errors"
        )
    if len(cites) != SMARTULTRA_N:
        raise ValueError(
            f"SMARTULTRA requires exactly {SMARTULTRA_N} cite flags"
        )
    mean = float(sum(scores) / float(SMARTULTRA_N))
    n_err = int(sum(1 for e in errors if e))
    n_cite = int(sum(1 for c in cites if c))
    return {
        "n_trials": SMARTULTRA_N,
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
        "beyond_smartmax_cite_bar": MIN_CITE_OK > 7,
    }


def decide_smartultra(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SMARTULTRA stats
    WHEN applying pesquisa §5 AF2 gate
    THEN PROMOTE if mean≥7 ∧ false-hit=0 ∧ cite≥8 ∧ quality;
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
