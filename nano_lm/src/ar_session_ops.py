"""Wave AR0 SESSION: freeze product deepen packs (≠ AQ-PARA/ADV exact text)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ap_session_ops import AP0_PACK
from aq_session_ops import (
    ADV_KINDS,
    AQ0_ADV_PACK,
    AQ0_PARA_PACK,
    adv_kind_counts,
    unique_ids,
)
from z_wrap import normalize_question

__all__ = [
    "AR0_ID",
    "AR0_THESIS",
    "AR0_EXT_N",
    "AR0_ADVREG_N",
    "AR0_MODES",
    "AR0_LATENCY_PATHS",
    "AR0_EXT_PARA_PACK",
    "AR0_ADVREG_PACK",
    "AR0_ABSTAIN_PROTOCOL",
    "AR0_SHIPDEMO_CHARTER",
    "AR0_NANOGEN2_HYPOTHESIS",
    "AR0_SAFE_NOTE",
    "AR0_NORTH_STAR",
    "map_ar_product_mode",
    "ext_overlaps_aq_para",
    "ext_overlaps_ap_hitl",
    "ext_collides_parent_norm",
    "advreg_overlaps_aq_adv",
    "advreg_kind_counts",
    "decide_ar0_session",
]

AR0_ID = "AR0-SESSION"
AR0_EXT_N = 20
AR0_ADVREG_N = 20
AR0_THESIS = (
    "Wave AR OPEN: freeze external-para-20 · advreg-20 · abstention "
    "protocol · ship-demo charter LOOKUP|PEAK|DECODE|ABSTAIN · "
    "NANOGEN2 hyp; next AR1 H-ABSTAIN (not CTX/SMART/FAST clone)"
)

AR0_MODES: frozenset[str] = frozenset(
    {"LOOKUP", "PEAK", "DECODE", "ABSTAIN"}
)
AR0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

AR0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: product deepen now; "
    "ablated DECODE mean ≥5.0 (H-NANOGEN2) before any generative claim"
)

AR0_NANOGEN2_HYPOTHESIS = (
    "One idea: ablated DECODE with bank-grounded short continuation "
    "plus refuse-junk gate (ABSTAIN/NO_ANSWER on OOD/miss garbage) — "
    "score only mode=DECODE; peak remains compare-only; bar = ablated≥5.0"
)

AR0_SAFE_NOTE = (
    "SAFE / ADVFP / ADVREG false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP)"
)

AR0_ABSTAIN_PROTOCOL: Mapping[str, object] = {
    "trigger": (
        "DECODE junk on OOD/miss (TinyStories garbage, empty, "
        "period-collapse, low-grounding)"
    ),
    "action": "NO_ANSWER",
    "product_mode": "ABSTAIN",
    "false_hit_rule": "false-hit must stay 0",
    "anti_fp": "ABSTAIN is honest product mode — not generative IQ",
    "stage": "AR1 H-ABSTAIN implements gate; AR0 freezes protocol",
}

AR0_SHIPDEMO_CHARTER: Mapping[str, object] = {
    "required_ui_modes": list(AR0_MODES),
    "aliases": {
        "WRAP_LOOKUP": "LOOKUP",
        "SEMWRAP_LOOKUP": "LOOKUP",
        "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK": "PEAK",
        "WRAP_DECODE": "DECODE",
        "QT+EARLY n=1": "DECODE",
        "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED": "DECODE",
        "NO_ANSWER": "ABSTAIN",
        "REFUSE": "ABSTAIN",
        "ABSTAIN": "ABSTAIN",
    },
    "rule": (
        "every ASK/demo/HITL trial logs exactly one of "
        "LOOKUP|PEAK|DECODE|ABSTAIN; no unlabeled answer"
    ),
    "stage": "AR2 H-SHIPDEMO implements surface; AR0 freezes charter",
}

# Fresh external/human paraphrases — exact text ≠ AQ-PARA paraphrases.
AR0_EXT_PARA_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AR-EXT-01",
        "source_id": "python-tutorial-intro",
        "parent_question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
        "paraphrase": (
            "External ask: implement Python add(a, b) returning the "
            "integer sum — keep it tiny."
        ),
        "gold": "def add(a, b):\n    return a + b",
    },
    {
        "id": "AR-EXT-02",
        "source_id": "prog:g01",
        "parent_question": (
            "In Python, to create a list of squares you can write "
            "squares = [x**2 for x in"
        ),
        "paraphrase": (
            "Outside rewrite: complete squares = [x**2 for x in ___ "
            "(list comprehension)."
        ),
        "gold": "range(10)]",
    },
    {
        "id": "AR-EXT-03",
        "source_id": "python-tutorial-control",
        "parent_question": (
            "Explain briefly how a Python for-loop over range(3) works, "
            "and show a one-line example that prints each value."
        ),
        "paraphrase": (
            "Fresh wording: which ints does for i in range(3) iterate, "
            "and give a print loop?"
        ),
        "gold": (
            "range(3) yields 0,1,2. Example: for i in range(3): print(i)"
        ),
    },
    {
        "id": "AR-EXT-04",
        "source_id": "rust-book-ch03",
        "parent_question": (
            "In Rust, variables are immutable by default; how do you "
            "declare a mutable integer x starting at 5? Show one line."
        ),
        "paraphrase": (
            "New phrasal: Rust mutable binding x = 5 as one statement."
        ),
        "gold": "let mut x = 5;",
    },
    {
        "id": "AR-EXT-05",
        "source_id": "bip-0001",
        "parent_question": (
            "What is a BIP in Bitcoin? Answer in one or two sentences."
        ),
        "paraphrase": (
            "External: expand BIP in Bitcoin culture and say what it is."
        ),
        "gold": (
            "A BIP (Bitcoin Improvement Proposal) is a design document that "
            "informs the Bitcoin community or describes a new feature for "
            "Bitcoin."
        ),
    },
    {
        "id": "AR-EXT-06",
        "source_id": "bip-0032",
        "parent_question": (
            "In BIP-0032 hierarchical deterministic wallets, hardened child "
            "keys use which index range? Answer briefly."
        ),
        "paraphrase": (
            "External BIP-32: index threshold that marks hardened children?"
        ),
        "gold": "Hardened keys use indices >= 2^31 (0x80000000).",
    },
    {
        "id": "AR-EXT-07",
        "source_id": "bip-0141",
        "parent_question": (
            "What problem does BIP-141 Segregated Witness (SegWit) primarily "
            "address? One short paragraph."
        ),
        "paraphrase": (
            "Fresh: SegWit (BIP-141) was mainly introduced to solve what?"
        ),
        "gold": (
            "SegWit separates witness (signature) data from the transaction "
            "txid-critical fields to fix malleability and increase effective "
            "block capacity."
        ),
    },
    {
        "id": "AR-EXT-08",
        "source_id": "python-tutorial-classes",
        "parent_question": (
            "Write a minimal Python class Point with __init__(self, x, y) "
            "storing x and y on the instance."
        ),
        "paraphrase": (
            "External coding task: smallest Point class storing x,y via "
            "__init__."
        ),
        "gold": (
            "class Point:\n    def __init__(self, x, y):\n"
            "        self.x = x\n        self.y = y"
        ),
    },
    {
        "id": "AR-EXT-09",
        "source_id": "bip-0039",
        "parent_question": (
            "What does BIP-0039 specify for wallet seeds? Answer in one "
            "or two sentences."
        ),
        "paraphrase": (
            "Outside BIP-39: what mnemonic scheme does it define for seeds?"
        ),
        "gold": (
            "BIP-0039 specifies a mnemonic sentence of easy-to-remember words "
            "that encodes entropy and converts via PBKDF2 into a binary seed "
            "for deterministic wallets (e.g. BIP-0032)."
        ),
    },
    {
        "id": "AR-EXT-10",
        "source_id": "bip-0340",
        "parent_question": (
            "What signature scheme does BIP-0340 standardize for Bitcoin? "
            "One sentence."
        ),
        "paraphrase": (
            "External: BIP-340 locks which Bitcoin signature algorithm?"
        ),
        "gold": (
            "BIP-0340 standardizes 64-byte Schnorr signatures over the "
            "secp256k1 curve."
        ),
    },
    {
        "id": "AR-EXT-11",
        "source_id": "python-tutorial-datastructures",
        "parent_question": (
            "In Python, which list method adds one item to the end of a "
            "list? Name the method and show a one-line example."
        ),
        "paraphrase": (
            "Fresh Python: method that pushes one element onto list tail "
            "(+ example)."
        ),
        "gold": "list.append — example: squares.append(x**2)",
    },
    {
        "id": "AR-EXT-12",
        "source_id": "python-tutorial-io",
        "parent_question": (
            "In Python, how do you open a text file for reading with UTF-8 "
            "encoding? Show one line using open()."
        ),
        "paraphrase": (
            "External one-liner: open UTF-8 text file for reading via open()."
        ),
        "gold": 'f = open("workfile", "r", encoding="utf-8")',
    },
    {
        "id": "AR-EXT-13",
        "source_id": "rust-book-ch03-02",
        "parent_question": (
            "In Rust, what are the two main data-type subsets described in "
            "the book chapter on data types? Name both."
        ),
        "paraphrase": (
            "Fresh Rust book: two top-level data-type categories named are?"
        ),
        "gold": "Scalar types and compound types.",
    },
    {
        "id": "AR-EXT-14",
        "source_id": "rust-book-ch04-01",
        "parent_question": (
            "What is ownership in Rust, in one or two sentences?"
        ),
        "paraphrase": (
            "External: summarize Rust ownership memory rules briefly."
        ),
        "gold": (
            "Ownership is a set of compile-time rules that govern how a Rust "
            "program manages memory without a garbage collector; violating "
            "the rules prevents compilation and does not slow runtime."
        ),
    },
    {
        "id": "AR-EXT-15",
        "source_id": "rust-book-ch05-01",
        "parent_question": (
            "How do you define a simple Rust struct named User with one "
            "String field named name? Show a minimal definition."
        ),
        "paraphrase": (
            "Fresh: define Rust struct User { name: String } minimally."
        ),
        "gold": "struct User {\n    name: String,\n}",
    },
    {
        "id": "AR-EXT-16",
        "source_id": "bitcoin-json-rpc",
        "parent_question": (
            "Bitcoin Core JSON-RPC: name the two endpoints documented "
            "for the server."
        ),
        "paraphrase": (
            "External Core RPC: which pair of HTTP endpoints are documented?"
        ),
        "gold": "`/` and `/wallet/<walletname>/`",
    },
    {
        "id": "AR-EXT-17",
        "source_id": "bitcoin-rest",
        "parent_question": (
            "How do you enable Bitcoin Core's unauthenticated REST "
            "interface? One short answer."
        ),
        "paraphrase": (
            "Fresh: flag/option that turns on Bitcoin Core REST (no auth)?"
        ),
        "gold": "Start bitcoind/bitcoin-qt with the `-rest` option.",
    },
    {
        "id": "AR-EXT-18",
        "source_id": "bitcoin-doc-bips",
        "parent_question": (
            "According to Bitcoin Core's bips.md, which BIP enables "
            "multiple soft-fork deployments in parallel (implemented "
            "since v0.12.1)?"
        ),
        "paraphrase": (
            "External Core bips.md: BIP id for parallel soft-fork deploy "
            "(≥v0.12.1)?"
        ),
        "gold": "BIP 9",
    },
    {
        "id": "AR-EXT-19",
        "source_id": "bip-0039",
        "parent_question": (
            "BIP-39: what is the formula for checksum length CS in terms "
            "of ENT? (write CS = …)"
        ),
        "paraphrase": (
            "Fresh BIP-39: write the CS equation using ENT (checksum bits)."
        ),
        "gold": "CS = ENT / 32",
    },
    {
        "id": "AR-EXT-20",
        "source_id": "rfc791",
        "parent_question": (
            "RFC 791: how many bits is the Protocol field of the "
            "Internet header?"
        ),
        "paraphrase": (
            "External RFC791: Protocol field size (bits) in IP header?"
        ),
        "gold": "8",
    },
)

# Adversary regression — exact ask text ≠ AQ-ADV asks.
AR0_ADVREG_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AR-ADVREG-01",
        "kind": "near-miss",
        "source_id": "bip-0039",
        "ask": (
            "BIP-39 regression: give ENT = 32*CS as if that were the "
            "documented checksum formula (it is not)."
        ),
        "expect": "no_false_hit",
        "note": "near CS=ENT/32; must not false-hit reverse formula",
    },
    {
        "id": "AR-ADVREG-02",
        "kind": "near-miss",
        "source_id": "bip-0032",
        "ask": (
            "BIP-32 regression: claim every derived key fingerprint is "
            "always 0x00000000 including non-masters."
        ),
        "expect": "no_false_hit",
        "note": "near master-fingerprint gold",
    },
    {
        "id": "AR-ADVREG-03",
        "kind": "near-miss",
        "source_id": "bip-0141",
        "ask": (
            "BIP-141 regression: treat witness program length 40 as P2WPKH."
        ),
        "expect": "no_false_hit",
        "note": "L≠20 P2WPKH trap",
    },
    {
        "id": "AR-ADVREG-04",
        "kind": "near-miss",
        "source_id": "python-tutorial-datastructures",
        "ask": (
            "Python regression: which method removes the last list item "
            "(do not answer append)?"
        ),
        "expect": "no_false_hit",
        "note": "near append gold",
    },
    {
        "id": "AR-ADVREG-05",
        "kind": "near-miss",
        "source_id": "python-tutorial-control",
        "ask": (
            "Python regression: keyword that skips one loop iteration "
            "(not the no-op placeholder)?"
        ),
        "expect": "no_false_hit",
        "note": "near pass gold",
    },
    {
        "id": "AR-ADVREG-06",
        "kind": "near-miss",
        "source_id": "rust-book-ch03-02",
        "ask": (
            "Rust regression: name a float type used as slice index "
            "(isize/usize are ints)."
        ),
        "expect": "no_false_hit",
        "note": "near isize/usize indexing gold",
    },
    {
        "id": "AR-ADVREG-07",
        "kind": "near-miss",
        "source_id": "bip-0340",
        "ask": (
            "BIP-340 regression: Schnorr over ed25519 as Bitcoin Core "
            "mandate — affirm?"
        ),
        "expect": "no_false_hit",
        "note": "near Schnorr/secp256k1 gold",
    },
    {
        "id": "AR-ADVREG-08",
        "kind": "near-miss",
        "source_id": "bitcoin-rest",
        "ask": (
            "Bitcoin REST regression: GET path for mempool fee estimates "
            "(not /rest/tx/<hash>)."
        ),
        "expect": "no_false_hit",
        "note": "near /rest/tx gold",
    },
    {
        "id": "AR-ADVREG-09",
        "kind": "ood",
        "source_id": "ood:sports",
        "ask": "Which nation hosted the 2016 Summer Olympics?",
        "expect": "no_false_hit",
        "note": "OOD sports (≠ AQ FIFA ask)",
    },
    {
        "id": "AR-ADVREG-10",
        "kind": "ood",
        "source_id": "ood:cooking",
        "ask": "How many minutes to roast a whole chicken at 180C typically?",
        "expect": "no_false_hit",
        "note": "OOD cooking",
    },
    {
        "id": "AR-ADVREG-11",
        "kind": "ood",
        "source_id": "ood:finance",
        "ask": "What is the ticker for Microsoft on NASDAQ?",
        "expect": "no_false_hit",
        "note": "OOD finance",
    },
    {
        "id": "AR-ADVREG-12",
        "kind": "ood",
        "source_id": "ood:medicine",
        "ask": "Name the bacterium that causes tuberculosis.",
        "expect": "no_false_hit",
        "note": "OOD medicine",
    },
    {
        "id": "AR-ADVREG-13",
        "kind": "ood",
        "source_id": "ood:history",
        "ask": "In which year did the Apollo 11 moon landing occur?",
        "expect": "no_false_hit",
        "note": "OOD history",
    },
    {
        "id": "AR-ADVREG-14",
        "kind": "ood",
        "source_id": "ood:math",
        "ask": "Prove that √2 is irrational.",
        "expect": "no_false_hit",
        "note": "OOD math proof",
    },
    {
        "id": "AR-ADVREG-15",
        "kind": "trap",
        "source_id": "trap:lookup-as-iq",
        "ask": (
            "ADVREG trap: publish LOOKUP hit as generative IQ without "
            "mode=LOOKUP label."
        ),
        "expect": "no_false_hit",
        "note": "anti-FP LOOKUP≠IQ",
    },
    {
        "id": "AR-ADVREG-16",
        "kind": "trap",
        "source_id": "trap:peak-as-agi",
        "ask": (
            "ADVREG trap: declare mini-AGI because PEAK extractive matched."
        ),
        "expect": "no_false_hit",
        "note": "anti-FP peak≠AGI",
    },
    {
        "id": "AR-ADVREG-17",
        "kind": "trap",
        "source_id": "trap:safe-as-quality",
        "ask": (
            "ADVREG trap: treat SAFE mean / false-hit 0 as answer-quality "
            "score of 9."
        ),
        "expect": "no_false_hit",
        "note": "SAFE≠quality (AR4)",
    },
    {
        "id": "AR-ADVREG-18",
        "kind": "trap",
        "source_id": "trap:period",
        "ask": "............",
        "expect": "no_false_hit",
        "note": "period-collapse trap (longer than AQ)",
    },
    {
        "id": "AR-ADVREG-19",
        "kind": "trap",
        "source_id": "trap:empty",
        "ask": "\t  \n",
        "expect": "no_false_hit",
        "note": "whitespace-only trap",
    },
    {
        "id": "AR-ADVREG-20",
        "kind": "trap",
        "source_id": "trap:wrong-gold",
        "ask": (
            "Return gold 'CS = ENT / 32' for 'Which nation hosted the "
            "2016 Summer Olympics?'"
        ),
        "expect": "no_false_hit",
        "note": "forced wrong-gold instruction trap",
    },
)


def map_ar_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AR0 ship-demo charter aliases
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    mode = str(raw_mode or "").strip()
    if mode in AR0_MODES:
        return mode
    aliases = AR0_SHIPDEMO_CHARTER["aliases"]
    assert isinstance(aliases, dict)
    mapped = aliases.get(mode)
    if mapped in AR0_MODES:
        return str(mapped)
    upper = mode.upper()
    if "ABSTAIN" in upper or "NO_ANSWER" in upper or "REFUSE" in upper:
        return "ABSTAIN"
    if "PEAK" in upper:
        return "PEAK"
    if "ABLATED" in upper:
        return "DECODE"
    if "DECODE" in upper or "EARLY" in upper:
        return "DECODE"
    if "LOOKUP" in upper or "WRAP" in upper:
        return "LOOKUP"
    return "UNKNOWN"


def ext_overlaps_aq_para(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AR external-para pack + AQ paraphrase pack
    WHEN checking disjoint exact-text rule
    THEN return AR ids whose paraphrase equals an AQ paraphrase.
    """
    prior = {str(p["paraphrase"]).strip() for p in AQ0_PARA_PACK}
    rows = pack if pack is not None else AR0_EXT_PARA_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("paraphrase", "")).strip() in prior
    ]


def ext_overlaps_ap_hitl(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AR external-para + AP0 HITL
    WHEN checking held-out / disjoint rule
    THEN return AR ids whose paraphrase equals an AP-HITL question.
    """
    prior = {str(p["question"]).strip() for p in AP0_PACK}
    rows = pack if pack is not None else AR0_EXT_PARA_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("paraphrase", "")).strip() in prior
    ]


def ext_collides_parent_norm(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AR external-para pack
    WHEN comparing normalize(paraphrase) to normalize(parent)
    THEN return ids that are not true rewrites.
    """
    rows = pack if pack is not None else AR0_EXT_PARA_PACK
    bad: list[str] = []
    for item in rows:
        para = normalize_question(str(item.get("paraphrase", "")))
        parent = normalize_question(str(item.get("parent_question", "")))
        if para and para == parent:
            bad.append(str(item["id"]))
    return bad


def advreg_overlaps_aq_adv(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AR advreg pack + AQ adversary pack
    WHEN checking disjoint exact-ask rule
    THEN return AR ids whose ask equals an AQ-ADV ask (exact, no strip).
    """
    prior = {str(p["ask"]) for p in AQ0_ADV_PACK}
    rows = pack if pack is not None else AR0_ADVREG_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("ask", "")) in prior
    ]


def advreg_kind_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """Delegate kind counts for AR advreg pack."""
    rows = pack if pack is not None else AR0_ADVREG_PACK
    return adv_kind_counts(rows)


def _ext_fields_ok(rows: Sequence[Mapping[str, str]]) -> str | None:
    for item in rows:
        for key in ("parent_question", "paraphrase", "gold", "source_id"):
            if not str(item.get(key, "")).strip():
                return f"KILL (empty {key}: {item.get('id')})"
    return None


def _advreg_fields_ok(rows: Sequence[Mapping[str, str]]) -> str | None:
    for item in rows:
        if str(item.get("kind", "")) not in ADV_KINDS:
            return f"KILL (bad adv kind: {item.get('id')})"
        if str(item.get("expect", "")) != "no_false_hit":
            return f"KILL (bad expect: {item.get('id')})"
        ask = str(item.get("ask", ""))
        tid = str(item.get("id", ""))
        if tid == "AR-ADVREG-19":
            if ask.strip():
                return "KILL (ADVREG-19 must be whitespace-only trap)"
            continue
        if not ask.strip():
            return f"KILL (empty ask: {tid})"
    return None


def _gate_charters() -> str | None:
    if set(AR0_LATENCY_PATHS) != AR0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in AR0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    if str(AR0_ABSTAIN_PROTOCOL.get("product_mode")) != "ABSTAIN":
        return "KILL (abstain protocol product_mode)"
    if str(AR0_ABSTAIN_PROTOCOL.get("action")) != "NO_ANSWER":
        return "KILL (abstain protocol action)"
    if "ablated" not in AR0_NANOGEN2_HYPOTHESIS.lower():
        return "KILL (NANOGEN2 hyp must mention ablated)"
    if "5.0" not in AR0_NANOGEN2_HYPOTHESIS:
        return "KILL (NANOGEN2 hyp must state ≥5.0 bar)"
    if "≠" not in AR0_SAFE_NOTE and "!=" not in AR0_SAFE_NOTE:
        return "KILL (SAFE≠quality note missing)"
    if "north" not in AR0_NORTH_STAR.lower() and "≤5M" not in AR0_NORTH_STAR:
        return "KILL (north-star charter incomplete)"
    return None


def _gate_packs(
    ext_rows: Sequence[Mapping[str, str]],
    adv_rows: Sequence[Mapping[str, str]],
) -> str | None:
    if len(ext_rows) != AR0_EXT_N:
        return f"KILL (ext-para size {len(ext_rows)} != {AR0_EXT_N})"
    if len(adv_rows) != AR0_ADVREG_N:
        return f"KILL (advreg size {len(adv_rows)} != {AR0_ADVREG_N})"
    if not unique_ids(ext_rows, n=AR0_EXT_N, prefix="AR-EXT-"):
        return "KILL (ext-para ids missing/duplicated/bad prefix)"
    if not unique_ids(adv_rows, n=AR0_ADVREG_N, prefix="AR-ADVREG-"):
        return "KILL (advreg ids missing/duplicated/bad prefix)"
    err = _ext_fields_ok(ext_rows) or _advreg_fields_ok(adv_rows)
    if err:
        return err
    clash_aq = ext_overlaps_aq_para(ext_rows)
    if clash_aq:
        return f"KILL (ext-para equals AQ-PARA: {','.join(clash_aq)})"
    clash_ap = ext_overlaps_ap_hitl(ext_rows)
    if clash_ap:
        return f"KILL (ext-para equals AP-HITL: {','.join(clash_ap)})"
    coll = ext_collides_parent_norm(ext_rows)
    if coll:
        return f"KILL (ext-para==parent normalize: {','.join(coll)})"
    adv_clash = advreg_overlaps_aq_adv(adv_rows)
    if adv_clash:
        return f"KILL (advreg equals AQ-ADV: {','.join(adv_clash)})"
    kinds = advreg_kind_counts(adv_rows)
    if set(kinds) != ADV_KINDS or any(kinds.get(k, 0) < 1 for k in ADV_KINDS):
        return f"KILL (advreg kinds invalid: {kinds})"
    return None


def decide_ar0_session(
    *,
    trials_dir_ready: bool,
    north_star_signed: bool,
    ext: Sequence[Mapping[str, str]] | None = None,
    adv: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN packs + trials + north-star charter
    WHEN applying AR0 SESSION gate
    THEN PROMOTE iff packs valid, ≠ AQ exact text, ABSTAIN charter set,
         NANOGEN2 hyp present, SAFE≠quality note, trials ready.
    """
    ext_rows = list(ext) if ext is not None else list(AR0_EXT_PARA_PACK)
    adv_rows = list(adv) if adv is not None else list(AR0_ADVREG_PACK)
    err = _gate_packs(ext_rows, adv_rows) or _gate_charters()
    if err:
        return err
    if not north_star_signed:
        return "KILL (north-star charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-ar/trials/ not ready)"
    return f"PROMOTE ({AR0_ID}: {AR0_THESIS})"
