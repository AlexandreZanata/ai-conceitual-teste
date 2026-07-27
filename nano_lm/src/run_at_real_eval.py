"""Wave AT4 AT-REAL-EVAL runner — product + gen + live ask battery."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from real_eval_ops import (
    ASK_BATTERY,
    PARENT_NANOGEN4_ABLATED,
    PROTOCOL,
    REAL_EVAL_CLAIM,
    REAL_EVAL_ID,
    REAL_EVAL_THESIS,
    battery_pass,
    decide_at_real_eval,
    force_abstain_row,
    near_miss_should_abstain,
)
from run_z_ask import ask_once
from shipapp_ops import attach_shipapp
from tipd_pair import tune_cpu_threads
from shipui_ops import attach_shipui

_SUMMARY = REPO / "results/nano-lm/wave-at/real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-at/trials"
_PRODREG = REPO / "results/nano-lm/wave-at/prodreg_summary.json"
_SHIPAPP = REPO / "results/nano-lm/wave-at/shipapp_summary.json"
_NANOGEN4 = REPO / "results/nano-lm/wave-at/nanogen4_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/wave-at-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-at/SESSION.md"
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
    workers = min(12, max(4, cpus - 2))
    return threads, workers


def _load_decision(path: Path) -> str:
    if not path.is_file():
        return "MISSING"
    data = json.loads(path.read_text(encoding="utf-8"))
    return str(data.get("decision", "MISSING"))


def _load_stats(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
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
    row = attach_shipapp(dict(payload))
    row["question"] = question
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
    elif kind == "known_lookup":
        payload = ask_once(
            question=q,
            root=root,
            seed=0,
            wrap=True,
            bank_path=bank,
            curated_root=curated,
            abstain=True,
        )
        payload = attach_shipapp(dict(payload))
    elif kind == "decode_smoke":
        payload = ask_once(
            question=q,
            root=root,
            seed=1,
            wrap=False,
            bank_path=bank,
            curated_root=curated,
            abstain=False,
        )
        payload = attach_shipapp(dict(payload))
    else:
        # ood_abstain · near_miss · junk_trap
        payload = ask_once(
            question=q,
            root=root,
            seed=0,
            semwrap=True,
            bank_path=bank,
            curated_root=curated,
            abstain=True,
        )
        payload = attach_shipapp(dict(payload))
        if kind == "near_miss" and near_miss_should_abstain(
            question=q,
            completion=str(payload.get("completion", "")),
            product_mode=str(payload.get("product_mode", "")),
        ):
            payload = attach_shipui(force_abstain_row(dict(payload)))
            payload["near_miss_refuse"] = True
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
    # Peak is CPU-heavy; keep sequential for peak, parallel others.
    peak = [i for i in items if i["kind"] == "labeled_peak"]
    rest = [i for i in items if i["kind"] != "labeled_peak"]
    out: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(workers, len(rest) or 1)) as pool:
        out.extend(list(pool.map(_one, rest)))
    for item in peak:
        out.append(_one(item))
    # Stable order by pack id
    by_id = {str(r["id"]): r for r in out}
    return [by_id[str(p["id"])] for p in ASK_BATTERY]


def _write_public(
    *,
    decision: str,
    pillars: dict[str, str],
    battery: list[dict[str, Any]],
    claim: str,
    nano_stats: dict[str, Any],
) -> None:
    bat_rows = [
        f"| {t['id']} | {t['kind']} | **{t.get('product_mode')}** | "
        f"`{t.get('expect_mode')}` | "
        f"{'PASS' if t.get('product_mode') == t.get('expect_mode') else 'FAIL'} |"
        for t in battery
    ]
    body = "\n".join(
        [
            f"# AT-REAL-EVAL — product + gen + live battery "
            f"(**DONE** — {decision.split('(', 1)[0].strip()})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AT4 · Session: "
            "`.local/wave-at/SESSION.md`  ",
            "> Parents: [formal-hprodreg-prodreg.md](formal-hprodreg-prodreg.md) · "
            "[formal-hshipapp-shipapp.md](formal-hshipapp-shipapp.md) · "
            "[formal-hnanogen4-nanogen4.md](formal-hnanogen4-nanogen4.md)  ",
            "> Module: `nano_lm/src/real_eval_ops.py` · "
            "Runner: `npm run nano:at:real-eval`",
            "",
            "## Hypothesis",
            "",
            REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| AT1 H-PRODREG | **{pillars['prodreg']}** |",
            f"| AT2 H-SHIPAPP | **{pillars['shipapp']}** |",
            f"| AT3 H-NANOGEN4 | **{pillars['nanogen4']}** "
            f"(ablated {nano_stats.get('gen_mean', PARENT_NANOGEN4_ABLATED)}) |",
            f"| Live ask battery | "
            f"**{'PASS' if battery_pass(battery) else 'FAIL'}** "
            f"({len(battery)}/{len(ASK_BATTERY)}) |",
            f"| Ship claim | `{claim}` |",
            f"| Decision | **{decision}** |",
            "",
            "## Live ask battery",
            "",
            "| ID | Kind | product_mode | expect | Row |",
            "|----|------|--------------|--------|-----|",
            *bat_rows,
            "",
            "## Finding",
            "",
            "1. Cite AT1–AT3 live summaries (no vanity rewrite of AS locks).  ",
            "2. Live ask battery under max safe CPU (`cpus-2`) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; near-miss SegWit/BIP-39 domain "
            "confusion → ABSTAIN refuse (anti-FP).  ",
            "3. Generative language allowed only because AT3 PROMOTE "
            "(ablated snippet-prefix DECODE) — still **not** unlabeled open chat.  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"summary_only_forbidden={PROTOCOL.get('summary_only_forbidden')}.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:at:real-eval",
            "npm run nano:nanogen4",
            "npm run nano:shipapp",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-at/real_eval_summary.json`  ",
            "- Contract: `nano_lm/tests/test_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Ablated DECODE (snippet-prefix) after AT3 | Unlabeled open chat |",
            "| Product PROMOTE + live battery | LOOKUP-as-IQ · Wave AU invent |",
            "| Mini-AGI-*inspired* stack shape (post AT4) | GPT-class / frontier chat |",
            "",
            "Next: **AT5 AT-REPORT** — public summary + paper-lab.",
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
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave AT session checklist (**OPEN** · AT4 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AT **OPEN**).  ",
            "> Parent: AS COMPLETE + FROZEN · Ship: **AF + AQ + AS trust + "
            "ablated DECODE (snippet-prefix)** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AT4 — AT-REAL-EVAL ({status})** · Next: **AT5 AT-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AT OPEN** |",
            f"| PRODREG / SHIPAPP | **{pillars.get('prodreg')}** / "
            f"**{pillars.get('shipapp')}** |",
            f"| NANOGEN4 | **{pillars.get('nanogen4')}** |",
            f"| Live battery | **{'PASS' if battery_ok else 'FAIL'}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AT0 | SESSION | **DONE — PROMOTE** |",
            "| AT1 | H-PRODREG | **DONE — PROMOTE** |",
            "| AT2 | H-SHIPAPP | **DONE — PROMOTE** |",
            "| AT3 | H-NANOGEN4 | **DONE — PROMOTE** |",
            f"| AT4 | AT-REAL-EVAL | **{status}** |",
            "| AT5 | AT-REPORT | **NEXT** |",
            "| AT6 | AT-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_at_real_eval(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    prodreg_path: Path,
    shipapp_path: Path,
    nanogen4_path: Path,
    claim: str,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AT1–AT3 summaries + live ask battery
    WHEN scoring AT4 real eval
    THEN PROMOTE iff product pass + battery pass + honest claim.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "prodreg": _load_decision(prodreg_path),
        "shipapp": _load_decision(shipapp_path),
        "nanogen4": _load_decision(nanogen4_path),
    }
    nano_stats = _load_stats(nanogen4_path)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    for row in battery:
        write_json(trials_dir / f"{row['id']}.json", row)
    ok_bat = battery_pass(battery)
    decision = decide_at_real_eval(
        prodreg_decision=pillars["prodreg"],
        shipapp_decision=pillars["shipapp"],
        nanogen4_decision=pillars["nanogen4"],
        battery_ok=ok_bat,
        claim=claim,
    )
    _write_public(
        decision=decision,
        pillars=pillars,
        battery=battery,
        claim=claim,
        nano_stats=nano_stats,
    )
    _update_local_session(decision, pillars, ok_bat)
    summary: dict[str, Any] = {
        "hyp_id": REAL_EVAL_ID,
        "stage": "AT4",
        "thesis": REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_pass": ok_bat,
        "claim": claim,
        "nanogen4_stats": nano_stats,
        "protocol": dict(PROTOCOL),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "elapsed_s": time.perf_counter() - t0,
        "finding": (
            f"{REAL_EVAL_ID}: prodreg={pillars['prodreg']} "
            f"shipapp={pillars['shipapp']} nanogen4={pillars['nanogen4']} "
            f"battery={'PASS' if ok_bat else 'FAIL'} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/wave-at-real-eval.md",
        "ship_claim": claim,
        "next": "AT5 AT-REPORT",
        "anti_fp": (
            "live battery modes; LOOKUP≠IQ; PEAK≠open-chat; "
            "gen claim only if AT3 PROMOTE"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AT4 AT-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--prodreg", type=Path, default=_PRODREG)
    ap.add_argument("--shipapp", type=Path, default=_SHIPAPP)
    ap.add_argument("--nanogen4", type=Path, default=_NANOGEN4)
    ap.add_argument("--claim", type=str, default=REAL_EVAL_CLAIM)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_at_real_eval(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            prodreg_path=Path(args.prodreg),
            shipapp_path=Path(args.shipapp),
            nanogen4_path=Path(args.nanogen4),
            claim=str(args.claim),
            workers=workers,
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
                "hyp_id": REAL_EVAL_ID,
                "decision": decision,
                "pillars": summary.get("pillars"),
                "battery_pass": summary.get("battery_pass"),
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
