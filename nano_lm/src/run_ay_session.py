"""Wave AY0 SESSION runner (nano:ay:session) — freeze AY packs + reopen."""

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
from ay_session_ops import (
    AY0_ANTI_FP,
    AY0_ASK_BATTERY,
    AY0_CITED_AX_LOCKS,
    AY0_GEN_STANCE,
    AY0_ID,
    AY0_INTENT_FP_PROTOCOL,
    AY0_INTENT_FP_ROWS,
    AY0_MODES,
    AY0_NORTH_STAR,
    AY0_PRODUCT_INT_CHARTER,
    AY0_REAL_EVAL_PROTOCOL,
    AY0_SAFE_NOTE,
    AY0_SHIP_LOCK,
    AY0_THESIS,
    AY0_TRUE_GEN_JUDGE,
    decide_ay0_session,
    map_ay_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ay/ay0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-ay/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-ay/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ay-session.md"
_LOCAL_SESSION = REPO / ".local/wave-ay/SESSION.md"
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
_INTENT_FP = str(AY0_INTENT_FP_ROWS[0]["question"])

_AY_ACTIVE_LINE = (
    "**Wave AY ACTIVE:** AY0 [SESSION PROMOTE](wave-ay-session.md) "
    "(`npm run nano:ay:session`) — intent-adversary FP · PRODINT charter · "
    "gen stance **defer** (H-NANOGEN9) · real-eval; next AY1 H-PRODINT; "
    "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
    "NANOGEN6·7 HOLD · NANOGEN8 DEFER; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # 16c host: leave ≥2 cores free; cap workers to avoid thrash/OOM.
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
    for item in AY0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AY0",
            "hyp_id": AY0_ID,
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


def _write_ifp_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AY0_INTENT_FP_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AY0",
            "hyp_id": AY0_ID,
            "pack": "intent-fp",
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


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("AY-PRODINT", "product-int-charter", dict(AY0_PRODUCT_INT_CHARTER)),
        (
            "AY-INTENT-FP",
            "intent-fp-protocol",
            dict(AY0_INTENT_FP_PROTOCOL),
        ),
        (
            "AY-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(AY0_GEN_STANCE),
                "true_gen_judge": dict(AY0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "AY-REAL-EVAL",
            "real-eval-protocol",
            dict(AY0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "AY0",
            "hyp_id": AY0_ID,
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
        + _write_ifp_trials(trials_dir)
        + _write_charter_trials(trials_dir)
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = len(AY0_ASK_BATTERY) + len(AY0_INTENT_FP_ROWS) + 4
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in AY0_ASK_BATTERY
    )
    ifp_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in AY0_INTENT_FP_ROWS
    )
    bars = AY0_PRODUCT_INT_CHARTER["bars"]
    debts = AY0_PRODUCT_INT_CHARTER["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    body = "\n".join(
        [
            "# Wave AY0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-ay/SESSION.md`  ",
            "> Module: `nano_lm/src/ay_session_ops.py` · "
            "Runner: `npm run nano:ay:session`  ",
            "> Parent: [ax-freeze.md](ax-freeze.md) "
            "(Wave AY reopened explicitly via lab-book reopen after AX-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze AY packs: "
            "intent-adversary FP protocol (N≥12 · 4 classes ≠ AX hard-natural) · "
            "H-PRODINT metrics charter · gen stance **defer** "
            "(CAPCHECK closed; **H-NANOGEN9**; **not** NANOGEN9=NANOGEN8+rename) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until AY3 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Product-int charter | 1 | intent FH0 · hard-natural hold · "
            "modes · KB · latency · DECODE law (AY1) |",
            f"| Intent-FP protocol | {len(AY0_INTENT_FP_ROWS)} | "
            "held-out live FP class ≠ AX hard-natural (AY1) |",
            "| Gen stance | 1 | **defer** · CAPCHECK closed · "
            "H-NANOGEN9 named · NANOGEN6·7 HOLD · NANOGEN8 DEFER cited (AY3) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (AY3) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "anti-FP (AY4) |",
            f"| Ask battery | {len(AY0_ASK_BATTERY)} | frozen live rows "
            "(scored at AY4) |",
            "",
            "## Cited AX locks",
            "",
            ", ".join(sorted(AY0_CITED_AX_LOCKS)),
            "",
            "## Product-int bars",
            "",
            f"- intent_false_hit_max: **{bars['intent_false_hit_max']}**  ",
            f"- hard_natural_para_hit_min: "
            f"**{bars['hard_natural_para_hit_min']}**  ",
            f"- false_hit_max: **{bars['false_hit_max']}**  ",
            f"- intent_fp_min_n: **{bars['intent_fp_min_n']}**  ",
            f"- intent_fp_classes_min: **{bars['intent_fp_classes_min']}**  ",
            f"- decode_gibberish_neq_content_ok: "
            f"**{bars['decode_gibberish_neq_content_ok']}**  ",
            f"- default_ask_intent_mismatch: "
            f"**{bars['default_ask_intent_mismatch']}**  ",
            f"- default_ask_near_miss: **{bars['default_ask_near_miss']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- pack_fh_neq_live_intent: "
            f"**{bars['pack_fh_neq_live_intent']}**  ",
            f"- bank_stuff_forbidden: **{bars['bank_stuff_forbidden']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no vanity re-SEMFIX / reopen PRODNAT unless PRODINT fails",
            "",
            "## Post-AX debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## Intent-FP protocol",
            "",
            f"- held_out: **{AY0_INTENT_FP_PROTOCOL['held_out']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{AY0_INTENT_FP_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- neq_ax_hard_natural: "
            f"**{AY0_INTENT_FP_PROTOCOL['neq_ax_hard_natural']}**  ",
            f"- intent_mismatch_is_false_hit: "
            f"**{AY0_INTENT_FP_PROTOCOL['intent_mismatch_is_false_hit']}**  ",
            f"- live_fp_id: **{AY0_INTENT_FP_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{AY0_INTENT_FP_PROTOCOL['min_n']}**  ",
            f"- path: `{AY0_INTENT_FP_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            ifp_rows,
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{AY0_GEN_STANCE['stance']}**  ",
            f"- named_hyp: **{AY0_GEN_STANCE['named_hyp']}**  ",
            f"- capcheck: **{AY0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen9_rename_forbidden: "
            f"**{AY0_GEN_STANCE['nanogen9_rename_forbidden']}**  ",
            f"- ay3_gate: `{AY0_GEN_STANCE['ay3_gate']}`  ",
            "",
            AY0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{AY0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen9_rename_forbidden: "
            f"{AY0_TRUE_GEN_JUDGE['nanogen9_rename_forbidden']}  ",
            f"- scoring: `{AY0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{AY0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{AY0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{AY0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- intent_mismatch_is_false_hit: "
            f"{AY0_REAL_EVAL_PROTOCOL['intent_mismatch_is_false_hit']}  ",
            f"- pack_fh_neq_live_intent: "
            f"{AY0_REAL_EVAL_PROTOCOL['pack_fh_neq_live_intent']}  ",
            f"- gen_claim_rule: "
            f"{AY0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {AY0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            AY0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AY0_ANTI_FP,
            "",
            "## North star",
            "",
            AY0_NORTH_STAR,
            "",
            "## Ship lock (until AY gen PROMOTE)",
            "",
            AY0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:ay:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Quad-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "intent-FP live probe is **recorded** (AY1 scores FH=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-ay/ay0_session.json` · "
            "`results/nano-lm/wave-ay/trials/AY-*.json`.  ",
            "Contract: `nano_lm/tests/test_ay_session.py`.",
            "",
            "## Claims",
            "",
            "- AX packs frozen for Wave AY — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{AY0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **AY3 H-NANOGEN9** "
            "true_continue under a real new method "
            "(never NANOGEN8+rename; span-fallback ≠ gen).  ",
            "- Forbidden: LOOKUP-as-IQ · intent-FP as hit · peak-as-open-chat · "
            "SAFE-as-quality · pack FH as live intent coverage · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN9 rename · CTX/SMART/FAST/APP "
            "clone · bank stuffing · vanity re-SEMFIX.",
            "",
            "Next: **AY1 H-PRODINT** — close intent FP on Caminho A; "
            "publish human-para · FH · p50/p99 · KB · modes.",
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


def _ask_intent_fp() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_INTENT_FP,
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
    ifp_mode: str,
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
        map_ay_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in AY0_MODES,
        ifp_mode in AY0_MODES,
    )
    return all(checks)


def _smoke_quad_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP + DECODE + near-miss + intent-FP live probe (anti-FP)."""
    n = min(4, max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        fut_l = pool.submit(_ask_lookup)
        fut_d = pool.submit(_ask_decode)
        fut_n = pool.submit(_ask_near_miss)
        fut_i = pool.submit(_ask_intent_fp)
        lookup = fut_l.result()
        gen = fut_d.result()
        near = fut_n.result()
        intent = fut_i.result()
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    n_tel = extract_telemetry(near)
    i_tel = extract_telemetry(intent)
    l_mode = map_ay_product_mode(str(l_tel["mode"]))
    g_mode = map_ay_product_mode(str(g_tel["mode"]))
    nm_mode = map_ay_product_mode(str(n_tel["mode"]))
    ifp_mode = map_ay_product_mode(str(i_tel["mode"]))
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
        nm_mode=nm_mode,
        ifp_mode=ifp_mode,
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
            "note": "AY1 must fail gibberish content_ok; AY0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AX PRODNAT locked ABSTAIN; AY0 verifies mapping",
        },
        "intent_fp": {
            "arm": classify_arm(intent),
            "raw_mode": i_tel["mode"],
            "product_mode": ifp_mode,
            "wall_ms": i_tel["wall_ms"],
            "n_new": i_tel["n_new"],
            "completion": str(intent.get("completion", ""))[:120],
            "question": _INTENT_FP,
            "note": "live intent FP class; AY1 scores FH=0 — AY0 records only",
        },
        "modes_charter": sorted(AY0_MODES),
        "abstain_alias": map_ay_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": AY0_GEN_STANCE["stance"],
        "named_hyp": AY0_GEN_STANCE["named_hyp"],
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_quad_arm(workers=workers)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "quad-arm smoke failed", "ask": ask}
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
            f"# Wave AY session checklist (**OPEN** · AY0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AY **OPEN** · Caminho A intent harden + Nano Generative "
            "defer).  ",
            f"> Parent: AX COMPLETE + FROZEN · Ship: **{AY0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after AX-FREEZE; intent FP open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8 DEFER).",
            "",
            "## Current stage",
            "",
            f"**AY0 — SESSION ({status})** · Next: **AY1 H-PRODINT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AY OPEN** |",
            "| Track | Caminho A intent FH0 · gen stance **defer** "
            "(H-NANOGEN9) |",
            "| Parent | AX COMPLETE + FROZEN |",
            "| Open hole | intent FP · hold hard-natural · FH0 · modes · "
            "p50/p99 · KB · DECODE law |",
            "| Forbidden | NANOGEN9 rename · LOOKUP-as-IQ · "
            "intent-FP as hit · CTX/SMART/FAST |",
            "",
            "## North star (signed)",
            "",
            AY0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AY0)",
            "",
            "```text",
            "MODEL = AY0-SESSION",
            "",
            "[x] Freeze intent-adversary held-out protocol (N≥12 · 4 classes)",
            "[x] Freeze H-PRODINT metrics charter (intent FH · para · latency · KB)",
            "[x] Freeze gen stance = defer (CAPCHECK closed; H-NANOGEN9 named)",
            "[x] Freeze true gen judge (rename forbidden)",
            "[x] Real-eval ask battery protocol (eval=prod ask)",
            "[x] Do NOT reopen PRODNAT/SHIPUX unless PRODINT fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN9 = NANOGEN8+rename",
            "[ ] Next: AY1 H-PRODINT",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AY0 | SESSION | **{status}** |",
            "| AY1 | H-PRODINT | **NEXT** |",
            "| AY2 | H-SHIPAY | pending |",
            "| AY3 | H-NANOGEN9 | pending (defer unless real new method) |",
            "| AY4 | AY-REAL-EVAL | pending |",
            "| AY5 | AY-REPORT | pending |",
            "| AY6 | AY-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Intent / adversary FH (ask path) | **0** | live FP debt |",
            "| Hard natural para hit | ≥ 0.70 hold | AX PRODNAT 1.0/18 |",
            "| Adversary FH (near-miss) | **0** | AX PRODNAT / AS ADVSAFE |",
            "| DECODE content | usable or ABSTAIN | AX STRICT lock |",
            "| Latency p50/p99 | publish | AX PRODNAT / AS METRICS |",
            "| True continue (NANOGEN9) | PROMOTE else HOLD/DEFER | "
            "NANOGEN6·7 HOLD · NANOGEN8 DEFER; stance defer |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    done_row = (
        "| AY0 | **SESSION** | Freeze AY packs: intent-adversary FP · "
        "product metrics · gen stance (**defer**) · real-eval | "
        "cite AX locks; stance=defer; H-NANOGEN9 named | **DONE — PROMOTE** |"
    )
    ay0_todo = (
        "| AY0 | **SESSION** | Freeze AY packs: intent-adversary FP · "
        "product metrics · gen method stance · real-eval | "
        "cite AX locks; name gen stance | **TODO** |"
    )
    if ay0_todo in text:
        text = text.replace(ay0_todo, done_row, 1)
    text = text.replace(
        "> **Session:** `.local/wave-ay/SESSION.md` (create at AY0).  ",
        "> **Session:** `.local/wave-ay/SESSION.md` "
        "(AY0 **DONE — PROMOTE**; next AY1 H-PRODINT).  ",
        1,
    )
    for old_next in (
        (
            "1. **AY0 SESSION** — open `.local/wave-ay/SESSION.md`; "
            "freeze intent-adversary pack (mul · difference-add · "
            "remove≠clear · half-known BIP); freeze product metric board; "
            "name gen stance (`new_method` | `capcheck_hybrid` | `defer`); "
            "cite AX locks.  "
        ),
        (
            "1. **AY0 SESSION** — open `.local/wave-ay/SESSION.md`; "
            "freeze intent-adversary pack (mul · difference-add · "
            "remove≠clear · half-known BIP); freeze product metric board; "
            "name gen stance (`new_method` \\| `capcheck_hybrid` \\| `defer`); "
            "cite AX locks.  "
        ),
    ):
        if old_next in text:
            text = text.replace(
                old_next,
                "1. **AY0 SESSION** — **DONE PROMOTE** "
                "(`npm run nano:ay:session`) · gen stance **defer** · "
                "H-NANOGEN9 named · intent-FP pack frozen.  ",
                1,
            )
            break
    text = text.replace(
        "2. **AY1 product** — close intent FP on Caminho A "
        "(SEMWRAP robustness ≠ bank stuffing); report human-para · FH · "
        "p50/p99 · KB · modes.  ",
        "2. **AY1 H-PRODINT** — **NEXT** — close intent FP on Caminho A "
        "(SEMWRAP robustness ≠ bank stuffing); report human-para · FH · "
        "p50/p99 · KB · modes.  ",
        1,
    )
    # Stage machine status for AY1 name
    ay1_todo = (
        "| AY1 | **H-PRODINT** (name at AY0) | Caminho A: intent/adversary "
        "FH 0 · hold hard-natural · p50/p99 · KB · modes · DECODE law | "
        "FH 0 on live FP class · metrics board | **TODO** |"
    )
    ay1_next = (
        "| AY1 | **H-PRODINT** | Caminho A: intent/adversary "
        "FH 0 · hold hard-natural · p50/p99 · KB · modes · DECODE law | "
        "FH 0 on live FP class · metrics board | **NEXT** |"
    )
    if ay1_todo in text:
        text = text.replace(ay1_todo, ay1_next, 1)
    ay2_todo = (
        "| AY2 | **H-SHIPAY** (name at AY0) | Ship/demo UI always "
        "`mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN); content matches mode | "
        "smoke + content · no unlabeled | **TODO** |"
    )
    ay2_named = (
        "| AY2 | **H-SHIPAY** | Ship/demo UI always "
        "`mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN); content matches mode | "
        "smoke + content · no unlabeled | **TODO** |"
    )
    if ay2_todo in text:
        text = text.replace(ay2_todo, ay2_named, 1)
    ay3_todo = (
        "| AY3 | **H-NANOGEN*** (name at AY0) | **North-star generative** — "
        "real new method / hybrid under named CAPCHECK; else HOLD/DEFER | "
        "true_continue → PROMOTE else HOLD/DEFER | **TODO** |"
    )
    ay3_named = (
        "| AY3 | **H-NANOGEN9** | **North-star generative** — "
        "real new method / hybrid under named CAPCHECK; else HOLD/DEFER "
        "(stance **defer** at AY0) | "
        "true_continue → PROMOTE else HOLD/DEFER | **TODO** |"
    )
    if ay3_todo in text:
        text = text.replace(ay3_todo, ay3_named, 1)
    bash_old = (
        "# after AY0:\n"
        "# npm run nano:ay:session\n"
        "# npm run nano:<prod-intent>\n"
        "# npm run nano:<ship-ay>\n"
        "# npm run nano:<nanogen-next>\n"
        "# npm run nano:ay:real-eval\n"
        "# npm run nano:ay:report\n"
        "# npm run nano:ay:freeze"
    )
    bash_new = (
        "npm run nano:ay:session\n"
        "# next: nano:prodint · nano:shipay · nano:nanogen9\n"
        "# npm run nano:ay:real-eval\n"
        "# npm run nano:ay:report\n"
        "# npm run nano:ay:freeze"
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

Wave AX **COMPLETE + FROZEN** (NANOGEN8 **DEFER**).  
**Reopen:** Wave **AY ACTIVE** via `pesquisa.md` — dual track only.  
**AY0 SESSION:** **DONE — PROMOTE** (`npm run nano:ay:session`) · gen stance **defer** · H-NANOGEN9 named.

## Dual track (locked)

| Track | Work |
|-------|------|
| **Caminho A** | Accept artifact · **intent FH 0** · hold hard-natural · FH · p50/p99 · KB · mode UI |
| **North star** | Nano generative / mini-AGI-*inspired* ≤5M · **defer** until real new method (NANOGEN6·7 HOLD · NANOGEN8 DEFER) |

## Next

1. **AY0 SESSION** — **DONE PROMOTE** (`npm run nano:ay:session`).  
2. **AY1 H-PRODINT** — **NEXT** — close intent FP; publish metrics board.  
3. Ship claim stays AX lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · intent-FP as hit · NANOGEN9=NANOGEN8+rename · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones.

```bash
npm run nano:ay:session
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

**Wave AY ACTIVE** (lab-book reopen after AX-FREEZE):

1. **Caminho A:** accept artifact — known-ask + robust SEMWRAP + labeled PEAK/RAG + apps; **intent FH 0** · hold hard-natural · p50/p99 · KB; mode UI always.  
2. **North star:** nano generative / mini-AGI-*inspired* ≤5M — gen stance **defer** (H-NANOGEN9; NANOGEN6·7 HOLD · NANOGEN8 DEFER until beaten; no NANOGEN9 clone).

Session: `wave-ay/SESSION.md` (AY0 **DONE — PROMOTE**; next AY1 H-PRODINT). Parent: Wave AX **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–AX | COMPLETE + FROZEN |
| Ship (until AY gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§8 · Wave AY0–AY6 |

## Do not

LOOKUP-as-IQ · intent-FP as hit · sell HOLD/DEFER as unlock · pack FH as live intent coverage · NANOGEN9=NANOGEN8+rename · CTX/SMART/FAST letter clones.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave AY ACTIVE" in text:
        return
    marker = "**Wave AX COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    # Replace "do not invent Wave AY" on AX line when present
    ax_line = text[idx:end]
    if "do not invent Wave AY" in ax_line:
        ax_line = ax_line.replace(
            "do not invent Wave AY",
            "Wave AY reopened via lab-book",
        )
        text = text[:idx] + ax_line + text[end:]
        end = idx + len(ax_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_ay() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave AY ACTIVE" in text:
        return
    agents_line = (
        "- **Wave AY ACTIVE** — AY0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-ay-session.md) "
        "(`npm run nano:ay:session`) — intent-adversary FP · PRODINT · "
        "gen stance **defer** (H-NANOGEN9); next AY1 H-PRODINT; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "NANOGEN6·7 HOLD · NANOGEN8 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave AY.",
        "Wave AY reopened via lab-book.",
        1,
    )
    text2, n = re.subn(
        r"- \*\*Wave AX COMPLETE \+ FROZEN\*\* —[^\n]+",
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_ay() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **AY** |" in text:
        return
    row = (
        "| **AY** | **ACTIVE** | AY0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-ay-session.md) (`npm run nano:ay:session`) "
        "— intent-FP · gen stance defer (H-NANOGEN9); next AY1 H-PRODINT; "
        "ship AF+AQ+AS trust + STRICT ablated DECODE; "
        "NANOGEN6·7 HOLD · NANOGEN8 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave AY |",
        "Wave AY reopened via lab-book |",
        1,
    )
    text2, n = re.subn(
        r"\| \*\*AX\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_ay() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave AY ACTIVE" in text:
        return
    dual = (
        "do not invent Wave AY); do not invent Wave AY",
        "Wave AY ACTIVE (AY0 SESSION PROMOTE; next AY1 H-PRODINT)); "
        "do not invent Wave AZ",
    )
    single = (
        "do not invent Wave AY",
        "Wave AY ACTIVE (AY0 SESSION PROMOTE; next AY1 H-PRODINT); "
        "do not invent Wave AZ",
    )
    if dual[0] in text:
        text = text.replace(dual[0], dual[1], 1)
    elif single[0] in text:
        text = text.replace(single[0], single[1], 1)
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_ay0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave AY0 SESSION" in text:
        return
    insert = (
        "| Wave AY0 SESSION | [wave-ay-session.md](wave-ay-session.md) "
        "**PROMOTE** (`npm run nano:ay:session`) — intent-FP N≥12 · "
        "4 classes · PRODINT charter · gen stance **defer** "
        "(H-NANOGEN9) · true-eval |"
    )
    marker = (
        "| Wave AX6 AX-FREEZE | [ax-freeze.md](ax-freeze.md) · "
        "[formal-haxfreeze-ax-freeze.md](formal-haxfreeze-ax-freeze.md) "
        "**PROMOTE** (`npm run nano:ax:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN8 DEFER; do not invent Wave AY |"
    )
    if marker not in text:
        return
    text = text.replace(
        marker,
        marker.replace("do not invent Wave AY", "Wave AY reopened via lab-book")
        + "\n"
        + insert,
        1,
    )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _AY_ACTIVE_LINE.replace(
        "**Wave AY ACTIVE:**", "**Wave AY ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _AY_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_ay()
    _patch_agenda_ay()
    _patch_evogen_ay()
    _patch_recipes_ay0()


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_ay0_session(
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
        "id": AY0_ID,
        "thesis": AY0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_ax_locks": sorted(AY0_CITED_AX_LOCKS),
        "product_int_charter": dict(AY0_PRODUCT_INT_CHARTER),
        "intent_fp_protocol": dict(AY0_INTENT_FP_PROTOCOL),
        "gen_stance": dict(AY0_GEN_STANCE),
        "true_gen_judge": dict(AY0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(AY0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(AY0_ASK_BATTERY),
        "intent_fp_n": len(AY0_INTENT_FP_ROWS),
        "safe_note": AY0_SAFE_NOTE,
        "anti_fp": AY0_ANTI_FP,
        "north_star": AY0_NORTH_STAR,
        "ship_lock": AY0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-ay-session.md",
        "rule": "pesquisa §5 AY0 · intent-FP + gen-defer + anti-FP",
        "next": "AY1 H-PRODINT (close intent FP debt)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AY0_ID,
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
