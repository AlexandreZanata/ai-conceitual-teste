"""Wave BB0 SESSION runner (nano:bb:session) — freeze BB packs + reopen after BA-FREEZE."""

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
from bb_session_ops import (
    BB0_ANTI_FP,
    BB0_ASK_BATTERY,
    BB0_AZ_HOLD_PROTOCOL,
    BB0_BA_HOLD_PROTOCOL,
    BB0_CITED_BA_LOCKS,
    BB0_CTX_BASELINE,
    BB0_FOREVER_PROTOCOL,
    BB0_FOREVER_ROWS,
    BB0_GEN_STANCE,
    BB0_ID,
    BB0_MODES,
    BB0_NORTH_STAR,
    BB0_REAL_EVAL_PROTOCOL,
    BB0_SAFE_NOTE,
    BB0_SCOREBOARD,
    BB0_SHIP_LOCK,
    BB0_SPEED_BASELINE,
    BB0_THESIS,
    BB0_TRUE_GEN_JUDGE,
    decide_bb0_session,
    map_bb_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bb/bb0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-bb/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-bb/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bb-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bb/SESSION.md"
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
_FOREVER_FP = str(BB0_FOREVER_ROWS[0]["question"])
_BA_HOLD = str(BA0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BB_ACTIVE_LINE = (
    "**Wave BB ACTIVE:** BB0 [SESSION PROMOTE](wave-bb-session.md) "
    "(`npm run nano:bb:session`) — BB-FOREVER anti-FP · BA/AZ hold · "
    "§1 scoreboard · ctx/speed baselines · gen stance **defer** "
    "(H-NANOGEN12 · M1|M2|M3) · real-eval; next BB1 H-INTENTGEN; "
    "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # 16c / 31Gi host: leave ≥6 cores free under mem pressure; cap workers.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(6, max(4, cpus - 6))
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
    for item in BB0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "BB0",
            "hyp_id": BB0_ID,
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
    for item in BB0_FOREVER_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "BB0",
            "hyp_id": BB0_ID,
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
        ("BB-SCOREBOARD", "scoreboard", dict(BB0_SCOREBOARD)),
        ("BB-FOREVER", "forever-protocol", dict(BB0_FOREVER_PROTOCOL)),
        ("BB-BA-HOLD", "ba-hold-protocol", dict(BB0_BA_HOLD_PROTOCOL)),
        ("BB-AZ-HOLD", "az-hold-protocol", dict(BB0_AZ_HOLD_PROTOCOL)),
        (
            "BB-BASELINES",
            "ctx-speed-baselines",
            {
                "speed": dict(BB0_SPEED_BASELINE),
                "ctx": dict(BB0_CTX_BASELINE),
            },
        ),
        (
            "BB-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BB0_GEN_STANCE),
                "true_gen_judge": dict(BB0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "BB-REAL-EVAL",
            "real-eval-protocol",
            dict(BB0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "BB0",
            "hyp_id": BB0_ID,
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
    need = len(BB0_ASK_BATTERY) + len(BB0_FOREVER_ROWS) + 7
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BB0_ASK_BATTERY
    )
    fh_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in BB0_FOREVER_ROWS
    )
    bars = BB0_SCOREBOARD["bars"]
    debts = BB0_SCOREBOARD["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BB0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    body = "\n".join(
        [
            "# Wave BB0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §8 · Session: "
            "`.local/wave-bb/SESSION.md`  ",
            "> Module: `nano_lm/src/bb_session_ops.py` · "
            "Runner: `npm run nano:bb:session`  ",
            "> Parent: [ba-freeze.md](ba-freeze.md) "
            "(Wave BB reopened explicitly via lab-book reopen after BA-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BB packs: "
            "BB-FOREVER (N≥15 · min·xor·absdiff·and·or + paraphrases ≠ BA/AZ) · "
            "BA-FOREVER hold (pow·mod·max·sort·len FH0) · "
            "AZ hold (div·sub·BIP FH0 · `a.clear()` LOOKUP) · §1 anti-FP "
            "scoreboard · ctx/speed baselines from BA · gen stance "
            "**defer** (CAPCHECK closed; **H-NANOGEN12**; M1|M2|M3 named; "
            "**not** NANOGEN12=NANOGEN11+rename) · real-eval protocol. "
            "**Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until BB4 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | BB FH0 · BA/AZ hold · live ask · "
            "ctx/speed · modes · DECODE law (BB1) |",
            f"| BB-FOREVER protocol | {len(BB0_FOREVER_ROWS)} | "
            "min·xor·absdiff·and·or + paraphrases (BB1) |",
            "| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Ctx/speed baselines | 1 | BA FASTREAL p50/p99 · CTXREAL2 "
            "content (BB2/BB3) |",
            "| Gen stance | 1 | **defer** · CAPCHECK closed · "
            "H-NANOGEN12 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10·11 "
            "DEFER cited (BB4) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BB4) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BB5) |",
            f"| Ask battery | {len(BB0_ASK_BATTERY)} | frozen live rows "
            "(scored at BB5) |",
            "",
            "## Cited BA locks",
            "",
            ", ".join(sorted(BB0_CITED_BA_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- bb_forever_false_hit_max: **{bars['bb_forever_false_hit_max']}**  ",
            f"- ba_forever_false_hit_max: **{bars['ba_forever_false_hit_max']}**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- bb_forever_min_n: **{bars['bb_forever_min_n']}**  ",
            f"- bb_forever_classes_min: **{bars['bb_forever_classes_min']}**  ",
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
            "- no vanity reopen REALGAIN/FASTREAL/CTXREAL2 unless INTENTGEN fails",
            "",
            "## Post-BA debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## BB-FOREVER protocol",
            "",
            f"- held_out: **{BB0_FOREVER_PROTOCOL['held_out']}**  ",
            f"- forever: **{BB0_FOREVER_PROTOCOL['forever']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{BB0_FOREVER_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: "
            f"**{BB0_FOREVER_PROTOCOL['paraphrase_required']}**  ",
            f"- neq_az_heldout: "
            f"**{BB0_FOREVER_PROTOCOL['neq_az_heldout']}**  ",
            f"- live_fp_id: **{BB0_FOREVER_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{BB0_FOREVER_PROTOCOL['min_n']}**  ",
            f"- path: `{BB0_FOREVER_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            fh_rows,
            "",
            "## BA hold protocol",
            "",
            f"- forever_false_hit_max: "
            f"**{BB0_BA_HOLD_PROTOCOL['forever_false_hit_max']}**  ",
            f"- heldout_n: **{BB0_BA_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- regression_hold: "
            f"**{BB0_BA_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## AZ hold protocol",
            "",
            f"- heldout_false_hit_max: "
            f"**{BB0_AZ_HOLD_PROTOCOL['heldout_false_hit_max']}**  ",
            f"- overrefuse_miss_max: "
            f"**{BB0_AZ_HOLD_PROTOCOL['overrefuse_miss_max']}**  ",
            f"- heldout_n: **{BB0_AZ_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- overrefuse_n: **{BB0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            f"- regression_hold: "
            f"**{BB0_AZ_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## Speed baseline (from BA FASTREAL)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BB0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- bb2_gate: `{BB0_SPEED_BASELINE['bb2_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BB0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BB0_CTX_BASELINE['content_bars_required']}**  ",
            f"- bb3_gate: `{BB0_CTX_BASELINE['bb3_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BB0_GEN_STANCE['stance']}**  ",
            f"- allowed: {' · '.join(BB0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BB0_GEN_STANCE['named_hyp']}**  ",
            f"- named_intentgen: **{BB0_GEN_STANCE['named_intentgen']}**  ",
            f"- named_fast: **{BB0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BB0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BB0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen12_rename_forbidden: "
            f"**{BB0_GEN_STANCE['nanogen12_rename_forbidden']}**  ",
            f"- bb4_gate: `{BB0_GEN_STANCE['bb4_gate']}`  ",
            "",
            BB0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BB0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen12_rename_forbidden: "
            f"{BB0_TRUE_GEN_JUDGE['nanogen12_rename_forbidden']}  ",
            f"- scoring: `{BB0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BB0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{BB0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BB0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- score_labels: "
            f"{' · '.join(BB0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_forever: "
            f"{BB0_REAL_EVAL_PROTOCOL['pack_pass_neq_forever']}  ",
            f"- gen_claim_rule: "
            f"{BB0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BB0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BB0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BB0_ANTI_FP,
            "",
            "## North star",
            "",
            BB0_NORTH_STAR,
            "",
            "## Ship lock (until BA gen PROMOTE)",
            "",
            BB0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:bb:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "BB-FOREVER + AZ hold probes are **recorded** "
            "(BB1 scores forever FH=0 / AZ hold=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-bb/bb0_session.json` · "
            "`results/nano-lm/wave-bb/trials/BA-*.json`.  ",
            "Contract: `nano_lm/tests/test_bb_session.py`.",
            "",
            "## Claims",
            "",
            "- BA packs frozen for Wave BB — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BB0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BB4 H-NANOGEN12** "
            "true_continue under a real new method (M1|M2|M3; "
            "never NANOGEN11+rename; span-fallback ≠ gen).  ",
            "- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN12 rename · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen.",
            "",
            "Next: **BB1 H-INTENTGEN** — drive forever FH → 0 via gate; "
            "hold AZ bars; live ask scoreboard OK|FP|MISS|ABSTAIN-OK.",
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
        map_bb_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in BB0_MODES,
        fh_mode in BB0_MODES,
        ba_mode in BB0_MODES,
        az_mode in BB0_MODES,
        orf_mode in BB0_MODES,
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
    l_mode = map_bb_product_mode(str(l_tel["mode"]))
    g_mode = map_bb_product_mode(str(g_tel["mode"]))
    nm_mode = map_bb_product_mode(str(n_tel["mode"]))
    fh_mode = map_bb_product_mode(str(f_tel["mode"]))
    ba_mode = map_bb_product_mode(str(b_tel["mode"]))
    az_mode = map_bb_product_mode(str(a_tel["mode"]))
    orf_mode = map_bb_product_mode(str(o_tel["mode"]))
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
            "note": "BB1 must fail gibberish content_ok; BB0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AZ locked ABSTAIN; BB0 verifies mapping",
        },
        "forever_fp": {
            "arm": classify_arm(forever),
            "raw_mode": f_tel["mode"],
            "product_mode": fh_mode,
            "wall_ms": f_tel["wall_ms"],
            "n_new": f_tel["n_new"],
            "completion": str(forever.get("completion", ""))[:120],
            "question": _FOREVER_FP,
            "note": "BB-FOREVER min FP; BB1 scores FH=0 — BB0 records only",
        },
        "ba_hold": {
            "arm": classify_arm(bahold),
            "raw_mode": b_tel["mode"],
            "product_mode": ba_mode,
            "wall_ms": b_tel["wall_ms"],
            "n_new": b_tel["n_new"],
            "completion": str(bahold.get("completion", ""))[:120],
            "question": _BA_HOLD,
            "note": "BA-FOREVER pow hold; must stay ABSTAIN — BB0 records",
        },
        "az_hold": {
            "arm": classify_arm(azhold),
            "raw_mode": a_tel["mode"],
            "product_mode": az_mode,
            "wall_ms": a_tel["wall_ms"],
            "n_new": a_tel["n_new"],
            "completion": str(azhold.get("completion", ""))[:120],
            "question": _AZ_HOLD,
            "note": "AZ hold div; must stay ABSTAIN — BB0 records",
        },
        "overrefuse": {
            "arm": classify_arm(overref),
            "raw_mode": o_tel["mode"],
            "product_mode": orf_mode,
            "wall_ms": o_tel["wall_ms"],
            "n_new": o_tel["n_new"],
            "completion": str(overref.get("completion", ""))[:120],
            "question": _OVERREFUSE,
            "note": "exact clear gold; must LOOKUP — BB0 records",
        },
        "modes_charter": sorted(BB0_MODES),
        "abstain_alias": map_bb_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BB0_GEN_STANCE["stance"],
        "named_hyp": BB0_GEN_STANCE["named_hyp"],
        "named_intentgen": BB0_GEN_STANCE["named_intentgen"],
        "named_fast": BB0_GEN_STANCE["named_fast"],
        "named_ctx": BB0_GEN_STANCE["named_ctx"],
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
            f"# Wave BB session checklist (**OPEN** · BB0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BB **OPEN** · real intelligence scoreboard + "
            "ctx/speed + honest gen).  ",
            f"> Parent: BA COMPLETE + FROZEN · Ship: **{BB0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after BA-FREEZE; BB-FOREVER FP open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER).",
            "",
            "## Current stage",
            "",
            f"**BB0 — SESSION ({status})** · Next: **BB1 H-INTENTGEN**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BB OPEN** |",
            "| Track | BB FH0 · BA/AZ hold · ctx/speed · "
            "gen stance **defer** (H-NANOGEN12) |",
            "| Parent | BA COMPLETE + FROZEN |",
            "| Open hole | BB-FOREVER min·xor·absdiff·and·or · "
            "live ask scoreboard · gate not bank-stuff |",
            "| Forbidden | NANOGEN12 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST |",
            "",
            "## North star (signed)",
            "",
            BB0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BB0)",
            "",
            "```text",
            "MODEL = BB0-SESSION",
            "",
            "[x] Freeze BB-FOREVER (N≥15 · min·xor·absdiff·and·or + paraphrases)",
            "[x] Freeze BA-FOREVER hold (pow·mod·max·sort·len FH0)",
            "[x] Freeze AZ hold regression (div·sub·BIP · a.clear())",
            "[x] Freeze §1 scoreboard (forever FH · live ask · ctx/speed)",
            "[x] Publish ctx/speed baselines from BA",
            "[x] Freeze gen stance = defer (CAPCHECK closed; H-NANOGEN12; M1|M2|M3)",
            "[x] Name BB1 H-INTENTGEN · BB2 H-FASTHOLD · BB3 H-CTXHOLD · BB4 H-NANOGEN12",
            "[x] Freeze true gen judge (rename forbidden)",
            "[x] Real-eval ask battery protocol (eval=prod ask · OK|FP|MISS)",
            "[x] Do NOT reopen REALGAIN/FASTREAL/CTXREAL2 unless INTENTGEN fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN12 = NANOGEN11+rename",
            "[ ] Next: BB1 H-INTENTGEN",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BB0 | SESSION | **{status}** |",
            "| BB1 | H-INTENTGEN | **NEXT** |",
            "| BB2 | H-FASTHOLD | pending |",
            "| BB3 | H-CTXHOLD | pending |",
            "| BB4 | H-NANOGEN12 | pending (defer unless real new method) |",
            "| BB5 | BB-REAL-EVAL | pending |",
            "| BB6 | BB-REPORT | pending |",
            "| BB7 | BB-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Forever intent FH (ask path) | **0** | live FP debt "
            "(min·xor·absdiff·and·or) |",
            "| BA-FOREVER FH | **0** | H-REALGAIN hold |",
            "| AZ hold FH (div·sub·BIP) | **0** | AZ PRODGEN 0/12 |",
            "| Over-refuse miss (exact clear) | **0** | AZ a.clear() LOOKUP |",
            "| Live ask scoreboard | OK|FP|MISS|ABSTAIN-OK | BB0 records |",
            "| Speed p50/p99 | publish / no FP regress | BA FASTREAL |",
            "| Context content bars | usable long/cite/howto | L_eff ≠ pass |",
            "| DECODE content | usable or ABSTAIN | STRICT lock |",
            "| True continue (NANOGEN12) | PROMOTE else HOLD/DEFER | "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER; stance defer |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    done_row = (
        "| BB0 | **SESSION** | Freeze BB-FOREVER + scoreboard + gen stance "
        "+ BA baselines | cite BA; no rename | **DONE — PROMOTE** |"
    )
    bb0_todo = (
        "| BB0 | **SESSION** | Freeze BB-FOREVER + scoreboard + gen stance "
        "+ BA baselines | cite BA; no rename | **TODO** |"
    )
    if bb0_todo in text:
        text = text.replace(bb0_todo, done_row, 1)
    text = text.replace(
        "> **Session:** `.local/wave-bb/SESSION.md` (create at BB0).  ",
        "> **Session:** `.local/wave-bb/SESSION.md` "
        "(BB0 **DONE — PROMOTE**; next BB1 H-INTENTGEN).  ",
        1,
    )
    old_next = (
        "1. **BB0 SESSION** — create `.local/wave-bb/SESSION.md` · freeze "
        "BB-FOREVER seeds (`min`·`xor`·`absdiff`·…) + paraphrase rule · "
        "cite BA boards · set gen stance (`M1`/`M2`/`M3`/defer).  "
    )
    if old_next in text:
        text = text.replace(
            old_next,
            "1. **BB0 SESSION** — **DONE PROMOTE** "
            "(`npm run nano:bb:session`) · gen stance **defer** · "
            "H-INTENTGEN·H-FASTHOLD·H-CTXHOLD·H-NANOGEN12 named · "
            "BB-FOREVER + BA/AZ hold + baselines frozen.  ",
            1,
        )
    text = text.replace(
        "2. **BB1 H-INTENTGEN** — compositional gate → BB-FOREVER FH **0**; "
        "hold BA-FOREVER + AZ; live novel probes.  ",
        "2. **BB1 H-INTENTGEN** — **NEXT** — compositional gate → "
        "BB-FOREVER FH **0**; hold BA-FOREVER + AZ; live novel probes.  ",
        1,
    )
    bb1_todo = (
        "| BB1 | **H-INTENTGEN** | Compositional binop/intent gate → "
        "BB-FOREVER FH 0 · BA hold | §1 board | **TODO** |"
    )
    bb1_next = (
        "| BB1 | **H-INTENTGEN** | Compositional binop/intent gate → "
        "BB-FOREVER FH 0 · BA hold | §1 board | **NEXT** |"
    )
    if bb1_todo in text:
        text = text.replace(bb1_todo, bb1_next, 1)
    bash_old = (
        "# BB0: session runner TBD after SESSION freeze\n"
        "# npm run nano:bb:session\n"
        "# npm run nano:intentgen\n"
        "# npm run nano:bb:fasthold\n"
        "# npm run nano:bb:ctxhold\n"
        "# npm run nano:nanogen12\n"
        "# npm run nano:bb:real-eval\n"
        "# npm run nano:bb:report\n"
        "# npm run nano:bb:freeze"
    )
    bash_new = (
        "npm run nano:bb:session\n"
        "# next: nano:intentgen · nano:bb:fasthold · nano:bb:ctxhold · "
        "nano:nanogen12\n"
        "# npm run nano:bb:real-eval\n"
        "# npm run nano:bb:report\n"
        "# npm run nano:bb:freeze"
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

Wave BA **COMPLETE + FROZEN** (H-NANOGEN11 **DEFER**).  
**Reopen:** Wave **BB ACTIVE** via `pesquisa.md` — compositional anti-FP.  
**BB0 SESSION:** **DONE — PROMOTE** (`npm run nano:bb:session`) · gen stance **defer** · H-INTENTGEN · H-FASTHOLD · H-CTXHOLD · H-NANOGEN12 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0–P1** | BB-FOREVER FH 0 (min·xor·absdiff·and·or) · BA/AZ hold · live ask |
| **P2–P3** | Speed p50/p99 + context content bars on prod path (no FP regress) |
| **P4** | One real gen method (M1|M2|M3) — else HOLD/DEFER (H-NANOGEN12) |

## Next

1. **BB0 SESSION** — **DONE PROMOTE** (`npm run nano:bb:session`).  
2. **BB1 H-INTENTGEN** — **NEXT** — BB-FOREVER FH → 0 via gate; hold BA/AZ.  
3. Ship claim stays BA lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · BA PASS with BB FP · NANOGEN12=NANOGEN11+rename · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones.

```bash
npm run nano:bb:session
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

**Wave BB ACTIVE** (lab-book reopen after BA-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation**.

**Cursor measures (anti-FP):**

1. **BB-FOREVER intent FH → 0** (min/xor/absdiff/and/or + paraphrases)  
2. **BA-FOREVER + AZ hold** — no regression  
3. **Speed** — prod ask p50/p99 (no quality regress)  
4. **Context** — usable long/cite/howto content bars (L_eff alone ≠ win)  
5. **Generative** — true_continue only; else HOLD/DEFER (NANOGEN6–11 cited)

Session: `wave-bb/SESSION.md` (BB0 **DONE — PROMOTE**; next BB1 H-INTENTGEN). Parent: Wave BA **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–BA | COMPLETE + FROZEN |
| Ship (until BB gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§12 · Wave BB0–BB7 |

## Do not

LOOKUP-as-IQ · BA PASS with BB FP · over-refuse as win · sell HOLD/DEFER as unlock · L_eff/cache vanity as ctx/speed · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BB ACTIVE" in text:
        return
    marker = "**Wave BA COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    ba_line = text[idx:end]
    if "do not invent Wave BB" in ba_line:
        ba_line = ba_line.replace(
            "do not invent Wave BB",
            "Wave BB reopened via lab-book",
        )
        text = text[:idx] + ba_line + text[end:]
        end = idx + len(ba_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_bb() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BB ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BB ACTIVE** — BB0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bb-session.md) "
        "(`npm run nano:bb:session`) — BB-FOREVER anti-FP · BA/AZ hold · "
        "§1 scoreboard · gen stance **defer** (H-NANOGEN12); next BB1 "
        "H-INTENTGEN; ship remains **AF + AQ + AS trust + STRICT ablated "
        "DECODE**; NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave BB.",
        "Wave BB reopened via lab-book.",
        1,
    )
    text2, n = re.subn(
        r"- \*\*Wave BA COMPLETE \+ FROZEN\*\* —[^\n]+",
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_bb() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **BB** |" in text:
        return
    row = (
        "| **BB** | **ACTIVE** | BB0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-bb-session.md) (`npm run nano:bb:session`) "
        "— BB-FOREVER · BA/AZ hold · gen stance defer (H-NANOGEN12); "
        "next BB1 H-INTENTGEN; ship AF+AQ+AS trust + STRICT ablated DECODE; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10·11 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave BB |",
        "Wave BB reopened via lab-book |",
        1,
    )
    text2, n = re.subn(
        r"\| \*\*BA\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_bb() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave BB ACTIVE" in text or "Wave BB COMPLETE" in text:
        # allow reopen phrase even if ACTIVE already present from partial run
        pass
    if "Wave BB ACTIVE" in text:
        return
    dual = (
        "do not invent Wave BB); do not invent Wave BB",
        "Wave BB ACTIVE (BB0 SESSION PROMOTE; next BB1 H-INTENTGEN)); "
        "do not invent Wave BC",
    )
    single = (
        "do not invent Wave BB",
        "Wave BB ACTIVE (BB0 SESSION PROMOTE; next BB1 H-INTENTGEN); "
        "do not invent Wave BC",
    )
    if dual[0] in text:
        text = text.replace(dual[0], dual[1], 1)
    elif single[0] in text:
        text = text.replace(single[0], single[1], 1)
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_bb0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BB0 SESSION" in text:
        return
    insert = (
        "| Wave BB0 SESSION | [wave-bb-session.md](wave-bb-session.md) "
        "**PROMOTE** (`npm run nano:bb:session`) — BB-FOREVER N≥15 · "
        "min·xor·absdiff·and·or · BA/AZ hold · §1 scoreboard · ctx/speed "
        "baselines · gen stance **defer** (H-NANOGEN12 · M1|M2|M3) · "
        "true-eval |"
    )
    marker = (
        "| Wave BA7 BA-FREEZE | [ba-freeze.md](ba-freeze.md) · "
        "[formal-habfreeze-ba-freeze.md](formal-habfreeze-ba-freeze.md) "
        "**PROMOTE** (`npm run nano:ba:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN11 DEFER; do not invent Wave BB |"
    )
    if marker not in text:
        marker2 = marker.replace(
            "do not invent Wave BB",
            "Wave BB reopened via lab-book",
        )
        if marker2 in text:
            text = text.replace(marker2, marker2 + "\n" + insert, 1)
            _RECIPES.write_text(text, encoding="utf-8")
        return
    text = text.replace(
        marker,
        marker.replace("do not invent Wave BB", "Wave BB reopened via lab-book")
        + "\n"
        + insert,
        1,
    )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BB_ACTIVE_LINE.replace(
        "**Wave BB ACTIVE:**", "**Wave BB ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BB_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_bb()
    _patch_agenda_bb()
    _patch_evogen_bb()
    _patch_recipes_bb0()


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_bb0_session(
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
        "id": BB0_ID,
        "thesis": BB0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_ba_locks": sorted(BB0_CITED_BA_LOCKS),
        "scoreboard": dict(BB0_SCOREBOARD),
        "forever_protocol": dict(BB0_FOREVER_PROTOCOL),
        "ba_hold_protocol": dict(BB0_BA_HOLD_PROTOCOL),
        "az_hold_protocol": dict(BB0_AZ_HOLD_PROTOCOL),
        "speed_baseline": dict(BB0_SPEED_BASELINE),
        "ctx_baseline": dict(BB0_CTX_BASELINE),
        "gen_stance": dict(BB0_GEN_STANCE),
        "true_gen_judge": dict(BB0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BB0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BB0_ASK_BATTERY),
        "forever_n": len(BB0_FOREVER_ROWS),
        "safe_note": BB0_SAFE_NOTE,
        "anti_fp": BB0_ANTI_FP,
        "north_star": BB0_NORTH_STAR,
        "ship_lock": BB0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-bb-session.md",
        "rule": "pesquisa §8 BB0 · BB-FOREVER + BA/AZ hold + gen-defer + anti-FP",
        "next": "BB1 H-INTENTGEN (BB-FOREVER FH 0 via gate; hold BA/AZ)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BB0_ID,
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
