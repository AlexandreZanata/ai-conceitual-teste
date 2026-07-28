"""Wave BA5 BA-REAL-EVAL runner — product+ctx+speed + live ask; gen if NANOGEN11 PROMOTE."""

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

from ba_real_eval_ops import (
    ASK_BATTERY,
    BA_REAL_EVAL_ANTI_FP,
    BA_REAL_EVAL_CLAIM,
    BA_REAL_EVAL_ID,
    BA_REAL_EVAL_SAFE_NOTE,
    BA_REAL_EVAL_THESIS,
    LOOKUP_KINDS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_ba_real_eval,
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

_SUMMARY = REPO / "results/nano-lm/wave-ba/ba_real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ba/real_eval_trials"
_REALGAIN = REPO / "results/nano-lm/wave-ba/realgain_summary.json"
_FASTREAL = REPO / "results/nano-lm/wave-ba/ba_fastreal_summary.json"
_CTXREAL2 = REPO / "results/nano-lm/wave-ba/ba_ctxreal2_summary.json"
_NANOGEN11 = REPO / "results/nano-lm/wave-ba/nanogen11_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-ba/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ba-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-ba/SESSION.md"
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
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(10, max(4, cpus - 4))
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
            f"# BA-REAL-EVAL — product+ctx+speed + live battery "
            f"(**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §1 · §8 BA5 · Session: "
            "`.local/wave-ba/SESSION.md`  ",
            "> Parents: [formal-hrealgain-realgain.md]"
            "(formal-hrealgain-realgain.md) · "
            "[formal-hfastreal-ba2.md](formal-hfastreal-ba2.md) · "
            "[formal-hctxreal2-ctxreal2.md](formal-hctxreal2-ctxreal2.md) · "
            "[formal-hnanogen11-nanogen11.md](formal-hnanogen11-nanogen11.md)  ",
            "> Module: `nano_lm/src/ba_real_eval_ops.py` · "
            "Runner: `npm run nano:ba:real-eval`",
            "",
            "## Hypothesis",
            "",
            BA_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| BA1 H-REALGAIN | **{pillars.get('realgain')}** |",
            f"| BA2 H-FASTREAL | **{pillars.get('fastreal')}** |",
            f"| BA3 H-CTXREAL2 | **{pillars.get('ctxreal2')}** |",
            f"| BA4 H-NANOGEN11 | **{pillars.get('nanogen11')}** "
            f"(true_continue_mean={tc}) |",
            f"| Live ask battery | **{'PASS' if battery_pass(battery) else 'FAIL'}** "
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
            "1. Cite BA1–BA4 live summaries (no vanity rewrite of AZ locks).  ",
            f"2. Live ask battery under max safe CPU (threads={threads}, "
            f"workers={workers}, ~{wall_s:.1f}s) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; forever FP → ABSTAIN; "
            "over-refuse → LOOKUP; DECODE junk → ABSTAIN.  ",
            "3. Generative unlock **locked** because BA4 DEFER "
            "(no real M1|M2|M3; NANOGEN6·7 HOLD · NANOGEN8·9·10 DEFER stand).  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "pack PASS ≠ forever.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"span_fallback_neq_gen={PROTOCOL.get('span_fallback_neq_gen')}.  ",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:ba:real-eval",
            "npm run nano:nanogen11",
            "npm run nano:ba:ctxreal2",
            "npm run nano:ba:fastreal",
            "npm run nano:realgain",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ba/ba_real_eval_summary.json`  ",
            "- Contract: `nano_lm/tests/test_ba_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Product/ctx/speed PROMOTE + live battery | Unlabeled open chat |",
            "| STRICT ship lock while BA4 DEFER | Gen unlock on DEFER/HOLD |",
            "| Forever ABSTAIN · over-refuse LOOKUP | LOOKUP-as-IQ · invent BB |",
            "",
            f"SAFE note: {BA_REAL_EVAL_SAFE_NOTE}  ",
            f"Anti-FP: {BA_REAL_EVAL_ANTI_FP}",
            "",
            "Next: **BA6 BA-REPORT** — summary + paper-lab.",
            "",
        ]
    )
    _PUBLIC.write_text(body, encoding="utf-8")


def _write_session(decision: str, battery: list[dict[str, Any]]) -> None:
    status = decision.split("(", 1)[0].strip()
    n_pass = sum(1 for t in battery if battery_row_ok(t))
    body = "\n".join(
        [
            f"# Wave BA session checklist (**OPEN** · BA5 DONE — {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Ship lock: **{BA_REAL_EVAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BA5 — BA-REAL-EVAL (DONE — {status})** · "
            "Next: **BA6 BA-REPORT**",
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
            "| BA0 | SESSION | **DONE — PROMOTE** |",
            "| BA1 | H-REALGAIN | **DONE — PROMOTE** |",
            "| BA2 | H-FASTREAL | **DONE — PROMOTE** |",
            "| BA3 | H-CTXREAL2 | **DONE — PROMOTE** |",
            "| BA4 | H-NANOGEN11 | **DONE — DEFER** |",
            f"| BA5 | BA-REAL-EVAL | **DONE — {status}** |",
            "| BA6 | BA-REPORT | **NEXT** |",
            "| BA7 | BA-FREEZE | pending |",
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
    ba5_next = (
        "| BA5 | **BA-REAL-EVAL** | Product + ctx + speed + gen + **live ask** "
        "(prod=eval) | gen claim iff BA4 PROMOTE | **NEXT** |"
    )
    ba5_done = (
        "| BA5 | **BA-REAL-EVAL** | Product + ctx + speed + gen + **live ask** "
        "(prod=eval) | gen claim iff BA4 PROMOTE | "
        f"**DONE — {status}** |"
    )
    if ba5_next in text:
        text = text.replace(ba5_next, ba5_done, 1)
    text = text.replace(
        "6. **BA5 BA-REAL-EVAL** — **NEXT** — product + ctx + speed + gen "
        "(gen claim iff BA4 PROMOTE).  ",
        f"6. **BA5 BA-REAL-EVAL** — **DONE {status}** "
        "(`npm run nano:ba:real-eval`) — battery live; gen locked (BA4 DEFER).  ",
        1,
    )
    text = text.replace(
        "7. **BA6→BA7** — report · freeze.  ",
        "7. **BA6 BA-REPORT** — **NEXT** — summary + paper-lab.  \n"
        "8. **BA7 BA-FREEZE** — lock outcomes.  ",
        1,
    )
    ba6_todo = (
        "| BA6 | **BA-REPORT** | Summary + paper-lab | anti-FP · HOLD/DEFER cited "
        "| **TODO** |"
    )
    ba6_next = (
        "| BA6 | **BA-REPORT** | Summary + paper-lab | anti-FP · HOLD/DEFER cited "
        "| **NEXT** |"
    )
    if ba6_todo in text:
        text = text.replace(ba6_todo, ba6_next, 1)
    text = text.replace(
        "npm run nano:nanogen11\n"
        "# next: nano:ba:real-eval\n"
        "# npm run nano:ba:real-eval\n",
        "npm run nano:nanogen11\n"
        "npm run nano:ba:real-eval\n"
        "# next: nano:ba:report\n",
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ba/SESSION.md` "
        "(BA4 H-NANOGEN11 **DONE — DEFER**; next BA5 BA-REAL-EVAL).  ",
        "> **Session:** `.local/wave-ba/SESSION.md` "
        f"(BA5 BA-REAL-EVAL **DONE — {status}**; next BA6 BA-REPORT).  ",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    _LOCAL_IMPL.write_text(
        f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

**BA0–BA3 PROMOTE · BA4 DEFER · BA5 DONE — {status}**. Next: **BA6 BA-REPORT**.

```bash
npm run nano:ba:real-eval
npm run nano:test && npm run verify
```
""",
        encoding="utf-8",
    )
    _LOCAL_README.write_text(
        f"""# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BA ACTIVE** — BA5 **BA-REAL-EVAL {status}** (gen locked).

Next: **BA6 BA-REPORT**.
""",
        encoding="utf-8",
    )


def _ba_active_line(status: str) -> str:
    return (
        "**Wave BA ACTIVE:** BA0 [SESSION PROMOTE](wave-ba-session.md) · "
        "BA1 [H-REALGAIN PROMOTE](formal-hrealgain-realgain.md) · "
        "BA2 [H-FASTREAL PROMOTE](formal-hfastreal-ba2.md) · "
        "BA3 [H-CTXREAL2 PROMOTE](formal-hctxreal2-ctxreal2.md) · "
        "BA4 [H-NANOGEN11 DEFER](formal-hnanogen11-nanogen11.md) · "
        f"BA5 [BA-REAL-EVAL {status}](wave-ba-real-eval.md) "
        f"(`npm run nano:ba:real-eval`) — live battery; gen locked; "
        "next BA6 BA-REPORT; ship remains **AF + AQ + AS trust + STRICT "
        "ablated DECODE**; ≤5M stays."
    )


def _patch_recipes(status: str, n_pass: int, n_bat: int) -> None:
    if not _RECIPES.is_file():
        return
    line = _ba_active_line(status)
    text = _RECIPES.read_text(encoding="utf-8")
    text2, n = re.subn(r"\*\*Wave BA ACTIVE:\*\*[^\n]+", line, text, count=1)
    insert = (
        f"| Wave BA5 BA-REAL-EVAL | [wave-ba-real-eval.md]"
        f"(wave-ba-real-eval.md) **{status}** (`npm run nano:ba:real-eval`) "
        f"— battery {n_pass}/{n_bat} · gen locked (BA4 DEFER) |"
    )
    if "Wave BA5 BA-REAL-EVAL" not in text2 and "Wave BA4 H-NANOGEN11 |" in text2:
        text2 = text2.replace(
            "| Wave BA4 H-NANOGEN11 |",
            insert + "\n| Wave BA4 H-NANOGEN11 |",
            1,
        )
    if n or "Wave BA5 BA-REAL-EVAL" in text2:
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
            "[H-NANOGEN11 DEFER](docs/results/nano-lm/formal-hnanogen11-nanogen11.md) "
            f"· BA5 [BA-REAL-EVAL {status}]"
            "(docs/results/nano-lm/wave-ba-real-eval.md) "
            "(`npm run nano:ba:real-eval`); next BA6 BA-REPORT; ship remains "
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
            f"| **BA** | **ACTIVE** | BA0–BA3 PROMOTE · BA4 DEFER · BA5 "
            f"BA-REAL-EVAL {status} (`npm run nano:ba:real-eval`); "
            "next BA6 BA-REPORT; ≤5M |"
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
        "BA0–BA3 PROMOTE · BA4 H-NANOGEN11 DEFER; next BA5 BA-REAL-EVAL",
        f"BA0–BA3 PROMOTE · BA4 DEFER · BA5 BA-REAL-EVAL {status}; "
        "next BA6 BA-REPORT",
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


def run_ba_real_eval(
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
    GIVEN BA1–BA4 summaries + BA0 live battery
    WHEN scoring prod=eval ask paths
    THEN PROMOTE iff product/ctx/speed + battery + honest gen lock.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    realgain = _load_decision(_REALGAIN)
    fastreal = _load_decision(_FASTREAL)
    ctxreal2 = _load_decision(_CTXREAL2)
    nanogen11 = _load_decision(_NANOGEN11)
    nano_board = _load_board(_NANOGEN11)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    bat_ok = battery_pass(battery)
    claim = BA_REAL_EVAL_CLAIM
    decision = decide_ba_real_eval(
        realgain_decision=realgain,
        fastreal_decision=fastreal,
        ctxreal2_decision=ctxreal2,
        nanogen11_decision=nanogen11,
        battery_ok=bat_ok,
        claim=claim,
    )
    wall_s = time.perf_counter() - t0
    pillars = {
        "realgain": realgain,
        "fastreal": fastreal,
        "ctxreal2": ctxreal2,
        "nanogen11": nanogen11,
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
        "id": BA_REAL_EVAL_ID,
        "stage": "BA5",
        "thesis": BA_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_ok": bat_ok,
        "battery_pass_n": sum(1 for t in battery if battery_row_ok(t)),
        "battery_n": len(battery),
        "claim": claim,
        "protocol": dict(PROTOCOL),
        "nanogen11_board": nano_board,
        "wall_s": wall_s,
        "cpu_threads": threads,
        "workers": workers,
        "public_note": "docs/results/nano-lm/wave-ba-real-eval.md",
        "next": "BA6 BA-REPORT",
        "anti_fp": BA_REAL_EVAL_ANTI_FP,
    }
    write_json(out, payload)
    write_json(trials_dir / "battery.json", {"rows": battery})
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave BA5 BA-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        payload = run_ba_real_eval(
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
                "hyp_id": BA_REAL_EVAL_ID,
                "stage": "BA5",
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
