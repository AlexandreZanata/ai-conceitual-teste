"""Wave AZ0 SESSION runner (nano:az:session) — freeze AZ packs + reopen."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from antifp_ops import classify_arm, extract_telemetry
from as_session_ops import AS0_ASKABSTAIN_CHARTER
from az_session_ops import (
    AZ0_ANTI_FP,
    AZ0_ASK_BATTERY,
    AZ0_CITED_AY_LOCKS,
    AZ0_GEN_STANCE,
    AZ0_HELDOUT_FP_PROTOCOL,
    AZ0_HELDOUT_FP_ROWS,
    AZ0_ID,
    AZ0_MODES,
    AZ0_NORTH_STAR,
    AZ0_OVERREFUSE_PROTOCOL,
    AZ0_OVERREFUSE_ROWS,
    AZ0_PRODUCT_GEN_CHARTER,
    AZ0_REAL_EVAL_PROTOCOL,
    AZ0_SAFE_NOTE,
    AZ0_SHIP_LOCK,
    AZ0_THESIS,
    AZ0_TRUE_GEN_JUDGE,
    decide_az0_session,
    map_az_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-az/az0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-az/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-az/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-az-session.md"
_LOCAL_SESSION = REPO / ".local/wave-az/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_DECODE_Q = "Explain Merkle trees briefly"
_NEAR_MISS = (
    "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
    "SegWit witness discount?"
)
_HELDOUT_FP = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_AZ_ACTIVE_LINE = (
    "**Wave AZ ACTIVE:** AZ0 [SESSION PROMOTE](wave-az-session.md) "
    "(`npm run nano:az:session`) — held-out intent FP · over-refuse gold · "
    "PRODGEN charter · gen stance **defer** (H-NANOGEN10) · real-eval; "
    "next AZ1 H-PRODGEN; ship remains **AF + AQ + AS trust + STRICT "
    "ablated DECODE**; NANOGEN6·7 HOLD · NANOGEN8·9 DEFER; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # 16c / 31Gi host: leave ≥2 cores free; cap workers to avoid thrash/OOM.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _clear_proxy() -> None:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)


def _write_battery_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AZ0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AZ0",
            "hyp_id": AZ0_ID,
            "pack": "ask-battery",
            "kind": item["kind"],
            "question": item["question"],
            "expect_mode": item["expect_mode"],
            "status": "frozen",
            "mode": None,
            "wall_ms": None,
            "n_new": None,
            "score": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_hfp_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AZ0_HELDOUT_FP_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AZ0",
            "hyp_id": AZ0_ID,
            "pack": "heldout-fp",
            "class": item["class"],
            "question": item["question"],
            "expect_mode": item["expect_mode"],
            "status": "frozen",
            "mode": None,
            "wall_ms": None,
            "false_hit": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_orf_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AZ0_OVERREFUSE_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AZ0",
            "hyp_id": AZ0_ID,
            "pack": "overrefuse",
            "class": item["class"],
            "question": item["question"],
            "expect_mode": item["expect_mode"],
            "gold": item["gold"],
            "status": "frozen",
            "mode": None,
            "wall_ms": None,
            "miss": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("AZ-PRODGEN", "product-gen-charter", dict(AZ0_PRODUCT_GEN_CHARTER)),
        (
            "AZ-HELDOUT-FP",
            "heldout-fp-protocol",
            dict(AZ0_HELDOUT_FP_PROTOCOL),
        ),
        (
            "AZ-OVERREFUSE",
            "overrefuse-protocol",
            dict(AZ0_OVERREFUSE_PROTOCOL),
        ),
        (
            "AZ-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(AZ0_GEN_STANCE),
                "true_gen_judge": dict(AZ0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "AZ-REAL-EVAL",
            "real-eval-protocol",
            dict(AZ0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "AZ0",
            "hyp_id": AZ0_ID,
            "pack": pack,
            "status": "frozen",
            "body": body,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _freeze_trials(trials_dir: Path) -> tuple[list[str], bool]:
    trials_dir.mkdir(parents=True, exist_ok=True)
    written = (
        _write_battery_trials(trials_dir)
        + _write_hfp_trials(trials_dir)
        + _write_orf_trials(trials_dir)
        + _write_charter_trials(trials_dir)
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = (
        len(AZ0_ASK_BATTERY)
        + len(AZ0_HELDOUT_FP_ROWS)
        + len(AZ0_OVERREFUSE_ROWS)
        + 5
    )
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in AZ0_ASK_BATTERY
    )
    hfp_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in AZ0_HELDOUT_FP_ROWS
    )
    orf_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} | `{p['gold']}` |"
        for p in AZ0_OVERREFUSE_ROWS
    )
    bars = AZ0_PRODUCT_GEN_CHARTER["bars"]
    debts = AZ0_PRODUCT_GEN_CHARTER["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    body = "\n".join(
        [
            "# Wave AZ0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-az/SESSION.md`  ",
            "> Module: `nano_lm/src/az_session_ops.py` · "
            "Runner: `npm run nano:az:session`  ",
            "> Parent: [ay-freeze.md](ay-freeze.md) "
            "(Wave AZ reopened explicitly via lab-book reopen after AY-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze AZ packs: "
            "held-out intent FP (N≥12 · div·sub·wrong-slot ≠ AY named) · "
            "over-refuse gold (`a.clear()` LOOKUP) · H-PRODGEN metrics "
            "charter · gen stance **defer** (CAPCHECK closed; "
            "**H-NANOGEN10**; **not** NANOGEN10=NANOGEN9+rename) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until AZ3 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Product-gen charter | 1 | held-out FH0 · no over-refuse · "
            "AY hold · modes · KB · latency · DECODE law (AZ1) |",
            f"| Held-out FP protocol | {len(AZ0_HELDOUT_FP_ROWS)} | "
            "div·sub·wrong-slot ≠ AY named (AZ1) |",
            f"| Over-refuse protocol | {len(AZ0_OVERREFUSE_ROWS)} | "
            "exact clear gold → LOOKUP (AZ1) |",
            "| Gen stance | 1 | **defer** · CAPCHECK closed · "
            "H-NANOGEN10 named · NANOGEN6·7 HOLD · NANOGEN8·9 DEFER "
            "cited (AZ3) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (AZ3) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "anti-FP (AZ4) |",
            f"| Ask battery | {len(AZ0_ASK_BATTERY)} | frozen live rows "
            "(scored at AZ4) |",
            "",
            "## Cited AY locks",
            "",
            ", ".join(sorted(AZ0_CITED_AY_LOCKS)),
            "",
            "## Product-gen bars",
            "",
            f"- heldout_false_hit_max: **{bars['heldout_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- named_intent_false_hit_max: "
            f"**{bars['named_intent_false_hit_max']}**  ",
            f"- hard_natural_para_hit_min: "
            f"**{bars['hard_natural_para_hit_min']}**  ",
            f"- false_hit_max: **{bars['false_hit_max']}**  ",
            f"- heldout_fp_min_n: **{bars['heldout_fp_min_n']}**  ",
            f"- heldout_fp_classes_min: "
            f"**{bars['heldout_fp_classes_min']}**  ",
            f"- overrefuse_min_n: **{bars['overrefuse_min_n']}**  ",
            f"- decode_gibberish_neq_content_ok: "
            f"**{bars['decode_gibberish_neq_content_ok']}**  ",
            f"- default_ask_intent_mismatch: "
            f"**{bars['default_ask_intent_mismatch']}**  ",
            f"- default_ask_exact_gold: "
            f"**{bars['default_ask_exact_gold']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- named_fh_neq_heldout: **{bars['named_fh_neq_heldout']}**  ",
            f"- bank_stuff_forbidden: **{bars['bank_stuff_forbidden']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no vanity reopen PRODINT/SHIPAY unless PRODGEN fails",
            "",
            "## Post-AY debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## Held-out FP protocol",
            "",
            f"- held_out: **{AZ0_HELDOUT_FP_PROTOCOL['held_out']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{AZ0_HELDOUT_FP_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- neq_ay_named_intent: "
            f"**{AZ0_HELDOUT_FP_PROTOCOL['neq_ay_named_intent']}**  ",
            f"- intent_mismatch_is_false_hit: "
            f"**{AZ0_HELDOUT_FP_PROTOCOL['intent_mismatch_is_false_hit']}**  ",
            f"- wrong_slot_is_false_hit: "
            f"**{AZ0_HELDOUT_FP_PROTOCOL['wrong_slot_is_false_hit']}**  ",
            f"- live_fp_id: **{AZ0_HELDOUT_FP_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{AZ0_HELDOUT_FP_PROTOCOL['min_n']}**  ",
            f"- path: `{AZ0_HELDOUT_FP_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            hfp_rows,
            "",
            "## Over-refuse protocol",
            "",
            f"- exact_gold_must_lookup: "
            f"**{AZ0_OVERREFUSE_PROTOCOL['exact_gold_must_lookup']}**  ",
            f"- overrefuse_is_miss: "
            f"**{AZ0_OVERREFUSE_PROTOCOL['overrefuse_is_miss']}**  ",
            f"- live_orf_id: **{AZ0_OVERREFUSE_PROTOCOL['live_orf_id']}**  ",
            f"- min_n: **{AZ0_OVERREFUSE_PROTOCOL['min_n']}**  ",
            "",
            "| id | class | expect_mode | gold |",
            "|----|-------|-------------|------|",
            orf_rows,
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{AZ0_GEN_STANCE['stance']}**  ",
            f"- named_hyp: **{AZ0_GEN_STANCE['named_hyp']}**  ",
            f"- named_prod: **{AZ0_GEN_STANCE['named_prod']}**  ",
            f"- named_ship: **{AZ0_GEN_STANCE['named_ship']}**  ",
            f"- capcheck: **{AZ0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen10_rename_forbidden: "
            f"**{AZ0_GEN_STANCE['nanogen10_rename_forbidden']}**  ",
            f"- az3_gate: `{AZ0_GEN_STANCE['az3_gate']}`  ",
            "",
            AZ0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{AZ0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen10_rename_forbidden: "
            f"{AZ0_TRUE_GEN_JUDGE['nanogen10_rename_forbidden']}  ",
            f"- scoring: `{AZ0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{AZ0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{AZ0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{AZ0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- intent_mismatch_is_false_hit: "
            f"{AZ0_REAL_EVAL_PROTOCOL['intent_mismatch_is_false_hit']}  ",
            f"- exact_gold_abstain_is_miss: "
            f"{AZ0_REAL_EVAL_PROTOCOL['exact_gold_abstain_is_miss']}  ",
            f"- named_fh_neq_heldout: "
            f"{AZ0_REAL_EVAL_PROTOCOL['named_fh_neq_heldout']}  ",
            f"- gen_claim_rule: "
            f"{AZ0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {AZ0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            AZ0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AZ0_ANTI_FP,
            "",
            "## North star",
            "",
            AZ0_NORTH_STAR,
            "",
            "## Ship lock (until AZ gen PROMOTE)",
            "",
            AZ0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:az:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "held-out FP + over-refuse probes are **recorded** "
            "(AZ1 scores FH=0 / miss=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-az/az0_session.json` · "
            "`results/nano-lm/wave-az/trials/AZ-*.json`.  ",
            "Contract: `nano_lm/tests/test_az_session.py`.",
            "",
            "## Claims",
            "",
            "- AY packs frozen for Wave AZ — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{AZ0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **AZ3 H-NANOGEN10** "
            "true_continue under a real new method "
            "(never NANOGEN9+rename; span-fallback ≠ gen).  ",
            "- Forbidden: LOOKUP-as-IQ · held-out FP as hit · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "named FH as held-out coverage · gold-substring PROMOTE · "
            "span-fallback as gen · DECODE telemetry-only content_ok · "
            "eval↔prod gap · mini-AGI claim early · NANOGEN10 rename · "
            "CTX/SMART/FAST/APP clone · bank stuffing · vanity reopen.",
            "",
            "Next: **AZ1 H-PRODGEN** — close held-out FH + over-refuse "
            "on Caminho A; publish human-para · FH · p50/p99 · KB · modes.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _ask_lookup() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_KNOWN,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
    )


def _ask_decode() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_DECODE_Q,
        root=_CHAMPION,
        seed=0,
        wrap=False,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=False,
    )


def _ask_near_miss() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_NEAR_MISS,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
        semwrap=True,
    )


def _ask_heldout_fp() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_HELDOUT_FP,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
        semwrap=True,
    )


def _ask_overrefuse() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_OVERREFUSE,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
        semwrap=True,
    )


def _decode_arm_ok(g_arm: str, g_mode: str, raw_g: str) -> bool:
    if g_mode == "DECODE":
        return True
    return g_arm == "GENERATE" and raw_g not in {"NO_ANSWER", "ABSTAIN"}


def _smoke_ok(
    *,
    lookup: dict[str, Any],
    l_arm: str,
    g_arm: str,
    l_mode: str,
    g_mode: str,
    nm_mode: str,
    hfp_mode: str,
    orf_mode: str,
    l_tel: dict[str, Any],
    g_tel: dict[str, Any],
) -> bool:
    checks = (
        l_arm == "LOOKUP",
        l_mode == "LOOKUP",
        l_tel["mode"] == "WRAP_LOOKUP",
        "def add" in str(lookup.get("completion", "")),
        _decode_arm_ok(g_arm, g_mode, str(g_tel["mode"] or "")),
        float(g_tel["wall_ms"] or 0) > 0.0,
        int(g_tel["n_new"] or 0) > 0,
        map_az_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in AZ0_MODES,
        hfp_mode in AZ0_MODES,
        orf_mode in AZ0_MODES,
    )
    return all(checks)


def _smoke_penta_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP + DECODE + near-miss + held-out FP + over-refuse (anti-FP)."""
    n = min(5, max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        fut_l = pool.submit(_ask_lookup)
        fut_d = pool.submit(_ask_decode)
        fut_n = pool.submit(_ask_near_miss)
        fut_h = pool.submit(_ask_heldout_fp)
        fut_o = pool.submit(_ask_overrefuse)
        lookup = fut_l.result()
        gen = fut_d.result()
        near = fut_n.result()
        heldout = fut_h.result()
        overref = fut_o.result()
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    n_tel = extract_telemetry(near)
    h_tel = extract_telemetry(heldout)
    o_tel = extract_telemetry(overref)
    l_mode = map_az_product_mode(str(l_tel["mode"]))
    g_mode = map_az_product_mode(str(g_tel["mode"]))
    nm_mode = map_az_product_mode(str(n_tel["mode"]))
    hfp_mode = map_az_product_mode(str(h_tel["mode"]))
    orf_mode = map_az_product_mode(str(o_tel["mode"]))
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
        nm_mode=nm_mode,
        hfp_mode=hfp_mode,
        orf_mode=orf_mode,
        l_tel=l_tel,
        g_tel=g_tel,
    )
    return {
        "ok": ok,
        "lookup": {
            "arm": l_arm,
            "raw_mode": l_tel["mode"],
            "product_mode": l_mode,
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
        },
        "decode": {
            "arm": g_arm,
            "raw_mode": g_tel["mode"],
            "product_mode": g_mode,
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
            "note": "AZ1 must fail gibberish content_ok; AZ0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AY/AX locked ABSTAIN; AZ0 verifies mapping",
        },
        "heldout_fp": {
            "arm": classify_arm(heldout),
            "raw_mode": h_tel["mode"],
            "product_mode": hfp_mode,
            "wall_ms": h_tel["wall_ms"],
            "n_new": h_tel["n_new"],
            "completion": str(heldout.get("completion", ""))[:120],
            "question": _HELDOUT_FP,
            "note": "held-out div FP; AZ1 scores FH=0 — AZ0 records only",
        },
        "overrefuse": {
            "arm": classify_arm(overref),
            "raw_mode": o_tel["mode"],
            "product_mode": orf_mode,
            "wall_ms": o_tel["wall_ms"],
            "n_new": o_tel["n_new"],
            "completion": str(overref.get("completion", ""))[:120],
            "question": _OVERREFUSE,
            "note": "exact clear gold; AZ1 scores miss=0 — AZ0 records only",
        },
        "modes_charter": sorted(AZ0_MODES),
        "abstain_alias": map_az_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": AZ0_GEN_STANCE["stance"],
        "named_hyp": AZ0_GEN_STANCE["named_hyp"],
        "named_prod": AZ0_GEN_STANCE["named_prod"],
        "named_ship": AZ0_GEN_STANCE["named_ship"],
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_penta_arm(workers=workers)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "penta-arm smoke failed", "ask": ask}
            )
        )
        return 2, ask
    return 0, ask


def _parallel_prep(workers: int, trials_dir: Path) -> tuple[list[str], bool]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fut = pool.submit(_freeze_trials, trials_dir)
        return fut.result()


def _update_local_session(decision: str) -> None:
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    status = "DONE — PROMOTE" if decision.startswith("PROMOTE") else "KILL"
    body = "\n".join(
        [
            f"# Wave AZ session checklist (**OPEN** · AZ0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AZ **OPEN** · Caminho A held-out harden + Nano Generative "
            "defer).  ",
            f"> Parent: AY COMPLETE + FROZEN · Ship: **{AZ0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after AY-FREEZE; held-out FP + over-refuse open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8·9 DEFER).",
            "",
            "## Current stage",
            "",
            f"**AZ0 — SESSION ({status})** · Next: **AZ1 H-PRODGEN**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AZ OPEN** |",
            "| Track | Caminho A held-out FH0 · no over-refuse · "
            "gen stance **defer** (H-NANOGEN10) |",
            "| Parent | AY COMPLETE + FROZEN |",
            "| Open hole | held-out div·sub·wrong-slot · a.clear() "
            "LOOKUP · FH0 · modes · p50/p99 · KB · DECODE law |",
            "| Forbidden | NANOGEN10 rename · LOOKUP-as-IQ · "
            "held-out FP as hit · over-refuse as win · CTX/SMART/FAST |",
            "",
            "## North star (signed)",
            "",
            AZ0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AZ0)",
            "",
            "```text",
            "MODEL = AZ0-SESSION",
            "",
            "[x] Freeze held-out intent protocol (N≥12 · div·sub·wrong-slot)",
            "[x] Freeze over-refuse gold protocol (a.clear() → LOOKUP)",
            "[x] Freeze H-PRODGEN metrics charter (held-out FH · para · "
            "latency · KB)",
            "[x] Freeze gen stance = defer (CAPCHECK closed; H-NANOGEN10 named)",
            "[x] Name AZ1 H-PRODGEN · AZ2 H-SHIPAZ · AZ3 H-NANOGEN10",
            "[x] Freeze true gen judge (rename forbidden)",
            "[x] Real-eval ask battery protocol (eval=prod ask)",
            "[x] Do NOT reopen PRODINT/SHIPAY unless PRODGEN fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN10 = NANOGEN9+rename",
            "[ ] Next: AZ1 H-PRODGEN",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AZ0 | SESSION | **{status}** |",
            "| AZ1 | H-PRODGEN | **NEXT** |",
            "| AZ2 | H-SHIPAZ | pending |",
            "| AZ3 | H-NANOGEN10 | pending (defer unless real new method) |",
            "| AZ4 | AZ-REAL-EVAL | pending |",
            "| AZ5 | AZ-REPORT | pending |",
            "| AZ6 | AZ-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Held-out intent FH (ask path) | **0** | live FP debt "
            "(div·sub·wrong-slot) |",
            "| Over-refuse miss (exact clear) | **0** | a.clear() ABSTAIN |",
            "| Named intent FH (AY hold) | **0** | AY PRODINT 0/12 |",
            "| Hard natural para hit | ≥ 0.70 hold | AX PRODNAT 1.0/18 |",
            "| Adversary FH (near-miss) | **0** | AY/AX / AS ADVSAFE |",
            "| DECODE content | usable or ABSTAIN | STRICT lock |",
            "| Latency p50/p99 | publish | AY PRODINT / AS METRICS |",
            "| True continue (NANOGEN10) | PROMOTE else HOLD/DEFER | "
            "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER; stance defer |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    done_row = (
        "| AZ0 | **SESSION** | Freeze packs: held-out intent · "
        "over-refuse golds · metrics · gen stance · real-eval | "
        "cite AY; stance=defer; H-PRODGEN·H-SHIPAZ·H-NANOGEN10 named | "
        "**DONE — PROMOTE** |"
    )
    az0_todo = (
        "| AZ0 | **SESSION** | Freeze packs: held-out intent · "
        "over-refuse golds · metrics · gen stance · real-eval | "
        "cite AY; name stance | **TODO** |"
    )
    if az0_todo in text:
        text = text.replace(az0_todo, done_row, 1)
    text = text.replace(
        "> **Session:** `.local/wave-az/SESSION.md` "
        "(create at AZ0 — still **TODO**).  ",
        "> **Session:** `.local/wave-az/SESSION.md` "
        "(AZ0 **DONE — PROMOTE**; next AZ1 H-PRODGEN).  ",
        1,
    )
    for old_next in (
        (
            "1. **AZ0 SESSION** — `.local/wave-az/SESSION.md`; freeze "
            "held-out pack (`div` · `sub` · wrong-slot BIP) + over-refuse "
            "gold (`a.clear()`); metric board; gen stance "
            "(`new_method` | `capcheck_hybrid` | `defer`).  "
        ),
        (
            "1. **AZ0 SESSION** — `.local/wave-az/SESSION.md`; freeze "
            "held-out pack (`div` · `sub` · wrong-slot BIP) + over-refuse "
            "gold (`a.clear()`); metric board; gen stance "
            "(`new_method` \\| `capcheck_hybrid` \\| `defer`).  "
        ),
    ):
        if old_next in text:
            text = text.replace(
                old_next,
                "1. **AZ0 SESSION** — **DONE PROMOTE** "
                "(`npm run nano:az:session`) · gen stance **defer** · "
                "H-PRODGEN·H-SHIPAZ·H-NANOGEN10 named · held-out + "
                "over-refuse packs frozen.  ",
                1,
            )
            break
    text = text.replace(
        "2. **AZ1** — Caminho A: generalize SEMWRAP intent · FH 0 held-out · "
        "exact gold LOOKUP · report the **four metrics** + modes.  ",
        "2. **AZ1 H-PRODGEN** — **NEXT** — Caminho A: generalize SEMWRAP "
        "intent · FH 0 held-out · exact gold LOOKUP · report the "
        "**four metrics** + modes.  ",
        1,
    )
    az1_todo = (
        "| AZ1 | **H-PRODGEN** (name at AZ0) | Caminho A: held-out FH 0 · "
        "no over-refuse · hold AY/AX bars · p50/p99 · KB · modes | "
        "metrics board | **TODO** |"
    )
    az1_next = (
        "| AZ1 | **H-PRODGEN** | Caminho A: held-out FH 0 · "
        "no over-refuse · hold AY/AX bars · p50/p99 · KB · modes | "
        "metrics board | **NEXT** |"
    )
    if az1_todo in text:
        text = text.replace(az1_todo, az1_next, 1)
    az2_todo = (
        "| AZ2 | **H-SHIPAZ** (name at AZ0) | Ship/demo always "
        "`mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN) | smoke + content | **TODO** |"
    )
    az2_named = (
        "| AZ2 | **H-SHIPAZ** | Ship/demo always "
        "`mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN) | smoke + content | **TODO** |"
    )
    if az2_todo in text:
        text = text.replace(az2_todo, az2_named, 1)
    # Repair accidental backslash-escaped pipes from older patch paths.
    text = text.replace(
        "`mode=LOOKUP\\|PEAK\\|DECODE`",
        "`mode=LOOKUP|PEAK|DECODE`",
    )
    az3_todo = (
        "| AZ3 | **H-NANOGEN*** (name at AZ0) | North-star gen — real "
        "method / hybrid; else HOLD/DEFER | true_continue | **TODO** |"
    )
    az3_named = (
        "| AZ3 | **H-NANOGEN10** | North-star gen — real method / hybrid; "
        "else HOLD/DEFER (stance **defer** at AZ0) | "
        "true_continue → PROMOTE else HOLD/DEFER | **TODO** |"
    )
    if az3_todo in text:
        text = text.replace(az3_todo, az3_named, 1)
    bash_old = (
        "# after AZ0:\n"
        "# npm run nano:az:session\n"
        "# npm run nano:<prod-gen>\n"
        "# npm run nano:<ship-az>\n"
        "# npm run nano:<nanogen-next>\n"
        "# npm run nano:az:real-eval\n"
        "# npm run nano:az:report\n"
        "# npm run nano:az:freeze"
    )
    bash_new = (
        "npm run nano:az:session\n"
        "# next: nano:prodgen · nano:shipaz · nano:nanogen10\n"
        "# npm run nano:az:real-eval\n"
        "# npm run nano:az:report\n"
        "# npm run nano:az:freeze"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _write_local_impl(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave AY **COMPLETE + FROZEN** (NANOGEN9 **DEFER**).  
**Reopen:** Wave **AZ ACTIVE** via `pesquisa.md` — dual track only.  
**AZ0 SESSION:** **DONE — PROMOTE** (`npm run nano:az:session`) · gen stance **defer** · H-PRODGEN · H-SHIPAZ · H-NANOGEN10 named.

## Dual track (locked)

| Track | Work |
|-------|------|
| **Caminho A** | Accept artifact · **held-out FH 0** · no over-refuse · hold AY/AX · FH · p50/p99 · KB · mode UI |
| **North star** | Nano generative / mini-AGI-*inspired* ≤5M · **defer** until real new method (NANOGEN6·7 HOLD · NANOGEN8·9 DEFER) |

## Next

1. **AZ0 SESSION** — **DONE PROMOTE** (`npm run nano:az:session`).  
2. **AZ1 H-PRODGEN** — **NEXT** — close held-out FH + over-refuse; publish metrics board.  
3. Ship claim stays AY lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · held-out FP as hit · over-refuse as win · NANOGEN10=NANOGEN9+rename · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones.

```bash
npm run nano:az:session
npm run nano:test && npm run verify
```
"""
    _LOCAL_IMPL.write_text(body, encoding="utf-8")


def _write_local_readme(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Local research notebook

Full lab book: **`pesquisa.md`**.

## Current wave

**Wave AZ ACTIVE** (lab-book reopen after AY-FREEZE):

1. **Caminho A:** accept artifact — known-ask + robust SEMWRAP + labeled PEAK/RAG + apps; **held-out FH 0** · no over-refuse · hold AY/AX · p50/p99 · KB; mode UI always.  
2. **North star:** nano generative / mini-AGI-*inspired* ≤5M — gen stance **defer** (H-NANOGEN10; NANOGEN6·7 HOLD · NANOGEN8·9 DEFER until beaten; no NANOGEN10 clone).

Session: `wave-az/SESSION.md` (AZ0 **DONE — PROMOTE**; next AZ1 H-PRODGEN). Parent: Wave AY **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–AY | COMPLETE + FROZEN |
| Ship (until AZ gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§8 · Wave AZ0–AZ6 |

## Do not

LOOKUP-as-IQ · held-out FP as hit · over-refuse as win · sell HOLD/DEFER as unlock · named FH as held-out coverage · NANOGEN10=NANOGEN9+rename · CTX/SMART/FAST letter clones.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave AZ ACTIVE" in text:
        return
    marker = "**Wave AY COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    ay_line = text[idx:end]
    if "do not invent Wave AZ" in ay_line:
        ay_line = ay_line.replace(
            "do not invent Wave AZ",
            "Wave AZ reopened via lab-book",
        )
        text = text[:idx] + ay_line + text[end:]
        end = idx + len(ay_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_az() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave AZ ACTIVE" in text:
        return
    agents_line = (
        "- **Wave AZ ACTIVE** — AZ0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-az-session.md) "
        "(`npm run nano:az:session`) — held-out intent FP · over-refuse · "
        "PRODGEN · gen stance **defer** (H-NANOGEN10); next AZ1 H-PRODGEN; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave AZ.",
        "Wave AZ reopened via lab-book.",
        1,
    )
    text2, n = re.subn(
        r"- \*\*Wave AY COMPLETE \+ FROZEN\*\* —[^\n]+",
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_az() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **AZ** |" in text:
        return
    row = (
        "| **AZ** | **ACTIVE** | AZ0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-az-session.md) (`npm run nano:az:session`) "
        "— held-out FP · over-refuse · gen stance defer (H-NANOGEN10); "
        "next AZ1 H-PRODGEN; ship AF+AQ+AS trust + STRICT ablated DECODE; "
        "NANOGEN6·7 HOLD · NANOGEN8·9 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave AZ |",
        "Wave AZ reopened via lab-book |",
        1,
    )
    text2, n = re.subn(
        r"\| \*\*AY\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_az() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave AZ ACTIVE" in text:
        return
    dual = (
        "do not invent Wave AZ); do not invent Wave AZ",
        "Wave AZ ACTIVE (AZ0 SESSION PROMOTE; next AZ1 H-PRODGEN)); "
        "do not invent Wave BA",
    )
    single = (
        "do not invent Wave AZ",
        "Wave AZ ACTIVE (AZ0 SESSION PROMOTE; next AZ1 H-PRODGEN); "
        "do not invent Wave BA",
    )
    if dual[0] in text:
        text = text.replace(dual[0], dual[1], 1)
    elif single[0] in text:
        text = text.replace(single[0], single[1], 1)
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_az0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave AZ0 SESSION" in text:
        return
    insert = (
        "| Wave AZ0 SESSION | [wave-az-session.md](wave-az-session.md) "
        "**PROMOTE** (`npm run nano:az:session`) — held-out FP N≥12 · "
        "div·sub·wrong-slot · over-refuse a.clear() · PRODGEN charter · "
        "gen stance **defer** (H-NANOGEN10) · true-eval |"
    )
    marker = (
        "| Wave AY6 AY-FREEZE | [ay-freeze.md](ay-freeze.md) · "
        "[formal-hayfreeze-ay-freeze.md](formal-hayfreeze-ay-freeze.md) "
        "**PROMOTE** (`npm run nano:ay:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN9 DEFER; do not invent Wave AZ |"
    )
    if marker not in text:
        return
    text = text.replace(
        marker,
        marker.replace("do not invent Wave AZ", "Wave AZ reopened via lab-book")
        + "\n"
        + insert,
        1,
    )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _AZ_ACTIVE_LINE.replace(
        "**Wave AZ ACTIVE:**", "**Wave AZ ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _AZ_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_az()
    _patch_agenda_az()
    _patch_evogen_az()
    _patch_recipes_az0()


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_az0_session(
        trials_dir_ready=trials_ready, anti_fp_signed=True
    )
    _write_public_note(decision=decision)
    _update_local_session(decision)
    _patch_pesquisa(decision)
    _write_local_impl(decision)
    _write_local_readme(decision)
    _patch_public_status(decision)
    rc, ask = _run_ask_smoke(
        decision, skip=bool(args.skip_ask), workers=workers
    )
    if rc != 0:
        return rc

    payload = {
        "id": AZ0_ID,
        "thesis": AZ0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_ay_locks": sorted(AZ0_CITED_AY_LOCKS),
        "product_gen_charter": dict(AZ0_PRODUCT_GEN_CHARTER),
        "heldout_fp_protocol": dict(AZ0_HELDOUT_FP_PROTOCOL),
        "overrefuse_protocol": dict(AZ0_OVERREFUSE_PROTOCOL),
        "gen_stance": dict(AZ0_GEN_STANCE),
        "true_gen_judge": dict(AZ0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(AZ0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(AZ0_ASK_BATTERY),
        "heldout_fp_n": len(AZ0_HELDOUT_FP_ROWS),
        "overrefuse_n": len(AZ0_OVERREFUSE_ROWS),
        "safe_note": AZ0_SAFE_NOTE,
        "anti_fp": AZ0_ANTI_FP,
        "north_star": AZ0_NORTH_STAR,
        "ship_lock": AZ0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-az-session.md",
        "rule": "pesquisa §5 AZ0 · held-out + over-refuse + gen-defer + anti-FP",
        "next": "AZ1 H-PRODGEN (close held-out FH + over-refuse debt)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AZ0_ID,
                "decision": decision[:120],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
