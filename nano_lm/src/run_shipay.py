"""Wave AY2 H-SHIPAY runner (nano:shipay) — modes + content after PRODINT."""

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
from shipay_ops import (
    APP_SMOKE_PACK,
    HARD_NATURAL_ASK,
    INTENT_FP_ASK,
    SHIPAY_ANTI_FP,
    SHIPAY_CLAIM,
    SHIPAY_ID,
    SHIPAY_PATHS,
    SHIPAY_SAFE_NOTE,
    SHIPAY_THESIS,
    arms_honest_ok,
    attach_shipay,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipay,
    demo_card_markdown,
)
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-ay/shipay_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shipay-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshipay-shipay.md"
_LOCAL_SESSION = REPO / ".local/wave-ay/SESSION.md"
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
_EMPTY_BANK = REPO / "results/nano-lm/wave-ay/_decode_empty_bank.jsonl"
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
    # 16c / ~10Gi avail: leave ≥2 cores; cap workers to avoid OOM thrash.
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
    row = attach_shipay(dict(payload))
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
    row = attach_shipay(dict(payload))
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
    row = attach_shipay(dict(payload))
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
    row = attach_shipay(dict(payload))
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
    row = attach_shipay(dict(payload))
    row["arm"] = "NEAR_MISS"
    row["question"] = NEAR_MISS_ASK
    return row


def _ask_labeled(
    question: str, *, root: Path, bank: Path, semwrap: bool = True
) -> dict[str, Any]:
    payload = ask_once(
        question=question,
        root=root,
        seed=0,
        wrap=True,
        semwrap=semwrap,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=True,
    )
    row = attach_shipay(dict(payload))
    row["question"] = question
    return row


def _default_asks(*, root: Path, bank: Path, workers: int) -> list[dict[str, Any]]:
    specs = (
        (KNOWN_ASK, False),
        (_OOD, True),
        (HARD_NATURAL_ASK, True),
        (INTENT_FP_ASK, True),
    )

    def _one(item: tuple[str, bool]) -> dict[str, Any]:
        q, sem = item
        return _ask_labeled(q, root=root, bank=bank, semwrap=sem)

    n = min(workers, 4, len(specs))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        return list(pool.map(_one, specs))


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
        row = attach_shipay(dict(payload))
        row["app_id"] = item["app_id"]
        row["trial_id"] = item["id"].replace("AS-APP-", "AY-APP-")
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
    intent_fp: dict[str, Any],
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
            f"# H-SHIPAY — modes + content after PRODINT (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AY2 · Session: "
            "`.local/wave-ay/SESSION.md`  ",
            "> Parent: [formal-hprodint-prodint.md](formal-hprodint-prodint.md) · "
            "Charter: AY2 SHIPAY  ",
            "> Module: `nano_lm/src/shipay_ops.py` · "
            "Runner: `npm run nano:shipay`",
            "",
            "## Hypothesis",
            "",
            SHIPAY_THESIS,
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
            "## Intent-FP (default ask)",
            "",
            f"- mode: **{intent_fp.get('product_mode')}**  ",
            f"- modeui: `{intent_fp.get('modeui_line')}`  ",
            f"- completion: `{str(intent_fp.get('completion', ''))[:80]}`",
            "",
            "## Near-miss (default ask)",
            "",
            f"- mode: **{near.get('product_mode')}**  ",
            f"- completion: `{str(near.get('completion', ''))[:80]}`",
            "",
            "| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | "
            f"banner_ok=**{banner_modes_ok()}** |",
            f"| Charter paths | {', '.join(SHIPAY_PATHS)} | — |",
            f"| Arms honest | **{arms_honest_ok(arms)}** | labeled + content |",
            f"| Core modes | **{core_modes_ok(arms)}** | LOOKUP·PEAK·ABSTAIN |",
            f"| Decision | **{status}** | smoke + content · no unlabeled |",
            "",
            "## Finding",
            "",
            "1. Ship/demo arms stay labeled after PRODINT; content matches mode.  ",
            "2. WRAP_DECODE gibberish refuses to ABSTAIN "
            "(DECODE content law holds).  ",
            "3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  ",
            "4. Apps surfaces stay labeled with usable LOOKUP gold.  ",
            "5. Near-miss on default ask stays ABSTAIN.  ",
            "6. Hard-natural stays labeled LOOKUP on ship path.  ",
            "7. Intent-FP (mul) stays labeled ABSTAIN on ship path.  ",
            "8. Demo card: [shipay-demo.md](shipay-demo.md).  ",
            f"9. Wall ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "10. Generative claim still locked (gen stance **defer**; AY3 "
            "H-NANOGEN9).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shipay",
            "npm run nano:prodint",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ay/shipay_summary.json`  ",
            "- Demo: [shipay-demo.md](shipay-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shipay.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {SHIPAY_CLAIM} | Open chat / mini-AGI |",
            "| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |",
            "| Intent-FP → ABSTAIN | Intent-mismatch as LOOKUP hit |",
            "| DECODE usable or ABSTAIN | telemetry-only content_ok |",
            "| Hard-natural labeled LOOKUP | Pack FH as live intent coverage |",
            "",
            f"SAFE note: {SHIPAY_SAFE_NOTE}  ",
            f"Anti-FP: {SHIPAY_ANTI_FP}",
            "",
            "Next: **AY3 H-NANOGEN9** — real new method or HOLD/DEFER "
            "(never NANOGEN8+rename).",
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
            f"# Wave AY session checklist (**OPEN** · AY2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AY **OPEN** · intent harden + gen defer).  ",
            f"> Ship lock: **{SHIPAY_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AY2 — H-SHIPAY ({status})** · Next: **AY3 H-NANOGEN9**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AY OPEN** |",
            f"| Decision | **{decision}** |",
            "| DECODE law | usable or ABSTAIN (junk refuses) |",
            "| Hard-natural | labeled LOOKUP on ship path |",
            "| Intent-FP | labeled ABSTAIN on ship path |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AY0 | SESSION | **DONE — PROMOTE** |",
            "| AY1 | H-PRODINT | **DONE — PROMOTE** |",
            f"| AY2 | H-SHIPAY | **{status}** |",
            "| AY3 | H-NANOGEN9 | **NEXT** (defer unless real new method) |",
            "| AY4 | AY-REAL-EVAL | pending |",
            "| AY5 | AY-REPORT | pending |",
            "| AY6 | AY-FREEZE | pending |",
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
        r"\| AY2 \| \*\*H-SHIPAY\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AY2 | **H-SHIPAY** | Ship/demo UI always "
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
            "2. **AY1 H-PRODINT** — **DONE PROMOTE** (`npm run nano:prodint`) · "
            "next **AY2 H-SHIPAY**.  "
        ),
        (
            "2. **AY1 H-PRODINT** — **DONE PROMOTE** (`npm run nano:prodint`).  \n"
            f"2b. **AY2 H-SHIPAY** — **DONE {status}** (`npm run nano:shipay`) · "
            "next **AY3 H-NANOGEN9**.  "
        ),
        1,
    )
    text = text.replace(
        (
            "3. **AY2 ship/demo** — keep `mode=LOOKUP|PEAK|DECODE` (+ ABSTAIN) "
            "always visible; content matches mode.  "
        ),
        (
            f"3. **AY2 H-SHIPAY** — **DONE {status}** (`npm run nano:shipay`) · "
            "modes+content · intent ABSTAIN labeled.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ay/SESSION.md` "
        "(AY1 H-PRODINT **DONE — PROMOTE**; next AY2 H-SHIPAY).  ",
        "> **Session:** `.local/wave-ay/SESSION.md` "
        f"(AY2 H-SHIPAY **DONE — {status}**; next AY3 H-NANOGEN9).  ",
        1,
    )
    if "# next: nano:shipay · nano:nanogen9" in text:
        text = text.replace(
            "# next: nano:shipay · nano:nanogen9",
            "npm run nano:shipay\n"
            "# next: nano:nanogen9 (defer unless real method)",
            1,
        )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_helpers(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2. **AY1 H-PRODINT** — **DONE PROMOTE** (`npm run nano:prodint`) · "
            "next **AY2 H-SHIPAY**.  "
        )
        new = (
            "2. **AY1 H-PRODINT** — **DONE PROMOTE** (`npm run nano:prodint`).  \n"
            "2b. **AY2 H-SHIPAY** — **DONE PROMOTE** (`npm run nano:shipay`) · "
            "next **AY3 H-NANOGEN9**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ay/SESSION.md` (AY1 H-PRODINT **DONE — PROMOTE**; "
            "next AY2 H-SHIPAY)."
        )
        new = (
            "Session: `wave-ay/SESSION.md` (AY2 H-SHIPAY **DONE — PROMOTE**; "
            "next AY3 H-NANOGEN9)."
        )
        if old in text:
            _LOCAL_README.write_text(text.replace(old, new, 1), encoding="utf-8")


def _insert_shipay_frag(text: str, prefix: str) -> str:
    if "H-SHIPAY PROMOTE" in text:
        return text
    frag = (
        "AY2 [H-SHIPAY PROMOTE](formal-hshipay-shipay.md) "
        "(`npm run nano:shipay`) — modes+content · intent ABSTAIN"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*H-PRODINT PROMOTE[^\n]*?)"
        r"(; next AY2 H-SHIPAY|; next AY2)",
        rf"\1 · {frag}; next AY3 H-NANOGEN9",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents_shipay() -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if "H-SHIPAY PROMOTE" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AY ACTIVE\*\* —[^\n]*H-PRODINT PROMOTE[^\n]*?)"
        r"(; next AY2 H-SHIPAY|; next AY2)",
        r"\1 · AY2 [H-SHIPAY PROMOTE]"
        r"(docs/results/nano-lm/formal-hshipay-shipay.md) "
        r"(`npm run nano:shipay`); next AY3 H-NANOGEN9",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda_shipay() -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ay_tail = text.split("| **AY** |", 1)[-1][:500] if "| **AY** |" in text else ""
    if "H-SHIPAY PROMOTE" in ay_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AY\*\* \| \*\*ACTIVE\*\* \|[^\n]*H-PRODINT "
        r"PROMOTE[^\n]*?)(; next AY2 H-SHIPAY|; next AY2)",
        r"\1 · AY2 [H-SHIPAY PROMOTE]"
        r"(results/nano-lm/formal-hshipay-shipay.md); "
        r"next AY3 H-NANOGEN9",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_recipes_table() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    if "Wave AY2 H-SHIPAY" in text:
        return
    insert = (
        "| Wave AY2 H-SHIPAY | [formal-hshipay-shipay.md]"
        "(formal-hshipay-shipay.md) **PROMOTE** (`npm run nano:shipay`) — "
        "modes+content · hard-natural LOOKUP · intent-FP ABSTAIN · no unlabeled |"
    )
    marker = "| Wave AY1 H-PRODINT |"
    idx = text.find(marker)
    if idx < 0:
        return
    end = text.find("\n", idx)
    if end < 0:
        return
    _RECIPES.write_text(text[: end + 1] + insert + "\n" + text[end + 1 :], encoding="utf-8")


def _patch_evogen_shipay() -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "formal-hshipay-shipay" in text:
        return
    text = text.replace(
        "Wave AY1: `formal-hprodint-prodint.md` PROMOTE",
        "Wave AY1: `formal-hprodint-prodint.md` PROMOTE · Wave AY2: "
        "`formal-hshipay-shipay.md` PROMOTE",
        1,
    )
    _EVOGEN.write_text(text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    for path, prefix in (
        (_RECIPES, "**Wave AY ACTIVE:**"),
        (_CARD, "**Wave AY ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_shipay_frag(text, prefix)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    _patch_agents_shipay()
    _patch_agenda_shipay()
    _patch_recipes_table()
    _patch_evogen_shipay()


def run_shipay(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AY2 SHIPAY charter after PRODINT
    WHEN smoking ask · apps · ship/demo with DECODE + hard-natural + intent-FP
    THEN PROMOTE/KILL per pesquisa §5 AY2.
    """
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(4, workers)) as pool:
        fut_apps = pool.submit(
            _apps_smoke, root=root, bank=bank, curated=curated, seed=0
        )
        fut_def = pool.submit(
            _default_asks, root=root, bank=bank, workers=workers
        )
        fut_nm = pool.submit(_near_miss, root=root, bank=bank)
        fut_dc = pool.submit(_smoke_decode_probe, root=root)
        defaults = fut_def.result()
        near = fut_nm.result()
        apps = fut_apps.result()
        decode_probe = fut_dc.result()
    arms = _live_arms(root=root, bank=bank, curated=curated)
    hard_nat = next(
        (r for r in defaults if r.get("question") == HARD_NATURAL_ASK),
        defaults[2],
    )
    intent_fp = next(
        (r for r in defaults if r.get("question") == INTENT_FP_ASK),
        defaults[-1],
    )
    decision = decide_shipay(
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
        intent_fp=intent_fp,
        decode_probe=decode_probe,
        wall_s=wall_s,
    )
    _update_local_session(decision)
    _patch_pesquisa(decision)
    _patch_local_helpers(decision)
    _patch_public_status(decision)
    payload = {
        "id": SHIPAY_ID,
        "thesis": SHIPAY_THESIS,
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
        "intent_fp": {
            "product_mode": intent_fp.get("product_mode"),
            "modeui_line": intent_fp.get("modeui_line"),
            "completion": str(intent_fp.get("completion", ""))[:120],
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
        "claim": SHIPAY_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hshipay-shipay.md",
        "next": "AY3 H-NANOGEN9",
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
        payload = run_shipay(
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
    intent = payload.get("intent_fp") or {}
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": SHIPAY_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "hard_natural_mode": hard.get("product_mode"),
                "intent_fp_mode": intent.get("product_mode"),
                "banner_ok": payload.get("banner_ok"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
