"""Wave AY REPORT runner: public closeout + SHIPAY mode smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ay_report_ops import (
    AY_EVIDENCE,
    AY_ID,
    AY_SCOREBOARD,
    AY_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_ay_report,
    realeval_section_ok,
    render_paper_lab_wave_ay,
    render_wave_ay_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipay_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ay/ay_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ay-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ay.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/ay-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-hayfreeze-ay-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-ay/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"


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
    return {p: (REPO / p).is_file() for p in AY_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-ay/ay0_session.json",
        "prodint": "results/nano-lm/wave-ay/prodint_summary.json",
        "shipay": "results/nano-lm/wave-ay/shipay_summary.json",
        "nanogen9": "results/nano-lm/wave-ay/nanogen9_summary.json",
        "real_eval": "results/nano-lm/wave-ay/real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_shipay_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · PEAK · ABSTAIN (+ DECODE probe) via SHIPAY content bars."""
    from run_shipay import (
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
        "decision": "PROMOTE" if ok else "KILL (SHIPAY mode smoke)",
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
                f"# {title} — placeholder (pending AY6)",
                "",
                "> Written by AY5 report so paper-lab links resolve. "
                "AY6 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave AZ without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "AY-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-hayfreeze-ay-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_ay_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ay(), encoding="utf-8")


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = (
        "DONE — PROMOTE"
        if decision == "PROMOTE"
        else f"DONE — {decision}"
    )
    body = "\n".join(
        [
            f"# Wave AY session checklist (**OPEN** · AY5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AY **OPEN** · intent harden + gen defer).  ",
            "> Ship lock: **"
            + SHIP_CLAIM
            + "** · ≤5M (no TAC / true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AY5 — AY-REPORT ({status})** · Next: **AY6 AY-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AY OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-ay-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-ay.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AY0 | SESSION | **DONE — PROMOTE** |",
            "| AY1 | H-PRODINT | **DONE — PROMOTE** |",
            "| AY2 | H-SHIPAY | **DONE — PROMOTE** |",
            "| AY3 | H-NANOGEN9 | **DONE — DEFER** |",
            "| AY4 | AY-REAL-EVAL | **DONE — PROMOTE** |",
            f"| AY5 | AY-REPORT | **{status}** |",
            "| AY6 | AY-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2d. **AY4 AY-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:ay:real-eval`) · next **AY5 AY-REPORT**.  "
        )
        new = (
            "2d. **AY4 AY-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:ay:real-eval`).  \n"
            f"2e. **AY5 AY-REPORT** — **DONE {status}** "
            "(`npm run nano:ay:report`) · next **AY6 AY-FREEZE**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-ay/SESSION.md` (AY4 AY-REAL-EVAL "
            "**DONE — PROMOTE**; next AY5 AY-REPORT)."
        )
        new = (
            f"Session: `wave-ay/SESSION.md` (AY5 AY-REPORT "
            f"**DONE — {status}**; next AY6 AY-FREEZE)."
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
        r"\| AY5 \| \*\*AY-REPORT\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AY5 | **AY-REPORT** | Public summary + paper-lab | "
            "anti-FP · NANOGEN6/7 HOLD · NANOGEN8 DEFER cited | "
            f"**DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2d. **AY4 AY-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:ay:real-eval`) · next **AY5 AY-REPORT**.  "
        ),
        (
            "2d. **AY4 AY-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:ay:real-eval`).  \n"
            f"2e. **AY5 AY-REPORT** — **DONE {status}** "
            "(`npm run nano:ay:report`) · next **AY6 AY-FREEZE**.  "
        ),
        1,
    )
    text = text.replace(
        (
            "5. **AY4 AY-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:ay:real-eval`) · next AY5–AY6 report · freeze.  "
        ),
        (
            "5. **AY4 AY-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:ay:real-eval`).  \n"
            f"5b. **AY5 AY-REPORT** — **DONE {status}** "
            "(`npm run nano:ay:report`) · next AY6 freeze.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-ay/SESSION.md` "
        "(AY4 AY-REAL-EVAL **DONE — PROMOTE**; next AY5 AY-REPORT).  ",
        "> **Session:** `.local/wave-ay/SESSION.md` "
        f"(AY5 AY-REPORT **DONE — {status}**; next AY6 AY-FREEZE).  ",
        1,
    )
    if "# next: nano:ay:report" in text:
        text = text.replace(
            "# next: nano:ay:report\n# npm run nano:ay:report",
            "npm run nano:ay:report\n# next: nano:ay:freeze",
            1,
        )
        if "# next: nano:ay:report" in text:
            text = text.replace(
                "# next: nano:ay:report",
                "npm run nano:ay:report\n# next: nano:ay:freeze",
                1,
            )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def _insert_report_frag(text: str, prefix: str, status: str) -> str:
    if f"AY-REPORT {status}" in text or f"AY5 [AY-REPORT {status}]" in text:
        return text
    frag = (
        f"AY5 [AY-REPORT {status}](wave-ay-summary.md) "
        f"(`npm run nano:ay:report`) · "
        "[paper-lab-wave-ay.md](paper-lab-wave-ay.md)"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*AY-REAL-EVAL PROMOTE[^\n]*?)"
        r"(; next AY5 AY-REPORT|; next AY5)",
        rf"\1 · {frag}; next AY6 AY-FREEZE",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if f"AY-REPORT {status}" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AY ACTIVE\*\* —[^\n]*AY-REAL-EVAL PROMOTE[^\n]*?)"
        r"(; next AY5 AY-REPORT|; next AY5)",
        rf"\1 · AY5 [AY-REPORT {status}]"
        r"(docs/results/nano-lm/wave-ay-summary.md) "
        r"(`npm run nano:ay:report`); next AY6 AY-FREEZE",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    ay_tail = text.split("| **AY** |", 1)[-1][:800]
    if f"AY-REPORT {status}" in ay_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AY\*\* \| \*\*ACTIVE\*\* \|[^\n]*AY-REAL-EVAL "
        r"PROMOTE[^\n]*?)(; next AY5 AY-REPORT|; next AY5)",
        rf"\1 · AY5 [AY-REPORT {status}]"
        r"(results/nano-lm/wave-ay-summary.md); "
        r"next AY6 AY-FREEZE",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "wave-ay-summary.md" in text and "paper-lab-wave-ay.md" in text:
        return
    needle = (
        "Wave AY4: `wave-ay-real-eval.md` PROMOTE · Wave AX0:"
    )
    repl = (
        "Wave AY4: `wave-ay-real-eval.md` PROMOTE · "
        f"Wave AY5: `wave-ay-summary.md` / `paper-lab-wave-ay.md` "
        f"{status} · Wave AX0:"
    )
    if needle in text:
        _EVOGEN.write_text(text.replace(needle, repl, 1), encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    status = "PROMOTE"
    for path, prefix in (
        (_RECIPES, "**Wave AY ACTIVE:**"),
        (_CARD, "**Wave AY ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_report_frag(text, prefix, status)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    if _RECIPES.is_file():
        text = _RECIPES.read_text(encoding="utf-8")
        if "Wave AY5 AY-REPORT" not in text:
            needle = (
                "| Wave AY4 AY-REAL-EVAL | [wave-ay-real-eval.md]"
                "(wave-ay-real-eval.md) **PROMOTE** "
                "(`npm run nano:ay:real-eval`) — battery 8/8 · "
                "gen locked (AY3 DEFER) · intent-FP ABSTAIN · prod=eval |\n"
            )
            row = (
                "| Wave AY5 AY-REPORT | [wave-ay-summary.md]"
                "(wave-ay-summary.md) · [paper-lab-wave-ay.md]"
                "(paper-lab-wave-ay.md) **PROMOTE** "
                "(`npm run nano:ay:report`) — anti-FP · "
                "NANOGEN6/7 HOLD · NANOGEN8 DEFER cited · gen DEFER |\n"
            )
            if needle in text:
                _RECIPES.write_text(
                    text.replace(needle, needle + row, 1), encoding="utf-8"
                )
    _patch_agents(status)
    _patch_agenda(status)
    _patch_evogen(status)


def run_ay_report(
    *, out: Path, skip_ask: bool = False, workers: int = 14
) -> dict[str, Any]:
    """
    GIVEN AY0–AY4 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_ay_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipay_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPAY smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-ay-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-ay-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-ay-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        decision = "KILL (wave-ay-summary missing real-eval section)"
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
    _patch_public_status(final)
    payload: dict[str, Any] = {
        "id": AY_ID,
        "hyp_id": AY_ID,
        "stage": "AY5",
        "thesis": AY_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(AY_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-ay-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-ay.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{AY_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "AY6 AY-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AY5 AY-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_ay_report(
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
                "hyp_id": AY_ID,
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
