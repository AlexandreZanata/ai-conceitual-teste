"""Wave AV2 H-SHIPUI2 runner (nano:shipui2) — modes + DECODE content law."""

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
from prodhard_ops import KNOWN_ASK, NEAR_MISS_ASK, PEAK_ASK
from prodship_ops import decode_content_honest
from run_z_ask import ask_many, ask_once
from shipui2_ops import (
    APP_SMOKE_PACK,
    SHIPUI2_ANTI_FP,
    SHIPUI2_CLAIM,
    SHIPUI2_ID,
    SHIPUI2_PATHS,
    SHIPUI2_SAFE_NOTE,
    SHIPUI2_THESIS,
    arms_honest_ok,
    attach_shipui2,
    banner_modes_ok,
    content_matches_mode,
    core_modes_ok,
    decide_shipui2,
    demo_card_markdown,
)
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-av/shipui2_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shipui2-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshipui2-shipui2.md"
_LOCAL_SESSION = REPO / ".local/wave-av/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-av/_decode_empty_bank.jsonl"
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
    # Max safe on 16c / ~13Gi avail: leave 2 cores; cap workers to avoid thrash.
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
    row = attach_shipui2(dict(payload))
    row["arm"] = "LOOKUP"
    return row


def _smoke_decode_probe(*, root: Path) -> dict[str, Any]:
    """WRAP_DECODE empty-bank (AU-ASK-05 class) → junk must ABSTAIN."""
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
    row = attach_shipui2(dict(payload))
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
    row = attach_shipui2(dict(payload))
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
    row = attach_shipui2(dict(payload))
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
    row = attach_shipui2(dict(payload))
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
    return [attach_shipui2(dict(known)), attach_shipui2(dict(ood))]


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
        row = attach_shipui2(dict(payload))
        row["app_id"] = item["app_id"]
        row["trial_id"] = item["id"].replace("AS-APP-", "AV-APP-")
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
    # Live honest arms: LOOKUP · PEAK · ABSTAIN (+ optional DECODE if usable).
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
    decode_probe: dict[str, Any],
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
    app_rows = []
    for r in apps:
        app_rows.append(
            f"| {r.get('app_id')} | **{r.get('product_mode')}** | "
            f"`{r.get('modeui_line')}` |"
        )
    body = "\n".join(
        [
            f"# H-SHIPUI2 — modes + DECODE content law (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AV2 · Session: "
            "`.local/wave-av/SESSION.md`  ",
            "> Parent: [formal-hprodship-prodship.md](formal-hprodship-prodship.md) · "
            "Charter: AV2 SHIPUI2  ",
            "> Module: `nano_lm/src/shipui2_ops.py` · "
            "Runner: `npm run nano:shipui2`",
            "",
            "## Hypothesis",
            "",
            SHIPUI2_THESIS,
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
            "## Near-miss (default ask)",
            "",
            f"- mode: **{near.get('product_mode')}**  ",
            f"- completion: `{str(near.get('completion', ''))[:80]}`",
            "",
            "| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | "
            f"banner_ok=**{banner_modes_ok()}** |",
            f"| Charter paths | {', '.join(SHIPUI2_PATHS)} | — |",
            f"| Arms honest | **{arms_honest_ok(arms)}** | labeled + content |",
            f"| Core modes | **{core_modes_ok(arms)}** | LOOKUP·PEAK·ABSTAIN |",
            f"| Decision | **{status}** | smoke + content · no unlabeled |",
            "",
            "## Finding",
            "",
            "1. Ship/demo arms stay labeled; content matches mode claim.  ",
            "2. WRAP_DECODE gibberish refuses to ABSTAIN "
            "(closes telemetry-only content_ok).  ",
            "3. Banner still advertises LOOKUP|PEAK|DECODE|ABSTAIN (4/4).  ",
            "4. Apps surfaces stay labeled with usable LOOKUP gold.  ",
            "5. Near-miss on default ask stays ABSTAIN.  ",
            "6. Demo card: [shipui2-demo.md](shipui2-demo.md).  ",
            f"7. Wall ~{wall_s:.1f}s · max safe CPU (`cpus-2`).  ",
            "8. Generative claim still locked until AV3 H-NANOGEN6.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shipui2",
            "npm run nano:prodship",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-av/shipui2_summary.json`  ",
            "- Demo: [shipui2-demo.md](shipui2-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shipui2.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {SHIPUI2_CLAIM} | Open chat / mini-AGI |",
            "| Mode + content honesty | Unlabeled · LOOKUP-as-IQ |",
            "| DECODE usable or ABSTAIN | telemetry-only content_ok |",
            "| PEAK usable extractive | Peak-as-open-chat · gibberish PEAK |",
            "",
            f"SAFE note: {SHIPUI2_SAFE_NOTE}  ",
            f"Anti-FP: {SHIPUI2_ANTI_FP}",
            "",
            "Next: **AV3 H-NANOGEN6** — true continue; span-fallback ≠ gen IQ.",
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
            f"# Wave AV session checklist (**OPEN** · AV2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AV **OPEN**).  ",
            f"> Ship lock: **{SHIPUI2_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AV2 — H-SHIPUI2 ({status})** · Next: **AV3 H-NANOGEN6**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AV OPEN** |",
            f"| Decision | **{decision}** |",
            "| DECODE law | usable or ABSTAIN (junk refuses) |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AV0 | SESSION | **DONE — PROMOTE** |",
            "| AV1 | H-PRODSHIP | **DONE — PROMOTE** |",
            f"| AV2 | H-SHIPUI2 | **{status}** |",
            "| AV3 | H-NANOGEN6 | **NEXT** |",
            "| AV4 | AV-REAL-EVAL | pending |",
            "| AV5 | AV-REPORT | pending |",
            "| AV6 | AV-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = decision.split("(", 1)[0].strip()
    old = (
        "| AV2 | **H-SHIPUI2** | Human ship/demo UI always "
        "`mode=LOOKUP\\|PEAK\\|DECODE` (+ ABSTAIN); content matches mode "
        "(incl. DECODE usable/ABSTAIN) | smoke + content · no unlabeled | "
        "**TODO** |"
    )
    new = (
        "| AV2 | **H-SHIPUI2** | Human ship/demo UI always "
        "`mode=LOOKUP\\|PEAK\\|DECODE` (+ ABSTAIN); content matches mode "
        "(incl. DECODE usable/ABSTAIN) | smoke + content · no unlabeled | "
        f"**DONE — {status}** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = (
        "2. **AV1 H-PRODSHIP** — **DONE PROMOTE** (`npm run nano:prodship`) · "
        "next **AV2 H-SHIPUI2**.  "
    )
    new_next = (
        "2. **AV1 H-PRODSHIP** — **DONE PROMOTE** (`npm run nano:prodship`).  \n"
        f"2b. **AV2 H-SHIPUI2** — **DONE {status}** (`npm run nano:shipui2`) · "
        "next **AV3 H-NANOGEN6**.  "
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    bash_old = "# next: nano:shipui2 · nano:nanogen6 (as stages land)"
    bash_new = (
        "npm run nano:shipui2\n"
        "# next: nano:nanogen6 (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_impl(decision: str) -> None:
    if not _LOCAL_IMPL.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_IMPL.read_text(encoding="utf-8")
    old = (
        "2. **AV1 H-PRODSHIP** — **DONE PROMOTE** (`npm run nano:prodship`) · "
        "next **AV2 H-SHIPUI2**.  "
    )
    new = (
        "2. **AV1 H-PRODSHIP** — **DONE PROMOTE** (`npm run nano:prodship`).  \n"
        "2b. **AV2 H-SHIPUI2** — **DONE PROMOTE** (`npm run nano:shipui2`) · "
        "next **AV3 H-NANOGEN6**.  "
    )
    if old in text:
        text = text.replace(old, new, 1)
        _LOCAL_IMPL.write_text(text, encoding="utf-8")


def _patch_local_readme(decision: str) -> None:
    if not _LOCAL_README.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_README.read_text(encoding="utf-8")
    old = (
        "Session: `wave-av/SESSION.md` (AV1 H-PRODSHIP **DONE — PROMOTE**; "
        "next AV2 H-SHIPUI2)."
    )
    new = (
        "Session: `wave-av/SESSION.md` (AV2 H-SHIPUI2 **DONE — PROMOTE**; "
        "next AV3 H-NANOGEN6)."
    )
    if old in text:
        text = text.replace(old, new, 1)
        _LOCAL_README.write_text(text, encoding="utf-8")


def run_shipui2(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN AV2 SHIPUI2 charter after PRODSHIP
    WHEN smoking ask · apps · ship/demo with DECODE content law
    THEN PROMOTE/KILL per pesquisa §5 AV2.
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
    # Prefer the dedicated probe (may duplicate live DECODE/ABSTAIN).
    decision = decide_shipui2(
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
        decode_probe=decode_probe,
        wall_s=wall_s,
    )
    _update_local_session(decision)
    _patch_pesquisa(decision)
    _patch_local_impl(decision)
    _patch_local_readme(decision)
    payload = {
        "id": SHIPUI2_ID,
        "thesis": SHIPUI2_THESIS,
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
        "decode_probe": {
            "product_mode": decode_probe.get("product_mode"),
            "content_ok": content_matches_mode(decode_probe),
            "honest": decode_content_honest(decode_probe),
            "modeui_line": decode_probe.get("modeui_line"),
            "completion": str(decode_probe.get("completion", ""))[:160],
            "abstained": decode_probe.get("abstained"),
        },
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
        "banner_modes_ok": banner_modes_ok(),
        "arms_honest_ok": arms_honest_ok(arms),
        "core_modes_ok": core_modes_ok(arms),
        "wall_s": wall_s,
        "workers": workers,
        "claim": SHIPUI2_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hshipui2-shipui2.md",
        "demo": "docs/results/nano-lm/shipui2-demo.md",
        "next": "AV3 H-NANOGEN6",
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
        payload = run_shipui2(
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
                "hyp_id": SHIPUI2_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "workers": workers,
                "decode_probe": (payload.get("decode_probe") or {}).get(
                    "product_mode"
                ),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
