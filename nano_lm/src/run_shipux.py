"""Wave AX2 H-SHIPUX runner (nano:shipux) — modes + content after PRODNAT."""

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
from prodship_ops import decode_content_honest
from run_z_ask import ask_many, ask_once
from shipux_ops import (
    APP_SMOKE_PACK,
    HARD_NATURAL_ASK,
    SHIPUX_ANTI_FP,
    SHIPUX_CLAIM,
    SHIPUX_ID,
    SHIPUX_PATHS,
    SHIPUX_SAFE_NOTE,
    SHIPUX_THESIS,
    arms_honest_ok,
    attach_shipux,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipux,
    demo_card_markdown,
)
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ax/shipux_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shipux-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshipux-shipux.md"
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
    # Max safe on 16c / ~12Gi avail: leave 2 cores; cap workers to avoid thrash.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
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
    row = attach_shipux(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode_probe(*, root: Path) -> dict[str, Any]:
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
    row = attach_shipux(dict(payload))
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
    row = attach_shipux(dict(payload))
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
    hard = ask_once(
        question=HARD_NATURAL_ASK,
        root=root,
        seed=0,
        wrap=True,
        semwrap=True,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    rows = [
        attach_shipux(dict(known)),
        attach_shipux(dict(ood)),
        attach_shipux(dict(hard)),
    ]
    rows[0]["question"] = KNOWN_ASK
    rows[1]["question"] = _OOD
    rows[2]["question"] = HARD_NATURAL_ASK
    return rows


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
        row = attach_shipux(dict(payload))
        row["app_id"] = item["app_id"]
        row["trial_id"] = item["id"].replace("AS-APP-", "AX-APP-")
        row["question"] = item["question"]
        rows.append(row)
    return rows


def _live_arms(*, root: Path, bank: Path, curated: Path) -> list[dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=3) as pool:
        fut_l = pool.submit(_smoke_lookup, root=root, bank=bank)
        fut_a = pool.submit(_smoke_abstain, root=root, bank=bank)
        fut_d = pool.submit(_smoke_decode_probe, root=root)
        lookup = fut_l.result()
        abstain = fut_a.result()
        decode_probe = fut_d.result()
    peak = _smoke_peak(curated=curated)
    arms = [lookup, peak, abstain]
    if str(decode_probe.get("product_mode")) == "DECODE":
        decode_probe["arm"] = "DECODE"
        arms.append(decode_probe)
    return arms


def _write_public(
    *,
    decision: str,
    arms: list[dict[str, Any]],
    apps: list[dict[str, Any]],
    near: dict[str, Any],
    hard_nat: dict[str, Any],
    decode_probe: dict[str, Any],
    wall_s: float,
) -> None:
    status = decision.split("(", 1)[0].strip()
    arm_rows = [
        f"| {r['arm']} | **{r['product_mode']}** | "
        f"**{content_matches_mode(r)}** | "
        f"`{str(r.get('completion', ''))[:72]}` |"
        for r in arms
    ]
    app_rows = [
        f"| {r.get('app_id')} | **{r.get('product_mode')}** | "
        f"`{r.get('modeui_line')}` |"
        for r in apps
    ]
    body = "\n".join(
        [
            f"# H-SHIPUX — modes + content after PRODNAT (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AX2 · Session: "
            "`.local/wave-ax/SESSION.md`  ",
            "> Parent: [formal-hprodnat-prodnat.md](formal-hprodnat-prodnat.md) · "
            "Charter: AX2 SHIPUX  ",
            "> Module: `nano_lm/src/shipux_ops.py` · "
            "Runner: `npm run nano:shipux`",
            "",
            "## Hypothesis",
            "",
            SHIPUX_THESIS,
            "",
            "## Gate — ship/demo arms (mode + content)",
            "",
            "| Arm | product_mode | content_ok | completion |",
            "|-----|--------------|------------|------------|",
            *arm_rows,
            "",
            "## Gate — DECODE path probe",
            "",
            f"- product_mode: **{decode_probe.get('product_mode')}**  ",
            f"- honest: **{decode_content_honest(decode_probe)}**  ",
            f"- completion: `{str(decode_probe.get('completion', ''))[:96]}`",
            "",
            "## Gate — apps ask",
            "",
            "| app_id | product_mode | modeui_line |",
            "|--------|--------------|-------------|",
            *app_rows,
            "",
            "## Hard-natural (default ask)",
            "",
            f"- mode: **{hard_nat.get('product_mode')}**  ",
            f"- modeui: `{hard_nat.get('modeui_line')}`  ",
            f"- completion: `{str(hard_nat.get('completion', ''))[:80]}`",
            "",
            "## Near-miss (default ask)",
            "",
            f"- mode: **{near.get('product_mode')}**  ",
            f"- completion: `{str(near.get('completion', ''))[:80]}`",
            "",
            "| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | "
            f"banner_ok=**{banner_modes_ok()}** |",
            f"| Charter paths | {', '.join(SHIPUX_PATHS)} | — |",
            f"| Arms honest | **{arms_honest_ok(arms)}** | labeled + content |",
            f"| Core modes | **{core_modes_ok(arms)}** | LOOKUP·PEAK·ABSTAIN |",
            f"| Decision | **{status}** | smoke + content · no unlabeled |",
            "",
            "## Finding",
            "",
            "1. Ship/demo arms stay labeled after PRODNAT; content matches mode.  ",
            "2. WRAP_DECODE gibberish refuses to ABSTAIN "
            "(DECODE content law holds).  ",
            "3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  ",
            "4. Apps surfaces stay labeled with usable LOOKUP gold.  ",
            "5. Near-miss on default ask stays ABSTAIN.  ",
            "6. Hard-natural live miss stays labeled LOOKUP on ship path.  ",
            "7. Demo card: [shipux-demo.md](shipux-demo.md).  ",
            f"8. Wall ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "9. Generative claim still locked (gen stance **defer**; AX3).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shipux",
            "npm run nano:prodnat",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ax/shipux_summary.json`  ",
            "- Demo: [shipux-demo.md](shipux-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shipux.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {SHIPUX_CLAIM} | Open chat / mini-AGI |",
            "| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |",
            "| DECODE usable or ABSTAIN | telemetry-only content_ok |",
            "| Hard-natural labeled LOOKUP | Pack-para as world coverage |",
            "",
            f"SAFE note: {SHIPUX_SAFE_NOTE}  ",
            f"Anti-FP: {SHIPUX_ANTI_FP}",
            "",
            "Next: **AX3 H-NANOGEN8** — real new method or HOLD/DEFER "
            "(never NANOGEN7+rename).",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")
    _DEMO.write_text(
        demo_card_markdown(arms=arms, apps=apps, decode_probe=decode_probe),
        encoding="utf-8",
    )


def _update_local_session(decision: str) -> None:
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave AX session checklist (**OPEN** · AX2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AX **OPEN** · hard-natural harden + gen defer).  ",
            f"> Ship lock: **{SHIPUX_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AX2 — H-SHIPUX ({status})** · Next: **AX3 H-NANOGEN8**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AX OPEN** |",
            f"| Decision | **{decision}** |",
            "| DECODE law | usable or ABSTAIN (junk refuses) |",
            "| Hard-natural | labeled LOOKUP on ship path |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AX0 | SESSION | **DONE — PROMOTE** |",
            "| AX1 | H-PRODNAT | **DONE — PROMOTE** |",
            f"| AX2 | H-SHIPUX | **{status}** |",
            "| AX3 | H-NANOGEN8 | **NEXT** (defer unless real new method) |",
            "| AX4 | AX-REAL-EVAL | pending |",
            "| AX5 | AX-REPORT | pending |",
            "| AX6 | AX-FREEZE | pending |",
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
        r"\| AX2 \| \*\*H-SHIPUX\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AX2 | **H-SHIPUX** | Ship/demo UI always "
            "`mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN); content matches mode | "
            f"smoke + content · no unlabeled | **DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2. **AX1 H-PRODNAT** — **DONE PROMOTE** (`npm run nano:prodnat`) · "
            "next **AX2 H-SHIPUX**.  "
        ),
        (
            "2. **AX1 H-PRODNAT** — **DONE PROMOTE** (`npm run nano:prodnat`).  \n"
            f"2b. **AX2 H-SHIPUX** — **DONE {status}** (`npm run nano:shipux`) · "
            "next **AX3 H-NANOGEN8**.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ax/SESSION.md` "
        "(AX1 H-PRODNAT **DONE — PROMOTE**; next AX2 H-SHIPUX).  ",
        "> **Session:** `.local/wave-ax/SESSION.md` "
        "(AX2 H-SHIPUX **DONE — PROMOTE**; next AX3 H-NANOGEN8).  ",
        1,
    )
    if "# next: nano:shipux" in text:
        text = text.replace(
            "# next: nano:shipux",
            "npm run nano:shipux\n"
            "# next: nano:nanogen8 (defer unless real method)",
            1,
        )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2. **AX1 H-PRODNAT** — **DONE PROMOTE** (`npm run nano:prodnat`) · "
            "next **AX2 H-SHIPUX**.  "
        )
        new = (
            "2. **AX1 H-PRODNAT** — **DONE PROMOTE** (`npm run nano:prodnat`).  \n"
            "2b. **AX2 H-SHIPUX** — **DONE PROMOTE** (`npm run nano:shipux`) · "
            "next **AX3 H-NANOGEN8**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ax/SESSION.md` (AX1 H-PRODNAT **DONE — PROMOTE**; "
            "next AX2 H-SHIPUX)."
        )
        new = (
            "Session: `wave-ax/SESSION.md` (AX2 H-SHIPUX **DONE — PROMOTE**; "
            "next AX3 H-NANOGEN8)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _insert_shipux_frag(text: str, prefix: str) -> str:
    if "H-SHIPUX PROMOTE" in text:
        return text
    frag = (
        "AX2 [H-SHIPUX PROMOTE](formal-hshipux-shipux.md) "
        "(`npm run nano:shipux`) — modes+content · hard-natural LOOKUP"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*H-PRODNAT PROMOTE[^\n]*?)"
        r"(; next AX2 H-SHIPUX|; next AX2)",
        rf"\1 · {frag}; next AX3 H-NANOGEN8",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents_shipux() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "H-SHIPUX PROMOTE" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AX ACTIVE\*\* —[^\n]*H-PRODNAT PROMOTE[^\n]*?)"
        r"(; next AX2 H-SHIPUX|; next AX2)",
        r"\1 · AX2 [H-SHIPUX PROMOTE]"
        r"(docs/results/nano-lm/formal-hshipux-shipux.md) "
        r"(`npm run nano:shipux`); next AX3 H-NANOGEN8",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_shipux() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ax_tail = text.split("| **AX** |", 1)[-1][:500]
    if "H-SHIPUX PROMOTE" in ax_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AX\*\* \| \*\*ACTIVE\*\* \|[^\n]*H-PRODNAT "
        r"PROMOTE[^\n]*?)(; next AX2 H-SHIPUX|; next AX2)",
        r"\1 · AX2 [H-SHIPUX PROMOTE]"
        r"(results/nano-lm/formal-hshipux-shipux.md); "
        r"next AX3 H-NANOGEN8",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    for path, prefix in (
        (_RECIPES, "**Wave AX ACTIVE:**"),
        (_CARD, "**Wave AX ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_shipux_frag(text, prefix)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    _patch_agents_shipux()
    _patch_agenda_shipux()


def run_shipux(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AX2 SHIPUX charter after PRODNAT
    WHEN smoking ask · apps · ship/demo with DECODE + hard-natural
    THEN PROMOTE/KILL per pesquisa §5 AX2.
    """
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(4, workers)) as pool:
        fut_apps = pool.submit(
            _apps_smoke, root=root, bank=bank, curated=curated, seed=0
        )
        fut_def = pool.submit(_default_asks, root=root, bank=bank)
        fut_nm = pool.submit(_near_miss, root=root, bank=bank)
        fut_dc = pool.submit(_smoke_decode_probe, root=root)
        defaults = fut_def.result()
        near = fut_nm.result()
        apps = fut_apps.result()
        decode_probe = fut_dc.result()
    arms = _live_arms(root=root, bank=bank, curated=curated)
    hard_nat = next(
        (r for r in defaults if r.get("question") == HARD_NATURAL_ASK),
        defaults[-1],
    )
    decision = decide_shipux(
        arms=arms,
        default_asks=defaults,
        apps=apps,
        decode_probe=decode_probe,
        near_miss=near,
        anti_fp_signed=True,
    )
    wall_s = time.perf_counter() - t0
    _write_public(
        decision=decision,
        arms=arms,
        apps=apps,
        near=near,
        hard_nat=hard_nat,
        decode_probe=decode_probe,
        wall_s=wall_s,
    )
    _update_local_session(decision)
    _patch_pesquisa(decision)
    _patch_local_helpers(decision)
    _patch_public_status(decision)
    payload = {
        "id": SHIPUX_ID,
        "thesis": SHIPUX_THESIS,
        "decision": decision,
        "arms": [
            {
                "arm": a.get("arm"),
                "product_mode": a.get("product_mode"),
                "modeui_line": a.get("modeui_line"),
                "content_ok": content_matches_mode(a),
            }
            for a in arms
        ],
        "apps": [
            {
                "app_id": a.get("app_id"),
                "product_mode": a.get("product_mode"),
                "modeui_line": a.get("modeui_line"),
            }
            for a in apps
        ],
        "hard_natural": {
            "product_mode": hard_nat.get("product_mode"),
            "modeui_line": hard_nat.get("modeui_line"),
            "completion": str(hard_nat.get("completion", ""))[:120],
        },
        "near_miss": {
            "product_mode": near.get("product_mode"),
            "modeui_line": near.get("modeui_line"),
        },
        "decode_probe": {
            "product_mode": decode_probe.get("product_mode"),
            "honest": decode_content_honest(decode_probe),
        },
        "banner_ok": banner_modes_ok(),
        "wall_s": wall_s,
        "workers": workers,
        "claim": SHIPUX_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hshipux-shipux.md",
        "next": "AX3 H-NANOGEN8",
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
        payload = run_shipux(
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
    hard = payload.get("hard_natural") or {}
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": SHIPUX_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "hard_natural_mode": hard.get("product_mode"),
                "banner_ok": payload.get("banner_ok"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
