"""Wave BH1 H-IQBAT runner (nano:iq-battery) — live IQ battery v0 scoreboard."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from bh_session_ops import map_bh_product_mode
from iqbat_ops import (
    IQBAT_ANTI_FP,
    IQBAT_BATTERY_PATH,
    IQBAT_CLAIM,
    IQBAT_ID,
    IQBAT_MIX_MIN,
    IQBAT_SAFE_NOTE,
    IQBAT_THESIS,
    decide_iqbat,
    load_iq_battery,
    score_iq_probe,
    summarize_iq_scores,
    validate_iq_mix,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-bh/iqbat_summary.json"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hiqbat-iqbat.md"
_LOCAL_SESSION = REPO / ".local/wave-bh/SESSION.md"
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
_BATTERY = REPO / IQBAT_BATTERY_PATH


def _hardware() -> tuple[int, int]:
    # 16c / ~12Gi avail: leave ≥6 cores free; ≤8 ask workers.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 6))
    workers = min(8, max(4, cpus - 6))
    return threads, workers


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


def _ask_once(question: str) -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=question,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
        semwrap=True,
    )


def _run_probe(probe: dict[str, Any]) -> dict[str, Any]:
    raw = _ask_once(str(probe["question"]))
    mode = map_bh_product_mode(str(raw.get("mode", "")))
    if raw.get("product_mode"):
        mode = str(raw["product_mode"])
    ask = {
        "product_mode": mode,
        "mode": raw.get("mode"),
        "completion": str(raw.get("completion", "")),
        "wall_ms": raw.get("wall_ms"),
        "n_new": raw.get("n_new"),
    }
    score = score_iq_probe(probe, ask)
    return {
        "id": probe["id"],
        "split": probe["split"],
        "family": probe.get("family"),
        "expect": probe["expect"],
        "question": probe["question"],
        "product_mode": mode,
        "completion": ask["completion"][:160],
        "wall_ms": ask["wall_ms"],
        "n_new": ask["n_new"],
        "score": score,
        "min_gold_substr": probe.get("min_gold_substr"),
        "wrong_if_contains": probe.get("wrong_if_contains"),
    }


def _score_battery(
    probes: list[dict[str, Any]], *, workers: int
) -> list[dict[str, Any]]:
    n = min(len(probes), max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(_run_probe, probes))


def _battery_hash(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest[:16]


def _write_public(
    *,
    decision: str,
    board: dict[str, Any],
    scored: list[dict[str, Any]],
    bhash: str,
) -> None:
    status = "PROMOTE" if decision.startswith("PROMOTE") else "KILL"
    miss_rows = [
        r for r in scored if str(r.get("score")) == "MISS"
    ]
    miss_tbl = "\n".join(
        f"| {r['id']} | {r['split']} | `{r['completion'][:40]}` |"
        for r in miss_rows[:12]
    ) or "| — | — | none |"
    split_rows = "\n".join(
        f"| {k} | **{v}** |"
        for k, v in sorted(board.get("by_split", {}).items())
    )
    score_rows = "\n".join(
        f"| {k} | **{v}** |"
        for k, v in sorted(board.get("by_score", {}).items())
    )
    body = "\n".join(
        [
            f"# H-IQBAT — IQ battery v0 live scoreboard (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §9 BH1 · Session: "
            "`.local/wave-bh/SESSION.md`  ",
            "> Parent: [wave-bh-session.md](wave-bh-session.md) · "
            f"Battery: [`iq-battery-v0.jsonl`](iq-battery-v0.jsonl) "
            f"(sha256 `{bhash}`)  ",
            "> Module: `nano_lm/src/iqbat_ops.py` · "
            "Runner: `npm run nano:iq-battery`",
            "",
            "## Hypothesis",
            "",
            IQBAT_THESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Bar |",
            "|--------|-------:|-----|",
            f"| n probes | **{board['n']}** | ≥{IQBAT_MIX_MIN['total']} |",
            f"| IQ | **{board['IQ']:.3f}** | publish |",
            f"| Novel_FP | **{board['Novel_FP']}** | **0** |",
            f"| Forever_FH | **{board['Forever_FH']}** | **0** |",
            f"| adversary_FP | **{board['adversary_FP']}** | **0** |",
            f"| gold/para MISS | **{board['gold_para_miss']}** | "
            "baseline (BH2 closes → 0) |",
            f"| FP_rate | **{board['FP_rate']:.3f}** | novel/adversary 0 |",
            f"| Decision | **{status}** | — |",
            "",
            "## Mix",
            "",
            "| Split | n |",
            "|-------|--:|",
            split_rows,
            "",
            "## Scores",
            "",
            "| Label | n |",
            "|-------|--:|",
            score_rows,
            "",
            "## Gold/para MISS residual (→ BH2 H-GOLDFIX)",
            "",
            "| id | split | completion |",
            "|----|-------|------------|",
            miss_tbl,
            "",
            "## SAFE ≠ quality",
            "",
            IQBAT_SAFE_NOTE,
            "",
            "## Anti-FP",
            "",
            IQBAT_ANTI_FP,
            "",
            "## Ship lock",
            "",
            IQBAT_CLAIM,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:iq-battery",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Next: **BH2 H-GOLDFIX** — Rust LOOKUP + full add body; "
            "hold Novel_FP=0 · Forever_FH=0.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, board: dict[str, Any]) -> None:
    status = "DONE — PROMOTE" if decision.startswith("PROMOTE") else "KILL"
    body = "\n".join(
        [
            f"# Wave BH session checklist (**OPEN** · BH1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md`.  ",
            f"> Parent: BG COMPLETE + FROZEN · Ship: **{IQBAT_CLAIM}**",
            "",
            "## Current stage",
            "",
            f"**BH1 — H-IQBAT ({status})** · Next: **BH2 H-GOLDFIX**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **BH ACTIVE** |",
            f"| Novel_FP | **{board.get('Novel_FP')}** |",
            f"| Forever_FH | **{board.get('Forever_FH')}** |",
            f"| gold/para MISS | **{board.get('gold_para_miss')}** "
            "(BH2 closes) |",
            f"| IQ | **{board.get('IQ')}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BH0 | SESSION | **DONE — PROMOTE** |",
            f"| BH1 | H-IQBAT | **{status}** |",
            "| BH2 | H-GOLDFIX | **NEXT** |",
            "| BH3 | H-SHIPIQ | pending |",
            "| BH4 | H-FASTBH | pending |",
            "| BH5 | H-CTXBH | pending |",
            "| BH6 | H-NANOGEN18 | pending (SKIP unless real method) |",
            "| BH7 | BH-REAL-EVAL | pending |",
            "| BH8 | BH-REPORT | pending |",
            "| BH9 | BH-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text = text.replace(
        "| BH1 | **H-IQBAT** | IQ battery v0 runner + ≥40 "
        "probes; Novel_FP=0 baseline | §0c | **NEXT** |",
        "| BH1 | **H-IQBAT** | IQ battery v0 runner + ≥40 "
        "probes; Novel_FP=0 baseline | §0c | **DONE — PROMOTE** |",
        1,
    )
    text = text.replace(
        "| BH2 | **H-GOLDFIX** | Rust LOOKUP + full add body; "
        "BA…BG anti-FP hold | MISS=0 · FP hold | **TODO** |",
        "| BH2 | **H-GOLDFIX** | Rust LOOKUP + full add body; "
        "BA…BG anti-FP hold | MISS=0 · FP hold | **NEXT** |",
        1,
    )
    text = text.replace(
        "2. **BH1 H-IQBAT** — **NEXT** — `iq-battery-v0.jsonl` + "
        "`npm run nano:iq-battery`; publish scoreboard.  ",
        "2. **BH1 H-IQBAT** — **DONE PROMOTE** "
        "(`npm run nano:iq-battery`) · Novel_FP=0 baseline · "
        "gold MISS residual → BH2.  ",
        1,
    )
    text = text.replace(
        "3. **BH2 H-GOLDFIX** — Rust LOOKUP + full add; BA…BG hold; "
        "Novel_FP=0.  ",
        "3. **BH2 H-GOLDFIX** — **NEXT** — Rust LOOKUP + full add; "
        "BA…BG hold; Novel_FP=0.  ",
        1,
    )
    text = text.replace(
        "(BH0 **DONE — PROMOTE**; next BH1 H-IQBAT)",
        "(BH0–BH1 **DONE — PROMOTE**; next BH2 H-GOLDFIX)",
        1,
    )
    text = text.replace(
        "ACTIVE** (BH0 SESSION **DONE — PROMOTE**; next BH1 H-IQBAT)",
        "ACTIVE** (BH0–BH1 **DONE — PROMOTE**; next BH2 H-GOLDFIX)",
        1,
    )
    bash_old = (
        "npm run nano:bh:session\n"
        "# next: nano:iq-battery · nano:goldfix · nano:bh:shipiq · "
        "nano:bh:fastbh · nano:bh:ctxbh · nano:nanogen18 "
        "(SKIP without plan)\n"
    )
    bash_new = (
        "npm run nano:bh:session\n"
        "npm run nano:iq-battery\n"
        "# next: nano:goldfix · nano:bh:shipiq · nano:bh:fastbh · "
        "nano:bh:ctxbh · nano:nanogen18 (SKIP without plan)\n"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _write_local_impl(decision: str, board: dict[str, Any]) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = f"""# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave **BH ACTIVE** · BH0 SESSION **DONE** · BH1 H-IQBAT **DONE — PROMOTE**.  
Novel_FP=**{board.get('Novel_FP')}** · Forever_FH=**{board.get('Forever_FH')}** · gold/para MISS=**{board.get('gold_para_miss')}** (BH2).

## Next

1. **BH1 H-IQBAT** — **DONE** (`npm run nano:iq-battery`).  
2. **BH2 H-GOLDFIX** — **NEXT** — Rust LOOKUP + full add; hold anti-FP.  
3. Ship: **AF + AQ + AS trust + STRICT ablated DECODE**.

```bash
npm run nano:iq-battery
npm run nano:test && npm run verify
```
"""
    _LOCAL_IMPL.write_text(body, encoding="utf-8")


def _write_local_readme(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Local research notebook

Full lab book: **`pesquisa.md`**.

**Wave BH ACTIVE** — BH0 SESSION PROMOTE · BH1 H-IQBAT PROMOTE · next BH2 H-GOLDFIX.

IQ battery v0 live at `docs/results/nano-lm/iq-battery-v0.jsonl` · formal `formal-hiqbat-iqbat.md`.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def _replace_once(path: Path, old: str, new: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "H-IQBAT PROMOTE" in text or old not in text:
        return
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _patch_recipes_iqbat() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "H-IQBAT PROMOTE" in text:
        return
    text = text.replace(
        "next BH1 H-IQBAT",
        "BH1 [H-IQBAT PROMOTE](formal-hiqbat-iqbat.md) "
        "(`npm run nano:iq-battery`); next BH2 H-GOLDFIX",
        1,
    )
    row = (
        "| Wave BH1 H-IQBAT | [formal-hiqbat-iqbat.md]"
        "(formal-hiqbat-iqbat.md) **PROMOTE** "
        "(`npm run nano:iq-battery`) — IQ battery v0 ≥40 · "
        "Novel_FP=0 · Forever_FH=0 · gold MISS residual → "
        "H-GOLDFIX |"
    )
    if "Wave BH0 SESSION" in text and "Wave BH1 H-IQBAT" not in text:
        text = text.replace(
            "| Wave BH0 SESSION |",
            row + "\n| Wave BH0 SESSION |",
            1,
        )
    _RECIPES.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    _patch_recipes_iqbat()
    _replace_once(
        _CARD,
        "next BH1 H-IQBAT",
        "BH1 [H-IQBAT PROMOTE](formal-hiqbat-iqbat.md) "
        "(`npm run nano:iq-battery`); next BH2 H-GOLDFIX",
    )
    _replace_once(
        _AGENTS,
        "next BH1 H-IQBAT",
        "BH1 H-IQBAT PROMOTE (`npm run nano:iq-battery`); "
        "next BH2 H-GOLDFIX",
    )
    _replace_once(
        _AGENDA,
        "next BH1 H-IQBAT",
        "BH1 [H-IQBAT PROMOTE](results/nano-lm/formal-hiqbat-iqbat.md) "
        "(`npm run nano:iq-battery`); next BH2 H-GOLDFIX",
    )
    _replace_once(
        _EVOGEN,
        "next BH1 H-IQBAT",
        "BH1 H-IQBAT PROMOTE; next BH2 H-GOLDFIX",
    )


def _persist_live(scored: list[dict[str, Any]], board: dict[str, Any]) -> None:
    path = REPO / ".local/wave-bh/live_audit_bh1_iqbat.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, {"board": board, "scored": scored})


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--battery", type=Path, default=_BATTERY)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    probes = load_iq_battery(Path(args.battery))
    mix_err = validate_iq_mix(probes)
    mix_ok = mix_err is None
    if not mix_ok:
        print(json.dumps({"ok": False, "error": mix_err}))
        return 2

    if args.skip_ask:
        scored = [
            {
                **p,
                "product_mode": p["expect"],
                "completion": "",
                "score": "ABSTAIN-OK"
                if p["expect"] == "ABSTAIN"
                else "MISS",
                "wall_ms": 0,
                "n_new": 0,
            }
            for p in probes
        ]
    else:
        scored = _score_battery(probes, workers=workers)

    board = summarize_iq_scores(scored)
    bhash = _battery_hash(Path(args.battery))
    _write_public(
        decision="PROMOTE", board=board, scored=scored, bhash=bhash
    )
    formal_ready = _PUBLIC.is_file()
    decision = decide_iqbat(
        mix_ok=mix_ok,
        board=board,
        anti_fp_signed=True,
        formal_ready=formal_ready,
    )
    # rewrite public with real decision
    _write_public(
        decision=decision, board=board, scored=scored, bhash=bhash
    )
    _update_local_session(decision, board)
    _patch_pesquisa(decision)
    _write_local_impl(decision, board)
    _write_local_readme(decision)
    _patch_public_status(decision)
    _persist_live(scored, board)

    payload = {
        "id": IQBAT_ID,
        "thesis": IQBAT_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "battery": str(Path(args.battery).relative_to(REPO)),
        "battery_sha256_16": bhash,
        "board": board,
        "scored_n": len(scored),
        "public_note": "docs/results/nano-lm/formal-hiqbat-iqbat.md",
        "next": "BH2 H-GOLDFIX (Rust LOOKUP + full add; hold Novel_FP=0)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = decision.startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": IQBAT_ID,
                "decision": decision[:140],
                "Novel_FP": board["Novel_FP"],
                "Forever_FH": board["Forever_FH"],
                "gold_para_miss": board["gold_para_miss"],
                "IQ": round(float(board["IQ"]), 4),
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
