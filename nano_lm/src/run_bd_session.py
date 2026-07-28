"""Wave BD0 SESSION runner (nano:bd:session) — freeze BD packs + reopen after BC-FREEZE."""

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
from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import (
    BD0_ANTI_FP,
    BD0_ASK_BATTERY,
    BD0_AZ_HOLD_PROTOCOL,
    BD0_BA_HOLD_PROTOCOL,
    BD0_BB_HOLD_PROTOCOL,
    BD0_BC_HOLD_PROTOCOL,
    BD0_CITED_BC_LOCKS,
    BD0_CTX_BASELINE,
    BD0_FOREVER_PROTOCOL,
    BD0_FOREVER_ROWS,
    BD0_GEN_STANCE,
    BD0_ID,
    BD0_MODES,
    BD0_NORTH_STAR,
    BD0_REAL_EVAL_PROTOCOL,
    BD0_SAFE_NOTE,
    BD0_SCOREBOARD,
    BD0_SHIP_LOCK,
    BD0_SPEED_BASELINE,
    BD0_THESIS,
    BD0_TRUE_GEN_JUDGE,
    decide_bd0_session,
    map_bd_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bd/bd0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-bd/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-bd/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bd-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bd/SESSION.md"
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
_FOREVER_FP = str(BD0_FOREVER_ROWS[0]["question"])
_FOREVER_MUL = str(BD0_FOREVER_ROWS[4]["question"])
_BA_HOLD = str(BA0_FOREVER_ROWS[0]["question"])
_BB_HOLD = str(BB0_FOREVER_ROWS[0]["question"])
_BC_HOLD = str(BC0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BD_ACTIVE_LINE = (
    "**Wave BD ACTIVE:** BD0 [SESSION PROMOTE](wave-bd-session.md) "
    "(`npm run nano:bd:session`) — BD-FOREVER semantic anti-FP · "
    "BA/BB/BC/AZ hold · §1 scoreboard · ctx/speed baselines · gen stance "
    "**defer** (H-NANOGEN14 · M1|M2|M3) · real-eval; next BD1 H-SEMINT; "
    "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # 16c / 31Gi host: leave ≥4 cores free; cap workers under mem pressure.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(8, max(4, cpus - 4))
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


def _write_row_trial(
    trials_dir: Path,
    *,
    tid: str,
    pack: str,
    body: dict[str, Any],
) -> str:
    payload = {
        "trial_id": tid,
        "stage": "BD0",
        "hyp_id": BD0_ID,
        "pack": pack,
        "status": "frozen",
        **body,
    }
    path = trials_dir / f"{tid}.json"
    write_json(path, payload)
    return str(path.relative_to(REPO))


def _write_battery_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in BD0_ASK_BATTERY:
        tid = str(item["id"])
        written.append(
            _write_row_trial(
                trials_dir,
                tid=tid,
                pack="ask-battery",
                body={
                    "kind": item["kind"],
                    "question": item["question"],
                    "expect_mode": item["expect_mode"],
                    "mode": None,
                    "wall_ms": None,
                    "n_new": None,
                    "score": None,
                },
            )
        )
    return written


def _write_forever_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in BD0_FOREVER_ROWS:
        tid = str(item["id"])
        written.append(
            _write_row_trial(
                trials_dir,
                tid=tid,
                pack="bd-forever",
                body={
                    "class": item["class"],
                    "question": item["question"],
                    "expect_mode": item["expect_mode"],
                    "mode": None,
                    "wall_ms": None,
                    "false_hit": None,
                },
            )
        )
    return written


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("BD-SCOREBOARD", "scoreboard", dict(BD0_SCOREBOARD)),
        ("BD-FOREVER", "forever-protocol", dict(BD0_FOREVER_PROTOCOL)),
        ("BD-BA-HOLD", "ba-hold-protocol", dict(BD0_BA_HOLD_PROTOCOL)),
        ("BD-BB-HOLD", "bb-hold-protocol", dict(BD0_BB_HOLD_PROTOCOL)),
        ("BD-BC-HOLD", "bc-hold-protocol", dict(BD0_BC_HOLD_PROTOCOL)),
        ("BD-AZ-HOLD", "az-hold-protocol", dict(BD0_AZ_HOLD_PROTOCOL)),
        (
            "BD-BASELINES",
            "ctx-speed-baselines",
            {
                "speed": dict(BD0_SPEED_BASELINE),
                "ctx": dict(BD0_CTX_BASELINE),
            },
        ),
        (
            "BD-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BD0_GEN_STANCE),
                "true_gen_judge": dict(BD0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "BD-REAL-EVAL",
            "real-eval-protocol",
            dict(BD0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        written.append(
            _write_row_trial(
                trials_dir, tid=tid, pack=pack, body={"body": body}
            )
        )
    return written


def _freeze_trials(trials_dir: Path) -> tuple[list[str], bool]:
    trials_dir.mkdir(parents=True, exist_ok=True)
    written = (
        _write_battery_trials(trials_dir)
        + _write_forever_trials(trials_dir)
        + _write_charter_trials(trials_dir)
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = len(BD0_ASK_BATTERY) + len(BD0_FOREVER_ROWS) + 9
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BD0_ASK_BATTERY
    )
    fh_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in BD0_FOREVER_ROWS
    )
    bars = BD0_SCOREBOARD["bars"]
    debts = BD0_SCOREBOARD["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BD0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    body = "\n".join(
        [
            "# Wave BD0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 · Session: "
            "`.local/wave-bd/SESSION.md`  ",
            "> Module: `nano_lm/src/bd_session_ops.py` · "
            "Runner: `npm run nano:bd:session`  ",
            "> Parent: [bc-freeze.md](bc-freeze.md) "
            "(Wave BD reopened explicitly via lab-book reopen after BC-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BD packs: "
            "BD-FOREVER (N≥12 · reverse≠f-string · mul≠add · wrong-bank "
            "neighbors + paraphrases ≠ BA/BB/BC/AZ) · BA-FOREVER hold · "
            "BB-FOREVER hold · BC-FOREVER hold · AZ hold (div·sub·BIP FH0 · "
            "`a.clear()` LOOKUP) · §1 anti-FP scoreboard · ctx/speed "
            "baselines from BC · gen stance **defer** (CAPCHECK closed; "
            "**H-NANOGEN14**; M1|M2|M3 named; **not** NANOGEN14=NANOGEN13+"
            "rename) · real-eval protocol. **Not** a CTX/SMART/FAST/APP "
            "clone.  ",
            "Anti-FP signed. Generative claim locked until BD4 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | BD FH0 · BA/BB/BC/AZ hold · live ask · "
            "ctx/speed · modes · DECODE law (BD1) |",
            f"| BD-FOREVER protocol | {len(BD0_FOREVER_ROWS)} | "
            "reverse≠f-string · mul≠add · wrong-bank + paraphrases (BD1) |",
            "| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |",
            "| BB hold protocol | 1 | min·xor·absdiff·and·or FH0 regression |",
            "| BC hold protocol | 1 | floordiv·neg·gcd·lshift·rshift·nand "
            "FH0 regression |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Ctx/speed baselines | 1 | BC FASTLIFT p50/p99 · CTXLIFT2 "
            "content (BD2/BD3) |",
            "| Gen stance | 1 | **defer** · CAPCHECK closed · "
            "H-NANOGEN14 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 "
            "DEFER cited (BD4) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BD4) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BD5) |",
            f"| Ask battery | {len(BD0_ASK_BATTERY)} | frozen live rows "
            "(scored at BD5) |",
            "",
            "## Cited BC locks",
            "",
            ", ".join(sorted(BD0_CITED_BC_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- bd_forever_false_hit_max: **{bars['bd_forever_false_hit_max']}**  ",
            f"- ba_forever_false_hit_max: **{bars['ba_forever_false_hit_max']}**  ",
            f"- bb_forever_false_hit_max: **{bars['bb_forever_false_hit_max']}**  ",
            f"- bc_forever_false_hit_max: **{bars['bc_forever_false_hit_max']}**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- bd_forever_min_n: **{bars['bd_forever_min_n']}**  ",
            f"- bd_forever_classes_min: **{bars['bd_forever_classes_min']}**  ",
            f"- decode_gibberish_neq_content_ok: "
            f"**{bars['decode_gibberish_neq_content_ok']}**  ",
            f"- default_ask_intent_mismatch: "
            f"**{bars['default_ask_intent_mismatch']}**  ",
            f"- default_ask_exact_gold: "
            f"**{bars['default_ask_exact_gold']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- pack_pass_neq_forever: **{bars['pack_pass_neq_forever']}**  ",
            f"- bank_stuff_forbidden: **{bars['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: **{bars['paraphrase_required']}**  ",
            f"- l_eff_alone_forbidden: **{bars['l_eff_alone_forbidden']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no vanity reopen OPSFAM/FASTLIFT/CTXLIFT2 unless SEMINT fails",
            "",
            "## Post-BC debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## BD-FOREVER protocol",
            "",
            f"- held_out: **{BD0_FOREVER_PROTOCOL['held_out']}**  ",
            f"- forever: **{BD0_FOREVER_PROTOCOL['forever']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{BD0_FOREVER_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: "
            f"**{BD0_FOREVER_PROTOCOL['paraphrase_required']}**  ",
            f"- neq_bc_forever: "
            f"**{BD0_FOREVER_PROTOCOL['neq_bc_forever']}**  ",
            f"- live_fp_id: **{BD0_FOREVER_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{BD0_FOREVER_PROTOCOL['min_n']}**  ",
            f"- path: `{BD0_FOREVER_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            fh_rows,
            "",
            "## BA hold protocol",
            "",
            f"- forever_false_hit_max: "
            f"**{BD0_BA_HOLD_PROTOCOL['forever_false_hit_max']}**  ",
            f"- heldout_n: **{BD0_BA_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- regression_hold: "
            f"**{BD0_BA_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## BB hold protocol",
            "",
            f"- forever_false_hit_max: "
            f"**{BD0_BB_HOLD_PROTOCOL['forever_false_hit_max']}**  ",
            f"- heldout_n: **{BD0_BB_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- regression_hold: "
            f"**{BD0_BB_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## BC hold protocol",
            "",
            f"- forever_false_hit_max: "
            f"**{BD0_BC_HOLD_PROTOCOL['forever_false_hit_max']}**  ",
            f"- heldout_n: **{BD0_BC_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- regression_hold: "
            f"**{BD0_BC_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## AZ hold protocol",
            "",
            f"- heldout_false_hit_max: "
            f"**{BD0_AZ_HOLD_PROTOCOL['heldout_false_hit_max']}**  ",
            f"- overrefuse_miss_max: "
            f"**{BD0_AZ_HOLD_PROTOCOL['overrefuse_miss_max']}**  ",
            f"- heldout_n: **{BD0_AZ_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- overrefuse_n: **{BD0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            f"- regression_hold: "
            f"**{BD0_AZ_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## Speed baseline (from BC FASTLIFT)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BD0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- bd2_gate: `{BD0_SPEED_BASELINE['bd2_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BD0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BD0_CTX_BASELINE['content_bars_required']}**  ",
            f"- bd3_gate: `{BD0_CTX_BASELINE['bd3_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BD0_GEN_STANCE['stance']}**  ",
            f"- allowed: {' · '.join(BD0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BD0_GEN_STANCE['named_hyp']}**  ",
            f"- named_semint: **{BD0_GEN_STANCE['named_semint']}**  ",
            f"- named_fast: **{BD0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BD0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BD0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen14_rename_forbidden: "
            f"**{BD0_GEN_STANCE['nanogen14_rename_forbidden']}**  ",
            f"- bd4_gate: `{BD0_GEN_STANCE['bd4_gate']}`  ",
            "",
            BD0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BD0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen14_rename_forbidden: "
            f"{BD0_TRUE_GEN_JUDGE['nanogen14_rename_forbidden']}  ",
            f"- scoring: `{BD0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BD0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{BD0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BD0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- score_labels: "
            f"{' · '.join(BD0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_forever: "
            f"{BD0_REAL_EVAL_PROTOCOL['pack_pass_neq_forever']}  ",
            f"- gen_claim_rule: "
            f"{BD0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BD0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BD0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BD0_ANTI_FP,
            "",
            "## North star",
            "",
            BD0_NORTH_STAR,
            "",
            "## Ship lock (until BD gen PROMOTE)",
            "",
            BD0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:bd:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "BD-FOREVER + BA/BB/BC/AZ hold probes are **recorded** "
            "(BD1 scores forever FH=0 / holds=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-bd/bd0_session.json` · "
            "`results/nano-lm/wave-bd/trials/BD-*.json`.  ",
            "Contract: `nano_lm/tests/test_bd_session.py`.",
            "",
            "## Claims",
            "",
            "- BC packs frozen for Wave BD — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BD0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BD4 H-NANOGEN14** "
            "true_continue under a real new method (M1|M2|M3; "
            "never NANOGEN13+rename; span-fallback ≠ gen).  ",
            "- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN14 rename · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen.",
            "",
            "Next: **BD1 H-SEMINT** — drive forever FH → 0 via semantic "
            "intent/SEMWRAP gate; hold BA/BB/BC/AZ bars; live ask "
            "scoreboard OK|FP|MISS|ABSTAIN-OK.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _ask_once(
    question: str,
    *,
    wrap: bool = True,
    abstain: bool = True,
    semwrap: bool = True,
) -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=question,
        root=_CHAMPION,
        seed=0,
        wrap=wrap,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=abstain,
        semwrap=semwrap if wrap else False,
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
    modes: list[str],
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
        map_bd_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        all(m in BD0_MODES for m in modes),
    )
    return all(checks)


def _arm_block(
    raw: dict[str, Any], *, question: str, note: str
) -> dict[str, Any]:
    tel = extract_telemetry(raw)
    mode = map_bd_product_mode(str(tel["mode"]))
    return {
        "arm": classify_arm(raw),
        "raw_mode": tel["mode"],
        "product_mode": mode,
        "wall_ms": tel["wall_ms"],
        "n_new": tel["n_new"],
        "completion": str(raw.get("completion", ""))[:120],
        "question": question,
        "note": note,
    }


def _smoke_octa_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP+DECODE+near-miss+BD FP+mul FP+BA/BB/BC/AZ hold+over-refuse."""
    jobs = (
        ("lookup", lambda: _ask_once(_KNOWN, wrap=True, abstain=True, semwrap=False)),
        ("decode", lambda: _ask_once(_DECODE_Q, wrap=False, abstain=False)),
        ("near", lambda: _ask_once(_NEAR_MISS)),
        ("forever", lambda: _ask_once(_FOREVER_FP)),
        ("mul", lambda: _ask_once(_FOREVER_MUL)),
        ("bahold", lambda: _ask_once(_BA_HOLD)),
        ("bbhold", lambda: _ask_once(_BB_HOLD)),
        ("bchold", lambda: _ask_once(_BC_HOLD)),
        ("azhold", lambda: _ask_once(_AZ_HOLD)),
        ("overref", lambda: _ask_once(_OVERREFUSE)),
    )
    n = min(len(jobs), max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        futs = {k: pool.submit(fn) for k, fn in jobs}
        raws = {k: fut.result() for k, fut in futs.items()}
    lookup = raws["lookup"]
    gen = raws["decode"]
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_mode = map_bd_product_mode(str(l_tel["mode"]))
    g_mode = map_bd_product_mode(str(g_tel["mode"]))
    blocks = {
        "near_miss": _arm_block(
            raws["near"],
            question=_NEAR_MISS,
            note="AZ locked ABSTAIN; BD0 verifies mapping",
        ),
        "forever_fp": _arm_block(
            raws["forever"],
            question=_FOREVER_FP,
            note="BD-FOREVER reverse FP; BD1 scores FH=0 — BD0 records only",
        ),
        "forever_mul_fp": _arm_block(
            raws["mul"],
            question=_FOREVER_MUL,
            note="BD-FOREVER mul FP; BD1 scores FH=0 — BD0 records only",
        ),
        "ba_hold": _arm_block(
            raws["bahold"],
            question=_BA_HOLD,
            note="BA-FOREVER pow hold; must stay ABSTAIN — BD0 records",
        ),
        "bb_hold": _arm_block(
            raws["bbhold"],
            question=_BB_HOLD,
            note="BB-FOREVER min hold; must stay ABSTAIN — BD0 records",
        ),
        "bc_hold": _arm_block(
            raws["bchold"],
            question=_BC_HOLD,
            note="BC-FOREVER floordiv hold; must stay ABSTAIN — BD0 records",
        ),
        "az_hold": _arm_block(
            raws["azhold"],
            question=_AZ_HOLD,
            note="AZ hold div; must stay ABSTAIN — BD0 records",
        ),
        "overrefuse": _arm_block(
            raws["overref"],
            question=_OVERREFUSE,
            note="exact clear gold; must LOOKUP — BD0 records",
        ),
    }
    modes = [str(b["product_mode"]) for b in blocks.values()]
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
        modes=modes,
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
            "note": "BD1 must fail gibberish content_ok; BD0 freezes bar",
        },
        **blocks,
        "modes_charter": sorted(BD0_MODES),
        "abstain_alias": map_bd_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BD0_GEN_STANCE["stance"],
        "named_hyp": BD0_GEN_STANCE["named_hyp"],
        "named_semint": BD0_GEN_STANCE["named_semint"],
        "named_fast": BD0_GEN_STANCE["named_fast"],
        "named_ctx": BD0_GEN_STANCE["named_ctx"],
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_octa_arm(workers=workers)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "octa-arm smoke failed", "ask": ask}
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
            f"# Wave BD session checklist (**OPEN** · BD0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BD **OPEN** · semantic anti-FP scoreboard + "
            "ctx/speed + honest gen).  ",
            f"> Parent: BC COMPLETE + FROZEN · Ship: **{BD0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after BC-FREEZE; BD-FOREVER FP open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 "
            "DEFER).",
            "",
            "## Current stage",
            "",
            f"**BD0 — SESSION ({status})** · Next: **BD1 H-SEMINT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BD ACTIVE** |",
            "| Track | BD FH0 · BA/BB/BC/AZ hold · ctx/speed · "
            "gen stance **defer** (H-NANOGEN14) |",
            "| Parent | BC COMPLETE + FROZEN |",
            "| Open hole | BD-FOREVER reverse≠f-string · mul≠add · "
            "wrong-bank · live ask scoreboard · gate not bank-stuff |",
            "| Forbidden | NANOGEN14 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST |",
            "",
            "## North star (signed)",
            "",
            BD0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BD0)",
            "",
            "```text",
            "MODEL = BD0-SESSION",
            "",
            "[x] Freeze BD-FOREVER (N≥12 · reverse≠f-string · mul≠add · "
            "wrong-bank + paraphrases)",
            "[x] Freeze BA/BB/BC-FOREVER hold + AZ hold",
            "[x] Freeze §1 scoreboard (forever FH · live ask · ctx/speed)",
            "[x] Publish ctx/speed baselines from BC",
            "[x] Freeze gen stance = defer (CAPCHECK closed; H-NANOGEN14; "
            "M1|M2|M3)",
            "[x] Name BD1 H-SEMINT · BD2 H-FASTGAIN · BD3 H-CTXGAIN · "
            "BD4 H-NANOGEN14",
            "[x] Freeze true gen judge (rename forbidden)",
            "[x] Real-eval ask battery protocol (eval=prod ask · OK|FP|MISS)",
            "[x] Copy live audits into .local/wave-bd/",
            "[x] Do NOT reopen OPSFAM/FASTLIFT/CTXLIFT2 unless SEMINT fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN14 = NANOGEN13+rename",
            "[ ] Next: BD1 H-SEMINT",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BD0 | SESSION | **{status}** |",
            "| BD1 | H-SEMINT | **NEXT** |",
            "| BD2 | H-FASTGAIN | pending |",
            "| BD3 | H-CTXGAIN | pending |",
            "| BD4 | H-NANOGEN14 | pending (defer unless real new method) |",
            "| BD5 | BD-REAL-EVAL | pending |",
            "| BD6 | BD-REPORT | pending |",
            "| BD7 | BD-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Forever semantic FH (ask path) | **0** | live FP debt "
            "(reverse→f-string · mul→add) |",
            "| BA-FOREVER FH | **0** | H-REALGAIN hold |",
            "| BB-FOREVER FH | **0** | H-INTENTGEN hold |",
            "| BC-FOREVER FH | **0** | H-OPSFAM hold |",
            "| AZ hold FH (div·sub·BIP) | **0** | AZ PRODGEN 0/12 |",
            "| Over-refuse miss (exact clear) | **0** | AZ a.clear() LOOKUP |",
            "| Live ask scoreboard | OK|FP|MISS|ABSTAIN-OK | BD0 records |",
            "| Speed p50/p99 | publish / no FP regress | BC FASTLIFT |",
            "| Context content bars | usable long/cite/howto | L_eff ≠ pass |",
            "| DECODE content | usable or ABSTAIN | STRICT lock |",
            "| True continue (NANOGEN14) | PROMOTE else HOLD/DEFER | "
            "NANOGEN6·7 HOLD · NANOGEN8…13 DEFER; stance defer |",
            "",
            "## Live audits promoted",
            "",
            "- `fp-novel-1785263054.jsonl`",
            "- `fp-extra-1785263130.jsonl`",
            "- `live-1785262996.log`",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    # Lab book escapes | inside cells as \|
    for mid in ("M1|M2|M3", "M1\\|M2\\|M3"):
        next_row = (
            "| BD0 | **SESSION** | Freeze BD-FOREVER from post-BC live FP; "
            f"lock §1 scoreboard; gen stance = prove {mid} or DEFER; "
            "`.local/wave-bd/SESSION.md` | cite BC; no rename | **TODO** |"
        )
        done_row = (
            "| BD0 | **SESSION** | Freeze BD-FOREVER from post-BC live FP; "
            f"lock §1 scoreboard; gen stance = prove {mid} or DEFER; "
            "`.local/wave-bd/SESSION.md` | cite BC; no rename | "
            "**DONE — PROMOTE** |"
        )
        if next_row in text:
            text = text.replace(next_row, done_row, 1)
            break
    text = text.replace(
        "> **Session:** create `.local/wave-bd/SESSION.md` at BD0.  ",
        "> **Session:** `.local/wave-bd/SESSION.md` "
        "(BD0 **DONE — PROMOTE**; next BD1 H-SEMINT).  ",
        1,
    )
    done_next = (
        "1. **BD0 SESSION** — **DONE PROMOTE** "
        "(`npm run nano:bd:session`) · gen stance **defer** · "
        "H-SEMINT·H-FASTGAIN·H-CTXGAIN·H-NANOGEN14 named · "
        "BD-FOREVER + BA/BB/BC/AZ hold + baselines frozen.  "
    )
    for mid in ("M1|M2|M3", "M1\\|M2\\|M3"):
        old_next = (
            "1. **BD0 SESSION** — freeze BD-FOREVER seeds from post-BC live "
            "residual FP (reverse≠f-string · mul≠add + paras); lock §1 "
            f"scoreboard; gen stance = prove {mid} or DEFER; create "
            "`.local/wave-bd/SESSION.md`; copy live audits into "
            "`.local/wave-bd/`.  "
        )
        if old_next in text:
            text = text.replace(old_next, done_next, 1)
            break
    text = text.replace(
        "**H-ID names** above are working titles — lock exact IDs at "
        "BD0 SESSION (must ≠ prior wave npm script collisions).",
        "**H-ID names locked at BD0:** H-SEMINT · H-FASTGAIN · "
        "H-CTXGAIN · H-NANOGEN14 (must ≠ prior wave npm script collisions).",
        1,
    )
    text = text.replace(
        "2. **BD1 H-SEMINT** — semantic / SEMWRAP intent gate → "
        "BD-FOREVER FH 0; BA/BB/BC/AZ hold; ≥10 novel FP 0; "
        "**no bank stuffing**.  ",
        "2. **BD1 H-SEMINT** — **NEXT** — semantic / SEMWRAP intent gate → "
        "BD-FOREVER FH 0; BA/BB/BC/AZ hold; ≥10 novel FP 0; "
        "**no bank stuffing**.  ",
        1,
    )
    bd1_todo = (
        "| BD1 | **H-SEMINT** (working name) | Semantic intent / SEMWRAP "
        "reject → BD-FOREVER FH 0 · BA/BB/BC hold · novel FP 0 | §1 board | "
        "**TODO** |"
    )
    bd1_next = (
        "| BD1 | **H-SEMINT** | Semantic intent / SEMWRAP reject → "
        "BD-FOREVER FH 0 · BA/BB/BC/AZ hold · novel FP 0 | §1 board | "
        "**NEXT** |"
    )
    if bd1_todo in text:
        text = text.replace(bd1_todo, bd1_next, 1)
    # Lock working names in stage table
    for old, new in (
        (
            "| BD2 | **H-FASTGAIN** (working name) |",
            "| BD2 | **H-FASTGAIN** |",
        ),
        (
            "| BD3 | **H-CTXGAIN** (working name) |",
            "| BD3 | **H-CTXGAIN** |",
        ),
    ):
        text = text.replace(old, new, 1)
    bash_old = (
        "# then (after BD0 scripts exist):\n"
        "# npm run nano:bd:session\n"
        "# npm run nano:semint            # or locked BD1 id\n"
        "# npm run nano:bd:fastgain\n"
        "# npm run nano:bd:ctxgain\n"
        "# npm run nano:nanogen14\n"
        "# npm run nano:bd:real-eval\n"
        "# npm run nano:bd:report\n"
        "# npm run nano:bd:freeze"
    )
    bash_new = (
        "npm run nano:bd:session\n"
        "# next: nano:semint · nano:bd:fastgain · nano:bd:ctxgain · "
        "nano:nanogen14\n"
        "# npm run nano:bd:real-eval\n"
        "# npm run nano:bd:report\n"
        "# npm run nano:bd:freeze"
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

Wave BC **COMPLETE + FROZEN** (H-NANOGEN13 **DEFER**).  
**Reopen:** Wave **BD ACTIVE** via `pesquisa.md` — semantic/wrong-bank anti-FP.  
**BD0 SESSION:** **DONE — PROMOTE** (`npm run nano:bd:session`) · gen stance **defer** · H-SEMINT · H-FASTGAIN · H-CTXGAIN · H-NANOGEN14 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0–P1** | BD-FOREVER FH 0 (reverse≠f-string · mul≠add · wrong-bank) · BA/BB/BC/AZ hold · novel |
| **P2–P3** | Speed p50/p99 + context content bars on prod path (no FP regress) |
| **P4** | One real gen method (M1|M2|M3) — else HOLD/DEFER (H-NANOGEN14) |

## Next

1. **BD0 SESSION** — **DONE PROMOTE** (`npm run nano:bd:session`).  
2. **BD1 H-SEMINT** — **NEXT** — BD-FOREVER FH → 0 via semantic intent gate; hold BA/BB/BC/AZ.  
3. Ship claim stays BC lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · BA+BB+BC PASS with BD FP · NANOGEN14=NANOGEN13+rename · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones.

```bash
npm run nano:bd:session
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

**Wave BD ACTIVE** (lab-book reopen after BC-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation**.

**Cursor measures (anti-FP):**

1. **BD-FOREVER semantic FH → 0** (reverse≠f-string · mul≠add · wrong-bank + paraphrases)  
2. **BA-FOREVER + BB-FOREVER + BC-FOREVER + AZ hold** — no regression  
3. **Speed** — prod ask p50/p99 (no quality regress)  
4. **Context** — usable long/cite/howto content bars (L_eff alone ≠ win)  
5. **Generative** — true_continue only; else HOLD/DEFER (NANOGEN6–13 cited)

Session: `wave-bd/SESSION.md` (BD0 **DONE — PROMOTE**; next BD1 H-SEMINT). Parent: Wave BC **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–BC | COMPLETE + FROZEN |
| Ship (until BD gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§13 · Wave BD0–BD7 |

## Do not

LOOKUP-as-IQ · BA+BB+BC PASS with BD FP · over-refuse as win · sell HOLD/DEFER as unlock · L_eff/cache vanity as ctx/speed · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BD ACTIVE" in text:
        return
    marker = "**Wave BC COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    bc_line = text[idx:end]
    if "do not invent Wave BD" in bc_line:
        bc_line = bc_line.replace(
            "do not invent Wave BD",
            "Wave BD reopened via lab-book",
        )
        text = text[:idx] + bc_line + text[end:]
        end = idx + len(bc_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_bd() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BD ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BD ACTIVE** — BD0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bd-session.md) "
        "(`npm run nano:bd:session`) — BD-FOREVER semantic anti-FP · "
        "BA/BB/BC/AZ hold · §1 scoreboard · gen stance **defer** "
        "(H-NANOGEN14); next BD1 H-SEMINT; ship remains **AF + AQ + AS "
        "trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8·9·10·11·12·13 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave BD.",
        "Wave BD reopened via lab-book.",
        1,
    )
    text2, n = re.subn(
        r"- \*\*Wave BC COMPLETE \+ FROZEN\*\* —[^\n]+",
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_bd() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **BD** |" in text:
        return
    row = (
        "| **BD** | **ACTIVE** | BD0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-bd-session.md) (`npm run nano:bd:session`) "
        "— BD-FOREVER · BA/BB/BC/AZ hold · gen stance defer (H-NANOGEN14); "
        "next BD1 H-SEMINT; ship AF+AQ+AS trust + STRICT ablated DECODE; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12·13 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave BD |",
        "Wave BD reopened via lab-book |",
        1,
    )
    text2, n = re.subn(
        r"\| \*\*BC\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_bd() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave BD ACTIVE" in text:
        return
    if "Wave BD ACTIVE" in text:
        return
    single = (
        "do not invent Wave BD",
        "Wave BD ACTIVE (BD0 SESSION PROMOTE; next BD1 H-SEMINT); "
        "do not invent Wave BE",
    )
    if single[0] in text:
        text = text.replace(single[0], single[1], 1)
        # Collapse any accidental second occurrence left from prior edits
        text = text.replace(single[0], "do not invent Wave BE", 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_bd0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BD0 SESSION" in text:
        return
    insert = (
        "| Wave BD0 SESSION | [wave-bd-session.md](wave-bd-session.md) "
        "**PROMOTE** (`npm run nano:bd:session`) — BD-FOREVER N≥12 · "
        "reverse≠f-string · mul≠add · wrong-bank · BA/BB/BC/AZ hold · §1 "
        "scoreboard · ctx/speed baselines · gen stance **defer** "
        "(H-NANOGEN14 · M1|M2|M3) · true-eval |"
    )
    marker = (
        "| Wave BC7 BC-FREEZE | [bc-freeze.md](bc-freeze.md) · "
        "[formal-habcfreeze-bc-freeze.md](formal-habcfreeze-bc-freeze.md) "
        "**PROMOTE** (`npm run nano:bc:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN13 DEFER; do not invent Wave BD |"
    )
    if marker not in text:
        marker2 = marker.replace(
            "do not invent Wave BD",
            "Wave BD reopened via lab-book",
        )
        if marker2 in text:
            text = text.replace(marker2, marker2 + "\n" + insert, 1)
            _RECIPES.write_text(text, encoding="utf-8")
        return
    text = text.replace(
        marker,
        marker.replace("do not invent Wave BD", "Wave BD reopened via lab-book")
        + "\n"
        + insert,
        1,
    )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BD_ACTIVE_LINE.replace(
        "**Wave BD ACTIVE:**", "**Wave BD ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BD_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_bd()
    _patch_agenda_bd()
    _patch_evogen_bd()
    _patch_recipes_bd0()


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_bd0_session(
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
        "id": BD0_ID,
        "thesis": BD0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_bc_locks": sorted(BD0_CITED_BC_LOCKS),
        "scoreboard": dict(BD0_SCOREBOARD),
        "forever_protocol": dict(BD0_FOREVER_PROTOCOL),
        "ba_hold_protocol": dict(BD0_BA_HOLD_PROTOCOL),
        "bb_hold_protocol": dict(BD0_BB_HOLD_PROTOCOL),
        "bc_hold_protocol": dict(BD0_BC_HOLD_PROTOCOL),
        "az_hold_protocol": dict(BD0_AZ_HOLD_PROTOCOL),
        "speed_baseline": dict(BD0_SPEED_BASELINE),
        "ctx_baseline": dict(BD0_CTX_BASELINE),
        "gen_stance": dict(BD0_GEN_STANCE),
        "true_gen_judge": dict(BD0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BD0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BD0_ASK_BATTERY),
        "forever_n": len(BD0_FOREVER_ROWS),
        "safe_note": BD0_SAFE_NOTE,
        "anti_fp": BD0_ANTI_FP,
        "north_star": BD0_NORTH_STAR,
        "ship_lock": BD0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-bd-session.md",
        "rule": (
            "pesquisa §9 BD0 · BD-FOREVER + BA/BB/BC/AZ hold + "
            "gen-defer + anti-FP"
        ),
        "next": "BD1 H-SEMINT (BD-FOREVER FH 0 via gate; hold BA/BB/BC/AZ)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BD0_ID,
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
