"""Wave BA4 H-NANOGEN11 runner — gen-defer; not NANOGEN10 rename."""

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
from nanogen11_ops import (
    NANOGEN11_ANTI_FP,
    NANOGEN11_CLAIM,
    NANOGEN11_ID,
    NANOGEN11_METHOD,
    NANOGEN11_SAFE_NOTE,
    NANOGEN11_STANCE,
    NANOGEN11_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen11,
    extract_nanogen11_board,
)
from prodhard_ops import KNOWN_ASK
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ba/nanogen11_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen11-nanogen11.md"
_NANOGEN10_SUM = REPO / "results/nano-lm/wave-az/nanogen10_summary.json"
_NANOGEN9_SUM = REPO / "results/nano-lm/wave-ay/nanogen9_summary.json"
_NANOGEN8_SUM = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_NANOGEN7_SUM = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_NANOGEN6_SUM = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_LOCAL_SESSION = REPO / ".local/wave-ba/SESSION.md"
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
_EMPTY_BANK = REPO / "results/nano-lm/wave-ba/_decode_empty_bank.jsonl"
_DECODE_Q = "Explain Merkle trees briefly"
_OOD = "Which nation hosted the 2016 Summer Olympics?"


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
    workers = min(10, max(4, cpus - 4))
    return threads, workers


def _load_parent_true_continue(path: Path) -> tuple[float, int, int]:
    if not path.is_file():
        return 0.0, 0, 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0.0, 0, 0
    board = data.get("board") if isinstance(data, dict) else None
    if isinstance(board, dict):
        return (
            float(board.get("true_continue_mean") or 0.0),
            int(board.get("n_true_continue") or 0),
            int(board.get("n_span_fallback") or 0),
        )
    stats = data.get("stats") if isinstance(data, dict) else {}
    if not isinstance(stats, dict):
        stats = {}
    return (
        float(stats.get("gen_mean") or stats.get("true_continue_mean") or 0.0),
        int(stats.get("n_true_continue") or 0),
        int(stats.get("n_span_fallback") or 0),
    )


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


def _live_modes_ok(rows: list[dict[str, Any]]) -> bool:
    modes = {str(r.get("product_mode") or "") for r in rows}
    if "LOOKUP" not in modes or "ABSTAIN" not in modes:
        return False
    for row in rows:
        mode = str(row.get("product_mode") or "")
        line = str(row.get("modeui_line") or "")
        if not mode or f"mode={mode}" not in line:
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
            f"# H-NANOGEN11 — gen-defer gate (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §4 · §8 BA4 · Session: "
            "`.local/wave-ba/SESSION.md`  ",
            "> Parent: [formal-hnanogen10-nanogen10.md]"
            "(formal-hnanogen10-nanogen10.md) (**DEFER**) · "
            "[formal-hnanogen9-nanogen9.md](formal-hnanogen9-nanogen9.md) · "
            "BA0 stance **defer**  ",
            "> Module: `nano_lm/src/nanogen11_ops.py` · "
            "Runner: `npm run nano:nanogen11`",
            "",
            "## Hypothesis",
            "",
            NANOGEN11_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| Stance | **{board.get('stance')}** | BA0 freeze |",
            f"| CAPCHECK | **{board.get('capcheck')}** | closed |",
            f"| real_new_method | **{board.get('real_new_method')}** | "
            "True for PROMOTE |",
            f"| method | **{board.get('method_id')}** / "
            f"{board.get('method_kind')} | not NANOGEN10 rename |",
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
            f"| parent NANOGEN8·9·10 DEFER | "
            f"**{board.get('parent_nanogen8_defer')}** / "
            f"**{board.get('parent_nanogen9_defer')}** / "
            f"**{board.get('parent_nanogen10_defer')}** | True |",
            f"| live_modes_ok | **{board.get('live_modes_ok')}** | "
            "LOOKUP+ABSTAIN labeled |",
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
            "1. BA0 froze gen stance as **defer**; CAPCHECK **closed**.  ",
            "2. No real M1|M2|M3 method claimed — **not** NANOGEN10 rename.  ",
            "3. NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand "
            "(span-fallback ≠ gen).  ",
            "4. Live smoke keeps LOOKUP/ABSTAIN labeled on prod path.  ",
            f"5. Decision **{status}** — generative / mini-AGI claim stays "
            "locked.  ",
            f"6. Wall ~{wall_s:.1f}s · threads={threads} · workers={workers}.  ",
            "7. Next: **BA5 BA-REAL-EVAL** (gen claim only if BA4 PROMOTE).  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen11",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ba/nanogen11_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen11.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest DEFER/HOLD under BA0 stance | "
            "NANOGEN11 = NANOGEN10+rename |",
            "| Cite NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER | "
            "Vanity gen unlock / LOOKUP-as-IQ |",
            "| PROMOTE only real method + true_continue≥5.5 | "
            "Raise ≤5M w/o CAPCHECK |",
            "",
            f"SAFE note: {NANOGEN11_SAFE_NOTE}  ",
            f"Anti-FP: {NANOGEN11_ANTI_FP}  ",
            f"Ship lock: {NANOGEN11_CLAIM}",
            "",
            "Next: **BA5 BA-REAL-EVAL** (`npm run nano:ba:real-eval`).",
            "",
        ]
    )
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, board: dict[str, Any]) -> None:
    status = decision.split("(", 1)[0].strip()
    body = "\n".join(
        [
            f"# Wave BA session checklist (**OPEN** · BA4 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{NANOGEN11_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BA4 — H-NANOGEN11 (DONE — {status})** · "
            "Next: **BA5 BA-REAL-EVAL**",
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
            "| BA0 | SESSION | **DONE — PROMOTE** |",
            "| BA1 | H-REALGAIN | **DONE — PROMOTE** |",
            "| BA2 | H-FASTREAL | **DONE — PROMOTE** |",
            "| BA3 | H-CTXREAL2 | **DONE — PROMOTE** |",
            f"| BA4 | H-NANOGEN11 | **DONE — {status}** |",
            "| BA5 | BA-REAL-EVAL | **NEXT** |",
            "| BA6 | BA-REPORT | pending |",
            "| BA7 | BA-FREEZE | pending |",
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
    ba4_next = (
        "| BA4 | **H-NANOGEN11** | One real gen method / hybrid / CAPCHECK — "
        "else HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | **NEXT** |"
    )
    ba4_done = (
        "| BA4 | **H-NANOGEN11** | One real gen method / hybrid / CAPCHECK — "
        "else HOLD/DEFER | true_continue → PROMOTE else HOLD/DEFER | "
        f"**DONE — {status}** |"
    )
    if ba4_next in text:
        text = text.replace(ba4_next, ba4_done, 1)
    text = text.replace(
        "5. **BA4 H-NANOGEN11** — **NEXT** — one real method or **HOLD/DEFER** "
        "(cite NANOGEN6–10).  ",
        f"5. **BA4 H-NANOGEN11** — **DONE {status}** "
        "(`npm run nano:nanogen11`) — gen stance defer · not NANOGEN10 rename.  ",
        1,
    )
    text = text.replace(
        "6. **BA5→BA7** — real-eval · report · freeze.  ",
        "6. **BA5 BA-REAL-EVAL** — **NEXT** — product + ctx + speed + gen "
        "(gen claim iff BA4 PROMOTE).  \n"
        "7. **BA6→BA7** — report · freeze.  ",
        1,
    )
    ba5_todo = (
        "| BA5 | **BA-REAL-EVAL** | Product + ctx + speed + gen + **live ask** "
        "(prod=eval) | gen claim iff BA4 PROMOTE | **TODO** |"
    )
    ba5_next = (
        "| BA5 | **BA-REAL-EVAL** | Product + ctx + speed + gen + **live ask** "
        "(prod=eval) | gen claim iff BA4 PROMOTE | **NEXT** |"
    )
    if ba5_todo in text:
        text = text.replace(ba5_todo, ba5_next, 1)
    text = text.replace(
        "npm run nano:ba:ctxreal2\n"
        "# next: nano:nanogen11\n",
        "npm run nano:ba:ctxreal2\n"
        "npm run nano:nanogen11\n"
        "# next: nano:ba:real-eval\n",
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ba/SESSION.md` (BA0–BA3 **DONE — PROMOTE**; "
        "next BA4 H-NANOGEN11).  ",
        "> **Session:** `.local/wave-ba/SESSION.md` "
        f"(BA4 H-NANOGEN11 **DONE — {status}**; next BA5 BA-REAL-EVAL).  ",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    _LOCAL_IMPL.write_text(
        f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BA0–BA3 PROMOTE · BA4 DONE — {status}**. Next: **BA5 BA-REAL-EVAL**.

```bash
npm run nano:nanogen11
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BA ACTIVE** — BA4 **H-NANOGEN11 {status}** (gen locked).

Next: **BA5 BA-REAL-EVAL**.
""",
        encoding="utf-8",
    )


def _ba_active_line(status: str) -> str:
    return (
        "**Wave BA ACTIVE:** BA0 [SESSION PROMOTE](wave-ba-session.md) · "
        "BA1 [H-REALGAIN PROMOTE](formal-hrealgain-realgain.md) · "
        "BA2 [H-FASTREAL PROMOTE](formal-hfastreal-ba2.md) · "
        "BA3 [H-CTXREAL2 PROMOTE](formal-hctxreal2-ctxreal2.md) · "
        f"BA4 [H-NANOGEN11 {status}](formal-hnanogen11-nanogen11.md) "
        f"(`npm run nano:nanogen11`) — gen stance defer · not NANOGEN10 rename; "
        "next BA5 BA-REAL-EVAL; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    line = _ba_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BA ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BA4 H-NANOGEN11 | [formal-hnanogen11-nanogen11.md]"
        f"(formal-hnanogen11-nanogen11.md) **{status}** "
        f"(`npm run nano:nanogen11`) — gen stance defer · CAPCHECK closed · "
        "not NANOGEN10 rename |"
    )
    if "Wave BA4 H-NANOGEN11" not in text2 and "Wave BA3 H-CTXREAL2 |" in text2:
        text2 = text2.replace(
            "| Wave BA3 H-CTXREAL2 |",
            insert + "\n| Wave BA3 H-CTXREAL2 |",
            1,
        )
    if n or "Wave BA4 H-NANOGEN11" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _patch_card_agents_agenda(status: str) -> None:
    line = _ba_active_line(status)
    if _CARD.is_file():
        text = _CARD.read_text(encoding="utf-8")
        text2, n = re.subn(
            r"\*\*Wave BA ACTIVE\*\* —[^\n]+",
            line.replace("**Wave BA ACTIVE:**", "**Wave BA ACTIVE** —"),
            text,
            count=1,
        )
        if n:
            _CARD.write_text(text2, encoding="utf-8")
    if _AGENTS.is_file():
        text = _AGENTS.read_text(encoding="utf-8")
        agents = (
            "- **Wave BA ACTIVE** — BA0 [SESSION PROMOTE]"
            "(docs/results/nano-lm/wave-ba-session.md) · BA1 [H-REALGAIN PROMOTE]"
            "(docs/results/nano-lm/formal-hrealgain-realgain.md) · BA2 "
            "[H-FASTREAL PROMOTE](docs/results/nano-lm/formal-hfastreal-ba2.md) · "
            "BA3 [H-CTXREAL2 PROMOTE]"
            "(docs/results/nano-lm/formal-hctxreal2-ctxreal2.md) · BA4 "
            f"[H-NANOGEN11 {status}]"
            "(docs/results/nano-lm/formal-hnanogen11-nanogen11.md) "
            "(`npm run nano:nanogen11`); next BA5 BA-REAL-EVAL; ship remains "
            "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
        )
        text2, n = re.subn(
            r"- \*\*Wave BA ACTIVE\*\* —[^\n]+", agents, text, count=1
        )
        if n:
            _AGENTS.write_text(text2, encoding="utf-8")
    if _AGENDA.is_file():
        text = _AGENDA.read_text(encoding="utf-8")
        row = (
            f"| **BA** | **ACTIVE** | BA0–BA3 PROMOTE · BA4 H-NANOGEN11 "
            f"{status} (`npm run nano:nanogen11`); next BA5 BA-REAL-EVAL; ≤5M |"
        )
        text2, n = re.subn(
            r"\| \*\*BA\*\* \| \*\*ACTIVE\*\* \|[^\n]+", row, text, count=1
        )
        if n:
            _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    text = text.replace(
        "BA0–BA3 PROMOTE (H-CTXREAL2); next BA4 H-NANOGEN11",
        f"BA0–BA3 PROMOTE · BA4 H-NANOGEN11 {status}; next BA5 BA-REAL-EVAL",
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


def run_nanogen11(
    *,
    root: Path,
    bank: Path,
    out: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN BA0 gen stance defer + archived NANOGEN6–10
    WHEN applying BA4 gate with live mode smoke
    THEN DEFER (no real method) or PROMOTE/HOLD/KILL.
    """
    t0 = time.perf_counter()
    tc10, n_tc10, n_span10 = _load_parent_true_continue(_NANOGEN10_SUM)
    tc9, n_tc9, n_span9 = _load_parent_true_continue(_NANOGEN9_SUM)
    tc8, _, _ = _load_parent_true_continue(_NANOGEN8_SUM)
    tc7, _, _ = _load_parent_true_continue(_NANOGEN7_SUM)
    tc6, _, _ = _load_parent_true_continue(_NANOGEN6_SUM)
    parent8 = _parent_is_defer(_NANOGEN8_SUM, default=PARENT_NANOGEN8_DEFER)
    parent9 = _parent_is_defer(_NANOGEN9_SUM, default=PARENT_NANOGEN9_DEFER)
    parent10 = _parent_is_defer(_NANOGEN10_SUM, default=PARENT_NANOGEN10_DEFER)

    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        rows = [fut_l.result(), fut_d.result(), fut_a.result()]
    modes_ok = _live_modes_ok(rows)

    # Honest archive: prefer NANOGEN10 board; fallback NANOGEN9.
    tc_mean = float(tc10) if tc10 else float(tc9)
    n_tc = int(n_tc10) if n_tc10 else int(n_tc9)
    n_span = int(n_span10) if n_span10 else int(n_span9)

    board = extract_nanogen11_board(
        true_continue_mean=tc_mean,
        n_true_continue=n_tc,
        n_span_fallback=n_span,
        parent6=float(tc6) if tc6 else PARENT_NANOGEN6_TRUE_CONTINUE,
        parent7=float(tc7) if tc7 else PARENT_NANOGEN7_TRUE_CONTINUE,
        parent8_defer=parent8,
        parent9_defer=parent9,
        parent10_defer=parent10,
        live_modes_ok=modes_ok,
    )
    decision = decide_nanogen11(board=board, anti_fp_signed=True)
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
        "id": NANOGEN11_ID,
        "stage": "BA4",
        "thesis": NANOGEN11_THESIS,
        "decision": decision,
        "stance": dict(NANOGEN11_STANCE),
        "method": dict(NANOGEN11_METHOD),
        "board": board,
        "true_gen_judge": dict(TRUE_GEN_JUDGE),
        "parent_archive": {
            "nanogen10_true_continue_mean": tc10,
            "nanogen10_n_true_continue": n_tc10,
            "nanogen10_n_span_fallback": n_span10,
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
        "claim": NANOGEN11_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hnanogen11-nanogen11.md",
        "next": "BA5 BA-REAL-EVAL",
        "anti_fp": NANOGEN11_ANTI_FP,
        "finding": (
            f"{NANOGEN11_ID}: stance={board.get('stance')} "
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
    ap = argparse.ArgumentParser(description="Wave BA4 H-NANOGEN11")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_nanogen11(
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
                "hyp_id": NANOGEN11_ID,
                "stage": "BA4",
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
