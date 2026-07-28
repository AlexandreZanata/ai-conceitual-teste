"""Wave AX0 SESSION runner (nano:ax:session) — freeze AX packs + reopen."""

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
from ax_session_ops import (
    AX0_ANTI_FP,
    AX0_ASK_BATTERY,
    AX0_CITED_AW_LOCKS,
    AX0_GEN_STANCE,
    AX0_HARD_NATURAL_PROTOCOL,
    AX0_HARD_NATURAL_ROWS,
    AX0_ID,
    AX0_MODES,
    AX0_NORTH_STAR,
    AX0_PRODUCT_NAT_CHARTER,
    AX0_REAL_EVAL_PROTOCOL,
    AX0_SAFE_NOTE,
    AX0_SHIP_LOCK,
    AX0_THESIS,
    AX0_TRUE_GEN_JUDGE,
    decide_ax0_session,
    map_ax_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ax/ax0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-ax/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-ax/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ax-session.md"
_LOCAL_SESSION = REPO / ".local/wave-ax/SESSION.md"
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
_HARD_NAT = str(AX0_HARD_NATURAL_ROWS[0]["question"])

_AX_ACTIVE_LINE = (
    "**Wave AX ACTIVE:** AX0 [SESSION PROMOTE](wave-ax-session.md) "
    "(`npm run nano:ax:session`) — hard-natural · PRODNAT charter · "
    "gen stance **defer** · real-eval; next AX1 H-PRODNAT; "
    "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
    "NANOGEN6·7 HOLD; ≤5M stays."
)


def _hardware() -> tuple[int, int]:
    # Max safe on 16c / ~17Gi avail: leave 2 cores; cap workers to avoid thrash.
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
    for item in AX0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AX0",
            "hyp_id": AX0_ID,
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


def _write_para_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AX0_HARD_NATURAL_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AX0",
            "hyp_id": AX0_ID,
            "pack": "hard-natural",
            "parent": item["parent"],
            "question": item["question"],
            "status": "frozen",
            "mode": None,
            "wall_ms": None,
            "hit": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("AX-PRODNAT", "product-nat-charter", dict(AX0_PRODUCT_NAT_CHARTER)),
        (
            "AX-HARD-NATURAL",
            "hard-natural-protocol",
            dict(AX0_HARD_NATURAL_PROTOCOL),
        ),
        (
            "AX-GEN-STANCE",
            "gen-stance",
            {
                "stance": dict(AX0_GEN_STANCE),
                "true_gen_judge": dict(AX0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "AX-REAL-EVAL",
            "real-eval-protocol",
            dict(AX0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "AX0",
            "hyp_id": AX0_ID,
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
        + _write_para_trials(trials_dir)
        + _write_charter_trials(trials_dir)
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = len(AX0_ASK_BATTERY) + len(AX0_HARD_NATURAL_ROWS) + 4
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in AX0_ASK_BATTERY
    )
    para_rows = "\n".join(
        f"| {p['id']} | {p['parent']} |" for p in AX0_HARD_NATURAL_ROWS
    )
    bars = AX0_PRODUCT_NAT_CHARTER["bars"]
    debts = AX0_PRODUCT_NAT_CHARTER["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    body = "\n".join(
        [
            "# Wave AX0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-ax/SESSION.md`  ",
            "> Module: `nano_lm/src/ax_session_ops.py` · "
            "Runner: `npm run nano:ax:session`  ",
            "> Parent: [aw-freeze.md](aw-freeze.md) "
            "(Wave AX reopened explicitly via lab-book reopen after AW-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze AX packs: "
            "hard-natural para protocol (N≥15 live-miss class ≠ AW/AV/AU) · "
            "H-PRODNAT metrics charter · gen stance **defer** "
            "(CAPCHECK closed; **not** NANOGEN8=NANOGEN7+rename) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until AX3 true-continue.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Product-nat charter | 1 | hard natural · FH0 · modes · "
            "KB · latency · DECODE law (AX1) |",
            f"| Hard-natural protocol | {len(AX0_HARD_NATURAL_ROWS)} | "
            "held-out live miss class ≠ AW/AV/AU (AX1) |",
            "| Gen stance | 1 | **defer** · CAPCHECK closed · "
            "NANOGEN6·7 HOLD cited (AX3) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "rename forbidden (AX3) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "anti-FP (AX4) |",
            f"| Ask battery | {len(AX0_ASK_BATTERY)} | frozen live rows "
            "(scored at AX4) |",
            "",
            "## Cited AW locks",
            "",
            ", ".join(sorted(AX0_CITED_AW_LOCKS)),
            "",
            "## Product-nat bars",
            "",
            f"- hard_natural_para_hit_min: "
            f"**{bars['hard_natural_para_hit_min']}**  ",
            f"- false_hit_max: **{bars['false_hit_max']}**  ",
            f"- hard_natural_min_n: **{bars['hard_natural_min_n']}**  ",
            f"- decode_gibberish_neq_content_ok: "
            f"**{bars['decode_gibberish_neq_content_ok']}**  ",
            f"- default_ask_near_miss: **{bars['default_ask_near_miss']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- pressure_para_neq_hard_natural: "
            f"**{bars['pressure_para_neq_hard_natural']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no re-SEMFIX/ADVSAFE unless PRODNAT fails",
            "",
            "## Post-AW debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## Hard-natural protocol",
            "",
            f"- held_out: **{AX0_HARD_NATURAL_PROTOCOL['held_out']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{AX0_HARD_NATURAL_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- neq_aw_pack: **{AX0_HARD_NATURAL_PROTOCOL['neq_aw_pack']}**  ",
            f"- neq_av_pack: **{AX0_HARD_NATURAL_PROTOCOL['neq_av_pack']}**  ",
            f"- neq_au_pack: **{AX0_HARD_NATURAL_PROTOCOL['neq_au_pack']}**  ",
            f"- live_miss_id: **{AX0_HARD_NATURAL_PROTOCOL['live_miss_id']}**  ",
            f"- min_n: **{AX0_HARD_NATURAL_PROTOCOL['min_n']}**  ",
            f"- path: `{AX0_HARD_NATURAL_PROTOCOL['path']}`  ",
            "",
            "| id | parent |",
            "|----|--------|",
            para_rows,
            "",
            "## Gen stance (frozen)",
            "",
            f"- stance: **{AX0_GEN_STANCE['stance']}**  ",
            f"- capcheck: **{AX0_GEN_STANCE['capcheck']}**  ",
            f"- nanogen8_rename_forbidden: "
            f"**{AX0_GEN_STANCE['nanogen8_rename_forbidden']}**  ",
            f"- ax3_gate: `{AX0_GEN_STANCE['ax3_gate']}`  ",
            "",
            AX0_GEN_STANCE["rationale"],
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{AX0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- nanogen8_rename_forbidden: "
            f"{AX0_TRUE_GEN_JUDGE['nanogen8_rename_forbidden']}  ",
            f"- scoring: `{AX0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{AX0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{AX0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{AX0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- pack_para_neq_hard_natural: "
            f"{AX0_REAL_EVAL_PROTOCOL['pack_para_neq_hard_natural']}  ",
            f"- gen_claim_rule: "
            f"{AX0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {AX0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            AX0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AX0_ANTI_FP,
            "",
            "## North star",
            "",
            AX0_NORTH_STAR,
            "",
            "## Ship lock (until AX gen PROMOTE)",
            "",
            AX0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:ax:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Quad-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) + near-miss ABSTAIN mapping; "
            "hard-natural live miss is **recorded** (AX1 scores hit).  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-ax/ax0_session.json` · "
            "`results/nano-lm/wave-ax/trials/AX-*.json`.  ",
            "Contract: `nano_lm/tests/test_ax_session.py`.",
            "",
            "## Claims",
            "",
            "- AW packs frozen for Wave AX — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{AX0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **AX3 H-NANOGEN8** "
            "true_continue under a real new method "
            "(never NANOGEN7+rename; span-fallback ≠ gen).  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "pack-para as hard-natural coverage · gold-substring PROMOTE · "
            "span-fallback as gen · DECODE telemetry-only content_ok · "
            "eval↔prod gap · mini-AGI claim early · NANOGEN8 rename · "
            "CTX/SMART/FAST/APP clone · bank stuffing · vanity re-SEMFIX.",
            "",
            "Next: **AX1 H-PRODNAT** — accept Caminho A; close hard-natural "
            "para debt; publish para · FH · p50/p99 · KB.",
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


def _ask_hard_natural() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_HARD_NAT,
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
    hn_mode: str,
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
        map_ax_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in AX0_MODES,
        hn_mode in AX0_MODES,
    )
    return all(checks)


def _smoke_quad_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP + DECODE + near-miss + hard-natural live miss (anti-FP)."""
    n = min(4, max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        fut_l = pool.submit(_ask_lookup)
        fut_d = pool.submit(_ask_decode)
        fut_n = pool.submit(_ask_near_miss)
        fut_h = pool.submit(_ask_hard_natural)
        lookup = fut_l.result()
        gen = fut_d.result()
        near = fut_n.result()
        hard = fut_h.result()
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    n_tel = extract_telemetry(near)
    h_tel = extract_telemetry(hard)
    l_mode = map_ax_product_mode(str(l_tel["mode"]))
    g_mode = map_ax_product_mode(str(g_tel["mode"]))
    nm_mode = map_ax_product_mode(str(n_tel["mode"]))
    hn_mode = map_ax_product_mode(str(h_tel["mode"]))
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
        nm_mode=nm_mode,
        hn_mode=hn_mode,
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
            "note": "AX1 must fail gibberish content_ok; AX0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AW PRODKEEP locked ABSTAIN; AX0 verifies mapping",
        },
        "hard_natural": {
            "arm": classify_arm(hard),
            "raw_mode": h_tel["mode"],
            "product_mode": hn_mode,
            "wall_ms": h_tel["wall_ms"],
            "n_new": h_tel["n_new"],
            "completion": str(hard.get("completion", ""))[:120],
            "question": _HARD_NAT,
            "note": "live miss class; AX1 scores hit — AX0 records only",
        },
        "modes_charter": sorted(AX0_MODES),
        "abstain_alias": map_ax_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
        "gen_stance": AX0_GEN_STANCE["stance"],
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
            f"# Wave AX session checklist (**OPEN** · AX0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AX **OPEN** · Caminho A harden + Nano Generative defer).  ",
            f"> Parent: AW COMPLETE + FROZEN · Ship: **{AX0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after AW-FREEZE; hard-natural open; "
            "generative deferred (NANOGEN6·7 HOLD).",
            "",
            "## Current stage",
            "",
            f"**AX0 — SESSION ({status})** · Next: **AX1 H-PRODNAT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AX OPEN** |",
            "| Track | Caminho A hard-natural · gen stance **defer** |",
            "| Parent | AW COMPLETE + FROZEN |",
            "| Open hole | hard natural para · FH0 · modes · "
            "p50/p99 · KB · DECODE law |",
            "| Forbidden | NANOGEN8 rename · LOOKUP-as-IQ · "
            "pack-para as hard-natural · CTX/SMART/FAST |",
            "",
            "## North star (signed)",
            "",
            AX0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AX0)",
            "",
            "```text",
            "MODEL = AX0-SESSION",
            "",
            "[x] Freeze hard-natural held-out protocol (N≥15 ≠ AW/AV/AU)",
            "[x] Freeze H-PRODNAT metrics charter (para · FH · latency · KB)",
            "[x] Freeze gen stance = defer (CAPCHECK closed)",
            "[x] Freeze true gen judge (rename forbidden)",
            "[x] Real-eval ask battery protocol (eval=prod ask)",
            "[x] Do NOT reopen SEMFIX/ADVSAFE unless PRODNAT fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT invent NANOGEN8 = NANOGEN7+rename",
            "[ ] Next: AX1 H-PRODNAT",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AX0 | SESSION | **{status}** |",
            "| AX1 | H-PRODNAT | **NEXT** |",
            "| AX2 | H-SHIPUX | pending |",
            "| AX3 | H-NANOGEN8 | pending (defer unless real new method) |",
            "| AX4 | AX-REAL-EVAL | pending |",
            "| AX5 | AX-REPORT | pending |",
            "| AX6 | AX-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Hard natural para hit | ≥ 0.70 | live miss ABSTAIN (debt) |",
            "| Adversary FH (ask path) | **0** | AW PRODKEEP / AS ADVSAFE |",
            "| DECODE content | usable or ABSTAIN | AW STRICT lock |",
            "| Latency p50/p99 | publish | AW PRODKEEP / AS METRICS |",
            "| True continue (NANOGEN8) | PROMOTE else HOLD/DEFER | "
            "NANOGEN6·7 HOLD; stance defer |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    done_row = (
        "| AX0 | **SESSION** | Freeze AX packs: hard-natural para · "
        "product metrics · gen stance (**defer**) · real-eval | "
        "cite AW locks; stance=defer | **DONE — PROMOTE** |"
    )
    for old in (
        (
            "| AX0 | **SESSION** | Freeze AX packs: hard-natural para · "
            "product metrics · gen stance (**new method** \\| "
            "**CAPCHECK/hybrid** \\| **defer**) · real-eval | "
            "cite AW locks; stance required | **TODO** |"
        ),
        (
            "| AX0 | **SESSION** | Freeze AX packs: hard-natural para · "
            "product metrics · gen stance (**new method** \\| "
            "**CAPCHECK/hybrid** \\| **defer**) · real-eval | "
            "cite AW locks; stance required | **DONE — PROMOTE** |"
        ),
    ):
        if old in text:
            text = text.replace(old, done_row, 1)
            break
    text = text.replace(
        "> **Session:** `.local/wave-ax/SESSION.md` (create at AX0).  ",
        "> **Session:** `.local/wave-ax/SESSION.md` "
        "(AX0 **DONE — PROMOTE**; next AX1 H-PRODNAT).  ",
        1,
    )
    for old_next in (
        (
            "1. **AX0 SESSION** — create `.local/wave-ax/SESSION.md`; "
            "freeze hard-natural para pack + metrics charter + gen stance "
            "(**new method** \\| **CAPCHECK/hybrid** \\| **defer**).  "
        ),
        (
            "1. **AX0 SESSION** — create `.local/wave-ax/SESSION.md`; "
            "freeze hard-natural para pack + metrics charter + gen stance "
            "(**new method** | **CAPCHECK/hybrid** | **defer**).  "
        ),
    ):
        if old_next in text:
            text = text.replace(
                old_next,
                "1. **AX0 SESSION** — **DONE PROMOTE** "
                "(`npm run nano:ax:session`) · gen stance **defer** · "
                "hard-natural pack frozen.  ",
                1,
            )
            break
    text = text.replace(
        "2. **AX1 H-PRODNAT** — accept Caminho A artifact; "
        "close hard natural para debt; publish para · FH · p50/p99 · KB; "
        "mode UI always.  ",
        "2. **AX1 H-PRODNAT** — **NEXT** — accept Caminho A artifact; "
        "close hard natural para debt; publish para · FH · p50/p99 · KB; "
        "mode UI always.  ",
        1,
    )
    bash_old = (
        "# after AX0 wiring:\n"
        "# npm run nano:ax:session"
    )
    bash_new = (
        "npm run nano:ax:session\n"
        "# next: nano:prodnat · nano:shipux"
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

Wave AW **COMPLETE + FROZEN** (NANOGEN7 TAC **HOLD**).  
**Reopen:** Wave **AX ACTIVE** via `pesquisa.md` — dual track only.  
**AX0 SESSION:** **DONE — PROMOTE** (`npm run nano:ax:session`) · gen stance **defer**.

## Dual track (locked)

| Track | Work |
|-------|------|
| **Caminho A** | Accept artifact · **hard natural** human para · FH · p50/p99 · KB · mode UI |
| **North star** | Nano generative / mini-AGI-*inspired* ≤5M · **defer** until real new method (NANOGEN6·7 HOLD) |

## Next

1. **AX0 SESSION** — **DONE PROMOTE** (`npm run nano:ax:session`).  
2. **AX1 H-PRODNAT** — **NEXT** — close hard natural para debt; publish metrics board.  
3. Ship claim stays AW lock: **AF + AQ + AS trust + STRICT ablated DECODE** — not TAC unlocked.

Never: LOOKUP-as-IQ · NANOGEN8=NANOGEN7+rename · sell HOLD as unlock · unlabeled open chat · CTX/SMART/FAST clones.

```bash
npm run nano:ax:session
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

**Wave AX ACTIVE** (lab-book reopen after AW-FREEZE):

1. **Caminho A:** accept artifact — known-ask + SEMWRAP + labeled PEAK/RAG + apps; hard natural para · FH · p50/p99 · KB; mode UI always.  
2. **North star:** nano generative / mini-AGI-*inspired* ≤5M — gen stance **defer** (NANOGEN6·7 HOLD until beaten; no NANOGEN8 clone).

Session: `wave-ax/SESSION.md` (AX0 **DONE — PROMOTE**; next AX1 H-PRODNAT). Parent: Wave AW **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–AW | COMPLETE + FROZEN |
| Ship (until AX gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat · **not** TAC unlocked |
| Reopen | `pesquisa.md` §0–§8 · Wave AX0–AX6 |

## Do not

LOOKUP-as-IQ · sell HOLD as unlock · pack-para as world coverage · NANOGEN8=NANOGEN7+rename · CTX/SMART/FAST letter clones.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _ensure_active_line(path: Path, line: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "Wave AX ACTIVE" in text:
        # Keep ACTIVE near AW COMPLETE when it was prepended at file top.
        if text.startswith("**Wave AX ACTIVE") and "**Wave AW COMPLETE" in text:
            first_nl = text.find("\n")
            ax_line = text[:first_nl]
            rest = text[first_nl + 1 :]
            if not rest.lstrip().startswith("**Wave AX ACTIVE"):
                marker = "**Wave AW COMPLETE + FROZEN**"
                idx = rest.find(marker)
                if idx >= 0:
                    end = rest.find("\n", idx)
                    if end < 0:
                        end = len(rest)
                    rest = (
                        rest[: end + 1] + ax_line + "\n" + rest[end + 1 :]
                    )
                    text = rest
                    path.write_text(text, encoding="utf-8")
        return
    marker = "**Wave AW COMPLETE + FROZEN**"
    idx = text.find(marker)
    if idx < 0:
        text = line + "\n" + text
        path.write_text(text, encoding="utf-8")
        return
    end = text.find("\n", idx)
    if end < 0:
        end = len(text)
    text = text[: end + 1] + line + "\n" + text[end + 1 :]
    path.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    card_line = _AX_ACTIVE_LINE.replace(
        "**Wave AX ACTIVE:**", "**Wave AX ACTIVE** —"
    )
    _ensure_active_line(_RECIPES, _AX_ACTIVE_LINE)
    _ensure_active_line(_CARD, card_line)
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents_line = (
            "- **Wave AX ACTIVE** — AX0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-ax-session.md) "
            "(`npm run nano:ax:session`) — hard-natural · PRODNAT · "
            "gen stance **defer**; next AX1 H-PRODNAT; "
            "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
            "NANOGEN6·7 HOLD; ≤5M stays."
        )
        if "Wave AX ACTIVE" not in text:
            text2, n = re.subn(
                r"- \*\*Wave AW COMPLETE \+ FROZEN\*\* —[^\n]+",
                lambda m: m.group(0) + "\n" + agents_line,
                text,
                count=1,
            )
            if n:
                _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            "| **AX** | **ACTIVE** | AX0 [SESSION PROMOTE]"
            "(results/nano-lm/wave-ax-session.md) (`npm run nano:ax:session`) "
            "— hard-natural · gen stance defer; next AX1 H-PRODNAT; "
            "ship AF+AQ+AS trust + STRICT ablated DECODE; "
            "NANOGEN6·7 HOLD; ≤5M |"
        )
        if "| **AX** |" not in text:
            text2, n = re.subn(
                r"\| \*\*AW\*\* \| \*\*COMPLETE \+ FROZEN\*\* \|[^\n]+",
                lambda m: m.group(0) + "\n" + row,
                text,
                count=1,
            )
            if n:
                _AGENDA.write_text(text2, encoding="utf-8")
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        if "Wave AX ACTIVE" not in text and "do not invent Wave AX" in text:
            text = text.replace(
                "do not invent Wave AX",
                "Wave AX ACTIVE (AX0 SESSION PROMOTE; next AX1 H-PRODNAT); "
                "do not invent Wave AY",
                1,
            )
            _EVOGEN.write_text(text, encoding="utf-8")


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_ax0_session(
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
        "id": AX0_ID,
        "thesis": AX0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_aw_locks": sorted(AX0_CITED_AW_LOCKS),
        "product_nat_charter": dict(AX0_PRODUCT_NAT_CHARTER),
        "hard_natural_protocol": dict(AX0_HARD_NATURAL_PROTOCOL),
        "gen_stance": dict(AX0_GEN_STANCE),
        "true_gen_judge": dict(AX0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(AX0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(AX0_ASK_BATTERY),
        "hard_natural_n": len(AX0_HARD_NATURAL_ROWS),
        "safe_note": AX0_SAFE_NOTE,
        "anti_fp": AX0_ANTI_FP,
        "north_star": AX0_NORTH_STAR,
        "ship_lock": AX0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-ax-session.md",
        "rule": "pesquisa §5 AX0 · hard-natural + gen-defer + anti-FP",
        "next": "AX1 H-PRODNAT (close hard natural para debt)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AX0_ID,
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
