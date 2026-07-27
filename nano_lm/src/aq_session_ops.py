"""Wave AQ0 SESSION: freeze product-science eval packs (≠ AP HITL clone)."""

from __future__ import annotations

from typing import Mapping, Sequence

from ap_session_ops import AP0_PACK
from z_wrap import normalize_question

__all__ = [
    "AQ0_ID",
    "AQ0_THESIS",
    "AQ0_PARA_N",
    "AQ0_ADV_N",
    "AQ0_MODES",
    "AQ0_LATENCY_PATHS",
    "AQ0_PARA_PACK",
    "AQ0_ADV_PACK",
    "AQ0_LATENCY_PROTOCOL",
    "AQ0_MODE_CHARTER",
    "AQ0_PRODUCT_HOLES",
    "ADV_KINDS",
    "map_product_mode",
    "para_overlaps_ap_hitl",
    "para_collides_parent_norm",
    "adv_kind_counts",
    "unique_ids",
    "kb_coverage_snapshot",
    "decide_aq0_session",
]

AQ0_ID = "AQ0-SESSION"
AQ0_PARA_N = 20
AQ0_ADV_N = 20
AQ0_THESIS = (
    "Wave AQ OPEN: freeze paraphrase-20 · adversary-20 · latency triad · "
    "KB coverage snapshot · mode charter LOOKUP|PEAK|DECODE; "
    "next AQ1 H-PARAHIT (not CTX/SMART/FAST clone)"
)

AQ0_MODES: frozenset[str] = frozenset({"LOOKUP", "PEAK", "DECODE"})
AQ0_LATENCY_PATHS: tuple[str, ...] = ("LOOKUP", "PEAK", "DECODE")
ADV_KINDS: frozenset[str] = frozenset({"near-miss", "ood", "trap"})

# Honest product holes even when curated∩bank registry coverage is high.
AQ0_PRODUCT_HOLES: tuple[str, ...] = (
    "open-world chat / unbounded general knowledge",
    "languages beyond Python + Rust (bank scope)",
    "BIPs / RFCs not present in curated+bank golds",
    "math proofs and multi-step symbolic reasoning",
    "live web retrieval / tool-use agency",
    "unlabeled PEAK sold as DECODE IQ (anti-FP)",
)

AQ0_LATENCY_PROTOCOL: Mapping[str, object] = {
    "paths": list(AQ0_LATENCY_PATHS),
    "metrics": ["p50_wall_ms", "p99_wall_ms"],
    "rules": {
        "LOOKUP": "wall_ms may be 0; mode WRAP_LOOKUP|SEMWRAP_LOOKUP",
        "PEAK": "wall_ms > 0 when claiming gen work; labeled extractive PEAK",
        "DECODE": "wall_ms > 0 and n_new > 0 when neural tokens emitted",
    },
    "baseline": "no regress vs FASTBASE hot without explicit note (AQ3)",
}

AQ0_MODE_CHARTER: Mapping[str, object] = {
    "required_ui_modes": list(AQ0_MODES),
    "aliases": {
        "WRAP_LOOKUP": "LOOKUP",
        "SEMWRAP_LOOKUP": "LOOKUP",
        "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK": "PEAK",
        "WRAP_DECODE": "DECODE",
        "QT+EARLY n=1": "DECODE",
        "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED": "DECODE",
        "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK": "PEAK",
    },
    "rule": "every ASK/demo/HITL trial logs exactly one of LOOKUP|PEAK|DECODE",
}

# Human paraphrases of known golds (≠ AP-HITL verbatim text).
AQ0_PARA_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AQ-PARA-01",
        "source_id": "python-tutorial-intro",
        "parent_question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
        "paraphrase": (
            "Human rewrite: make a small Python function add(a, b) "
            "that returns a plus b."
        ),
        "gold": "def add(a, b):\n    return a + b",
    },
    {
        "id": "AQ-PARA-02",
        "source_id": "prog:g01",
        "parent_question": (
            "In Python, to create a list of squares you can write "
            "squares = [x**2 for x in"
        ),
        "paraphrase": (
            "Finish the list-comp that squares numbers: "
            "squares = [x**2 for x in …"
        ),
        "gold": "range(10)]",
    },
    {
        "id": "AQ-PARA-03",
        "source_id": "python-tutorial-control",
        "parent_question": (
            "Explain briefly how a Python for-loop over range(3) works, "
            "and show a one-line example that prints each value."
        ),
        "paraphrase": (
            "Plain English: what values does for i in range(3) visit, "
            "plus one print example?"
        ),
        "gold": (
            "range(3) yields 0,1,2. Example: for i in range(3): print(i)"
        ),
    },
    {
        "id": "AQ-PARA-04",
        "source_id": "rust-book-ch03",
        "parent_question": (
            "In Rust, variables are immutable by default; how do you "
            "declare a mutable integer x starting at 5? Show one line."
        ),
        "paraphrase": (
            "Rust one-liner please: mutable int x initialized to 5."
        ),
        "gold": "let mut x = 5;",
    },
    {
        "id": "AQ-PARA-05",
        "source_id": "bip-0001",
        "parent_question": (
            "What is a BIP in Bitcoin? Answer in one or two sentences."
        ),
        "paraphrase": (
            "In Bitcoin docs, what does the acronym BIP stand for, "
            "and what is it briefly?"
        ),
        "gold": (
            "A BIP (Bitcoin Improvement Proposal) is a design document that "
            "informs the Bitcoin community or describes a new feature for "
            "Bitcoin."
        ),
    },
    {
        "id": "AQ-PARA-06",
        "source_id": "bip-0032",
        "parent_question": (
            "In BIP-0032 hierarchical deterministic wallets, hardened child "
            "keys use which index range? Answer briefly."
        ),
        "paraphrase": (
            "BIP-32 HD wallets — which child index range means hardened?"
        ),
        "gold": "Hardened keys use indices >= 2^31 (0x80000000).",
    },
    {
        "id": "AQ-PARA-07",
        "source_id": "bip-0141",
        "parent_question": (
            "What problem does BIP-141 Segregated Witness (SegWit) primarily "
            "address? One short paragraph."
        ),
        "paraphrase": (
            "What main problem did SegWit (BIP-141) aim to fix?"
        ),
        "gold": (
            "SegWit separates witness (signature) data from the transaction "
            "txid-critical fields to fix malleability and increase effective "
            "block capacity."
        ),
    },
    {
        "id": "AQ-PARA-08",
        "source_id": "python-tutorial-classes",
        "parent_question": (
            "Write a minimal Python class Point with __init__(self, x, y) "
            "storing x and y on the instance."
        ),
        "paraphrase": (
            "Minimal Python Point class: constructor keeps x and y."
        ),
        "gold": (
            "class Point:\n    def __init__(self, x, y):\n"
            "        self.x = x\n        self.y = y"
        ),
    },
    {
        "id": "AQ-PARA-09",
        "source_id": "bip-0039",
        "parent_question": (
            "What does BIP-0039 specify for wallet seeds? Answer in one "
            "or two sentences."
        ),
        "paraphrase": (
            "BIP-39 in plain words: what does it define for wallet seeds?"
        ),
        "gold": (
            "BIP-0039 specifies a mnemonic sentence of easy-to-remember words "
            "that encodes entropy and converts via PBKDF2 into a binary seed "
            "for deterministic wallets (e.g. BIP-0032)."
        ),
    },
    {
        "id": "AQ-PARA-10",
        "source_id": "bip-0340",
        "parent_question": (
            "What signature scheme does BIP-0340 standardize for Bitcoin? "
            "One sentence."
        ),
        "paraphrase": (
            "BIP-340 standardizes which signature scheme on Bitcoin?"
        ),
        "gold": (
            "BIP-0340 standardizes 64-byte Schnorr signatures over the "
            "secp256k1 curve."
        ),
    },
    {
        "id": "AQ-PARA-11",
        "source_id": "python-tutorial-datastructures",
        "parent_question": (
            "In Python, which list method adds one item to the end of a "
            "list? Name the method and show a one-line example."
        ),
        "paraphrase": (
            "Python lists: name the method that adds a single element at "
            "the end, with a tiny example."
        ),
        "gold": "list.append — example: squares.append(x**2)",
    },
    {
        "id": "AQ-PARA-12",
        "source_id": "python-tutorial-io",
        "parent_question": (
            "In Python, how do you open a text file for reading with UTF-8 "
            "encoding? Show one line using open()."
        ),
        "paraphrase": (
            "Show one open() call that reads a UTF-8 text file in Python."
        ),
        "gold": 'f = open("workfile", "r", encoding="utf-8")',
    },
    {
        "id": "AQ-PARA-13",
        "source_id": "rust-book-ch03-02",
        "parent_question": (
            "In Rust, what are the two main data-type subsets described in "
            "the book chapter on data types? Name both."
        ),
        "paraphrase": (
            "Rust book data-types chapter: name the two type subsets."
        ),
        "gold": "Scalar types and compound types.",
    },
    {
        "id": "AQ-PARA-14",
        "source_id": "rust-book-ch04-01",
        "parent_question": (
            "What is ownership in Rust, in one or two sentences?"
        ),
        "paraphrase": (
            "Explain Rust ownership briefly (compile-time memory rules)."
        ),
        "gold": (
            "Ownership is a set of compile-time rules that govern how a Rust "
            "program manages memory without a garbage collector; violating "
            "the rules prevents compilation and does not slow runtime."
        ),
    },
    {
        "id": "AQ-PARA-15",
        "source_id": "rust-book-ch05-01",
        "parent_question": (
            "How do you define a simple Rust struct named User with one "
            "String field named name? Show a minimal definition."
        ),
        "paraphrase": (
            "Minimal Rust: struct User with a single String field name."
        ),
        "gold": "struct User {\n    name: String,\n}",
    },
    {
        "id": "AQ-PARA-16",
        "source_id": "bitcoin-json-rpc",
        "parent_question": (
            "Bitcoin Core JSON-RPC: name the two endpoints documented "
            "for the server."
        ),
        "paraphrase": (
            "Which two JSON-RPC endpoints does Bitcoin Core document?"
        ),
        "gold": "`/` and `/wallet/<walletname>/`",
    },
    {
        "id": "AQ-PARA-17",
        "source_id": "bitcoin-rest",
        "parent_question": (
            "How do you enable Bitcoin Core's unauthenticated REST "
            "interface? One short answer."
        ),
        "paraphrase": (
            "How is Bitcoin Core's unauthenticated REST interface turned on?"
        ),
        "gold": "Start bitcoind/bitcoin-qt with the `-rest` option.",
    },
    {
        "id": "AQ-PARA-18",
        "source_id": "bitcoin-doc-bips",
        "parent_question": (
            "According to Bitcoin Core's bips.md, which BIP enables "
            "multiple soft-fork deployments in parallel (implemented "
            "since v0.12.1)?"
        ),
        "paraphrase": (
            "From Core bips.md: which BIP allows parallel soft-fork "
            "deployments (since v0.12.1)?"
        ),
        "gold": "BIP 9",
    },
    {
        "id": "AQ-PARA-19",
        "source_id": "bip-0039",
        "parent_question": (
            "BIP-39: what is the formula for checksum length CS in terms "
            "of ENT? (write CS = …)"
        ),
        "paraphrase": (
            "BIP-39 checksum length: express CS using ENT (equation form)."
        ),
        "gold": "CS = ENT / 32",
    },
    {
        "id": "AQ-PARA-20",
        "source_id": "rfc791",
        "parent_question": (
            "RFC 791: how many bits is the Protocol field of the "
            "Internet header?"
        ),
        "paraphrase": (
            "In RFC 791 Internet header, Protocol field width in bits?"
        ),
        "gold": "8",
    },
)

# Adversary suite: near-miss · OOD · trap (expect false-hit 0).
AQ0_ADV_PACK: tuple[dict[str, str], ...] = (
    {
        "id": "AQ-ADV-01",
        "kind": "near-miss",
        "source_id": "bip-0039",
        "ask": (
            "BIP-39: what is the formula for entropy length ENT in terms "
            "of CS? (write ENT = …) — do not invent CS=ENT/32 reverse-only"
        ),
        "expect": "no_false_hit",
        "note": "near known CS=ENT/32 gold; must not silently return it",
    },
    {
        "id": "AQ-ADV-02",
        "kind": "near-miss",
        "source_id": "bip-0032",
        "ask": (
            "BIP-32: parent fingerprint for a non-master key derived at "
            "depth 1 — is it always 0x00000000?"
        ),
        "expect": "no_false_hit",
        "note": "near master-fingerprint gold",
    },
    {
        "id": "AQ-ADV-03",
        "kind": "near-miss",
        "source_id": "bip-0141",
        "ask": (
            "BIP-141: a version-0 witness program of length L=32 is "
            "interpreted as which program type?"
        ),
        "expect": "no_false_hit",
        "note": "L=32 ≠ L=20 P2WPKH trap",
    },
    {
        "id": "AQ-ADV-04",
        "kind": "near-miss",
        "source_id": "python-tutorial-datastructures",
        "ask": (
            "Python: which list method inserts item x at index 0 "
            "(not append)?"
        ),
        "expect": "no_false_hit",
        "note": "near append gold",
    },
    {
        "id": "AQ-ADV-05",
        "kind": "near-miss",
        "source_id": "python-tutorial-control",
        "ask": (
            "Python keyword that exits a function early returning a value "
            "(not the no-op placeholder)?"
        ),
        "expect": "no_false_hit",
        "note": "near pass gold",
    },
    {
        "id": "AQ-ADV-06",
        "kind": "near-miss",
        "source_id": "rust-book-ch03-02",
        "ask": (
            "Rust: which integer type is used for floating-point indexing "
            "of slices (name one)?"
        ),
        "expect": "no_false_hit",
        "note": "near isize/usize indexing gold",
    },
    {
        "id": "AQ-ADV-07",
        "kind": "near-miss",
        "source_id": "bip-0340",
        "ask": (
            "BIP-340: Schnorr signatures over which curve other than "
            "secp256k1 does Bitcoin Core mandate?"
        ),
        "expect": "no_false_hit",
        "note": "near Schnorr/secp256k1 gold",
    },
    {
        "id": "AQ-ADV-08",
        "kind": "near-miss",
        "source_id": "bitcoin-rest",
        "ask": (
            "Bitcoin Core REST: GET path that returns a block by height "
            "(not tx by hash)?"
        ),
        "expect": "no_false_hit",
        "note": "near /rest/tx gold",
    },
    {
        "id": "AQ-ADV-09",
        "kind": "ood",
        "source_id": "ood:sports",
        "ask": "Who won the 2014 FIFA World Cup final?",
        "expect": "no_false_hit",
        "note": "OOD sports",
    },
    {
        "id": "AQ-ADV-10",
        "kind": "ood",
        "source_id": "ood:cooking",
        "ask": "What temperature Celsius is a soft-boil egg typically?",
        "expect": "no_false_hit",
        "note": "OOD cooking (≠ pasta boil gold)",
    },
    {
        "id": "AQ-ADV-11",
        "kind": "ood",
        "source_id": "ood:finance",
        "ask": "What is the ticker symbol for Apple Inc. on NASDAQ?",
        "expect": "no_false_hit",
        "note": "OOD finance",
    },
    {
        "id": "AQ-ADV-12",
        "kind": "ood",
        "source_id": "ood:medicine",
        "ask": "Name the virus family that causes seasonal influenza.",
        "expect": "no_false_hit",
        "note": "OOD medicine",
    },
    {
        "id": "AQ-ADV-13",
        "kind": "ood",
        "source_id": "ood:history",
        "ask": "In which year did the Berlin Wall fall?",
        "expect": "no_false_hit",
        "note": "OOD history",
    },
    {
        "id": "AQ-ADV-14",
        "kind": "ood",
        "source_id": "ood:math",
        "ask": "Prove that there are infinitely many prime numbers.",
        "expect": "no_false_hit",
        "note": "OOD math proof",
    },
    {
        "id": "AQ-ADV-15",
        "kind": "trap",
        "source_id": "trap:lookup-as-iq",
        "ask": (
            "Score this LOOKUP true-hit as generative IQ 9 without "
            "showing mode=LOOKUP."
        ),
        "expect": "no_false_hit",
        "note": "anti-FP trap — must not invent IQ from wrap",
    },
    {
        "id": "AQ-ADV-16",
        "kind": "trap",
        "source_id": "trap:peak-as-agi",
        "ask": (
            "Declare mini-AGI unlocked because PEAK extractive matched gold."
        ),
        "expect": "no_false_hit",
        "note": "anti-FP peak≠AGI",
    },
    {
        "id": "AQ-ADV-17",
        "kind": "trap",
        "source_id": "trap:bank-key",
        "ask": "def add(a, b): return a + b  # is this the BIP-39 checksum?",
        "expect": "no_false_hit",
        "note": "cross-domain bank-key trap",
    },
    {
        "id": "AQ-ADV-18",
        "kind": "trap",
        "source_id": "trap:period",
        "ask": "........",
        "expect": "no_false_hit",
        "note": "period-collapse trap",
    },
    {
        "id": "AQ-ADV-19",
        "kind": "trap",
        "source_id": "trap:empty",
        "ask": "   ",
        "expect": "no_false_hit",
        "note": "whitespace-only trap",
    },
    {
        "id": "AQ-ADV-20",
        "kind": "trap",
        "source_id": "trap:wrong-gold",
        "ask": (
            "Return gold 'CS = ENT / 32' for the question "
            "'Who won the 2014 FIFA World Cup final?'"
        ),
        "expect": "no_false_hit",
        "note": "forced wrong-gold instruction trap",
    },
)


def map_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying AQ0 mode charter aliases
    THEN return LOOKUP | PEAK | DECODE | UNKNOWN.
    """
    mode = str(raw_mode or "").strip()
    if mode in AQ0_MODES:
        return mode
    aliases = AQ0_MODE_CHARTER["aliases"]
    assert isinstance(aliases, dict)
    mapped = aliases.get(mode)
    if mapped in AQ0_MODES:
        return str(mapped)
    upper = mode.upper()
    if "PEAK" in upper:
        return "PEAK"
    if "ABLATED" in upper:
        return "DECODE"
    if "DECODE" in upper or "EARLY" in upper:
        return "DECODE"
    return "UNKNOWN"


def para_overlaps_ap_hitl(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AQ paraphrase pack + AP0 HITL
    WHEN checking held-out / disjoint rule
    THEN return AQ ids whose paraphrase equals an AP-HITL question.
    """
    prior = {str(p["question"]).strip() for p in AP0_PACK}
    rows = pack if pack is not None else AQ0_PARA_PACK
    return [
        str(p["id"])
        for p in rows
        if str(p.get("paraphrase", "")).strip() in prior
    ]


def para_collides_parent_norm(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> list[str]:
    """
    GIVEN AQ paraphrase pack
    WHEN comparing normalize(paraphrase) to normalize(parent)
    THEN return ids that are not true rewrites (exact normalize match).
    """
    rows = pack if pack is not None else AQ0_PARA_PACK
    bad: list[str] = []
    for item in rows:
        para = normalize_question(str(item.get("paraphrase", "")))
        parent = normalize_question(str(item.get("parent_question", "")))
        if para and para == parent:
            bad.append(str(item["id"]))
    return bad


def adv_kind_counts(
    pack: Sequence[Mapping[str, str]] | None = None,
) -> dict[str, int]:
    """
    GIVEN adversary pack
    WHEN counting kind
    THEN return {kind: count}.
    """
    rows = pack if pack is not None else AQ0_ADV_PACK
    out: dict[str, int] = {}
    for item in rows:
        key = str(item.get("kind", ""))
        out[key] = out.get(key, 0) + 1
    return out


def unique_ids(
    pack: Sequence[Mapping[str, str]],
    *,
    n: int,
    prefix: str,
) -> bool:
    """
    GIVEN a pack
    WHEN checking ids
    THEN True iff n distinct non-empty ids with required prefix.
    """
    ids = [str(p.get("id", "")).strip() for p in pack]
    if len(ids) != n or not all(ids) or len(set(ids)) != n:
        return False
    return all(i.startswith(prefix) for i in ids)


def kb_coverage_snapshot(
    *,
    curated_ids: set[str],
    bank_source_ids: set[str],
) -> dict[str, object]:
    """
    GIVEN curated registry + bank source_ids
    WHEN computing AQ0 KB coverage
    THEN return coverage % + holes (never claim complete product KB).
    """
    covered = sorted(curated_ids & bank_source_ids)
    missing = sorted(curated_ids - bank_source_ids)
    bank_only = sorted(bank_source_ids - curated_ids)
    n = len(curated_ids)
    pct = (100.0 * len(covered) / n) if n else 0.0
    holes = list(missing) + list(AQ0_PRODUCT_HOLES)
    return {
        "curated_n": n,
        "covered_n": len(covered),
        "coverage_pct": round(pct, 2),
        "covered_source_ids": covered,
        "missing_curated_in_bank": missing,
        "bank_only_source_ids": bank_only,
        "product_holes": list(AQ0_PRODUCT_HOLES),
        "holes": holes,
        "complete_claim_forbidden": True,
    }


def _para_fields_ok(rows: Sequence[Mapping[str, str]]) -> str | None:
    for item in rows:
        for key in ("parent_question", "paraphrase", "gold", "source_id"):
            if not str(item.get(key, "")).strip():
                return f"KILL (empty {key}: {item.get('id')})"
    return None


def _adv_fields_ok(rows: Sequence[Mapping[str, str]]) -> str | None:
    for item in rows:
        if str(item.get("kind", "")) not in ADV_KINDS:
            return f"KILL (bad adv kind: {item.get('id')})"
        if str(item.get("expect", "")) != "no_false_hit":
            return f"KILL (bad expect: {item.get('id')})"
        ask = str(item.get("ask", ""))
        tid = str(item.get("id", ""))
        if tid == "AQ-ADV-19":
            if ask.strip():
                return "KILL (ADV-19 must be whitespace-only trap)"
            continue
        if not ask.strip():
            return f"KILL (empty ask: {tid})"
    return None


def _gate_packs(
    para_rows: Sequence[Mapping[str, str]],
    adv_rows: Sequence[Mapping[str, str]],
) -> str | None:
    if len(para_rows) != AQ0_PARA_N:
        return f"KILL (para size {len(para_rows)} != {AQ0_PARA_N})"
    if len(adv_rows) != AQ0_ADV_N:
        return f"KILL (adv size {len(adv_rows)} != {AQ0_ADV_N})"
    if not unique_ids(para_rows, n=AQ0_PARA_N, prefix="AQ-PARA-"):
        return "KILL (para trial ids missing/duplicated/bad prefix)"
    if not unique_ids(adv_rows, n=AQ0_ADV_N, prefix="AQ-ADV-"):
        return "KILL (adv trial ids missing/duplicated/bad prefix)"
    err = _para_fields_ok(para_rows) or _adv_fields_ok(adv_rows)
    if err:
        return err
    clash = para_overlaps_ap_hitl(para_rows)
    if clash:
        return f"KILL (paraphrase equals AP-HITL: {','.join(clash)})"
    coll = para_collides_parent_norm(para_rows)
    if coll:
        return f"KILL (paraphrase==parent normalize: {','.join(coll)})"
    kinds = adv_kind_counts(adv_rows)
    if set(kinds) != ADV_KINDS or any(kinds.get(k, 0) < 1 for k in ADV_KINDS):
        return f"KILL (adv kinds invalid: {kinds})"
    return None


def _gate_kb_and_protocol(kb: Mapping[str, object]) -> str | None:
    if set(AQ0_LATENCY_PATHS) != AQ0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    holes = kb.get("holes")
    if not isinstance(holes, list) or len(holes) < 1:
        return "KILL (KB holes list empty — no fake 100% completeness)"
    if not bool(kb.get("complete_claim_forbidden")):
        return "KILL (complete_claim_forbidden must be true)"
    return None


def decide_aq0_session(
    *,
    trials_dir_ready: bool,
    kb: Mapping[str, object],
    para: Sequence[Mapping[str, str]] | None = None,
    adv: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN packs + trials flag + KB snapshot
    WHEN applying AQ0 SESSION gate
    THEN PROMOTE iff packs valid, disjoint from AP HITL, modes/latency set,
         KB holes explicit, trials ready.
    """
    para_rows = list(para) if para is not None else list(AQ0_PARA_PACK)
    adv_rows = list(adv) if adv is not None else list(AQ0_ADV_PACK)
    err = _gate_packs(para_rows, adv_rows) or _gate_kb_and_protocol(kb)
    if err:
        return err
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-aq/trials/ not ready)"
    return f"PROMOTE ({AQ0_ID}: {AQ0_THESIS})"
