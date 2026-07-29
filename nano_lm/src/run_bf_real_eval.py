"""Wave BF6 BF-REAL-EVAL runner — product+util+ctx+speed + live ask; gen if NANOGEN16 PROMOTE."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bf_real_eval_ops import (
    ASK_BATTERY,
    BF_REAL_EVAL_ANTI_FP,
    BF_REAL_EVAL_CLAIM,
    BF_REAL_EVAL_ID,
    BF_REAL_EVAL_SAFE_NOTE,
    BF_REAL_EVAL_THESIS,
    LOOKUP_KINDS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_bf_real_eval,
    force_abstain_row,
    near_miss_should_abstain,
)
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bf/bf_real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bf/real_eval_trials"
_PREDINT = REPO / "results/nano-lm/wave-bf/predint_summary.json"
_SHIPUSE2 = REPO / "results/nano-lm/wave-bf/shipuse2_summary.json"
_FASTBF = REPO / "results/nano-lm/wave-bf/fastbf_summary.json"
_CTXBF = REPO / "results/nano-lm/wave-bf/ctxbf_summary.json"
_NANOGEN16 = REPO / "results/nano-lm/wave-bf/nanogen16_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bf/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bf-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-bf/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_PEAK_SOURCE = "rust-book-ch04-01"


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


def _hardware() -> tuple[int, int]:
    # 16c / ~31Gi: leave ≥6 cores free under mem pressure; cap workers.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(6, max(3, cpus - 6))
    return threads, workers


def _load_decision(path: Path) -> str:
    if not path.is_file():
        return "MISSING"
    data = json.loads(path.read_text(encoding="utf-8"))
    return str(data.get("decision", "MISSING"))


def _load_board(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    board = data.get("board")
    return dict(board) if isinstance(board, dict) else {}


def _peak_row(*, curated: Path, question: str) -> dict[str, Any]:
    meta = _BY_ID.get(_PEAK_SOURCE)
    if meta is None:
        raise ValueError(f"unknown source_id: {_PEAK_SOURCE}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    for _ in range(2):
        fastbase_generate(question=question, chunks=chunks, doc=doc)
    payload = fastbase_generate(question=question, chunks=chunks, doc=doc)
    row = attach_shipreal(dict(payload))
    row["question"] = question
    return row


def _decode_row(*, root: Path, curated: Path, question: str) -> dict[str, Any]:
    _EMPTY_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _EMPTY_BANK.is_file():
        _EMPTY_BANK.write_text("", encoding="utf-8")
    payload = ask_once(
        question=question,
        root=root,
        seed=1,
        wrap=True,
        bank_path=_EMPTY_BANK,
        curated_root=curated,
        abstain=True,
    )
    row = attach_shipreal(dict(payload))
    row["decode_wrap_miss"] = True
    return row


def _ask_row(
    *,
    item: dict[str, str],
    root: Path,
    bank: Path,
    curated: Path,
) -> dict[str, Any]:
    kind = str(item["kind"])
    q = str(item["question"])
    if kind == "labeled_peak":
        payload = _peak_row(curated=curated, question=q)
    elif kind in {"decode_content", "decode_gibberish_bar"}:
        payload = _decode_row(root=root, curated=curated, question=q)
    elif kind in LOOKUP_KINDS:
        payload = ask_once(
            question=q,
            root=root,
            seed=0,
            wrap=True,
            semwrap=kind in {"overrefuse_gold", "utilization_smoke"},
            bank_path=bank,
            curated_root=curated,
            abstain=True,
        )
        payload = attach_shipreal(dict(payload))
    else:
        payload = ask_once(
            question=q,
            root=root,
            seed=0,
            wrap=True,
            semwrap=True,
            bank_path=bank,
            curated_root=curated,
            abstain=True,
        )
        payload = attach_shipreal(dict(payload))
        if kind == "near_miss" and near_miss_should_abstain(
            question=q,
            completion=str(payload.get("completion", "")),
            product_mode=str(payload.get("product_mode", "")),
        ):
            payload = attach_shipreal(force_abstain_row(dict(payload)))
            payload["near_miss_refuse"] = True
    content_ok = content_matches_mode(payload)
    return {
        "id": item["id"],
        "kind": kind,
        "expect_mode": item["expect_mode"],
        "question": q,
        "mode": payload.get("mode"),
        "product_mode": payload.get("product_mode"),
        "modeui_line": payload.get("modeui_line"),
        "completion": str(payload.get("completion", ""))[:160],
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "abstained": payload.get("abstained"),
        "near_miss_refuse": payload.get("near_miss_refuse", False),
        "content_ok": content_ok,
    }


def _run_battery(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    workers: int,
) -> list[dict[str, Any]]:
    def _one(item: dict[str, str]) -> dict[str, Any]:
        return _ask_row(item=item, root=root, bank=bank, curated=curated)

    items = [dict(p) for p in ASK_BATTERY]
    serial_kinds = {"labeled_peak", "decode_content", "decode_gibberish_bar"}
    serial = [i for i in items if i["kind"] in serial_kinds]
    rest = [i for i in items if i["kind"] not in serial_kinds]
    out: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(workers, len(rest) or 1)) as pool:
        out.extend(list(pool.map(_one, rest)))
    for item in serial:
        out.append(_one(item))
    by_id = {str(r["id"]): r for r in out}
    return [by_id[str(p["id"])] for p in ASK_BATTERY]


def _write_public(
    *,
    decision: str,
    pillars: dict[str, str],
    battery: list[dict[str, Any]],
    claim: str,
    nano_board: dict[str, Any],
    wall_s: float,
    threads: int,
    workers: int,
) -> None:
    status = decision.split("(", 1)[0].strip()
    n_pass = sum(1 for t in battery if battery_row_ok(t))
    bat_rows = [
        f"| {t['id']} | {t['kind']} | **{t.get('product_mode')}** | "
        f"`{t.get('expect_mode')}` | "
        f"{'PASS' if battery_row_ok(t) else 'FAIL'} |"
        for t in battery
    ]
    tc = nano_board.get("true_continue_mean", "n/a")
    body = "\n".join(
        [
            f"# BF-REAL-EVAL — product+util+ctx+speed + live battery "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §1 · §9 BF6 · Session: "
            "`.local/wave-bf/SESSION.md`  ",
            "> Parents: [formal-hpredint-predint.md](formal-hpredint-predint.md) · "
            "[formal-hshipuse2-shipuse2.md](formal-hshipuse2-shipuse2.md) · "
            "[formal-hfastbf-fastbf.md](formal-hfastbf-fastbf.md) · "
            "[formal-hctxbf-ctxbf.md](formal-hctxbf-ctxbf.md) · "
            "[formal-hnanogen16-nanogen16.md](formal-hnanogen16-nanogen16.md)  ",
            "> Module: `nano_lm/src/bf_real_eval_ops.py` · "
            "Runner: `npm run nano:bf:real-eval`",
            "",
            "## Hypothesis",
            "",
            BF_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| BF1 H-PREDINT | **{pillars.get('predint')}** |",
            f"| BF2 H-SHIPUSE2 | **{pillars.get('shipuse2')}** |",
            f"| BF3 H-FASTBF | **{pillars.get('fastbf')}** |",
            f"| BF4 H-CTXBF | **{pillars.get('ctxbf')}** |",
            f"| BF5 H-NANOGEN16 | **{pillars.get('nanogen16')}** "
            f"(true_continue_mean={tc}) |",
            f"| Live ask battery | "
            f"**{'PASS' if battery_pass(battery) else 'FAIL'}** "
            f"({n_pass}/{len(battery)}) |",
            f"| Ship claim | `{claim}` |",
            f"| Decision | **{status}** |",
            "",
            "## Live ask battery",
            "",
            "| ID | Kind | product_mode | expect | Row |",
            "|----|------|--------------|--------|-----|",
            *bat_rows,
            "",
            "## Finding",
            "",
            "1. Cite BF1–BF5 live summaries "
            "(no vanity rewrite of BE/BD/BC/BB/BA/AZ locks).  ",
            f"2. Live ask battery under max safe CPU (threads={threads}, "
            f"workers={workers}, ~{wall_s:.1f}s · `cpus-6`) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; BF-FOREVER FP → ABSTAIN; "
            "over-refuse → LOOKUP; DECODE junk → ABSTAIN.  ",
            "3. Generative unlock **locked** because BF5 SKIP "
            "(no written M1|M2|M3 plan; SKIP stop rule; NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER · NANOGEN16 SKIP).  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "BA…BE PASS ≠ BF forever.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"utilization={PROTOCOL.get('utilization_scored')} · "
            f"span_fallback_neq_gen="
            f"{PROTOCOL.get('span_fallback_neq_gen')}.  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bf:real-eval",
            "npm run nano:nanogen16",
            "npm run nano:ctxbf",
            "npm run nano:fastbf",
            "npm run nano:shipuse2",
            "npm run nano:predint",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bf/bf_real_eval_summary.json`  ",
            "- Trials: `results/nano-lm/wave-bf/real_eval_trials/`  ",
            "- Contract: `nano_lm/tests/test_bf_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {claim} | Open chat / mini-AGI while BF5 SKIP |",
            "| Live battery PASS under anti-FP | Summary-only theater |",
            "| Gen claim only if BF5 PROMOTE | NANOGEN16 = NANOGEN15+rename |",
            "",
            f"SAFE note: {BF_REAL_EVAL_SAFE_NOTE}  ",
            f"Anti-FP: {BF_REAL_EVAL_ANTI_FP}",
            "",
            "Next: **BF7 BF-REPORT** (`npm run nano:bf:report`).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, battery: list[dict[str, Any]]) -> None:
    status = decision.split("(", 1)[0].strip()
    n_pass = sum(1 for t in battery if battery_row_ok(t))
    body = "\n".join(
        [
            f"# Wave BF session checklist (**OPEN** · BF6 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{BF_REAL_EVAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BF6 — BF-REAL-EVAL (DONE — {status})** · "
            "Next: **BF7 BF-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Battery | **{n_pass}/{len(battery)}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BF0 | SESSION | **DONE — PROMOTE** |",
            "| BF1 | H-PREDINT | **DONE — PROMOTE** |",
            "| BF2 | H-SHIPUSE2 | **DONE — PROMOTE** |",
            "| BF3 | H-FASTBF | **DONE — PROMOTE** |",
            "| BF4 | H-CTXBF | **DONE — PROMOTE** |",
            "| BF5 | H-NANOGEN16 / SKIP | **DONE — SKIP** |",
            f"| BF6 | BF-REAL-EVAL | **DONE — {status}** |",
            "| BF7 | BF-REPORT | **NEXT** |",
            "| BF8 | BF-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    if not decision.startswith("PROMOTE"):
        return
    status = decision.split("(", 1)[0].strip()
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"(\| BF6 \| \*\*BF-REAL-EVAL\*\* \|[^\n]+\| )\*\*NEXT\*\* \|",
        rf"\1**DONE — {status}** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BF7 \| \*\*BF-REPORT\*\* \|[^\n]+\| )(?:pending|\*\*TODO\*\*) \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        "7. **BF6 BF-REAL-EVAL** — **NEXT** — live battery; gen claim only "
        "if BF5 PROMOTE.  ",
        f"7. **BF6 BF-REAL-EVAL** — **DONE {status}** "
        "(`npm run nano:bf:real-eval`) — battery live; gen locked "
        "(BF5 SKIP).  ",
        1,
    )
    text = text.replace(
        "8. **BF7 BF-REPORT** — summary + paper-lab; arXiv path if measured lift.  ",
        "8. **BF7 BF-REPORT** — **NEXT** — summary + paper-lab; arXiv path "
        "if measured lift.  ",
        1,
    )
    text = text.replace(
        "npm run nano:nanogen16\n"
        "# next: nano:bf:real-eval\n"
        "# npm run nano:bf:real-eval\n",
        "npm run nano:nanogen16\n"
        "npm run nano:bf:real-eval\n"
        "# next: nano:bf:report\n",
        1,
    )
    text = text.replace(
        "(BF5 H-NANOGEN16 **DONE — SKIP**; next BF6 BF-REAL-EVAL)",
        f"(BF6 BF-REAL-EVAL **DONE — {status}**; next BF7 BF-REPORT)",
        1,
    )
    text = text.replace(
        "(BF5 H-NANOGEN16 **DONE — SKIP**; next BF6 BF-REAL-EVAL).",
        f"(BF6 BF-REAL-EVAL **DONE — {status}**; next BF7 BF-REPORT).",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    if _LOCAL_IMPL.is_file():
        _LOCAL_IMPL.write_text(
            f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BF0–BF4 PROMOTE · BF5 SKIP · BF6 DONE — {status}**. Next: **BF7 BF-REPORT**.

```bash
npm run nano:bf:real-eval
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BF ACTIVE** — BF6 **BF-REAL-EVAL {status}** (gen locked · BF5 SKIP).

Next: **BF7 BF-REPORT**.
""",
            encoding="utf-8",
        )


def _bf_active_line(status: str) -> str:
    return (
        "**Wave BF ACTIVE:** BF0 [SESSION PROMOTE](wave-bf-session.md) · "
        "BF1 [H-PREDINT PROMOTE](formal-hpredint-predint.md) · "
        "BF2 [H-SHIPUSE2 PROMOTE](formal-hshipuse2-shipuse2.md) · "
        "BF3 [H-FASTBF PROMOTE](formal-hfastbf-fastbf.md) · "
        "BF4 [H-CTXBF PROMOTE](formal-hctxbf-ctxbf.md) · "
        "BF5 [H-NANOGEN16 SKIP](formal-hnanogen16-nanogen16.md) · "
        f"BF6 [BF-REAL-EVAL {status}](wave-bf-real-eval.md) "
        f"(`npm run nano:bf:real-eval`) — live battery; gen locked; "
        "next BF7 BF-REPORT; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str, n_pass: int, n_bat: int) -> None:
    if not _RECIPES.is_file():
        return
    line = _bf_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BF ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BF6 BF-REAL-EVAL | [wave-bf-real-eval.md]"
        f"(wave-bf-real-eval.md) **{status}** (`npm run nano:bf:real-eval`) "
        f"— battery {n_pass}/{n_bat} · gen locked (BF5 SKIP) |"
    )
    if "Wave BF6 BF-REAL-EVAL" not in text2:
        marker = "| Wave BF5 H-NANOGEN16 |"
        if marker in text2:
            text2 = text2.replace(marker, insert + "\n" + marker, 1)
    if n or "Wave BF6 BF-REAL-EVAL" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(status: str) -> None:
    line = _bf_active_line(status)
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BF ACTIVE\*\* —[^\n]+",
            line.replace("**Wave BF ACTIVE:**", "**Wave BF ACTIVE** —"),
            text,
            count=1,
        )
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BF ACTIVE** — BF0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-bf-session.md) "
            "(`npm run nano:bf:session`) · BF1 [H-PREDINT PROMOTE]"
            "(docs/results/nano-lm/formal-hpredint-predint.md) "
            "(`npm run nano:predint`) · BF2 [H-SHIPUSE2 PROMOTE]"
            "(docs/results/nano-lm/formal-hshipuse2-shipuse2.md) "
            "(`npm run nano:shipuse2`) · BF3 [H-FASTBF PROMOTE]"
            "(docs/results/nano-lm/formal-hfastbf-fastbf.md) "
            "(`npm run nano:fastbf`) · BF4 [H-CTXBF PROMOTE]"
            "(docs/results/nano-lm/formal-hctxbf-ctxbf.md) "
            "(`npm run nano:ctxbf`) · BF5 [H-NANOGEN16 SKIP]"
            "(docs/results/nano-lm/formal-hnanogen16-nanogen16.md) "
            "(`npm run nano:nanogen16`) · BF6 "
            f"[BF-REAL-EVAL {status}]"
            "(docs/results/nano-lm/wave-bf-real-eval.md) "
            "(`npm run nano:bf:real-eval`); next BF7 BF-REPORT; ship remains "
            "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER · NANOGEN16 SKIP; ≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BF ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            f"| **BF** | **ACTIVE** | BF0–BF4 PROMOTE · BF5 SKIP · BF6 "
            f"BF-REAL-EVAL {status} (`npm run nano:bf:real-eval`); "
            "next BF7 BF-REPORT; ≤5M |"
        )
        text2, n = re.subn(
            r"\| \*\*BE\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "BF5 H-NANOGEN16 SKIP; next BF6 BF-REAL-EVAL",
        f"BF5 SKIP · BF6 BF-REAL-EVAL {status}; next BF7 BF-REPORT",
        1,
    )
    text = text.replace(
        "next BF6 BF-REAL-EVAL",
        f"BF6 BF-REAL-EVAL {status}; next BF7 BF-REPORT",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public(decision: str, battery: list[dict[str, Any]]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    status = decision.split("(", 1)[0].strip()
    n_pass = sum(1 for t in battery if battery_row_ok(t))
    _patch_recipes(status, n_pass, len(battery))
    _patch_card_agents_agenda(status)
    _patch_evogen(status)


def run_bf_real_eval(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN BF1–BF5 summaries + BF0 live battery
    WHEN scoring prod=eval ask path
    THEN PROMOTE iff pillars + battery + honest claim (gen iff BF5 PROMOTE).
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "predint": _load_decision(_PREDINT),
        "shipuse2": _load_decision(_SHIPUSE2),
        "fastbf": _load_decision(_FASTBF),
        "ctxbf": _load_decision(_CTXBF),
        "nanogen16": _load_decision(_NANOGEN16),
    }
    nano_board = _load_board(_NANOGEN16)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    bat_ok = battery_pass(battery)
    decision = decide_bf_real_eval(
        predint_decision=pillars["predint"],
        shipuse2_decision=pillars["shipuse2"],
        fastbf_decision=pillars["fastbf"],
        ctxbf_decision=pillars["ctxbf"],
        nanogen16_decision=pillars["nanogen16"],
        battery_ok=bat_ok,
        claim=BF_REAL_EVAL_CLAIM,
    )
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "BF-REAL-EVAL-BOARD.json",
        {
            "pillars": pillars,
            "battery": battery,
            "battery_ok": bat_ok,
            "decision": decision,
            "claim": BF_REAL_EVAL_CLAIM,
        },
    )
    _write_public(
        decision=decision,
        pillars=pillars,
        battery=battery,
        claim=BF_REAL_EVAL_CLAIM,
        nano_board=nano_board,
        wall_s=wall_s,
        threads=threads,
        workers=workers,
    )
    _write_session(decision, battery)
    _patch_pesquisa(decision)
    _patch_local_notes(decision)
    _patch_public(decision, battery)
    n_pass = sum(1 for t in battery if battery_row_ok(t))
    payload: dict[str, Any] = {
        "id": BF_REAL_EVAL_ID,
        "stage": "BF6",
        "thesis": BF_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_ok": bat_ok,
        "battery_pass_n": n_pass,
        "battery_n": len(battery),
        "nanogen16_board": nano_board,
        "claim": BF_REAL_EVAL_CLAIM,
        "protocol": dict(PROTOCOL),
        "wall_s": wall_s,
        "cpu_threads": threads,
        "workers": workers,
        "public_note": "docs/results/nano-lm/wave-bf-real-eval.md",
        "next": "BF7 BF-REPORT",
        "anti_fp": BF_REAL_EVAL_ANTI_FP,
        "finding": (
            f"{BF_REAL_EVAL_ID}: battery {n_pass}/{len(battery)} "
            f"nanogen16={pillars['nanogen16'][:40]} → {decision}"
        ),
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BF6 BF-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_bf_real_eval(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            workers=workers,
            threads=threads,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(payload.get("decision", ""))
    ok = decision.startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BF_REAL_EVAL_ID,
                "stage": "BF6",
                "decision": decision[:180],
                "cpu_threads": threads,
                "workers": workers,
                "battery_pass_n": payload.get("battery_pass_n"),
                "battery_n": payload.get("battery_n"),
                "nanogen16": (payload.get("pillars") or {}).get("nanogen16", "")[
                    :60
                ],
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
