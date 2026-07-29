"""Contract: Wave BF2 H-SHIPUSE2 — Track A+ utilization (pesquisa §9)."""

from __future__ import annotations

from shipuse2_ops import (
    APPEND_ASK,
    BE_RESIDUAL_ASK,
    BF_RESIDUAL_ASK,
    KNOWN_ASK,
    OOD_ASK,
    OVERREFUSE_ASK,
    REQUIRED_MODES,
    SHIPUSE2_CHARTER,
    SHIPUSE2_CLAIM,
    SHIPUSE2_ID,
    SHIPUSE2_THESIS,
    attach_shipuse2,
    claim_matches_live,
    decide_shipuse2,
    operator_card_ok,
    paper_claim_ok,
)


def _arm(arm: str, raw: str, *, completion: str, product_mode: str | None = None) -> dict:
    row = attach_shipuse2(
        {
            "arm": arm,
            "mode": raw,
            "completion": completion,
            "wall_ms": 1.0,
            "n_new": 0,
        }
    )
    if product_mode:
        row["product_mode"] = product_mode
        row = attach_shipuse2(row)
    row["arm"] = arm
    return row


def _good_arms() -> list[dict]:
    return [
        _arm("LOOKUP", "WRAP_LOOKUP", completion="def add(a, b):\n    return a + b"),
        _arm(
            "PEAK",
            "PEAK_FAST+GENBASE",
            completion="Ownership is a set of rules that govern memory.",
        ),
        _arm(
            "ABSTAIN",
            "NO_ANSWER",
            completion="NO_ANSWER",
            product_mode="ABSTAIN",
        ),
    ]


def _probe(question: str, *, mode: str, completion: str) -> dict:
    raw = "WRAP_LOOKUP" if mode == "LOOKUP" else "NO_ANSWER"
    return attach_shipuse2(
        {
            "mode": raw,
            "product_mode": mode,
            "completion": completion,
            "wall_ms": 1.0,
            "n_new": 0,
            "question": question,
        }
    )


def _good_probes() -> list[dict]:
    return [
        _probe(KNOWN_ASK, mode="LOOKUP", completion="def add(a, b):\n    return a + b"),
        _probe(APPEND_ASK, mode="LOOKUP", completion="a.append(x)"),
        _probe(BE_RESIDUAL_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
        _probe(BF_RESIDUAL_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
        _probe(OVERREFUSE_ASK, mode="LOOKUP", completion="a.clear()"),
        _probe(OOD_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
    ]


def _docs() -> tuple[str, str, str, str]:
    recipes = (
        "Known-ask: npm run nano:z:ask -- --wrap --semwrap\n"
        "Modes LOOKUP PEAK DECODE ABSTAIN\n"
        "H-PREDINT hold: even → ABSTAIN\n"
        "Ship: AF packaged STRICT not unlabeled open chat\n"
    )
    card = recipes
    narrative = (
        "AF packaged STRICT not unlabeled open chat. "
        "True novel generative continue remains HOLD/DEFER under ≤5M."
    )
    tex = (
        "AF packaged STRICT --- not unlabeled open chat; not TAC unlocked. "
        "HOLD/DEFER true-continue under 5M."
    )
    return recipes, card, narrative, tex


def test_given_contract_when_constants_then_track_a_plus() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BF2 Track A+ utilization
    assert SHIPUSE2_ID == "H-SHIPUSE2"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert "Track A+" in SHIPUSE2_THESIS or "utilization" in SHIPUSE2_THESIS.lower()
    assert "not TAC unlocked" in SHIPUSE2_CLAIM
    util = SHIPUSE2_CHARTER.get("util_track") or {}
    assert "SHIPUSE2" in str(util.get("bf2_gate", ""))
    assert "is even" in BF_RESIDUAL_ASK.lower()


def test_given_operator_docs_when_check_then_ok() -> None:
    recipes, card, _, _ = _docs()
    assert operator_card_ok(recipes=recipes, card=card)
    assert not operator_card_ok(recipes="LOOKUP only", card=card)


def test_given_paper_texts_when_check_then_ok() -> None:
    _, _, narrative, tex = _docs()
    assert paper_claim_ok(narrative=narrative, paper_tex=tex)
    assert not paper_claim_ok(
        narrative="We claim true-continue unlocked now.",
        paper_tex=tex,
    )


def test_given_good_board_when_decide_then_promote() -> None:
    recipes, card, narrative, tex = _docs()
    arms = _good_arms()
    probes = _good_probes()
    decode = attach_shipuse2(
        {
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 10.0,
            "n_new": 8,
        }
    )
    near = _probe("BIP near miss", mode="ABSTAIN", completion="NO_ANSWER")
    decision = decide_shipuse2(
        arms=arms,
        probes=probes,
        decode_probe=decode,
        near_miss=near,
        recipes=recipes,
        card=card,
        narrative=narrative,
        paper_tex=tex,
        paper_build_ok=True,
    )
    assert decision.startswith("PROMOTE")
    assert claim_matches_live(claim=SHIPUSE2_CLAIM, arms=arms, probes=probes)


def test_given_bf_residual_lookup_when_decide_then_kill() -> None:
    recipes, card, narrative, tex = _docs()
    probes = _good_probes()
    for i, row in enumerate(probes):
        if "is even" in str(row.get("question", "")).lower():
            probes[i] = _probe(
                BF_RESIDUAL_ASK,
                mode="LOOKUP",
                completion="def add(a, b): return a + b",
            )
            break
    decision = decide_shipuse2(
        arms=_good_arms(),
        probes=probes,
        decode_probe=attach_shipuse2(
            {
                "mode": "NO_ANSWER",
                "product_mode": "ABSTAIN",
                "completion": "NO_ANSWER",
                "wall_ms": 1.0,
                "n_new": 0,
            }
        ),
        near_miss=_probe("near", mode="ABSTAIN", completion="NO_ANSWER"),
        recipes=recipes,
        card=card,
        narrative=narrative,
        paper_tex=tex,
        paper_build_ok=True,
    )
    assert decision.startswith("KILL")
    assert "BF residual" in decision


def test_given_missing_predint_needle_when_operator_then_fail() -> None:
    recipes = "nano:z:ask semwrap LOOKUP PEAK DECODE ABSTAIN"
    card = recipes
    assert not operator_card_ok(recipes=recipes, card=card)
