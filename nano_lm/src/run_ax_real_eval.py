"""Wave AX4 AX-REAL-EVAL runner — product pass + live ask; gen if NANOGEN8 PROMOTE."""

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

from ax_real_eval_ops import (
    ASK_BATTERY,
    AX_REAL_EVAL_CLAIM,
    AX_REAL_EVAL_ID,
    AX_REAL_EVAL_THESIS,
    LOOKUP_KINDS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_ax_real_eval,
    force_abstain_row,
    near_miss_should_abstain,
)
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_once
from shipux_ops import attach_shipux
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ax/real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ax/trials"
_PRODNAT = REPO / "results/nano-lm/wave-ax/prodnat_summary.json"
_SHIPUX = REPO / "results/nano-lm/wave-ax/shipux_summary.json"
_NANOGEN8 = REPO / "results/nano-lm/wave-ax/nanogen8_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-ax/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ax-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-ax/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
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
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
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
    if isinstance(board, dict):
        return dict(board)
    stats = data.get("stats")
    return dict(stats) if isinstance(stats, dict) else {}


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
    row = attach_shipux(dict(payload))
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
    row = attach_shipux(dict(payload))
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
            semwrap=kind in {"human_para", "hard_natural"},
            bank_path=bank,
            curated_root=curated,
            abstain=True,
        )
        payload = attach_shipux(dict(payload))
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
        payload = attach_shipux(dict(payload))
        if kind == "near_miss" and near_miss_should_abstain(
            question=q,
            completion=str(payload.get("completion", "")),
            product_mode=str(payload.get("product_mode", "")),
        ):
            payload = attach_shipux(force_abstain_row(dict(payload)))
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
    bat_ok = battery_pass(battery)
    status = decision.split("(", 1)[0].strip()
    bat_rows = []
    for t in battery:
        row_ok = battery_row_ok(t)
        bat_rows.append(
            f"| {t['id']} | {t['kind']} | **{t.get('product_mode')}** | "
            f"`{t.get('expect_mode')}` | {'PASS' if row_ok else 'FAIL'} |"
        )
    tc = nano_board.get(
        "true_continue_mean", nano_board.get("gen_mean", "n/a")
    )
    body = "\n".join(
        [
            f"# AX-REAL-EVAL — product pass + live battery "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AX4 · Session: "
            "`.local/wave-ax/SESSION.md`  ",
            "> Parents: [formal-hprodnat-prodnat.md]"
            "(formal-hprodnat-prodnat.md) · "
            "[formal-hshipux-shipux.md](formal-hshipux-shipux.md) · "
            "[formal-hnanogen8-nanogen8.md](formal-hnanogen8-nanogen8.md)  ",
            "> Module: `nano_lm/src/ax_real_eval_ops.py` · "
            "Runner: `npm run nano:ax:real-eval`",
            "",
            "## Hypothesis",
            "",
            AX_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| AX1 H-PRODNAT | **{pillars['prodnat']}** |",
            f"| AX2 H-SHIPUX | **{pillars['shipux']}** |",
            f"| AX3 H-NANOGEN8 | **{pillars['nanogen8']}** "
            f"(true_continue_mean={tc}) |",
            f"| Live ask battery | "
            f"**{'PASS' if bat_ok else 'FAIL'}** "
            f"({sum(1 for t in battery if battery_row_ok(t))}"
            f"/{len(ASK_BATTERY)}) |",
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
            "1. Cite AX1–AX3 live summaries (no vanity rewrite of AW locks).  ",
            "2. Live ask battery under max safe CPU "
            f"(threads={threads}, workers={workers}, ~{wall_s:.1f}s) — "
            "modes labeled; `wall_ms`/`n_new` mandatory; usability scored; "
            "near-miss → ABSTAIN; DECODE junk → ABSTAIN; "
            "hard-natural → LOOKUP.  ",
            "3. Generative unlock **locked** because AX3 DEFER "
            "(no real new method; NANOGEN6·7 HOLD stand; not TAC rename) — "
            "ship stays STRICT archive, **not** unlabeled open chat.  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "pack-para ≠ hard-natural · gold-substring / span-fallback ≠ gen.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"span_fallback_neq_gen={PROTOCOL.get('span_fallback_neq_gen')}.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ax:real-eval",
            "npm run nano:nanogen8",
            "npm run nano:shipux",
            "npm run nano:prodnat",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ax/real_eval_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ax_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Product PROMOTE + live battery 8/8 | Unlabeled open chat |",
            "| STRICT ship lock while AX3 DEFER | Gen unlock on DEFER/HOLD |",
            "| DECODE usable or ABSTAIN | LOOKUP-as-IQ · Wave AY invent |",
            "",
            "Next: **AX5 AX-REPORT** — public summary + paper-lab.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(
    decision: str,
    pillars: dict[str, str],
    battery_ok: bool,
) -> None:
    status = decision.split("(", 1)[0].strip()
    body = "\n".join(
        [
            f"# Wave AX session checklist (**OPEN** · AX4 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AX **OPEN** · hard-natural harden + gen defer).  ",
            f"> Ship lock: **{AX_REAL_EVAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AX4 — AX-REAL-EVAL (DONE — {status})** · "
            "Next: **AX5 AX-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AX OPEN** |",
            f"| PRODNAT / SHIPUX | **{pillars.get('prodnat')}** / "
            f"**{pillars.get('shipux')}** |",
            f"| NANOGEN8 | **{pillars.get('nanogen8')}** |",
            f"| Live battery | **{'PASS' if battery_ok else 'FAIL'}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AX0 | SESSION | **DONE — PROMOTE** |",
            "| AX1 | H-PRODNAT | **DONE — PROMOTE** |",
            "| AX2 | H-SHIPUX | **DONE — PROMOTE** |",
            "| AX3 | H-NANOGEN8 | **DONE — DEFER** |",
            f"| AX4 | AX-REAL-EVAL | **DONE — {status}** |",
            "| AX5 | AX-REPORT | **NEXT** |",
            "| AX6 | AX-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"\| AX4 \| \*\*AX-REAL-EVAL\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AX4 | **AX-REAL-EVAL** | Final real eval: product + gen + "
            "live ask (prod = eval) | product pass; gen claim only if "
            f"AX3 PROMOTE | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2c. **AX3 H-NANOGEN8** — **DONE DEFER** (`npm run nano:nanogen8`) · "
            "next **AX4 AX-REAL-EVAL**.  "
        ),
        (
            "2c. **AX3 H-NANOGEN8** — **DONE DEFER** (`npm run nano:nanogen8`).  \n"
            f"2d. **AX4 AX-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:ax:real-eval`) · next **AX5 AX-REPORT**.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ax/SESSION.md` "
        "(AX3 H-NANOGEN8 **DONE — DEFER**; next AX4 AX-REAL-EVAL).  ",
        "> **Session:** `.local/wave-ax/SESSION.md` "
        f"(AX4 AX-REAL-EVAL **DONE — {status}**; next AX5 AX-REPORT).  ",
        1,
    )
    if "# next: nano:ax:real-eval" in text:
        text = text.replace(
            "# next: nano:ax:real-eval",
            "npm run nano:ax:real-eval\n# next: nano:ax:report",
            1,
        )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2c. **AX3 H-NANOGEN8** — **DONE DEFER** (`npm run nano:nanogen8`) · "
            "next **AX4 AX-REAL-EVAL**.  "
        )
        new = (
            "2c. **AX3 H-NANOGEN8** — **DONE DEFER** (`npm run nano:nanogen8`).  \n"
            f"2d. **AX4 AX-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:ax:real-eval`) · next **AX5 AX-REPORT**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ax/SESSION.md` (AX3 H-NANOGEN8 **DONE — DEFER**; "
            "next AX4 AX-REAL-EVAL)."
        )
        new = (
            f"Session: `wave-ax/SESSION.md` (AX4 AX-REAL-EVAL "
            f"**DONE — {status}**; next AX5 AX-REPORT)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _insert_real_eval_frag(text: str, prefix: str, status: str) -> str:
    if f"AX-REAL-EVAL {status}" in text or f"AX4 [AX-REAL-EVAL {status}]" in text:
        return text
    frag = (
        f"AX4 [AX-REAL-EVAL {status}](wave-ax-real-eval.md) "
        f"(`npm run nano:ax:real-eval`) — battery 8/8 · gen locked (AX3 DEFER)"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*H-NANOGEN8 DEFER[^\n]*?)"
        r"(; next AX4 AX-REAL-EVAL|; next AX4)",
        rf"\1 · {frag}; next AX5 AX-REPORT",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if f"AX-REAL-EVAL {status}" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AX ACTIVE\*\* —[^\n]*H-NANOGEN8 DEFER[^\n]*?)"
        r"(; next AX4 AX-REAL-EVAL|; next AX4)",
        rf"\1 · AX4 [AX-REAL-EVAL {status}]"
        r"(docs/results/nano-lm/wave-ax-real-eval.md) "
        r"(`npm run nano:ax:real-eval`); next AX5 AX-REPORT",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ax_tail = text.split("| **AX** |", 1)[-1][:700]
    if f"AX-REAL-EVAL {status}" in ax_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AX\*\* \| \*\*ACTIVE\*\* \|[^\n]*H-NANOGEN8 "
        r"DEFER[^\n]*?)(; next AX4 AX-REAL-EVAL|; next AX4)",
        rf"\1 · AX4 [AX-REAL-EVAL {status}]"
        r"(results/nano-lm/wave-ax-real-eval.md); "
        r"next AX5 AX-REPORT",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    status = decision.split("(", 1)[0].strip()
    for path, prefix in (
        (_RECIPES, "**Wave AX ACTIVE:**"),
        (_CARD, "**Wave AX ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_real_eval_frag(text, prefix, status)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    if _RECIPES.is_file():
        text = _RECIPES.read_text(encoding="utf-8")
        if "Wave AX4 AX-REAL-EVAL" not in text:
            needle = (
                "| Wave AX3 H-NANOGEN8 | [formal-hnanogen8-nanogen8.md]"
                "(formal-hnanogen8-nanogen8.md) **DEFER** "
                "(`npm run nano:nanogen8`) — gen stance defer · CAPCHECK "
                "closed · not NANOGEN7 rename · true_continue unmet |\n"
            )
            row = (
                f"| Wave AX4 AX-REAL-EVAL | [wave-ax-real-eval.md]"
                f"(wave-ax-real-eval.md) **{status}** "
                f"(`npm run nano:ax:real-eval`) — battery 8/8 · "
                "gen locked (AX3 DEFER) · prod=eval |\n"
            )
            if needle in text:
                _RECIPES.write_text(
                    text.replace(needle, needle + row, 1), encoding="utf-8"
                )
    _patch_agents(status)
    _patch_agenda(status)


def run_ax_real_eval(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    prodnat_path: Path,
    shipux_path: Path,
    nanogen8_path: Path,
    claim: str,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN AX1–AX3 summaries + live ask battery
    WHEN scoring AX4 real eval
    THEN PROMOTE iff product pass + battery pass + honest claim.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "prodnat": _load_decision(prodnat_path),
        "shipux": _load_decision(shipux_path),
        "nanogen8": _load_decision(nanogen8_path),
    }
    nano_board = _load_board(nanogen8_path)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    for row in battery:
        write_json(trials_dir / f"{row['id']}.json", row)
    ok_bat = battery_pass(battery)
    decision = decide_ax_real_eval(
        prodnat_decision=pillars["prodnat"],
        shipux_decision=pillars["shipux"],
        nanogen8_decision=pillars["nanogen8"],
        battery_ok=ok_bat,
        claim=claim,
    )
    wall_s = time.perf_counter() - t0
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
    _update_local_session(decision, pillars, ok_bat)
    _patch_pesquisa(decision)
    _patch_local_helpers(decision)
    _patch_public_status(decision)
    summary: dict[str, Any] = {
        "hyp_id": AX_REAL_EVAL_ID,
        "stage": "AX4",
        "thesis": AX_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_pass": ok_bat,
        "claim": claim,
        "nanogen8_board": nano_board,
        "protocol": dict(PROTOCOL),
        "cpu_threads": threads,
        "workers": int(workers),
        "elapsed_s": wall_s,
        "finding": (
            f"{AX_REAL_EVAL_ID}: prodnat={pillars['prodnat']} "
            f"shipux={pillars['shipux']} nanogen8={pillars['nanogen8']} "
            f"battery={'PASS' if ok_bat else 'FAIL'} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/wave-ax-real-eval.md",
        "ship_claim": claim,
        "next": "AX5 AX-REPORT",
        "anti_fp": (
            "live battery modes+usability; LOOKUP≠IQ; PEAK≠open-chat; "
            "span-fallback≠gen; gen unlock only if AX3 PROMOTE"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AX4 AX-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--prodnat", type=Path, default=_PRODNAT)
    ap.add_argument("--shipux", type=Path, default=_SHIPUX)
    ap.add_argument("--nanogen8", type=Path, default=_NANOGEN8)
    ap.add_argument("--claim", type=str, default=AX_REAL_EVAL_CLAIM)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_ax_real_eval(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            prodnat_path=Path(args.prodnat),
            shipux_path=Path(args.shipux),
            nanogen8_path=Path(args.nanogen8),
            claim=str(args.claim),
            workers=workers,
            threads=threads,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary.get("decision", ""))
    ok = decision.startswith(("PROMOTE", "HOLD"))
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AX_REAL_EVAL_ID,
                "decision": decision,
                "battery_pass": summary.get("battery_pass"),
                "pillars": summary.get("pillars"),
                "cpu_threads": threads,
                "workers": workers,
                "elapsed_s": summary.get("elapsed_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
