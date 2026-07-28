"""Wave AY4 AY-REAL-EVAL runner — product pass + live ask; gen if NANOGEN9 PROMOTE."""

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

from ay_real_eval_ops import (
    ASK_BATTERY,
    AY_REAL_EVAL_CLAIM,
    AY_REAL_EVAL_ID,
    AY_REAL_EVAL_THESIS,
    LOOKUP_KINDS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_ay_real_eval,
    force_abstain_row,
    near_miss_should_abstain,
)
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_once
from shipay_ops import attach_shipay
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ay/real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ay/real_eval_trials"
_PRODINT = REPO / "results/nano-lm/wave-ay/prodint_summary.json"
_SHIPAY = REPO / "results/nano-lm/wave-ay/shipay_summary.json"
_NANOGEN9 = REPO / "results/nano-lm/wave-ay/nanogen9_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-ay/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ay-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-ay/SESSION.md"
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
    row = attach_shipay(dict(payload))
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
    row = attach_shipay(dict(payload))
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
            semwrap=kind in {"human_para", "hard_natural", "hard_natural_hold"},
            bank_path=bank,
            curated_root=curated,
            abstain=True,
        )
        payload = attach_shipay(dict(payload))
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
        payload = attach_shipay(dict(payload))
        if kind == "near_miss" and near_miss_should_abstain(
            question=q,
            completion=str(payload.get("completion", "")),
            product_mode=str(payload.get("product_mode", "")),
        ):
            payload = attach_shipay(force_abstain_row(dict(payload)))
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
            f"# AY-REAL-EVAL — product pass + live battery "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AY4 · Session: "
            "`.local/wave-ay/SESSION.md`  ",
            "> Parents: [formal-hprodint-prodint.md]"
            "(formal-hprodint-prodint.md) · "
            "[formal-hshipay-shipay.md](formal-hshipay-shipay.md) · "
            "[formal-hnanogen9-nanogen9.md](formal-hnanogen9-nanogen9.md)  ",
            "> Module: `nano_lm/src/ay_real_eval_ops.py` · "
            "Runner: `npm run nano:ay:real-eval`",
            "",
            "## Hypothesis",
            "",
            AY_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| AY1 H-PRODINT | **{pillars['prodint']}** |",
            f"| AY2 H-SHIPAY | **{pillars['shipay']}** |",
            f"| AY3 H-NANOGEN9 | **{pillars['nanogen9']}** "
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
            "1. Cite AY1–AY3 live summaries (no vanity rewrite of AX locks).  ",
            "2. Live ask battery under max safe CPU "
            f"(threads={threads}, workers={workers}, ~{wall_s:.1f}s) — "
            "modes labeled; `wall_ms`/`n_new` mandatory; usability scored; "
            "near-miss → ABSTAIN; intent-FP → ABSTAIN; DECODE junk → ABSTAIN; "
            "hard-natural → LOOKUP.  ",
            "3. Generative unlock **locked** because AY3 DEFER "
            "(no real new method; NANOGEN6·7 HOLD · NANOGEN8 DEFER stand; "
            "not NANOGEN8 rename) — ship stays STRICT archive, "
            "**not** unlabeled open chat.  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "intent-mismatch LOOKUP = false-hit · "
            "gold-substring / span-fallback ≠ gen.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"intent_fp={PROTOCOL.get('intent_mismatch_is_false_hit')} · "
            f"span_fallback_neq_gen={PROTOCOL.get('span_fallback_neq_gen')}.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ay:real-eval",
            "npm run nano:nanogen9",
            "npm run nano:shipay",
            "npm run nano:prodint",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ay/real_eval_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ay_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Product PROMOTE + live battery 8/8 | Unlabeled open chat |",
            "| STRICT ship lock while AY3 DEFER | Gen unlock on DEFER/HOLD |",
            "| Intent-FP ABSTAIN · DECODE usable/ABSTAIN | LOOKUP-as-IQ · invent AZ |",
            "",
            "Next: **AY5 AY-REPORT** — public summary + paper-lab.",
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
            f"# Wave AY session checklist (**OPEN** · AY4 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AY **OPEN** · intent harden + gen defer).  ",
            f"> Ship lock: **{AY_REAL_EVAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AY4 — AY-REAL-EVAL (DONE — {status})** · "
            "Next: **AY5 AY-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AY OPEN** |",
            f"| PRODINT / SHIPAY | **{pillars.get('prodint')}** / "
            f"**{pillars.get('shipay')}** |",
            f"| NANOGEN9 | **{pillars.get('nanogen9')}** |",
            f"| Live battery | **{'PASS' if battery_ok else 'FAIL'}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AY0 | SESSION | **DONE — PROMOTE** |",
            "| AY1 | H-PRODINT | **DONE — PROMOTE** |",
            "| AY2 | H-SHIPAY | **DONE — PROMOTE** |",
            "| AY3 | H-NANOGEN9 | **DONE — DEFER** |",
            f"| AY4 | AY-REAL-EVAL | **DONE — {status}** |",
            "| AY5 | AY-REPORT | **NEXT** |",
            "| AY6 | AY-FREEZE | pending |",
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
        r"\| AY4 \| \*\*AY-REAL-EVAL\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AY4 | **AY-REAL-EVAL** | Final real eval: product + gen + "
            "**live ask** (prod = eval) | product pass; gen claim only if "
            f"AY3 PROMOTE | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2c. **AY3 H-NANOGEN9** — **DONE DEFER** (`npm run nano:nanogen9`) · "
            "next **AY4 AY-REAL-EVAL**.  "
        ),
        (
            "2c. **AY3 H-NANOGEN9** — **DONE DEFER** (`npm run nano:nanogen9`).  \n"
            f"2d. **AY4 AY-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:ay:real-eval`) · next **AY5 AY-REPORT**.  "
        ),
        1,
    )
    text = text.replace(
        (
            "5. **AY4–AY6** — real-eval (live ask) · report · freeze.  "
        ),
        (
            f"5. **AY4 AY-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:ay:real-eval`) · next AY5–AY6 report · freeze.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ay/SESSION.md` "
        "(AY3 H-NANOGEN9 **DONE — DEFER**; next AY4 AY-REAL-EVAL).  ",
        "> **Session:** `.local/wave-ay/SESSION.md` "
        f"(AY4 AY-REAL-EVAL **DONE — {status}**; next AY5 AY-REPORT).  ",
        1,
    )
    if "# next: nano:ay:real-eval" in text:
        text = text.replace(
            "# next: nano:ay:real-eval\n# npm run nano:ay:real-eval",
            "npm run nano:ay:real-eval\n# next: nano:ay:report",
            1,
        )
        if "# next: nano:ay:real-eval" in text:
            text = text.replace(
                "# next: nano:ay:real-eval",
                "npm run nano:ay:real-eval\n# next: nano:ay:report",
                1,
            )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2c. **AY3 H-NANOGEN9** — **DONE DEFER** (`npm run nano:nanogen9`) · "
            "next **AY4 AY-REAL-EVAL**.  "
        )
        new = (
            "2c. **AY3 H-NANOGEN9** — **DONE DEFER** (`npm run nano:nanogen9`).  \n"
            f"2d. **AY4 AY-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:ay:real-eval`) · next **AY5 AY-REPORT**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ay/SESSION.md` (AY3 H-NANOGEN9 **DONE — DEFER**; "
            "next AY4 AY-REAL-EVAL)."
        )
        new = (
            f"Session: `wave-ay/SESSION.md` (AY4 AY-REAL-EVAL "
            f"**DONE — {status}**; next AY5 AY-REPORT)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _insert_real_eval_frag(text: str, prefix: str, status: str) -> str:
    if f"AY-REAL-EVAL {status}" in text or f"AY4 [AY-REAL-EVAL {status}]" in text:
        return text
    frag = (
        f"AY4 [AY-REAL-EVAL {status}](wave-ay-real-eval.md) "
        f"(`npm run nano:ay:real-eval`) — battery 8/8 · gen locked (AY3 DEFER)"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*H-NANOGEN9 DEFER[^\n]*?)"
        r"(; next AY4 AY-REAL-EVAL|; next AY4)",
        rf"\1 · {frag}; next AY5 AY-REPORT",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if f"AY-REAL-EVAL {status}" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AY ACTIVE\*\* —[^\n]*H-NANOGEN9 DEFER[^\n]*?)"
        r"(; next AY4 AY-REAL-EVAL|; next AY4)",
        rf"\1 · AY4 [AY-REAL-EVAL {status}]"
        r"(docs/results/nano-lm/wave-ay-real-eval.md) "
        r"(`npm run nano:ay:real-eval`); next AY5 AY-REPORT",
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
    if f"AY-REAL-EVAL {status}" in ay_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AY\*\* \| \*\*ACTIVE\*\* \|[^\n]*H-NANOGEN9 "
        r"DEFER[^\n]*?)(; next AY4 AY-REAL-EVAL|; next AY4)",
        rf"\1 · AY4 [AY-REAL-EVAL {status}]"
        r"(results/nano-lm/wave-ay-real-eval.md); "
        r"next AY5 AY-REPORT",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "wave-ay-real-eval.md" in text:
        return
    needle = (
        "Wave AY3: `formal-hnanogen9-nanogen9.md` DEFER · Wave AX0:"
    )
    repl = (
        "Wave AY3: `formal-hnanogen9-nanogen9.md` DEFER · "
        f"Wave AY4: `wave-ay-real-eval.md` {status} · Wave AX0:"
    )
    if needle in text:
        _EVOGEN.write_text(text.replace(needle, repl, 1), encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    status = decision.split("(", 1)[0].strip()
    for path, prefix in (
        (_RECIPES, "**Wave AY ACTIVE:**"),
        (_CARD, "**Wave AY ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_real_eval_frag(text, prefix, status)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    if _RECIPES.is_file():
        text = _RECIPES.read_text(encoding="utf-8")
        if "Wave AY4 AY-REAL-EVAL" not in text:
            needle = (
                "| Wave AY3 H-NANOGEN9 | [formal-hnanogen9-nanogen9.md]"
                "(formal-hnanogen9-nanogen9.md) **DEFER** "
                "(`npm run nano:nanogen9`) — gen stance defer · CAPCHECK "
                "closed · not NANOGEN8 rename · true_continue unmet |\n"
            )
            row = (
                f"| Wave AY4 AY-REAL-EVAL | [wave-ay-real-eval.md]"
                f"(wave-ay-real-eval.md) **{status}** "
                f"(`npm run nano:ay:real-eval`) — battery 8/8 · "
                "gen locked (AY3 DEFER) · intent-FP ABSTAIN · prod=eval |\n"
            )
            if needle in text:
                _RECIPES.write_text(
                    text.replace(needle, needle + row, 1), encoding="utf-8"
                )
    _patch_agents(status)
    _patch_agenda(status)
    _patch_evogen(status)


def run_ay_real_eval(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    prodint_path: Path,
    shipay_path: Path,
    nanogen9_path: Path,
    claim: str,
    workers: int,
    threads: int,
) -> dict[str, Any]:
    """
    GIVEN AY1–AY3 summaries + live ask battery
    WHEN scoring AY4 real eval
    THEN PROMOTE iff product pass + battery pass + honest claim.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "prodint": _load_decision(prodint_path),
        "shipay": _load_decision(shipay_path),
        "nanogen9": _load_decision(nanogen9_path),
    }
    nano_board = _load_board(nanogen9_path)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    for row in battery:
        write_json(trials_dir / f"{row['id']}.json", row)
    ok_bat = battery_pass(battery)
    decision = decide_ay_real_eval(
        prodint_decision=pillars["prodint"],
        shipay_decision=pillars["shipay"],
        nanogen9_decision=pillars["nanogen9"],
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
        "hyp_id": AY_REAL_EVAL_ID,
        "stage": "AY4",
        "thesis": AY_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_pass": ok_bat,
        "claim": claim,
        "nanogen9_board": nano_board,
        "protocol": dict(PROTOCOL),
        "cpu_threads": threads,
        "workers": int(workers),
        "elapsed_s": wall_s,
        "finding": (
            f"{AY_REAL_EVAL_ID}: prodint={pillars['prodint']} "
            f"shipay={pillars['shipay']} nanogen9={pillars['nanogen9']} "
            f"battery={'PASS' if ok_bat else 'FAIL'} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/wave-ay-real-eval.md",
        "ship_claim": claim,
        "next": "AY5 AY-REPORT",
        "anti_fp": (
            "live battery modes+usability; LOOKUP≠IQ; PEAK≠open-chat; "
            "intent-FP ABSTAIN; span-fallback≠gen; "
            "gen unlock only if AY3 PROMOTE"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AY4 AY-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--prodint", type=Path, default=_PRODINT)
    ap.add_argument("--shipay", type=Path, default=_SHIPAY)
    ap.add_argument("--nanogen9", type=Path, default=_NANOGEN9)
    ap.add_argument("--claim", type=str, default=AY_REAL_EVAL_CLAIM)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_ay_real_eval(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            prodint_path=Path(args.prodint),
            shipay_path=Path(args.shipay),
            nanogen9_path=Path(args.nanogen9),
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
                "hyp_id": AY_REAL_EVAL_ID,
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
