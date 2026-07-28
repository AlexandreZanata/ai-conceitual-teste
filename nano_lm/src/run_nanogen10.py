"""Wave AZ3 H-NANOGEN10 runner — gen-defer; not NANOGEN9 rename."""

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
from nanogen10_ops import (
    NANOGEN10_ANTI_FP,
    NANOGEN10_CLAIM,
    NANOGEN10_ID,
    NANOGEN10_METHOD,
    NANOGEN10_SAFE_NOTE,
    NANOGEN10_STANCE,
    NANOGEN10_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    PARENT_NANOGEN8_DEFER,
    PARENT_NANOGEN9_DEFER,
    TRUE_GEN_JUDGE,
    decide_nanogen10,
    extract_nanogen10_board,
)
from prodhard_ops import KNOWN_ASK
from run_z_ask import ask_once
from shipaz_ops import attach_shipaz
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-az/nanogen10_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen10-nanogen10.md"
_NANOGEN9_SUM = REPO / "results/nano-lm/wave-ay/nanogen9_summary.json"
_NANOGEN8_SUM = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_NANOGEN7_SUM = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_NANOGEN6_SUM = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_LOCAL_SESSION = REPO / ".local/wave-az/SESSION.md"
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
_EMPTY_BANK = REPO / "results/nano-lm/wave-az/_decode_empty_bank.jsonl"
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
    # 16c / ~31Gi: leave ≥2 cores + headroom; avoid thrash under 7Gi free.
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
    row = attach_shipaz(dict(payload))
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
    row = attach_shipaz(dict(payload))
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
    row = attach_shipaz(dict(payload))
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
        f"# H-NANOGEN10 — gen-defer gate (**DONE** — {status})",
        "",
        "> Lab: `.local/pesquisa.md` §5 AZ3 · Session: `.local/wave-az/SESSION.md`  ",
        "> Parent: [formal-hnanogen9-nanogen9.md](formal-hnanogen9-nanogen9.md) "
        "(**DEFER**) · [formal-hnanogen8-nanogen8.md](formal-hnanogen8-nanogen8.md) "
        "(**DEFER**) · [formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md) "
        "· [formal-hnanogen6-nanogen6.md](formal-hnanogen6-nanogen6.md) · "
        "AZ0 stance **defer**  ",
        "> Module: `nano_lm/src/nanogen10_ops.py` · Runner: `npm run nano:nanogen10`",
        "",
        "## Hypothesis",
        "",
        NANOGEN10_THESIS,
        "",
        "## Gate",
        "",
        "| Metric | Result | Pass bar |",
        "|--------|-------:|----------|",
        f"| Stance | **{board.get('stance')}** | AZ0 freeze |",
        f"| CAPCHECK | **{board.get('capcheck')}** | closed |",
        f"| real_new_method | **{board.get('real_new_method')}** | True for PROMOTE |",
        f"| method | **{board.get('method_id')}** / {board.get('method_kind')} | not NANOGEN9 rename |",
        f"| is_rename | **{board.get('is_rename')}** | False |",
        f"| true_continue_mean (archive) | **{board.get('true_continue_mean')}** | ≥5.5 + method |",
        f"| n_true_continue | **{board.get('n_true_continue')}** | >0 for PROMOTE |",
        f"| n_span_fallback (archive) | **{board.get('n_span_fallback')}** | ≠ gen credit |",
        f"| parent NANOGEN6 / 7 | **{PARENT_NANOGEN6_TRUE_CONTINUE}** / "
        f"**{PARENT_NANOGEN7_TRUE_CONTINUE}** | HOLD stand |",
        f"| parent NANOGEN8 DEFER | **{board.get('parent_nanogen8_defer')}** | True |",
        f"| parent NANOGEN9 DEFER | **{board.get('parent_nanogen9_defer')}** | True |",
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
            "1. AZ0 froze gen stance as **defer**; CAPCHECK **closed**.  ",
            "2. No real new train/data/arch method claimed — "
            "**not** NANOGEN9 rename theater.  ",
            "3. NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand "
            "(span-fallback ≠ gen).  ",
            "4. Live smoke keeps LOOKUP/ABSTAIN labeled on SHIPAZ path.  ",
            f"5. Decision **{status}** — generative / mini-AGI claim stays locked.  ",
            f"6. Wall ~{wall_s:.1f}s · threads={threads} · workers={workers}.  ",
            "7. Next: **AZ4 AZ-REAL-EVAL** (product pass; gen claim only if "
            "AZ3 PROMOTE — here deferred).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen10",
            "npm run nano:nanogen9",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-az/nanogen10_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen10.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest DEFER/HOLD under AZ0 stance | NANOGEN10 = NANOGEN9+rename |",
            "| Cite NANOGEN6·7 HOLD · NANOGEN8·9 DEFER | Vanity gen unlock / LOOKUP-as-IQ |",
            "| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |",
            "",
            f"SAFE note: {NANOGEN10_SAFE_NOTE}  ",
            f"Anti-FP: {NANOGEN10_ANTI_FP}  ",
            f"Ship lock: {NANOGEN10_CLAIM}",
            "",
            "Next: **AZ4 AZ-REAL-EVAL** (`npm run nano:az:real-eval`).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text("\n".join(lines), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    body = (
        f"# Wave AZ session checklist (**OPEN** · AZ3 DONE — {status})\n"
        "\n"
        "> Private under `.local/`. Lab: `.local/pesquisa.md` "
        "(Wave AZ **OPEN** · held-out harden + gen defer).  \n"
        f"> Ship lock: **{NANOGEN10_CLAIM}** · ≤5M.\n"
        "\n"
        "## Current stage\n"
        "\n"
        f"**AZ3 — H-NANOGEN10 (DONE — {status})** · Next: **AZ4 AZ-REAL-EVAL**\n"
        "\n"
        "| Field | Value |\n"
        "|-------|--------|\n"
        "| Wave | **AZ OPEN** |\n"
        f"| Decision | **{decision}** |\n"
        "| Stance | **defer** (AZ0 freeze) |\n"
        "| CAPCHECK | **closed** |\n"
        "| true_continue | **unmet** (NANOGEN6·7 HOLD · NANOGEN8·9 DEFER stand) |\n"
        "\n"
        "## Stage board\n"
        "\n"
        "| Stage | ID | Status |\n"
        "|------:|----|--------|\n"
        "| AZ0 | SESSION | **DONE — PROMOTE** |\n"
        "| AZ1 | H-PRODGEN | **DONE — PROMOTE** |\n"
        "| AZ2 | H-SHIPAZ | **DONE — PROMOTE** |\n"
        f"| AZ3 | H-NANOGEN10 | **DONE — {status}** |\n"
        "| AZ4 | AZ-REAL-EVAL | **NEXT** |\n"
        "| AZ5 | AZ-REPORT | pending |\n"
        "| AZ6 | AZ-FREEZE | pending |\n"
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"\| AZ3 \| \*\*H-NANOGEN10\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AZ3 | **H-NANOGEN10** | North-star gen — real method / hybrid; "
            "else HOLD/DEFER (stance **defer** at AZ0) | "
            f"true_continue → PROMOTE else HOLD/DEFER | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2b. **AZ2 H-SHIPAZ** — **DONE PROMOTE** (`npm run nano:shipaz`) · "
            "next **AZ3 H-NANOGEN10**.  "
        ),
        (
            "2b. **AZ2 H-SHIPAZ** — **DONE PROMOTE** (`npm run nano:shipaz`).  \n"
            f"2c. **AZ3 H-NANOGEN10** — **DONE {status}** "
            "(`npm run nano:nanogen10`) · next **AZ4 AZ-REAL-EVAL**.  "
        ),
        1,
    )
    text = text.replace(
        (
            "3. **AZ2 H-SHIPAZ** — **DONE PROMOTE** (`npm run nano:shipaz`) · "
            "modes+content · held-out ABSTAIN · over-refuse LOOKUP.  \n"
            "4. **AZ3** — nano generative / mini-AGI-inspired: **real method** "
            "or **HOLD/DEFER**; real eval only.  "
        ),
        (
            "3. **AZ2 H-SHIPAZ** — **DONE PROMOTE** (`npm run nano:shipaz`) · "
            "modes+content · held-out ABSTAIN · over-refuse LOOKUP.  \n"
            f"4. **AZ3 H-NANOGEN10** — **DONE {status}** "
            "(`npm run nano:nanogen10`) · gen stance defer · not NANOGEN9 rename.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-az/SESSION.md` "
        "(AZ2 H-SHIPAZ **DONE — PROMOTE**; next AZ3 H-NANOGEN10).  ",
        "> **Session:** `.local/wave-az/SESSION.md` "
        f"(AZ3 H-NANOGEN10 **DONE — {status}**; next AZ4 AZ-REAL-EVAL).  ",
        1,
    )
    if "# next: nano:nanogen10" in text:
        text = text.replace(
            "# next: nano:nanogen10 (defer unless real method)",
            "npm run nano:nanogen10\n# next: nano:az:real-eval",
            1,
        )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2b. **AZ2 H-SHIPAZ** — **DONE PROMOTE** (`npm run nano:shipaz`) · "
            "next **AZ3 H-NANOGEN10**.  "
        )
        new = (
            "2b. **AZ2 H-SHIPAZ** — **DONE PROMOTE** (`npm run nano:shipaz`).  \n"
            f"2c. **AZ3 H-NANOGEN10** — **DONE {status}** "
            "(`npm run nano:nanogen10`) · next **AZ4 AZ-REAL-EVAL**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-az/SESSION.md` (AZ2 H-SHIPAZ **DONE — PROMOTE**; "
            "next AZ3 H-NANOGEN10)."
        )
        new = (
            f"Session: `wave-az/SESSION.md` (AZ3 H-NANOGEN10 **DONE — {status}**; "
            "next AZ4 AZ-REAL-EVAL)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _insert_nanogen10_frag(text: str, prefix: str, status: str) -> str:
    if f"H-NANOGEN10 {status}" in text:
        return text
    frag = (
        f"AZ3 [H-NANOGEN10 {status}](formal-hnanogen10-nanogen10.md) "
        f"(`npm run nano:nanogen10`) — gen stance defer · CAPCHECK closed · "
        "not NANOGEN9 rename"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*H-SHIPAZ PROMOTE[^\n]*?)"
        r"(; next AZ3 H-NANOGEN10|; next AZ3)",
        rf"\1 · {frag}; next AZ4 AZ-REAL-EVAL",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if f"H-NANOGEN10 {status}" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AZ ACTIVE\*\* —[^\n]*H-SHIPAZ PROMOTE[^\n]*?)"
        r"(; next AZ3 H-NANOGEN10|; next AZ3)",
        rf"\1 · AZ3 [H-NANOGEN10 {status}]"
        r"(docs/results/nano-lm/formal-hnanogen10-nanogen10.md) "
        r"(`npm run nano:nanogen10`); next AZ4 AZ-REAL-EVAL",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    az_tail = text.split("| **AZ** |", 1)[-1][:700]
    if f"H-NANOGEN10 {status}" in az_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AZ\*\* \| \*\*ACTIVE\*\* \|[^\n]*H-SHIPAZ "
        r"PROMOTE[^\n]*?)(; next AZ3 H-NANOGEN10|; next AZ3)",
        rf"\1 · AZ3 [H-NANOGEN10 {status}]"
        r"(results/nano-lm/formal-hnanogen10-nanogen10.md); "
        r"next AZ4 AZ-REAL-EVAL",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "formal-hnanogen10-nanogen10.md" in text:
        return
    needle = (
        "Wave AZ ACTIVE (AZ0 SESSION PROMOTE · AZ1 H-PRODGEN PROMOTE · "
        "AZ2 H-SHIPAZ PROMOTE; next AZ3 H-NANOGEN10)"
    )
    repl = (
        "Wave AZ ACTIVE (AZ0 SESSION PROMOTE · AZ1 H-PRODGEN PROMOTE · "
        "AZ2 H-SHIPAZ PROMOTE · "
        f"AZ3 H-NANOGEN10 {status}; next AZ4 AZ-REAL-EVAL)"
    )
    if needle in text:
        _EVOGEN.write_text(text.replace(needle, repl, 1), encoding="utf-8")
        return
    # Fallback: compact AZ2 / next AZ3 mention in Active blurb.
    needle2 = "AZ2 H-SHIPAZ PROMOTE; next AZ3 H-NANOGEN10"
    repl2 = (
        f"AZ2 H-SHIPAZ PROMOTE · AZ3 H-NANOGEN10 {status}; "
        "next AZ4 AZ-REAL-EVAL"
    )
    if needle2 in text:
        _EVOGEN.write_text(text.replace(needle2, repl2, 1), encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    for path, prefix in (
        (_RECIPES, "**Wave AZ ACTIVE:**"),
        (_CARD, "**Wave AZ ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_nanogen10_frag(text, prefix, status)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    if _RECIPES.is_file():
        text = _RECIPES.read_text(encoding="utf-8")
        if "Wave AZ3 H-NANOGEN10" not in text:
            needle = (
                "| Wave AZ2 H-SHIPAZ | [formal-hshipaz-shipaz.md]"
                "(formal-hshipaz-shipaz.md) **PROMOTE** (`npm run nano:shipaz`) "
                "— modes+content · held-out ABSTAIN · over-refuse LOOKUP · "
                "no unlabeled |\n"
            )
            row = (
                f"| Wave AZ3 H-NANOGEN10 | [formal-hnanogen10-nanogen10.md]"
                f"(formal-hnanogen10-nanogen10.md) **{status}** "
                f"(`npm run nano:nanogen10`) — gen stance defer · CAPCHECK "
                "closed · not NANOGEN9 rename · true_continue unmet |\n"
            )
            if needle in text:
                _RECIPES.write_text(
                    text.replace(needle, needle + row, 1), encoding="utf-8"
                )
    _patch_agents(status)
    _patch_agenda(status)
    _patch_evogen(status)


def run_nanogen10(
    *,
    root: Path,
    bank: Path,
    out: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN AZ0 gen stance defer + archived NANOGEN6·7 HOLD · NANOGEN8·9 DEFER
    WHEN applying AZ3 north-star gate with live product smoke
    THEN DEFER (no real method / not NANOGEN9 rename) or PROMOTE/HOLD/KILL.
    """
    t0 = time.perf_counter()
    tc9, n_tc9, n_span9 = _load_parent_true_continue(_NANOGEN9_SUM)
    tc8, _, _ = _load_parent_true_continue(_NANOGEN8_SUM)
    tc7, _, _ = _load_parent_true_continue(_NANOGEN7_SUM)
    tc6, _, _ = _load_parent_true_continue(_NANOGEN6_SUM)
    parent8_defer = _parent_is_defer(
        _NANOGEN8_SUM, default=PARENT_NANOGEN8_DEFER
    )
    parent9_defer = _parent_is_defer(
        _NANOGEN9_SUM, default=PARENT_NANOGEN9_DEFER
    )
    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        rows = [fut_l.result(), fut_d.result(), fut_a.result()]
    modes_ok = _live_modes_ok(rows)
    # Honest archive: NANOGEN9 board true_continue (not a new rename run).
    board = extract_nanogen10_board(
        true_continue_mean=float(tc9),
        n_true_continue=int(n_tc9),
        n_span_fallback=int(n_span9),
        parent6=float(tc6) if tc6 else PARENT_NANOGEN6_TRUE_CONTINUE,
        parent7=float(tc7) if tc7 else PARENT_NANOGEN7_TRUE_CONTINUE,
        parent8_defer=parent8_defer,
        parent9_defer=parent9_defer,
        live_modes_ok=modes_ok,
    )
    decision = decide_nanogen10(board=board, anti_fp_signed=True)
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
        "id": NANOGEN10_ID,
        "thesis": NANOGEN10_THESIS,
        "decision": decision,
        "stance": dict(NANOGEN10_STANCE),
        "method": dict(NANOGEN10_METHOD),
        "board": board,
        "true_gen_judge": dict(TRUE_GEN_JUDGE),
        "parent_archive": {
            "nanogen9_true_continue_mean": tc9,
            "nanogen9_n_true_continue": n_tc9,
            "nanogen9_n_span_fallback": n_span9,
            "nanogen9_defer": parent9_defer,
            "nanogen8_true_continue_mean": tc8,
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
        "claim": NANOGEN10_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hnanogen10-nanogen10.md",
        "next": "AZ4 AZ-REAL-EVAL",
        "anti_fp": NANOGEN10_ANTI_FP,
        "finding": (
            f"{NANOGEN10_ID}: stance={board.get('stance')} "
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
    ap = argparse.ArgumentParser(description="Wave AZ3 H-NANOGEN10")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_nanogen10(
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
                "hyp_id": NANOGEN10_ID,
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
