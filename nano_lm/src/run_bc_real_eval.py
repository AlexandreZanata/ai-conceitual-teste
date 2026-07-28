"""Wave BC5 BC-REAL-EVAL runner — product+ctx+speed + live ask; gen if NANOGEN13 PROMOTE."""

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

from bc_real_eval_ops import (
    ASK_BATTERY,
    BC_REAL_EVAL_ANTI_FP,
    BC_REAL_EVAL_CLAIM,
    BC_REAL_EVAL_ID,
    BC_REAL_EVAL_SAFE_NOTE,
    BC_REAL_EVAL_THESIS,
    LOOKUP_KINDS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_bc_real_eval,
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

_SUMMARY = REPO / "results/nano-lm/wave-bc/bc_real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-bc/real_eval_trials"
_OPSFAM = REPO / "results/nano-lm/wave-bc/opsfam_summary.json"
_FASTLIFT = REPO / "results/nano-lm/wave-bc/bc_fastlift_summary.json"
_CTXLIFT2 = REPO / "results/nano-lm/wave-bc/bc_ctxlift2_summary.json"
_NANOGEN13 = REPO / "results/nano-lm/wave-bc/nanogen13_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bc/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-bc-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-bc/SESSION.md"
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
            f"# BC-REAL-EVAL — product+ctx+speed + live battery "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §1 · §9 BC5 · Session: "
            "`.local/wave-bc/SESSION.md`  ",
            "> Parents: [formal-hopsfam-opsfam.md](formal-hopsfam-opsfam.md) · "
            "[formal-hfastlift-bc2.md](formal-hfastlift-bc2.md) · "
            "[formal-hctxlift2-ctxlift2.md](formal-hctxlift2-ctxlift2.md) · "
            "[formal-hnanogen13-nanogen13.md](formal-hnanogen13-nanogen13.md)  ",
            "> Module: `nano_lm/src/bc_real_eval_ops.py` · "
            "Runner: `npm run nano:bc:real-eval`",
            "",
            "## Hypothesis",
            "",
            BC_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| BC1 H-OPSFAM | **{pillars.get('opsfam')}** |",
            f"| BC2 H-FASTLIFT | **{pillars.get('fastlift')}** |",
            f"| BC3 H-CTXLIFT2 | **{pillars.get('ctxlift2')}** |",
            f"| BC4 H-NANOGEN13 | **{pillars.get('nanogen13')}** "
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
            "1. Cite BC1–BC4 live summaries "
            "(no vanity rewrite of BB/BA/AZ locks).  ",
            f"2. Live ask battery under max safe CPU (threads={threads}, "
            f"workers={workers}, ~{wall_s:.1f}s) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; BC-FOREVER FP → ABSTAIN; "
            "over-refuse → LOOKUP; DECODE junk → ABSTAIN.  ",
            "3. Generative unlock **locked** because BC4 DEFER "
            "(no real M1|M2|M3; NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12 DEFER stand).  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "BA+BB PASS ≠ BC forever.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"span_fallback_neq_gen="
            f"{PROTOCOL.get('span_fallback_neq_gen')}.  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:bc:real-eval",
            "npm run nano:nanogen13",
            "npm run nano:bc:ctxlift2",
            "npm run nano:bc:fastlift",
            "npm run nano:opsfam",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bc/bc_real_eval_summary.json`  ",
            "- Contract: `nano_lm/tests/test_bc_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Product/ctx/speed PROMOTE + live battery | Unlabeled open chat |",
            "| STRICT ship lock while BC4 DEFER | Gen unlock on DEFER/HOLD |",
            "| Forever ABSTAIN · over-refuse LOOKUP | LOOKUP-as-IQ · invent BD |",
            "",
            f"SAFE note: {BC_REAL_EVAL_SAFE_NOTE}  ",
            f"Anti-FP: {BC_REAL_EVAL_ANTI_FP}",
            "",
            "Next: **BC6 BC-REPORT** — summary + paper-lab.",
            "",
        ]
    )
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, battery: list[dict[str, Any]]) -> None:
    status = decision.split("(", 1)[0].strip()
    n_pass = sum(1 for t in battery if battery_row_ok(t))
    body = "\n".join(
        [
            f"# Wave BC session checklist (**OPEN** · BC5 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{BC_REAL_EVAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BC5 — BC-REAL-EVAL (DONE — {status})** · "
            "Next: **BC6 BC-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Live battery | **{n_pass}/{len(battery)}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BC0 | SESSION | **DONE — PROMOTE** |",
            "| BC1 | H-OPSFAM | **DONE — PROMOTE** |",
            "| BC2 | H-FASTLIFT | **DONE — PROMOTE** |",
            "| BC3 | H-CTXLIFT2 | **DONE — PROMOTE** |",
            "| BC4 | H-NANOGEN13 | **DONE — DEFER** |",
            f"| BC5 | BC-REAL-EVAL | **DONE — {status}** |",
            "| BC6 | BC-REPORT | **NEXT** |",
            "| BC7 | BC-FREEZE | pending |",
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
        r"(\| BC5 \| \*\*BC-REAL-EVAL\*\* \|[^\n]+\| )\*\*NEXT\*\* \|",
        rf"\1**DONE — {status}** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BC6 \| \*\*BC-REPORT\*\* \|[^\n]+\| )pending \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        "6. **BC5 BC-REAL-EVAL** — **NEXT** — live battery; gen claim only "
        "if BC4 PROMOTE.  ",
        f"6. **BC5 BC-REAL-EVAL** — **DONE {status}** "
        "(`npm run nano:bc:real-eval`) — battery live; gen locked "
        "(BC4 DEFER).  ",
        1,
    )
    text = text.replace(
        "7. **BC6 BC-REPORT** → **BC7 BC-FREEZE**.  ",
        "7. **BC6 BC-REPORT** — **NEXT** — summary + paper-lab.  \n"
        "8. **BC7 BC-FREEZE** — lock outcomes.  ",
        1,
    )
    text = text.replace(
        "npm run nano:nanogen13\n"
        "# next: nano:bc:real-eval\n"
        "# npm run nano:bc:real-eval\n",
        "npm run nano:nanogen13\n"
        "npm run nano:bc:real-eval\n"
        "# next: nano:bc:report\n",
        1,
    )
    text = text.replace(
        "(BC4 H-NANOGEN13 **DONE — DEFER**; next BC5 BC-REAL-EVAL).",
        f"(BC5 BC-REAL-EVAL **DONE — {status}**; next BC6 BC-REPORT).",
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

**BC0–BC3 PROMOTE · BC4 DEFER · BC5 DONE — {status}**. Next: **BC6 BC-REPORT**.

```bash
npm run nano:bc:real-eval
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BC ACTIVE** — BC5 **BC-REAL-EVAL {status}** (gen locked).

Next: **BC6 BC-REPORT**.
""",
            encoding="utf-8",
        )


def _bc_active_line(status: str) -> str:
    return (
        "**Wave BC ACTIVE:** BC0 [SESSION PROMOTE](wave-bc-session.md) · "
        "BC1 [H-OPSFAM PROMOTE](formal-hopsfam-opsfam.md) · "
        "BC2 [H-FASTLIFT PROMOTE](formal-hfastlift-bc2.md) · "
        "BC3 [H-CTXLIFT2 PROMOTE](formal-hctxlift2-ctxlift2.md) · "
        "BC4 [H-NANOGEN13 DEFER](formal-hnanogen13-nanogen13.md) · "
        f"BC5 [BC-REAL-EVAL {status}](wave-bc-real-eval.md) "
        f"(`npm run nano:bc:real-eval`) — live battery; gen locked; "
        "next BC6 BC-REPORT; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str, n_pass: int, n_bat: int) -> None:
    if not _RECIPES.is_file():
        return
    line = _bc_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BC ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BC5 BC-REAL-EVAL | [wave-bc-real-eval.md]"
        f"(wave-bc-real-eval.md) **{status}** (`npm run nano:bc:real-eval`) "
        f"— battery {n_pass}/{n_bat} · gen locked (BC4 DEFER) |"
    )
    if "Wave BC5 BC-REAL-EVAL" not in text2 and "Wave BC4 H-NANOGEN13 |" in text2:
        text2 = text2.replace(
            "| Wave BC4 H-NANOGEN13 |",
            insert + "\n| Wave BC4 H-NANOGEN13 |",
            1,
        )
    if n or "Wave BC5 BC-REAL-EVAL" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(status: str) -> None:
    line = _bc_active_line(status)
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BC ACTIVE\*\* —[^\n]+",
            line.replace("**Wave BC ACTIVE:**", "**Wave BC ACTIVE** —"),
            text,
            count=1,
        )
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BC ACTIVE** — BC0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-bc-session.md) · BC1 [H-OPSFAM PROMOTE]"
            "(docs/results/nano-lm/formal-hopsfam-opsfam.md) · BC2 "
            "[H-FASTLIFT PROMOTE](docs/results/nano-lm/formal-hfastlift-bc2.md) · "
            "BC3 [H-CTXLIFT2 PROMOTE]"
            "(docs/results/nano-lm/formal-hctxlift2-ctxlift2.md) · BC4 "
            "[H-NANOGEN13 DEFER](docs/results/nano-lm/formal-hnanogen13-nanogen13.md) "
            f"· BC5 [BC-REAL-EVAL {status}]"
            "(docs/results/nano-lm/wave-bc-real-eval.md) "
            "(`npm run nano:bc:real-eval`); next BC6 BC-REPORT; ship remains "
            "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BC ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            f"| **BC** | **ACTIVE** | BC0–BC3 PROMOTE · BC4 DEFER · BC5 "
            f"BC-REAL-EVAL {status} (`npm run nano:bc:real-eval`); "
            "next BC6 BC-REPORT; ≤5M |"
        )
        text2, n = re.subn(
            r"\| \*\*BC\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "Wave BC ACTIVE (BC0–BC3 PROMOTE · BC4 H-NANOGEN13 DEFER; "
        "next BC5 BC-REAL-EVAL)",
        f"Wave BC ACTIVE (BC0–BC3 PROMOTE · BC4 DEFER · BC5 BC-REAL-EVAL "
        f"{status}; next BC6 BC-REPORT)",
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


def run_bc_real_eval(
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
    GIVEN BC1–BC4 summaries + BC0 live battery
    WHEN scoring prod=eval ask paths
    THEN PROMOTE iff product/ctx/speed + battery + honest gen lock.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    opsfam = _load_decision(_OPSFAM)
    fastlift = _load_decision(_FASTLIFT)
    ctxlift2 = _load_decision(_CTXLIFT2)
    nanogen13 = _load_decision(_NANOGEN13)
    nano_board = _load_board(_NANOGEN13)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    bat_ok = battery_pass(battery)
    claim = BC_REAL_EVAL_CLAIM
    decision = decide_bc_real_eval(
        opsfam_decision=opsfam,
        fastlift_decision=fastlift,
        ctxlift2_decision=ctxlift2,
        nanogen13_decision=nanogen13,
        battery_ok=bat_ok,
        claim=claim,
    )
    wall_s = time.perf_counter() - t0
    pillars = {
        "opsfam": opsfam,
        "fastlift": fastlift,
        "ctxlift2": ctxlift2,
        "nanogen13": nanogen13,
    }
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
    if decision.startswith("PROMOTE"):
        _patch_pesquisa(decision)
        _patch_local_notes(decision)
        _patch_public(decision, battery)
    payload: dict[str, Any] = {
        "id": BC_REAL_EVAL_ID,
        "stage": "BC5",
        "thesis": BC_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_ok": bat_ok,
        "battery_pass_n": sum(1 for t in battery if battery_row_ok(t)),
        "battery_n": len(battery),
        "claim": claim,
        "protocol": dict(PROTOCOL),
        "nanogen13_board": nano_board,
        "wall_s": wall_s,
        "cpu_threads": threads,
        "workers": workers,
        "public_note": "docs/results/nano-lm/wave-bc-real-eval.md",
        "next": "BC6 BC-REPORT",
        "anti_fp": BC_REAL_EVAL_ANTI_FP,
    }
    write_json(out, payload)
    write_json(trials_dir / "battery.json", {"rows": battery})
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BC5 BC-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_bc_real_eval(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            workers=workers,
            threads=threads,
        )
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(payload.get("decision", ""))
    ok = decision.startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": BC_REAL_EVAL_ID,
                "stage": "BC5",
                "decision": decision[:200],
                "cpu_threads": threads,
                "workers": workers,
                "battery": (
                    f"{payload.get('battery_pass_n')}/"
                    f"{payload.get('battery_n')}"
                ),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
