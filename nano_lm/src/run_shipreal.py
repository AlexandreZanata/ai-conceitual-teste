"""Wave AU2 H-SHIPREAL runner (nano:shipreal) — modes + content bars."""

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

from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from prodhard_ops import KNOWN_ASK, NEAR_MISS_ASK, PEAK_ASK
from run_z_ask import ask_many, ask_once
from shipreal_ops import (
    APP_SMOKE_PACK,
    APP_SURFACES,
    REQUIRED_MODES,
    SHIPREAL_CLAIM,
    SHIPREAL_ID,
    SHIPREAL_PATHS,
    SHIPREAL_THESIS,
    arms_content_ok,
    attach_shipreal,
    content_matches_mode,
    decide_shipreal,
    demo_card_markdown,
)
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-au/shipreal_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shipreal-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshipreal-shipreal.md"
_LOCAL_SESSION = REPO / ".local/wave-au/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_BY_ID = {str(s["id"]): s for s in SOURCES}
_OOD = "Which nation hosted the 2016 Summer Olympics?"
_DECODE_Q = "Explain Merkle trees briefly"
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
    row = attach_shipreal(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode(*, root: Path, bank: Path) -> dict[str, Any]:
    # WRAP_DECODE: raw QT path is period-collapse; wrap miss still labels DECODE.
    payload = ask_once(
        question=_DECODE_Q,
        root=root,
        seed=0,
        wrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=False,
    )
    row = attach_shipreal(dict(payload))
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
    row = attach_shipreal(dict(payload))
    row["arm"] = "ABSTAIN"
    row["question"] = _OOD
    return row


def _smoke_peak(*, curated: Path) -> dict[str, Any]:
    meta = _BY_ID.get(_PEAK_SOURCE)
    if meta is None:
        raise ValueError(f"unknown source_id: {_PEAK_SOURCE}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    payload = fastbase_generate(question=PEAK_ASK, chunks=chunks, doc=doc)
    row = attach_shipreal(dict(payload))
    row["arm"] = "PEAK"
    row["question"] = PEAK_ASK
    return row


def _near_miss(*, root: Path, bank: Path) -> dict[str, Any]:
    payload = ask_once(
        question=NEAR_MISS_ASK,
        root=root,
        seed=0,
        wrap=True,
        semwrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipreal(dict(payload))
    row["arm"] = "NEAR_MISS"
    row["question"] = NEAR_MISS_ASK
    return row


def _default_asks(*, root: Path, bank: Path) -> list[dict[str, Any]]:
    known = ask_once(
        question=KNOWN_ASK,
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
    return [attach_shipreal(dict(known)), attach_shipreal(dict(ood))]


def _apps_smoke(
    *, root: Path, bank: Path, curated: Path, seed: int
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
        row = attach_shipreal(dict(payload))
        row["app_id"] = item["app_id"]
        row["trial_id"] = item["id"].replace("AS-APP-", "AU-APP-")
        row["question"] = item["question"]
        rows.append(row)
    return rows


def _four_arms(*, root: Path, bank: Path, curated: Path) -> list[dict[str, Any]]:
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
    near: dict[str, Any],
    wall_s: float,
) -> None:
    status = decision.split("(", 1)[0].strip()
    arm_rows = []
    for r in arms:
        ok = content_matches_mode(r)
        arm_rows.append(
            f"| {r['arm']} | **{r['product_mode']}** | "
            f"**{ok}** | `{str(r.get('completion', ''))[:72]}` |"
        )
    app_rows = [
        f"| {r['app_id']} | **{r['product_mode']}** | `{r['modeui_line']}` |"
        for r in apps
    ]
    body = "\n".join(
        [
            f"# H-SHIPREAL — modes + content bars (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AU2 · Session: "
            "`.local/wave-au/SESSION.md`  ",
            "> Parent: [formal-hprodhard-prodhard.md](formal-hprodhard-prodhard.md) · "
            "Charter: AU2 SHIPREAL  ",
            "> Module: `nano_lm/src/shipreal_ops.py` · "
            "Runner: `npm run nano:shipreal`",
            "",
            "## Hypothesis",
            "",
            SHIPREAL_THESIS,
            "",
            "## Gate — ship/demo arms (mode + content)",
            "",
            "| Arm | product_mode | content_ok | completion |",
            "|-----|--------------|------------|------------|",
            *arm_rows,
            "",
            "## Gate — apps ask",
            "",
            "| app_id | product_mode | modeui_line |",
            "|--------|--------------|-------------|",
            *app_rows,
            "",
            "## Near-miss (default ask)",
            "",
            f"- mode: **{near.get('product_mode')}**  ",
            f"- completion: `{str(near.get('completion', ''))[:80]}`",
            "",
            f"| Modes required | **{' · '.join(REQUIRED_MODES)}** | — |",
            f"| Charter paths | {', '.join(SHIPREAL_PATHS)} | — |",
            f"| Content bars | **{arms_content_ok(arms)}** | match mode claim |",
            f"| Decision | **{status}** | 4/4 · content · no unlabeled |",
            "",
            "## Finding",
            "",
            "1. Ship/demo four-arm smoke keeps LOOKUP · PEAK · DECODE · "
            "ABSTAIN visible.  ",
            "2. Each arm completion matches its mode claim (content bars).  ",
            "3. Apps surfaces stay labeled; known-ask LOOKUP carries usable "
            "gold.  ",
            "4. Near-miss on default ask stays ABSTAIN (AU1 hold).  ",
            "5. Demo card: [shipreal-demo.md](shipreal-demo.md).  ",
            f"6. Wall ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "7. Generative claim still locked until AU3 H-NANOGEN5.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shipreal",
            "npm run nano:prodhard",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-au/shipreal_summary.json`  ",
            "- Demo: [shipreal-demo.md](shipreal-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shipreal.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {SHIPREAL_CLAIM} | Open chat / mini-AGI |",
            "| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |",
            "| PEAK usable extractive | Peak-as-open-chat · gibberish PEAK |",
            "",
            "Next: **AU3 H-NANOGEN5** — strict ablated generative gate.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")
    _DEMO.write_text(
        demo_card_markdown(arms=arms, apps=apps).replace(
            "SHIPAPP", "SHIPREAL", 1
        ),
        encoding="utf-8",
    )


def _update_local_session(decision: str) -> None:
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave AU session checklist (**OPEN** · AU2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AU **OPEN**).  ",
            f"> Ship lock: **{SHIPREAL_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AU2 — H-SHIPREAL ({status})** · Next: **AU3 H-NANOGEN5**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AU OPEN** |",
            f"| Decision | **{decision}** |",
            "| Paths | nano:z:ask · apps ask · ship/demo |",
            "| Modes | LOOKUP · PEAK · DECODE · ABSTAIN + content |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AU0 | SESSION | **DONE — PROMOTE** |",
            "| AU1 | H-PRODHARD | **DONE — PROMOTE** |",
            f"| AU2 | H-SHIPREAL | **{status}** |",
            "| AU3 | H-NANOGEN5 | **NEXT** |",
            "| AU4 | AU-REAL-EVAL | pending |",
            "| AU5 | AU-REPORT | pending |",
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
    # Normalize any prior AU2 status cell.
    text2, n = re.subn(
        r"(\| AU2 \| \*\*H-SHIPREAL\*\* \| Human ship/demo: always "
        r"`mode=LOOKUP\\?\|PEAK\\?\|DECODE` \(\+ ABSTAIN\); answers match mode "
        r"claim \| smoke \+ content bars · no unlabeled \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2b\. \*\*AU2 H-SHIPREAL\*\* — \*\*DONE [^*]+\*\*",
        f"2b. **AU2 H-SHIPREAL** — **DONE {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    old_next = (
        "2. **AU1 H-PRODHARD** — **DONE PROMOTE** (`npm run nano:prodhard`) · "
        "next **AU2 H-SHIPREAL**.  "
    )
    new_next = (
        "2. **AU1 H-PRODHARD** — **DONE PROMOTE** (`npm run nano:prodhard`).  \n"
        f"2b. **AU2 H-SHIPREAL** — **DONE {status}** (`npm run nano:shipreal`) · "
        "next **AU3 H-NANOGEN5**.  "
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    bash_old = "# next: nano:shipreal · nano:nanogen5 (as stages land)"
    bash_new = (
        "npm run nano:shipreal\n"
        "# next: nano:nanogen5 (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def run_shipreal(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AU2 SHIPREAL charter after PRODHARD
    WHEN smoking ask · apps · ship/demo with content bars
    THEN PROMOTE/KILL per pesquisa §5 AU2.
    """
    t0 = time.perf_counter()
    # Parallel defaults / near-miss / apps; arms on main (owns inner pool).
    with ThreadPoolExecutor(max_workers=min(3, workers)) as pool:
        fut_apps = pool.submit(
            _apps_smoke, root=root, bank=bank, curated=curated, seed=0
        )
        fut_def = pool.submit(_default_asks, root=root, bank=bank)
        fut_nm = pool.submit(_near_miss, root=root, bank=bank)
        defaults = fut_def.result()
        near = fut_nm.result()
        apps = fut_apps.result()
    arms = _four_arms(root=root, bank=bank, curated=curated)
    decision = decide_shipreal(
        arms=arms,
        default_asks=defaults,
        apps=apps,
        near_miss=near,
        anti_fp_signed=True,
    )
    wall_s = time.perf_counter() - t0
    _write_public(
        decision=decision, arms=arms, apps=apps, near=near, wall_s=wall_s
    )
    _update_local_session(decision)
    _patch_pesquisa(decision)
    payload = {
        "id": SHIPREAL_ID,
        "thesis": SHIPREAL_THESIS,
        "decision": decision,
        "arms": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "content_ok": content_matches_mode(r),
                "modeui_line": r.get("modeui_line"),
                "completion": str(r.get("completion", ""))[:160],
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in arms
        ],
        "apps": [
            {
                "app_id": r.get("app_id"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
            }
            for r in apps
        ],
        "near_miss": {
            "product_mode": near.get("product_mode"),
            "completion": str(near.get("completion", ""))[:80],
        },
        "content_bars_ok": arms_content_ok(arms),
        "wall_s": wall_s,
        "workers": workers,
        "claim": SHIPREAL_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hshipreal-shipreal.md",
        "demo": "docs/results/nano-lm/shipreal-demo.md",
        "next": "AU3 H-NANOGEN5",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        # Avoid nested pool thrash: run arms on main after prep futs.
        payload = run_shipreal(
            root=Path(args.root),
            bank=Path(args.bank),
            curated=Path(args.curated),
            out=Path(args.out),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(payload.get("decision", ""))
    ok = decision.startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": SHIPREAL_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "content_bars_ok": payload.get("content_bars_ok"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
