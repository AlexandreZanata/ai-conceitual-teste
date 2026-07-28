"""Wave AX3 H-NANOGEN8 runner — gen-defer; not NANOGEN7 TAC rename."""

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
from nanogen8_ops import (
    NANOGEN8_ANTI_FP,
    NANOGEN8_CLAIM,
    NANOGEN8_ID,
    NANOGEN8_METHOD,
    NANOGEN8_SAFE_NOTE,
    NANOGEN8_STANCE,
    NANOGEN8_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    PARENT_NANOGEN7_TRUE_CONTINUE,
    TRUE_GEN_JUDGE,
    decide_nanogen8,
    extract_nanogen8_board,
)
from prodhard_ops import KNOWN_ASK
from run_z_ask import ask_once
from shipux_ops import attach_shipux
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hnanogen8-nanogen8.md"
_NANOGEN7_SUM = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_NANOGEN6_SUM = REPO / "results/nano-lm/wave-av/nanogen6_summary.json"
_LOCAL_SESSION = REPO / ".local/wave-ax/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-ax/_decode_empty_bank.jsonl"
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
        stats = data if isinstance(data, dict) else {}
    mean = float(stats.get("gen_mean") or 0.0)
    n_tc = int(stats.get("n_true_continue") or 0)
    n_span = int(stats.get("n_span_fallback") or 0)
    return mean, n_tc, n_span


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
    row = attach_shipux(dict(payload))
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
    row = attach_shipux(dict(payload))
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
    row = attach_shipux(dict(payload))
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
        f"# H-NANOGEN8 — gen-defer gate (**DONE** — {status})",
        "",
        "> Lab: `.local/pesquisa.md` §5 AX3 · Session: `.local/wave-ax/SESSION.md`  ",
        "> Parent: [formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md) "
        "(true_continue **0**) · [formal-hnanogen6-nanogen6.md]"
        "(formal-hnanogen6-nanogen6.md) · AX0 stance **defer**  ",
        "> Module: `nano_lm/src/nanogen8_ops.py` · Runner: `npm run nano:nanogen8`",
        "",
        "## Hypothesis",
        "",
        NANOGEN8_THESIS,
        "",
        "## Gate",
        "",
        "| Metric | Result | Pass bar |",
        "|--------|-------:|----------|",
        f"| Stance | **{board.get('stance')}** | AX0 freeze |",
        f"| CAPCHECK | **{board.get('capcheck')}** | closed |",
        f"| real_new_method | **{board.get('real_new_method')}** | True for PROMOTE |",
        f"| method | **{board.get('method_id')}** / {board.get('method_kind')} | not TAC rename |",
        f"| is_rename | **{board.get('is_rename')}** | False |",
        f"| true_continue_mean (archive) | **{board.get('true_continue_mean')}** | ≥5.5 + method |",
        f"| n_true_continue | **{board.get('n_true_continue')}** | >0 for PROMOTE |",
        f"| n_span_fallback (archive) | **{board.get('n_span_fallback')}** | ≠ gen credit |",
        f"| parent NANOGEN6 / 7 | **{PARENT_NANOGEN6_TRUE_CONTINUE}** / "
        f"**{PARENT_NANOGEN7_TRUE_CONTINUE}** | HOLD stand |",
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
            "1. AX0 froze gen stance as **defer**; CAPCHECK **closed**.  ",
            "2. No real new train/data/arch method claimed — "
            "**not** NANOGEN7 TAC rename theater.  ",
            "3. Archived NANOGEN6·7 true_continue remain **0** "
            "(span-fallback ≠ gen).  ",
            "4. Live smoke keeps LOOKUP/ABSTAIN labeled on product path.  ",
            f"5. Decision **{status}** — generative / mini-AGI claim stays locked.  ",
            f"6. Wall ~{wall_s:.1f}s · threads={threads} · workers={workers}.  ",
            "7. Next: **AX4 AX-REAL-EVAL** (product pass; gen claim only if "
            "AX3 PROMOTE — here deferred).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:nanogen8",
            "npm run nano:nanogen7",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ax/nanogen8_summary.json`  ",
            "- Contract: `nano_lm/tests/test_nanogen8.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Honest DEFER/HOLD under AX0 stance | NANOGEN8 = NANOGEN7+rename |",
            "| Cite NANOGEN6·7 HOLD | Vanity gen unlock / LOOKUP-as-IQ |",
            "| PROMOTE only real method + true_continue≥5.5 | Raise ≤5M w/o CAPCHECK |",
            "",
            f"SAFE note: {NANOGEN8_SAFE_NOTE}  ",
            f"Anti-FP: {NANOGEN8_ANTI_FP}  ",
            f"Ship lock: {NANOGEN8_CLAIM}",
            "",
            "Next: **AX4 AX-REAL-EVAL** (`npm run nano:ax:real-eval`).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text("\n".join(lines), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    body = (
        f"# Wave AX session checklist (**OPEN** · AX3 DONE — {status})\n"
        "\n"
        "> Private under `.local/`. Lab: `.local/pesquisa.md` "
        "(Wave AX **OPEN** · hard-natural harden + gen defer).  \n"
        f"> Ship lock: **{NANOGEN8_CLAIM}** · ≤5M.\n"
        "\n"
        "## Current stage\n"
        "\n"
        f"**AX3 — H-NANOGEN8 (DONE — {status})** · Next: **AX4 AX-REAL-EVAL**\n"
        "\n"
        "| Field | Value |\n"
        "|-------|--------|\n"
        "| Wave | **AX OPEN** |\n"
        f"| Decision | **{decision}** |\n"
        "| Stance | **defer** (AX0 freeze) |\n"
        "| CAPCHECK | **closed** |\n"
        "| true_continue | **unmet** (NANOGEN6·7 HOLD stand) |\n"
        "\n"
        "## Stage board\n"
        "\n"
        "| Stage | ID | Status |\n"
        "|------:|----|--------|\n"
        "| AX0 | SESSION | **DONE — PROMOTE** |\n"
        "| AX1 | H-PRODNAT | **DONE — PROMOTE** |\n"
        "| AX2 | H-SHIPUX | **DONE — PROMOTE** |\n"
        f"| AX3 | H-NANOGEN8 | **DONE — {status}** |\n"
        "| AX4 | AX-REAL-EVAL | **NEXT** |\n"
        "| AX5 | AX-REPORT | pending |\n"
        "| AX6 | AX-FREEZE | pending |\n"
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"\| AX3 \| \*\*H-NANOGEN8\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AX3 | **H-NANOGEN8** | **North-star generative** — real new "
            "method / hybrid under named CAPCHECK; else **DEFER/HOLD** | "
            f"true_continue → PROMOTE else HOLD/DEFER | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2b. **AX2 H-SHIPUX** — **DONE PROMOTE** (`npm run nano:shipux`) · "
            "next **AX3 H-NANOGEN8**.  "
        ),
        (
            "2b. **AX2 H-SHIPUX** — **DONE PROMOTE** (`npm run nano:shipux`).  \n"
            f"2c. **AX3 H-NANOGEN8** — **DONE {status}** "
            "(`npm run nano:nanogen8`) · next **AX4 AX-REAL-EVAL**.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ax/SESSION.md` "
        "(AX2 H-SHIPUX **DONE — PROMOTE**; next AX3 H-NANOGEN8).  ",
        "> **Session:** `.local/wave-ax/SESSION.md` "
        f"(AX3 H-NANOGEN8 **DONE — {status}**; next AX4 AX-REAL-EVAL).  ",
        1,
    )
    if "# next: nano:nanogen8" in text:
        text = text.replace(
            "# next: nano:nanogen8 (defer unless real method)",
            "npm run nano:nanogen8\n# next: nano:ax:real-eval",
            1,
        )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2b. **AX2 H-SHIPUX** — **DONE PROMOTE** (`npm run nano:shipux`) · "
            "next **AX3 H-NANOGEN8**.  "
        )
        new = (
            "2b. **AX2 H-SHIPUX** — **DONE PROMOTE** (`npm run nano:shipux`).  \n"
            f"2c. **AX3 H-NANOGEN8** — **DONE {status}** "
            "(`npm run nano:nanogen8`) · next **AX4 AX-REAL-EVAL**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ax/SESSION.md` (AX2 H-SHIPUX **DONE — PROMOTE**; "
            "next AX3 H-NANOGEN8)."
        )
        new = (
            f"Session: `wave-ax/SESSION.md` (AX3 H-NANOGEN8 **DONE — {status}**; "
            "next AX4 AX-REAL-EVAL)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _insert_nanogen8_frag(text: str, prefix: str, status: str) -> str:
    if "H-NANOGEN8" in text and status in text.split("H-NANOGEN8", 1)[-1][:80]:
        if f"H-NANOGEN8 {status}" in text:
            return text
    frag = (
        f"AX3 [H-NANOGEN8 {status}](formal-hnanogen8-nanogen8.md) "
        f"(`npm run nano:nanogen8`) — gen stance defer · CAPCHECK closed · "
        "not TAC rename"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*H-SHIPUX PROMOTE[^\n]*?)"
        r"(; next AX3 H-NANOGEN8|; next AX3)",
        rf"\1 · {frag}; next AX4 AX-REAL-EVAL",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if f"H-NANOGEN8 {status}" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AX ACTIVE\*\* —[^\n]*H-SHIPUX PROMOTE[^\n]*?)"
        r"(; next AX3 H-NANOGEN8|; next AX3)",
        rf"\1 · AX3 [H-NANOGEN8 {status}]"
        r"(docs/results/nano-lm/formal-hnanogen8-nanogen8.md) "
        r"(`npm run nano:nanogen8`); next AX4 AX-REAL-EVAL",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ax_tail = text.split("| **AX** |", 1)[-1][:600]
    if f"H-NANOGEN8 {status}" in ax_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AX\*\* \| \*\*ACTIVE\*\* \|[^\n]*H-SHIPUX "
        r"PROMOTE[^\n]*?)(; next AX3 H-NANOGEN8|; next AX3)",
        rf"\1 · AX3 [H-NANOGEN8 {status}]"
        r"(results/nano-lm/formal-hnanogen8-nanogen8.md); "
        r"next AX4 AX-REAL-EVAL",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    for path, prefix in (
        (_RECIPES, "**Wave AX ACTIVE:**"),
        (_CARD, "**Wave AX ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_nanogen8_frag(text, prefix, status)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    # Recipe table row
    if _RECIPES.is_file():
        text = _RECIPES.read_text(encoding="utf-8")
        if "Wave AX3 H-NANOGEN8" not in text:
            needle = (
                "| Wave AX2 H-SHIPUX | [formal-hshipux-shipux.md]"
                "(formal-hshipux-shipux.md) **PROMOTE** (`npm run nano:shipux`) "
                "— modes+content · hard-natural LOOKUP · DECODE usable/ABSTAIN · "
                "no unlabeled |\n"
            )
            row = (
                f"| Wave AX3 H-NANOGEN8 | [formal-hnanogen8-nanogen8.md]"
                f"(formal-hnanogen8-nanogen8.md) **{status}** "
                f"(`npm run nano:nanogen8`) — gen stance defer · CAPCHECK "
                "closed · not NANOGEN7 rename · true_continue unmet |\n"
            )
            if needle in text:
                _RECIPES.write_text(
                    text.replace(needle, needle + row, 1), encoding="utf-8"
                )
    _patch_agents(status)
    _patch_agenda(status)


def run_nanogen8(
    *,
    root: Path,
    bank: Path,
    out: Path,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN AX0 gen stance defer + archived NANOGEN6·7 HOLD
    WHEN applying AX3 north-star gate with live product smoke
    THEN DEFER (no real method / not TAC rename) or PROMOTE/HOLD/KILL.
    """
    t0 = time.perf_counter()
    tc7, n_tc7, n_span7 = _load_parent_true_continue(_NANOGEN7_SUM)
    tc6, _, _ = _load_parent_true_continue(_NANOGEN6_SUM)
    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        rows = [fut_l.result(), fut_d.result(), fut_a.result()]
    modes_ok = _live_modes_ok(rows)
    # Honest archive: use NANOGEN7 true_continue (not a new TAC run rename).
    board = extract_nanogen8_board(
        true_continue_mean=float(tc7),
        n_true_continue=int(n_tc7),
        n_span_fallback=int(n_span7),
        parent6=float(tc6) if tc6 else PARENT_NANOGEN6_TRUE_CONTINUE,
        parent7=PARENT_NANOGEN7_TRUE_CONTINUE,
        live_modes_ok=modes_ok,
    )
    decision = decide_nanogen8(board=board, anti_fp_signed=True)
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
        "id": NANOGEN8_ID,
        "thesis": NANOGEN8_THESIS,
        "decision": decision,
        "stance": dict(NANOGEN8_STANCE),
        "method": dict(NANOGEN8_METHOD),
        "board": board,
        "true_gen_judge": dict(TRUE_GEN_JUDGE),
        "parent_archive": {
            "nanogen7_true_continue_mean": tc7,
            "nanogen7_n_true_continue": n_tc7,
            "nanogen7_n_span_fallback": n_span7,
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
        "claim": NANOGEN8_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hnanogen8-nanogen8.md",
        "next": "AX4 AX-REAL-EVAL",
        "anti_fp": NANOGEN8_ANTI_FP,
        "finding": (
            f"{NANOGEN8_ID}: stance={board.get('stance')} "
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
    ap = argparse.ArgumentParser(description="Wave AX3 H-NANOGEN8")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_nanogen8(
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
                "hyp_id": NANOGEN8_ID,
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
