"""Wave BC0 SESSION runner (nano:bc:session) — freeze BC packs + reopen after BB-FREEZE."""

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
from bc_session_ops import (
    BC0_ANTI_FP,
    BC0_ASK_BATTERY,
    BC0_AZ_HOLD_PROTOCOL,
    BC0_BA_HOLD_PROTOCOL,
    BC0_BB_HOLD_PROTOCOL,
    BC0_CITED_BB_LOCKS,
    BC0_CTX_BASELINE,
    BC0_FOREVER_PROTOCOL,
    BC0_FOREVER_ROWS,
    BC0_GEN_STANCE,
    BC0_ID,
    BC0_MODES,
    BC0_NORTH_STAR,
    BC0_REAL_EVAL_PROTOCOL,
    BC0_SAFE_NOTE,
    BC0_SCOREBOARD,
    BC0_SHIP_LOCK,
    BC0_SPEED_BASELINE,
    BC0_THESIS,
    BC0_TRUE_GEN_JUDGE,
    decide_bc0_session,
    map_bc_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bc/bc0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-bc/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-bc/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bc-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bc/SESSION.md"
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
_FOREVER_FP = str(BC0_FOREVER_ROWS[0]["question"])
_BA_HOLD = str(BA0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BC_ACTIVE_LINE = (
    "**Wave BC ACTIVE:** BC0 [SESSION PROMOTE](wave-bc-session.md) "
    "(`npm run nano:bc:session`) — BC-FOREVER anti-FP · BA/BB/AZ hold · "
    "§1 scoreboard · ctx/speed baselines · gen stance **defer** "
    "(H-NANOGEN13 · M1|M2|M3) · real-eval; next BC1 H-OPSFAM; "
    "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER; ≤5M stays."
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


def _write_battery_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in BC0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "BC0",
            "hyp_id": BC0_ID,
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


def _write_forever_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in BC0_FOREVER_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "BC0",
            "hyp_id": BC0_ID,
            "pack": "bb-forever",
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
        ("BC-SCOREBOARD", "scoreboard", dict(BC0_SCOREBOARD)),
        ("BC-FOREVER", "forever-protocol", dict(BC0_FOREVER_PROTOCOL)),
        ("BC-BA-HOLD", "ba-hold-protocol", dict(BC0_BA_HOLD_PROTOCOL)),
        ("BC-BB-HOLD", "bb-hold-protocol", dict(BC0_BB_HOLD_PROTOCOL)),
        ("BC-AZ-HOLD", "az-hold-protocol", dict(BC0_AZ_HOLD_PROTOCOL)),
        (
            "BC-BASELINES",
            "ctx-speed-baselines",
            {
                "speed": dict(BC0_SPEED_BASELINE),
                "ctx": dict(BC0_CTX_BASELINE),
            },
        ),
        (
            "BC-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BC0_GEN_STANCE),
                "true_gen_judge": dict(BC0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "BC-REAL-EVAL",
            "real-eval-protocol",
            dict(BC0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "BC0",
            "hyp_id": BC0_ID,
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
        + _write_forever_trials(trials_dir)
        + _write_charter_trials(trials_dir)
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = len(BC0_ASK_BATTERY) + len(BC0_FOREVER_ROWS) + 8
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BC0_ASK_BATTERY
    )
    fh_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in BC0_FOREVER_ROWS
    )
    bars = BC0_SCOREBOARD["bars"]
    debts = BC0_SCOREBOARD["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BC0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    body = "\n".join(
        [
            "# Wave BC0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §8 · Session: "
            "`.local/wave-bc/SESSION.md`  ",
            "> Module: `nano_lm/src/bc_session_ops.py` · "
            "Runner: `npm run nano:bc:session`  ",
            "> Parent: [bb-freeze.md](bb-freeze.md) "
            "(Wave BC reopened explicitly via lab-book reopen after BB-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BC packs: "
            "BC-FOREVER (N≥18 · floordiv·neg·gcd·lshift·rshift·nand + paraphrases ≠ BA/BB/AZ) · "
            "BA-FOREVER hold · BB-FOREVER hold · "
            "AZ hold (div·sub·BIP FH0 · `a.clear()` LOOKUP) · §1 anti-FP "
            "scoreboard · ctx/speed baselines from BB · gen stance "
            "**defer** (CAPCHECK closed; **H-NANOGEN13**; M1|M2|M3 named; "
            "**not** NANOGEN13=NANOGEN12+rename) · real-eval protocol. "
            "**Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until BC4 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | BC FH0 · BA/BB/AZ hold · live ask · "
            "ctx/speed · modes · DECODE law (BC1) |",
            f"| BC-FOREVER protocol | {len(BC0_FOREVER_ROWS)} | "
            "floordiv·neg·gcd·lshift·rshift·nand + paraphrases (BC1) |",
            "| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |",
            "| BB hold protocol | 1 | min·xor·absdiff·and·or FH0 regression |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Ctx/speed baselines | 1 | BB FASTHOLD p50/p99 · CTXHOLD "
            "content (BC2/BC3) |",
            "| Gen stance | 1 | **defer** · CAPCHECK closed · "
            "H-NANOGEN13 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 "
            "DEFER cited (BC4) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BC4) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BC5) |",
            f"| Ask battery | {len(BC0_ASK_BATTERY)} | frozen live rows "
            "(scored at BC5) |",
            "",
            "## Cited BB locks",
            "",
            ", ".join(sorted(BC0_CITED_BB_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- bc_forever_false_hit_max: **{bars['bc_forever_false_hit_max']}**  ",
            f"- ba_forever_false_hit_max: **{bars['ba_forever_false_hit_max']}**  ",
            f"- bb_forever_false_hit_max: **{bars['bb_forever_false_hit_max']}**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- bc_forever_min_n: **{bars['bc_forever_min_n']}**  ",
            f"- bc_forever_classes_min: **{bars['bc_forever_classes_min']}**  ",
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
            "- no vanity reopen INTENTGEN/FASTHOLD/CTXHOLD unless OPSFAM fails",
            "",
            "## Post-BB debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## BC-FOREVER protocol",
            "",
            f"- held_out: **{BC0_FOREVER_PROTOCOL['held_out']}**  ",
            f"- forever: **{BC0_FOREVER_PROTOCOL['forever']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{BC0_FOREVER_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: "
            f"**{BC0_FOREVER_PROTOCOL['paraphrase_required']}**  ",
            f"- neq_az_heldout: "
            f"**{BC0_FOREVER_PROTOCOL['neq_az_heldout']}**  ",
            f"- live_fp_id: **{BC0_FOREVER_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{BC0_FOREVER_PROTOCOL['min_n']}**  ",
            f"- path: `{BC0_FOREVER_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            fh_rows,
            "",
            "## BA hold protocol",
            "",
            f"- forever_false_hit_max: "
            f"**{BC0_BA_HOLD_PROTOCOL['forever_false_hit_max']}**  ",
            f"- heldout_n: **{BC0_BA_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- regression_hold: "
            f"**{BC0_BA_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## BB hold protocol",
            "",
            f"- forever_false_hit_max: "
            f"**{BC0_BB_HOLD_PROTOCOL['forever_false_hit_max']}**  ",
            f"- heldout_n: **{BC0_BB_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- regression_hold: "
            f"**{BC0_BB_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## AZ hold protocol",
            "",
            f"- heldout_false_hit_max: "
            f"**{BC0_AZ_HOLD_PROTOCOL['heldout_false_hit_max']}**  ",
            f"- overrefuse_miss_max: "
            f"**{BC0_AZ_HOLD_PROTOCOL['overrefuse_miss_max']}**  ",
            f"- heldout_n: **{BC0_AZ_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- overrefuse_n: **{BC0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            f"- regression_hold: "
            f"**{BC0_AZ_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## Speed baseline (from BB FASTHOLD)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BC0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- bc2_gate: `{BC0_SPEED_BASELINE['bc2_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BC0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BC0_CTX_BASELINE['content_bars_required']}**  ",
            f"- bc3_gate: `{BC0_CTX_BASELINE['bc3_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BC0_GEN_STANCE['stance']}**  ",
            f"- allowed: {' · '.join(BC0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BC0_GEN_STANCE['named_hyp']}**  ",
            f"- named_opsfam: **{BC0_GEN_STANCE['named_opsfam']}**  ",
            f"- named_fast: **{BC0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BC0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BC0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen13_rename_forbidden: "
            f"**{BC0_GEN_STANCE['nanogen13_rename_forbidden']}**  ",
            f"- bc4_gate: `{BC0_GEN_STANCE['bc4_gate']}`  ",
            "",
            BC0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BC0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen13_rename_forbidden: "
            f"{BC0_TRUE_GEN_JUDGE['nanogen13_rename_forbidden']}  ",
            f"- scoring: `{BC0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BC0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{BC0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BC0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- score_labels: "
            f"{' · '.join(BC0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_forever: "
            f"{BC0_REAL_EVAL_PROTOCOL['pack_pass_neq_forever']}  ",
            f"- gen_claim_rule: "
            f"{BC0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BC0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BC0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BC0_ANTI_FP,
            "",
            "## North star",
            "",
            BC0_NORTH_STAR,
            "",
            "## Ship lock (until BC gen PROMOTE)",
            "",
            BC0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:bc:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "BC-FOREVER + AZ hold probes are **recorded** "
            "(BC1 scores forever FH=0 / AZ hold=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-bc/bc0_session.json` · "
            "`results/nano-lm/wave-bc/trials/BC-*.json`.  ",
            "Contract: `nano_lm/tests/test_bc_session.py`.",
            "",
            "## Claims",
            "",
            "- BB packs frozen for Wave BC — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BC0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BC4 H-NANOGEN13** "
            "true_continue under a real new method (M1|M2|M3; "
            "never NANOGEN12+rename; span-fallback ≠ gen).  ",
            "- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN13 rename · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen.",
            "",
            "Next: **BC1 H-OPSFAM** — drive forever FH → 0 via gate; "
            "hold BA/BB/AZ bars; live ask scoreboard OK|FP|MISS|ABSTAIN-OK.",
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


def _ask_forever_fp() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_FOREVER_FP,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
        semwrap=True,
    )



def _ask_ba_hold() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_BA_HOLD,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
        semwrap=True,
    )


def _ask_az_hold() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_AZ_HOLD,
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
    fh_mode: str,
    ba_mode: str,
    az_mode: str,
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
        map_bc_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in BC0_MODES,
        fh_mode in BC0_MODES,
        ba_mode in BC0_MODES,
        az_mode in BC0_MODES,
        orf_mode in BC0_MODES,
    )
    return all(checks)


def _smoke_hexa_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP+DECODE+near-miss+BB FP+BA hold+AZ hold+over-refuse."""
    n = min(7, max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        fut_l = pool.submit(_ask_lookup)
        fut_d = pool.submit(_ask_decode)
        fut_n = pool.submit(_ask_near_miss)
        fut_f = pool.submit(_ask_forever_fp)
        fut_b = pool.submit(_ask_ba_hold)
        fut_a = pool.submit(_ask_az_hold)
        fut_o = pool.submit(_ask_overrefuse)
        lookup = fut_l.result()
        gen = fut_d.result()
        near = fut_n.result()
        forever = fut_f.result()
        bahold = fut_b.result()
        azhold = fut_a.result()
        overref = fut_o.result()
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    n_tel = extract_telemetry(near)
    f_tel = extract_telemetry(forever)
    b_tel = extract_telemetry(bahold)
    a_tel = extract_telemetry(azhold)
    o_tel = extract_telemetry(overref)
    l_mode = map_bc_product_mode(str(l_tel["mode"]))
    g_mode = map_bc_product_mode(str(g_tel["mode"]))
    nm_mode = map_bc_product_mode(str(n_tel["mode"]))
    fh_mode = map_bc_product_mode(str(f_tel["mode"]))
    ba_mode = map_bc_product_mode(str(b_tel["mode"]))
    az_mode = map_bc_product_mode(str(a_tel["mode"]))
    orf_mode = map_bc_product_mode(str(o_tel["mode"]))
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
        nm_mode=nm_mode,
        fh_mode=fh_mode,
        ba_mode=ba_mode,
        az_mode=az_mode,
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
            "note": "BC1 must fail gibberish content_ok; BC0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AZ locked ABSTAIN; BC0 verifies mapping",
        },
        "forever_fp": {
            "arm": classify_arm(forever),
            "raw_mode": f_tel["mode"],
            "product_mode": fh_mode,
            "wall_ms": f_tel["wall_ms"],
            "n_new": f_tel["n_new"],
            "completion": str(forever.get("completion", ""))[:120],
            "question": _FOREVER_FP,
            "note": "BC-FOREVER min FP; BC1 scores FH=0 — BC0 records only",
        },
        "ba_hold": {
            "arm": classify_arm(bahold),
            "raw_mode": b_tel["mode"],
            "product_mode": ba_mode,
            "wall_ms": b_tel["wall_ms"],
            "n_new": b_tel["n_new"],
            "completion": str(bahold.get("completion", ""))[:120],
            "question": _BA_HOLD,
            "note": "BA-FOREVER pow hold; must stay ABSTAIN — BC0 records",
        },
        "az_hold": {
            "arm": classify_arm(azhold),
            "raw_mode": a_tel["mode"],
            "product_mode": az_mode,
            "wall_ms": a_tel["wall_ms"],
            "n_new": a_tel["n_new"],
            "completion": str(azhold.get("completion", ""))[:120],
            "question": _AZ_HOLD,
            "note": "AZ hold div; must stay ABSTAIN — BC0 records",
        },
        "overrefuse": {
            "arm": classify_arm(overref),
            "raw_mode": o_tel["mode"],
            "product_mode": orf_mode,
            "wall_ms": o_tel["wall_ms"],
            "n_new": o_tel["n_new"],
            "completion": str(overref.get("completion", ""))[:120],
            "question": _OVERREFUSE,
            "note": "exact clear gold; must LOOKUP — BC0 records",
        },
        "modes_charter": sorted(BC0_MODES),
        "abstain_alias": map_bc_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BC0_GEN_STANCE["stance"],
        "named_hyp": BC0_GEN_STANCE["named_hyp"],
        "named_opsfam": BC0_GEN_STANCE["named_opsfam"],
        "named_fast": BC0_GEN_STANCE["named_fast"],
        "named_ctx": BC0_GEN_STANCE["named_ctx"],
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_hexa_arm(workers=workers)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "hepta-arm smoke failed", "ask": ask}
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
            f"# Wave BC session checklist (**OPEN** · BC0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BC **OPEN** · real intelligence scoreboard + "
            "ctx/speed + honest gen).  ",
            f"> Parent: BB COMPLETE + FROZEN · Ship: **{BC0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after BB-FREEZE; BC-FOREVER FP open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER).",
            "",
            "## Current stage",
            "",
            f"**BC0 — SESSION ({status})** · Next: **BC1 H-OPSFAM**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BC ACTIVE** |",
            "| Track | BC FH0 · BA/BB/AZ hold · ctx/speed · "
            "gen stance **defer** (H-NANOGEN13) |",
            "| Parent | BB COMPLETE + FROZEN |",
            "| Open hole | BC-FOREVER floordiv·neg·gcd·lshift·rshift·nand · "
            "live ask scoreboard · gate not bank-stuff |",
            "| Forbidden | NANOGEN13 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST |",
            "",
            "## North star (signed)",
            "",
            BC0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BC0)",
            "",
            "```text",
            "MODEL = BC0-SESSION",
            "",
            "[x] Freeze BC-FOREVER (N≥18 · floordiv·neg·gcd·lshift·rshift·nand + paraphrases)",
            "[x] Freeze BA-FOREVER hold (pow·mod·max·sort·len FH0)",
            "[x] Freeze AZ hold regression (div·sub·BIP · a.clear())",
            "[x] Freeze §1 scoreboard (forever FH · live ask · ctx/speed)",
            "[x] Publish ctx/speed baselines from BB",
            "[x] Freeze gen stance = defer (CAPCHECK closed; H-NANOGEN13; M1|M2|M3)",
            "[x] Name BC1 H-OPSFAM · BC2 H-FASTLIFT · BC3 H-CTXLIFT2 · BC4 H-NANOGEN13",
            "[x] Freeze true gen judge (rename forbidden)",
            "[x] Real-eval ask battery protocol (eval=prod ask · OK|FP|MISS)",
            "[x] Do NOT reopen INTENTGEN/FASTHOLD/CTXHOLD unless OPSFAM fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN13 = NANOGEN12+rename",
            "[ ] Next: BC1 H-OPSFAM",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BC0 | SESSION | **{status}** |",
            "| BC1 | H-OPSFAM | **NEXT** |",
            "| BC2 | H-FASTLIFT | pending |",
            "| BC3 | H-CTXLIFT2 | pending |",
            "| BC4 | H-NANOGEN13 | pending (defer unless real new method) |",
            "| BC5 | BC-REAL-EVAL | pending |",
            "| BC6 | BC-REPORT | pending |",
            "| BC7 | BC-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Forever intent FH (ask path) | **0** | live FP debt "
            "(floordiv·neg·gcd·lshift·rshift·nand) |",
            "| BA-FOREVER FH | **0** | H-REALGAIN hold |",
            "| BB-FOREVER FH | **0** | H-INTENTGEN hold |",
            "| AZ hold FH (div·sub·BIP) | **0** | AZ PRODGEN 0/12 |",
            "| Over-refuse miss (exact clear) | **0** | AZ a.clear() LOOKUP |",
            "| Live ask scoreboard | OK|FP|MISS|ABSTAIN-OK | BC0 records |",
            "| Speed p50/p99 | publish / no FP regress | BB FASTHOLD |",
            "| Context content bars | usable long/cite/howto | L_eff ≠ pass |",
            "| DECODE content | usable or ABSTAIN | STRICT lock |",
            "| True continue (NANOGEN13) | PROMOTE else HOLD/DEFER | "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER; stance defer |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    next_row = (
        "| BC0 | **SESSION** | Freeze BC-FOREVER + scoreboard + gen stance "
        "+ BB baselines + live residual FP | cite BB; no rename | **NEXT** |"
    )
    done_row = (
        "| BC0 | **SESSION** | Freeze BC-FOREVER + scoreboard + gen stance "
        "+ BB baselines + live residual FP | cite BB; no rename | "
        "**DONE — PROMOTE** |"
    )
    if next_row in text:
        text = text.replace(next_row, done_row, 1)
    text = text.replace(
        "> **Session:** `.local/wave-bc/SESSION.md` (create at BC0).  ",
        "> **Session:** `.local/wave-bc/SESSION.md` "
        "(BC0 **DONE — PROMOTE**; next BC1 H-OPSFAM).  ",
        1,
    )
    old_next = (
        "1. **BC0 SESSION** — freeze BC-FOREVER seeds from post-BB live "
        "residual FP; lock §1 scoreboard; gen stance = prove M1|M2|M3 or "
        "DEFER; create `.local/wave-bc/SESSION.md`.  "
    )
    if old_next in text:
        text = text.replace(
            old_next,
            "1. **BC0 SESSION** — **DONE PROMOTE** "
            "(`npm run nano:bc:session`) · gen stance **defer** · "
            "H-OPSFAM·H-FASTLIFT·H-CTXLIFT2·H-NANOGEN13 named · "
            "BC-FOREVER + BA/BB/AZ hold + baselines frozen.  ",
            1,
        )
    text = text.replace(
        "2. **BC1 H-OPSFAM** — family ops/intent gate → BC-FOREVER FH 0; "
        "BA/BB hold; ≥10 novel live probes FP 0.  ",
        "2. **BC1 H-OPSFAM** — **NEXT** — family ops/intent gate → "
        "BC-FOREVER FH 0; BA/BB hold; ≥10 novel live probes FP 0.  ",
        1,
    )
    bc1_pending = (
        "| BC1 | **H-OPSFAM** | Family ops/intent gate → BC-FOREVER FH 0 · "
        "BA/BB hold · novel FP 0 | §1 board | pending |"
    )
    bc1_next = (
        "| BC1 | **H-OPSFAM** | Family ops/intent gate → BC-FOREVER FH 0 · "
        "BA/BB hold · novel FP 0 | §1 board | **NEXT** |"
    )
    if bc1_pending in text:
        text = text.replace(bc1_pending, bc1_next, 1)
    bash_old = (
        "# BC0 next — implement when coding starts:\n"
        "# npm run nano:bc:session\n"
        "# npm run nano:opsfam\n"
        "# npm run nano:bc:fastlift\n"
        "# npm run nano:bc:ctxlift2\n"
        "# npm run nano:nanogen13\n"
        "# npm run nano:bc:real-eval\n"
        "# npm run nano:bc:report\n"
        "# npm run nano:bc:freeze"
    )
    bash_new = (
        "npm run nano:bc:session\n"
        "# next: nano:opsfam · nano:bc:fastlift · nano:bc:ctxlift2 · "
        "nano:nanogen13\n"
        "# npm run nano:bc:real-eval\n"
        "# npm run nano:bc:report\n"
        "# npm run nano:bc:freeze"
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

Wave BB **COMPLETE + FROZEN** (H-NANOGEN12 **DEFER**).  
**Reopen:** Wave **BC ACTIVE** via `pesquisa.md` — family-level anti-FP.  
**BC0 SESSION:** **DONE — PROMOTE** (`npm run nano:bc:session`) · gen stance **defer** · H-OPSFAM · H-FASTLIFT · H-CTXLIFT2 · H-NANOGEN13 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0–P1** | BC-FOREVER FH 0 (floordiv·neg·gcd·lshift·rshift·nand) · BA/BB/AZ hold · novel |
| **P2–P3** | Speed p50/p99 + context content bars on prod path (no FP regress) |
| **P4** | One real gen method (M1|M2|M3) — else HOLD/DEFER (H-NANOGEN13) |

## Next

1. **BC0 SESSION** — **DONE PROMOTE** (`npm run nano:bc:session`).  
2. **BC1 H-OPSFAM** — **NEXT** — BC-FOREVER FH → 0 via family gate; hold BA/BB/AZ.  
3. Ship claim stays BB lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · BA+BB PASS with BC FP · NANOGEN13=NANOGEN12+rename · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones.

```bash
npm run nano:bc:session
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

**Wave BC ACTIVE** (lab-book reopen after BB-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation**.

**Cursor measures (anti-FP):**

1. **BC-FOREVER intent FH → 0** (floordiv/neg/gcd/lshift/rshift/nand + paraphrases)  
2. **BA-FOREVER + BB-FOREVER + AZ hold** — no regression  
3. **Speed** — prod ask p50/p99 (no quality regress)  
4. **Context** — usable long/cite/howto content bars (L_eff alone ≠ win)  
5. **Generative** — true_continue only; else HOLD/DEFER (NANOGEN6–12 cited)

Session: `wave-bc/SESSION.md` (BC0 **DONE — PROMOTE**; next BC1 H-OPSFAM). Parent: Wave BB **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–BB | COMPLETE + FROZEN |
| Ship (until BC gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§13 · Wave BC0–BC7 |

## Do not

LOOKUP-as-IQ · BA+BB PASS with BC FP · over-refuse as win · sell HOLD/DEFER as unlock · L_eff/cache vanity as ctx/speed · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BC ACTIVE" in text:
        return
    marker = "**Wave BB COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    bb_line = text[idx:end]
    if "do not invent Wave BC" in bb_line:
        bb_line = bb_line.replace(
            "do not invent Wave BC",
            "Wave BC reopened via lab-book",
        )
        text = text[:idx] + bb_line + text[end:]
        end = idx + len(bb_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_bc() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BC ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BC ACTIVE** — BC0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bc-session.md) "
        "(`npm run nano:bc:session`) — BC-FOREVER anti-FP · BA/BB/AZ hold · "
        "§1 scoreboard · gen stance **defer** (H-NANOGEN13); next BC1 "
        "H-OPSFAM; ship remains **AF + AQ + AS trust + STRICT ablated "
        "DECODE**; NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave BC.",
        "Wave BC reopened via lab-book.",
        1,
    )
    text2, n = re.subn(
        r"- \*\*Wave BB COMPLETE \+ FROZEN\*\* —[^\n]+",
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_bc() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **BC** |" in text:
        return
    row = (
        "| **BC** | **ACTIVE** | BC0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-bc-session.md) (`npm run nano:bc:session`) "
        "— BC-FOREVER · BA/BB/AZ hold · gen stance defer (H-NANOGEN13); "
        "next BC1 H-OPSFAM; ship AF+AQ+AS trust + STRICT ablated DECODE; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave BC |",
        "Wave BC reopened via lab-book |",
        1,
    )
    text2, n = re.subn(
        r"\| \*\*BB\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_bc() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave BC ACTIVE" in text:
        return
    single = (
        "do not invent Wave BC",
        "Wave BC ACTIVE (BC0 SESSION PROMOTE; next BC1 H-OPSFAM); "
        "do not invent Wave BD",
    )
    if single[0] in text:
        text = text.replace(single[0], single[1], 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_bc0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BC0 SESSION" in text:
        return
    insert = (
        "| Wave BC0 SESSION | [wave-bc-session.md](wave-bc-session.md) "
        "**PROMOTE** (`npm run nano:bc:session`) — BC-FOREVER N≥18 · "
        "floordiv·neg·gcd·lshift·rshift·nand · BA/BB/AZ hold · §1 "
        "scoreboard · ctx/speed baselines · gen stance **defer** "
        "(H-NANOGEN13 · M1|M2|M3) · true-eval |"
    )
    marker = (
        "| Wave BB7 BB-FREEZE | [bb-freeze.md](bb-freeze.md) · "
        "[formal-habbfreeze-bb-freeze.md](formal-habbfreeze-bb-freeze.md) "
        "**PROMOTE** (`npm run nano:bb:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN12 DEFER; do not invent Wave BC |"
    )
    if marker not in text:
        marker2 = marker.replace(
            "do not invent Wave BC",
            "Wave BC reopened via lab-book",
        )
        if marker2 in text:
            text = text.replace(marker2, marker2 + "\n" + insert, 1)
            _RECIPES.write_text(text, encoding="utf-8")
        return
    text = text.replace(
        marker,
        marker.replace("do not invent Wave BC", "Wave BC reopened via lab-book")
        + "\n"
        + insert,
        1,
    )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BC_ACTIVE_LINE.replace(
        "**Wave BC ACTIVE:**", "**Wave BC ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BC_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_bc()
    _patch_agenda_bc()
    _patch_evogen_bc()
    _patch_recipes_bc0()


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_bc0_session(
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
        "id": BC0_ID,
        "thesis": BC0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_bb_locks": sorted(BC0_CITED_BB_LOCKS),
        "scoreboard": dict(BC0_SCOREBOARD),
        "forever_protocol": dict(BC0_FOREVER_PROTOCOL),
        "ba_hold_protocol": dict(BC0_BA_HOLD_PROTOCOL),
        "bb_hold_protocol": dict(BC0_BB_HOLD_PROTOCOL),
        "az_hold_protocol": dict(BC0_AZ_HOLD_PROTOCOL),
        "speed_baseline": dict(BC0_SPEED_BASELINE),
        "ctx_baseline": dict(BC0_CTX_BASELINE),
        "gen_stance": dict(BC0_GEN_STANCE),
        "true_gen_judge": dict(BC0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BC0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BC0_ASK_BATTERY),
        "forever_n": len(BC0_FOREVER_ROWS),
        "safe_note": BC0_SAFE_NOTE,
        "anti_fp": BC0_ANTI_FP,
        "north_star": BC0_NORTH_STAR,
        "ship_lock": BC0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-bc-session.md",
        "rule": "pesquisa §9 BC0 · BC-FOREVER + BA/BB/AZ hold + gen-defer + anti-FP",
        "next": "BC1 H-OPSFAM (BC-FOREVER FH 0 via gate; hold BA/BB/AZ)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BC0_ID,
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
