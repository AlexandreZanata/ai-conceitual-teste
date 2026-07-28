"""Wave BF0 SESSION runner (nano:bf:session) — freeze BF packs after BE-FREEZE."""

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
from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import (
    BF0_ANTI_FP,
    BF0_ASK_BATTERY,
    BF0_AZ_HOLD_PROTOCOL,
    BF0_BA_HOLD_PROTOCOL,
    BF0_BB_HOLD_PROTOCOL,
    BF0_BC_HOLD_PROTOCOL,
    BF0_BD_HOLD_PROTOCOL,
    BF0_BE_HOLD_PROTOCOL,
    BF0_CITED_BE_LOCKS,
    BF0_CTX_BASELINE,
    BF0_FOREVER_PROTOCOL,
    BF0_FOREVER_ROWS,
    BF0_GEN_STANCE,
    BF0_ID,
    BF0_MODES,
    BF0_NORTH_STAR,
    BF0_REAL_EVAL_PROTOCOL,
    BF0_SAFE_NOTE,
    BF0_SCOREBOARD,
    BF0_SHIP_LOCK,
    BF0_SPEED_BASELINE,
    BF0_THESIS,
    BF0_TRUE_GEN_JUDGE,
    BF0_UTIL_TRACK,
    decide_bf0_session,
    map_bf_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bf/bf0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-bf/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-bf/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bf-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bf/SESSION.md"
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
_FOREVER_FP = str(BF0_FOREVER_ROWS[0]["question"])
_FOREVER_NEI = str(BF0_FOREVER_ROWS[5]["question"])
_BA_HOLD = str(BA0_FOREVER_ROWS[0]["question"])
_BB_HOLD = str(BB0_FOREVER_ROWS[0]["question"])
_BC_HOLD = str(BC0_FOREVER_ROWS[0]["question"])
_BD_HOLD = str(BD0_FOREVER_ROWS[0]["question"])
_BE_HOLD = str(BE0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BF_ACTIVE_LINE = (
    "**Wave BF ACTIVE:** BF0 [SESSION PROMOTE](wave-bf-session.md) "
    "(`npm run nano:bf:session`) — BF-FOREVER predicate/boolean anti-FP · "
    "BA/BB/BC/BD/BE/AZ hold · Track A+ utilization · §1 scoreboard · "
    "ctx/speed baselines · gen stance **SKIP** (no NANOGEN16 without "
    "method plan) · real-eval; next BF1 H-PREDINT; ship remains **AF + AQ + "
    "AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
    "NANOGEN8…15 DEFER; ≤5M stays."
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
        "stage": "BF0",
        "hyp_id": BF0_ID,
        "pack": pack,
        "status": "frozen",
        **body,
    }
    path = trials_dir / f"{tid}.json"
    write_json(path, payload)
    return str(path.relative_to(REPO))


def _write_battery_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in BF0_ASK_BATTERY:
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
    for item in BF0_FOREVER_ROWS:
        tid = str(item["id"])
        written.append(
            _write_row_trial(
                trials_dir,
                tid=tid,
                pack="bf-forever",
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
        ("BF-SCOREBOARD", "scoreboard", dict(BF0_SCOREBOARD)),
        ("BF-FOREVER", "forever-protocol", dict(BF0_FOREVER_PROTOCOL)),
        ("BF-BA-HOLD", "ba-hold-protocol", dict(BF0_BA_HOLD_PROTOCOL)),
        ("BF-BB-HOLD", "bb-hold-protocol", dict(BF0_BB_HOLD_PROTOCOL)),
        ("BF-BC-HOLD", "bc-hold-protocol", dict(BF0_BC_HOLD_PROTOCOL)),
        ("BF-BD-HOLD", "bd-hold-protocol", dict(BF0_BD_HOLD_PROTOCOL)),
        ("BF-BE-HOLD", "be-hold-protocol", dict(BF0_BE_HOLD_PROTOCOL)),
        ("BF-AZ-HOLD", "az-hold-protocol", dict(BF0_AZ_HOLD_PROTOCOL)),
        (
            "BF-BASELINES",
            "ctx-speed-baselines",
            {
                "speed": dict(BF0_SPEED_BASELINE),
                "ctx": dict(BF0_CTX_BASELINE),
            },
        ),
        (
            "BF-UTIL",
            "util-track",
            dict(BF0_UTIL_TRACK),
        ),
        (
            "BF-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BF0_GEN_STANCE),
                "true_gen_judge": dict(BF0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "BF-REAL-EVAL",
            "real-eval-protocol",
            dict(BF0_REAL_EVAL_PROTOCOL),
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
    need = len(BF0_ASK_BATTERY) + len(BF0_FOREVER_ROWS) + 12
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BF0_ASK_BATTERY
    )
    fh_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in BF0_FOREVER_ROWS
    )
    bars = BF0_SCOREBOARD["bars"]
    debts = BF0_SCOREBOARD["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BF0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    util_rows = "\n".join(f"| {i+1} | {c} |" for i, c in enumerate(BF0_UTIL_TRACK["checklist"]))  # type: ignore[index]
    body = "\n".join(
        [
            "# Wave BF0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 · Session: "
            "`.local/wave-bf/SESSION.md`  ",
            "> Module: `nano_lm/src/bf_session_ops.py` · "
            "Runner: `npm run nano:bf:session`  ",
            "> Parent: [be-freeze.md](be-freeze.md) "
            "(Wave BF reopened explicitly via lab-book reopen after BE-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BF packs: "
            "BF-FOREVER (N≥12 · predicate/boolean even≠add · paraphrases · "
            "predicate/schema neighbors ≠ BA…BE/AZ) · BA…BE-FOREVER hold · "
            "AZ hold · Track A utilization · §1 anti-FP scoreboard · "
            "ctx/speed baselines from BE · gen stance **SKIP** "
            "(CAPCHECK closed; **H-NANOGEN16**; M1|M2|M3 named; **not** "
            "NANOGEN16 without method plan) · real-eval protocol. **Not** a "
            "CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked (BF5 SKIP without method plan).",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | BF FH0 · BA…BE/AZ hold · live ask · "
            "ctx/speed · util · modes · DECODE law (BF1) |",
            f"| BF-FOREVER protocol | {len(BF0_FOREVER_ROWS)} | "
            "even≠add · bool/predicate neighbors + paraphrases (BF1) |",
            "| BA hold protocol | 1 | pow·mod·max·sort·len FH0 regression |",
            "| BB hold protocol | 1 | min·xor·absdiff·and·or FH0 regression |",
            "| BC hold protocol | 1 | floordiv·neg·gcd·lshift·rshift·nand "
            "FH0 regression |",
            "| BD hold protocol | 1 | reverse≠f-string · mul≠add FH0 |",
            "| BE hold protocol | 1 | str→int / type-coercion FH0 |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Track A utilization | 1 | demo · recipes · paper · operator "
            "(BF2) |",
            "| Ctx/speed baselines | 1 | BE FASTBE p50/p99 · CTXBE "
            "content (BF3/BF4) |",
            "| Gen stance | 1 | **SKIP** · CAPCHECK closed · "
            "H-NANOGEN16 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8…15 "
            "DEFER cited (BF5) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BF5) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BF6) |",
            f"| Ask battery | {len(BF0_ASK_BATTERY)} | frozen live rows "
            "(scored at BF6) |",
            "",
            "## Cited BE locks",
            "",
            ", ".join(sorted(BF0_CITED_BE_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- bf_forever_false_hit_max: **{bars['bf_forever_false_hit_max']}**  ",
            f"- ba_forever_false_hit_max: **{bars['ba_forever_false_hit_max']}**  ",
            f"- bb_forever_false_hit_max: **{bars['bb_forever_false_hit_max']}**  ",
            f"- bc_forever_false_hit_max: **{bars['bc_forever_false_hit_max']}**  ",
            f"- bd_forever_false_hit_max: **{bars['bd_forever_false_hit_max']}**  ",
            f"- be_forever_false_hit_max: **{bars['be_forever_false_hit_max']}**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- bf_forever_min_n: **{bars['bf_forever_min_n']}**  ",
            f"- bf_forever_classes_min: **{bars['bf_forever_classes_min']}**  ",
            f"- utilization_track_frozen: **{bars['utilization_track_frozen']}**  ",
            f"- predicate_gate_preferred: **{bars['predicate_gate_preferred']}**  ",
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
            "- no vanity reopen SEMINT/FASTGAIN/CTXGAIN unless PREDINT fails",
            "",
            "## Post-BE debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## BF-FOREVER protocol",
            "",
            f"- held_out: **{BF0_FOREVER_PROTOCOL['held_out']}**  ",
            f"- forever: **{BF0_FOREVER_PROTOCOL['forever']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{BF0_FOREVER_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: "
            f"**{BF0_FOREVER_PROTOCOL['paraphrase_required']}**  ",
            f"- predicate_gate_preferred: "
            f"**{BF0_FOREVER_PROTOCOL['predicate_gate_preferred']}**  ",
            f"- neq_bd_forever: "
            f"**{BF0_FOREVER_PROTOCOL['neq_bd_forever']}**  ",
            f"- live_fp_id: **{BF0_FOREVER_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{BF0_FOREVER_PROTOCOL['min_n']}**  ",
            f"- path: `{BF0_FOREVER_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            fh_rows,
            "",
            "## BA / BB / BC / BD / BE / AZ hold",
            "",
            f"- BA heldout_n: **{BF0_BA_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BB heldout_n: **{BF0_BB_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BC heldout_n: **{BF0_BC_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BD heldout_n: **{BF0_BD_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BE heldout_n: **{BF0_BE_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- AZ heldout_n: **{BF0_AZ_HOLD_PROTOCOL['heldout_n']}** · "
            f"overrefuse_n: **{BF0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            "",
            "## Track A+ utilization",
            "",
            f"- gpt_claim_forbidden: **{BF0_UTIL_TRACK['gpt_claim_forbidden']}**  ",
            f"- bf2_gate: `{BF0_UTIL_TRACK['bf2_gate']}`",
            "",
            "| # | checklist |",
            "|--:|-----------|",
            util_rows,
            "",
            "## Speed baseline (from BE FASTBE)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BF0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- bf3_gate: `{BF0_SPEED_BASELINE['bf3_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BF0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BF0_CTX_BASELINE['content_bars_required']}**  ",
            f"- bf4_gate: `{BF0_CTX_BASELINE['bf4_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BF0_GEN_STANCE['stance']}** (SKIP)  ",
            f"- allowed: {' · '.join(BF0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BF0_GEN_STANCE['named_hyp']}**  ",
            f"- named_predint: **{BF0_GEN_STANCE['named_predint']}**  ",
            f"- named_shipuse2: **{BF0_GEN_STANCE['named_shipuse2']}**  ",
            f"- named_fast: **{BF0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BF0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BF0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen16_rename_forbidden: "
            f"**{BF0_GEN_STANCE['nanogen16_rename_forbidden']}**  ",
            f"- bf5_gate: `{BF0_GEN_STANCE['bf5_gate']}`  ",
            "",
            BF0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BF0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen16_rename_forbidden: "
            f"{BF0_TRUE_GEN_JUDGE['nanogen16_rename_forbidden']}  ",
            f"- scoring: `{BF0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BF0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{BF0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BF0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- score_labels: "
            f"{' · '.join(BF0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_forever: "
            f"{BF0_REAL_EVAL_PROTOCOL['pack_pass_neq_forever']}  ",
            f"- gen_claim_rule: "
            f"{BF0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BF0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BF0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BF0_ANTI_FP,
            "",
            "## North star",
            "",
            BF0_NORTH_STAR,
            "",
            "## Ship lock (until BF gen PROMOTE)",
            "",
            BF0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:bf:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Nona-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "BF-FOREVER + BA/BB/BC/BD/BE/AZ hold probes are **recorded** "
            "(BF1 scores forever FH=0 / holds=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-bf/bf0_session.json` · "
            "`results/nano-lm/wave-bf/trials/BF-*.json`.  ",
            "Contract: `nano_lm/tests/test_bf_session.py`.",
            "",
            "## Claims",
            "",
            "- BE packs frozen for Wave BF — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BF0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BF5 H-NANOGEN16** "
            "true_continue under a real new method (M1|M2|M3; "
            "written M1|M2|M3 plan — else SKIP stop rule).  ",
            "- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN16 without plan · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen · invent Wave BG.",
            "",
            "Next: **BF1 H-PREDINT** — drive forever FH → 0 via "
            "predicate/schema gate; hold BA…BE/AZ bars; live ask "
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
        map_bf_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        all(m in BF0_MODES for m in modes),
    )
    return all(checks)


def _arm_block(
    raw: dict[str, Any], *, question: str, note: str
) -> dict[str, Any]:
    tel = extract_telemetry(raw)
    mode = map_bf_product_mode(str(tel["mode"]))
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


def _smoke_nona_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP+DECODE+near-miss+BE FP+nei+BA/BB/BC/BD/BE/AZ hold+over-refuse."""
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
        ("behold", lambda: _ask_once(_BE_HOLD)),
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
    l_mode = map_bf_product_mode(str(l_tel["mode"]))
    g_mode = map_bf_product_mode(str(g_tel["mode"]))
    blocks = {
        "near_miss": _arm_block(
            raws["near"],
            question=_NEAR_MISS,
            note="AZ locked ABSTAIN; BF0 verifies mapping",
        ),
        "forever_fp": _arm_block(
            raws["forever"],
            question=_FOREVER_FP,
            note="BF-FOREVER type FP; BF1 scores FH=0 — BF0 records only",
        ),
        "forever_nei_fp": _arm_block(
            raws["nei"],
            question=_FOREVER_NEI,
            note="BF-FOREVER neighbor FP; BF1 scores FH=0 — BF0 records only",
        ),
        "ba_hold": _arm_block(
            raws["bahold"],
            question=_BA_HOLD,
            note="BA-FOREVER pow hold; must stay ABSTAIN — BF0 records",
        ),
        "bb_hold": _arm_block(
            raws["bbhold"],
            question=_BB_HOLD,
            note="BB-FOREVER min hold; must stay ABSTAIN — BF0 records",
        ),
        "bc_hold": _arm_block(
            raws["bchold"],
            question=_BC_HOLD,
            note="BC-FOREVER floordiv hold; must stay ABSTAIN — BF0 records",
        ),
        "bd_hold": _arm_block(
            raws["bdhold"],
            question=_BD_HOLD,
            note="BD-FOREVER reverse hold; must stay ABSTAIN — BF0 records",
        ),
        "be_hold": _arm_block(
            raws["behold"],
            question=_BE_HOLD,
            note="BE-FOREVER type hold; must stay ABSTAIN — BF0 records",
        ),
        "az_hold": _arm_block(
            raws["azhold"],
            question=_AZ_HOLD,
            note="AZ hold div; must stay ABSTAIN — BF0 records",
        ),
        "overrefuse": _arm_block(
            raws["overref"],
            question=_OVERREFUSE,
            note="exact clear gold; must LOOKUP — BF0 records",
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
            "note": "BF1 must fail gibberish content_ok; BF0 freezes bar",
        },
        **blocks,
        "modes_charter": sorted(BF0_MODES),
        "abstain_alias": map_bf_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BF0_GEN_STANCE["stance"],
        "named_hyp": BF0_GEN_STANCE["named_hyp"],
        "named_predint": BF0_GEN_STANCE["named_predint"],
        "named_shipuse2": BF0_GEN_STANCE["named_shipuse2"],
        "named_fast": BF0_GEN_STANCE["named_fast"],
        "named_ctx": BF0_GEN_STANCE["named_ctx"],
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_nona_arm(workers=workers)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "nona-arm smoke failed", "ask": ask}
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
            f"# Wave BF session checklist (**OPEN** · BF0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BF **OPEN** · predicate anti-FP + utilization + "
            "ctx/speed + honest gen).  ",
            f"> Parent: BE COMPLETE + FROZEN · Ship: **{BF0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after BE-FREEZE; BF-FOREVER predicate/boolean FP open; "
            "generative deferred once (NANOGEN6·7 HOLD · NANOGEN8…15 DEFER).",
            "",
            "## Current stage",
            "",
            f"**BF0 — SESSION ({status})** · Next: **BF1 H-PREDINT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BE ACTIVE** |",
            "| Track | BF FH0 · BA…BE/AZ hold · Track A util · ctx/speed · "
            "gen stance **SKIP** (H-NANOGEN16) |",
            "| Parent | BE COMPLETE + FROZEN |",
            "| Open hole | BF-FOREVER even≠add · predicate/schema · "
            "live ask scoreboard · predicate gate not bank-stuff |",
            "| Forbidden | NANOGEN16 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST · invent Wave BG |",
            "",
            "## North star (signed)",
            "",
            BF0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BF0)",
            "",
            "```text",
            "MODEL = BF0-SESSION",
            "",
            "[x] Freeze BF-FOREVER (N≥12 · even≠add · predicate/schema + paras)",
            "[x] Freeze BA/BB/BC/BD-FOREVER hold + AZ hold",
            "[x] Freeze §1 scoreboard (forever FH · live ask · ctx/speed · util)",
            "[x] Freeze Track A utilization checklist (H-SHIPUSE2)",
            "[x] Publish ctx/speed baselines from BD",
            "[x] Freeze gen stance = SKIP (CAPCHECK closed; H-NANOGEN16; "
            "M1|M2|M3)",
            "[x] Name BF1 H-PREDINT · BF2 H-SHIPUSE22 · BF3 H-FASTBF · "
            "BF4 H-CTXBF · BF5 H-NANOGEN16",
            "[x] Freeze true gen judge (rename forbidden; SKIP)",
            "[x] Real-eval ask battery protocol (eval=prod ask · OK|FP|MISS)",
            "[x] Copy live audits into .local/wave-bf/",
            "[x] Do NOT reopen SEMINT/FASTGAIN/CTXGAIN unless PREDINT fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN16 = NANOGEN14+rename",
            "[x] Do NOT invent Wave BG",
            "[ ] Next: BF1 H-PREDINT",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BF0 | SESSION | **{status}** |",
            "| BF1 | H-PREDINT | **NEXT** |",
            "| BF2 | H-SHIPUSE2 | pending |",
            "| BF3 | H-FASTBF | pending |",
            "| BF4 | H-CTXBF | pending |",
            "| BF5 | H-NANOGEN16 | pending (SKIP unless real method) |",
            "| BF6 | BF-REAL-EVAL | pending |",
            "| BF7 | BE-REPORT | pending |",
            "| BF8 | BE-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Forever predicate/boolean FH (ask path) | **0** | live FP debt "
            "(even→add) |",
            "| BA-FOREVER FH | **0** | H-REALGAIN hold |",
            "| BB-FOREVER FH | **0** | H-INTENTGEN hold |",
            "| BC-FOREVER FH | **0** | H-OPSFAM hold |",
            "| BD-FOREVER FH | **0** | H-SEMINT hold |",
            "| AZ hold FH (div·sub·BIP) | **0** | AZ PRODGEN 0/12 |",
            "| Over-refuse miss (exact clear) | **0** | AZ a.clear() LOOKUP |",
            "| Live ask scoreboard | OK|FP|MISS|ABSTAIN-OK | BF0 records |",
            "| Utilization Track A | demo+paper+recipes | BF0 frozen |",
            "| Speed p50/p99 | publish / no FP regress | BD FASTGAIN |",
            "| Context content bars | usable long/cite/howto | L_eff ≠ pass |",
            "| DECODE content | usable or ABSTAIN | STRICT lock |",
            "| True continue (NANOGEN16) | PROMOTE else SKIP | "
            "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER; stance skip |",
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
    exact = (
        "| BF0 | **SESSION** | Freeze BF-FOREVER; lock §1; gen = method plan "
        "**or SKIP/STOP**; Track A+ util plan; `.local/wave-bf/SESSION.md` | "
        "cite BE; no rename | **TODO** |"
    )
    exact_done = exact.replace("**TODO**", "**DONE — PROMOTE**")
    if exact in text:
        text = text.replace(exact, exact_done, 1)
    text = text.replace(
        "> **Session:** create `.local/wave-bf/SESSION.md` at BF0.  ",
        "> **Session:** `.local/wave-bf/SESSION.md` "
        "(BF0 **DONE — PROMOTE**; next BF1 H-PREDINT).  ",
        1,
    )
    old_next = (
        "1. **BF0 SESSION** — freeze BF-FOREVER from post-BE live FP "
        "(`even`≠add + paras); lock §1; decide gen = **method plan** or "
        "**SKIP/STOP**; write Track A+ utilization checklist; create "
        "`.local/wave-bf/SESSION.md`; copy live audits.  "
    )
    done_next = (
        "1. **BF0 SESSION** — **DONE PROMOTE** "
        "(`npm run nano:bf:session`) · gen stance **SKIP** · "
        "H-PREDINT·H-SHIPUSE2·H-FASTBF·H-CTXBF·H-NANOGEN16 named · "
        "BF-FOREVER + BA…BE/AZ hold + Track A+ + baselines frozen.  "
    )
    if old_next in text:
        text = text.replace(old_next, done_next, 1)
    text = text.replace(
        "**H-ID names** are working titles — lock exact IDs at BF0 "
        "(must ≠ prior npm script collisions).",
        "**H-ID names locked at BF0:** H-PREDINT · H-SHIPUSE2 · "
        "H-FASTBF · H-CTXBF · H-NANOGEN16 (must ≠ prior npm script "
        "collisions).",
        1,
    )
    text = text.replace(
        "2. **BF1 H-PREDINT** — predicate/schema gate → BF-FOREVER FH 0; "
        "BA…BE/AZ hold; ≥10 novel FP 0; **no bank stuffing**.  ",
        "2. **BF1 H-PREDINT** — **NEXT** — predicate/schema gate → "
        "BF-FOREVER FH 0; BA…BE/AZ hold; ≥10 novel FP 0; "
        "**no bank stuffing**.  ",
        1,
    )
    bf1_todo = (
        "| BF1 | **H-PREDINT** (working name) | Predicate/schema refuse → "
        "BF-FOREVER FH 0 · BA…BE hold · novel FP 0 | §1 board | **TODO** |"
    )
    bf1_next = (
        "| BF1 | **H-PREDINT** | Predicate/schema refuse → "
        "BF-FOREVER FH 0 · BA…BE hold · novel FP 0 | §1 board | **NEXT** |"
    )
    if bf1_todo in text:
        text = text.replace(bf1_todo, bf1_next, 1)
    for old, new in (
        (
            "| BF2 | **H-SHIPUSE2** (working name) |",
            "| BF2 | **H-SHIPUSE2** |",
        ),
        (
            "| BF3 | **H-FASTBF** (working name) |",
            "| BF3 | **H-FASTBF** |",
        ),
        (
            "| BF4 | **H-CTXBF** (working name) |",
            "| BF4 | **H-CTXBF** |",
        ),
    ):
        text = text.replace(old, new, 1)
    bash_old = (
        "# then (after BF0 scripts exist):\n"
        "# npm run nano:bf:session\n"
        "# npm run nano:predint          # or locked BF1 id\n"
        "# npm run nano:bf:shipuse2\n"
        "# npm run nano:bf:fastbf\n"
        "# npm run nano:bf:ctxbf\n"
        "# npm run nano:nanogen16         # ONLY if method plan exists"
        " — else SKIP\n"
        "# npm run nano:bf:real-eval\n"
        "# npm run nano:bf:report\n"
        "# npm run nano:bf:freeze"
    )
    bash_new = (
        "npm run nano:bf:session\n"
        "# next: nano:predint · nano:bf:shipuse2 · nano:bf:fastbf · "
        "nano:bf:ctxbf · nano:nanogen16 (SKIP without plan)\n"
        "# npm run nano:bf:real-eval\n"
        "# npm run nano:bf:report\n"
        "# npm run nano:bf:freeze"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    text = text.replace(
        "> **Status:** Wave BE **COMPLETE + FROZEN** (archive). Wave **BF "
        "REOPENED**",
        "> **Status:** Wave BE **COMPLETE + FROZEN** (archive). Wave **BF "
        "ACTIVE** (BF0 SESSION **DONE — PROMOTE**; next BF1 H-PREDINT)",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")

def _write_local_impl(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave BE **COMPLETE + FROZEN** (H-NANOGEN15 **DEFER**).  
**Reopen:** Wave **BF ACTIVE** via `pesquisa.md` — predicate/boolean anti-FP + utilization.  
**BF0 SESSION:** **DONE — PROMOTE** (`npm run nano:bf:session`) · gen stance **SKIP** · H-PREDINT · H-SHIPUSE2 · H-FASTBF · H-CTXBF · H-NANOGEN16 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0–P1** | BF-FOREVER FH 0 (even≠add · predicate/schema) · BA…BE/AZ hold · novel |
| **P2** | Track A+ utilization (demo + recipes + paper; H-SHIPUSE hold) |
| **P3–P4** | Speed p50/p99 + context content bars on prod path (no FP regress) |
| **P5** | One real gen method (M1|M2|M3) — else SKIP (H-NANOGEN16 stop rule) |

## Next

1. **BF0 SESSION** — **DONE PROMOTE** (`npm run nano:bf:session`).  
2. **BF1 H-PREDINT** — **NEXT** — BF-FOREVER FH → 0 via predicate gate; hold BA…BE/AZ.  
3. Ship claim stays BE lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · BA…BE PASS with BF FP · NANOGEN16 without method plan · sell HOLD/DEFER as unlock · unlabeled open chat · CTX/SMART/FAST clones · invent Wave BG.

```bash
npm run nano:bf:session
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

**Wave BF ACTIVE** (lab-book reopen after BE-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation**.

**Cursor measures (anti-FP):**

1. **BF-FOREVER predicate/boolean FH → 0** (even≠add · predicate/schema + paraphrases)  
2. **BA…BE-FOREVER + AZ hold** — no regression  
3. **Track A+ utilization** — demo + recipes + paper claim match live  
4. **Speed** — prod ask p50/p99 (no quality regress)  
5. **Context** — usable long/cite/howto content bars (L_eff alone ≠ win)  
6. **Generative** — true_continue only with written plan; else SKIP (NANOGEN6–15 cited)

Session: `wave-bf/SESSION.md` (BF0 **DONE — PROMOTE**; next BF1 H-PREDINT). Parent: Wave BE **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–BE | COMPLETE + FROZEN |
| Ship (until BF gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§13 · Wave BF0–BF8 |

## Do not

LOOKUP-as-IQ · BA…BE PASS with BF FP · over-refuse as win · sell HOLD/DEFER as unlock · L_eff/cache vanity as ctx/speed · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing · invent Wave BG.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")

def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BF ACTIVE" in text:
        return
    marker = "**Wave BE COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    bd_line = text[idx:end]
    if "do not invent Wave BF" in bd_line:
        bd_line = bd_line.replace(
            "do not invent Wave BF",
            "Wave BF reopened via lab-book",
        )
        text = text[:idx] + bd_line + text[end:]
        end = idx + len(bd_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")

def _patch_agents_be() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BF ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BF ACTIVE** — BF0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bf-session.md) "
        "(`npm run nano:bf:session`) — BF-FOREVER predicate/boolean anti-FP · "
        "BA…BE/AZ hold · Track A+ utilization · §1 scoreboard · gen stance "
        "**SKIP** (H-NANOGEN16); next BF1 H-PREDINT; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8…15 DEFER; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave BF.",
        "Wave BF reopened via lab-book.",
        1,
    )
    pat = r"- \*\*Wave BE COMPLETE \+ FROZEN\*\* —[^\n]+"
    text2, n = re.subn(
        pat,
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
    if "| **BF** |" in text:
        return
    row = (
        "| **BF** | **ACTIVE** | BF0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-bf-session.md) (`npm run nano:bf:session`) "
        "— BF-FOREVER · BA…BE/AZ hold · Track A+ util · gen stance SKIP "
        "(H-NANOGEN16); next BF1 H-PREDINT; ship AF+AQ+AS trust + STRICT "
        "ablated DECODE; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave BF |",
        "Wave BF reopened via lab-book |",
        1,
    )
    pat = r"\| \*\*BE\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+"
    text2, n = re.subn(
        pat,
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
    if "Wave BF ACTIVE" in text:
        return
    if "do not invent Wave BF" in text:
        text = text.replace(
            "do not invent Wave BF",
            "Wave BF ACTIVE (BF0 SESSION PROMOTE; next BF1 H-PREDINT); "
            "do not invent Wave BG",
            1,
        )
        _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_be0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BF0 SESSION" in text:
        return
    insert = (
        "| Wave BF0 SESSION | [wave-bf-session.md](wave-bf-session.md) "
        "**PROMOTE** (`npm run nano:bf:session`) — BF-FOREVER N≥12 · "
        "even≠add · predicate/schema · BA…BE/AZ hold · Track A+ util · §1 "
        "scoreboard · ctx/speed baselines · gen stance **SKIP** "
        "(no NANOGEN16 without method plan) · true-eval |"
    )
    marker = (
        "| Wave BE8 BE-FREEZE | [be-freeze.md](be-freeze.md) · "
        "[formal-habefreeze-be-freeze.md](formal-habefreeze-be-freeze.md) "
        "**PROMOTE** (`npm run nano:be:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN15 DEFER; do not invent Wave BF |"
    )
    marker2 = marker.replace(
        "do not invent Wave BF",
        "Wave BF reopened via lab-book",
    )
    nl = "\n"
    if marker in text:
        text = text.replace(marker, marker2 + nl + insert, 1)
        _RECIPES.write_text(text, encoding="utf-8")
        return
    if marker2 in text:
        text = text.replace(marker2, marker2 + nl + insert, 1)
        _RECIPES.write_text(text, encoding="utf-8")

def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BF_ACTIVE_LINE.replace(
        "**Wave BF ACTIVE:**", "**Wave BF ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BF_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_be()
    _patch_agenda_be()
    _patch_evogen_be()
    _patch_recipes_be0()

def _promote_live_audits() -> list[str]:
    src_dir = REPO / ".local/tmp-live-audit"
    dst = REPO / ".local/wave-bf"
    dst.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    if not src_dir.is_dir():
        return copied
    for name in (
        "be-reval-1785270649.jsonl",
        "be-novel-1785270737.jsonl",
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
    path = REPO / ".local/wave-bf/live_audit_bf0_smoke.json"
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
    decision = decide_bf0_session(
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
        "id": BF0_ID,
        "thesis": BF0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_be_locks": sorted(BF0_CITED_BE_LOCKS),
        "scoreboard": dict(BF0_SCOREBOARD),
        "forever_protocol": dict(BF0_FOREVER_PROTOCOL),
        "ba_hold_protocol": dict(BF0_BA_HOLD_PROTOCOL),
        "bb_hold_protocol": dict(BF0_BB_HOLD_PROTOCOL),
        "bc_hold_protocol": dict(BF0_BC_HOLD_PROTOCOL),
        "bd_hold_protocol": dict(BF0_BD_HOLD_PROTOCOL),
        "be_hold_protocol": dict(BF0_BE_HOLD_PROTOCOL),
        "az_hold_protocol": dict(BF0_AZ_HOLD_PROTOCOL),
        "util_track": dict(BF0_UTIL_TRACK),
        "speed_baseline": dict(BF0_SPEED_BASELINE),
        "ctx_baseline": dict(BF0_CTX_BASELINE),
        "gen_stance": dict(BF0_GEN_STANCE),
        "true_gen_judge": dict(BF0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BF0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BF0_ASK_BATTERY),
        "forever_n": len(BF0_FOREVER_ROWS),
        "safe_note": BF0_SAFE_NOTE,
        "anti_fp": BF0_ANTI_FP,
        "north_star": BF0_NORTH_STAR,
        "ship_lock": BF0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "live_audits_promoted": audits,
        "public_note": "docs/results/nano-lm/wave-bf-session.md",
        "rule": (
            "pesquisa §9 BF0 · BF-FOREVER + BA…BE/AZ hold + "
            "Track A util + gen-skip-once + anti-FP"
        ),
        "next": "BF1 H-PREDINT (BF-FOREVER FH 0 via gate; hold BA…BE/AZ)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BF0_ID,
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
