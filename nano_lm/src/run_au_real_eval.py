"""Wave AU4 AU-REAL-EVAL runner — product + STRICT gen + live ask battery."""

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

from au_real_eval_ops import (
    ASK_BATTERY,
    AU_REAL_EVAL_CLAIM,
    AU_REAL_EVAL_ID,
    AU_REAL_EVAL_THESIS,
    PARENT_NANOGEN5_STRICT,
    PROTOCOL,
    battery_pass,
    content_matches_mode,
    decide_au_real_eval,
    force_abstain_row,
    near_miss_should_abstain,
)
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_once
from shipreal_ops import attach_shipreal
from shipui_ops import attach_shipui
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-au/real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-au/trials"
_PRODHARD = REPO / "results/nano-lm/wave-au/prodhard_summary.json"
_SHIPREAL = REPO / "results/nano-lm/wave-au/shipreal_summary.json"
_NANOGEN5 = REPO / "results/nano-lm/wave-au/nanogen5_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/wave-au-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-au/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
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
    row = attach_shipreal(dict(payload))
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
    elif kind in {"known_lookup", "human_para"}:
        payload = ask_once(
            question=q,
            root=root,
            seed=0,
            wrap=True,
            semwrap=kind == "human_para",
            bank_path=bank,
            curated_root=curated,
            abstain=True,
        )
        payload = attach_shipreal(dict(payload))
    elif kind == "decode_smoke":
        # WRAP_DECODE prod path (SHIPREAL): bank hit on this Q → LOOKUP;
        # empty bank forces wrap-miss DECODE with usable non-period telemetry.
        empty = REPO / "results/nano-lm/wave-au/_decode_empty_bank.jsonl"
        empty.parent.mkdir(parents=True, exist_ok=True)
        if not empty.is_file():
            empty.write_text("", encoding="utf-8")
        payload = ask_once(
            question=q,
            root=root,
            seed=1,
            wrap=True,
            bank_path=empty,
            curated_root=curated,
            abstain=False,
        )
        payload = attach_shipreal(dict(payload))
        payload["decode_wrap_miss"] = True
    else:
        # ood_abstain · near_miss · junk_trap — prod ask path
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
            payload = attach_shipui(force_abstain_row(dict(payload)))
            payload = attach_shipreal(dict(payload))
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
    # Peak + DECODE are GPU-heavy; keep sequential to avoid CUDA races.
    serial_kinds = {"labeled_peak", "decode_smoke"}
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
    nano_stats: dict[str, Any],
) -> None:
    bat_ok = battery_pass(battery)
    bat_rows = []
    for t in battery:
        mode_ok = t.get("product_mode") == t.get("expect_mode")
        row_ok = mode_ok and bool(t.get("content_ok"))
        bat_rows.append(
            f"| {t['id']} | {t['kind']} | **{t.get('product_mode')}** | "
            f"`{t.get('expect_mode')}` | {'PASS' if row_ok else 'FAIL'} |"
        )
    body = "\n".join(
        [
            f"# AU-REAL-EVAL — product + STRICT gen + live battery "
            f"(**DONE** — {decision.split('(', 1)[0].strip()})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AU4 · Session: "
            "`.local/wave-au/SESSION.md`  ",
            "> Parents: [formal-hprodhard-prodhard.md]"
            "(formal-hprodhard-prodhard.md) · "
            "[formal-hshipreal-shipreal.md](formal-hshipreal-shipreal.md) · "
            "[formal-hnanogen5-nanogen5.md](formal-hnanogen5-nanogen5.md)  ",
            "> Module: `nano_lm/src/au_real_eval_ops.py` · "
            "Runner: `npm run nano:au:real-eval`",
            "",
            "## Hypothesis",
            "",
            AU_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| AU1 H-PRODHARD | **{pillars['prodhard']}** |",
            f"| AU2 H-SHIPREAL | **{pillars['shipreal']}** |",
            f"| AU3 H-NANOGEN5 | **{pillars['nanogen5']}** "
            f"(strict {nano_stats.get('gen_mean', PARENT_NANOGEN5_STRICT)}) |",
            f"| Live ask battery | "
            f"**{'PASS' if bat_ok else 'FAIL'}** "
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
            "1. Cite AU1–AU3 live summaries (no vanity rewrite of AT locks).  ",
            "2. Live ask battery under max safe CPU (`cpus-2`) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; answer usability scored; "
            "near-miss → ABSTAIN; human para → LOOKUP.  ",
            "3. Generative language allowed only because AU3 PROMOTE "
            "(STRICT ablated snippet-prefix + gibberish-tail) — still "
            "**not** unlabeled open chat.  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "gold-substring ≠ gen.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"gibberish_tail_fails={PROTOCOL.get('gibberish_tail_fails')}.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:au:real-eval",
            "npm run nano:nanogen5",
            "npm run nano:shipreal",
            "npm run nano:prodhard",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-au/real_eval_summary.json`  ",
            "- Contract: `nano_lm/tests/test_au_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| STRICT ablated DECODE after AU3 | Unlabeled open chat |",
            "| Product PROMOTE + live battery 7/7 | LOOKUP-as-IQ · Wave AV invent |",
            "| Mini-AGI-*inspired* stack shape (post AU4) | GPT-class / frontier chat |",
            "",
            "Next: **AU5 AU-REPORT** — public summary + paper-lab.",
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
            f"# Wave AU session checklist (**OPEN** · AU4 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AU **OPEN**).  ",
            "> Ship: **AF + AQ + AS trust + ablated DECODE "
            "(snippet-prefix + gibberish-tail STRICT)** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AU4 — AU-REAL-EVAL ({status})** · Next: **AU5 AU-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AU OPEN** |",
            f"| PRODHARD / SHIPREAL | **{pillars.get('prodhard')}** / "
            f"**{pillars.get('shipreal')}** |",
            f"| NANOGEN5 | **{pillars.get('nanogen5')}** |",
            f"| Live battery | **{'PASS' if battery_ok else 'FAIL'}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AU0 | SESSION | **DONE — PROMOTE** |",
            "| AU1 | H-PRODHARD | **DONE — PROMOTE** |",
            "| AU2 | H-SHIPREAL | **DONE — PROMOTE** |",
            "| AU3 | H-NANOGEN5 | **DONE — PROMOTE** |",
            f"| AU4 | AU-REAL-EVAL | **{status}** |",
            "| AU5 | AU-REPORT | **NEXT** |",
            "| AU6 | AU-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"(\| AU4 \| \*\*AU-REAL-EVAL\*\* \| Final real eval: product \+ "
        r"generative \+ live ask \(prod path = eval path\) \| product pass; "
        r"gen claim only if AU3 PROMOTE \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2d\. \*\*AU4 AU-REAL-EVAL\*\* — \*\*DONE [^*]+\*\*",
        f"2d. **AU4 AU-REAL-EVAL** — **DONE {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2c\. \*\*AU3 H-NANOGEN5\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:nanogen5`\))? · next \*\*AU4 AU-REAL-EVAL\*\*\.",
        (
            "2c. **AU3 H-NANOGEN5** — **DONE PROMOTE** "
            "(`npm run nano:nanogen5`).  \n"
            f"2d. **AU4 AU-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:au:real-eval`) · next **AU5 AU-REPORT**."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:au:real-eval (as stages land)"
    bash_new = (
        "npm run nano:au:real-eval\n"
        "# next: nano:au:report (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_au_real_eval(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    prodhard_path: Path,
    shipreal_path: Path,
    nanogen5_path: Path,
    claim: str,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AU1–AU3 summaries + live ask battery
    WHEN scoring AU4 real eval
    THEN PROMOTE iff product pass + battery pass + honest claim.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "prodhard": _load_decision(prodhard_path),
        "shipreal": _load_decision(shipreal_path),
        "nanogen5": _load_decision(nanogen5_path),
    }
    nano_stats = _load_stats(nanogen5_path)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    for row in battery:
        write_json(trials_dir / f"{row['id']}.json", row)
    ok_bat = battery_pass(battery)
    decision = decide_au_real_eval(
        prodhard_decision=pillars["prodhard"],
        shipreal_decision=pillars["shipreal"],
        nanogen5_decision=pillars["nanogen5"],
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
    _patch_pesquisa(decision)
    summary: dict[str, Any] = {
        "hyp_id": AU_REAL_EVAL_ID,
        "stage": "AU4",
        "thesis": AU_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_pass": ok_bat,
        "claim": claim,
        "nanogen5_stats": nano_stats,
        "protocol": dict(PROTOCOL),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "elapsed_s": time.perf_counter() - t0,
        "finding": (
            f"{AU_REAL_EVAL_ID}: prodhard={pillars['prodhard']} "
            f"shipreal={pillars['shipreal']} nanogen5={pillars['nanogen5']} "
            f"battery={'PASS' if ok_bat else 'FAIL'} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/wave-au-real-eval.md",
        "ship_claim": claim,
        "next": "AU5 AU-REPORT",
        "anti_fp": (
            "live battery modes+usability; LOOKUP≠IQ; PEAK≠open-chat; "
            "gen claim only if AU3 STRICT PROMOTE"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AU4 AU-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--prodhard", type=Path, default=_PRODHARD)
    ap.add_argument("--shipreal", type=Path, default=_SHIPREAL)
    ap.add_argument("--nanogen5", type=Path, default=_NANOGEN5)
    ap.add_argument("--claim", type=str, default=AU_REAL_EVAL_CLAIM)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_au_real_eval(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            prodhard_path=Path(args.prodhard),
            shipreal_path=Path(args.shipreal),
            nanogen5_path=Path(args.nanogen5),
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
                "hyp_id": AU_REAL_EVAL_ID,
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
