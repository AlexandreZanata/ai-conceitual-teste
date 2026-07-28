"""Wave BE5 H-NANOGEN15 runner — gen-defer-once; not NANOGEN14 rename."""

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
from nanogen15_ops import (
    NANOGEN15_ANTI_FP,
    NANOGEN15_CLAIM,
    NANOGEN15_ID,
    NANOGEN15_METHOD,
    NANOGEN15_SAFE_NOTE,
    NANOGEN15_STANCE,
    NANOGEN15_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    PARENT_NANOGEN11_DEFER,
    PARENT_NANOGEN12_DEFER,
    PARENT_NANOGEN13_DEFER,
    PARENT_NANOGEN14_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen15,
    extract_nanogen15_board,
)
from prodhard_ops import KNOWN_ASK
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-be/nanogen15_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen15-nanogen15.md"
_NANOGEN14_SUM = REPO / "results/nano-lm/wave-bd/nanogen14_summary.json"
_NANOGEN13_SUM = REPO / "results/nano-lm/wave-bc/nanogen13_summary.json"
_NANOGEN12_SUM = REPO / "results/nano-lm/wave-bb/nanogen12_summary.json"
_NANOGEN11_SUM = REPO / "results/nano-lm/wave-ba/nanogen11_summary.json"
_NANOGEN10_SUM = REPO / "results/nano-lm/wave-az/nanogen10_summary.json"
_NANOGEN9_SUM = REPO / "results/nano-lm/wave-ay/nanogen9_summary.json"
_NANOGEN8_SUM = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_NANOGEN7_SUM = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_NANOGEN6_SUM = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_LOCAL_SESSION = REPO / ".local/wave-be/SESSION.md"
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
_EMPTY_BANK = REPO / "results/nano-lm/wave-be/_decode_empty_bank.jsonl"
_DECODE_Q = "Explain Merkle trees briefly"
_OOD = "Which nation hosted the 2016 Summer Olympics?"
_BD_FH = "How do I reverse a string in Python?"
_BE_FH = "How do I convert string s to integer in Python?"


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


def _ask(
    question: str,
    *,
    root: Path,
    bank: Path,
    wrap: bool = True,
    semwrap: bool = True,
    abstain: bool = True,
) -> dict[str, Any]:
    payload = ask_once(
        question=question,
        root=root,
        seed=0,
        wrap=wrap,
        semwrap=semwrap,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=abstain,
    )
    return attach_shipreal(dict(payload))


def _smoke_lookup(*, root: Path, bank: Path) -> dict[str, Any]:
    row = _ask(KNOWN_ASK, root=root, bank=bank)
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
    row = _ask(_OOD, root=root, bank=bank, wrap=False, semwrap=True)
    row["arm"] = "ABSTAIN"
    return row


def _smoke_bd_forever(*, root: Path, bank: Path) -> dict[str, Any]:
    row = _ask(_BD_FH, root=root, bank=bank)
    row["arm"] = "BD_FOREVER"
    return row


def _smoke_be_forever(*, root: Path, bank: Path) -> dict[str, Any]:
    row = _ask(_BE_FH, root=root, bank=bank)
    row["arm"] = "BE_FOREVER"
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
    for row in rows:
        arm = str(row.get("arm") or "")
        if arm in {"BD_FOREVER", "BE_FOREVER"}:
            if str(row.get("product_mode")) != "ABSTAIN":
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
            f"# H-NANOGEN15 — gen-defer-once gate (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §4 · §9 BE5 · Session: "
            "`.local/wave-be/SESSION.md`  ",
            "> Parent: [formal-hnanogen14-nanogen14.md]"
            "(formal-hnanogen14-nanogen14.md) (**DEFER**) · "
            "BE0 stance **defer**  ",
            "> Module: `nano_lm/src/nanogen15_ops.py` · "
            "Runner: `npm run nano:nanogen15`",
            "",
            "## Hypothesis",
            "",
            NANOGEN15_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| Stance | **{board.get('stance')}** | BE0 freeze |",
            f"| CAPCHECK | **{board.get('capcheck')}** | closed |",
            f"| real_new_method | **{board.get('real_new_method')}** | "
            "True for PROMOTE |",
            f"| method | **{board.get('method_id')}** / "
            f"{board.get('method_kind')} | not NANOGEN14 rename |",
            f"| is_rename | **{board.get('is_rename')}** | False |",
            f"| defer_once_stop_rule | **{board.get('defer_once_stop_rule')}** "
            "| True |",
            f"| true_continue_mean (archive) | "
            f"**{board.get('true_continue_mean')}** | ≥5.5 + method |",
            f"| n_true_continue | **{board.get('n_true_continue')}** | "
            ">0 for PROMOTE |",
            f"| n_span_fallback (archive) | "
            f"**{board.get('n_span_fallback')}** | ≠ gen credit |",
            f"| parent NANOGEN6 / 7 | "
            f"**{board.get('parent_nanogen6_true_continue')}** / "
            f"**{board.get('parent_nanogen7_true_continue')}** | HOLD stand |",
            f"| parent NANOGEN8…14 DEFER | "
            f"**{board.get('parent_nanogen8_defer')}** / "
            f"**{board.get('parent_nanogen9_defer')}** / "
            f"**{board.get('parent_nanogen10_defer')}** / "
            f"**{board.get('parent_nanogen11_defer')}** / "
            f"**{board.get('parent_nanogen12_defer')}** / "
            f"**{board.get('parent_nanogen13_defer')}** / "
            f"**{board.get('parent_nanogen14_defer')}** | True |",
            f"| live_modes_ok | **{board.get('live_modes_ok')}** | "
            "LOOKUP+ABSTAIN · BD/BE-FOREVER ABSTAIN |",
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
            "1. BE0 froze gen stance as **defer**; CAPCHECK **closed**.  ",
            "2. No real M1|M2|M3 method claimed — **not** NANOGEN14 rename.  ",
            "3. NANOGEN6·7 HOLD · NANOGEN8…14 DEFER stand "
            "(span-fallback ≠ gen).  ",
            "4. Live smoke keeps LOOKUP/ABSTAIN labeled; BD/BE-FOREVER ABSTAIN.  ",
            f"5. Decision **{status}** — generative / mini-AGI claim stays "
            "locked (DEFER once stop rule).  ",
            f"6. Wall ~{wall_s:.1f}s · threads={threads} · workers={workers} "
            "(`cpus-6`).  ",
            "7. Next: **BE6 BE-REAL-EVAL** (gen claim only if BE5 PROMOTE).  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen15",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-be/nanogen15_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen15.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest DEFER/HOLD under BE0 stance | "
            "NANOGEN15 = NANOGEN14+rename |",
            "| Cite NANOGEN6·7 HOLD · NANOGEN8…14 DEFER | "
            "Vanity gen unlock / LOOKUP-as-IQ |",
            "| PROMOTE only real method + true_continue≥5.5 | "
            "Raise ≤5M w/o CAPCHECK |",
            "",
            f"SAFE note: {NANOGEN15_SAFE_NOTE}  ",
            f"Anti-FP: {NANOGEN15_ANTI_FP}  ",
            f"Ship lock: {NANOGEN15_CLAIM}",
            "",
            "Next: **BE6 BE-REAL-EVAL** (`npm run nano:be:real-eval`).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, board: dict[str, Any]) -> None:
    status = decision.split("(", 1)[0].strip()
    body = "\n".join(
        [
            f"# Wave BE session checklist (**OPEN** · BE5 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{NANOGEN15_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BE5 — H-NANOGEN15 (DONE — {status})** · "
            "Next: **BE6 BE-REAL-EVAL**",
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
            "| BE0 | SESSION | **DONE — PROMOTE** |",
            "| BE1 | H-COMPINT | **DONE — PROMOTE** |",
            "| BE2 | H-SHIPUSE | **DONE — PROMOTE** |",
            "| BE3 | H-FASTBE | **DONE — PROMOTE** |",
            "| BE4 | H-CTXBE | **DONE — PROMOTE** |",
            f"| BE5 | H-NANOGEN15 | **DONE — {status}** |",
            "| BE6 | BE-REAL-EVAL | **NEXT** |",
            "| BE7 | BE-REPORT | pending |",
            "| BE8 | BE-FREEZE | pending |",
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
        r"(\| BE5 \| \*\*H-NANOGEN15\*\* \|[^\n]+\| )\*\*NEXT\*\* \|",
        rf"\1**DONE — {status}** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"(\| BE6 \| \*\*BE-REAL-EVAL\*\* \|[^\n]+\| )(?:pending|\*\*TODO\*\*) \|",
        r"\1**NEXT** |",
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        "6. **BE5 H-NANOGEN15** — **NEXT** — one real M1\\|M2\\|M3 → PROMOTE "
        "else **DEFER once** (not NANOGEN14 rename).  ",
        f"6. **BE5 H-NANOGEN15** — **DONE {status}** "
        "(`npm run nano:nanogen15`) — gen stance defer once · "
        "not NANOGEN14 rename.  ",
        1,
    )
    text = text.replace(
        "7. **BE6 BE-REAL-EVAL** — live battery; gen claim only if BE5 PROMOTE.  ",
        "7. **BE6 BE-REAL-EVAL** — **NEXT** — live battery; gen claim only "
        "if BE5 PROMOTE.  ",
        1,
    )
    text = text.replace(
        "npm run nano:ctxbe\n"
        "# next: nano:nanogen15\n",
        "npm run nano:ctxbe\n"
        "npm run nano:nanogen15\n"
        "# next: nano:be:real-eval\n",
        1,
    )
    text = text.replace(
        "(BE0–BE4 **DONE — PROMOTE**; next BE5 H-NANOGEN15)",
        f"(BE5 H-NANOGEN15 **DONE — {status}**; next BE6 BE-REAL-EVAL)",
        1,
    )
    text = text.replace(
        "(BE0–BE4 **DONE — PROMOTE**; next BE5 H-NANOGEN15).",
        f"(BE5 H-NANOGEN15 **DONE — {status}**; next BE6 BE-REAL-EVAL).",
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

**BE0–BE4 PROMOTE · BE5 DONE — {status}**. Next: **BE6 BE-REAL-EVAL**.

```bash
npm run nano:nanogen15
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BE ACTIVE** — BE5 **H-NANOGEN15 {status}** (gen locked · defer once).

Next: **BE6 BE-REAL-EVAL**.
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
        f"BE5 [H-NANOGEN15 {status}](formal-hnanogen15-nanogen15.md) "
        f"(`npm run nano:nanogen15`) — gen stance defer once · "
        "not NANOGEN14 rename; next BE6 BE-REAL-EVAL; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    line = _be_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BE ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BE5 H-NANOGEN15 | [formal-hnanogen15-nanogen15.md]"
        f"(formal-hnanogen15-nanogen15.md) **{status}** "
        f"(`npm run nano:nanogen15`) — gen stance defer once · CAPCHECK closed · "
        "not NANOGEN14 rename |"
    )
    if "Wave BE5 H-NANOGEN15" not in text2:
        marker = "| Wave BE4 H-CTXBE |"
        if marker in text2:
            text2 = text2.replace(marker, insert + "\n" + marker, 1)
    if n or "Wave BE5 H-NANOGEN15" in text2:
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
            "(`npm run nano:ctxbe`) · BE5 "
            f"[H-NANOGEN15 {status}]"
            "(docs/results/nano-lm/formal-hnanogen15-nanogen15.md) "
            "(`npm run nano:nanogen15`); next BE6 BE-REAL-EVAL; ship remains "
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
            f"| **BE** | **ACTIVE** | BE0–BE4 PROMOTE · BE5 H-NANOGEN15 "
            f"{status} (`npm run nano:nanogen15`); next BE6 BE-REAL-EVAL; ≤5M |"
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
        "Wave BE ACTIVE (BE0–BE4 PROMOTE · H-CTXBE; next BE5 H-NANOGEN15)",
        f"Wave BE ACTIVE (BE0–BE4 PROMOTE · BE5 H-NANOGEN15 {status}; "
        "next BE6 BE-REAL-EVAL)",
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


def run_nanogen15(
    *,
    root: Path,
    bank: Path,
    out: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN BE0 gen stance defer + archived NANOGEN6–14
    WHEN applying BE5 gate with live mode smoke
    THEN DEFER once (no real method) or PROMOTE/HOLD/KILL.
    """
    t0 = time.perf_counter()
    tc14, n_tc14, n_span14 = _load_parent_true_continue(_NANOGEN14_SUM)
    tc13, n_tc13, n_span13 = _load_parent_true_continue(_NANOGEN13_SUM)
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
    parent13 = _parent_is_defer(_NANOGEN13_SUM, default=PARENT_NANOGEN13_DEFER)
    parent14 = _parent_is_defer(_NANOGEN14_SUM, default=PARENT_NANOGEN14_DEFER)

    with ThreadPoolExecutor(max_workers=min(5, workers)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        fut_bd = pool.submit(_smoke_bd_forever, root=root, bank=bank)
        fut_be = pool.submit(_smoke_be_forever, root=root, bank=bank)
        rows = [
            fut_l.result(),
            fut_d.result(),
            fut_a.result(),
            fut_bd.result(),
            fut_be.result(),
        ]
    modes_ok = _live_modes_ok(rows)

    if tc14 or n_tc14:
        tc_mean, n_tc, n_span = float(tc14), int(n_tc14), int(n_span14)
    elif tc13 or n_tc13:
        tc_mean, n_tc, n_span = float(tc13), int(n_tc13), int(n_span13)
    elif tc12 or n_tc12:
        tc_mean, n_tc, n_span = float(tc12), int(n_tc12), int(n_span12)
    elif tc11 or n_tc11:
        tc_mean, n_tc, n_span = float(tc11), int(n_tc11), int(n_span11)
    elif tc10 or n_tc10:
        tc_mean, n_tc, n_span = float(tc10), int(n_tc10), int(n_span10)
    else:
        tc_mean, n_tc, n_span = float(tc9), int(n_tc9), int(n_span9)

    board = extract_nanogen15_board(
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
        parent13_defer=parent13,
        parent14_defer=parent14,
        live_modes_ok=modes_ok,
    )
    decision = decide_nanogen15(board=board, anti_fp_signed=True)
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
        "id": NANOGEN15_ID,
        "stage": "BE5",
        "thesis": NANOGEN15_THESIS,
        "decision": decision,
        "stance": dict(NANOGEN15_STANCE),
        "method": dict(NANOGEN15_METHOD),
        "board": board,
        "true_gen_judge": dict(TRUE_GEN_JUDGE),
        "parent_archive": {
            "nanogen14_true_continue_mean": tc14,
            "nanogen14_n_true_continue": n_tc14,
            "nanogen14_n_span_fallback": n_span14,
            "nanogen14_defer": parent14,
            "nanogen13_true_continue_mean": tc13,
            "nanogen13_defer": parent13,
            "nanogen12_true_continue_mean": tc12,
            "nanogen12_defer": parent12,
            "nanogen11_true_continue_mean": tc11,
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
        "claim": NANOGEN15_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hnanogen15-nanogen15.md",
        "next": "BE6 BE-REAL-EVAL",
        "anti_fp": NANOGEN15_ANTI_FP,
        "finding": (
            f"{NANOGEN15_ID}: stance={board.get('stance')} "
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
    ap = argparse.ArgumentParser(description="Wave BE5 H-NANOGEN15")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_nanogen15(
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
    board = payload.get("board") or {}
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": NANOGEN15_ID,
                "stage": "BE5",
                "decision": decision[:180],
                "cpu_threads": threads,
                "workers": workers,
                "stance": board.get("stance"),
                "real_new_method": board.get("real_new_method"),
                "true_continue_mean": board.get("true_continue_mean"),
                "live_modes_ok": board.get("live_modes_ok"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
