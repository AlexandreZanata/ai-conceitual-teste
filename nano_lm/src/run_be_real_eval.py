"""Wave BE6 BE-REAL-EVAL runner — product+util+ctx+speed + live ask; gen if NANOGEN15 PROMOTE."""

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

from be_real_eval_ops import (
    ASK_BATTERY,
    BE_REAL_EVAL_ANTI_FP,
    BE_REAL_EVAL_CLAIM,
    BE_REAL_EVAL_ID,
    BE_REAL_EVAL_SAFE_NOTE,
    BE_REAL_EVAL_THESIS,
    LOOKUP_KINDS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_be_real_eval,
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

_SUMMARY = REPO / "results/nano-lm/wave-be/be_real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-be/real_eval_trials"
_COMPINT = REPO / "results/nano-lm/wave-be/compint_summary.json"
_SHIPUSE = REPO / "results/nano-lm/wave-be/shipuse_summary.json"
_FASTBE = REPO / "results/nano-lm/wave-be/fastbe_summary.json"
_CTXBE = REPO / "results/nano-lm/wave-be/ctxbe_summary.json"
_NANOGEN15 = REPO / "results/nano-lm/wave-be/nanogen15_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-be/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-be-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-be/SESSION.md"
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
            f"# BE-REAL-EVAL — product+util+ctx+speed + live battery "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §1 · §9 BE6 · Session: "
            "`.local/wave-be/SESSION.md`  ",
            "> Parents: [formal-hcompint-compint.md](formal-hcompint-compint.md) · "
            "[formal-hshipuse-shipuse.md](formal-hshipuse-shipuse.md) · "
            "[formal-hfastbe-fastbe.md](formal-hfastbe-fastbe.md) · "
            "[formal-hctxbe-ctxbe.md](formal-hctxbe-ctxbe.md) · "
            "[formal-hnanogen15-nanogen15.md](formal-hnanogen15-nanogen15.md)  ",
            "> Module: `nano_lm/src/be_real_eval_ops.py` · "
            "Runner: `npm run nano:be:real-eval`",
            "",
            "## Hypothesis",
            "",
            BE_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| BE1 H-COMPINT | **{pillars.get('compint')}** |",
            f"| BE2 H-SHIPUSE | **{pillars.get('shipuse')}** |",
            f"| BE3 H-FASTBE | **{pillars.get('fastbe')}** |",
            f"| BE4 H-CTXBE | **{pillars.get('ctxbe')}** |",
            f"| BE5 H-NANOGEN15 | **{pillars.get('nanogen15')}** "
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
            "1. Cite BE1–BE5 live summaries "
            "(no vanity rewrite of BD/BC/BB/BA/AZ locks).  ",
            f"2. Live ask battery under max safe CPU (threads={threads}, "
            f"workers={workers}, ~{wall_s:.1f}s · `cpus-6`) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; BE-FOREVER FP → ABSTAIN; "
            "over-refuse → LOOKUP; DECODE junk → ABSTAIN.  ",
            "3. Generative unlock **locked** because BE5 DEFER "
            "(no real M1|M2|M3; DEFER once; NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER stand).  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "BA…BD PASS ≠ BE forever.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"utilization={PROTOCOL.get('utilization_scored')} · "
            f"span_fallback_neq_gen="
            f"{PROTOCOL.get('span_fallback_neq_gen')}.  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:be:real-eval",
            "npm run nano:nanogen15",
            "npm run nano:ctxbe",
            "npm run nano:fastbe",
            "npm run nano:shipuse",
            "npm run nano:compint",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-be/be_real_eval_summary.json`  ",
            "- Trials: `results/nano-lm/wave-be/real_eval_trials/`  ",
            "- Contract: `nano_lm/tests/test_be_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {claim} | Open chat / mini-AGI while BE5 DEFER |",
            "| Live battery PASS under anti-FP | Summary-only theater |",
            "| Gen claim only if BE5 PROMOTE | NANOGEN15 = NANOGEN14+rename |",
            "",
            f"SAFE note: {BE_REAL_EVAL_SAFE_NOTE}  ",
            f"Anti-FP: {BE_REAL_EVAL_ANTI_FP}",
            "",
            "Next: **BE7 BE-REPORT** (`npm run nano:be:report`).",
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
            f"# Wave BE session checklist (**OPEN** · BE6 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{BE_REAL_EVAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BE6 — BE-REAL-EVAL (DONE — {status})** · "
            "Next: **BE7 BE-REPORT**",
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
            "| BE0 | SESSION | **DONE — PROMOTE** |",
            "| BE1 | H-COMPINT | **DONE — PROMOTE** |",
            "| BE2 | H-SHIPUSE | **DONE — PROMOTE** |",
            "| BE3 | H-FASTBE | **DONE — PROMOTE** |",
            "| BE4 | H-CTXBE | **DONE — PROMOTE** |",
            "| BE5 | H-NANOGEN15 | **DONE — DEFER** |",
            f"| BE6 | BE-REAL-EVAL | **DONE — {status}** |",
            "| BE7 | BE-REPORT | **NEXT** |",
            "| BE8 | BE-FREEZE | pending |",
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
        r"(\| BE6 \| \*\*BE-REAL-EVAL\*\* \|[^\n]+\| )\*\*NEXT\*\* \|",
        rf"\1**DONE — {status}** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BE7 \| \*\*BE-REPORT\*\* \|[^\n]+\| )(?:pending|\*\*TODO\*\*) \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        "7. **BE6 BE-REAL-EVAL** — **NEXT** — live battery; gen claim only "
        "if BE5 PROMOTE.  ",
        f"7. **BE6 BE-REAL-EVAL** — **DONE {status}** "
        "(`npm run nano:be:real-eval`) — battery live; gen locked "
        "(BE5 DEFER).  ",
        1,
    )
    text = text.replace(
        "8. **BE7 BE-REPORT** — summary + paper-lab; arXiv path if measured lift.  ",
        "8. **BE7 BE-REPORT** — **NEXT** — summary + paper-lab; arXiv path "
        "if measured lift.  ",
        1,
    )
    text = text.replace(
        "npm run nano:nanogen15\n"
        "# next: nano:be:real-eval\n"
        "# npm run nano:be:real-eval\n",
        "npm run nano:nanogen15\n"
        "npm run nano:be:real-eval\n"
        "# next: nano:be:report\n",
        1,
    )
    text = text.replace(
        "(BE5 H-NANOGEN15 **DONE — DEFER**; next BE6 BE-REAL-EVAL)",
        f"(BE6 BE-REAL-EVAL **DONE — {status}**; next BE7 BE-REPORT)",
        1,
    )
    text = text.replace(
        "(BE5 H-NANOGEN15 **DONE — DEFER**; next BE6 BE-REAL-EVAL).",
        f"(BE6 BE-REAL-EVAL **DONE — {status}**; next BE7 BE-REPORT).",
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

**BE0–BE4 PROMOTE · BE5 DEFER · BE6 DONE — {status}**. Next: **BE7 BE-REPORT**.

```bash
npm run nano:be:real-eval
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BE ACTIVE** — BE6 **BE-REAL-EVAL {status}** (gen locked · BE5 DEFER).

Next: **BE7 BE-REPORT**.
""",
            encoding="utf-8",
        )


def _be_active_line(status: str) -> str:
    return (
        "**Wave BE ACTIVE:** BE0 [SESSION PROMOTE](wave-be-session.md) · "
        "BE1 [H-COMPINT PROMOTE](formal-hcompint-compint.md) · "
        "BE2 [H-SHIPUSE PROMOTE](formal-hshipuse-shipuse.md) · "
        "BE3 [H-FASTBE PROMOTE](formal-hfastbe-fastbe.md) · "
        "BE4 [H-CTXBE PROMOTE](formal-hctxbe-ctxbe.md) · "
        "BE5 [H-NANOGEN15 DEFER](formal-hnanogen15-nanogen15.md) · "
        f"BE6 [BE-REAL-EVAL {status}](wave-be-real-eval.md) "
        f"(`npm run nano:be:real-eval`) — live battery; gen locked; "
        "next BE7 BE-REPORT; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str, n_pass: int, n_bat: int) -> None:
    if not _RECIPES.is_file():
        return
    line = _be_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BE ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BE6 BE-REAL-EVAL | [wave-be-real-eval.md]"
        f"(wave-be-real-eval.md) **{status}** (`npm run nano:be:real-eval`) "
        f"— battery {n_pass}/{n_bat} · gen locked (BE5 DEFER) |"
    )
    if "Wave BE6 BE-REAL-EVAL" not in text2:
        marker = "| Wave BE5 H-NANOGEN15 |"
        if marker in text2:
            text2 = text2.replace(marker, insert + "\n" + marker, 1)
    if n or "Wave BE6 BE-REAL-EVAL" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(status: str) -> None:
    line = _be_active_line(status)
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BE ACTIVE\*\* —[^\n]+",
            line.replace("**Wave BE ACTIVE:**", "**Wave BE ACTIVE** —"),
            text,
            count=1,
        )
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BE ACTIVE** — BE0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-be-session.md) "
            "(`npm run nano:be:session`) · BE1 [H-COMPINT PROMOTE]"
            "(docs/results/nano-lm/formal-hcompint-compint.md) "
            "(`npm run nano:compint`) · BE2 [H-SHIPUSE PROMOTE]"
            "(docs/results/nano-lm/formal-hshipuse-shipuse.md) "
            "(`npm run nano:shipuse`) · BE3 [H-FASTBE PROMOTE]"
            "(docs/results/nano-lm/formal-hfastbe-fastbe.md) "
            "(`npm run nano:fastbe`) · BE4 [H-CTXBE PROMOTE]"
            "(docs/results/nano-lm/formal-hctxbe-ctxbe.md) "
            "(`npm run nano:ctxbe`) · BE5 [H-NANOGEN15 DEFER]"
            "(docs/results/nano-lm/formal-hnanogen15-nanogen15.md) "
            "(`npm run nano:nanogen15`) · BE6 "
            f"[BE-REAL-EVAL {status}]"
            "(docs/results/nano-lm/wave-be-real-eval.md) "
            "(`npm run nano:be:real-eval`); next BE7 BE-REPORT; ship remains "
            "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER; ≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BE ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            f"| **BE** | **ACTIVE** | BE0–BE4 PROMOTE · BE5 DEFER · BE6 "
            f"BE-REAL-EVAL {status} (`npm run nano:be:real-eval`); "
            "next BE7 BE-REPORT; ≤5M |"
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
        "Wave BE ACTIVE (BE0–BE4 PROMOTE · BE5 H-NANOGEN15 DEFER; "
        "next BE6 BE-REAL-EVAL)",
        f"Wave BE ACTIVE (BE0–BE4 PROMOTE · BE5 DEFER · BE6 BE-REAL-EVAL "
        f"{status}; next BE7 BE-REPORT)",
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


def run_be_real_eval(
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
    GIVEN BE1–BE5 summaries + BE0 live battery
    WHEN scoring prod=eval ask path
    THEN PROMOTE iff pillars + battery + honest claim (gen iff BE5 PROMOTE).
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "compint": _load_decision(_COMPINT),
        "shipuse": _load_decision(_SHIPUSE),
        "fastbe": _load_decision(_FASTBE),
        "ctxbe": _load_decision(_CTXBE),
        "nanogen15": _load_decision(_NANOGEN15),
    }
    nano_board = _load_board(_NANOGEN15)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    bat_ok = battery_pass(battery)
    decision = decide_be_real_eval(
        compint_decision=pillars["compint"],
        shipuse_decision=pillars["shipuse"],
        fastbe_decision=pillars["fastbe"],
        ctxbe_decision=pillars["ctxbe"],
        nanogen15_decision=pillars["nanogen15"],
        battery_ok=bat_ok,
        claim=BE_REAL_EVAL_CLAIM,
    )
    wall_s = time.perf_counter() - t0
    write_json(
        trials_dir / "BE-REAL-EVAL-BOARD.json",
        {
            "pillars": pillars,
            "battery": battery,
            "battery_ok": bat_ok,
            "decision": decision,
            "claim": BE_REAL_EVAL_CLAIM,
        },
    )
    _write_public(
        decision=decision,
        pillars=pillars,
        battery=battery,
        claim=BE_REAL_EVAL_CLAIM,
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
        "id": BE_REAL_EVAL_ID,
        "stage": "BE6",
        "thesis": BE_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_ok": bat_ok,
        "battery_pass_n": n_pass,
        "battery_n": len(battery),
        "nanogen15_board": nano_board,
        "claim": BE_REAL_EVAL_CLAIM,
        "protocol": dict(PROTOCOL),
        "wall_s": wall_s,
        "cpu_threads": threads,
        "workers": workers,
        "public_note": "docs/results/nano-lm/wave-be-real-eval.md",
        "next": "BE7 BE-REPORT",
        "anti_fp": BE_REAL_EVAL_ANTI_FP,
        "finding": (
            f"{BE_REAL_EVAL_ID}: battery {n_pass}/{len(battery)} "
            f"nanogen15={pillars['nanogen15'][:40]} → {decision}"
        ),
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BE6 BE-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_be_real_eval(
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
                "hyp_id": BE_REAL_EVAL_ID,
                "stage": "BE6",
                "decision": decision[:180],
                "cpu_threads": threads,
                "workers": workers,
                "battery_pass_n": payload.get("battery_pass_n"),
                "battery_n": payload.get("battery_n"),
                "nanogen15": (payload.get("pillars") or {}).get("nanogen15", "")[
                    :60
                ],
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
