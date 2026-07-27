"""Wave AT2 H-SHIPAPP runner (nano:shipapp) — ask · apps · ship/demo modes."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ap_session_ops import AP0_PACK
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_many, ask_once
from shipapp_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    REQUIRED_MODES,
    SHIPAPP_CLAIM,
    SHIPAPP_ID,
    SHIPAPP_PATHS,
    SHIPAPP_THESIS,
    attach_shipapp,
    decide_shipapp,
    demo_card_markdown,
)
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_SUMMARY = REPO / "results/nano-lm/wave-at/shipapp_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shipapp-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshipapp-shipapp.md"
_LOCAL_SESSION = REPO / ".local/wave-at/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_OOD = "Which nation hosted the 2016 Summer Olympics?"
_DECODE_Q = "Explain Merkle trees briefly"


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


def _smoke_lookup(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=_KNOWN,
        root=root,
        seed=0,
        wrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipapp(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=_DECODE_Q,
        root=root,
        seed=0,
        wrap=False,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=False,
    )
    row = attach_shipapp(dict(payload))
    row["arm"] = "DECODE"
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
    row = attach_shipapp(dict(payload))
    row["arm"] = "ABSTAIN"
    row["question"] = _OOD
    return row


def _smoke_peak(*, curated: Path) -> dict[str, Any]:
    item = dict(AP0_PACK[0])
    sid = str(item["source_id"])
    meta = _BY_ID.get(sid)
    if meta is None:
        raise ValueError(f"unknown source_id: {sid}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    for _ in range(4):
        fastbase_generate(
            question=str(item["question"]), chunks=chunks, doc=doc
        )
    payload = fastbase_generate(
        question=str(item["question"]), chunks=chunks, doc=doc
    )
    row = attach_shipapp(dict(payload))
    row["arm"] = "PEAK"
    row["question"] = item["question"]
    return row


def _default_asks(*, root: Path, bank: Path) -> list[dict[str, Any]]:
    known = ask_once(
        question=_KNOWN,
        root=root,
        seed=0,
        wrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    ood = ask_once(
        question=_OOD,
        root=root,
        seed=0,
        semwrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    return [dict(known), dict(ood)]


def _apps_smoke(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    seed: int,
) -> list[dict[str, Any]]:
    questions = [p["question"] for p in APP_SMOKE_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=True,
        bank_path=bank,
        curated_root=curated,
        abstain=True,
    )
    rows: list[dict[str, Any]] = []
    for item, payload in zip(APP_SMOKE_PACK, payloads, strict=True):
        row = attach_shipapp(dict(payload))
        row["app_id"] = item["app_id"]
        row["trial_id"] = item["id"].replace("AS-APP-", "AT-APP-")
        row["question"] = item["question"]
        row["source_id"] = item["source_id"]
        rows.append(row)
    return rows


def _four_arms(*, root: Path, bank: Path, curated: Path) -> list[dict[str, Any]]:
    # Parallel LOOKUP/DECODE/ABSTAIN; PEAK is CPU-local generate.
    with ThreadPoolExecutor(max_workers=3) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode, root=root, bank=bank)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        lookup = fut_l.result()
        decode = fut_d.result()
        abstain = fut_a.result()
    peak = _smoke_peak(curated=curated)
    return [lookup, peak, decode, abstain]


def _write_public(
    *,
    decision: str,
    arms: list[dict[str, Any]],
    apps: list[dict[str, Any]],
    wall_s: float,
) -> None:
    arm_rows = [
        f"| {r['arm']} | **{r['product_mode']}** | `{r['modeui_line']}` |"
        for r in arms
    ]
    app_rows = [
        f"| {r['app_id']} | **{r['product_mode']}** | `{r['modeui_line']}` |"
        for r in apps
    ]
    body = "\n".join(
        [
            f"# H-SHIPAPP — human ask/apps/ship-demo modes (**DONE** — "
            f"{decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AT2 · Session: "
            "`.local/wave-at/SESSION.md`  ",
            "> Parent: [formal-hprodreg-prodreg.md](formal-hprodreg-prodreg.md) · "
            "Charter: AT0 SHIPAPP  ",
            "> Module: `nano_lm/src/shipapp_ops.py` · "
            "Runner: `npm run nano:shipapp`",
            "",
            "## Hypothesis",
            "",
            SHIPAPP_THESIS,
            "",
            "## Gate — ship/demo arms",
            "",
            "| Arm | product_mode | modeui_line |",
            "|-----|--------------|-------------|",
            *arm_rows,
            "",
            "## Gate — apps ask",
            "",
            "| app_id | product_mode | modeui_line |",
            "|--------|--------------|-------------|",
            *app_rows,
            "",
            f"| Modes required | **{' · '.join(REQUIRED_MODES)}** | — |",
            f"| Charter paths | {', '.join(SHIPAPP_PATHS)} | — |",
            f"| Decision | **{decision}** | 4/4 · apps labeled |",
            "",
            "## Finding",
            "",
            "1. `nano:z:ask` default path keeps LOOKUP + ABSTAIN banners.  ",
            "2. Ship/demo four-arm smoke shows LOOKUP · PEAK · DECODE · "
            "ABSTAIN.  ",
            f"3. Apps surfaces ({', '.join(APP_SURFACES)}) each emit "
            "`modeui_line`.  ",
            "4. Demo card: [shipapp-demo.md](shipapp-demo.md).  ",
            f"5. Wall ~{wall_s:.1f}s · max safe CPU (`cpus-2`); AS SHIPUI "
            "formal stays frozen.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shipapp",
            "npm run nano:z:ask -- --wrap --question \"Write a short Python "
            "function named add that returns the sum of two integers a and b.\"",
            f'npm run nano:z:ask -- --semwrap --question "{_OOD}"',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-at/shipapp_summary.json`  ",
            "- Demo: [shipapp-demo.md](shipapp-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shipapp.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {SHIPAPP_CLAIM} | Open chat / mini-AGI |",
            "| Labeled modes on ask · apps · ship/demo | Unlabeled answers |",
            "| PEAK labeled extractive | Peak-as-open-chat |",
            "",
            "Next: **AT3 H-NANOGEN4** — ablated DECODE ≥ **5.0** vs NANOGEN3 "
            "4.3.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")
    _DEMO.write_text(
        demo_card_markdown(arms=arms, apps=apps), encoding="utf-8"
    )


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AT session checklist (**OPEN** · AT2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AT **OPEN** · Caminho A ship + Nano Generative).  ",
            "> Parent: AS COMPLETE + FROZEN · Ship: **AF + AQ + AS trust "
            "path — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AT2 — H-SHIPAPP ({status})** · Next: **AT3 H-NANOGEN4**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AT OPEN** |",
            f"| Decision | **{decision}** |",
            "| Paths | nano:z:ask · apps ask · ship/demo |",
            "| Modes | LOOKUP · PEAK · DECODE · ABSTAIN |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AT0 | SESSION | **DONE — PROMOTE** |",
            "| AT1 | H-PRODREG | **DONE — PROMOTE** |",
            f"| AT2 | H-SHIPAPP | **{status}** |",
            "| AT3 | H-NANOGEN4 | **NEXT** (generative north-star gate) |",
            "| AT4 | AT-REAL-EVAL | pending |",
            "| AT5 | AT-REPORT | pending |",
            "| AT6 | AT-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    old = (
        "| AT2 | **H-SHIPAPP** | Human-facing ship/demo always shows "
        "`mode=LOOKUP\\|PEAK\\|DECODE` (+ ABSTAIN) | smoke 4/4 · no unlabeled "
        "answer | pending |"
    )
    new = (
        "| AT2 | **H-SHIPAPP** | Human-facing ship/demo always shows "
        "`mode=LOOKUP\\|PEAK\\|DECODE` (+ ABSTAIN) | smoke 4/4 · no unlabeled "
        f"answer | **DONE — {decision}** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    # Also try without escaped pipes (file may use raw |)
    old2 = (
        "| AT2 | **H-SHIPAPP** | Human-facing ship/demo always shows "
        "`mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN) | smoke 4/4 · no unlabeled "
        "answer | pending |"
    )
    new2 = (
        "| AT2 | **H-SHIPAPP** | Human-facing ship/demo always shows "
        "`mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN) | smoke 4/4 · no unlabeled "
        f"answer | **DONE — {decision}** |"
    )
    if old2 in text:
        text = text.replace(old2, new2, 1)
    marker = (
        "2. **H-PRODREG** — **DONE PROMOTE** (`npm run nano:prodreg`) · "
        "next **AT2 H-SHIPAPP**."
    )
    repl = (
        f"2. **H-SHIPAPP** — **DONE {decision}** (`npm run nano:shipapp`) · "
        "next **AT3 H-NANOGEN4**."
    )
    if marker in text:
        text = text.replace(marker, repl, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_shipapp(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AT0 SHIPAPP charter after PRODREG
    WHEN smoking ask · apps · ship/demo
    THEN PROMOTE iff 4/4 + apps labeled · no unlabeled.
    """
    del workers  # reserved; ask_many uses process threads via torch
    t0 = time.perf_counter()
    _ = load_bank_rows(bank)  # ensure bank readable
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_arms = pool.submit(
            _four_arms, root=root, bank=bank, curated=curated
        )
        fut_apps = pool.submit(
            _apps_smoke,
            root=root,
            bank=bank,
            curated=curated,
            seed=seed,
        )
        fut_def = pool.submit(_default_asks, root=root, bank=bank)
        arms = fut_arms.result()
        apps = fut_apps.result()
        defaults = fut_def.result()
    decision = decide_shipapp(arms=arms, default_asks=defaults, apps=apps)
    wall_s = time.perf_counter() - t0
    _write_public(decision=decision, arms=arms, apps=apps, wall_s=wall_s)
    _update_local_session(decision)
    _patch_pesquisa(decision)
    summary: dict[str, Any] = {
        "hyp_id": SHIPAPP_ID,
        "stage": "AT2",
        "thesis": SHIPAPP_THESIS,
        "decision": decision,
        "paths": list(SHIPAPP_PATHS),
        "required_modes": list(REQUIRED_MODES),
        "app_surfaces": list(APP_SURFACES),
        "arms": [
            {
                "arm": r["arm"],
                "product_mode": r["product_mode"],
                "modeui_line": r["modeui_line"],
                "raw_mode": r.get("mode"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in arms
        ],
        "apps": [
            {
                "app_id": r["app_id"],
                "product_mode": r["product_mode"],
                "modeui_line": r["modeui_line"],
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in apps
        ],
        "default_asks_labeled": [
            {
                "product_mode": d.get("product_mode"),
                "modeui_line": d.get("modeui_line"),
            }
            for d in defaults
        ],
        "claim": SHIPAPP_CLAIM,
        "wall_s": round(wall_s, 3),
        "public_note": "docs/results/nano-lm/formal-hshipapp-shipapp.md",
        "demo": "docs/results/nano-lm/shipapp-demo.md",
        "next": "AT3 H-NANOGEN4",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_shipapp(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            workers=workers,
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    summary["cpu_threads"] = threads
    summary["workers"] = workers
    write_json(Path(args.out), summary)
    ok = str(summary.get("decision", "")) == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": SHIPAPP_ID,
                "decision": summary.get("decision"),
                "cpu_threads": threads,
                "workers": workers,
                "wall_s": summary.get("wall_s"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
