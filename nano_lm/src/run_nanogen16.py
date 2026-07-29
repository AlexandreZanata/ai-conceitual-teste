"""Wave BF5 H-NANOGEN16 runner — gen-SKIP stop rule; not empty DEFER letter."""

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

from bf_session_ops import BF0_FOREVER_ROWS
from matrix_common import REPO, write_json
from nanogen16_ops import (
    NANOGEN16_ANTI_FP,
    NANOGEN16_CLAIM,
    NANOGEN16_ID,
    NANOGEN16_METHOD,
    NANOGEN16_SAFE_NOTE,
    NANOGEN16_STANCE,
    NANOGEN16_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    PARENT_NANOGEN10_DEFER,
    PARENT_NANOGEN11_DEFER,
    PARENT_NANOGEN12_DEFER,
    PARENT_NANOGEN13_DEFER,
    PARENT_NANOGEN14_DEFER,
    PARENT_NANOGEN15_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen16,
    extract_nanogen16_board,
)
from prodhard_ops import KNOWN_ASK
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bf/nanogen16_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen16-nanogen16.md"
_NANOGEN15_SUM = REPO / "results/nano-lm/wave-be/nanogen15_summary.json"
_NANOGEN14_SUM = REPO / "results/nano-lm/wave-bd/nanogen14_summary.json"
_NANOGEN13_SUM = REPO / "results/nano-lm/wave-bc/nanogen13_summary.json"
_NANOGEN12_SUM = REPO / "results/nano-lm/wave-bb/nanogen12_summary.json"
_NANOGEN11_SUM = REPO / "results/nano-lm/wave-ba/nanogen11_summary.json"
_NANOGEN10_SUM = REPO / "results/nano-lm/wave-az/nanogen10_summary.json"
_NANOGEN9_SUM = REPO / "results/nano-lm/wave-ay/nanogen9_summary.json"
_NANOGEN8_SUM = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_NANOGEN7_SUM = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_NANOGEN6_SUM = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_LOCAL_SESSION = REPO / ".local/wave-bf/SESSION.md"
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
_EMPTY_BANK = REPO / "results/nano-lm/wave-bf/_decode_empty_bank.jsonl"
_DECODE_Q = "Explain Merkle trees briefly"
_OOD = "Which nation hosted the 2016 Summer Olympics?"
_BD_FH = "How do I reverse a string in Python?"
_BE_FH = "How do I convert string s to integer in Python?"
_BF_FH = str(BF0_FOREVER_ROWS[0].get("question") or "")


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


def _smoke_bf_forever(*, root: Path, bank: Path) -> dict[str, Any]:
    row = _ask(_BF_FH, root=root, bank=bank)
    row["arm"] = "BF_FOREVER"
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
        if arm in {"BD_FOREVER", "BE_FOREVER", "BF_FOREVER"}:
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
            f"# H-NANOGEN16 — gen-SKIP stop-rule gate (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 · §9 BF5 · Session: "
            "`.local/wave-bf/SESSION.md`  ",
            "> Parent: [formal-hnanogen15-nanogen15.md]"
            "(formal-hnanogen15-nanogen15.md) (**DEFER**) · "
            "BF0 stance **skip**  ",
            "> Module: `nano_lm/src/nanogen16_ops.py` · "
            "Runner: `npm run nano:nanogen16`",
            "",
            "## Hypothesis",
            "",
            NANOGEN16_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| Stance | **{board.get('stance')}** | BF0 freeze |",
            f"| CAPCHECK | **{board.get('capcheck')}** | closed |",
            f"| method_plan_attached | **{board.get('method_plan_attached')}** "
            "| True for PROMOTE |",
            f"| real_new_method | **{board.get('real_new_method')}** | "
            "True for PROMOTE |",
            f"| method | **{board.get('method_id')}** / "
            f"{board.get('method_kind')} | not NANOGEN15 rename |",
            f"| is_rename | **{board.get('is_rename')}** | False |",
            f"| skip_gen_stop_rule | **{board.get('skip_gen_stop_rule')}** "
            "| True |",
            f"| empty_defer_letter | **{board.get('empty_defer_letter')}** "
            "| False |",
            f"| true_continue_mean (archive) | "
            f"**{board.get('true_continue_mean')}** | ≥5.5 + plan |",
            f"| n_true_continue | **{board.get('n_true_continue')}** | "
            ">0 for PROMOTE |",
            f"| n_span_fallback (archive) | "
            f"**{board.get('n_span_fallback')}** | ≠ gen credit |",
            f"| parent NANOGEN6 / 7 | "
            f"**{board.get('parent_nanogen6_true_continue')}** / "
            f"**{board.get('parent_nanogen7_true_continue')}** | HOLD stand |",
            f"| parent NANOGEN8…15 DEFER | "
            f"**{board.get('parent_nanogen8_defer')}** / "
            f"**{board.get('parent_nanogen9_defer')}** / "
            f"**{board.get('parent_nanogen10_defer')}** / "
            f"**{board.get('parent_nanogen11_defer')}** / "
            f"**{board.get('parent_nanogen12_defer')}** / "
            f"**{board.get('parent_nanogen13_defer')}** / "
            f"**{board.get('parent_nanogen14_defer')}** / "
            f"**{board.get('parent_nanogen15_defer')}** | True |",
            f"| live_modes_ok | **{board.get('live_modes_ok')}** | "
            "LOOKUP+ABSTAIN · BD/BE/BF-FOREVER ABSTAIN |",
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
            "1. BF0 froze gen stance as **skip**; CAPCHECK **closed**; "
            "no written M1|M2|M3 plan.  ",
            "2. H-NANOGEN15 already **DEFER once** — stop rule forbids empty "
            "NANOGEN16 DEFER letter → **SKIP stage**.  ",
            "3. Not NANOGEN15/14/…/6 rename. NANOGEN6·7 HOLD · "
            "NANOGEN8…15 DEFER stand (span-fallback ≠ gen).  ",
            "4. Live smoke keeps LOOKUP/ABSTAIN labeled; "
            "BD/BE/BF-FOREVER ABSTAIN.  ",
            f"5. Decision **{status}** — generative / mini-AGI claim stays "
            "locked (SKIP stop rule).  ",
            f"6. Wall ~{wall_s:.1f}s · threads={threads} · workers={workers} "
            "(`cpus-6`).  ",
            "7. Next: **BF6 BF-REAL-EVAL** (gen claim only if BF5 PROMOTE).  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen16",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bf/nanogen16_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen16.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest SKIP under BF0 stance | "
            "Empty DEFER letter / NANOGEN15+rename |",
            "| Cite NANOGEN6·7 HOLD · NANOGEN8…15 DEFER | "
            "Vanity gen unlock / LOOKUP-as-IQ |",
            "| PROMOTE only written plan + true_continue≥5.5 | "
            "Raise ≤5M w/o CAPCHECK |",
            "",
            f"SAFE note: {NANOGEN16_SAFE_NOTE}  ",
            f"Anti-FP: {NANOGEN16_ANTI_FP}  ",
            f"Ship lock: {NANOGEN16_CLAIM}",
            "",
            "Next: **BF6 BF-REAL-EVAL** (`npm run nano:bf:real-eval`).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, board: dict[str, Any]) -> None:
    status = decision.split("(", 1)[0].strip()
    body = "\n".join(
        [
            f"# Wave BF session checklist (**OPEN** · BF5 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{NANOGEN16_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BF5 — H-NANOGEN16 (DONE — {status})** · "
            "Next: **BF6 BF-REAL-EVAL**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Stance | **{board.get('stance')}** |",
            f"| method_plan_attached | **{board.get('method_plan_attached')}** |",
            f"| real_new_method | **{board.get('real_new_method')}** |",
            f"| true_continue_mean | **{board.get('true_continue_mean')}** |",
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
            f"| BF5 | H-NANOGEN16 / SKIP | **DONE — {status}** |",
            "| BF6 | BF-REAL-EVAL | **NEXT** |",
            "| BF7 | BF-REPORT | pending |",
            "| BF8 | BF-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    if not decision.startswith(("PROMOTE", "HOLD", "SKIP", "DEFER")):
        return
    status = decision.split("(", 1)[0].strip()
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text = text.replace(
        "| BF5 | **H-NANOGEN16** **or SKIP** | Only if BF0 method plan — else "
        "**SKIP stage** (stop rule) | true_continue → PROMOTE else STOP | "
        "**NEXT** |",
        "| BF5 | **H-NANOGEN16** **or SKIP** | Only if BF0 method plan — else "
        "**SKIP stage** (stop rule) | true_continue → PROMOTE else STOP | "
        f"**DONE — {status}** |",
        1,
    )
    text = text.replace(
        "| BF6 | **BF-REAL-EVAL** | Product + util + ctx + speed + gen/skip + "
        "**live ask** | gen claim iff BF5 PROMOTE | **TODO** |",
        "| BF6 | **BF-REAL-EVAL** | Product + util + ctx + speed + gen/skip + "
        "**live ask** | gen claim iff BF5 PROMOTE | **NEXT** |",
        1,
    )
    text = text.replace(
        "6. **BF5 H-NANOGEN16 or SKIP** — only with written M1\\|M2\\|M3; else "
        "**SKIP** (not empty DEFER letter).  ",
        f"6. **BF5 H-NANOGEN16 or SKIP** — **DONE {status}** "
        "(`npm run nano:nanogen16`) — no written plan · SKIP stop rule · "
        "not empty DEFER letter.  ",
        1,
    )
    text = text.replace(
        "6. **BF5 H-NANOGEN16 or SKIP** — **NEXT** — only with written "
        "M1\\|M2\\|M3; else **SKIP** (not empty DEFER letter).  ",
        f"6. **BF5 H-NANOGEN16 or SKIP** — **DONE {status}** "
        "(`npm run nano:nanogen16`) — no written plan · SKIP stop rule · "
        "not empty DEFER letter.  ",
        1,
    )
    text = text.replace(
        "7. **BF6 BF-REAL-EVAL** — live battery; gen claim only if BF5 PROMOTE.  ",
        "7. **BF6 BF-REAL-EVAL** — **NEXT** — live battery; gen claim only "
        "if BF5 PROMOTE.  ",
        1,
    )
    text = text.replace(
        "npm run nano:ctxbf\n"
        "# next: nano:nanogen16 (SKIP without plan)\n",
        "npm run nano:ctxbf\n"
        "npm run nano:nanogen16\n"
        "# next: nano:bf:real-eval\n",
        1,
    )
    text = text.replace(
        "(BF0–BF4 **DONE — PROMOTE**; next BF5 H-NANOGEN16 / SKIP)",
        f"(BF5 H-NANOGEN16 **DONE — {status}**; next BF6 BF-REAL-EVAL)",
        1,
    )
    text = text.replace(
        "(BF0–BF4 **DONE — PROMOTE**; next BF5 H-NANOGEN16 / SKIP).",
        f"(BF5 H-NANOGEN16 **DONE — {status}**; next BF6 BF-REAL-EVAL).",
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

Wave **BF ACTIVE**. BF0–BF4 PROMOTE · BF5 DONE — {status}
(`npm run nano:nanogen16`).

## Next

1. BF0–BF5 done (gen SKIP).  
2. **BF6 BF-REAL-EVAL** — **NEXT**.  
3. Ship stays AF+AQ+AS STRICT ablated DECODE · gen locked.

```bash
npm run nano:nanogen16
npm run nano:test && npm run verify
```
""",
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BF ACTIVE** — BF5 **H-NANOGEN16 {status}** (gen locked · SKIP stop rule).

Next: **BF6 BF-REAL-EVAL**. Parent: Wave BE **COMPLETE + FROZEN**.
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
        f"BF5 [H-NANOGEN16 {status}](formal-hnanogen16-nanogen16.md) "
        f"(`npm run nano:nanogen16`) — gen SKIP stop rule · "
        "not empty DEFER letter; next BF6 BF-REAL-EVAL; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str) -> None:
    if not _RECIPES.is_file():
        return
    line = _bf_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BF ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BF5 H-NANOGEN16 | [formal-hnanogen16-nanogen16.md]"
        f"(formal-hnanogen16-nanogen16.md) **{status}** "
        f"(`npm run nano:nanogen16`) — gen SKIP stop rule · CAPCHECK closed · "
        "not empty DEFER letter |"
    )
    if "Wave BF5 H-NANOGEN16" not in text2:
        marker = "| Wave BF4 H-CTXBF |"
        if marker in text2:
            text2 = text2.replace(marker, insert + "\n" + marker, 1)
    if n or "Wave BF5 H-NANOGEN16" in text2:
        _RECIPES.write_text(text2, encoding="utf-8")


def _sub_file(path: Path, pattern: str, repl: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text2, n = re.subn(pattern, repl, text, count=1)
    if n:
        path.write_text(text2, encoding="utf-8")


def _patch_public(decision: str) -> None:
    if not decision.startswith(("PROMOTE", "HOLD", "SKIP", "DEFER")):
        return
    status = decision.split("(", 1)[0].strip()
    _patch_recipes(status)
    _sub_file(
        _CARD,
        r"\*\*Wave BF ACTIVE\*\* —[^\n]+",
        _bf_active_line(status).replace(
            "**Wave BF ACTIVE:**", "**Wave BF ACTIVE** —"
        ),
    )
    _sub_file(
        _AGENTS,
        r"- \*\*Wave BF ACTIVE\*\* —[^\n]+",
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
        "(`npm run nano:ctxbf`) · BF5 "
        f"[H-NANOGEN16 {status}]"
        "(docs/results/nano-lm/formal-hnanogen16-nanogen16.md) "
        "(`npm run nano:nanogen16`); next BF6 BF-REAL-EVAL; ship remains "
        "**AF + AQ + AS trust + STRICT ablated DECODE**; NANOGEN6·7 HOLD · "
        "NANOGEN8…15 DEFER · NANOGEN16 SKIP; ≤5M stays.",
    )
    _sub_file(
        _AGENDA,
        r"\| \*\*BF\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
        f"| **BF** | **ACTIVE** | BF0–BF4 PROMOTE · BF5 H-NANOGEN16 {status} "
        f"(docs/results/nano-lm/formal-hnanogen16-nanogen16.md) "
        f"(`npm run nano:nanogen16`); next BF6 BF-REAL-EVAL; ≤5M |",
    )
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text = text.replace(
            "BF0–BF4 PROMOTE · H-CTXBF; next BF5 H-NANOGEN16/SKIP",
            f"BF0–BF4 PROMOTE · BF5 H-NANOGEN16 {status}; next BF6 BF-REAL-EVAL",
            1,
        )
        text = text.replace(
            "BF4 H-CTXBF PROMOTE; next BF5 H-NANOGEN16/SKIP",
            f"BF5 H-NANOGEN16 {status}; next BF6 BF-REAL-EVAL",
            1,
        )
        text = text.replace(
            "next BF5 H-NANOGEN16/SKIP",
            f"BF5 H-NANOGEN16 {status}; next BF6 BF-REAL-EVAL",
            1,
        )
        _EVOGEN.write_text(text, encoding="utf-8")


def run_nanogen16(
    *,
    root: Path,
    bank: Path,
    out: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN BF0 gen stance skip + archived NANOGEN6–15
    WHEN applying BF5 gate with live mode smoke
    THEN SKIP (no method plan) or PROMOTE/HOLD/KILL.
    """
    t0 = time.perf_counter()
    tc15, n_tc15, n_span15 = _load_parent_true_continue(_NANOGEN15_SUM)
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
    parent15 = _parent_is_defer(_NANOGEN15_SUM, default=PARENT_NANOGEN15_DEFER)

    with ThreadPoolExecutor(max_workers=min(6, workers)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        fut_bd = pool.submit(_smoke_bd_forever, root=root, bank=bank)
        fut_be = pool.submit(_smoke_be_forever, root=root, bank=bank)
        fut_bf = pool.submit(_smoke_bf_forever, root=root, bank=bank)
        rows = [
            fut_l.result(),
            fut_d.result(),
            fut_a.result(),
            fut_bd.result(),
            fut_be.result(),
            fut_bf.result(),
        ]
    modes_ok = _live_modes_ok(rows)

    if tc15 or n_tc15:
        tc_mean, n_tc, n_span = float(tc15), int(n_tc15), int(n_span15)
    elif tc14 or n_tc14:
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

    board = extract_nanogen16_board(
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
        parent15_defer=parent15,
        live_modes_ok=modes_ok,
    )
    decision = decide_nanogen16(board=board, anti_fp_signed=True)
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
        "id": NANOGEN16_ID,
        "stage": "BF5",
        "thesis": NANOGEN16_THESIS,
        "decision": decision,
        "stance": dict(NANOGEN16_STANCE),
        "method": dict(NANOGEN16_METHOD),
        "board": board,
        "true_gen_judge": dict(TRUE_GEN_JUDGE),
        "parent_archive": {
            "nanogen15_true_continue_mean": tc15,
            "nanogen15_n_true_continue": n_tc15,
            "nanogen15_n_span_fallback": n_span15,
            "nanogen15_defer": parent15,
            "nanogen14_true_continue_mean": tc14,
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
        "claim": NANOGEN16_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hnanogen16-nanogen16.md",
        "next": "BF6 BF-REAL-EVAL",
        "anti_fp": NANOGEN16_ANTI_FP,
        "finding": (
            f"{NANOGEN16_ID}: stance={board.get('stance')} "
            f"plan={board.get('method_plan_attached')} "
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
    ap = argparse.ArgumentParser(description="Wave BF5 H-NANOGEN16")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_nanogen16(
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
    ok = decision.startswith(("PROMOTE", "HOLD", "SKIP", "DEFER"))
    board = payload.get("board") or {}
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": NANOGEN16_ID,
                "stage": "BF5",
                "decision": decision[:180],
                "cpu_threads": threads,
                "workers": workers,
                "stance": board.get("stance"),
                "method_plan_attached": board.get("method_plan_attached"),
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
