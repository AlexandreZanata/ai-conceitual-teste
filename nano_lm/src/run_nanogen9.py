"""Wave AY3 H-NANOGEN9 runner — gen-defer; not NANOGEN8 rename."""

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
from nanogen9_ops import (
    NANOGEN9_ANTI_FP,
    NANOGEN9_CLAIM,
    NANOGEN9_ID,
    NANOGEN9_METHOD,
    NANOGEN9_SAFE_NOTE,
    NANOGEN9_STANCE,
    NANOGEN9_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen9,
    extract_nanogen9_board,
)
from prodhard_ops import KNOWN_ASK
from run_z_ask import ask_once
from shipay_ops import attach_shipay
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ay/nanogen9_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen9-nanogen9.md"
_NANOGEN8_SUM = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_NANOGEN7_SUM = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_NANOGEN6_SUM = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_LOCAL_SESSION = REPO / ".local/wave-ay/SESSION.md"
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
_EMPTY_BANK = REPO / "results/nano-lm/wave-ay/_decode_empty_bank.jsonl"
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
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _load_parent_true_continue(path: Path) -> tuple[float, int, int]:
    if not path.is_file():
        return 0.0, 0, 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0.0, 0, 0
    stats = data.get("stats") if isinstance(data, dict) else None
    if not isinstance(stats, dict):
        board = data.get("board") if isinstance(data, dict) else None
        if isinstance(board, dict):
            return (
                float(board.get("true_continue_mean") or 0.0),
                int(board.get("n_true_continue") or 0),
                int(board.get("n_span_fallback") or 0),
            )
        stats = data if isinstance(data, dict) else {}
    mean = float(stats.get("gen_mean") or stats.get("true_continue_mean") or 0.0)
    n_tc = int(stats.get("n_true_continue") or 0)
    n_span = int(stats.get("n_span_fallback") or 0)
    return mean, n_tc, n_span


def _parent8_is_defer(path: Path) -> bool:
    if not path.is_file():
        return PARENT_NANOGEN8_DEFER
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return PARENT_NANOGEN8_DEFER
    decision = str(data.get("decision") or "")
    return decision.startswith("DEFER") or PARENT_NANOGEN8_DEFER


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
    row = attach_shipay(dict(payload))
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
    row = attach_shipay(dict(payload))
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
    row = attach_shipay(dict(payload))
    row["arm"] = "ABSTAIN"
    return row


def _live_modes_ok(rows: list[dict[str, Any]]) -> bool:
    modes = {str(r.get("product_mode") or "") for r in rows}
    if "LOOKUP" not in modes:
        return False
    if "ABSTAIN" not in modes:
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
    lines = [
        f"# H-NANOGEN9 — gen-defer gate (**DONE** — {status})",
        "",
        "> Lab: `.local/pesquisa.md` §5 AY3 · Session: `.local/wave-ay/SESSION.md`  ",
        "> Parent: [formal-hnanogen8-nanogen8.md](formal-hnanogen8-nanogen8.md) "
        "(**DEFER**) · [formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md) "
        "· [formal-hnanogen6-nanogen6.md](formal-hnanogen6-nanogen6.md) · "
        "AY0 stance **defer**  ",
        "> Module: `nano_lm/src/nanogen9_ops.py` · Runner: `npm run nano:nanogen9`",
        "",
        "## Hypothesis",
        "",
        NANOGEN9_THESIS,
        "",
        "## Gate",
        "",
        "| Metric | Result | Pass bar |",
        "|--------|-------:|----------|",
        f"| Stance | **{board.get('stance')}** | AY0 freeze |",
        f"| CAPCHECK | **{board.get('capcheck')}** | closed |",
        f"| real_new_method | **{board.get('real_new_method')}** | True for PROMOTE |",
        f"| method | **{board.get('method_id')}** / {board.get('method_kind')} | not NANOGEN8 rename |",
        f"| is_rename | **{board.get('is_rename')}** | False |",
        f"| true_continue_mean (archive) | **{board.get('true_continue_mean')}** | ≥5.5 + method |",
        f"| n_true_continue | **{board.get('n_true_continue')}** | >0 for PROMOTE |",
        f"| n_span_fallback (archive) | **{board.get('n_span_fallback')}** | ≠ gen credit |",
        f"| parent NANOGEN6 / 7 | **{PARENT_NANOGEN6_TRUE_CONTINUE}** / "
        f"**{PARENT_NANOGEN7_TRUE_CONTINUE}** | HOLD stand |",
        f"| parent NANOGEN8 DEFER | **{board.get('parent_nanogen8_defer')}** | True |",
        f"| live_modes_ok | **{board.get('live_modes_ok')}** | LOOKUP+ABSTAIN labeled |",
        f"| Decision | **{status}** | — |",
        "",
        "## Live product smoke (modes still honest)",
        "",
        "| Arm | product_mode | modeui |",
        "|-----|--------------|--------|",
    ]
    for row in rows:
        mode = row.get("product_mode")
        line = str(row.get("modeui_line") or "")[:80]
        lines.append(f"| {row.get('arm')} | **{mode}** | `{line}` |")
    lines.extend(
        [
            "",
            "## Finding",
            "",
            "1. AY0 froze gen stance as **defer**; CAPCHECK **closed**.  ",
            "2. No real new train/data/arch method claimed — "
            "**not** NANOGEN8 rename theater.  ",
            "3. NANOGEN6·7 HOLD · NANOGEN8 DEFER stand "
            "(span-fallback ≠ gen).  ",
            "4. Live smoke keeps LOOKUP/ABSTAIN labeled on SHIPAY path.  ",
            f"5. Decision **{status}** — generative / mini-AGI claim stays locked.  ",
            f"6. Wall ~{wall_s:.1f}s · threads={threads} · workers={workers}.  ",
            "7. Next: **AY4 AY-REAL-EVAL** (product pass; gen claim only if "
            "AY3 PROMOTE — here deferred).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen9",
            "npm run nano:nanogen8",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ay/nanogen9_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen9.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest DEFER/HOLD under AY0 stance | NANOGEN9 = NANOGEN8+rename |",
            "| Cite NANOGEN6·7 HOLD · NANOGEN8 DEFER | Vanity gen unlock / LOOKUP-as-IQ |",
            "| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |",
            "",
            f"SAFE note: {NANOGEN9_SAFE_NOTE}  ",
            f"Anti-FP: {NANOGEN9_ANTI_FP}  ",
            f"Ship lock: {NANOGEN9_CLAIM}",
            "",
            "Next: **AY4 AY-REAL-EVAL** (`npm run nano:ay:real-eval`).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text("\n".join(lines), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    body = (
        f"# Wave AY session checklist (**OPEN** · AY3 DONE — {status})\n"
        "\n"
        "> Private under `.local/`. Lab: `.local/pesquisa.md` "
        "(Wave AY **OPEN** · intent harden + gen defer).  \n"
        f"> Ship lock: **{NANOGEN9_CLAIM}** · ≤5M.\n"
        "\n"
        "## Current stage\n"
        "\n"
        f"**AY3 — H-NANOGEN9 (DONE — {status})** · Next: **AY4 AY-REAL-EVAL**\n"
        "\n"
        "| Field | Value |\n"
        "|-------|--------|\n"
        "| Wave | **AY OPEN** |\n"
        f"| Decision | **{decision}** |\n"
        "| Stance | **defer** (AY0 freeze) |\n"
        "| CAPCHECK | **closed** |\n"
        "| true_continue | **unmet** (NANOGEN6·7 HOLD · NANOGEN8 DEFER stand) |\n"
        "\n"
        "## Stage board\n"
        "\n"
        "| Stage | ID | Status |\n"
        "|------:|----|--------|\n"
        "| AY0 | SESSION | **DONE — PROMOTE** |\n"
        "| AY1 | H-PRODINT | **DONE — PROMOTE** |\n"
        "| AY2 | H-SHIPAY | **DONE — PROMOTE** |\n"
        f"| AY3 | H-NANOGEN9 | **DONE — {status}** |\n"
        "| AY4 | AY-REAL-EVAL | **NEXT** |\n"
        "| AY5 | AY-REPORT | pending |\n"
        "| AY6 | AY-FREEZE | pending |\n"
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"\| AY3 \| \*\*H-NANOGEN9\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AY3 | **H-NANOGEN9** | **North-star generative** — real new "
            "method / hybrid under named CAPCHECK; else HOLD/DEFER "
            "(stance **defer** at AY0) | "
            f"true_continue → PROMOTE else HOLD/DEFER | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2b. **AY2 H-SHIPAY** — **DONE PROMOTE** (`npm run nano:shipay`) · "
            "next **AY3 H-NANOGEN9**.  "
        ),
        (
            "2b. **AY2 H-SHIPAY** — **DONE PROMOTE** (`npm run nano:shipay`).  \n"
            f"2c. **AY3 H-NANOGEN9** — **DONE {status}** "
            "(`npm run nano:nanogen9`) · next **AY4 AY-REAL-EVAL**.  "
        ),
        1,
    )
    text = text.replace(
        (
            "3. **AY2 H-SHIPAY** — **DONE PROMOTE** (`npm run nano:shipay`) · "
            "modes+content · intent ABSTAIN labeled.  \n"
            "4. **AY3 generative** — only with a **real new** train/data/arch "
            "method (or named hybrid); else **HOLD/DEFER**. North star stays: "
            "nano generative / mini-AGI-inspired ≤5M.  "
        ),
        (
            "3. **AY2 H-SHIPAY** — **DONE PROMOTE** (`npm run nano:shipay`) · "
            "modes+content · intent ABSTAIN labeled.  \n"
            f"4. **AY3 H-NANOGEN9** — **DONE {status}** "
            "(`npm run nano:nanogen9`) · gen stance defer · not NANOGEN8 rename.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ay/SESSION.md` "
        "(AY2 H-SHIPAY **DONE — PROMOTE**; next AY3 H-NANOGEN9).  ",
        "> **Session:** `.local/wave-ay/SESSION.md` "
        f"(AY3 H-NANOGEN9 **DONE — {status}**; next AY4 AY-REAL-EVAL).  ",
        1,
    )
    if "# next: nano:nanogen9" in text:
        text = text.replace(
            "# next: nano:nanogen9 (defer unless real method)",
            "npm run nano:nanogen9\n# next: nano:ay:real-eval",
            1,
        )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2b. **AY2 H-SHIPAY** — **DONE PROMOTE** (`npm run nano:shipay`) · "
            "next **AY3 H-NANOGEN9**.  "
        )
        new = (
            "2b. **AY2 H-SHIPAY** — **DONE PROMOTE** (`npm run nano:shipay`).  \n"
            f"2c. **AY3 H-NANOGEN9** — **DONE {status}** "
            "(`npm run nano:nanogen9`) · next **AY4 AY-REAL-EVAL**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ay/SESSION.md` (AY2 H-SHIPAY **DONE — PROMOTE**; "
            "next AY3 H-NANOGEN9)."
        )
        new = (
            f"Session: `wave-ay/SESSION.md` (AY3 H-NANOGEN9 **DONE — {status}**; "
            "next AY4 AY-REAL-EVAL)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _insert_nanogen9_frag(text: str, prefix: str, status: str) -> str:
    if f"H-NANOGEN9 {status}" in text:
        return text
    frag = (
        f"AY3 [H-NANOGEN9 {status}](formal-hnanogen9-nanogen9.md) "
        f"(`npm run nano:nanogen9`) — gen stance defer · CAPCHECK closed · "
        "not NANOGEN8 rename"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*H-SHIPAY PROMOTE[^\n]*?)"
        r"(; next AY3 H-NANOGEN9|; next AY3)",
        rf"\1 · {frag}; next AY4 AY-REAL-EVAL",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if f"H-NANOGEN9 {status}" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AY ACTIVE\*\* —[^\n]*H-SHIPAY PROMOTE[^\n]*?)"
        r"(; next AY3 H-NANOGEN9|; next AY3)",
        rf"\1 · AY3 [H-NANOGEN9 {status}]"
        r"(docs/results/nano-lm/formal-hnanogen9-nanogen9.md) "
        r"(`npm run nano:nanogen9`); next AY4 AY-REAL-EVAL",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ay_tail = text.split("| **AY** |", 1)[-1][:700]
    if f"H-NANOGEN9 {status}" in ay_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AY\*\* \| \*\*ACTIVE\*\* \|[^\n]*H-SHIPAY "
        r"PROMOTE[^\n]*?)(; next AY3 H-NANOGEN9|; next AY3)",
        rf"\1 · AY3 [H-NANOGEN9 {status}]"
        r"(results/nano-lm/formal-hnanogen9-nanogen9.md); "
        r"next AY4 AY-REAL-EVAL",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "formal-hnanogen9-nanogen9.md" in text:
        return
    needle = "Wave AY2: `formal-hshipay-shipay.md` PROMOTE · Wave AX0:"
    repl = (
        "Wave AY2: `formal-hshipay-shipay.md` PROMOTE · "
        f"Wave AY3: `formal-hnanogen9-nanogen9.md` {status} · Wave AX0:"
    )
    if needle in text:
        _EVOGEN.write_text(text.replace(needle, repl, 1), encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    for path, prefix in (
        (_RECIPES, "**Wave AY ACTIVE:**"),
        (_CARD, "**Wave AY ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_nanogen9_frag(text, prefix, status)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    if _RECIPES.is_file():
        text = _RECIPES.read_text(encoding="utf-8")
        if "Wave AY3 H-NANOGEN9" not in text:
            needle = (
                "| Wave AY2 H-SHIPAY | [formal-hshipay-shipay.md]"
                "(formal-hshipay-shipay.md) **PROMOTE** (`npm run nano:shipay`) "
                "— modes+content · hard-natural LOOKUP · intent-FP ABSTAIN · "
                "no unlabeled |\n"
            )
            row = (
                f"| Wave AY3 H-NANOGEN9 | [formal-hnanogen9-nanogen9.md]"
                f"(formal-hnanogen9-nanogen9.md) **{status}** "
                f"(`npm run nano:nanogen9`) — gen stance defer · CAPCHECK "
                "closed · not NANOGEN8 rename · true_continue unmet |\n"
            )
            if needle in text:
                _RECIPES.write_text(
                    text.replace(needle, needle + row, 1), encoding="utf-8"
                )
    _patch_agents(status)
    _patch_agenda(status)
    _patch_evogen(status)


def run_nanogen9(
    *,
    root: Path,
    bank: Path,
    out: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN AY0 gen stance defer + archived NANOGEN6·7 HOLD · NANOGEN8 DEFER
    WHEN applying AY3 north-star gate with live product smoke
    THEN DEFER (no real method / not NANOGEN8 rename) or PROMOTE/HOLD/KILL.
    """
    t0 = time.perf_counter()
    tc8, n_tc8, n_span8 = _load_parent_true_continue(_NANOGEN8_SUM)
    tc7, _, _ = _load_parent_true_continue(_NANOGEN7_SUM)
    tc6, _, _ = _load_parent_true_continue(_NANOGEN6_SUM)
    parent8_defer = _parent8_is_defer(_NANOGEN8_SUM)
    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        rows = [fut_l.result(), fut_d.result(), fut_a.result()]
    modes_ok = _live_modes_ok(rows)
    # Honest archive: NANOGEN8 board true_continue (not a new rename run).
    board = extract_nanogen9_board(
        true_continue_mean=float(tc8),
        n_true_continue=int(n_tc8),
        n_span_fallback=int(n_span8),
        parent6=float(tc6) if tc6 else PARENT_NANOGEN6_TRUE_CONTINUE,
        parent7=float(tc7) if tc7 else PARENT_NANOGEN7_TRUE_CONTINUE,
        parent8_defer=parent8_defer,
        live_modes_ok=modes_ok,
    )
    decision = decide_nanogen9(board=board, anti_fp_signed=True)
    wall_s = time.perf_counter() - t0
    _write_public(
        decision=decision,
        board=board,
        rows=rows,
        wall_s=wall_s,
        threads=threads,
        workers=workers,
    )
    _update_local_session(decision)
    _patch_pesquisa(decision)
    _patch_local_helpers(decision)
    _patch_public_status(decision)
    payload = {
        "id": NANOGEN9_ID,
        "thesis": NANOGEN9_THESIS,
        "decision": decision,
        "stance": dict(NANOGEN9_STANCE),
        "method": dict(NANOGEN9_METHOD),
        "board": board,
        "true_gen_judge": dict(TRUE_GEN_JUDGE),
        "parent_archive": {
            "nanogen8_true_continue_mean": tc8,
            "nanogen8_n_true_continue": n_tc8,
            "nanogen8_n_span_fallback": n_span8,
            "nanogen8_defer": parent8_defer,
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
        "claim": NANOGEN9_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hnanogen9-nanogen9.md",
        "next": "AY4 AY-REAL-EVAL",
        "anti_fp": NANOGEN9_ANTI_FP,
        "finding": (
            f"{NANOGEN9_ID}: stance={board.get('stance')} "
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
    ap = argparse.ArgumentParser(description="Wave AY3 H-NANOGEN9")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_nanogen9(
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
                "hyp_id": NANOGEN9_ID,
                "decision": decision[:160],
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
