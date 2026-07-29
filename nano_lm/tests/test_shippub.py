"""Contract: Wave BG2 H-SHIPPUB — Track A++ utilization (pesquisa §9)."""

from __future__ import annotations

from shippub_ops import (
    APPEND_ASK,
    BE_RESIDUAL_ASK,
    BF_RESIDUAL_ASK,
    BG_TRANSFORM_ASK,
    BG_UNARY_ASK,
    KNOWN_ASK,
    OOD_ASK,
    OVERREFUSE_ASK,
    REQUIRED_MODES,
    SHIPPUB_CHARTER,
    SHIPPUB_CLAIM,
    SHIPPUB_ID,
    SHIPPUB_THESIS,
    attach_shippub,
    claim_matches_live,
    decide_shippub,
    operator_card_ok,
    paper_arxiv_ok,
    paper_claim_ok,
)


def _arm(
    arm: str, raw: str, *, completion: str, product_mode: str | None = None
) -> dict:
    row = attach_shippub(
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
        row = attach_shippub(row)
    row["arm"] = arm
    return row


def _good_arms() -> list[dict]:
    return [
        _arm(
            "LOOKUP",
            "WRAP_LOOKUP",
            completion="def add(a, b):\n    return a + b",
        ),
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
    return attach_shippub(
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
        _probe(
            KNOWN_ASK, mode="LOOKUP", completion="def add(a, b):\n    return a + b"
        ),
        _probe(APPEND_ASK, mode="LOOKUP", completion="a.append(x)"),
        _probe(BE_RESIDUAL_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
        _probe(BF_RESIDUAL_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
        _probe(BG_UNARY_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
        _probe(BG_TRANSFORM_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
        _probe(OVERREFUSE_ASK, mode="LOOKUP", completion="a.clear()"),
        _probe(OOD_ASK, mode="ABSTAIN", completion="NO_ANSWER"),
    ]


def _docs() -> tuple[str, str, str, str, str]:
    recipes = (
        "Known-ask: npm run nano:z:ask -- --wrap --semwrap\n"
        "Modes LOOKUP PEAK DECODE ABSTAIN\n"
        "H-UNARYINT hold: absolute value → ABSTAIN\n"
        "Ship: AF packaged STRICT not unlabeled open chat\n"
    )
    card = recipes
    narrative = (
        "AF packaged STRICT not unlabeled open chat. "
        "Workshop / arXiv selective retriever. "
        "True novel generative continue remains HOLD/DEFER under ≤5M."
    )
    tex = (
        "AF packaged STRICT --- not unlabeled open chat; not TAC unlocked. "
        "HOLD/DEFER true-continue under 5M."
    )
    arxiv = "# arXiv path\nselective retriever + refuse ≤5M\n"
    return recipes, card, narrative, tex, arxiv


def test_given_contract_when_constants_then_track_a_plusplus() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BG2 Track A++ utilization
    assert SHIPPUB_ID == "H-SHIPPUB"
    assert REQUIRED_MODES == ("LOOKUP", "PEAK", "DECODE", "ABSTAIN")
    assert "Track A++" in SHIPPUB_THESIS or "arXiv" in SHIPPUB_THESIS
    assert "not TAC unlocked" in SHIPPUB_CLAIM
    util = SHIPPUB_CHARTER.get("util_track") or {}
    assert "SHIPPUB" in str(util.get("bg2_gate", ""))
    assert "absolute value" in BG_UNARY_ASK.lower()
    assert "uppercase" in BG_TRANSFORM_ASK.lower()


def test_given_operator_docs_when_check_then_ok() -> None:
    recipes, card, _, _, _ = _docs()
    assert operator_card_ok(recipes=recipes, card=card)
    assert not operator_card_ok(recipes="LOOKUP only", card=card)


def test_given_paper_texts_when_check_then_ok() -> None:
    _, _, narrative, tex, arxiv = _docs()
    assert paper_claim_ok(narrative=narrative, paper_tex=tex)
    assert paper_arxiv_ok(narrative=narrative, arxiv_md=arxiv)
    assert not paper_claim_ok(
        narrative="We claim true-continue unlocked now.",
        paper_tex=tex,
    )
    assert not paper_arxiv_ok(narrative="no path", arxiv_md="")


def test_given_good_board_when_decide_then_promote() -> None:
    recipes, card, narrative, tex, arxiv = _docs()
    arms = _good_arms()
    probes = _good_probes()
    decode = attach_shippub(
        {
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "wall_ms": 10.0,
            "n_new": 8,
        }
    )
    near = _probe("BIP near miss", mode="ABSTAIN", completion="NO_ANSWER")
    decision = decide_shippub(
        arms=arms,
        probes=probes,
        decode_probe=decode,
        near_miss=near,
        recipes=recipes,
        card=card,
        narrative=narrative,
        paper_tex=tex,
        arxiv_md=arxiv,
        paper_build_ok=True,
    )
    assert decision.startswith("PROMOTE")
    assert claim_matches_live(claim=SHIPPUB_CLAIM, arms=arms, probes=probes)


def test_given_bg_unary_lookup_when_decide_then_kill() -> None:
    recipes, card, narrative, tex, arxiv = _docs()
    probes = _good_probes()
    for i, row in enumerate(probes):
        if "absolute value" in str(row.get("question", "")).lower():
            probes[i] = _probe(
                BG_UNARY_ASK,
                mode="LOOKUP",
                completion="def add(a, b): return a + b",
            )
            break
    decision = decide_shippub(
        arms=_good_arms(),
        probes=probes,
        decode_probe=attach_shippub(
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
        arxiv_md=arxiv,
        paper_build_ok=True,
    )
    assert decision.startswith("KILL")
    assert "BG unary" in decision


def test_given_missing_unaryint_needle_when_operator_then_fail() -> None:
    recipes = "nano:z:ask semwrap LOOKUP PEAK DECODE ABSTAIN H-PREDINT"
    card = recipes
    assert not operator_card_ok(recipes=recipes, card=card)
