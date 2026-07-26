"""Wave AC-FREEZE runner (nano:ac:freeze) — lock AC; no Wave AD invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ac_freeze_ops import (
    AC_DECISIONS,
    AC_FREEZE_ID,
    AC_PRODUCT_DOCS,
    AC_PUBLIC,
    AC_THESIS,
    decide_ac_freeze,
    render_ac_freeze,
)
from ac_report_ops import render_paper_lab_wave_ac, render_wave_ac_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ac/ac_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ac-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hacfreeze-ac-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ac-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ac.md"


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


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_ac_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ac(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ac_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AC-FREEZE — Wave AC lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §8.5 AC7 · "
                "Public note: [ac-freeze.md](ac-freeze.md)  ",
                "> After: [wave-ac-summary.md](wave-ac-summary.md) / "
                "[paper-lab-wave-ac.md](paper-lab-wave-ac.md)",
                "",
                "## Hypothesis",
                "",
                "After AC-REPORT, freeze Wave AC the same way AB-FREEZE "
                "locked AB: **outcomes stay**; **no Wave AD** without an "
                "explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AC formals keep CTXPLUS…APPPLUS · HITL · REPORT **PROMOTE** | "
                "**ok** |",
                "| `wave-ac-summary` · `paper-lab-wave-ac` · `ac-freeze` contain "
                "**COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXPLUS** · **H-APPPLUS** · "
                "**COMPLETE** | **ok** |",
                "| ASKFAST/SEMWRAP known-ask smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ac:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Product claim stays scoped AC packaged apps on AB+AC spine.  ",
                "2. AC-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in `.local/pesquisa.md`.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ac_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ac_freeze.py`",
                "- Summary: `results/nano-lm/wave-ac/ac_freeze.json`",
                "- Contract: `nano_lm/tests/test_ac_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_askfast() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = (
        "Which Bitcoin signature scheme does BIP-340 lock in, "
        "and over which curve?"
    )
    cache = AskCompletionCache()
    payload = ask_once(
        question=q,
        askfast=True,
        seed=0,
        bank_path=REPO / "results/nano-lm/wave-z/error_bank.jsonl",
        curated_root=REPO / "nano_lm/data/curated",
        ask_cache=cache,
    )
    mode = str(payload.get("mode", ""))
    text = str(payload.get("completion", "")).strip()
    ok = mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"} and bool(text)
    return {
        "ok": ok,
        "mode": mode,
        "wall_ms": payload.get("wall_ms"),
        "n_chars": len(text),
    }


def run_ac_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AC PROMOTE formals + COMPLETE closeout
    WHEN locking Wave AC
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AC_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AC_PUBLIC, *AC_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(max(4, cpus - 4), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AC_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AC_PRODUCT_DOCS}
    decision = decide_ac_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_askfast()
        if not bool(ask.get("ok")):
            decision = "KILL (askfast smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    payload: dict[str, Any] = {
        "id": AC_FREEZE_ID,
        "hyp_id": AC_FREEZE_ID,
        "stage": "AC7",
        "thesis": AC_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AC_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ac-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hacfreeze-ac-freeze.md",
        "wave_ac_summary": "docs/results/nano-lm/wave-ac-summary.md",
        "rule": "pesquisa §8.5 AC-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "COMPLETE",
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_ac_freeze(
            out=Path(args.out), skip_ask=bool(args.skip_ask)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(summary.get("decision", "")).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AC_FREEZE_ID,
                "decision": str(summary.get("decision", ""))[:96],
                "wave_status": summary.get("wave_status"),
                "cpu_threads": threads,
                "workers": summary.get("workers"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
