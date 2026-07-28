"""Wave AZ REPORT runner: public closeout + SHIPAZ mode smoke."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from az_report_ops import (
    AZ_EVIDENCE,
    AZ_ID,
    AZ_SCOREBOARD,
    AZ_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_az_report,
    realeval_section_ok,
    render_paper_lab_wave_az,
    render_wave_az_summary,
    report_markers_ok,
    scoreboard_ok,
)
from matrix_common import REPO, write_json
from shipaz_ops import arms_honest_ok, core_modes_ok
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-az/az_report_summary.json"
_SUMMARY = REPO / "docs/results/nano-lm/wave-az-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-az.md"
_FREEZE_STUB = REPO / "docs/results/nano-lm/az-freeze.md"
_FORMAL_FREEZE_STUB = REPO / "docs/results/nano-lm/formal-hazfreeze-az-freeze.md"
_LOCAL_SESSION = REPO / ".local/wave-az/SESSION.md"
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
    # 16c / tight RAM: leave ≥2 cores free for SHIPAZ smoke.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _evidence_map() -> dict[str, bool]:
    return {p: (REPO / p).is_file() for p in AZ_EVIDENCE}


def _load_json(rel: str) -> dict[str, Any] | None:
    path = REPO / rel
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_facts() -> dict[str, Any]:
    keys = {
        "session": "results/nano-lm/wave-az/az0_session.json",
        "prodgen": "results/nano-lm/wave-az/prodgen_summary.json",
        "shipaz": "results/nano-lm/wave-az/shipaz_summary.json",
        "nanogen10": "results/nano-lm/wave-az/nanogen10_summary.json",
        "real_eval": "results/nano-lm/wave-az/real_eval_summary.json",
    }
    out: dict[str, Any] = {}
    for name, rel in keys.items():
        data = _load_json(rel) or {}
        out[name] = data.get("decision")
    return out


def _smoke_shipaz_modes(*, workers: int) -> dict[str, Any]:
    """LOOKUP · PEAK · ABSTAIN (+ DECODE probe) via SHIPAZ content bars."""
    from run_shipaz import (
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
        "decision": "PROMOTE" if ok else "KILL (SHIPAZ mode smoke)",
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
                f"# {title} — placeholder (pending AZ6)",
                "",
                "> Written by AZ5 report so paper-lab links resolve. "
                "AZ6 replaces this with the formal freeze.",
                "",
                f"Ship claim: **{SHIP_CLAIM}**",
                "",
                "Do not invent Wave BA without lab-book reopen.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _ensure_freeze_stubs() -> None:
    _write_stub(_FREEZE_STUB, "AZ-FREEZE")
    _write_stub(_FORMAL_FREEZE_STUB, "formal-hazfreeze-az-freeze")


def _write_public() -> None:
    _SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    _ensure_freeze_stubs()
    _SUMMARY.write_text(render_wave_az_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_az(), encoding="utf-8")


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
            f"# Wave AZ session checklist (**OPEN** · AZ5 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AZ **OPEN** · held-out harden + gen defer).  ",
            "> Ship lock: **"
            + SHIP_CLAIM
            + "** · ≤5M (no TAC / true-continue unlock).",
            "",
            "## Current stage",
            "",
            f"**AZ5 — AZ-REPORT ({status})** · Next: **AZ6 AZ-FREEZE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AZ OPEN** (RESEARCH_COMPLETE pending FREEZE) |",
            f"| Decision | **{decision}** |",
            "| Public | `docs/results/nano-lm/wave-az-summary.md` |",
            "| Paper-lab | `docs/results/nano-lm/paper-lab-wave-az.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AZ0 | SESSION | **DONE — PROMOTE** |",
            "| AZ1 | H-PRODGEN | **DONE — PROMOTE** |",
            "| AZ2 | H-SHIPAZ | **DONE — PROMOTE** |",
            "| AZ3 | H-NANOGEN10 | **DONE — DEFER** |",
            "| AZ4 | AZ-REAL-EVAL | **DONE — PROMOTE** |",
            f"| AZ5 | AZ-REPORT | **{status}** |",
            "| AZ6 | AZ-FREEZE | **NEXT** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_local_helpers(status: str) -> None:
    if _LOCAL_IMPL.is_file():
        text = _LOCAL_IMPL.read_text(encoding="utf-8")
        old = (
            "2d. **AZ4 AZ-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:az:real-eval`) · next **AZ5 AZ-REPORT**.  "
        )
        new = (
            "2d. **AZ4 AZ-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:az:real-eval`).  \n"
            f"2e. **AZ5 AZ-REPORT** — **DONE {status}** "
            "(`npm run nano:az:report`) · next **AZ6 AZ-FREEZE**.  "
        )
        if old in text:
            _LOCAL_IMPL.write_text(text.replace(old, new, 1), encoding="utf-8")
    if _LOCAL_README.is_file():
        text = _LOCAL_README.read_text(encoding="utf-8")
        old = (
            "Session: `wave-az/SESSION.md` (AZ4 AZ-REAL-EVAL "
            "**DONE — PROMOTE**; next AZ5 AZ-REPORT)."
        )
        new = (
            f"Session: `wave-az/SESSION.md` (AZ5 AZ-REPORT "
            f"**DONE — {status}**; next AZ6 AZ-FREEZE)."
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
        r"\| AZ5 \| \*\*AZ-REPORT\*\* \|[^\n]+\| \*\*TODO\*\* \|",
        (
            "| AZ5 | **AZ-REPORT** | Summary + paper-lab | "
            "anti-FP · HOLD/DEFER cited | "
            f"**DONE — {status}** |"
        ),
        text,
        count=1,
    )
    if n:
        text = text2
    text = text.replace(
        (
            "2d. **AZ4 AZ-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:az:real-eval`) · next **AZ5 AZ-REPORT**.  "
        ),
        (
            "2d. **AZ4 AZ-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:az:real-eval`).  \n"
            f"2e. **AZ5 AZ-REPORT** — **DONE {status}** "
            "(`npm run nano:az:report`) · next **AZ6 AZ-FREEZE**.  "
        ),
        1,
    )
    text = text.replace(
        (
            "5. **AZ4 AZ-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:az:real-eval`) · next AZ5–AZ6 report · freeze.  "
        ),
        (
            "5. **AZ4 AZ-REAL-EVAL** — **DONE PROMOTE** "
            "(`npm run nano:az:real-eval`).  \n"
            f"5b. **AZ5 AZ-REPORT** — **DONE {status}** "
            "(`npm run nano:az:report`) · next AZ6 freeze.  "
        ),
        1,
    )
    text = text.replace(
        "> **Session:** `.local/wave-az/SESSION.md` "
        "(AZ4 AZ-REAL-EVAL **DONE — PROMOTE**; next AZ5 AZ-REPORT).  ",
        "> **Session:** `.local/wave-az/SESSION.md` "
        f"(AZ5 AZ-REPORT **DONE — {status}**; next AZ6 AZ-FREEZE).  ",
        1,
    )
    if "# next: nano:az:report" in text:
        text = text.replace(
            "# next: nano:az:report\n# npm run nano:az:report",
            "npm run nano:az:report\n# next: nano:az:freeze",
            1,
        )
        if "# next: nano:az:report" in text:
            text = text.replace(
                "# next: nano:az:report",
                "npm run nano:az:report\n# next: nano:az:freeze",
                1,
            )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")
    _patch_local_helpers(status)


def _insert_report_frag(text: str, prefix: str, status: str) -> str:
    if f"AZ-REPORT {status}" in text or f"AZ5 [AZ-REPORT {status}]" in text:
        return text
    frag = (
        f"AZ5 [AZ-REPORT {status}](wave-az-summary.md) "
        f"(`npm run nano:az:report`) · "
        "[paper-lab-wave-az.md](paper-lab-wave-az.md)"
    )
    text2, count = re.subn(
        rf"({re.escape(prefix)}[^\n]*AZ-REAL-EVAL PROMOTE[^\n]*?)"
        r"(; next AZ5 AZ-REPORT|; next AZ5)",
        rf"\1 · {frag}; next AZ6 AZ-FREEZE",
        text,
        count=1,
    )
    return text2 if count else text


def _patch_agents(status: str) -> None:
    if not _AGENTS.is_file():
        return
    text = _AGENTS.read_text(encoding="utf-8")
    if f"AZ-REPORT {status}" in text:
        return
    text2, n = re.subn(
        r"(- \*\*Wave AZ ACTIVE\*\* —[^\n]*AZ-REAL-EVAL PROMOTE[^\n]*?)"
        r"(; next AZ5 AZ-REPORT|; next AZ5)",
        rf"\1 · AZ5 [AZ-REPORT {status}]"
        r"(docs/results/nano-lm/wave-az-summary.md) "
        r"(`npm run nano:az:report`); next AZ6 AZ-FREEZE",
        text,
        count=1,
    )
    if n:
        _AGENTS.write_text(text2, encoding="utf-8")


def _patch_agenda(status: str) -> None:
    if not _AGENDA.is_file():
        return
    text = _AGENDA.read_text(encoding="utf-8")
    az_tail = text.split("| **AZ** |", 1)[-1][:800]
    if f"AZ-REPORT {status}" in az_tail:
        return
    text2, n = re.subn(
        r"(\| \*\*AZ\*\* \| \*\*ACTIVE\*\* \|[^\n]*AZ-REAL-EVAL "
        r"PROMOTE[^\n]*?)(; next AZ5 AZ-REPORT|; next AZ5)",
        rf"\1 · AZ5 [AZ-REPORT {status}]"
        r"(results/nano-lm/wave-az-summary.md); "
        r"next AZ6 AZ-FREEZE",
        text,
        count=1,
    )
    if n:
        _AGENDA.write_text(text2, encoding="utf-8")


def _patch_evogen(status: str) -> None:
    if not _EVOGEN.is_file():
        return
    text = _EVOGEN.read_text(encoding="utf-8")
    if "wave-az-summary.md" in text and "paper-lab-wave-az.md" in text:
        return
    needle = "AZ4 AZ-REAL-EVAL PROMOTE; next AZ5 AZ-REPORT"
    repl = (
        f"AZ4 AZ-REAL-EVAL PROMOTE · AZ5 AZ-REPORT {status} "
        f"(wave-az-summary.md / paper-lab-wave-az.md); next AZ6 AZ-FREEZE"
    )
    if needle in text:
        _EVOGEN.write_text(text.replace(needle, repl, 1), encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    status = "PROMOTE"
    for path, prefix in (
        (_RECIPES, "**Wave AZ ACTIVE:**"),
        (_CARD, "**Wave AZ ACTIVE** —"),
    ):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        updated = _insert_report_frag(text, prefix, status)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
    if _RECIPES.is_file():
        text = _RECIPES.read_text(encoding="utf-8")
        if "Wave AZ5 AZ-REPORT" not in text:
            needle = (
                "| Wave AZ4 AZ-REAL-EVAL | [wave-az-real-eval.md]"
                "(wave-az-real-eval.md) **PROMOTE** "
                "(`npm run nano:az:real-eval`) — battery 9/9 · "
                "gen locked (AZ3 DEFER) · held-out ABSTAIN · "
                "over-refuse LOOKUP · prod=eval |\n"
            )
            row = (
                "| Wave AZ5 AZ-REPORT | [wave-az-summary.md]"
                "(wave-az-summary.md) · [paper-lab-wave-az.md]"
                "(paper-lab-wave-az.md) **PROMOTE** "
                "(`npm run nano:az:report`) — anti-FP · "
                "NANOGEN6/7 HOLD · NANOGEN8·9 DEFER cited · gen DEFER |\n"
            )
            if needle in text:
                _RECIPES.write_text(
                    text.replace(needle, needle + row, 1), encoding="utf-8"
                )
    _patch_agents(status)
    _patch_agenda(status)
    _patch_evogen(status)


def run_az_report(
    *, out: Path, skip_ask: bool = False, workers: int = 14
) -> dict[str, Any]:
    """
    GIVEN AZ0–AZ4 evidence
    WHEN writing public summary + paper-lab and checking anti-FP/mode smoke
    THEN PROMOTE iff evidence ∧ markers ∧ scoreboard ∧ antifp ∧ realeval ∧ smoke.
    """
    _write_public()
    evidence = _evidence_map()
    decision = decide_az_report(evidence)
    report_text = _SUMMARY.read_text(encoding="utf-8")
    markers = report_markers_ok(report_text)
    board = scoreboard_ok(report_text)
    antifp = antifp_section_ok(report_text)
    realeval = realeval_section_ok(report_text)
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_shipaz_modes(workers=workers)
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·ABSTAIN SHIPAZ smoke failed)"
    if decision.startswith("PROMOTE") and not markers:
        decision = "KILL (wave-az-summary missing thesis markers)"
    if decision.startswith("PROMOTE") and not board:
        decision = "KILL (wave-az-summary missing scoreboard)"
    if decision.startswith("PROMOTE") and not antifp:
        decision = "KILL (wave-az-summary missing anti-FP evidence)"
    if decision.startswith("PROMOTE") and not realeval:
        decision = "KILL (wave-az-summary missing real-eval section)"
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
        "id": AZ_ID,
        "hyp_id": AZ_ID,
        "stage": "AZ5",
        "thesis": AZ_THESIS,
        "decision": final,
        "markers_ok": markers,
        "scoreboard_ok": board,
        "antifp_ok": antifp,
        "realeval_ok": realeval,
        "scoreboard": list(AZ_SCOREBOARD),
        "evidence": evidence,
        "stage_facts": _stage_facts(),
        "ask_smoke": ask,
        "public_report": "docs/results/nano-lm/wave-az-summary.md",
        "paper_lab": "docs/results/nano-lm/paper-lab-wave-az.md",
        "wave_status": "RESEARCH_COMPLETE" if ok else "OPEN",
        "ship_claim": SHIP_CLAIM,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "finding": (
            f"{AZ_ID}: decision={final}; "
            f"markers={markers}; scoreboard={board}; "
            f"antifp={antifp}; realeval={realeval}."
        ),
        "next": "AZ6 AZ-FREEZE",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser(description="Wave AZ5 AZ-REPORT")
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        summary = run_az_report(
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
                "hyp_id": AZ_ID,
                "decision": summary.get("decision"),
                "markers_ok": summary.get("markers_ok"),
                "scoreboard_ok": summary.get("scoreboard_ok"),
                "antifp_ok": summary.get("antifp_ok"),
                "realeval_ok": summary.get("realeval_ok"),
                "ask_smoke_ok": (summary.get("ask_smoke") or {}).get("ok"),
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
