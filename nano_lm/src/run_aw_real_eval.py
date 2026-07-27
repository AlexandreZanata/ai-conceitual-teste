"""Wave AW4 AW-REAL-EVAL runner — product keep + live ask; gen if NANOGEN7 PROMOTE."""

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

from aw_real_eval_ops import (
    ASK_BATTERY,
    AW_REAL_EVAL_CLAIM,
    AW_REAL_EVAL_ID,
    AW_REAL_EVAL_THESIS,
    PROTOCOL,
    battery_pass,
    battery_row_ok,
    content_matches_mode,
    decide_aw_real_eval,
    force_abstain_row,
    near_miss_should_abstain,
)
from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from run_z_ask import ask_once
from shipkeep_ops import attach_shipkeep
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-aw/real_eval_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-aw/trials"
_PRODKEEP = REPO / "results/nano-lm/wave-aw/prodkeep_summary.json"
_SHIPKEEP = REPO / "results/nano-lm/wave-aw/shipkeep_summary.json"
_NANOGEN7 = REPO / "results/nano-lm/wave-aw/nanogen7_summary.json"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-aw/_decode_empty_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-aw-real-eval.md"
_LOCAL_SESSION = REPO / ".local/wave-aw/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
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
    # Max safe on 16c: leave 2 cores; cap workers to avoid thrash.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
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
    row = attach_shipkeep(dict(payload))
    row["question"] = question
    return row


def _decode_row(*, root: Path, curated: Path, question: str) -> dict[str, Any]:
    """WRAP_DECODE empty-bank path — junk must ABSTAIN (DECODE content law)."""
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
    row = attach_shipkeep(dict(payload))
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
        payload = attach_shipkeep(dict(payload))
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
        payload = attach_shipkeep(dict(payload))
        if kind == "near_miss" and near_miss_should_abstain(
            question=q,
            completion=str(payload.get("completion", "")),
            product_mode=str(payload.get("product_mode", "")),
        ):
            payload = attach_shipkeep(force_abstain_row(dict(payload)))
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
    # Peak + DECODE are model-heavy; keep sequential to avoid races.
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
    nano_stats: dict[str, Any],
) -> None:
    bat_ok = battery_pass(battery)
    bat_rows = []
    for t in battery:
        row_ok = battery_row_ok(t)
        bat_rows.append(
            f"| {t['id']} | {t['kind']} | **{t.get('product_mode')}** | "
            f"`{t.get('expect_mode')}` | {'PASS' if row_ok else 'FAIL'} |"
        )
    body = "\n".join(
        [
            f"# AW-REAL-EVAL — product keep + live battery "
            f"(**DONE** — {decision.split('(', 1)[0].strip()})",
            "",
            "> Lab: `.local/pesquisa.md` §2 AW4 · Session: "
            "`.local/wave-aw/SESSION.md`  ",
            "> Parents: [formal-hprodkeep-prodkeep.md]"
            "(formal-hprodkeep-prodkeep.md) · "
            "[formal-hshipkeep-shipkeep.md](formal-hshipkeep-shipkeep.md) · "
            "[formal-hnanogen7-nanogen7.md](formal-hnanogen7-nanogen7.md)  ",
            "> Module: `nano_lm/src/aw_real_eval_ops.py` · "
            "Runner: `npm run nano:aw:real-eval`",
            "",
            "## Hypothesis",
            "",
            AW_REAL_EVAL_THESIS,
            "",
            "## Gate",
            "",
            "| Pillar | Decision |",
            "|--------|----------|",
            f"| AW1 H-PRODKEEP | **{pillars['prodkeep']}** |",
            f"| AW2 H-SHIPKEEP | **{pillars['shipkeep']}** |",
            f"| AW3 H-NANOGEN7 | **{pillars['nanogen7']}** "
            f"(true_continue / gen_mean "
            f"{nano_stats.get('true_continue', nano_stats.get('gen_mean', 'n/a'))}"
            f") |",
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
            "1. Cite AW1–AW3 live summaries (no vanity rewrite of AV/AU locks).  ",
            "2. Live ask battery under max safe CPU (`cpus-2`) — modes labeled; "
            "`wall_ms`/`n_new` mandatory; answer usability scored; "
            "near-miss → ABSTAIN; DECODE junk → ABSTAIN (content law); "
            "human para → LOOKUP.  ",
            "3. Generative / TAC true-continue unlock **locked** because AW3 HOLD "
            "(span-fallback ≠ gen IQ) — ship stays AV STRICT archive, "
            "**not** unlabeled open chat.  ",
            "4. LOOKUP ≠ IQ · PEAK ≠ open-chat · SAFE ≠ quality · "
            "gold-substring / truncate-to-span ≠ gen.  ",
            f"5. Protocol: live_ask={PROTOCOL.get('live_ask_battery')} · "
            f"eval_eq_prod={PROTOCOL.get('eval_eq_prod_ask')} · "
            f"span_fallback_neq_gen={PROTOCOL.get('span_fallback_neq_gen')}.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:aw:real-eval",
            "npm run nano:nanogen7",
            "npm run nano:shipkeep",
            "npm run nano:prodkeep",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-aw/real_eval_summary.json`  ",
            "- Contract: `nano_lm/tests/test_aw_real_eval.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| Product PROMOTE + live battery 8/8 | Unlabeled open chat |",
            "| AV STRICT ship lock while AW3 HOLD | TAC unlock on HOLD |",
            "| DECODE usable or ABSTAIN | LOOKUP-as-IQ · Wave AX invent |",
            "",
            "Next: **AW5 AW-REPORT** — public summary + paper-lab.",
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
            f"# Wave AW session checklist (**OPEN** · AW4 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AW **OPEN**).  ",
            "> Ship: **AF + AQ + AS trust + ablated DECODE "
            "(snippet-prefix + gibberish-tail STRICT)** · ≤5M "
            "(no TAC true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AW4 — AW-REAL-EVAL ({status})** · Next: **AW5 AW-REPORT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AW OPEN** |",
            f"| PRODKEEP / SHIPKEEP | **{pillars.get('prodkeep')}** / "
            f"**{pillars.get('shipkeep')}** |",
            f"| NANOGEN7 | **{pillars.get('nanogen7')}** |",
            f"| Live battery | **{'PASS' if battery_ok else 'FAIL'}** |",
            f"| Decision | **{decision}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AW0 | SESSION | **DONE — PROMOTE** |",
            "| AW1 | H-PRODKEEP | **DONE — PROMOTE** |",
            "| AW2 | H-SHIPKEEP | **DONE — PROMOTE** |",
            "| AW3 | H-NANOGEN7 | **DONE — HOLD** |",
            f"| AW4 | AW-REAL-EVAL | **{status}** |",
            "| AW5 | AW-REPORT | **NEXT** |",
            "| AW6 | AW-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    status = decision.split("(", 1)[0].strip()
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2c. **AW3 H-NANOGEN7** — **DONE HOLD** "
            "(`npm run nano:nanogen7`) · next **AW4 AW-REAL-EVAL**."
        )
        new = (
            "2c. **AW3 H-NANOGEN7** — **DONE HOLD** "
            "(`npm run nano:nanogen7`).  \n"
            f"2d. **AW4 AW-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:aw:real-eval`) · next **AW5 AW-REPORT**."
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-aw/SESSION.md` (AW3 H-NANOGEN7 **DONE — HOLD**; "
            "next AW4 AW-REAL-EVAL)."
        )
        new = (
            f"Session: `wave-aw/SESSION.md` (AW4 AW-REAL-EVAL "
            f"**DONE — {status}**; next AW5 AW-REPORT)."
        )
        if old in text:
            _LOCAL_README.write_text(
                text.replace(old, new, 1), encoding="utf-8"
            )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    text2, n = re.subn(
        r"(\| AW4 \| \*\*AW-REAL-EVAL\*\* \| Final real eval: product \+ "
        r"generative \+ live ask \| product pass; "
        r"gen claim only if AW3 PROMOTE \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2c\. \*\*AW3 H-NANOGEN7\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:nanogen7`\))? · next \*\*AW4 AW-REAL-EVAL\*\*\.",
        (
            "2c. **AW3 H-NANOGEN7** — **DONE HOLD** "
            "(`npm run nano:nanogen7`).  \n"
            f"2d. **AW4 AW-REAL-EVAL** — **DONE {status}** "
            "(`npm run nano:aw:real-eval`) · next **AW5 AW-REPORT**."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:aw:real-eval"
    bash_new = (
        "npm run nano:aw:real-eval\n"
        "# next: nano:aw:report"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(decision)


def run_aw_real_eval(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    trials_dir: Path,
    prodkeep_path: Path,
    shipkeep_path: Path,
    nanogen7_path: Path,
    claim: str,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AW1–AW3 summaries + live ask battery
    WHEN scoring AW4 real eval
    THEN PROMOTE iff product pass + battery pass + honest claim.
    """
    t0 = time.perf_counter()
    trials_dir.mkdir(parents=True, exist_ok=True)
    pillars = {
        "prodkeep": _load_decision(prodkeep_path),
        "shipkeep": _load_decision(shipkeep_path),
        "nanogen7": _load_decision(nanogen7_path),
    }
    nano_stats = _load_stats(nanogen7_path)
    battery = _run_battery(
        root=root, bank=bank, curated=curated, workers=workers
    )
    for row in battery:
        write_json(trials_dir / f"{row['id']}.json", row)
    ok_bat = battery_pass(battery)
    decision = decide_aw_real_eval(
        prodkeep_decision=pillars["prodkeep"],
        shipkeep_decision=pillars["shipkeep"],
        nanogen7_decision=pillars["nanogen7"],
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
        "hyp_id": AW_REAL_EVAL_ID,
        "stage": "AW4",
        "thesis": AW_REAL_EVAL_THESIS,
        "decision": decision,
        "pillars": pillars,
        "battery": battery,
        "battery_pass": ok_bat,
        "claim": claim,
        "nanogen7_stats": nano_stats,
        "protocol": dict(PROTOCOL),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "elapsed_s": time.perf_counter() - t0,
        "finding": (
            f"{AW_REAL_EVAL_ID}: prodkeep={pillars['prodkeep']} "
            f"shipkeep={pillars['shipkeep']} nanogen7={pillars['nanogen7']} "
            f"battery={'PASS' if ok_bat else 'FAIL'} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/wave-aw-real-eval.md",
        "ship_claim": claim,
        "next": "AW5 AW-REPORT",
        "anti_fp": (
            "live battery modes+usability; LOOKUP≠IQ; PEAK≠open-chat; "
            "span-fallback≠gen; TAC unlock only if AW3 PROMOTE"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AW4 AW-REAL-EVAL")
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--prodkeep", type=Path, default=_PRODKEEP)
    ap.add_argument("--shipkeep", type=Path, default=_SHIPKEEP)
    ap.add_argument("--nanogen7", type=Path, default=_NANOGEN7)
    ap.add_argument("--claim", type=str, default=AW_REAL_EVAL_CLAIM)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_aw_real_eval(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            prodkeep_path=Path(args.prodkeep),
            shipkeep_path=Path(args.shipkeep),
            nanogen7_path=Path(args.nanogen7),
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
                "hyp_id": AW_REAL_EVAL_ID,
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
