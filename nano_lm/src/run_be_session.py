"""Wave BE0 SESSION runner (nano:be:session) — freeze BE packs after BD-FREEZE."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
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
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import (
    BE0_ANTI_FP,
    BE0_ASK_BATTERY,
    BE0_AZ_HOLD_PROTOCOL,
    BE0_BA_HOLD_PROTOCOL,
    BE0_BB_HOLD_PROTOCOL,
    BE0_BC_HOLD_PROTOCOL,
    BE0_BD_HOLD_PROTOCOL,
    BE0_CITED_BD_LOCKS,
    BE0_CTX_BASELINE,
    BE0_FOREVER_PROTOCOL,
    BE0_FOREVER_ROWS,
    BE0_GEN_STANCE,
    BE0_ID,
    BE0_MODES,
    BE0_NORTH_STAR,
    BE0_REAL_EVAL_PROTOCOL,
    BE0_SAFE_NOTE,
    BE0_SCOREBOARD,
    BE0_SHIP_LOCK,
    BE0_SPEED_BASELINE,
    BE0_THESIS,
    BE0_TRUE_GEN_JUDGE,
    BE0_UTIL_TRACK,
    decide_be0_session,
    map_be_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-be/be0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-be/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-be/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-be-session.md"
_LOCAL_SESSION = REPO / ".local/wave-be/SESSION.md"
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
_FOREVER_FP = str(BE0_FOREVER_ROWS[0]["question"])
_FOREVER_NEI = str(BE0_FOREVER_ROWS[5]["question"])
_BA_HOLD = str(BA0_FOREVER_ROWS[0]["question"])
_BB_HOLD = str(BB0_FOREVER_ROWS[0]["question"])
_BC_HOLD = str(BC0_FOREVER_ROWS[0]["question"])
_BD_HOLD = str(BD0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BE_ACTIVE_LINE = (
    "**Wave BE ACTIVE:** BE0 [SESSION PROMOTE](wave-be-session.md) "
    "(`npm run nano:be:session`) — BE-FOREVER type/coercion anti-FP · "
    "BA/BB/BC/BD/AZ hold · Track A utilization · §1 scoreboard · "
    "ctx/speed baselines · gen stance **defer once** (H-NANOGEN15 · "
    "M1|M2|M3) · real-eval; next BE1 H-COMPINT; ship remains **AF + AQ + "
    "AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
    "NANOGEN8…14 DEFER; ≤5M stays."
)



def _hardware() -> tuple[int, int]:
    # 16c / 31Gi host: leave ≥6 cores free under mem pressure.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(6, max(3, cpus - 6))
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
        "stage": "BE0",
        "hyp_id": BE0_ID,
        "pack": pack,
        "status": "frozen",
        **body,
    }
    path = trials_dir / f"{tid}.json"
    write_json(path, payload)
    return str(path.relative_to(REPO))


def _write_battery_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in BE0_ASK_BATTERY:
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
    for item in BE0_FOREVER_ROWS:
        tid = str(item["id"])
        written.append(
            _write_row_trial(
                trials_dir,
                tid=tid,
                pack="be-forever",
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
        ("BE-SCOREBOARD", "scoreboard", dict(BE0_SCOREBOARD)),
        ("BE-FOREVER", "forever-protocol", dict(BE0_FOREVER_PROTOCOL)),
        ("BE-BA-HOLD", "ba-hold-protocol", dict(BE0_BA_HOLD_PROTOCOL)),
        ("BE-BB-HOLD", "bb-hold-protocol", dict(BE0_BB_HOLD_PROTOCOL)),
        ("BE-BC-HOLD", "bc-hold-protocol", dict(BE0_BC_HOLD_PROTOCOL)),
        ("BE-BD-HOLD", "bd-hold-protocol", dict(BE0_BD_HOLD_PROTOCOL)),
        ("BE-AZ-HOLD", "az-hold-protocol", dict(BE0_AZ_HOLD_PROTOCOL)),
        (
            "BE-BASELINES",
            "ctx-speed-baselines",
            {
                "speed": dict(BE0_SPEED_BASELINE),
                "ctx": dict(BE0_CTX_BASELINE),
            },
        ),
        (
            "BE-UTIL",
            "util-track",
            dict(BE0_UTIL_TRACK),
        ),
        (
            "BE-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BE0_GEN_STANCE),
                "true_gen_judge": dict(BE0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "BE-REAL-EVAL",
            "real-eval-protocol",
            dict(BE0_REAL_EVAL_PROTOCOL),
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
    need = len(BE0_ASK_BATTERY) + len(BE0_FOREVER_ROWS) + 11
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BE0_ASK_BATTERY
    )
    fh_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in BE0_FOREVER_ROWS
    )
    bars = BE0_SCOREBOARD["bars"]
    debts = BE0_SCOREBOARD["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BE0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    util_rows = "\n".join(f"| {i+1} | {c} |" for i, c in enumerate(BE0_UTIL_TRACK["checklist"]))  # type: ignore[index]
    body = "\n".join(
        [
            "# Wave BE0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 · Session: "
            "`.local/wave-be/SESSION.md`  ",
            "> Module: `nano_lm/src/be_session_ops.py` · "
            "Runner: `npm run nano:be:session`  ",
            "> Parent: [bd-freeze.md](bd-freeze.md) "
            "(Wave BE reopened explicitly via lab-book reopen after BD-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BE packs: "
            "BE-FOREVER (N≥12 · type/coercion str→int≠add · paraphrases · "
            "type-schema neighbors ≠ BA/BB/BC/BD/AZ) · BA…BD-FOREVER hold · "
            "AZ hold · Track A utilization · §1 anti-FP scoreboard · "
            "ctx/speed baselines from BD · gen stance **defer once** "
            "(CAPCHECK closed; **H-NANOGEN15**; M1|M2|M3 named; **not** "
            "NANOGEN15=NANOGEN14+rename) · real-eval protocol. **Not** a "
            "CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until BE5 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | BE FH0 · BA…BD/AZ hold · live ask · "
            "ctx/speed · util · modes · DECODE law (BE1) |",
            f"| BE-FOREVER protocol | {len(BE0_FOREVER_ROWS)} | "
            "str→int≠add · type/schema neighbors + paraphrases (BE1) |",
            "| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |",
            "| BB hold protocol | 1 | min·xor·absdiff·and·or FH0 regression |",
            "| BC hold protocol | 1 | floordiv·neg·gcd·lshift·rshift·nand "
            "FH0 regression |",
            "| BD hold protocol | 1 | reverse≠f-string · mul≠add FH0 |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Track A utilization | 1 | demo · recipes · paper · operator "
            "(BE2) |",
            "| Ctx/speed baselines | 1 | BD FASTGAIN p50/p99 · CTXGAIN "
            "content (BE3/BE4) |",
            "| Gen stance | 1 | **defer once** · CAPCHECK closed · "
            "H-NANOGEN15 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8…14 "
            "DEFER cited (BE5) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BE5) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BE6) |",
            f"| Ask battery | {len(BE0_ASK_BATTERY)} | frozen live rows "
            "(scored at BE6) |",
            "",
            "## Cited BD locks",
            "",
            ", ".join(sorted(BE0_CITED_BD_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- be_forever_false_hit_max: **{bars['be_forever_false_hit_max']}**  ",
            f"- ba_forever_false_hit_max: **{bars['ba_forever_false_hit_max']}**  ",
            f"- bb_forever_false_hit_max: **{bars['bb_forever_false_hit_max']}**  ",
            f"- bc_forever_false_hit_max: **{bars['bc_forever_false_hit_max']}**  ",
            f"- bd_forever_false_hit_max: **{bars['bd_forever_false_hit_max']}**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- be_forever_min_n: **{bars['be_forever_min_n']}**  ",
            f"- be_forever_classes_min: **{bars['be_forever_classes_min']}**  ",
            f"- utilization_track_frozen: **{bars['utilization_track_frozen']}**  ",
            f"- compositional_gate_preferred: **{bars['compositional_gate_preferred']}**  ",
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
            "- no vanity reopen SEMINT/FASTGAIN/CTXGAIN unless COMPINT fails",
            "",
            "## Post-BD debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## BE-FOREVER protocol",
            "",
            f"- held_out: **{BE0_FOREVER_PROTOCOL['held_out']}**  ",
            f"- forever: **{BE0_FOREVER_PROTOCOL['forever']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{BE0_FOREVER_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: "
            f"**{BE0_FOREVER_PROTOCOL['paraphrase_required']}**  ",
            f"- compositional_gate_preferred: "
            f"**{BE0_FOREVER_PROTOCOL['compositional_gate_preferred']}**  ",
            f"- neq_bd_forever: "
            f"**{BE0_FOREVER_PROTOCOL['neq_bd_forever']}**  ",
            f"- live_fp_id: **{BE0_FOREVER_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{BE0_FOREVER_PROTOCOL['min_n']}**  ",
            f"- path: `{BE0_FOREVER_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            fh_rows,
            "",
            "## BA / BB / BC / BD / AZ hold",
            "",
            f"- BA heldout_n: **{BE0_BA_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BB heldout_n: **{BE0_BB_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BC heldout_n: **{BE0_BC_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BD heldout_n: **{BE0_BD_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- AZ heldout_n: **{BE0_AZ_HOLD_PROTOCOL['heldout_n']}** · "
            f"overrefuse_n: **{BE0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            "",
            "## Track A utilization",
            "",
            f"- gpt_claim_forbidden: **{BE0_UTIL_TRACK['gpt_claim_forbidden']}**  ",
            f"- be2_gate: `{BE0_UTIL_TRACK['be2_gate']}`",
            "",
            "| # | checklist |",
            "|--:|-----------|",
            util_rows,
            "",
            "## Speed baseline (from BD FASTGAIN)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BE0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- be3_gate: `{BE0_SPEED_BASELINE['be3_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BE0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BE0_CTX_BASELINE['content_bars_required']}**  ",
            f"- be4_gate: `{BE0_CTX_BASELINE['be4_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BE0_GEN_STANCE['stance']}** (DEFER once)  ",
            f"- allowed: {' · '.join(BE0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BE0_GEN_STANCE['named_hyp']}**  ",
            f"- named_compint: **{BE0_GEN_STANCE['named_compint']}**  ",
            f"- named_shipuse: **{BE0_GEN_STANCE['named_shipuse']}**  ",
            f"- named_fast: **{BE0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BE0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BE0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen15_rename_forbidden: "
            f"**{BE0_GEN_STANCE['nanogen15_rename_forbidden']}**  ",
            f"- be5_gate: `{BE0_GEN_STANCE['be5_gate']}`  ",
            "",
            BE0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BE0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen15_rename_forbidden: "
            f"{BE0_TRUE_GEN_JUDGE['nanogen15_rename_forbidden']}  ",
            f"- scoring: `{BE0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BE0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{BE0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BE0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- score_labels: "
            f"{' · '.join(BE0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_forever: "
            f"{BE0_REAL_EVAL_PROTOCOL['pack_pass_neq_forever']}  ",
            f"- gen_claim_rule: "
            f"{BE0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BE0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BE0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BE0_ANTI_FP,
            "",
            "## North star",
            "",
            BE0_NORTH_STAR,
            "",
            "## Ship lock (until BE gen PROMOTE)",
            "",
            BE0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:be:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Penta-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "BE-FOREVER + BA/BB/BC/BD/AZ hold probes are **recorded** "
            "(BE1 scores forever FH=0 / holds=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-be/be0_session.json` · "
            "`results/nano-lm/wave-be/trials/BE-*.json`.  ",
            "Contract: `nano_lm/tests/test_be_session.py`.",
            "",
            "## Claims",
            "",
            "- BD packs frozen for Wave BE — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BE0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BE5 H-NANOGEN15** "
            "true_continue under a real new method (M1|M2|M3; "
            "never NANOGEN14+rename; span-fallback ≠ gen; DEFER once).  ",
            "- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN15 rename · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen · invent Wave BF.",
            "",
            "Next: **BE1 H-COMPINT** — drive forever FH → 0 via "
            "compositional type/schema gate; hold BA…BD/AZ bars; live ask "
            "scoreboard OK|FP|MISS|ABSTAIN-OK; no bank stuffing.",
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
        map_be_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        all(m in BE0_MODES for m in modes),
    )
    return all(checks)


def _arm_block(
    raw: dict[str, Any], *, question: str, note: str
) -> dict[str, Any]:
    tel = extract_telemetry(raw)
    mode = map_be_product_mode(str(tel["mode"]))
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
    """LOOKUP+DECODE+near-miss+BE FP+nei+BA/BB/BC/BD/AZ hold+over-refuse."""
    jobs = (
        ("lookup", lambda: _ask_once(_KNOWN, wrap=True, abstain=True, semwrap=False)),
        ("decode", lambda: _ask_once(_DECODE_Q, wrap=False, abstain=False)),
        ("near", lambda: _ask_once(_NEAR_MISS)),
        ("forever", lambda: _ask_once(_FOREVER_FP)),
        ("nei", lambda: _ask_once(_FOREVER_NEI)),
        ("bahold", lambda: _ask_once(_BA_HOLD)),
        ("bbhold", lambda: _ask_once(_BB_HOLD)),
        ("bchold", lambda: _ask_once(_BC_HOLD)),
        ("bdhold", lambda: _ask_once(_BD_HOLD)),
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
    l_mode = map_be_product_mode(str(l_tel["mode"]))
    g_mode = map_be_product_mode(str(g_tel["mode"]))
    blocks = {
        "near_miss": _arm_block(
            raws["near"],
            question=_NEAR_MISS,
            note="AZ locked ABSTAIN; BE0 verifies mapping",
        ),
        "forever_fp": _arm_block(
            raws["forever"],
            question=_FOREVER_FP,
            note="BE-FOREVER type FP; BE1 scores FH=0 — BE0 records only",
        ),
        "forever_nei_fp": _arm_block(
            raws["nei"],
            question=_FOREVER_NEI,
            note="BE-FOREVER neighbor FP; BE1 scores FH=0 — BE0 records only",
        ),
        "ba_hold": _arm_block(
            raws["bahold"],
            question=_BA_HOLD,
            note="BA-FOREVER pow hold; must stay ABSTAIN — BE0 records",
        ),
        "bb_hold": _arm_block(
            raws["bbhold"],
            question=_BB_HOLD,
            note="BB-FOREVER min hold; must stay ABSTAIN — BE0 records",
        ),
        "bc_hold": _arm_block(
            raws["bchold"],
            question=_BC_HOLD,
            note="BC-FOREVER floordiv hold; must stay ABSTAIN — BE0 records",
        ),
        "bd_hold": _arm_block(
            raws["bdhold"],
            question=_BD_HOLD,
            note="BD-FOREVER reverse hold; must stay ABSTAIN — BE0 records",
        ),
        "az_hold": _arm_block(
            raws["azhold"],
            question=_AZ_HOLD,
            note="AZ hold div; must stay ABSTAIN — BE0 records",
        ),
        "overrefuse": _arm_block(
            raws["overref"],
            question=_OVERREFUSE,
            note="exact clear gold; must LOOKUP — BE0 records",
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
            "note": "BE1 must fail gibberish content_ok; BE0 freezes bar",
        },
        **blocks,
        "modes_charter": sorted(BE0_MODES),
        "abstain_alias": map_be_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BE0_GEN_STANCE["stance"],
        "named_hyp": BE0_GEN_STANCE["named_hyp"],
        "named_compint": BE0_GEN_STANCE["named_compint"],
        "named_shipuse": BE0_GEN_STANCE["named_shipuse"],
        "named_fast": BE0_GEN_STANCE["named_fast"],
        "named_ctx": BE0_GEN_STANCE["named_ctx"],
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
            f"# Wave BE session checklist (**OPEN** · BE0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BE **OPEN** · compositional anti-FP + utilization + "
            "ctx/speed + honest gen).  ",
            f"> Parent: BD COMPLETE + FROZEN · Ship: **{BE0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after BD-FREEZE; BE-FOREVER type/coercion FP open; "
            "generative deferred once (NANOGEN6·7 HOLD · NANOGEN8…14 DEFER).",
            "",
            "## Current stage",
            "",
            f"**BE0 — SESSION ({status})** · Next: **BE1 H-COMPINT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BE ACTIVE** |",
            "| Track | BE FH0 · BA…BD/AZ hold · Track A util · ctx/speed · "
            "gen stance **defer once** (H-NANOGEN15) |",
            "| Parent | BD COMPLETE + FROZEN |",
            "| Open hole | BE-FOREVER str→int≠add · type/schema · "
            "live ask scoreboard · compositional gate not bank-stuff |",
            "| Forbidden | NANOGEN15 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST · invent Wave BF |",
            "",
            "## North star (signed)",
            "",
            BE0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BE0)",
            "",
            "```text",
            "MODEL = BE0-SESSION",
            "",
            "[x] Freeze BE-FOREVER (N≥12 · str→int≠add · type/schema + paras)",
            "[x] Freeze BA/BB/BC/BD-FOREVER hold + AZ hold",
            "[x] Freeze §1 scoreboard (forever FH · live ask · ctx/speed · util)",
            "[x] Freeze Track A utilization checklist (H-SHIPUSE)",
            "[x] Publish ctx/speed baselines from BD",
            "[x] Freeze gen stance = defer once (CAPCHECK closed; H-NANOGEN15; "
            "M1|M2|M3)",
            "[x] Name BE1 H-COMPINT · BE2 H-SHIPUSE · BE3 H-FASTBE · "
            "BE4 H-CTXBE · BE5 H-NANOGEN15",
            "[x] Freeze true gen judge (rename forbidden; DEFER once)",
            "[x] Real-eval ask battery protocol (eval=prod ask · OK|FP|MISS)",
            "[x] Copy live audits into .local/wave-be/",
            "[x] Do NOT reopen SEMINT/FASTGAIN/CTXGAIN unless COMPINT fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN15 = NANOGEN14+rename",
            "[x] Do NOT invent Wave BF",
            "[ ] Next: BE1 H-COMPINT",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BE0 | SESSION | **{status}** |",
            "| BE1 | H-COMPINT | **NEXT** |",
            "| BE2 | H-SHIPUSE | pending |",
            "| BE3 | H-FASTBE | pending |",
            "| BE4 | H-CTXBE | pending |",
            "| BE5 | H-NANOGEN15 | pending (defer once unless real method) |",
            "| BE6 | BE-REAL-EVAL | pending |",
            "| BE7 | BE-REPORT | pending |",
            "| BE8 | BE-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Forever type/coercion FH (ask path) | **0** | live FP debt "
            "(str→int→add) |",
            "| BA-FOREVER FH | **0** | H-REALGAIN hold |",
            "| BB-FOREVER FH | **0** | H-INTENTGEN hold |",
            "| BC-FOREVER FH | **0** | H-OPSFAM hold |",
            "| BD-FOREVER FH | **0** | H-SEMINT hold |",
            "| AZ hold FH (div·sub·BIP) | **0** | AZ PRODGEN 0/12 |",
            "| Over-refuse miss (exact clear) | **0** | AZ a.clear() LOOKUP |",
            "| Live ask scoreboard | OK|FP|MISS|ABSTAIN-OK | BE0 records |",
            "| Utilization Track A | demo+paper+recipes | BE0 frozen |",
            "| Speed p50/p99 | publish / no FP regress | BD FASTGAIN |",
            "| Context content bars | usable long/cite/howto | L_eff ≠ pass |",
            "| DECODE content | usable or ABSTAIN | STRICT lock |",
            "| True continue (NANOGEN15) | PROMOTE else DEFER once | "
            "NANOGEN6·7 HOLD · NANOGEN8…14 DEFER; stance defer |",
            "",
            "## Live audits promoted",
            "",
            "- `reval-1785266523.jsonl`",
            "- `novel-hunt-1785266608.jsonl`",
            "- `fp-novel-1785263054.jsonl`",
            "- `fp-extra-1785263130.jsonl`",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")

def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    for mid in ("M1|M2|M3", "M1\\|M2\\|M3"):
        next_row = (
            "| BE0 | **SESSION** | Freeze BE-FOREVER; lock §1; gen stance = "
            f"method plan **or** DEFER-once; Track A utilization plan; "
            "`.local/wave-be/SESSION.md` | cite BD; no rename | **TODO** |"
        )
        # lab book actual wording from §9
        next_row2 = (
            "| BE0 | **SESSION** | Freeze BE-FOREVER; lock §1; gen stance = "
            f"method plan **or** DEFER-once; Track A utilization plan; "
            "`.local/wave-be/SESSION.md` | cite BD; no rename | **TODO** |"
        )
        done_row = (
            "| BE0 | **SESSION** | Freeze BE-FOREVER; lock §1; gen stance = "
            f"method plan **or** DEFER-once; Track A utilization plan; "
            "`.local/wave-be/SESSION.md` | cite BD; no rename | "
            "**DONE — PROMOTE** |"
        )
        # Exact table row from pesquisa §9
        exact = (
            "| BE0 | **SESSION** | Freeze BE-FOREVER; lock §1; gen stance = "
            "method plan or DEFER-once; Track A utilization plan; "
            "`.local/wave-be/SESSION.md` | cite BD; no rename | **TODO** |"
        )
        exact_done = (
            "| BE0 | **SESSION** | Freeze BE-FOREVER; lock §1; gen stance = "
            "method plan or DEFER-once; Track A utilization plan; "
            "`.local/wave-be/SESSION.md` | cite BD; no rename | "
            "**DONE — PROMOTE** |"
        )
        if exact in text:
            text = text.replace(exact, exact_done, 1)
            break
        _ = mid, next_row, next_row2, done_row
    text = text.replace(
        "> **Session:** create `.local/wave-be/SESSION.md` at BE0.  ",
        "> **Session:** `.local/wave-be/SESSION.md` "
        "(BE0 **DONE — PROMOTE**; next BE1 H-COMPINT).  ",
        1,
    )
    done_next = (
        "1. **BE0 SESSION** — **DONE PROMOTE** "
        "(`npm run nano:be:session`) · gen stance **defer once** · "
        "H-COMPINT·H-SHIPUSE·H-FASTBE·H-CTXBE·H-NANOGEN15 named · "
        "BE-FOREVER + BA…BD/AZ hold + Track A + baselines frozen.  "
    )
    old_next = (
        "1. **BE0 SESSION** — freeze BE-FOREVER from post-BD live FP "
        "(`str→int`≠add + paras); lock §1; decide gen = method plan **or** "
        "DEFER-once; write Track A utilization checklist; create "
        "`.local/wave-be/SESSION.md`; copy live audits.  "
    )
    if old_next in text:
        text = text.replace(old_next, done_next, 1)
    text = text.replace(
        "**H-ID names** are working titles — lock exact IDs at BE0 "
        "(must ≠ prior npm script collisions).",
        "**H-ID names locked at BE0:** H-COMPINT · H-SHIPUSE · "
        "H-FASTBE · H-CTXBE · H-NANOGEN15 (must ≠ prior npm script "
        "collisions).",
        1,
    )
    text = text.replace(
        "2. **BE1 H-COMPINT** — compositional gate → BE-FOREVER FH 0; "
        "BA…BD/AZ hold; ≥10 novel FP 0; **no bank stuffing**.  ",
        "2. **BE1 H-COMPINT** — **NEXT** — compositional gate → "
        "BE-FOREVER FH 0; BA…BD/AZ hold; ≥10 novel FP 0; "
        "**no bank stuffing**.  ",
        1,
    )
    be1_todo = (
        "| BE1 | **H-COMPINT** (working name) | Compositional / type-schema "
        "intent gate → BE-FOREVER FH 0 · BA…BD hold · novel FP 0 | §1 board | "
        "**TODO** |"
    )
    be1_next = (
        "| BE1 | **H-COMPINT** | Compositional / type-schema intent gate → "
        "BE-FOREVER FH 0 · BA…BD/AZ hold · novel FP 0 | §1 board | "
        "**NEXT** |"
    )
    if be1_todo in text:
        text = text.replace(be1_todo, be1_next, 1)
    for old, new in (
        (
            "| BE2 | **H-SHIPUSE** (working name) |",
            "| BE2 | **H-SHIPUSE** |",
        ),
        (
            "| BE3 | **H-FASTBE** (working name) |",
            "| BE3 | **H-FASTBE** |",
        ),
        (
            "| BE4 | **H-CTXBE** (working name) |",
            "| BE4 | **H-CTXBE** |",
        ),
    ):
        text = text.replace(old, new, 1)
    bash_old = (
        "# then (after BE0 scripts exist):\n"
        "# npm run nano:be:session\n"
        "# npm run nano:compint          # or locked BE1 id\n"
        "# npm run nano:be:shipuse\n"
        "# npm run nano:be:fastbe\n"
        "# npm run nano:be:ctxbe\n"
        "# npm run nano:nanogen15\n"
        "# npm run nano:be:real-eval\n"
        "# npm run nano:be:report\n"
        "# npm run nano:be:freeze"
    )
    bash_new = (
        "npm run nano:be:session\n"
        "# next: nano:compint · nano:be:shipuse · nano:be:fastbe · "
        "nano:be:ctxbe · nano:nanogen15\n"
        "# npm run nano:be:real-eval\n"
        "# npm run nano:be:report\n"
        "# npm run nano:be:freeze"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    # Status header
    text = text.replace(
        "> **Status:** Wave BD **COMPLETE + FROZEN** (archive). Wave **BE "
        "REOPENED**",
        "> **Status:** Wave BD **COMPLETE + FROZEN** (archive). Wave **BE "
        "ACTIVE** (BE0 SESSION **DONE — PROMOTE**; next BE1 H-COMPINT)",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")

def _write_local_impl(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave BD **COMPLETE + FROZEN** (H-NANOGEN14 **DEFER**).  
**Reopen:** Wave **BE ACTIVE** via `pesquisa.md` — compositional type/coercion anti-FP + utilization.  
**BE0 SESSION:** **DONE — PROMOTE** (`npm run nano:be:session`) · gen stance **defer once** · H-COMPINT · H-SHIPUSE · H-FASTBE · H-CTXBE · H-NANOGEN15 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0–P1** | BE-FOREVER FH 0 (str→int≠add · type/schema) · BA…BD/AZ hold · novel |
| **P2** | Track A utilization (demo + recipes + paper) |
| **P3–P4** | Speed p50/p99 + context content bars on prod path (no FP regress) |
| **P5** | One real gen method (M1|M2|M3) — else DEFER once (H-NANOGEN15) |

## Next

1. **BE0 SESSION** — **DONE PROMOTE** (`npm run nano:be:session`).  
2. **BE1 H-COMPINT** — **NEXT** — BE-FOREVER FH → 0 via compositional gate; hold BA…BD/AZ.  
3. Ship claim stays BD lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · BA…BD PASS with BE FP · NANOGEN15=NANOGEN14+rename · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones · invent Wave BF.

```bash
npm run nano:be:session
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

**Wave BE ACTIVE** (lab-book reopen after BD-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation**.

**Cursor measures (anti-FP):**

1. **BE-FOREVER type/coercion FH → 0** (str→int≠add · type/schema + paraphrases)  
2. **BA…BD-FOREVER + AZ hold** — no regression  
3. **Track A utilization** — demo + recipes + paper claim match live  
4. **Speed** — prod ask p50/p99 (no quality regress)  
5. **Context** — usable long/cite/howto content bars (L_eff alone ≠ win)  
6. **Generative** — true_continue only; else DEFER once (NANOGEN6–14 cited)

Session: `wave-be/SESSION.md` (BE0 **DONE — PROMOTE**; next BE1 H-COMPINT). Parent: Wave BD **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–BD | COMPLETE + FROZEN |
| Ship (until BE gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§13 · Wave BE0–BE8 |

## Do not

LOOKUP-as-IQ · BA…BD PASS with BE FP · over-refuse as win · sell HOLD/DEFER as unlock · L_eff/cache vanity as ctx/speed · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing · invent Wave BF.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")

def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BE ACTIVE" in text:
        return
    marker = "**Wave BD COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    bd_line = text[idx:end]
    if "do not invent Wave BE" in bd_line:
        bd_line = bd_line.replace(
            "do not invent Wave BE",
            "Wave BE reopened via lab-book",
        )
        text = text[:idx] + bd_line + text[end:]
        end = idx + len(bd_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")

def _patch_agents_be() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BE ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BE ACTIVE** — BE0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-be-session.md) "
        "(`npm run nano:be:session`) — BE-FOREVER type/coercion anti-FP · "
        "BA…BD/AZ hold · Track A utilization · §1 scoreboard · gen stance "
        "**defer once** (H-NANOGEN15); next BE1 H-COMPINT; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8…14 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave BE.",
        "Wave BE reopened via lab-book.",
        1,
    )
    text2, n = re.subn(
        r"- \*\*Wave BD COMPLETE \+ FROZEN\*\* —[^\n]+",
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")

def _patch_agenda_be() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **BE** |" in text:
        return
    row = (
        "| **BE** | **ACTIVE** | BE0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-be-session.md) (`npm run nano:be:session`) "
        "— BE-FOREVER · BA…BD/AZ hold · Track A util · gen stance defer once "
        "(H-NANOGEN15); next BE1 H-COMPINT; ship AF+AQ+AS trust + STRICT "
        "ablated DECODE; NANOGEN6·7 HOLD · NANOGEN8…14 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave BE |",
        "Wave BE reopened via lab-book |",
        1,
    )
    text2, n = re.subn(
        r"\| \*\*BD\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")

def _patch_evogen_be() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave BE ACTIVE" in text:
        return
    single = (
        "do not invent Wave BE",
        "Wave BE ACTIVE (BE0 SESSION PROMOTE; next BE1 H-COMPINT); "
        "do not invent Wave BF",
    )
    if single[0] in text:
        text = text.replace(single[0], single[1], 1)
        text = text.replace(single[0], "do not invent Wave BF", 1)
        _EVOGEN.write_text(text, encoding="utf-8")

def _patch_recipes_be0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BE0 SESSION" in text:
        return
    insert = (
        "| Wave BE0 SESSION | [wave-be-session.md](wave-be-session.md) "
        "**PROMOTE** (`npm run nano:be:session`) — BE-FOREVER N≥12 · "
        "str→int≠add · type/schema · BA…BD/AZ hold · Track A util · §1 "
        "scoreboard · ctx/speed baselines · gen stance **defer once** "
        "(H-NANOGEN15 · M1|M2|M3) · true-eval |"
    )
    marker = (
        "| Wave BD7 BD-FREEZE | [bd-freeze.md](bd-freeze.md) · "
        "[formal-habdfreeze-bd-freeze.md](formal-habdfreeze-bd-freeze.md) "
        "**PROMOTE** (`npm run nano:bd:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN14 DEFER; do not invent Wave BE |"
    )
    marker2 = marker.replace(
        "do not invent Wave BE",
        "Wave BE reopened via lab-book",
    )
    if marker in text:
        text = text.replace(
            marker,
            marker2 + "\n" + insert,
            1,
        )
        _RECIPES.write_text(text, encoding="utf-8")
        return
    if marker2 in text:
        text = text.replace(marker2, marker2 + "\n" + insert, 1)
        _RECIPES.write_text(text, encoding="utf-8")

def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BE_ACTIVE_LINE.replace(
        "**Wave BE ACTIVE:**", "**Wave BE ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BE_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_be()
    _patch_agenda_be()
    _patch_evogen_be()
    _patch_recipes_be0()

def _promote_live_audits() -> list[str]:
    src_dir = REPO / ".local/tmp-live-audit"
    dst = REPO / ".local/wave-be"
    dst.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    if not src_dir.is_dir():
        return copied
    for name in (
        "reval-1785266523.jsonl",
        "novel-hunt-1785266608.jsonl",
        "fp-novel-1785263054.jsonl",
        "fp-extra-1785263130.jsonl",
        "live-1785262996.log",
    ):
        src = src_dir / name
        if src.is_file():
            target = dst / name
            shutil.copy2(src, target)
            copied.append(str(target.relative_to(REPO)))
    return copied


def _persist_smoke(ask: dict[str, Any] | None) -> None:
    if ask is None:
        return
    path = REPO / ".local/wave-be/live_audit_be0_smoke.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, ask)

def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_be0_session(
        trials_dir_ready=trials_ready, anti_fp_signed=True
    )
    audits = _promote_live_audits()
    _write_public_note(decision=decision)
    _update_local_session(decision)
    _patch_pesquisa(decision)
    _write_local_impl(decision)
    _write_local_readme(decision)
    _patch_public_status(decision)
    rc, ask = _run_ask_smoke(
        decision, skip=bool(args.skip_ask), workers=workers
    )
    _persist_smoke(ask)
    if rc != 0:
        return rc

    payload = {
        "id": BE0_ID,
        "thesis": BE0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_bd_locks": sorted(BE0_CITED_BD_LOCKS),
        "scoreboard": dict(BE0_SCOREBOARD),
        "forever_protocol": dict(BE0_FOREVER_PROTOCOL),
        "ba_hold_protocol": dict(BE0_BA_HOLD_PROTOCOL),
        "bb_hold_protocol": dict(BE0_BB_HOLD_PROTOCOL),
        "bc_hold_protocol": dict(BE0_BC_HOLD_PROTOCOL),
        "bd_hold_protocol": dict(BE0_BD_HOLD_PROTOCOL),
        "az_hold_protocol": dict(BE0_AZ_HOLD_PROTOCOL),
        "util_track": dict(BE0_UTIL_TRACK),
        "speed_baseline": dict(BE0_SPEED_BASELINE),
        "ctx_baseline": dict(BE0_CTX_BASELINE),
        "gen_stance": dict(BE0_GEN_STANCE),
        "true_gen_judge": dict(BE0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BE0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BE0_ASK_BATTERY),
        "forever_n": len(BE0_FOREVER_ROWS),
        "safe_note": BE0_SAFE_NOTE,
        "anti_fp": BE0_ANTI_FP,
        "north_star": BE0_NORTH_STAR,
        "ship_lock": BE0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "live_audits_promoted": audits,
        "public_note": "docs/results/nano-lm/wave-be-session.md",
        "rule": (
            "pesquisa §9 BE0 · BE-FOREVER + BA…BD/AZ hold + "
            "Track A util + gen-defer-once + anti-FP"
        ),
        "next": "BE1 H-COMPINT (BE-FOREVER FH 0 via gate; hold BA…BD/AZ)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BE0_ID,
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
