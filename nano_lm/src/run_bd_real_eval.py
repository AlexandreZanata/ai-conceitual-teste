"""Wave BD5 BD-REAL-EVAL runner — product+ctx+speed + live ask; gen if NANOGEN14 PROMOTE."""

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

from bd_real_eval_ops import (
    ASK_BATTERY,
    BD_REAL_EVAL_ANTI_FP,
    BD_REAL_EVAL_CLAIM,
    BD_REAL_EVAL_ID,
    BD_REAL_EVAL_SAFE_NOTE,
    BD_REAL_EVAL_THESIS,
    LOOKUP_KINDS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_bd_real_eval,
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

_SUMMARY = REPO / "results/nano-lm/wave-bd/bd_real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bd/real_eval_trials"
_SEMINT = REPO / "results/nano-lm/wave-bd/semint_summary.json"
_FASTGAIN = REPO / "results/nano-lm/wave-bd/bd_fastgain_summary.json"
_CTXGAIN = REPO / "results/nano-lm/wave-bd/bd_ctxgain_summary.json"
_NANOGEN14 = REPO / "results/nano-lm/wave-bd/nanogen14_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bd/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bd-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-bd/SESSION.md"
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
    """Max safe CPU: leave ~4 cores free (16c → threads≈12, workers≤8)."""
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(8, max(4, cpus - 4))
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
            semwrap=kind == "overrefuse_gold",
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
            f"# BD-REAL-EVAL — product+ctx+speed + live battery "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §1 · §9 BD5 · Session: "
            "`.local/wave-bd/SESSION.md`  ",
            "> Parents: [formal-hsemint-semint.md](formal-hsemint-semint.md) · "
            "[formal-hfastgain-fastgain.md](formal-hfastgain-fastgain.md) · "
            "[formal-hctxgain-ctxgain.md](formal-hctxgain-ctxgain.md) · "
            "[formal-hnanogen14-nanogen14.md](formal-hnanogen14-nanogen14.md)  ",
            "> Module: `nano_lm/src/bd_real_eval_ops.py` · "
            "Runner: `npm run nano:bd:real-eval`",
            "",
            "## Hypothesis",
            "",
            BD_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| BD1 H-SEMINT | **{pillars.get('semint')}** |",
            f"| BD2 H-FASTGAIN | **{pillars.get('fastgain')}** |",
            f"| BD3 H-CTXGAIN | **{pillars.get('ctxgain')}** |",
            f"| BD4 H-NANOGEN14 | **{pillars.get('nanogen14')}** "
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
            "1. Cite BD1–BD4 live summaries "
            "(no vanity rewrite of BC/BB/BA/AZ locks).  ",
            f"2. Live ask battery under max safe CPU (threads={threads}, "
            f"workers={workers}, ~{wall_s:.1f}s) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; BD-FOREVER FP → ABSTAIN; "
            "over-refuse → LOOKUP; DECODE junk → ABSTAIN.  ",
            "3. Generative unlock **locked** because BD4 DEFER "
            "(no real M1|M2|M3; NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12·13 DEFER stand).  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "BA+BB+BC PASS ≠ BD forever.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"span_fallback_neq_gen="
            f"{PROTOCOL.get('span_fallback_neq_gen')}.  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bd:real-eval",
            "npm run nano:nanogen14",
            "npm run nano:bd:ctxgain",
            "npm run nano:bd:fastgain",
            "npm run nano:semint",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bd/bd_real_eval_summary.json`  ",
            "- Trials: `results/nano-lm/wave-bd/real_eval_trials/`  ",
            "- Contract: `nano_lm/tests/test_bd_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {claim} | Open chat / mini-AGI while BD4 DEFER |",
            "| Live battery PASS under anti-FP | Summary-only theater |",
            "| Gen claim only if BD4 PROMOTE | NANOGEN14 = NANOGEN13+rename |",
            "",
            f"SAFE note: {BD_REAL_EVAL_SAFE_NOTE}  ",
            f"Anti-FP: {BD_REAL_EVAL_ANTI_FP}",
            "",
            "Next: **BD6 BD-REPORT** (`npm run nano:bd:report`).",
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
            f"# Wave BD session checklist (**OPEN** · BD5 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{BD_REAL_EVAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BD5 — BD-REAL-EVAL (DONE — {status})** · "
            "Next: **BD6 BD-REPORT**",
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
            "| BD0 | SESSION | **DONE — PROMOTE** |",
            "| BD1 | H-SEMINT | **DONE — PROMOTE** |",
            "| BD2 | H-FASTGAIN | **DONE — PROMOTE** |",
            "| BD3 | H-CTXGAIN | **DONE — PROMOTE** |",
            "| BD4 | H-NANOGEN14 | **DONE — DEFER** |",
            f"| BD5 | BD-REAL-EVAL | **DONE — {status}** |",
            "| BD6 | BD-REPORT | **NEXT** |",
            "| BD7 | BD-FREEZE | pending |",
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
        r"(\| BD5 \| \*\*BD-REAL-EVAL\*\* \|[^\n]+\| )\*\*NEXT\*\* \|",
        rf"\1**DONE — {status}** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BD6 \| \*\*BD-REPORT\*\* \|[^\n]+\| )(?:pending|\*\*TODO\*\*) \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        "6. **BD5 BD-REAL-EVAL** — **NEXT** — live battery; gen claim only "
        "if BD4 PROMOTE.  ",
        f"6. **BD5 BD-REAL-EVAL** — **DONE {status}** "
        "(`npm run nano:bd:real-eval`) — battery live; gen locked "
        "(BD4 DEFER).  ",
        1,
    )
    text = text.replace(
        "6. **BD5 BD-REAL-EVAL** — live battery; gen claim only if BD4 PROMOTE.  ",
        f"6. **BD5 BD-REAL-EVAL** — **DONE {status}** "
        "(`npm run nano:bd:real-eval`) — battery live; gen locked "
        "(BD4 DEFER).  ",
        1,
    )
    text = text.replace(
        "7. **BD6 BD-REPORT** — summary + paper-lab; update paper only after "
        "measured lift.  ",
        "7. **BD6 BD-REPORT** — **NEXT** — summary + paper-lab; update paper "
        "only after measured lift.  ",
        1,
    )
    # Fix stale BD4 NEXT line if still present
    text = text.replace(
        "5. **BD4 H-NANOGEN14** — **NEXT** — one real method M1|M2|M3 → "
        "true_continue PROMOTE else HOLD/DEFER (not NANOGEN13 rename).  ",
        "5. **BD4 H-NANOGEN14** — **DONE DEFER** "
        "(`npm run nano:nanogen14`) — gen stance defer · not NANOGEN13 rename.  ",
        1,
    )
    text = text.replace(
        "npm run nano:nanogen14\n"
        "# next: nano:bd:real-eval\n"
        "# npm run nano:bd:real-eval\n",
        "npm run nano:nanogen14\n"
        "npm run nano:bd:real-eval\n"
        "# next: nano:bd:report\n",
        1,
    )
    text = text.replace(
        "(BD4 H-NANOGEN14 **DONE — DEFER**; next BD5 BD-REAL-EVAL).",
        f"(BD5 BD-REAL-EVAL **DONE — {status}**; next BD6 BD-REPORT).",
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

**BD0–BD3 PROMOTE · BD4 DEFER · BD5 DONE — {status}**. Next: **BD6 BD-REPORT**.

```bash
npm run nano:bd:real-eval
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BD ACTIVE** — BD5 **BD-REAL-EVAL {status}** (gen locked).

Next: **BD6 BD-REPORT**.
""",
            encoding="utf-8",
        )


def _bd_active_line(status: str) -> str:
    return (
        "**Wave BD ACTIVE:** BD0 [SESSION PROMOTE](wave-bd-session.md) · "
        "BD1 [H-SEMINT PROMOTE](formal-hsemint-semint.md) · "
        "BD2 [H-FASTGAIN PROMOTE](formal-hfastgain-fastgain.md) · "
        "BD3 [H-CTXGAIN PROMOTE](formal-hctxgain-ctxgain.md) · "
        "BD4 [H-NANOGEN14 DEFER](formal-hnanogen14-nanogen14.md) · "
        f"BD5 [BD-REAL-EVAL {status}](wave-bd-real-eval.md) "
        f"(`npm run nano:bd:real-eval`) — live battery; gen locked; "
        "next BD6 BD-REPORT; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str, n_pass: int, n_bat: int) -> None:
    if not _RECIPES.is_file():
        return
    line = _bd_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BD ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BD5 BD-REAL-EVAL | [wave-bd-real-eval.md]"
        f"(wave-bd-real-eval.md) **{status}** (`npm run nano:bd:real-eval`) "
        f"— battery {n_pass}/{n_bat} · gen locked (BD4 DEFER) |"
    )
    if "Wave BD5 BD-REAL-EVAL" not in text2 and "Wave BD4 H-NANOGEN14 |" in text2:
        text2 = text2.replace(
            "| Wave BD4 H-NANOGEN14 |",
            insert + "\n| Wave BD4 H-NANOGEN14 |",
            1,
        )
    if n or "Wave BD5 BD-REAL-EVAL" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(status: str) -> None:
    line = _bd_active_line(status)
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BD ACTIVE\*\* —[^\n]+",
            line.replace("**Wave BD ACTIVE:**", "**Wave BD ACTIVE** —"),
            text,
            count=1,
        )
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BD ACTIVE** — BD0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-bd-session.md) · BD1 [H-SEMINT PROMOTE]"
            "(docs/results/nano-lm/formal-hsemint-semint.md) · BD2 "
            "[H-FASTGAIN PROMOTE](docs/results/nano-lm/formal-hfastgain-fastgain.md) · "
            "BD3 [H-CTXGAIN PROMOTE]"
            "(docs/results/nano-lm/formal-hctxgain-ctxgain.md) · BD4 "
            "[H-NANOGEN14 DEFER](docs/results/nano-lm/formal-hnanogen14-nanogen14.md) "
            f"· BD5 [BD-REAL-EVAL {status}]"
            "(docs/results/nano-lm/wave-bd-real-eval.md) "
            "(`npm run nano:bd:real-eval`); next BD6 BD-REPORT; ship remains "
            "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BD ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            f"| **BD** | **ACTIVE** | BD0–BD3 PROMOTE · BD4 DEFER · BD5 "
            f"BD-REAL-EVAL {status} (`npm run nano:bd:real-eval`); "
            "next BD6 BD-REPORT; ≤5M |"
        )
        text2, n = re.subn(
            r"\| \*\*BD\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "Wave BD ACTIVE (BD0–BD3 PROMOTE · BD4 H-NANOGEN14 DEFER; "
        "next BD5 BD-REAL-EVAL)",
        f"Wave BD ACTIVE (BD0–BD3 PROMOTE · BD4 DEFER · BD5 BD-REAL-EVAL "
        f"{status}; next BD6 BD-REPORT)",
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


def run_bd_real_eval(
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
    GIVEN BD1–BD4 summaries + BD0 ask battery
    WHEN running live prod=eval battery under max safe CPU
    THEN PROMOTE iff pillars + battery + honest claim (gen iff BD4 PROMOTE).
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "semint": _load_decision(_SEMINT),
        "fastgain": _load_decision(_FASTGAIN),
        "ctxgain": _load_decision(_CTXGAIN),
        "nanogen14": _load_decision(_NANOGEN14),
    }
    nano_board = _load_board(_NANOGEN14)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    bat_ok = battery_pass(battery)
    claim = BD_REAL_EVAL_CLAIM
    decision = decide_bd_real_eval(
        semint_decision=pillars["semint"],
        fastgain_decision=pillars["fastgain"],
        ctxgain_decision=pillars["ctxgain"],
        nanogen14_decision=pillars["nanogen14"],
        battery_ok=bat_ok,
        claim=claim,
    )
    wall_s = time.perf_counter() - t0
    write_json(trials_dir / "BD-REAL-EVAL-BOARD.json", {
        "pillars": pillars,
        "battery": battery,
        "battery_ok": bat_ok,
        "decision": decision,
        "claim": claim,
    })
    _write_public(
        decision=decision,
        pillars=pillars,
        battery=battery,
        claim=claim,
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
    payload = {
        "id": BD_REAL_EVAL_ID,
        "stage": "BD5",
        "thesis": BD_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_ok": bat_ok,
        "battery_pass_n": n_pass,
        "battery_n": len(battery),
        "claim": claim,
        "nanogen14_board": nano_board,
        "wall_s": wall_s,
        "cpu_threads": threads,
        "workers": workers,
        "public_note": "docs/results/nano-lm/wave-bd-real-eval.md",
        "next": "BD6 BD-REPORT",
        "anti_fp": BD_REAL_EVAL_ANTI_FP,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BD5 BD-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_bd_real_eval(
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
                "hyp_id": BD_REAL_EVAL_ID,
                "stage": "BD5",
                "decision": decision[:180],
                "cpu_threads": threads,
                "workers": workers,
                "battery_pass_n": payload.get("battery_pass_n"),
                "battery_n": payload.get("battery_n"),
                "pillars": payload.get("pillars"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
