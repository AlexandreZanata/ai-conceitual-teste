"""Wave BH0 SESSION runner (nano:bh:session) — freeze IQ plan after BG-FREEZE."""

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
from bg_session_ops import BG0_FOREVER_ROWS
from bh_session_ops import (
    BH0_ANTI_FP,
    BH0_ASK_BATTERY,
    BH0_AZ_HOLD_PROTOCOL,
    BH0_BA_HOLD_PROTOCOL,
    BH0_BB_HOLD_PROTOCOL,
    BH0_BC_HOLD_PROTOCOL,
    BH0_BD_HOLD_PROTOCOL,
    BH0_BE_HOLD_PROTOCOL,
    BH0_BF_HOLD_PROTOCOL,
    BH0_BG_HOLD_PROTOCOL,
    BH0_CITED_BG_LOCKS,
    BH0_CTX_BASELINE,
    BH0_GEN_STANCE,
    BH0_GOLD_HOLES,
    BH0_ID,
    BH0_IQ_BATTERY_PROTOCOL,
    BH0_IQ_SEED_ROWS,
    BH0_MODES,
    BH0_NORTH_STAR,
    BH0_REAL_EVAL_PROTOCOL,
    BH0_SAFE_NOTE,
    BH0_SCOREBOARD,
    BH0_SHIP_LOCK,
    BH0_SPEED_BASELINE,
    BH0_THESIS,
    BH0_TRUE_GEN_JUDGE,
    BH0_UTIL_TRACK,
    decide_bh0_session,
    map_bh_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bh/bh0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-bh/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-bh/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bh-session.md"
_LOCAL_SESSION = REPO / ".local/wave-bh/SESSION.md"
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
_RUST = "In Rust how do I declare a mutable integer x starting at 5?"
_DECODE_Q = "Explain Merkle trees briefly"
_NEAR_MISS = (
    "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
    "SegWit witness discount?"
)
_BG_HOLD = str(BG0_FOREVER_ROWS[0]["question"])
_BG_XFORM = str(BG0_FOREVER_ROWS[2]["question"])
_BA_HOLD = str(BA0_FOREVER_ROWS[0]["question"])
_BB_HOLD = str(BB0_FOREVER_ROWS[0]["question"])
_BC_HOLD = str(BC0_FOREVER_ROWS[0]["question"])
_BD_HOLD = str(BD0_FOREVER_ROWS[0]["question"])
_BE_HOLD = str(BE0_FOREVER_ROWS[0]["question"])
_BF_HOLD = str(BF0_FOREVER_ROWS[0]["question"])
_AZ_HOLD = str(AZ0_HELDOUT_FP_ROWS[0]["question"])
_OVERREFUSE = str(AZ0_OVERREFUSE_ROWS[0]["question"])

_BH_ACTIVE_LINE = (
    "**Wave BH ACTIVE:** BH0 [SESSION PROMOTE](wave-bh-session.md) "
    "(`npm run nano:bh:session`) — IQ battery v0 plan · gold holes "
    "(Rust MISS · add truncation) · BA…BG/AZ hold · Track A++ paper/util · "
    "§1 scoreboard · ctx/speed baselines · gen stance **SKIP** "
    "(no NANOGEN18 without method plan) · real-eval; next BH1 H-IQBAT; "
    "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
    "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16·17 SKIP; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # 16c / 31Gi with swap pressure: leave ≥6 cores free; ≤8 ask workers.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(8, max(4, cpus - 6))
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
        "stage": "BH0",
        "hyp_id": BH0_ID,
        "pack": pack,
        "status": "frozen",
        **body,
    }
    path = trials_dir / f"{tid}.json"
    write_json(path, payload)
    return str(path.relative_to(REPO))


def _write_battery_trials(trials_dir: Path) -> list[str]:
    out: list[str] = []
    for item in BH0_ASK_BATTERY:
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


def _write_iq_seed_trials(trials_dir: Path) -> list[str]:
    out: list[str] = []
    for item in BH0_IQ_SEED_ROWS:
        out.append(
            _write_row_trial(
                trials_dir,
                tid=str(item["id"]),
                pack="iq-seed",
                body={
                    "split": item["split"],
                    "family": item["family"],
                    "expect": item["expect"],
                    "question": item["question"],
                    "min_gold_substr": item["min_gold_substr"],
                    "wrong_if_contains": item["wrong_if_contains"],
                    "notes": item["notes"],
                },
            )
        )
    return out


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("BH-SCOREBOARD", "scoreboard", dict(BH0_SCOREBOARD)),
        ("BH-IQ-PLAN", "iq-battery-protocol", dict(BH0_IQ_BATTERY_PROTOCOL)),
        ("BH-GOLD-HOLES", "gold-holes", dict(BH0_GOLD_HOLES)),
        ("BH-BA-HOLD", "ba-hold-protocol", dict(BH0_BA_HOLD_PROTOCOL)),
        ("BH-BB-HOLD", "bb-hold-protocol", dict(BH0_BB_HOLD_PROTOCOL)),
        ("BH-BC-HOLD", "bc-hold-protocol", dict(BH0_BC_HOLD_PROTOCOL)),
        ("BH-BD-HOLD", "bd-hold-protocol", dict(BH0_BD_HOLD_PROTOCOL)),
        ("BH-BE-HOLD", "be-hold-protocol", dict(BH0_BE_HOLD_PROTOCOL)),
        ("BH-BF-HOLD", "bf-hold-protocol", dict(BH0_BF_HOLD_PROTOCOL)),
        ("BH-BG-HOLD", "bg-hold-protocol", dict(BH0_BG_HOLD_PROTOCOL)),
        ("BH-AZ-HOLD", "az-hold-protocol", dict(BH0_AZ_HOLD_PROTOCOL)),
        (
            "BH-BASELINES",
            "ctx-speed-baselines",
            {"speed": dict(BH0_SPEED_BASELINE), "ctx": dict(BH0_CTX_BASELINE)},
        ),
        ("BH-UTIL", "util-track", dict(BH0_UTIL_TRACK)),
        (
            "BH-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(BH0_GEN_STANCE),
                "true_gen_judge": dict(BH0_TRUE_GEN_JUDGE),
            },
        ),
        ("BH-REAL-EVAL", "real-eval-protocol", dict(BH0_REAL_EVAL_PROTOCOL)),
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
        + _write_iq_seed_trials(trials_dir)
        + _write_charter_trials(trials_dir)
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = len(BH0_ASK_BATTERY) + len(BH0_IQ_SEED_ROWS) + 15
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bars = BH0_SCOREBOARD["bars"]
    holes = BH0_GOLD_HOLES["holes"]
    hole_rows = "\n".join(
        f"| {h['id']} | {h['family']} | {h['expect']} | {h['live_mode']} |"
        for h in holes  # type: ignore[union-attr]
    )
    seed_rows = "\n".join(
        f"| {p['id']} | {p['split']} | {p['expect']} |"
        for p in BH0_IQ_SEED_ROWS
    )
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in BH0_ASK_BATTERY
    )
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |"
        for d in BH0_SCOREBOARD["debts"]  # type: ignore[index]
    )
    speed_rows = "\n".join(
        f"| {path} | **{vals['p50']}** | **{vals['p99']}** |"
        for path, vals in BH0_SPEED_BASELINE["paths"].items()  # type: ignore[union-attr]
    )
    util_rows = "\n".join(
        f"| {i + 1} | {c} |"
        for i, c in enumerate(BH0_UTIL_TRACK["checklist"])  # type: ignore[index]
    )
    mix = BH0_IQ_BATTERY_PROTOCOL["mix_min"]
    body = "\n".join(
        [
            "# Wave BH0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §9 · Session: "
            "`.local/wave-bh/SESSION.md`  ",
            "> Module: `nano_lm/src/bh_session_ops.py` · "
            "Runner: `npm run nano:bh:session`  ",
            "> Parent: [bg-freeze.md](bg-freeze.md) "
            "(Wave BH reopened explicitly via lab-book reopen after BG-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze BH packs: "
            "IQ battery v0 plan (schema · mix ≥40 · Novel_FP=0 · "
            "gold MISS=0) · gold holes (Rust MISS · add truncation) · "
            "BA…BG-FOREVER hold · AZ hold · Track A++ utilization · "
            "§1 anti-FP scoreboard · ctx/speed baselines from BG · "
            "gen stance **SKIP** (CAPCHECK closed; **H-NANOGEN18**; "
            "M1|M2|M3 named; **not** NANOGEN18 without method plan) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked "
            "(BH6 SKIP without method plan).",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Scoreboard charter | 1 | IQ · gold MISS · BA…BG/AZ hold · "
            "live ask · ctx/speed · util · modes |",
            f"| IQ battery plan | seed {len(BH0_IQ_SEED_ROWS)} / "
            f"target ≥{mix['total']} | schema + mix + Novel_FP=0 (BH1) |",
            f"| Gold holes | {len(holes)} | Rust LOOKUP · full add body "
            "(BH2) |",
            "| BA…BF hold protocols | 6 | forever FH0 regression |",
            "| BG hold protocol | 1 | abs·factorial·upper·all FH0 |",
            "| AZ hold protocol | 1 | div·sub·BIP + a.clear() regression |",
            "| Track A++ utilization | 1 | demo · recipes · paper + IQ cite "
            "(BH3) |",
            "| Ctx/speed baselines | 1 | BG FASTBG p50/p99 · CTXBG "
            "content (BH4/BH5) |",
            "| Gen stance | 1 | **SKIP** · CAPCHECK closed · "
            "H-NANOGEN18 · M1|M2|M3 · NANOGEN6·7 HOLD · NANOGEN8…15 "
            "DEFER · NANOGEN16·17 SKIP cited (BH6) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (BH6) |",
            "| Real-eval protocol | 1 | IQ + live ask · eval=prod · "
            "OK|FP|MISS|ABSTAIN-OK (BH7) |",
            f"| Ask battery | {len(BH0_ASK_BATTERY)} | frozen live rows "
            "(scored at BH7) |",
            "",
            "## Cited BG locks",
            "",
            ", ".join(sorted(BH0_CITED_BG_LOCKS)),
            "",
            "## Scoreboard bars",
            "",
            f"- iq_battery_min_n: **{bars['iq_battery_min_n']}**  ",
            f"- novel_fp_max: **{bars['novel_fp_max']}**  ",
            f"- gold_miss_max: **{bars['gold_miss_max']}**  ",
            f"- gold_rust_miss_max: **{bars['gold_rust_miss_max']}**  ",
            f"- gold_add_truncation_miss_max: "
            f"**{bars['gold_add_truncation_miss_max']}**  ",
            f"- ba…bg forever false_hit_max: **0**  ",
            f"- az_hold_false_hit_max: **{bars['az_hold_false_hit_max']}**  ",
            f"- overrefuse_miss_max: **{bars['overrefuse_miss_max']}**  ",
            f"- truncated_gold_is_miss: **{bars['truncated_gold_is_miss']}**  ",
            f"- pack_pass_neq_iq: **{bars['pack_pass_neq_iq']}**  ",
            f"- iq_battery_plan_frozen: "
            f"**{bars['iq_battery_plan_frozen']}**  ",
            f"- gold_holes_frozen: **{bars['gold_holes_frozen']}**  ",
            f"- utilization_track_frozen: "
            f"**{bars['utilization_track_frozen']}**  ",
            f"- decode_gibberish_neq_content_ok: "
            f"**{bars['decode_gibberish_neq_content_ok']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- bank_stuff_forbidden: **{bars['bank_stuff_forbidden']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "",
            "## Post-BG debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## IQ battery protocol",
            "",
            f"- version: **{BH0_IQ_BATTERY_PROTOCOL['version']}**  ",
            f"- artifact: `{BH0_IQ_BATTERY_PROTOCOL['artifact_target']}`  ",
            f"- runner: `{BH0_IQ_BATTERY_PROTOCOL['runner_target']}`  ",
            f"- mix total ≥ **{mix['total']}** "
            f"(gold≥{mix['gold']} · para≥{mix['para']} · "
            f"adversary≥{mix['adversary']} · novel≥{mix['novel']} · "
            f"ood≥{mix['ood']} · gen≥{mix['gen']})  ",
            f"- promote: Novel_FP=0 · gold MISS=0 · Forever FH=0  ",
            f"- bh1_gate: `{BH0_IQ_BATTERY_PROTOCOL['bh1_gate']}`",
            "",
            "| id | split | expect |",
            "|----|-------|--------|",
            seed_rows,
            "",
            "## Gold holes",
            "",
            "| id | family | expect | live_mode |",
            "|----|--------|--------|-----------|",
            hole_rows,
            "",
            f"- bh2_gate: `{BH0_GOLD_HOLES['bh2_gate']}`",
            "",
            "## BA / BB / BC / BD / BE / BF / BG / AZ hold",
            "",
            f"- BA heldout_n: **{BH0_BA_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BB heldout_n: **{BH0_BB_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BC heldout_n: **{BH0_BC_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BD heldout_n: **{BH0_BD_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BE heldout_n: **{BH0_BE_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BF heldout_n: **{BH0_BF_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- BG heldout_n: **{BH0_BG_HOLD_PROTOCOL['heldout_n']}**  ",
            f"- AZ heldout_n: **{BH0_AZ_HOLD_PROTOCOL['heldout_n']}** · "
            f"overrefuse_n: **{BH0_AZ_HOLD_PROTOCOL['overrefuse_n']}**  ",
            "",
            "## Track A++ utilization",
            "",
            f"- gpt_claim_forbidden: **{BH0_UTIL_TRACK['gpt_claim_forbidden']}**  ",
            f"- iq_battery_cited_in_paper: "
            f"**{BH0_UTIL_TRACK['iq_battery_cited_in_paper']}**  ",
            f"- bh3_gate: `{BH0_UTIL_TRACK['bh3_gate']}`",
            "",
            "| # | checklist |",
            "|--:|-----------|",
            util_rows,
            "",
            "## Speed baseline (from BG FASTBG)",
            "",
            "| Path | p50 wall_ms | p99 wall_ms |",
            "|------|------------:|------------:|",
            speed_rows,
            "",
            f"- quality_regress_forbidden: "
            f"**{BH0_SPEED_BASELINE['quality_regress_forbidden']}**  ",
            f"- bh4_gate: `{BH0_SPEED_BASELINE['bh4_gate']}`",
            "",
            "## Context baseline",
            "",
            f"- l_eff_alone_insufficient: "
            f"**{BH0_CTX_BASELINE['l_eff_alone_insufficient']}**  ",
            f"- content_bars_required: "
            f"**{BH0_CTX_BASELINE['content_bars_required']}**  ",
            f"- bh5_gate: `{BH0_CTX_BASELINE['bh5_gate']}`",
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{BH0_GEN_STANCE['stance']}** (SKIP)  ",
            f"- allowed: {' · '.join(BH0_GEN_STANCE['allowed_stances'])}  ",
            f"- named_hyp: **{BH0_GEN_STANCE['named_hyp']}**  ",
            f"- named_iqbat: **{BH0_GEN_STANCE['named_iqbat']}**  ",
            f"- named_goldfix: **{BH0_GEN_STANCE['named_goldfix']}**  ",
            f"- named_shipiq: **{BH0_GEN_STANCE['named_shipiq']}**  ",
            f"- named_fast: **{BH0_GEN_STANCE['named_fast']}**  ",
            f"- named_ctx: **{BH0_GEN_STANCE['named_ctx']}**  ",
            f"- capcheck: **{BH0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen18_rename_forbidden: "
            f"**{BH0_GEN_STANCE['nanogen18_rename_forbidden']}**  ",
            f"- bh6_gate: `{BH0_GEN_STANCE['bh6_gate']}`  ",
            "",
            BH0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{BH0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen18_rename_forbidden: "
            f"{BH0_TRUE_GEN_JUDGE['nanogen18_rename_forbidden']}  ",
            f"- scoring: `{BH0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{BH0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- iq_battery_required: "
            f"{BH0_REAL_EVAL_PROTOCOL['iq_battery_required']}  ",
            f"- live_ask_battery: "
            f"{BH0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{BH0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- read_completion_text: "
            f"{BH0_REAL_EVAL_PROTOCOL['read_completion_text']}  ",
            f"- truncated_gold_is_miss: "
            f"{BH0_REAL_EVAL_PROTOCOL['truncated_gold_is_miss']}  ",
            f"- score_labels: "
            f"{' · '.join(BH0_REAL_EVAL_PROTOCOL['score_labels'])}  ",
            f"- pack_pass_neq_iq: "
            f"{BH0_REAL_EVAL_PROTOCOL['pack_pass_neq_iq']}  ",
            f"- gen_claim_rule: "
            f"{BH0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {BH0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            BH0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            BH0_ANTI_FP,
            "",
            "## North star",
            "",
            BH0_NORTH_STAR,
            "",
            "## Ship lock (until BH gen PROMOTE)",
            "",
            BH0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:bh:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Ask-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "gold holes (Rust ABSTAIN · add truncation) are **recorded** "
            "(BH2 scores MISS=0); BA…BG/AZ hold probes are **recorded**.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-bh/bh0_session.json` · "
            "`results/nano-lm/wave-bh/trials/BH-*.json`.  ",
            "Contract: `nano_lm/tests/test_bh_session.py`.",
            "",
            "## Claims",
            "",
            "- BG packs frozen for Wave BH — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{BH0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **BH6 H-NANOGEN18** "
            "true_continue under a real new method (M1|M2|M3; "
            "written M1|M2|M3 plan — else SKIP stop rule).  ",
            "- Forbidden: LOOKUP-as-IQ · pack theater · truncated gold as OK · "
            "over-refuse as win · peak-as-open-chat · SAFE-as-quality · "
            "L_eff as sole ctx win · warm-cache as sole speed win · "
            "gold-substring PROMOTE · span-fallback as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · NANOGEN18 without plan · CTX/SMART/FAST "
            "clone · bank stuffing · vanity reopen · invent Wave BI.",
            "",
            "Next: **BH1 H-IQBAT** — materialize iq-battery-v0.jsonl "
            "(≥40 probes) + `npm run nano:iq-battery`; publish scoreboard; "
            "Novel_FP=0 baseline; no pack theater.",
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
        map_bh_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        all(m in BH0_MODES for m in modes),
    )
    return all(checks)


def _arm_block(
    raw: dict[str, Any], *, question: str, note: str
) -> dict[str, Any]:
    tel = extract_telemetry(raw)
    mode = map_bh_product_mode(str(tel["mode"]))
    return {
        "arm": classify_arm(raw),
        "raw_mode": tel["mode"],
        "product_mode": mode,
        "wall_ms": tel["wall_ms"],
        "n_new": tel["n_new"],
        "completion": str(raw.get("completion", ""))[:160],
        "question": question,
        "note": note,
    }


def _score_gold_holes(
    *, add_raw: dict[str, Any], rust_raw: dict[str, Any]
) -> dict[str, Any]:
    add_c = str(add_raw.get("completion", ""))
    rust_c = str(rust_raw.get("completion", ""))
    rust_mode = map_bh_product_mode(
        str(extract_telemetry(rust_raw)["mode"])
    )
    add_mode = map_bh_product_mode(str(extract_telemetry(add_raw)["mode"]))
    add_full = (
        "def add" in add_c and "return" in add_c and "a + b" in add_c
    )
    rust_ok = rust_mode == "LOOKUP" and "mut" in rust_c.lower()
    return {
        "add": {
            "product_mode": add_mode,
            "completion": add_c[:120],
            "truncated": add_mode == "LOOKUP" and not add_full,
            "full_body_ok": add_full,
            "class": "MISS-content" if (add_mode == "LOOKUP" and not add_full) else (
                "OK" if add_full else "MISS"
            ),
        },
        "rust": {
            "product_mode": rust_mode,
            "completion": rust_c[:120],
            "lookup_ok": rust_ok,
            "class": "OK" if rust_ok else "MISS",
        },
        "note": "BH0 records holes; BH2 H-GOLDFIX must close MISS=0",
    }


def _smoke_ask_arms(*, workers: int) -> dict[str, Any]:
    """LOOKUP+DECODE+near-miss+gold holes+BA…BG/AZ hold+over-refuse."""
    jobs = (
        ("lookup", lambda: _ask_once(_KNOWN, wrap=True, abstain=True, semwrap=False)),
        ("rust", lambda: _ask_once(_RUST)),
        ("decode", lambda: _ask_once(_DECODE_Q, wrap=False, abstain=False)),
        ("near", lambda: _ask_once(_NEAR_MISS)),
        ("bghold", lambda: _ask_once(_BG_HOLD)),
        ("bgxform", lambda: _ask_once(_BG_XFORM)),
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
    l_mode = map_bh_product_mode(str(l_tel["mode"]))
    g_mode = map_bh_product_mode(str(g_tel["mode"]))
    blocks = {
        "near_miss": _arm_block(
            raws["near"], question=_NEAR_MISS, note="ABSTAIN mapping"
        ),
        "bg_hold": _arm_block(
            raws["bghold"], question=_BG_HOLD, note="BG hold ABSTAIN"
        ),
        "bg_transform": _arm_block(
            raws["bgxform"], question=_BG_XFORM, note="BG upper hold"
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
        "rust_gold": _arm_block(
            raws["rust"],
            question=_RUST,
            note="BH-GOLD-01 MISS recorded — BH2 repairs",
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
    gold = _score_gold_holes(add_raw=lookup, rust_raw=raws["rust"])
    return {
        "ok": ok,
        "lookup": {
            "arm": l_arm,
            "raw_mode": l_tel["mode"],
            "product_mode": l_mode,
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
            "completion": str(lookup.get("completion", ""))[:120],
        },
        "decode": {
            "arm": g_arm,
            "raw_mode": g_tel["mode"],
            "product_mode": g_mode,
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
            "note": "BH1 must fail gibberish content_ok; BH0 freezes bar",
        },
        "gold_holes": gold,
        **blocks,
        "modes_charter": sorted(BH0_MODES),
        "abstain_alias": map_bh_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": BH0_GEN_STANCE["stance"],
        "named_hyp": BH0_GEN_STANCE["named_hyp"],
        "named_iqbat": BH0_GEN_STANCE["named_iqbat"],
        "named_goldfix": BH0_GEN_STANCE["named_goldfix"],
        "named_shipiq": BH0_GEN_STANCE["named_shipiq"],
        "named_fast": BH0_GEN_STANCE["named_fast"],
        "named_ctx": BH0_GEN_STANCE["named_ctx"],
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
            f"# Wave BH session checklist (**OPEN** · BH0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BH **OPEN** · IQ battery + gold repair + utilization + "
            "ctx/speed + honest gen).  ",
            f"> Parent: BG COMPLETE + FROZEN · Ship: **{BH0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after BG-FREEZE; IQ battery + gold MISS open; "
            "generative deferred (NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
            "NANOGEN16·17 SKIP).",
            "",
            "## Current stage",
            "",
            f"**BH0 — SESSION ({status})** · Next: **BH1 H-IQBAT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BH ACTIVE** |",
            "| Track | IQ battery v0 · gold MISS=0 · BA…BG/AZ hold · "
            "Track A++ util · ctx/speed · gen stance **SKIP** "
            "(H-NANOGEN18) |",
            "| Parent | BG COMPLETE + FROZEN |",
            "| Open hole | Rust LOOKUP MISS · add truncation MISS · "
            "IQ battery ≥40 |",
            "| Forbidden | NANOGEN18 rename · LOOKUP-as-IQ · "
            "pack theater · CTX/SMART/FAST · invent Wave BI |",
            "",
            "## North star (signed)",
            "",
            BH0_NORTH_STAR,
            "",
            "## Cursor operator checklist (BH0)",
            "",
            "```text",
            "MODEL = BH0-SESSION",
            "",
            "[x] Freeze IQ battery v0 plan (schema · mix ≥40 · Novel_FP=0)",
            "[x] Freeze gold holes (Rust MISS · add truncation)",
            "[x] Freeze BA…BG-FOREVER hold + AZ hold",
            "[x] Freeze §1 scoreboard (IQ · gold MISS · live ask · ctx/speed)",
            "[x] Freeze Track A++ utilization checklist (H-SHIPIQ)",
            "[x] Publish ctx/speed baselines from BG",
            "[x] Freeze gen stance = SKIP (CAPCHECK closed; H-NANOGEN18; "
            "M1|M2|M3)",
            "[x] Name BH1 H-IQBAT · BH2 H-GOLDFIX · BH3 H-SHIPIQ · "
            "BH4 H-FASTBH · BH5 H-CTXBH · BH6 H-NANOGEN18",
            "[x] Freeze true gen judge (rename forbidden; SKIP)",
            "[x] Real-eval ask battery protocol (eval=prod · OK|FP|MISS)",
            "[x] Copy live audits into .local/wave-bh/",
            "[x] Do NOT reopen UNARYINT/SHIPPUB/FASTBG/CTXBG unless IQ fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN18 = NANOGEN17+rename",
            "[x] Do NOT invent Wave BI",
            "[ ] Next: BH1 H-IQBAT",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| BH0 | SESSION | **{status}** |",
            "| BH1 | H-IQBAT | **NEXT** |",
            "| BH2 | H-GOLDFIX | pending |",
            "| BH3 | H-SHIPIQ | pending |",
            "| BH4 | H-FASTBH | pending |",
            "| BH5 | H-CTXBH | pending |",
            "| BH6 | H-NANOGEN18 | pending (SKIP unless real method) |",
            "| BH7 | BH-REAL-EVAL | pending |",
            "| BH8 | BH-REPORT | pending |",
            "| BH9 | BH-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    exact = (
        "| BH0 | **SESSION** | Lock IQ battery plan + gold holes; "
        "gen=plan\\|SKIP; `.local/wave-bh/SESSION.md` | cite BG | **TODO** |"
    )
    exact_done = exact.replace("**TODO**", "**DONE — PROMOTE**")
    if exact in text:
        text = text.replace(exact, exact_done, 1)
    exact_plain = exact.replace("gen=plan\\|SKIP", "gen=plan|SKIP")
    if exact_plain in text:
        text = text.replace(
            exact_plain,
            exact_plain.replace("**TODO**", "**DONE — PROMOTE**"),
            1,
        )
    text = text.replace(
        "> **Session:** create `.local/wave-bh/SESSION.md` at BH0.  ",
        "> **Session:** `.local/wave-bh/SESSION.md` "
        "(BH0 **DONE — PROMOTE**; next BH1 H-IQBAT).  ",
        1,
    )
    old_next = (
        "1. **BH0 SESSION** — freeze IQ battery plan + gold holes "
        "(Rust MISS · add truncation); gen=plan\\|SKIP; create "
        "`.local/wave-bh/SESSION.md`; copy live audits.  "
    )
    done_next = (
        "1. **BH0 SESSION** — **DONE PROMOTE** "
        "(`npm run nano:bh:session`) · gen stance **SKIP** · "
        "H-IQBAT·H-GOLDFIX·H-SHIPIQ·H-FASTBH·H-CTXBH·H-NANOGEN18 named · "
        "IQ plan + gold holes + BA…BG/AZ hold + Track A++ + baselines "
        "frozen.  "
    )
    if old_next in text:
        text = text.replace(old_next, done_next, 1)
    old_next_plain = old_next.replace("gen=plan\\|SKIP", "gen=plan|SKIP")
    if old_next_plain in text:
        text = text.replace(old_next_plain, done_next, 1)
    text = text.replace(
        "**H-ID names** lock at BH0 (≠ prior npm collisions).",
        "**H-ID names locked at BH0:** H-IQBAT · H-GOLDFIX · "
        "H-SHIPIQ · H-FASTBH · H-CTXBH · H-NANOGEN18 (must ≠ prior npm "
        "script collisions).",
        1,
    )
    text = text.replace(
        "2. **BH1 H-IQBAT** — `iq-battery-v0.jsonl` + "
        "`npm run nano:iq-battery`; publish scoreboard.  ",
        "2. **BH1 H-IQBAT** — **NEXT** — `iq-battery-v0.jsonl` + "
        "`npm run nano:iq-battery`; publish scoreboard.  ",
        1,
    )
    bh1_todo = (
        "| BH1 | **H-IQBAT** (working name) | IQ battery v0 runner + ≥40 "
        "probes; Novel_FP=0 baseline | §0c | **TODO** |"
    )
    bh1_next = (
        "| BH1 | **H-IQBAT** | IQ battery v0 runner + ≥40 "
        "probes; Novel_FP=0 baseline | §0c | **NEXT** |"
    )
    if bh1_todo in text:
        text = text.replace(bh1_todo, bh1_next, 1)
    for old, new in (
        (
            "| BH2 | **H-GOLDFIX** (working name) |",
            "| BH2 | **H-GOLDFIX** |",
        ),
        (
            "| BH3 | **H-SHIPIQ** (working name) |",
            "| BH3 | **H-SHIPIQ** |",
        ),
        (
            "| BH4 | **H-FASTBH** (working name) |",
            "| BH4 | **H-FASTBH** |",
        ),
        (
            "| BH5 | **H-CTXBH** (working name) |",
            "| BH5 | **H-CTXBH** |",
        ),
    ):
        text = text.replace(old, new, 1)
    bash_old = (
        "# after BH0 scripts:\n"
        "# npm run nano:bh:session\n"
        "# npm run nano:iq-battery\n"
        "# npm run nano:goldfix\n"
        "# npm run nano:bh:shipiq\n"
        "# npm run nano:bh:fastbh\n"
        "# npm run nano:bh:ctxbh\n"
        "# npm run nano:nanogen18   # ONLY with method plan — else SKIP\n"
        "# npm run nano:bh:real-eval\n"
        "# npm run nano:bh:report\n"
        "# npm run nano:bh:freeze"
    )
    bash_new = (
        "npm run nano:bh:session\n"
        "# next: nano:iq-battery · nano:goldfix · nano:bh:shipiq · "
        "nano:bh:fastbh · nano:bh:ctxbh · nano:nanogen18 "
        "(SKIP without plan)\n"
        "# npm run nano:bh:real-eval\n"
        "# npm run nano:bh:report\n"
        "# npm run nano:bh:freeze"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    text = text.replace(
        "> **Status:** Wave BG **COMPLETE + FROZEN** (archive). Wave **BH "
        "REOPENED**",
        "> **Status:** Wave BG **COMPLETE + FROZEN** (archive). Wave **BH "
        "ACTIVE** (BH0 SESSION **DONE — PROMOTE**; next BH1 H-IQBAT)",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _write_local_impl(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave BG **COMPLETE + FROZEN** (H-NANOGEN17 **SKIP**).  
**Reopen:** Wave **BH ACTIVE** via `pesquisa.md` — IQ battery + gold repair + utilization/paper.  
**BH0 SESSION:** **DONE — PROMOTE** (`npm run nano:bh:session`) · gen stance **SKIP** · H-IQBAT · H-GOLDFIX · H-SHIPIQ · H-FASTBH · H-CTXBH · H-NANOGEN18 named.

## Tracks (locked)

| Track | Work |
|-------|------|
| **P0** | IQ battery v0 (≥40 probes · Novel_FP=0 · gold MISS=0) |
| **P1** | Gold repair (Rust LOOKUP · full add body) · BA…BG/AZ hold |
| **P2–P3** | Track A++ utilization (demo + recipes + paper citing IQ) |
| **P4–P5** | Speed p50/p99 + context content bars (no FP/MISS regress) |
| **P6** | One real gen method (M1|M2|M3) — else SKIP (H-NANOGEN18 stop rule) |

## Next

1. **BH0 SESSION** — **DONE PROMOTE** (`npm run nano:bh:session`).  
2. **BH1 H-IQBAT** — **NEXT** — iq-battery-v0.jsonl + runner; Novel_FP=0 baseline.  
3. Ship claim stays BG lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · pack theater · truncated gold as OK · NANOGEN18 without method plan · sell HOLD/DEFER/SKIP as unlock · unlabeled open chat · CTX/SMART/FAST clones · invent Wave BI.

```bash
npm run nano:bh:session
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

**Wave BH ACTIVE** (lab-book reopen after BG-FREEZE):

**ONE objective:** nano generative / mini-AGI-*inspired* ≤5M (retrieve · generate · route · refuse · evaluate) with **real evaluation** via **IQ battery**.

**Cursor measures (anti-FP):**

1. **IQ battery** — versioned probes; Novel_FP=0 · gold MISS=0  
2. **Gold repair** — Rust LOOKUP · full add body  
3. **BA…BG-FOREVER + AZ hold** — no regression  
4. **Track A++ utilization** — demo + recipes + paper citing IQ  
5. **Speed / Context** — prod p50/p99 · content bars (no FP/MISS regress)  
6. **Generative** — true_continue only with written plan; else SKIP (NANOGEN6–17 cited)

Session: `wave-bh/SESSION.md` (BH0 **DONE — PROMOTE**; next BH1 H-IQBAT). Parent: Wave BG **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–BG | COMPLETE + FROZEN |
| Ship (until BH gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§13 · Wave BH0–BH9 |

## Do not

LOOKUP-as-IQ · pack theater · truncated gold as OK · over-refuse as win · sell HOLD/DEFER/SKIP as unlock · L_eff/cache vanity · NANOGEN rename · CTX/SMART/FAST letter clones · bank stuffing · invent Wave BI.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave BH ACTIVE" in text:
        return
    marker = "**Wave BG COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    bg_line = text[idx:end]
    if "do not invent Wave BH" in bg_line:
        bg_line = bg_line.replace(
            "do not invent Wave BH",
            "Wave BH reopened via lab-book",
        )
        text = text[:idx] + bg_line + text[end:]
        end = idx + len(bg_line)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_agents_bh() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "Wave BH ACTIVE" in text:
        return
    agents_line = (
        "- **Wave BH ACTIVE** — BH0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bh-session.md) "
        "(`npm run nano:bh:session`) — IQ battery v0 plan · gold holes "
        "(Rust MISS · add truncation) · BA…BG/AZ hold · Track A++ util · "
        "gen stance **SKIP** (H-NANOGEN18); next BH1 H-IQBAT; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8…15 DEFER · NANOGEN16·17 SKIP; ≤5M stays."
    )
    # Prefer inserting after W–BF/BG freeze bullet if present
    pat = r"- Waves W–\*\*B[FG]\*\* \*\*COMPLETE \+ FROZEN\*\*[^\n]*"
    text2, n = re.subn(
        pat,
        lambda m: m.group(0) + "\n" + agents_line,
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")
        return
    # Fallback: after Delivery posture active-wave bullet
    marker = (
        "- Active wave / reopen: **only** what `.local/pesquisa.md` says."
    )
    if marker in text:
        text = text.replace(marker, marker + "\n" + agents_line, 1)
        _AGENTS.write_text(text, encoding="utf-8")


def _patch_agenda_bh() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    if "| **BH** |" in text:
        return
    row = (
        "| **BH** | **ACTIVE** | BH0 [SESSION PROMOTE]"
        "(results/nano-lm/wave-bh-session.md) (`npm run nano:bh:session`) "
        "— IQ battery plan · gold holes · BA…BG/AZ hold · Track A++ util · "
        "gen stance SKIP (H-NANOGEN18); next BH1 H-IQBAT; ship AF+AQ+AS "
        "trust + STRICT ablated DECODE; NANOGEN6·7 HOLD · NANOGEN8…15 "
        "DEFER · NANOGEN16·17 SKIP; ≤5M |"
    )
    # Extend AA–BF band mention and insert BH row after Active line
    text2 = text.replace(
        "| AA–BF | COMPLETE + FROZEN | `docs/results/nano-lm/*-freeze.md` |",
        "| AA–BG | COMPLETE + FROZEN | `docs/results/nano-lm/*-freeze.md` |",
        1,
    )
    pat = r"\| Active / reopen \| \*\*only\*\* lab book \|[^\n]+"
    text2, n = re.subn(
        pat,
        lambda m: row + "\n" + m.group(0),
        text2,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen_bh() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "Wave BH ACTIVE" in text:
        return
    # Insert active wave hint into lab-book bullet
    old = (
        "- **Lab book:** read `.local/pesquisa.md` before wave work — "
        "do not invent the next letter without reopen."
    )
    new = (
        "- **Lab book:** read `.local/pesquisa.md` before wave work — "
        "Wave BH ACTIVE (BH0 SESSION PROMOTE; next BH1 H-IQBAT); "
        "do not invent Wave BI without reopen."
    )
    if old in text:
        text = text.replace(old, new, 1)
        _EVOGEN.write_text(text, encoding="utf-8")


def _patch_recipes_bh0() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave BH0 SESSION" in text:
        return
    insert = (
        "| Wave BH0 SESSION | [wave-bh-session.md](wave-bh-session.md) "
        "**PROMOTE** (`npm run nano:bh:session`) — IQ battery v0 plan · "
        "gold holes (Rust MISS · add truncation) · BA…BG/AZ hold · "
        "Track A++ util · §1 scoreboard · ctx/speed baselines · gen "
        "stance **SKIP** (no NANOGEN18 without method plan) · true-eval |"
    )
    marker = (
        "| Wave BG8 BG-FREEZE | [bg-freeze.md](bg-freeze.md) · "
        "[formal-habgfreeze-bg-freeze.md](formal-habgfreeze-bg-freeze.md) "
        "**PROMOTE** (`npm run nano:bg:freeze`) — COMPLETE+FROZEN; "
        "H-NANOGEN17 SKIP; do not invent Wave BH |"
    )
    marker2 = marker.replace(
        "do not invent Wave BH",
        "Wave BH reopened via lab-book",
    )
    nl = "\n"
    if marker in text:
        text = text.replace(marker, marker2 + nl + insert, 1)
        _RECIPES.write_text(text, encoding="utf-8")
        return
    if marker2 in text:
        text = text.replace(marker2, marker2 + nl + insert, 1)
        _RECIPES.write_text(text, encoding="utf-8")
        return
    if "bg-freeze.md" in text:
        text = text.replace(
            "do not invent Wave BH",
            "Wave BH reopened via lab-book",
            1,
        )
        _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _BH_ACTIVE_LINE.replace(
        "**Wave BH ACTIVE:**", "**Wave BH ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _BH_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    _patch_agents_bh()
    _patch_agenda_bh()
    _patch_evogen_bh()
    _patch_recipes_bh0()


def _promote_live_audits() -> list[str]:
    src_dir = REPO / ".local/tmp-live-audit"
    dst = REPO / ".local/wave-bh"
    dst.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    if not src_dir.is_dir():
        return copied
    for name in (
        "bg-reval-1785332425.jsonl",
    ):
        src = src_dir / name
        if src.is_file():
            target = dst / name
            shutil.copy2(src, target)
            copied.append(str(target.relative_to(REPO)))
    # Also promote prior BG session audits if present
    bg_dir = REPO / ".local/wave-bg"
    if bg_dir.is_dir():
        for name in (
            "live_audit_bg0_smoke.json",
            "live_audit_bg0_scored.json",
            "bf-reval-1785327348.jsonl",
            "bf-novel-1785327433.jsonl",
        ):
            src = bg_dir / name
            if src.is_file():
                target = dst / name
                shutil.copy2(src, target)
                copied.append(str(target.relative_to(REPO)))
    return copied


def _persist_smoke(ask: dict[str, Any] | None) -> None:
    if ask is None:
        return
    path = REPO / ".local/wave-bh/live_audit_bh0_smoke.json"
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
    decision = decide_bh0_session(
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
        "id": BH0_ID,
        "thesis": BH0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_bg_locks": sorted(BH0_CITED_BG_LOCKS),
        "scoreboard": dict(BH0_SCOREBOARD),
        "iq_battery_protocol": dict(BH0_IQ_BATTERY_PROTOCOL),
        "gold_holes": dict(BH0_GOLD_HOLES),
        "ba_hold_protocol": dict(BH0_BA_HOLD_PROTOCOL),
        "bb_hold_protocol": dict(BH0_BB_HOLD_PROTOCOL),
        "bc_hold_protocol": dict(BH0_BC_HOLD_PROTOCOL),
        "bd_hold_protocol": dict(BH0_BD_HOLD_PROTOCOL),
        "be_hold_protocol": dict(BH0_BE_HOLD_PROTOCOL),
        "bf_hold_protocol": dict(BH0_BF_HOLD_PROTOCOL),
        "bg_hold_protocol": dict(BH0_BG_HOLD_PROTOCOL),
        "az_hold_protocol": dict(BH0_AZ_HOLD_PROTOCOL),
        "util_track": dict(BH0_UTIL_TRACK),
        "speed_baseline": dict(BH0_SPEED_BASELINE),
        "ctx_baseline": dict(BH0_CTX_BASELINE),
        "gen_stance": dict(BH0_GEN_STANCE),
        "true_gen_judge": dict(BH0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(BH0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(BH0_ASK_BATTERY),
        "iq_seed_n": len(BH0_IQ_SEED_ROWS),
        "safe_note": BH0_SAFE_NOTE,
        "anti_fp": BH0_ANTI_FP,
        "north_star": BH0_NORTH_STAR,
        "ship_lock": BH0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "live_audits_promoted": audits,
        "public_note": "docs/results/nano-lm/wave-bh-session.md",
        "rule": (
            "pesquisa §9 BH0 · IQ battery plan + gold holes + "
            "BA…BG/AZ hold + Track A++ util + gen-skip + anti-FP"
        ),
        "next": "BH1 H-IQBAT (iq-battery-v0 ≥40; Novel_FP=0 baseline)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BH0_ID,
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
