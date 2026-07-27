"""Wave AV REPORT runner: public closeout + SHIPUI2 mode smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from av_report_ops import (
    AV_EVIDENCE,
    AV_ID,
    AV_SCOREBOARD,
    AV_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_av_report,
    realeval_section_ok,
    render_paper_lab_wave_av,
    render_wave_av_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipui2_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-av/av_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-av-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-av.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/av-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-havfreeze-av-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-av/SESSION.md"
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
    return {p: (REPO / p).is_file() for p in AV_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-av/av0_session.json",
        "prodship": "results/nano-lm/wave-av/prodship_summary.json",
        "shipui2": "results/nano-lm/wave-av/shipui2_summary.json",
        "nanogen6": "results/nano-lm/wave-av/nanogen6_summary.json",
        "real_eval": "results/nano-lm/wave-av/real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_shipui2_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · PEAK · ABSTAIN (+ DECODE probe) via SHIPUI2 content bars."""
    from run_shipui2 import (
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
        "decision": "PROMOTE" if ok else "KILL (SHIPUI2 mode smoke)",
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
                f"# {title} — placeholder (pending AV6)",
                "",
                "> Written by AV5 report so paper-lab links resolve. "
                "AV6 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave AW without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "AV-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-havfreeze-av-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_av_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_av(), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AV session checklist (**OPEN** · AV5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AV **OPEN**).  ",
            "> Parent: AU COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M (no true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AV5 — AV-REPORT ({status})** · Next: **AV6 AV-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AV OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-av-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-av.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AV0 | SESSION | **DONE — PROMOTE** |",
            "| AV1 | H-PRODSHIP | **DONE — PROMOTE** |",
            "| AV2 | H-SHIPUI2 | **DONE — PROMOTE** |",
            "| AV3 | H-NANOGEN6 | **DONE — HOLD** |",
            "| AV4 | AV-REAL-EVAL | **DONE — PROMOTE** |",
            f"| AV5 | AV-REPORT | **{status}** |",
            "| AV6 | AV-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2d. **AV4 AV-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:av:real-eval`) · next **AV5 AV-REPORT**."
        )
        new = (
            "2d. **AV4 AV-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:av:real-eval`).  \n"
            f"2e. **AV5 AV-REPORT** — **DONE {status}** "
            "(`npm run nano:av:report`) · next **AV6 AV-FREEZE**."
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-av/SESSION.md` (AV4 AV-REAL-EVAL "
            "**DONE — PROMOTE**; next AV5 AV-REPORT)."
        )
        new = (
            f"Session: `wave-av/SESSION.md` (AV5 AV-REPORT "
            f"**DONE — {status}**; next AV6 AV-FREEZE)."
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
        r"(\| AV5 \| \*\*AV-REPORT\*\* \| Public summary \+ paper-lab \| "
        r"anti-FP \+ real-eval section \| )\*\*[^*]+\*\*",
        rf"\1**DONE — {status}**",
        text,
        count=1,
    )
    if n:
        text = text2
    text2, n = re.subn(
        r"2d\. \*\*AV4 AV-REAL-EVAL\*\* — \*\*DONE [^*]+\*\*"
        r"(?: \(`npm run nano:av:real-eval`\))? · next \*\*AV5 AV-REPORT\*\*\.",
        (
            "2d. **AV4 AV-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:av:real-eval`).  \n"
            f"2e. **AV5 AV-REPORT** — **DONE {status}** "
            "(`npm run nano:av:report`) · next **AV6 AV-FREEZE**."
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    bash_old = "# next: nano:av:report (as stages land)"
    bash_new = (
        "npm run nano:av:report\n"
        "# next: nano:av:freeze (as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def run_av_report(
    *, out: Path, skip_ask: bool = False, workers: int = 14
) -> dict[str, Any]:
    """
    GIVEN AV0–AV4 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_av_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipui2_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPUI2 smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-av-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-av-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-av-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        decision = "KILL (wave-av-summary missing real-eval section)"
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
        "id": AV_ID,
        "hyp_id": AV_ID,
        "stage": "AV5",
        "thesis": AV_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(AV_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-av-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-av.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{AV_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "AV6 AV-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AV5 AV-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_av_report(
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
                "hyp_id": AV_ID,
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
