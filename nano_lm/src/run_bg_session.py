"""Wave BG0 SESSION runner (nano:bg:session) — freeze BG packs after BF-FREEZE."""

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
from bf_session_ops import BF0_FOREVER_ROWS
from bg_session_ops import (
    BG0_ANTI_FP,
    BG0_ASK_BATTERY,
    BG0_AZ_HOLD_PROTOCOL,
    BG0_BA_HOLD_PROTOCOL,
    BG0_BB_HOLD_PROTOCOL,
    BG0_BC_HOLD_PROTOCOL,
    BG0_BD_HOLD_PROTOCOL,
    BG0_BE_HOLD_PROTOCOL,
    BG0_BF_HOLD_PROTOCOL,
    BG0_CITED_BF_LOCKS,
    BG0_CTX_BASELINE,
    BG0_FOREVER_PROTOCOL,
    BG0_FOREVER_ROWS,
    BG0_GEN_STANCE,
    BG0_ID,
    BG0_MODES,
    BG0_NORTH_STAR,
    BG0_REAL_EVAL_PROTOCOL,
    BG0_SAFE_NOTE,
    BG0_SCOREBOARD,
    BG0_SHIP_LOCK,
    BG0_SPEED_BASELINE,
    BG0_THESIS,
    BG0_TRUE_GEN_JUDGE,
    BG0_UTIL_TRACK,
    decide_bg0_session,
    map_bg_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bg/bg0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-bg/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-bg/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bg-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bg/SESSION.md"
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
_FOREVER_FP = str(BG0_FOREVER_ROWS[0]["question"])
_FOREVER_NEI = str(BG0_FOREVER_ROWS[2]["question"])  # uppercase transform
_BA_HOLD = str(BA0_FOREVER_ROWS[0]["question"])
_BB_HOLD = str(BB0_FOREVER_ROWS[0]["question"])
_BC_HOLD = str(BC0_FOREVER_ROWS[0]["question"])
_BD_HOLD = str(BD0_FOREVER_ROWS[0]["question"])
_BE_HOLD = str(BE0_FOREVER_ROWS[0]["question"])
_BF_HOLD = str(BF0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BG_ACTIVE_LINE = (
    "**Wave BG ACTIVE:** BG0 [SESSION PROMOTE](wave-bg-session.md) "
    "(`npm run nano:bg:session`) — BG-FOREVER unary/transform anti-FP · "
    "BA…BF/AZ hold · Track A++ paper/util · §1 scoreboard · "
    "ctx/speed baselines · gen stance **SKIP** (no NANOGEN17 without "
    "method plan) · real-eval; next BG1 H-UNARYINT; ship remains **AF + AQ + "
    "AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
    "NANOGEN8…15 DEFER · NANOGEN16 SKIP; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # 16c / 31Gi: leave ≥4 cores free; up to 10 parallel ask workers.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(10, max(4, cpus - 4))
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
    trials_dir: Path, *, tid: str, pack: str, body: dict[str, Any]
) -> str:
    payload = {
        "trial_id": tid,
        "stage": "BG0",
        "hyp_id": BG0_ID,
        "pack": pack,
        "status": "frozen",
        **body,
    }
    path = trials_dir / f"{tid}.json"
    write_json(path, payload)
    return str(path.relative_to(REPO))


def _write_battery_trials(trials_dir: Path) -> list[str]:
    out: list[str] = []
    for item in BG0_ASK_BATTERY:
        out.append(
            _write_row_trial(
                trials_dir,
                tid=str(item["id"]),
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
    return out


def _write_forever_trials(trials_dir: Path) -> list[str]:
    out: list[str] = []
    for item in BG0_FOREVER_ROWS:
        out.append(
            _write_row_trial(
                trials_dir,
                tid=str(item["id"]),
                pack="bg-forever",
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
    return out


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("BG-SCOREBOARD", "scoreboard", dict(BG0_SCOREBOARD)),
        ("BG-FOREVER", "forever-protocol", dict(BG0_FOREVER_PROTOCOL)),
        ("BG-BA-HOLD", "ba-hold-protocol", dict(BG0_BA_HOLD_PROTOCOL)),
        ("BG-BB-HOLD", "bb-hold-protocol", dict(BG0_BB_HOLD_PROTOCOL)),
        ("BG-BC-HOLD", "bc-hold-protocol", dict(BG0_BC_HOLD_PROTOCOL)),
        ("BG-BD-HOLD", "bd-hold-protocol", dict(BG0_BD_HOLD_PROTOCOL)),
        ("BG-BE-HOLD", "be-hold-protocol", dict(BG0_BE_HOLD_PROTOCOL)),
        ("BG-BF-HOLD", "bf-hold-protocol", dict(BG0_BF_HOLD_PROTOCOL)),
        ("BG-AZ-HOLD", "az-hold-protocol", dict(BG0_AZ_HOLD_PROTOCOL)),
        (
            "BG-BASELINES",
            "ctx-speed-baselines",
            {"speed": dict(BG0_SPEED_BASELINE), "ctx": dict(BG0_CTX_BASELINE)},
        ),
        (
            "BG-UTIL",
            "util-track",
            dict(BG0_UTIL_TRACK),
        ),
        (
            "BG-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BG0_GEN_STANCE),
                "true_gen_judge": dict(BG0_TRUE_GEN_JUDGE),
            },
        ),
        ("BG-REAL-EVAL", "real-eval-protocol", dict(BG0_REAL_EVAL_PROTOCOL)),
    )
    out: list[str] = []
    for tid, pack, body in rows:
        out.append(
            _write_row_trial(
                trials_dir, tid=tid, pack=pack, body={"body": body}
            )
        )
    return out


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
    need = len(BG0_ASK_BATTERY) + len(BG0_FOREVER_ROWS) + 13
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bars = BG0_SCOREBOARD["bars"]
    debts = BG0_SCOREBOARD["debts"]
    fh_rows = "\n".join(
        f"| {p['id']} | {p['class']} | {p['expect_mode']} |"
        for p in BG0_FOREVER_ROWS
    )
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BG0_ASK_BATTERY
    )
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BG0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    util_rows = "\n".join(
        f"| {i + 1} | {c} |"
        for i, c in enumerate(BG0_UTIL_TRACK["checklist"])  # type: ignore[index]
    )
    body = "\n".join(
        [
            "# Wave BG0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 · Session: "
            "`.local/wave-bg/SESSION.md`  ",
            "> Module: `nano_lm/src/bg_session_ops.py` · "
            "Runner: `npm run nano:bg:session`  ",
            "> Parent: [bf-freeze.md](bf-freeze.md) "
            "(Wave BG reopened explicitly via lab-book reopen after BF-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BG packs: "
            "BG-FOREVER (N≥12 · unary/math/string-transform/aggregate · "
            "paraphrases · arity/transform neighbors ≠ BA…BF/AZ) · "
            "BA…BF-FOREVER hold · AZ hold · Track A++ utilization · "
            "§1 anti-FP scoreboard · ctx/speed baselines from BF · "
            "gen stance **SKIP** (CAPCHECK closed; **H-NANOGEN17**; "
            "M1|M2|M3 named; **not** NANOGEN17 without method plan) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked "
            "(BG5 SKIP without method plan).",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | BG FH0 · BA…BF/AZ hold · live ask · "
            "ctx/speed · util · modes · DECODE law (BG1) |",
            f"| BG-FOREVER protocol | {len(BG0_FOREVER_ROWS)} | "
            "abs≠add · factorial≠add · upper≠f-string · all-truthy≠clear "
            "+ paras (BG1) |",
            "| BA…BE hold protocols | 5 | forever FH0 regression |",
            "| BF hold protocol | 1 | even/bool ≠ add FH0 |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Track A++ utilization | 1 | demo · recipes · paper/arXiv "
            "(BG2) |",
            "| Ctx/speed baselines | 1 | BF FASTBF p50/p99 · CTXBF "
            "content (BG3/BG4) |",
            "| Gen stance | 1 | **SKIP** · CAPCHECK closed · "
            "H-NANOGEN17 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8…15 "
            "DEFER · NANOGEN16 SKIP cited (BG5) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BG5) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BG6) |",
            f"| Ask battery | {len(BG0_ASK_BATTERY)} | frozen live rows "
            "(scored at BG6) |",
            "",
            "## Cited BF locks",
            "",
            ", ".join(sorted(BG0_CITED_BF_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- bg_forever_false_hit_max: **{bars['bg_forever_false_hit_max']}**  ",
            f"- bf_forever_false_hit_max: **{bars['bf_forever_false_hit_max']}**  ",
            f"- ba…be forever false_hit_max: **0**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- bg_forever_min_n: **{bars['bg_forever_min_n']}**  ",
            f"- bg_forever_classes_min: **{bars['bg_forever_classes_min']}**  ",
            f"- utilization_track_frozen: **{bars['utilization_track_frozen']}**  ",
            f"- unary_transform_gate_preferred: "
            f"**{bars['unary_transform_gate_preferred']}**  ",
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
            "- no vanity reopen PREDINT/SHIPUSE2/FASTBF/CTXBF unless "
            "UNARYINT fails",
            "",
            "## Post-BF debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## BG-FOREVER protocol",
            "",
            f"- held_out: **{BG0_FOREVER_PROTOCOL['held_out']}**  ",
            f"- forever: **{BG0_FOREVER_PROTOCOL['forever']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{BG0_FOREVER_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- paraphrase_required: "
            f"**{BG0_FOREVER_PROTOCOL['paraphrase_required']}**  ",
            f"- unary_transform_gate_preferred: "
            f"**{BG0_FOREVER_PROTOCOL['unary_transform_gate_preferred']}**  ",
            f"- neq_bf_forever: "
            f"**{BG0_FOREVER_PROTOCOL['neq_bf_forever']}**  ",
            f"- live_fp_id: **{BG0_FOREVER_PROTOCOL['live_fp_id']}**  ",
            f"- min_n: **{BG0_FOREVER_PROTOCOL['min_n']}**  ",
            f"- path: `{BG0_FOREVER_PROTOCOL['path']}`  ",
            "",
            "| id | class | expect_mode |",
            "|----|-------|-------------|",
            fh_rows,
            "",
            "## BA / BB / BC / BD / BE / BF / AZ hold",
            "",
            f"- BA heldout_n: **{BG0_BA_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BB heldout_n: **{BG0_BB_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BC heldout_n: **{BG0_BC_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BD heldout_n: **{BG0_BD_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BE heldout_n: **{BG0_BE_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BF heldout_n: **{BG0_BF_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- AZ heldout_n: **{BG0_AZ_HOLD_PROTOCOL['heldout_n']}** · "
            f"overrefuse_n: **{BG0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            "",
            "## Track A++ utilization",
            "",
            f"- gpt_claim_forbidden: **{BG0_UTIL_TRACK['gpt_claim_forbidden']}**  ",
            f"- paper_arxiv_sync: **{BG0_UTIL_TRACK['paper_arxiv_sync']}**  ",
            f"- bg2_gate: `{BG0_UTIL_TRACK['bg2_gate']}`",
            "",
            "| # | checklist |",
            "|--:|-----------|",
            util_rows,
            "",
            "## Speed baseline (from BF FASTBF)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BG0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- bg3_gate: `{BG0_SPEED_BASELINE['bg3_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BG0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BG0_CTX_BASELINE['content_bars_required']}**  ",
            f"- bg4_gate: `{BG0_CTX_BASELINE['bg4_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BG0_GEN_STANCE['stance']}** (SKIP)  ",
            f"- allowed: {' · '.join(BG0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BG0_GEN_STANCE['named_hyp']}**  ",
            f"- named_unaryint: **{BG0_GEN_STANCE['named_unaryint']}**  ",
            f"- named_shippub: **{BG0_GEN_STANCE['named_shippub']}**  ",
            f"- named_fast: **{BG0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BG0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BG0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen17_rename_forbidden: "
            f"**{BG0_GEN_STANCE['nanogen17_rename_forbidden']}**  ",
            f"- bg5_gate: `{BG0_GEN_STANCE['bg5_gate']}`  ",
            "",
            BG0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BG0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen17_rename_forbidden: "
            f"{BG0_TRUE_GEN_JUDGE['nanogen17_rename_forbidden']}  ",
            f"- scoring: `{BG0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BG0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{BG0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BG0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- score_labels: "
            f"{' · '.join(BG0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_forever: "
            f"{BG0_REAL_EVAL_PROTOCOL['pack_pass_neq_forever']}  ",
            f"- gen_claim_rule: "
            f"{BG0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BG0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BG0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BG0_ANTI_FP,
            "",
            "## North star",
            "",
            BG0_NORTH_STAR,
            "",
            "## Ship lock (until BG gen PROMOTE)",
            "",
            BG0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:bg:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Ask-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "BG-FOREVER + BA…BF/AZ hold probes are **recorded** "
            "(BG1 scores forever FH=0 / holds=0).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-bg/bg0_session.json` · "
            "`results/nano-lm/wave-bg/trials/BG-*.json`.  ",
            "Contract: `nano_lm/tests/test_bg_session.py`.",
            "",
            "## Claims",
            "",
            "- BF packs frozen for Wave BG — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BG0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BG5 H-NANOGEN17** "
            "true_continue under a real new method (M1|M2|M3; "
            "written M1|M2|M3 plan — else SKIP stop rule).  ",
            "- Forbidden: LOOKUP-as-IQ · forever FP as hit · pack theater · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN17 without plan · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen · invent Wave BH.",
            "",
            "Next: **BG1 H-UNARYINT** — drive forever FH → 0 via "
            "unary/transform/arity gate; hold BA…BF/AZ bars; live ask "
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
        map_bg_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        all(m in BG0_MODES for m in modes),
    )
    return all(checks)


def _arm_block(
    raw: dict[str, Any], *, question: str, note: str
) -> dict[str, Any]:
    tel = extract_telemetry(raw)
    mode = map_bg_product_mode(str(tel["mode"]))
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


def _smoke_ask_arms(*, workers: int) -> dict[str, Any]:
    """LOOKUP+DECODE+near-miss+BG FP+transform+BA…BF/AZ hold+over-refuse."""
    jobs = (
        ("lookup", lambda: _ask_once(_KNOWN, wrap=True, abstain=True, semwrap=False)),
        ("decode", lambda: _ask_once(_DECODE_Q, wrap=False, abstain=False)),
        ("near", lambda: _ask_once(_NEAR_MISS)),
        ("forever", lambda: _ask_once(_FOREVER_FP)),
        ("transform", lambda: _ask_once(_FOREVER_NEI)),
        ("bahold", lambda: _ask_once(_BA_HOLD)),
        ("bbhold", lambda: _ask_once(_BB_HOLD)),
        ("bchold", lambda: _ask_once(_BC_HOLD)),
        ("bdhold", lambda: _ask_once(_BD_HOLD)),
        ("behold", lambda: _ask_once(_BE_HOLD)),
        ("bfhold", lambda: _ask_once(_BF_HOLD)),
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
    l_mode = map_bg_product_mode(str(l_tel["mode"]))
    g_mode = map_bg_product_mode(str(g_tel["mode"]))
    blocks = {
        "near_miss": _arm_block(
            raws["near"], question=_NEAR_MISS, note="ABSTAIN mapping"
        ),
        "forever_fp": _arm_block(
            raws["forever"],
            question=_FOREVER_FP,
            note="BG-FOREVER abs FP; BG1 scores FH=0 — BG0 records only",
        ),
        "forever_transform_fp": _arm_block(
            raws["transform"],
            question=_FOREVER_NEI,
            note="BG-FOREVER upper FP; BG1 scores FH=0 — BG0 records only",
        ),
        "ba_hold": _arm_block(
            raws["bahold"], question=_BA_HOLD, note="BA hold ABSTAIN"
        ),
        "bb_hold": _arm_block(
            raws["bbhold"], question=_BB_HOLD, note="BB hold ABSTAIN"
        ),
        "bc_hold": _arm_block(
            raws["bchold"], question=_BC_HOLD, note="BC hold ABSTAIN"
        ),
        "bd_hold": _arm_block(
            raws["bdhold"], question=_BD_HOLD, note="BD hold ABSTAIN"
        ),
        "be_hold": _arm_block(
            raws["behold"], question=_BE_HOLD, note="BE hold ABSTAIN"
        ),
        "bf_hold": _arm_block(
            raws["bfhold"], question=_BF_HOLD, note="BF hold ABSTAIN"
        ),
        "az_hold": _arm_block(
            raws["azhold"], question=_AZ_HOLD, note="AZ hold ABSTAIN"
        ),
        "overrefuse": _arm_block(
            raws["overref"], question=_OVERREFUSE, note="exact clear LOOKUP"
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
            "note": "BG1 must fail gibberish content_ok; BG0 freezes bar",
        },
        **blocks,
        "modes_charter": sorted(BG0_MODES),
        "abstain_alias": map_bg_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BG0_GEN_STANCE["stance"],
        "named_hyp": BG0_GEN_STANCE["named_hyp"],
        "named_unaryint": BG0_GEN_STANCE["named_unaryint"],
        "named_shippub": BG0_GEN_STANCE["named_shippub"],
        "named_fast": BG0_GEN_STANCE["named_fast"],
        "named_ctx": BG0_GEN_STANCE["named_ctx"],
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_ask_arms(workers=workers)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "ask-arm smoke failed", "ask": ask}
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
            f"# Wave BG session checklist (**OPEN** · BG0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BG **OPEN** · unary/transform anti-FP + utilization + "
            "ctx/speed + honest gen).  ",
            f"> Parent: BF COMPLETE + FROZEN · Ship: **{BG0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after BF-FREEZE; BG-FOREVER unary/transform FP open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
            "NANOGEN16 SKIP).",
            "",
            "## Current stage",
            "",
            f"**BG0 — SESSION ({status})** · Next: **BG1 H-UNARYINT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BG ACTIVE** |",
            "| Track | BG FH0 · BA…BF/AZ hold · Track A++ util · ctx/speed · "
            "gen stance **SKIP** (H-NANOGEN17) |",
            "| Parent | BF COMPLETE + FROZEN |",
            "| Open hole | BG-FOREVER abs≠add · factorial≠add · "
            "upper≠f-string · all-truthy≠clear · unary/transform gate |",
            "| Forbidden | NANOGEN17 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST · invent Wave BH |",
            "",
            "## North star (signed)",
            "",
            BG0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BG0)",
            "",
            "```text",
            "MODEL = BG0-SESSION",
            "",
            "[x] Freeze BG-FOREVER (N≥12 · unary/transform + paras)",
            "[x] Freeze BA…BF-FOREVER hold + AZ hold",
            "[x] Freeze §1 scoreboard (forever FH · live ask · ctx/speed · util)",
            "[x] Freeze Track A++ utilization checklist (H-SHIPPUB)",
            "[x] Publish ctx/speed baselines from BF",
            "[x] Freeze gen stance = SKIP (CAPCHECK closed; H-NANOGEN17; "
            "M1|M2|M3)",
            "[x] Name BG1 H-UNARYINT · BG2 H-SHIPPUB · BG3 H-FASTBG · "
            "BG4 H-CTXBG · BG5 H-NANOGEN17",
            "[x] Freeze true gen judge (rename forbidden; SKIP)",
            "[x] Real-eval ask battery protocol (eval=prod ask · OK|FP|MISS)",
            "[x] Copy live audits into .local/wave-bg/",
            "[x] Do NOT reopen PREDINT/SHIPUSE2/FASTBF/CTXBF unless UNARYINT fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN17 = NANOGEN16+rename",
            "[x] Do NOT invent Wave BH",
            "[ ] Next: BG1 H-UNARYINT",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BG0 | SESSION | **{status}** |",
            "| BG1 | H-UNARYINT | **NEXT** |",
            "| BG2 | H-SHIPPUB | pending |",
            "| BG3 | H-FASTBG | pending |",
            "| BG4 | H-CTXBG | pending |",
            "| BG5 | H-NANOGEN17 | pending (SKIP unless real method) |",
            "| BG6 | BG-REAL-EVAL | pending |",
            "| BG7 | BG-REPORT | pending |",
            "| BG8 | BG-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    exact = (
        "| BG0 | **SESSION** | Freeze BG-FOREVER; lock §1; gen = method plan "
        "**or SKIP**; Track A++ paper/util plan; `.local/wave-bg/SESSION.md` | "
        "cite BF; no rename | **TODO** |"
    )
    exact_done = exact.replace("**TODO**", "**DONE — PROMOTE**")
    if exact in text:
        text = text.replace(exact, exact_done, 1)
    text = text.replace(
        "> **Session:** create `.local/wave-bg/SESSION.md` at BG0.  ",
        "> **Session:** `.local/wave-bg/SESSION.md` "
        "(BG0 **DONE — PROMOTE**; next BG1 H-UNARYINT).  ",
        1,
    )
    old_next = (
        "1. **BG0 SESSION** — freeze BG-FOREVER from post-BF live FP "
        "(abs·factorial·upper·all-truthy + paras); lock §1; decide gen = "
        "**method plan** or **SKIP**; write Track A++ paper/util checklist; "
        "create `.local/wave-bg/SESSION.md`; copy live audits.  "
    )
    done_next = (
        "1. **BG0 SESSION** — **DONE PROMOTE** "
        "(`npm run nano:bg:session`) · gen stance **SKIP** · "
        "H-UNARYINT·H-SHIPPUB·H-FASTBG·H-CTXBG·H-NANOGEN17 named · "
        "BG-FOREVER + BA…BF/AZ hold + Track A++ + baselines frozen.  "
    )
    if old_next in text:
        text = text.replace(old_next, done_next, 1)
    text = text.replace(
        "**H-ID names** are working titles — lock exact IDs at BG0 "
        "(must ≠ prior npm script collisions).",
        "**H-ID names locked at BG0:** H-UNARYINT · H-SHIPPUB · "
        "H-FASTBG · H-CTXBG · H-NANOGEN17 (must ≠ prior npm script "
        "collisions).",
        1,
    )
    text = text.replace(
        "2. **BG1 H-UNARYINT** — unary/transform/arity gate → BG-FOREVER FH 0; "
        "BA…BF/AZ hold; ≥10 novel FP 0; **no bank stuffing**.  ",
        "2. **BG1 H-UNARYINT** — **NEXT** — unary/transform/arity gate → "
        "BG-FOREVER FH 0; BA…BF/AZ hold; ≥10 novel FP 0; "
        "**no bank stuffing**.  ",
        1,
    )
    bg1_todo = (
        "| BG1 | **H-UNARYINT** (working name) | Unary/transform/arity refuse → "
        "BG-FOREVER FH 0 · BA…BF hold · novel FP 0 | §1 board | **TODO** |"
    )
    bg1_next = (
        "| BG1 | **H-UNARYINT** | Unary/transform/arity refuse → "
        "BG-FOREVER FH 0 · BA…BF hold · novel FP 0 | §1 board | **NEXT** |"
    )
    if bg1_todo in text:
        text = text.replace(bg1_todo, bg1_next, 1)
    for old, new in (
        (
            "| BG2 | **H-SHIPPUB** (working name) |",
            "| BG2 | **H-SHIPPUB** |",
        ),
        (
            "| BG3 | **H-FASTBG** (working name) |",
            "| BG3 | **H-FASTBG** |",
        ),
        (
            "| BG4 | **H-CTXBG** (working name) |",
            "| BG4 | **H-CTXBG** |",
        ),
    ):
        text = text.replace(old, new, 1)
    bash_old = (
        "# then (after BG0 scripts exist):\n"
        "# npm run nano:bg:session\n"
        "# npm run nano:unaryint         # or locked BG1 id\n"
        "# npm run nano:bg:shippub\n"
        "# npm run nano:bg:fastbg\n"
        "# npm run nano:bg:ctxbg\n"
        "# npm run nano:nanogen17         # ONLY if method plan exists"
        " — else SKIP\n"
        "# npm run nano:bg:real-eval\n"
        "# npm run nano:bg:report\n"
        "# npm run nano:bg:freeze"
    )
    bash_new = (
        "npm run nano:bg:session\n"
        "# next: nano:unaryint · nano:bg:shippub · nano:bg:fastbg · "
        "nano:bg:ctxbg · nano:nanogen17 (SKIP without plan)\n"
        "# npm run nano:bg:real-eval\n"
        "# npm run nano:bg:report\n"
        "# npm run nano:bg:freeze"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    text = text.replace(
        "> **Status:** Wave BF **COMPLETE + FROZEN** (archive). Wave **BG "
        "REOPENED**",
        "> **Status:** Wave BF **COMPLETE + FROZEN** (archive). Wave **BG "
        "ACTIVE** (BG0 SESSION **DONE — PROMOTE**; next BG1 H-UNARYINT)",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _write_local_impl(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave BF **COMPLETE + FROZEN** (H-NANOGEN16 **SKIP**).  
**Reopen:** Wave **BG ACTIVE** via `pesquisa.md` — unary/transform anti-FP + utilization/paper.  
**BG0 SESSION:** **DONE — PROMOTE** (`npm run nano:bg:session`) · gen stance **SKIP** · H-UNARYINT · H-SHIPPUB · H-FASTBG · H-CTXBG · H-NANOGEN17 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0–P1** | BG-FOREVER FH 0 (abs≠add · factorial≠add · upper≠f-string · all-truthy≠clear) · BA…BF/AZ hold · novel |
| **P2** | Track A++ utilization (demo + recipes + paper/arXiv; H-SHIPUSE2 hold) |
| **P3–P4** | Speed p50/p99 + context content bars on prod path (no FP regress) |
| **P5** | One real gen method (M1|M2|M3) — else SKIP (H-NANOGEN17 stop rule) |

## Next

1. **BG0 SESSION** — **DONE PROMOTE** (`npm run nano:bg:session`).  
2. **BG1 H-UNARYINT** — **NEXT** — BG-FOREVER FH → 0 via unary/transform gate; hold BA…BF/AZ.  
3. Ship claim stays BF lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · BA…BF PASS with BG FP · NANOGEN17 without method plan · sell HOLD/DEFER/SKIP as unlock · unlabeled open chat · CTX/SMART/FAST clones · invent Wave BH.

```bash
npm run nano:bg:session
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

**Wave BG ACTIVE** (lab-book reopen after BF-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation**.

**Cursor measures (anti-FP):**

1. **BG-FOREVER unary/transform FH → 0** (abs≠add · factorial≠add · upper≠f-string · all-truthy≠clear + paraphrases)  
2. **BA…BF-FOREVER + AZ hold** — no regression  
3. **Track A++ utilization** — demo + recipes + paper/arXiv claim match live  
4. **Speed** — prod ask p50/p99 (no quality regress)  
5. **Context** — usable long/cite/howto content bars (L_eff alone ≠ win)  
6. **Generative** — true_continue only with written plan; else SKIP (NANOGEN6–16 cited)

Session: `wave-bg/SESSION.md` (BG0 **DONE — PROMOTE**; next BG1 H-UNARYINT). Parent: Wave BF **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–BF | COMPLETE + FROZEN |
| Ship (until BG gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§13 · Wave BG0–BG8 |

## Do not

LOOKUP-as-IQ · BA…BF PASS with BG FP · over-refuse as win · sell HOLD/DEFER/SKIP as unlock · L_eff/cache vanity as ctx/speed · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing · invent Wave BH.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BG ACTIVE" in text:
        return
    marker = "**Wave BF COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    bf_line = text[idx:end]
    if "do not invent Wave BG" in bf_line:
        bf_line = bf_line.replace(
            "do not invent Wave BG",
            "Wave BG reopened via lab-book",
        )
        text = text[:idx] + bf_line + text[end:]
        end = idx + len(bf_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_bf() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BG ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BG ACTIVE** — BG0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bg-session.md) "
        "(`npm run nano:bg:session`) — BG-FOREVER unary/transform anti-FP · "
        "BA…BF/AZ hold · Track A++ utilization · §1 scoreboard · gen stance "
        "**SKIP** (H-NANOGEN17); next BG1 H-UNARYINT; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8…15 DEFER · NANOGEN16 SKIP; ≤5M stays."
    )
    text2 = text.replace(
        "do not invent Wave BG.",
        "Wave BG reopened via lab-book.",
        1,
    )
    pat = r"- \*\*Wave BF COMPLETE \+ FROZEN\*\* —[^\n]+"
    text2, n = re.subn(
        pat,
        lambda m: m.group(0) + "\n" + agents_line,
        text2,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_bf() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **BG** |" in text:
        return
    row = (
        "| **BG** | **ACTIVE** | BG0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-bg-session.md) (`npm run nano:bg:session`) "
        "— BG-FOREVER · BA…BF/AZ hold · Track A++ util · gen stance SKIP "
        "(H-NANOGEN17); next BG1 H-UNARYINT; ship AF+AQ+AS trust + STRICT "
        "ablated DECODE; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 "
        "SKIP; ≤5M |"
    )
    text2 = text.replace(
        "do not invent Wave BG |",
        "Wave BG reopened via lab-book |",
        1,
    )
    pat = r"\| \*\*BF\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+"
    text2, n = re.subn(
        pat,
        lambda m: m.group(0) + "\n" + row,
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_bf() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave BG ACTIVE" in text:
        return
    if "do not invent Wave BG" in text:
        text = text.replace(
            "do not invent Wave BG",
            "Wave BG ACTIVE (BG0 SESSION PROMOTE; next BG1 H-UNARYINT); "
            "do not invent Wave BH",
            1,
        )
        _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_bg0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BG0 SESSION" in text:
        return
    insert = (
        "| Wave BG0 SESSION | [wave-bg-session.md](wave-bg-session.md) "
        "**PROMOTE** (`npm run nano:bg:session`) — BG-FOREVER N≥12 · "
        "abs≠add · factorial≠add · upper≠f-string · all-truthy≠clear · "
        "BA…BF/AZ hold · Track A++ util · §1 scoreboard · ctx/speed "
        "baselines · gen stance **SKIP** (no NANOGEN17 without method "
        "plan) · true-eval |"
    )
    marker = (
        "| Wave BF8 BF-FREEZE | [bf-freeze.md](bf-freeze.md) · "
        "[formal-habffreeze-bf-freeze.md](formal-habffreeze-bf-freeze.md) "
        "**PROMOTE** (`npm run nano:bf:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN16 SKIP; do not invent Wave BG |"
    )
    marker2 = marker.replace(
        "do not invent Wave BG",
        "Wave BG reopened via lab-book",
    )
    nl = "\n"
    if marker in text:
        text = text.replace(marker, marker2 + nl + insert, 1)
        _RECIPES.write_text(text, encoding="utf-8")
        return
    if marker2 in text:
        text = text.replace(marker2, marker2 + nl + insert, 1)
        _RECIPES.write_text(text, encoding="utf-8")
    # fallback: append after BF freeze mention
    if "Wave BG0 SESSION" not in text and "bf-freeze.md" in text:
        text = text.replace(
            "do not invent Wave BG",
            "Wave BG reopened via lab-book",
            1,
        )
        # insert near top active section is handled by _ensure_active_line
        _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BG_ACTIVE_LINE.replace(
        "**Wave BG ACTIVE:**", "**Wave BG ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BG_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_bf()
    _patch_agenda_bf()
    _patch_evogen_bf()
    _patch_recipes_bg0()


def _promote_live_audits() -> list[str]:
    src_dir = REPO / ".local/tmp-live-audit"
    dst = REPO / ".local/wave-bg"
    dst.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    if not src_dir.is_dir():
        return copied
    for name in (
        "bf-reval-1785327348.jsonl",
        "bf-novel-1785327433.jsonl",
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
    path = REPO / ".local/wave-bg/live_audit_bg0_smoke.json"
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
    decision = decide_bg0_session(
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
        "id": BG0_ID,
        "thesis": BG0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_bf_locks": sorted(BG0_CITED_BF_LOCKS),
        "scoreboard": dict(BG0_SCOREBOARD),
        "forever_protocol": dict(BG0_FOREVER_PROTOCOL),
        "ba_hold_protocol": dict(BG0_BA_HOLD_PROTOCOL),
        "bb_hold_protocol": dict(BG0_BB_HOLD_PROTOCOL),
        "bc_hold_protocol": dict(BG0_BC_HOLD_PROTOCOL),
        "bd_hold_protocol": dict(BG0_BD_HOLD_PROTOCOL),
        "be_hold_protocol": dict(BG0_BE_HOLD_PROTOCOL),
        "bf_hold_protocol": dict(BG0_BF_HOLD_PROTOCOL),
        "az_hold_protocol": dict(BG0_AZ_HOLD_PROTOCOL),
        "util_track": dict(BG0_UTIL_TRACK),
        "speed_baseline": dict(BG0_SPEED_BASELINE),
        "ctx_baseline": dict(BG0_CTX_BASELINE),
        "gen_stance": dict(BG0_GEN_STANCE),
        "true_gen_judge": dict(BG0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BG0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BG0_ASK_BATTERY),
        "forever_n": len(BG0_FOREVER_ROWS),
        "safe_note": BG0_SAFE_NOTE,
        "anti_fp": BG0_ANTI_FP,
        "north_star": BG0_NORTH_STAR,
        "ship_lock": BG0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "live_audits_promoted": audits,
        "public_note": "docs/results/nano-lm/wave-bg-session.md",
        "rule": (
            "pesquisa §9 BG0 · BG-FOREVER + BA…BF/AZ hold + "
            "Track A++ util + gen-skip + anti-FP"
        ),
        "next": "BG1 H-UNARYINT (BG-FOREVER FH 0 via gate; hold BA…BF/AZ)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BG0_ID,
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
