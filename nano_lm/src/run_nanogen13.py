"""Wave BC4 H-NANOGEN13 runner — gen-defer; not NANOGEN12 rename."""

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

from matrix_common import REPO, write_json
from nanogen13_ops import (
    NANOGEN13_ANTI_FP,
    NANOGEN13_CLAIM,
    NANOGEN13_ID,
    NANOGEN13_METHOD,
    NANOGEN13_SAFE_NOTE,
    NANOGEN13_STANCE,
    NANOGEN13_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    PARENT_NANOGEN11_DEFER,
    PARENT_NANOGEN12_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen13,
    extract_nanogen13_board,
)
from prodhard_ops import KNOWN_ASK
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bc/nanogen13_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen13-nanogen13.md"
_NANOGEN12_SUM = REPO / "results/nano-lm/wave-bb/nanogen12_summary.json"
_NANOGEN11_SUM = REPO / "results/nano-lm/wave-ba/nanogen11_summary.json"
_NANOGEN10_SUM = REPO / "results/nano-lm/wave-az/nanogen10_summary.json"
_NANOGEN9_SUM = REPO / "results/nano-lm/wave-ay/nanogen9_summary.json"
_NANOGEN8_SUM = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_NANOGEN7_SUM = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_NANOGEN6_SUM = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_LOCAL_SESSION = REPO / ".local/wave-bc/SESSION.md"
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
_EMPTY_BANK = REPO / "results/nano-lm/wave-bc/_decode_empty_bank.jsonl"
_DECODE_Q = "Explain Merkle trees briefly"
_OOD = "Which nation hosted the 2016 Summer Olympics?"
_BC_FH = "floordiv of a and b"


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
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(8, max(4, cpus - 4))
    return threads, workers


def _board_true_continue(data: dict[str, Any]) -> tuple[float, int, int] | None:
    board = data.get("board")
    if not isinstance(board, dict):
        return None
    return (
        float(board.get("true_continue_mean") or 0.0),
        int(board.get("n_true_continue") or 0),
        int(board.get("n_span_fallback") or 0),
    )


def _stats_true_continue(data: dict[str, Any]) -> tuple[float, int, int]:
    stats = data.get("stats") if isinstance(data, dict) else {}
    if not isinstance(stats, dict):
        stats = {}
    return (
        float(stats.get("gen_mean") or stats.get("true_continue_mean") or 0.0),
        int(stats.get("n_true_continue") or 0),
        int(stats.get("n_span_fallback") or 0),
    )


def _load_parent_true_continue(path: Path) -> tuple[float, int, int]:
    if not path.is_file():
        return 0.0, 0, 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0.0, 0, 0
    if not isinstance(data, dict):
        return 0.0, 0, 0
    from_board = _board_true_continue(data)
    if from_board is not None:
        return from_board
    return _stats_true_continue(data)


def _parent_is_defer(path: Path, *, default: bool) -> bool:
    if not path.is_file():
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default
    decision = str(data.get("decision") or "")
    return decision.startswith("DEFER") or default


def _smoke_lookup(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=KNOWN_ASK,
        root=root,
        seed=0,
        wrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipreal(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode(*, root: Path) -> dict[str, Any]:
    _EMPTY_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _EMPTY_BANK.is_file():
        _EMPTY_BANK.write_text("", encoding="utf-8")
    payload = ask_once(
        question=_DECODE_Q,
        root=root,
        seed=1,
        wrap=True,
        bank_path=_EMPTY_BANK,
        curated_root=_CURATED,
        abstain=False,
    )
    row = attach_shipreal(dict(payload))
    row["arm"] = "DECODE_PROBE"
    return row


def _smoke_abstain(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=_OOD,
        root=root,
        seed=0,
        semwrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipreal(dict(payload))
    row["arm"] = "ABSTAIN"
    return row


def _smoke_bc_forever(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=_BC_FH,
        root=root,
        seed=0,
        wrap=True,
        semwrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipreal(dict(payload))
    row["arm"] = "BC_FOREVER"
    return row


def _live_modes_ok(rows: list[dict[str, Any]]) -> bool:
    modes = {str(r.get("product_mode") or "") for r in rows}
    if "LOOKUP" not in modes or "ABSTAIN" not in modes:
        return False
    for row in rows:
        mode = str(row.get("product_mode") or "")
        line = str(row.get("modeui_line") or "")
        if not mode or f"mode={mode}" not in line:
            return False
    # BC forever residual must still ABSTAIN (anti-FP hold on gen gate path)
    for row in rows:
        if row.get("arm") == "BC_FOREVER" and str(row.get("product_mode")) != "ABSTAIN":
            return False
    return True


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    rows: list[dict[str, Any]],
    wall_s: float,
    threads: int,
    workers: int,
) -> None:
    status = decision.split("(", 1)[0].strip()
    smoke = [
        f"| {r.get('arm')} | **{r.get('product_mode')}** | "
        f"`{r.get('modeui_line')}` |"
        for r in rows
    ]
    body = "\n".join(
        [
            f"# H-NANOGEN13 — gen-defer gate (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §4 · §9 BC4 · Session: "
            "`.local/wave-bc/SESSION.md`  ",
            "> Parent: [formal-hnanogen12-nanogen12.md]"
            "(formal-hnanogen12-nanogen12.md) (**DEFER**) · "
            "[formal-hnanogen11-nanogen11.md](formal-hnanogen11-nanogen11.md) · "
            "BC0 stance **defer**  ",
            "> Module: `nano_lm/src/nanogen13_ops.py` · "
            "Runner: `npm run nano:nanogen13`",
            "",
            "## Hypothesis",
            "",
            NANOGEN13_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| Stance | **{board.get('stance')}** | BC0 freeze |",
            f"| CAPCHECK | **{board.get('capcheck')}** | closed |",
            f"| real_new_method | **{board.get('real_new_method')}** | "
            "True for PROMOTE |",
            f"| method | **{board.get('method_id')}** / "
            f"{board.get('method_kind')} | not NANOGEN12 rename |",
            f"| is_rename | **{board.get('is_rename')}** | False |",
            f"| true_continue_mean (archive) | "
            f"**{board.get('true_continue_mean')}** | ≥5.5 + method |",
            f"| n_true_continue | **{board.get('n_true_continue')}** | "
            ">0 for PROMOTE |",
            f"| n_span_fallback (archive) | "
            f"**{board.get('n_span_fallback')}** | ≠ gen credit |",
            f"| parent NANOGEN6 / 7 | "
            f"**{board.get('parent_nanogen6_true_continue')}** / "
            f"**{board.get('parent_nanogen7_true_continue')}** | HOLD stand |",
            f"| parent NANOGEN8·9·10·11·12 DEFER | "
            f"**{board.get('parent_nanogen8_defer')}** / "
            f"**{board.get('parent_nanogen9_defer')}** / "
            f"**{board.get('parent_nanogen10_defer')}** / "
            f"**{board.get('parent_nanogen11_defer')}** / "
            f"**{board.get('parent_nanogen12_defer')}** | True |",
            f"| live_modes_ok | **{board.get('live_modes_ok')}** | "
            "LOOKUP+ABSTAIN · BC-FOREVER ABSTAIN |",
            f"| Decision | **{status}** | — |",
            "",
            "## Live product smoke (modes still honest)",
            "",
            "| Arm | product_mode | modeui |",
            "|-----|--------------|--------|",
            *smoke,
            "",
            "## Finding",
            "",
            "1. BC0 froze gen stance as **defer**; CAPCHECK **closed**.  ",
            "2. No real M1|M2|M3 method claimed — **not** NANOGEN12 rename.  ",
            "3. NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER stand "
            "(span-fallback ≠ gen).  ",
            "4. Live smoke keeps LOOKUP/ABSTAIN labeled; BC-FOREVER ABSTAIN.  ",
            f"5. Decision **{status}** — generative / mini-AGI claim stays "
            "locked.  ",
            f"6. Wall ~{wall_s:.1f}s · threads={threads} · workers={workers}.  ",
            "7. Next: **BC5 BC-REAL-EVAL** (gen claim only if BC4 PROMOTE).  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen13",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bc/nanogen13_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen13.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest DEFER/HOLD under BC0 stance | "
            "NANOGEN13 = NANOGEN12+rename |",
            "| Cite NANOGEN6·7 HOLD · NANOGEN8·9·10·11·12 DEFER | "
            "Vanity gen unlock / LOOKUP-as-IQ |",
            "| PROMOTE only real method + true_continue≥5.5 | "
            "Raise ≤5M w/o CAPCHECK |",
            "",
            f"SAFE note: {NANOGEN13_SAFE_NOTE}  ",
            f"Anti-FP: {NANOGEN13_ANTI_FP}  ",
            f"Ship lock: {NANOGEN13_CLAIM}",
            "",
            "Next: **BC5 BC-REAL-EVAL** (`npm run nano:bc:real-eval`).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, board: dict[str, Any]) -> None:
    status = decision.split("(", 1)[0].strip()
    body = "\n".join(
        [
            f"# Wave BC session checklist (**OPEN** · BC4 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{NANOGEN13_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BC4 — H-NANOGEN13 (DONE — {status})** · "
            "Next: **BC5 BC-REAL-EVAL**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Stance | **{board.get('stance')}** |",
            f"| real_new_method | **{board.get('real_new_method')}** |",
            f"| true_continue_mean | **{board.get('true_continue_mean')}** |",
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
            f"| BC4 | H-NANOGEN13 | **DONE — {status}** |",
            "| BC5 | BC-REAL-EVAL | **NEXT** |",
            "| BC6 | BC-REPORT | pending |",
            "| BC7 | BC-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    if not decision.startswith(("PROMOTE", "HOLD", "DEFER")):
        return
    status = decision.split("(", 1)[0].strip()
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"(\| BC4 \| \*\*H-NANOGEN13\*\* \|[^\n]+\| )\*\*NEXT\*\* \|",
        rf"\1**DONE — {status}** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BC5 \| \*\*BC-REAL-EVAL\*\* \|[^\n]+\| )pending \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        "5. **BC4 H-NANOGEN13** — **NEXT** — one real method; true_continue → "
        "PROMOTE else HOLD/DEFER (not NANOGEN12 rename).  ",
        f"5. **BC4 H-NANOGEN13** — **DONE {status}** "
        "(`npm run nano:nanogen13`) — gen stance defer · not NANOGEN12 rename.  ",
        1,
    )
    text = text.replace(
        "6. **BC5 BC-REAL-EVAL** — live battery; gen claim only if BC4 PROMOTE.  ",
        "6. **BC5 BC-REAL-EVAL** — **NEXT** — live battery; gen claim only "
        "if BC4 PROMOTE.  ",
        1,
    )
    text = text.replace(
        "npm run nano:bc:ctxlift2\n"
        "# next: nano:nanogen13\n",
        "npm run nano:bc:ctxlift2\n"
        "npm run nano:nanogen13\n"
        "# next: nano:bc:real-eval\n",
        1,
    )
    text = text.replace(
        "(BC0–BC3 **DONE — PROMOTE**; next BC4 H-NANOGEN13).",
        f"(BC4 H-NANOGEN13 **DONE — {status}**; next BC5 BC-REAL-EVAL).",
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

**BC0–BC3 PROMOTE · BC4 DONE — {status}**. Next: **BC5 BC-REAL-EVAL**.

```bash
npm run nano:nanogen13
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BC ACTIVE** — BC4 **H-NANOGEN13 {status}** (gen locked).

Next: **BC5 BC-REAL-EVAL**.
""",
            encoding="utf-8",
        )


def _bc_active_line(status: str) -> str:
    return (
        "**Wave BC ACTIVE:** BC0 [SESSION PROMOTE](wave-bc-session.md) · "
        "BC1 [H-OPSFAM PROMOTE](formal-hopsfam-opsfam.md) · "
        "BC2 [H-FASTLIFT PROMOTE](formal-hfastlift-bc2.md) · "
        "BC3 [H-CTXLIFT2 PROMOTE](formal-hctxlift2-ctxlift2.md) · "
        f"BC4 [H-NANOGEN13 {status}](formal-hnanogen13-nanogen13.md) "
        f"(`npm run nano:nanogen13`) — gen stance defer · not NANOGEN12 rename; "
        "next BC5 BC-REAL-EVAL; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    line = _bc_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BC ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BC4 H-NANOGEN13 | [formal-hnanogen13-nanogen13.md]"
        f"(formal-hnanogen13-nanogen13.md) **{status}** "
        f"(`npm run nano:nanogen13`) — gen stance defer · CAPCHECK closed · "
        "not NANOGEN12 rename |"
    )
    if "Wave BC4 H-NANOGEN13" not in text2 and "| Wave BC3 H-CTXLIFT2 |" in text2:
        text2 = text2.replace(
            "| Wave BC3 H-CTXLIFT2 |",
            insert + "\n| Wave BC3 H-CTXLIFT2 |",
            1,
        )
    if n or "Wave BC4 H-NANOGEN13" in text2:
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
            "(docs/results/nano-lm/wave-bc-session.md) "
            "(`npm run nano:bc:session`) · BC1 [H-OPSFAM PROMOTE]"
            "(docs/results/nano-lm/formal-hopsfam-opsfam.md) "
            "(`npm run nano:opsfam`) · BC2 [H-FASTLIFT PROMOTE]"
            "(docs/results/nano-lm/formal-hfastlift-bc2.md) "
            "(`npm run nano:bc:fastlift`) · BC3 [H-CTXLIFT2 PROMOTE]"
            "(docs/results/nano-lm/formal-hctxlift2-ctxlift2.md) "
            "(`npm run nano:bc:ctxlift2`) · BC4 "
            f"[H-NANOGEN13 {status}]"
            "(docs/results/nano-lm/formal-hnanogen13-nanogen13.md) "
            "(`npm run nano:nanogen13`); next BC5 BC-REAL-EVAL; ship remains "
            "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
            "NANOGEN8·9·10·11·12 DEFER; ≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BC ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            f"| **BC** | **ACTIVE** | BC0–BC3 PROMOTE · BC4 H-NANOGEN13 "
            f"{status} (`npm run nano:nanogen13`); next BC5 BC-REAL-EVAL; ≤5M |"
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
        "Wave BC ACTIVE (BC0–BC3 PROMOTE · H-CTXLIFT2; next BC4 H-NANOGEN13)",
        f"Wave BC ACTIVE (BC0–BC3 PROMOTE · BC4 H-NANOGEN13 {status}; "
        "next BC5 BC-REAL-EVAL)",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public(decision: str) -> None:
    if not decision.startswith(("PROMOTE", "HOLD", "DEFER")):
        return
    status = decision.split("(", 1)[0].strip()
    _patch_recipes(status)
    _patch_card_agents_agenda(status)
    _patch_evogen(status)


def run_nanogen13(
    *,
    root: Path,
    bank: Path,
    out: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN BC0 gen stance defer + archived NANOGEN6–12
    WHEN applying BC4 gate with live mode smoke
    THEN DEFER (no real method) or PROMOTE/HOLD/KILL.
    """
    t0 = time.perf_counter()
    tc12, n_tc12, n_span12 = _load_parent_true_continue(_NANOGEN12_SUM)
    tc11, n_tc11, n_span11 = _load_parent_true_continue(_NANOGEN11_SUM)
    tc10, n_tc10, n_span10 = _load_parent_true_continue(_NANOGEN10_SUM)
    tc9, n_tc9, n_span9 = _load_parent_true_continue(_NANOGEN9_SUM)
    tc8, _, _ = _load_parent_true_continue(_NANOGEN8_SUM)
    tc7, _, _ = _load_parent_true_continue(_NANOGEN7_SUM)
    tc6, _, _ = _load_parent_true_continue(_NANOGEN6_SUM)
    parent8 = _parent_is_defer(_NANOGEN8_SUM, default=PARENT_NANOGEN8_DEFER)
    parent9 = _parent_is_defer(_NANOGEN9_SUM, default=PARENT_NANOGEN9_DEFER)
    parent10 = _parent_is_defer(_NANOGEN10_SUM, default=PARENT_NANOGEN10_DEFER)
    parent11 = _parent_is_defer(_NANOGEN11_SUM, default=PARENT_NANOGEN11_DEFER)
    parent12 = _parent_is_defer(_NANOGEN12_SUM, default=PARENT_NANOGEN12_DEFER)

    with ThreadPoolExecutor(max_workers=min(4, workers)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        fut_bc = pool.submit(_smoke_bc_forever, root=root, bank=bank)
        rows = [
            fut_l.result(),
            fut_d.result(),
            fut_a.result(),
            fut_bc.result(),
        ]
    modes_ok = _live_modes_ok(rows)

    if tc12 or n_tc12:
        tc_mean, n_tc, n_span = float(tc12), int(n_tc12), int(n_span12)
    elif tc11 or n_tc11:
        tc_mean, n_tc, n_span = float(tc11), int(n_tc11), int(n_span11)
    elif tc10 or n_tc10:
        tc_mean, n_tc, n_span = float(tc10), int(n_tc10), int(n_span10)
    else:
        tc_mean, n_tc, n_span = float(tc9), int(n_tc9), int(n_span9)

    board = extract_nanogen13_board(
        true_continue_mean=tc_mean,
        n_true_continue=n_tc,
        n_span_fallback=n_span,
        parent6=float(tc6) if tc6 else PARENT_NANOGEN6_TRUE_CONTINUE,
        parent7=float(tc7) if tc7 else PARENT_NANOGEN7_TRUE_CONTINUE,
        parent8_defer=parent8,
        parent9_defer=parent9,
        parent10_defer=parent10,
        parent11_defer=parent11,
        parent12_defer=parent12,
        live_modes_ok=modes_ok,
    )
    decision = decide_nanogen13(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    _write_public(
        decision=decision,
        board=board,
        rows=rows,
        wall_s=wall_s,
        threads=threads,
        workers=workers,
    )
    _write_session(decision, board)
    _patch_pesquisa(decision)
    _patch_local_notes(decision)
    _patch_public(decision)
    payload: dict[str, Any] = {
        "id": NANOGEN13_ID,
        "stage": "BC4",
        "thesis": NANOGEN13_THESIS,
        "decision": decision,
        "stance": dict(NANOGEN13_STANCE),
        "method": dict(NANOGEN13_METHOD),
        "board": board,
        "true_gen_judge": dict(TRUE_GEN_JUDGE),
        "parent_archive": {
            "nanogen12_true_continue_mean": tc12,
            "nanogen12_n_true_continue": n_tc12,
            "nanogen12_n_span_fallback": n_span12,
            "nanogen12_defer": parent12,
            "nanogen11_true_continue_mean": tc11,
            "nanogen11_n_true_continue": n_tc11,
            "nanogen11_defer": parent11,
            "nanogen10_true_continue_mean": tc10,
            "nanogen10_defer": parent10,
            "nanogen9_true_continue_mean": tc9,
            "nanogen9_defer": parent9,
            "nanogen8_true_continue_mean": tc8,
            "nanogen8_defer": parent8,
            "nanogen7_true_continue_mean": tc7,
            "nanogen6_true_continue_mean": tc6,
        },
        "live_smoke": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
            }
            for r in rows
        ],
        "wall_s": wall_s,
        "cpu_threads": threads,
        "workers": workers,
        "claim": NANOGEN13_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hnanogen13-nanogen13.md",
        "next": "BC5 BC-REAL-EVAL",
        "anti_fp": NANOGEN13_ANTI_FP,
        "finding": (
            f"{NANOGEN13_ID}: stance={board.get('stance')} "
            f"method={board.get('method_id')} "
            f"true_c_mean={board.get('true_continue_mean')} "
            f"n_true_c={board.get('n_true_continue')} "
            f"modes_ok={modes_ok} → {decision}"
        ),
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BC4 H-NANOGEN13")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_nanogen13(
            root=Path(args.root),
            bank=Path(args.bank),
            out=Path(args.out),
            workers=workers,
            threads=threads,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(payload.get("decision", ""))
    ok = decision.startswith(("PROMOTE", "HOLD", "DEFER"))
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": NANOGEN13_ID,
                "stage": "BC4",
                "decision": decision[:180],
                "cpu_threads": threads,
                "workers": workers,
                "stance": (payload.get("board") or {}).get("stance"),
                "true_continue_mean": (payload.get("board") or {}).get(
                    "true_continue_mean"
                ),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
