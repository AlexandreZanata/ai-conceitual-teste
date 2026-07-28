"""Contract: Wave BE2 H-SHIPUSE — Track A utilization (pesquisa §9)."""

from __future__ import annotations

from shipuse_ops import (
    BE_RESIDUAL_ASK,
    KNOWN_ASK,
    OOD_ASK,
    OVERREFUSE_ASK,
    REQUIRED_MODES,
    SHIPUSE_CHARTER,
    SHIPUSE_CLAIM,
    SHIPUSE_ID,
    SHIPUSE_THESIS,
    attach_shipuse,
    claim_matches_live,
    decide_shipuse,
    operator_card_ok,
    paper_claim_ok,
)


def _arm(arm: str, raw: str, *, completion: str, product_mode: str | None = None) -> dict:
    row = attach_shipuse(
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
        row = attach_shipuse(row)
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
    row = attach_shipuse(
        {
            "mode": raw,
            "product_mode": mode,
            "completion": completion,
            "wall_ms": 1.0,
            "n_new": 0,
            "question": question,
        }
    )
    return row


def _good_probes() -> list[dict]:
    return [
        _probe(KNOWN_ASK, mode="LOOKUP", completion="def add(a, b):\n    return a + b"),
        _probe(BE_RESIDUAL_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
        _probe(OVERREFUSE_ASK, mode="LOOKUP", completion="a.clear()"),
        _probe(OOD_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
    ]


def _docs() -> tuple[str, str, str, str]:
    recipes = (
        "Known-ask: npm run nano:z:ask -- --wrap --semwrap\n"
        "Modes LOOKUP PEAK DECODE ABSTAIN\n"
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


def test_given_contract_when_constants_then_track_a() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BE2 Track A utilization
    assert SHIPUSE_ID == "H-SHIPUSE"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert "utilization" in SHIPUSE_THESIS.lower() or "Track A" in SHIPUSE_THESIS
    assert "not TAC unlocked" in SHIPUSE_CLAIM
    assert "SHIPUSE" in str(SHIPUSE_CHARTER.get("be2_gate") or "") or "SHIPUSE" in str(
        (SHIPUSE_CHARTER.get("util_track") or {}).get("be2_gate", "")
    )


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


def test_given_live_rows_when_claim_match_then_ok() -> None:
    arms = _good_arms()
    probes = _good_probes()
    assert claim_matches_live(claim=SHIPUSE_CLAIM, arms=arms, probes=probes)


def test_given_track_a_board_when_decide_then_promote() -> None:
    recipes, card, narrative, tex = _docs()
    out = decide_shipuse(
        arms=_good_arms(),
        probes=_good_probes(),
        decode_probe=_arm(
            "DECODE", "WRAP_DECODE", completion="NO_ANSWER", product_mode="ABSTAIN"
        ),
        near_miss=_probe("near", mode="ABSTAIN", completion="NO_ANSWER"),
        recipes=recipes,
        card=card,
        narrative=narrative,
        paper_tex=tex,
        paper_build_ok=True,
        anti_fp_signed=True,
    )
    assert out.startswith("PROMOTE")


def test_given_be_residual_lookup_when_decide_then_kill() -> None:
    recipes, card, narrative, tex = _docs()
    probes = _good_probes()
    probes[1] = _probe(
        BE_RESIDUAL_ASK,
        mode="LOOKUP",
        completion="def add(a, b):\n    return a + b",
    )
    out = decide_shipuse(
        arms=_good_arms(),
        probes=probes,
        decode_probe=_arm(
            "DECODE", "NO_ANSWER", completion="NO_ANSWER", product_mode="ABSTAIN"
        ),
        near_miss=_probe("near", mode="ABSTAIN", completion="NO_ANSWER"),
        recipes=recipes,
        card=card,
        narrative=narrative,
        paper_tex=tex,
        paper_build_ok=True,
    )
    assert out.startswith("KILL")
    assert "BE residual" in out


def test_given_paper_build_fail_when_decide_then_kill() -> None:
    recipes, card, narrative, tex = _docs()
    out = decide_shipuse(
        arms=_good_arms(),
        probes=_good_probes(),
        decode_probe=_arm(
            "DECODE", "NO_ANSWER", completion="NO_ANSWER", product_mode="ABSTAIN"
        ),
        near_miss=None,
        recipes=recipes,
        card=card,
        narrative=narrative,
        paper_tex=tex,
        paper_build_ok=False,
    )
    assert out.startswith("KILL")
    assert "paper:build" in out
