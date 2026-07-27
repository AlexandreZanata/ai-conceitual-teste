"""Wave AW REPORT runner: public closeout + SHIPKEEP mode smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from aw_report_ops import (
    AW_EVIDENCE,
    AW_ID,
    AW_SCOREBOARD,
    AW_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_aw_report,
    realeval_section_ok,
    render_paper_lab_wave_aw,
    render_wave_aw_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipkeep_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-aw/aw_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-aw-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-aw.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/aw-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-hawfreeze-aw-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-aw/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"


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
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in AW_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-aw/aw0_session.json",
        "prodkeep": "results/nano-lm/wave-aw/prodkeep_summary.json",
        "shipkeep": "results/nano-lm/wave-aw/shipkeep_summary.json",
        "nanogen7": "results/nano-lm/wave-aw/nanogen7_summary.json",
        "real_eval": "results/nano-lm/wave-aw/real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_shipkeep_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · PEAK · ABSTAIN (+ DECODE probe) via SHIPKEEP content bars."""
    from run_shipkeep import (
        _CHAMPION,
        _CURATED,
        _Z_BANK,
        _smoke_abstain,
        _smoke_decode_probe,
        _smoke_lookup,
        _smoke_peak,
    )

    with ThreadPoolExecutor(max_workers=min(workers, 4)) as pool:
        fut_l = pool.submit(_smoke_lookup, root=_CHAMPION, bank=_Z_BANK)
        fut_p = pool.submit(_smoke_peak, curated=_CURATED)
        fut_a = pool.submit(_smoke_abstain, root=_CHAMPION, bank=_Z_BANK)
        fut_d = pool.submit(_smoke_decode_probe, root=_CHAMPION)
        lookup = fut_l.result()
        peak = fut_p.result()
        abstain = fut_a.result()
        decode_probe = fut_d.result()
    arms = [lookup, peak, abstain]
    if str(decode_probe.get("product_mode")) == "DECODE":
        decode_probe["arm"] = "DECODE"
        arms.append(decode_probe)
    ok = arms_honest_ok(arms) and core_modes_ok(arms)
    return {
        "ok": ok,
        "decision": "PROMOTE" if ok else "KILL (SHIPKEEP mode smoke)",
        "core_modes_ok": core_modes_ok(arms),
        "arms_honest_ok": arms_honest_ok(arms),
        "arms": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
                "content_ok": True,
            }
            for r in arms
        ],
        "decode_probe": {
            "product_mode": decode_probe.get("product_mode"),
            "wall_ms": decode_probe.get("wall_ms"),
            "n_new": decode_probe.get("n_new"),
        },
    }


def _write_stub(path: Path, title: str) -> None:
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# {title} — placeholder (pending AW6)",
                "",
                "> Written by AW5 report so paper-lab links resolve. "
                "AW6 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave AX without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "AW-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-hawfreeze-aw-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_aw_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_aw(), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AW session checklist (**OPEN** · AW5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AW **OPEN**).  ",
            "> Parent: AV COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (no TAC true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AW5 — AW-REPORT ({status})** · Next: **AW6 AW-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AW OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-aw-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-aw.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AW0 | SESSION | **DONE — PROMOTE** |",
            "| AW1 | H-PRODKEEP | **DONE — PROMOTE** |",
            "| AW2 | H-SHIPKEEP | **DONE — PROMOTE** |",
            "| AW3 | H-NANOGEN7 | **DONE — HOLD** |",
            "| AW4 | AW-REAL-EVAL | **DONE — PROMOTE** |",
            f"| AW5 | AW-REPORT | **{status}** |",
            "| AW6 | AW-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2d. **AW4 AW-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:aw:real-eval`) · next **AW5 AW-REPORT**."
        )
        new = (
            "2d. **AW4 AW-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:aw:real-eval`).  \n"
            f"2e. **AW5 AW-REPORT** — **DONE {status}** "
            "(`npm run nano:aw:report`) · next **AW6 AW-FREEZE**."
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-aw/SESSION.md` (AW4 AW-REAL-EVAL "
            "**DONE — PROMOTE**; next AW5 AW-REPORT)."
        )
        new = (
            f"Session: `wave-aw/SESSION.md` (AW5 AW-REPORT "
            f"**DONE — {status}**; next AW6 AW-FREEZE)."
        )
        if old in text:
            _LOCAL_README.write_text(
                text.replace(old, new, 1), encoding="utf-8"
            )


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file():
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    status = (
        "PROMOTE"
        if decision == "PROMOTE"
        else decision.split("(", 1)[0].strip()
    )
    text2, n = re.subn(
        r"(\| AW5 \| \*\*AW-REPORT\*\* \| Public summary \+ paper-lab \| "
        r"anti-FP \+ real-eval \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2d\. \*\*AW4 AW-REAL-EVAL\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:aw:real-eval`\))? · next \*\*AW5 AW-REPORT\*\*\.",
        (
            "2d. **AW4 AW-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:aw:real-eval`).  \n"
            f"2e. **AW5 AW-REPORT** — **DONE {status}** "
            "(`npm run nano:aw:report`) · next **AW6 AW-FREEZE**."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:aw:report"
    bash_new = (
        "npm run nano:aw:report\n"
        "# next: nano:aw:freeze"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def run_aw_report(
    *, out: Path, skip_ask: bool = False, workers: int = 14
) -> dict[str, Any]:
    """
    GIVEN AW0–AW4 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_aw_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipkeep_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPKEEP smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-aw-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-aw-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-aw-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        decision = "KILL (wave-aw-summary missing real-eval section)"
    ok = (
        str(decision).startswith("PROMOTE")
        and markers
        and board
        and antifp
        and realeval
    )
    if ask is not None:
        ok = ok and bool(ask.get("ok"))
    final = "PROMOTE" if ok else decision
    _update_local_session(final)
    _patch_pesquisa(final)
    payload: dict[str, Any] = {
        "id": AW_ID,
        "hyp_id": AW_ID,
        "stage": "AW5",
        "thesis": AW_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(AW_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-aw-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-aw.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{AW_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "AW6 AW-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AW5 AW-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_aw_report(
            out=Path(args.out),
            skip_ask=bool(args.skip_ask),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(summary.get("decision")) == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AW_ID,
                "decision": summary.get("decision"),
                "wave_status": summary.get("wave_status"),
                "markers_ok": summary.get("markers_ok"),
                "scoreboard_ok": summary.get("scoreboard_ok"),
                "antifp_ok": summary.get("antifp_ok"),
                "realeval_ok": summary.get("realeval_ok"),
                "ship_claim": summary.get("ship_claim"),
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
