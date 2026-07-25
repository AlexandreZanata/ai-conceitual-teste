"""
Contract: champion card documents tip-stack after TIPD (STAG′ official).
"""

from __future__ import annotations

from pathlib import Path

CARD = Path("docs/results/nano-lm/champion-card.md")


def test_given_card_when_read_then_official_tips_present() -> None:
    text = CARD.read_text(encoding="utf-8")
    for tip in ("H-STAG′", "H-EARLY", "H-POOL", "H-STAG"):
        assert tip in text, f"missing {tip}"
    assert "STAG_PRIME" in text or "TIPD" in text


def test_given_card_when_read_then_compose_kills_listed() -> None:
    text = CARD.read_text(encoding="utf-8")
    for hid in ("H-SYS", "H-JOINT", "H-CACHE", "H-CAP"):
        assert hid in text


def test_given_card_when_read_then_wave_v_parked() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-DOM" in text or "DOM" in text
    assert "COMPLETE" in text or "PARKED" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_hprog_promote() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-PROG" in text or "PROG" in text
    assert "formal-hprog-programming" in text


def test_given_card_when_read_then_hbtc_smoke() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-BTC" in text or "BTC" in text
    assert "formal-hbtc-bitcoin" in text


def test_given_card_when_read_then_hmixd_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-MIXD" in text or "MIXD" in text
    assert "KILL" in text
    assert "hmixd-mix" in text or "formal-hmixd" in text


def test_given_card_when_read_then_wave_w_complete() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "Wave W" in text
    assert "COMPLETE" in text
    assert "wave-w-summary" in text
    assert "Wave X" in text
    assert "ACTIVE" in text or "PARKED" in text


def test_given_card_when_read_then_heff_formal() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-EFF" in text or "EFF" in text
    assert "formal-heff-efficiency" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_htchr_promote() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-TCHR" in text or "TCHR" in text
    assert "formal-htchr-code-teacher" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_hrag_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-RAG" in text or "RAG" in text
    assert "KILL" in text
    assert "hrag-retrieve" in text


def test_given_card_when_read_then_hctx_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-CTX" in text or "CTX" in text
    assert "KILL" in text
    assert "hctx-long-window" in text


def test_given_card_when_read_then_hqt_promote() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-QT" in text or "QT" in text
    assert "formal-hqt-quantize" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_hckd_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-CKD" in text or "CKD" in text
    assert "KILL" in text
    assert "hckd-code-kd" in text


def test_given_card_when_read_then_hqctx_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-QCTX" in text or "QCTX" in text
    assert "KILL" in text
    assert "hqctx-born-attn" in text


def test_given_card_when_read_then_hqcomp_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-QCOMP" in text or "QCOMP" in text
    assert "KILL" in text
    assert "hqcomp-shadow-kv" in text


def test_given_card_when_read_then_hqubitkv_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-QUBITKV" in text or "QUBITKV" in text
    assert "KILL" in text
    assert "hqubitkv-critical-kv" in text


def test_given_card_when_read_then_hgenc_promote() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-GENC" in text or "GENC" in text
    assert "formal-hgenc-genome" in text
    assert "PROMOTE" in text


def test_given_card_when_read_then_hgenq_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-GENQ" in text or "GENQ" in text
    assert "KILL" in text
    assert "hgenq-amplitude" in text


def test_given_card_when_read_then_hdist_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-DIST" in text or "DIST" in text
    assert "KILL" in text
    assert "hdist-distill" in text


def test_given_card_when_read_then_hqslot_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-SLOT" in text or "Q-SLOT" in text or "QSLOT" in text
    assert "KILL" in text
    assert "hqslot-slots" in text


def test_given_card_when_read_then_hqinterf_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-INTERF" in text or "INTERF" in text
    assert "KILL" in text
    assert "hqinterf-interference" in text


def test_given_card_when_read_then_habsrev_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-REV" in text or "ABS-REV" in text
    assert "KILL" in text
    assert "habsrev-reverse" in text


def test_given_card_when_read_then_hqanneal_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-ANNEAL" in text or "ANNEAL" in text
    assert "KILL" in text
    assert "hqanneal-anneal" in text


def test_given_card_when_read_then_hspiral_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-SPIRAL" in text or "SPIRAL" in text
    assert "KILL" in text
    assert "habsspiral-spiral" in text


def test_given_card_when_read_then_hqgrover_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-GROVER" in text or "GROVER" in text
    assert "KILL" in text
    assert "hqgrover-grover" in text


def test_given_card_when_read_then_hqtunnel_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-TUNNEL" in text or "TUNNEL" in text
    assert "KILL" in text
    assert "hqtunnel-tunnel" in text


def test_given_card_when_read_then_hqbell_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-BELL" in text or "BELL" in text
    assert "KILL" in text
    assert "hqbell-bell" in text


def test_given_card_when_read_then_horacle1_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-ORACLE1" in text or "ORACLE1" in text
    assert "KILL" in text
    assert "horacle1-oracle" in text


def test_given_card_when_read_then_hdna_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-DNA" in text or "DNA" in text
    assert "KILL" in text
    assert "hdna-dna" in text


def test_given_card_when_read_then_hdebate_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-DEBATE" in text or "DEBATE" in text
    assert "KILL" in text
    assert "hdebate-debate" in text


def test_given_card_when_read_then_hholo_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-HOLO" in text or "HOLO" in text
    assert "KILL" in text
    assert "hholo-holo" in text
    assert "H-ABS-PHASE" in text or "PHASE" in text


def test_given_card_when_read_then_hphase_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-PHASE" in text or "PHASE" in text
    assert "KILL" in text
    assert "hphase-phase" in text
    assert "H-Q-ENTPOS" in text or "ENTPOS" in text


def test_given_card_when_read_then_hentpos_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-ENTPOS" in text or "ENTPOS" in text
    assert "KILL" in text
    assert "hentpos-entpos" in text
    assert "H-Q-MEASURE" in text or "MEASURE" in text


def test_given_card_when_read_then_hmeasure_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-MEASURE" in text or "MEASURE" in text
    assert "KILL" in text
    assert "hmeasure-measure" in text
    assert "H-Q-TELE" in text or "TELE" in text


def test_given_card_when_read_then_htele_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-TELE" in text or "TELE" in text
    assert "KILL" in text
    assert "htele-teleport" in text
    assert "H-Q-WIGNER" in text or "WIGNER" in text


def test_given_card_when_read_then_hwigner_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-Q-WIGNER" in text or "WIGNER" in text
    assert "KILL" in text
    assert "hwigner-wigner" in text
    assert "H-ABS-CHRONO" in text or "CHRONO" in text


def test_given_card_when_read_then_hchrono_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-CHRONO" in text or "CHRONO" in text
    assert "KILL" in text
    assert "hchrono-chrono" in text
    assert "H-ABS-MIRROR" in text or "MIRROR" in text


def test_given_card_when_read_then_hmirror_kill() -> None:
    text = CARD.read_text(encoding="utf-8")
    assert "H-ABS-MIRROR" in text or "MIRROR" in text
    assert "KILL" in text
    assert "hmirror-mirror" in text
