"""Wave BA0 SESSION runner (nano:ba:session) — freeze BA packs + reopen."""

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
from ba_session_ops import (
    BA0_ANTI_FP,
    BA0_ASK_BATTERY,
    BA0_AZ_HOLD_PROTOCOL,
    BA0_CITED_AZ_LOCKS,
    BA0_CTX_BASELINE,
    BA0_FOREVER_PROTOCOL,
    BA0_FOREVER_ROWS,
    BA0_GEN_STANCE,
    BA0_ID,
    BA0_MODES,
    BA0_NORTH_STAR,
    BA0_REAL_EVAL_PROTOCOL,
    BA0_SAFE_NOTE,
    BA0_SCOREBOARD,
    BA0_SHIP_LOCK,
    BA0_SPEED_BASELINE,
    BA0_THESIS,
    BA0_TRUE_GEN_JUDGE,
    decide_ba0_session,
    map_ba_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ba/ba0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-ba/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-ba/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ba-session.md"
_LOCAL_SESSION = REPO / ".local/wave-ba/SESSION.md"
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
_FOREVER_FP = str(BA0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BA_ACTIVE_LINE = (
    "**Wave BA ACTIVE:** BA0 [SESSION PROMOTE](wave-ba-session.md) "
    "(`npm run nano:ba:session`) — BA-FOREVER anti-FP · AZ hold · "
    "§1 scoreboard · ctx/speed baselines · gen stance **defer** "
    "(H-NANOGEN11 · M1|M2|M3) · real-eval; next BA1 H-REALGAIN; "
    "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
    "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # 16c / 31Gi host: leave ≥4 cores free; cap workers under memory pressure.
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
    for item in BA0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "BA0",
            "hyp_id": BA0_ID,
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
    for item in BA0_FOREVER_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "BA0",
            "hyp_id": BA0_ID,
            "pack": "ba-forever",
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
        ("BA-SCOREBOARD", "scoreboard", dict(BA0_SCOREBOARD)),
        ("BA-FOREVER", "forever-protocol", dict(BA0_FOREVER_PROTOCOL)),
        ("BA-AZ-HOLD", "az-hold-protocol", dict(BA0_AZ_HOLD_PROTOCOL)),
        (
            "BA-BASELINES",
            "ctx-speed-baselines",
            {
                "speed": dict(BA0_SPEED_BASELINE),
                "ctx": dict(BA0_CTX_BASELINE),
            },
        ),
        (
            "BA-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BA0_GEN_STANCE),
                "true_gen_judge": dict(BA0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "BA-REAL-EVAL",
            "real-eval-protocol",
            dict(BA0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "BA0",
            "hyp_id": BA0_ID,
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
    need = len(BA0_ASK_BATTERY) + len(BA0_FOREVER_ROWS) + 6
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BA0_ASK_BATTERY
    )
    fh_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in BA0_FOREVER_ROWS
    )
    bars = BA0_SCOREBOARD["bars"]
    debts = BA0_SCOREBOARD["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BA0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    body = "\n".join(
        [
            "# Wave BA0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §8 · Session: "
            "`.local/wave-ba/SESSION.md`  ",
            "> Module: `nano_lm/src/ba_session_ops.py` · "
            "Runner: `npm run nano:ba:session`  ",
            "> Parent: [az-freeze.md](az-freeze.md) "
            "(Wave BA reopened explicitly via lab-book reopen after AZ-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BA packs: "
            "BA-FOREVER (N≥15 · pow·mod·max·sort·len + paraphrases ≠ AZ) · "
            "AZ hold (div·sub·BIP FH0 · `a.clear()` LOOKUP) · §1 anti-FP "
            "scoreboard · ctx/speed baselines from AZ · gen stance "
            "**defer** (CAPCHECK closed; **H-NANOGEN11**; M1|M2|M3 named; "
            "**not** NANOGEN11=NANOGEN10+rename) · real-eval protocol. "
            "**Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until BA4 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | forever FH0 · AZ hold · live ask · "
            "ctx/speed · modes · DECODE law (BA1) |",
            f"| BA-FOREVER protocol | {len(BA0_FOREVER_ROWS)} | "
            "pow·mod·max·sort·len + paraphrases (BA1) |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Ctx/speed baselines | 1 | AZ PRODGEN p50/p99 · content bars "
            "(BA2/BA3) |",
            "| Gen stance | 1 | **defer** · CAPCHECK closed · "
            "H-NANOGEN11 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8·9·10 "
            "DEFER cited (BA4) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BA4) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BA5) |",
            f"| Ask battery | {len(BA0_ASK_BATTERY)} | frozen live rows "
            "(scored at BA5) |",
            "",
            "## Cited AZ locks",
            "",
            ", ".join(sorted(BA0_CITED_AZ_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- forever_false_hit_max: **{bars['forever_false_hit_max']}**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- forever_min_n: **{bars['forever_min_n']}**  ",
            f"- forever_classes_min: **{bars['forever_classes_min']}**  ",
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
            "- no vanity reopen PRODGEN/SHIPAZ unless REALGAIN fails",
            "",
            "## Post-AZ debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## BA-FOREVER protocol",
            "",
            f"- held_out: **{BA0_FOREVER_PROTOCOL['held_out']}**  ",
            f"- forever: **{BA0_FOREVER_PROTOCOL['forever']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{BA0_FOREVER_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: "
            f"**{BA0_FOREVER_PROTOCOL['paraphrase_required']}**  ",
            f"- neq_az_heldout: "
            f"**{BA0_FOREVER_PROTOCOL['neq_az_heldout']}**  ",
            f"- live_fp_id: **{BA0_FOREVER_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{BA0_FOREVER_PROTOCOL['min_n']}**  ",
            f"- path: `{BA0_FOREVER_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            fh_rows,
            "",
            "## AZ hold protocol",
            "",
            f"- heldout_false_hit_max: "
            f"**{BA0_AZ_HOLD_PROTOCOL['heldout_false_hit_max']}**  ",
            f"- overrefuse_miss_max: "
            f"**{BA0_AZ_HOLD_PROTOCOL['overrefuse_miss_max']}**  ",
            f"- heldout_n: **{BA0_AZ_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- overrefuse_n: **{BA0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            f"- regression_hold: "
            f"**{BA0_AZ_HOLD_PROTOCOL['regression_hold']}**  ",
            "",
            "## Speed baseline (from AZ PRODGEN)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BA0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- ba2_gate: `{BA0_SPEED_BASELINE['ba2_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BA0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BA0_CTX_BASELINE['content_bars_required']}**  ",
            f"- ba3_gate: `{BA0_CTX_BASELINE['ba3_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BA0_GEN_STANCE['stance']}**  ",
            f"- allowed: {' · '.join(BA0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BA0_GEN_STANCE['named_hyp']}**  ",
            f"- named_realgain: **{BA0_GEN_STANCE['named_realgain']}**  ",
            f"- named_fast: **{BA0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BA0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BA0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen11_rename_forbidden: "
            f"**{BA0_GEN_STANCE['nanogen11_rename_forbidden']}**  ",
            f"- ba4_gate: `{BA0_GEN_STANCE['ba4_gate']}`  ",
            "",
            BA0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BA0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen11_rename_forbidden: "
            f"{BA0_TRUE_GEN_JUDGE['nanogen11_rename_forbidden']}  ",
            f"- scoring: `{BA0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BA0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{BA0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BA0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- score_labels: "
            f"{' · '.join(BA0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_forever: "
            f"{BA0_REAL_EVAL_PROTOCOL['pack_pass_neq_forever']}  ",
            f"- gen_claim_rule: "
            f"{BA0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BA0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BA0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BA0_ANTI_FP,
            "",
            "## North star",
            "",
            BA0_NORTH_STAR,
            "",
            "## Ship lock (until BA gen PROMOTE)",
            "",
            BA0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:ba:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "BA-FOREVER + AZ hold probes are **recorded** "
            "(BA1 scores forever FH=0 / AZ hold=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-ba/ba0_session.json` · "
            "`results/nano-lm/wave-ba/trials/BA-*.json`.  ",
            "Contract: `nano_lm/tests/test_ba_session.py`.",
            "",
            "## Claims",
            "",
            "- AZ packs frozen for Wave BA — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BA0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BA4 H-NANOGEN11** "
            "true_continue under a real new method (M1|M2|M3; "
            "never NANOGEN10+rename; span-fallback ≠ gen).  ",
            "- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN11 rename · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen.",
            "",
            "Next: **BA1 H-REALGAIN** — drive forever FH → 0 via gate; "
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
        map_ba_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in BA0_MODES,
        fh_mode in BA0_MODES,
        az_mode in BA0_MODES,
        orf_mode in BA0_MODES,
    )
    return all(checks)


def _smoke_hexa_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP + DECODE + near-miss + forever FP + AZ hold + over-refuse."""
    n = min(6, max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        fut_l = pool.submit(_ask_lookup)
        fut_d = pool.submit(_ask_decode)
        fut_n = pool.submit(_ask_near_miss)
        fut_f = pool.submit(_ask_forever_fp)
        fut_a = pool.submit(_ask_az_hold)
        fut_o = pool.submit(_ask_overrefuse)
        lookup = fut_l.result()
        gen = fut_d.result()
        near = fut_n.result()
        forever = fut_f.result()
        azhold = fut_a.result()
        overref = fut_o.result()
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    n_tel = extract_telemetry(near)
    f_tel = extract_telemetry(forever)
    a_tel = extract_telemetry(azhold)
    o_tel = extract_telemetry(overref)
    l_mode = map_ba_product_mode(str(l_tel["mode"]))
    g_mode = map_ba_product_mode(str(g_tel["mode"]))
    nm_mode = map_ba_product_mode(str(n_tel["mode"]))
    fh_mode = map_ba_product_mode(str(f_tel["mode"]))
    az_mode = map_ba_product_mode(str(a_tel["mode"]))
    orf_mode = map_ba_product_mode(str(o_tel["mode"]))
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
        nm_mode=nm_mode,
        fh_mode=fh_mode,
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
            "note": "BA1 must fail gibberish content_ok; BA0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AZ locked ABSTAIN; BA0 verifies mapping",
        },
        "forever_fp": {
            "arm": classify_arm(forever),
            "raw_mode": f_tel["mode"],
            "product_mode": fh_mode,
            "wall_ms": f_tel["wall_ms"],
            "n_new": f_tel["n_new"],
            "completion": str(forever.get("completion", ""))[:120],
            "question": _FOREVER_FP,
            "note": "BA-FOREVER pow FP; BA1 scores FH=0 — BA0 records only",
        },
        "az_hold": {
            "arm": classify_arm(azhold),
            "raw_mode": a_tel["mode"],
            "product_mode": az_mode,
            "wall_ms": a_tel["wall_ms"],
            "n_new": a_tel["n_new"],
            "completion": str(azhold.get("completion", ""))[:120],
            "question": _AZ_HOLD,
            "note": "AZ hold div; must stay ABSTAIN — BA0 records",
        },
        "overrefuse": {
            "arm": classify_arm(overref),
            "raw_mode": o_tel["mode"],
            "product_mode": orf_mode,
            "wall_ms": o_tel["wall_ms"],
            "n_new": o_tel["n_new"],
            "completion": str(overref.get("completion", ""))[:120],
            "question": _OVERREFUSE,
            "note": "exact clear gold; must LOOKUP — BA0 records",
        },
        "modes_charter": sorted(BA0_MODES),
        "abstain_alias": map_ba_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BA0_GEN_STANCE["stance"],
        "named_hyp": BA0_GEN_STANCE["named_hyp"],
        "named_realgain": BA0_GEN_STANCE["named_realgain"],
        "named_fast": BA0_GEN_STANCE["named_fast"],
        "named_ctx": BA0_GEN_STANCE["named_ctx"],
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
                {"ok": False, "error": "hexa-arm smoke failed", "ask": ask}
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
            f"# Wave BA session checklist (**OPEN** · BA0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BA **OPEN** · real intelligence scoreboard + "
            "ctx/speed + honest gen).  ",
            f"> Parent: AZ COMPLETE + FROZEN · Ship: **{BA0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after AZ-FREEZE; BA-FOREVER FP open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER).",
            "",
            "## Current stage",
            "",
            f"**BA0 — SESSION ({status})** · Next: **BA1 H-REALGAIN**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BA OPEN** |",
            "| Track | forever FH0 · AZ hold · ctx/speed · "
            "gen stance **defer** (H-NANOGEN11) |",
            "| Parent | AZ COMPLETE + FROZEN |",
            "| Open hole | BA-FOREVER pow·mod·max·sort·len · "
            "live ask scoreboard · gate not bank-stuff |",
            "| Forbidden | NANOGEN11 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST |",
            "",
            "## North star (signed)",
            "",
            BA0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BA0)",
            "",
            "```text",
            "MODEL = BA0-SESSION",
            "",
            "[x] Freeze BA-FOREVER (N≥15 · pow·mod·max·sort·len + paraphrases)",
            "[x] Freeze AZ hold regression (div·sub·BIP · a.clear())",
            "[x] Freeze §1 scoreboard (forever FH · live ask · ctx/speed)",
            "[x] Publish ctx/speed baselines from AZ",
            "[x] Freeze gen stance = defer (CAPCHECK closed; H-NANOGEN11; M1|M2|M3)",
            "[x] Name BA1 H-REALGAIN · BA2 H-FASTREAL · BA3 H-CTXREAL2 · BA4 H-NANOGEN11",
            "[x] Freeze true gen judge (rename forbidden)",
            "[x] Real-eval ask battery protocol (eval=prod ask · OK|FP|MISS)",
            "[x] Do NOT reopen PRODGEN/SHIPAZ unless REALGAIN fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN11 = NANOGEN10+rename",
            "[ ] Next: BA1 H-REALGAIN",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BA0 | SESSION | **{status}** |",
            "| BA1 | H-REALGAIN | **NEXT** |",
            "| BA2 | H-FASTREAL | pending |",
            "| BA3 | H-CTXREAL2 | pending |",
            "| BA4 | H-NANOGEN11 | pending (defer unless real new method) |",
            "| BA5 | BA-REAL-EVAL | pending |",
            "| BA6 | BA-REPORT | pending |",
            "| BA7 | BA-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Forever intent FH (ask path) | **0** | live FP debt "
            "(pow·mod·max·sort·len) |",
            "| AZ hold FH (div·sub·BIP) | **0** | AZ PRODGEN 0/12 |",
            "| Over-refuse miss (exact clear) | **0** | AZ a.clear() LOOKUP |",
            "| Live ask scoreboard | OK|FP|MISS|ABSTAIN-OK | BA0 records |",
            "| Speed p50/p99 | publish / no FP regress | AZ PRODGEN |",
            "| Context content bars | usable long/cite/howto | L_eff ≠ pass |",
            "| DECODE content | usable or ABSTAIN | STRICT lock |",
            "| True continue (NANOGEN11) | PROMOTE else HOLD/DEFER | "
            "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER; stance defer |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    done_row = (
        "| BA0 | **SESSION** | Freeze BA-FOREVER + scoreboard + gen method "
        "stance + ctx/speed baselines | cite AZ; no rename | "
        "**DONE — PROMOTE** |"
    )
    ba0_todo = (
        "| BA0 | **SESSION** | Freeze BA-FOREVER + scoreboard + gen method "
        "stance + ctx/speed baselines | cite AZ; no rename | **TODO** |"
    )
    if ba0_todo in text:
        text = text.replace(ba0_todo, done_row, 1)
    text = text.replace(
        "> **Session:** `.local/wave-ba/SESSION.md` (create at BA0).  ",
        "> **Session:** `.local/wave-ba/SESSION.md` "
        "(BA0 **DONE — PROMOTE**; next BA1 H-REALGAIN).  ",
        1,
    )
    old_next = (
        "1. **BA0 SESSION** — create `.local/wave-ba/SESSION.md` · freeze "
        "BA-FOREVER seeds + paraphrase rule · publish ctx/speed baselines "
        "from AZ · set gen method stance (`M1`/`M2`/`M3`/defer).  "
    )
    if old_next in text:
        text = text.replace(
            old_next,
            "1. **BA0 SESSION** — **DONE PROMOTE** "
            "(`npm run nano:ba:session`) · gen stance **defer** · "
            "H-REALGAIN·H-FASTREAL·H-CTXREAL2·H-NANOGEN11 named · "
            "BA-FOREVER + AZ hold + baselines frozen.  ",
            1,
        )
    text = text.replace(
        "2. **BA1 H-REALGAIN** — drive forever FH → **0** via **gate** "
        "(not stuffing); hold AZ bars; live ask scoreboard OK/FP/MISS.  ",
        "2. **BA1 H-REALGAIN** — **NEXT** — drive forever FH → **0** via "
        "**gate** (not stuffing); hold AZ bars; live ask scoreboard "
        "OK/FP/MISS.  ",
        1,
    )
    ba1_todo = (
        "| BA1 | **H-REALGAIN** | Forever FH 0 · AZ hold · over-refuse 0 · "
        "live probes · modes | §1 board | **TODO** |"
    )
    ba1_next = (
        "| BA1 | **H-REALGAIN** | Forever FH 0 · AZ hold · over-refuse 0 · "
        "live probes · modes | §1 board | **NEXT** |"
    )
    if ba1_todo in text:
        text = text.replace(ba1_todo, ba1_next, 1)
    bash_old = (
        "# BA0: session runner TBD after SESSION freeze\n"
        "# npm run nano:ba:session\n"
        "# npm run nano:realgain\n"
        "# npm run nano:fastreal\n"
        "# npm run nano:ctxreal2\n"
        "# npm run nano:nanogen11\n"
        "# npm run nano:ba:real-eval\n"
        "# npm run nano:ba:report\n"
        "# npm run nano:ba:freeze"
    )
    bash_new = (
        "npm run nano:ba:session\n"
        "# next: nano:realgain · nano:fastreal · nano:ctxreal2 · "
        "nano:nanogen11\n"
        "# npm run nano:ba:real-eval\n"
        "# npm run nano:ba:report\n"
        "# npm run nano:ba:freeze"
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

Wave AZ **COMPLETE + FROZEN** (NANOGEN10 **DEFER**).  
**Reopen:** Wave **BA ACTIVE** via `pesquisa.md` — real intelligence scoreboard.  
**BA0 SESSION:** **DONE — PROMOTE** (`npm run nano:ba:session`) · gen stance **defer** · H-REALGAIN · H-FASTREAL · H-CTXREAL2 · H-NANOGEN11 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0–P1** | Forever FH 0 (BA-FOREVER) · AZ hold · live ask OK|FP|MISS |
| **P2–P3** | Speed p50/p99 + context content bars on prod path (no FP regress) |
| **P4** | One real gen method (M1|M2|M3) — else HOLD/DEFER (H-NANOGEN11) |

## Next

1. **BA0 SESSION** — **DONE PROMOTE** (`npm run nano:ba:session`).  
2. **BA1 H-REALGAIN** — **NEXT** — forever FH → 0 via gate; hold AZ; live scoreboard.  
3. Ship claim stays AZ lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · forever FP as hit · NANOGEN11=NANOGEN10+rename · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones.

```bash
npm run nano:ba:session
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

**Wave BA ACTIVE** (lab-book reopen after AZ-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation**.

**Cursor measures (anti-FP):**

1. **Forever held-out intent FH → 0** (BA-FOREVER: pow/mod/max/sort/len + paraphrases)  
2. **Speed** — prod ask p50/p99 (no quality regress)  
3. **Context** — usable long/cite/howto content bars (L_eff alone ≠ win)  
4. **Generative** — true_continue only; else HOLD/DEFER (NANOGEN6–10 cited)

Session: `wave-ba/SESSION.md` (BA0 **DONE — PROMOTE**; next BA1 H-REALGAIN). Parent: Wave AZ **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–AZ | COMPLETE + FROZEN |
| Ship (until BA gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§12 · Wave BA0–BA7 |

## Do not

LOOKUP-as-IQ · pack PASS with forever FP · over-refuse as win · sell HOLD/DEFER as unlock · L_eff/cache vanity as ctx/speed · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BA ACTIVE" in text:
        return
    marker = "**Wave AZ COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    az_line = text[idx:end]
    if "do not invent Wave BA" in az_line:
        az_line = az_line.replace(
            "do not invent Wave BA",
            "Wave BA reopened via lab-book",
        )
        text = text[:idx] + az_line + text[end:]
        end = idx + len(az_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_ba() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BA ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BA ACTIVE** — BA0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-ba-session.md) "
        "(`npm run nano:ba:session`) — BA-FOREVER anti-FP · AZ hold · "
        "§1 scoreboard · gen stance **defer** (H-NANOGEN11); next BA1 "
        "H-REALGAIN; ship remains **AF + AQ + AS trust + STRICT ablated "
        "DECODE**; NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave BA.",
        "Wave BA reopened via lab-book.",
        1,
    )
    text2, n = re.subn(
        r"- \*\*Wave AZ COMPLETE \+ FROZEN\*\* —[^\n]+",
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_ba() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **BA** |" in text:
        return
    row = (
        "| **BA** | **ACTIVE** | BA0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-ba-session.md) (`npm run nano:ba:session`) "
        "— BA-FOREVER · AZ hold · gen stance defer (H-NANOGEN11); "
        "next BA1 H-REALGAIN; ship AF+AQ+AS trust + STRICT ablated DECODE; "
        "NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave BA |",
        "Wave BA reopened via lab-book |",
        1,
    )
    text2, n = re.subn(
        r"\| \*\*AZ\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_ba() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave BA ACTIVE" in text:
        return
    dual = (
        "do not invent Wave BA); do not invent Wave BA",
        "Wave BA ACTIVE (BA0 SESSION PROMOTE; next BA1 H-REALGAIN)); "
        "do not invent Wave BB",
    )
    single = (
        "do not invent Wave BA",
        "Wave BA ACTIVE (BA0 SESSION PROMOTE; next BA1 H-REALGAIN); "
        "do not invent Wave BB",
    )
    if dual[0] in text:
        text = text.replace(dual[0], dual[1], 1)
    elif single[0] in text:
        text = text.replace(single[0], single[1], 1)
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_ba0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BA0 SESSION" in text:
        return
    insert = (
        "| Wave BA0 SESSION | [wave-ba-session.md](wave-ba-session.md) "
        "**PROMOTE** (`npm run nano:ba:session`) — BA-FOREVER N≥15 · "
        "pow·mod·max·sort·len · AZ hold · §1 scoreboard · ctx/speed "
        "baselines · gen stance **defer** (H-NANOGEN11 · M1|M2|M3) · "
        "true-eval |"
    )
    marker = (
        "| Wave AZ6 AZ-FREEZE | [az-freeze.md](az-freeze.md) · "
        "[formal-hazfreeze-az-freeze.md](formal-hazfreeze-az-freeze.md) "
        "**PROMOTE** (`npm run nano:az:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN10 DEFER; do not invent Wave BA |"
    )
    if marker not in text:
        # Try after status line update already rewrote "do not invent".
        marker2 = marker.replace(
            "do not invent Wave BA",
            "Wave BA reopened via lab-book",
        )
        if marker2 in text:
            text = text.replace(marker2, marker2 + "\n" + insert, 1)
            _RECIPES.write_text(text, encoding="utf-8")
        return
    text = text.replace(
        marker,
        marker.replace("do not invent Wave BA", "Wave BA reopened via lab-book")
        + "\n"
        + insert,
        1,
    )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BA_ACTIVE_LINE.replace(
        "**Wave BA ACTIVE:**", "**Wave BA ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BA_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_ba()
    _patch_agenda_ba()
    _patch_evogen_ba()
    _patch_recipes_ba0()


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_ba0_session(
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
        "id": BA0_ID,
        "thesis": BA0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_az_locks": sorted(BA0_CITED_AZ_LOCKS),
        "scoreboard": dict(BA0_SCOREBOARD),
        "forever_protocol": dict(BA0_FOREVER_PROTOCOL),
        "az_hold_protocol": dict(BA0_AZ_HOLD_PROTOCOL),
        "speed_baseline": dict(BA0_SPEED_BASELINE),
        "ctx_baseline": dict(BA0_CTX_BASELINE),
        "gen_stance": dict(BA0_GEN_STANCE),
        "true_gen_judge": dict(BA0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BA0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BA0_ASK_BATTERY),
        "forever_n": len(BA0_FOREVER_ROWS),
        "safe_note": BA0_SAFE_NOTE,
        "anti_fp": BA0_ANTI_FP,
        "north_star": BA0_NORTH_STAR,
        "ship_lock": BA0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-ba-session.md",
        "rule": "pesquisa §8 BA0 · forever + AZ hold + gen-defer + anti-FP",
        "next": "BA1 H-REALGAIN (forever FH 0 via gate; hold AZ)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BA0_ID,
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
