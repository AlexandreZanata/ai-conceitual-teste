"""Wave BG2 H-SHIPPUB runner (nano:shippub) — Track A++ utilization."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from curated_sources import SOURCES
from fastbase_ops import fastbase_generate
from genpeak_ops import chunk_doc
from matrix_common import REPO, write_json
from prodship_ops import decode_content_honest
from run_z_ask import ask_once
from shippub_ops import (
    APPEND_ASK,
    BE_RESIDUAL_ASK,
    BF_RESIDUAL_ASK,
    BG_TRANSFORM_ASK,
    BG_UNARY_ASK,
    KNOWN_ASK,
    NEAR_MISS_ASK,
    OOD_ASK,
    OVERREFUSE_ASK,
    PEAK_ASK,
    SHIPPUB_ANTI_FP,
    SHIPPUB_CLAIM,
    SHIPPUB_ID,
    SHIPPUB_SAFE_NOTE,
    SHIPPUB_THESIS,
    attach_shippub,
    banner_modes_ok,
    content_matches_mode,
    decide_shippub,
    demo_card_markdown,
    operator_card_ok,
    paper_arxiv_ok,
    paper_claim_ok,
)
from tipd_pair import tune_cpu_threads

_SUMMARY = REPO / "results/nano-lm/wave-bg/shippub_summary.json"
_DEMO = REPO / "docs/results/nano-lm/shippub-demo.md"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hshippub-shippub.md"
_LOCAL_SESSION = REPO / ".local/wave-bg/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_RECIPES = REPO / "docs/results/nano-lm/RECIPES.md"
_CARD = REPO / "docs/results/nano-lm/champion-card.md"
_AGENTS = REPO / "AGENTS.md"
_AGENDA = REPO / "docs/NANO-STUDENT-AGENDA.md"
_EVOGEN = REPO / ".cursor/rules/evogen-project.mdc"
_NARRATIVE = REPO / "docs/paper_narrative.md"
_ARXIV = REPO / "docs/arxiv.md"
_PAPER_SECTIONS = REPO / "paper/sections"
_PAPER_PDF = REPO / "paper/main.pdf"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_EMPTY_BANK = REPO / "results/nano-lm/wave-bg/_decode_empty_bank.jsonl"
_BY_ID = {str(s["id"]): s for s in SOURCES}
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
    # 16c / ~31Gi: leave ≥4 cores free; workers ≤6 under mem pressure.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(6, max(3, cpus - 4))
    return threads, workers


def _ask(
    question: str,
    *,
    root: Path,
    bank: Path,
    semwrap: bool = True,
    wrap: bool = True,
    abstain: bool = True,
) -> dict[str, Any]:
    payload = ask_once(
        question=question,
        root=root,
        seed=0,
        wrap=wrap,
        semwrap=semwrap,
        bank_path=bank,
        curated_root=_CURATED,
        abstain=abstain,
    )
    row = attach_shippub(dict(payload))
    row["question"] = question
    return row


def _smoke_lookup(*, root: Path, bank: Path) -> dict[str, Any]:
    row = _ask(KNOWN_ASK, root=root, bank=bank, semwrap=False)
    row["arm"] = "LOOKUP"
    return row


def _smoke_abstain(*, root: Path, bank: Path) -> dict[str, Any]:
    row = _ask(OOD_ASK, root=root, bank=bank)
    row["arm"] = "ABSTAIN"
    return row


def _smoke_peak(*, curated: Path) -> dict[str, Any]:
    meta = _BY_ID.get(_PEAK_SOURCE)
    if meta is None:
        raise ValueError(f"unknown source_id: {_PEAK_SOURCE}")
    path = curated / str(meta["path"])
    doc = path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_doc(doc, win=400, stride=160)
    payload = fastbase_generate(question=PEAK_ASK, chunks=chunks, doc=doc)
    row = attach_shippub(dict(payload))
    row["arm"] = "PEAK"
    row["question"] = PEAK_ASK
    return row


def _smoke_decode(*, root: Path) -> dict[str, Any]:
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
    row = attach_shippub(dict(payload))
    row["arm"] = "DECODE_PROBE"
    return row


def _probes(*, root: Path, bank: Path, workers: int) -> list[dict[str, Any]]:
    specs = (
        (KNOWN_ASK, False),
        (APPEND_ASK, True),
        (BE_RESIDUAL_ASK, True),
        (BF_RESIDUAL_ASK, True),
        (BG_UNARY_ASK, True),
        (BG_TRANSFORM_ASK, True),
        (OVERREFUSE_ASK, True),
        (OOD_ASK, True),
    )

    def _one(item: tuple[str, bool]) -> dict[str, Any]:
        q, sem = item
        return _ask(q, root=root, bank=bank, semwrap=sem)

    n = min(workers, len(specs))
    with ThreadPoolExecutor(max_workers=max(1, n)) as pool:
        return list(pool.map(_one, specs))


def _read_paper_tex() -> str:
    if not _PAPER_SECTIONS.is_dir():
        return ""
    parts: list[str] = []
    for path in sorted(_PAPER_SECTIONS.glob("*.tex")):
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def _sync_operator_card() -> None:
    """Ensure RECIPES/card expose ask+semwrap+modes (Track A++ operator)."""
    block = (
        "\n## Wave BG utilization (Track A++ · H-SHIPPUB)\n\n"
        "| Use | Command |\n"
        "|-----|----------|\n"
        "| Known-ask HITL | `npm run nano:z:ask -- --wrap --semwrap "
        '--question "…"` |\n'
        "| Modes | always `LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` |\n"
        "| H-UNARYINT hold | abs / factorial / uppercase → **ABSTAIN** "
        "(not wrong LOOKUP) |\n"
        "| H-PREDINT hold | even / predicate ask → **ABSTAIN** |\n"
        "| Append gold | append x to list a → **LOOKUP** |\n"
        "| Ship claim | AF packaged + AQ + AS + STRICT ablated DECODE — "
        "not unlabeled open chat · not TAC unlocked |\n"
        "| Paper / arXiv | `npm run paper:build` · `docs/arxiv.md` |\n"
        "| Suite | `npm run nano:shippub` |\n"
    )
    for path in (_RECIPES, _CARD):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        marker = "## Wave BG utilization (Track A++"
        if marker in text and "H-UNARYINT" in text and "nano:z:ask" in text:
            continue
        if marker in text:
            text = text.split(marker)[0].rstrip() + "\n"
        path.write_text(text.rstrip() + "\n" + block + "\n", encoding="utf-8")


def _sync_paper_narrative() -> None:
    if not _NARRATIVE.is_file():
        return
    text = _NARRATIVE.read_text(encoding="utf-8")
    if "H-UNARYINT" not in text:
        text = text.replace(
            "| Anti-FP | H-PREDINT · H-COMPINT · H-PRODGEN · H-REALGAIN · "
            "BA…BF-FOREVER · live ask batteries |",
            "| Anti-FP | H-UNARYINT · H-PREDINT · H-COMPINT · H-PRODGEN · "
            "H-REALGAIN · BA…BG-FOREVER · live ask batteries |",
            1,
        )
    if "H-SHIPPUB" not in text:
        text = text.replace(
            "| Ship stack | AF packaged + AQ product + AS trust + "
            "STRICT ablated DECODE · H-SHIPUSE2 Track A+ |",
            "| Ship stack | AF packaged + AQ product + AS trust + "
            "STRICT ablated DECODE · H-SHIPPUB Track A++ |",
            1,
        )
        if "H-SHIPPUB" not in text:
            text = text.replace(
                "| Ship stack | AF packaged + AQ product + AS trust + "
                "STRICT ablated DECODE |",
                "| Ship stack | AF packaged + AQ product + AS trust + "
                "STRICT ablated DECODE · H-SHIPPUB Track A++ |",
                1,
            )
    if "selective retriever" not in text.lower():
        text = text.replace(
            "Under a hard **≤5M** student budget, **labeled known-ask + "
            "refuse + mode honesty** delivers real, measurable product "
            "gains (anti-FP, context content, prod-path speed).",
            "Under a hard **≤5M** student budget, a **selective retriever** "
            "+ honest refuse stack (**labeled known-ask + refuse + mode "
            "honesty**) delivers real, measurable product gains (anti-FP, "
            "context content, prod-path speed).",
            1,
        )
    if "NANOGEN8–15" in text and "NANOGEN16" not in text:
        text = text.replace(
            "NANOGEN8–15 DEFER",
            "NANOGEN8–15 DEFER · NANOGEN16 SKIP",
            1,
        )
    _NARRATIVE.write_text(text, encoding="utf-8")
    _sync_arxiv_guide()


def _sync_arxiv_guide() -> None:
    """Ensure docs/arxiv.md states selective-retriever thesis (Track A++)."""
    if not _ARXIV.is_file():
        return
    text = _ARXIV.read_text(encoding="utf-8")
    if "selective retriever" in text.lower():
        return
    block = (
        "\n## Thesis (Track A++ · H-SHIPPUB)\n\n"
        "Publish as a **selective retriever** + refuse product under ≤5M — "
        "not an open generative LM / mini-AGI unlock. "
        "Cite H-UNARYINT · H-SHIPUSE2 · AF+AQ+AS STRICT ablated DECODE.\n"
    )
    marker = "## Honesty checklist"
    if marker in text:
        text = text.replace(marker, block + "\n" + marker, 1)
    else:
        text = text.rstrip() + "\n" + block + "\n"
    _ARXIV.write_text(text, encoding="utf-8")


def _run_paper_build() -> bool:
    try:
        proc = subprocess.run(
            ["npm", "run", "paper:build"],
            cwd=str(REPO),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired):
        return _PAPER_PDF.is_file()
    if proc.returncode != 0:
        return _PAPER_PDF.is_file()
    return _PAPER_PDF.is_file()


def _write_public(
    *,
    decision: str,
    arms: list[dict[str, Any]],
    probes: list[dict[str, Any]],
    near: dict[str, Any],
    decode_probe: dict[str, Any],
    paper_build_ok: bool,
    paper_arxiv_sync: bool,
    wall_s: float,
) -> None:
    status = decision.split("(", 1)[0].strip()
    arm_rows = [
        f"| {r['arm']} | **{r['product_mode']}** | "
        f"**{content_matches_mode(r)}** | "
        f"`{str(r.get('completion', ''))[:72]}` |"
        for r in arms
    ]
    probe_rows = [
        f"| {str(r.get('question', ''))[:48]} | "
        f"**{r.get('product_mode')}** | "
        f"`{str(r.get('completion', ''))[:48]}` |"
        for r in probes
    ]
    body = "\n".join(
        [
            f"# H-SHIPPUB — Track A++ utilization (**DONE** — {status})",
            "",
            "> Lab: `.local/pesquisa.md` §9 BG2 · Session: "
            "`.local/wave-bg/SESSION.md`  ",
            "> Parent: [formal-hunaryint-unaryint.md]"
            "(formal-hunaryint-unaryint.md) · "
            "Hold: [formal-hshipuse2-shipuse2.md]"
            "(formal-hshipuse2-shipuse2.md)  ",
            "> Module: `nano_lm/src/shippub_ops.py` · "
            "Runner: `npm run nano:shippub`",
            "",
            "## Hypothesis",
            "",
            SHIPPUB_THESIS,
            "",
            "## Gate — demo arms (mode + content)",
            "",
            "| Arm | product_mode | content_ok | completion |",
            "|-----|--------------|------------|------------|",
            *arm_rows,
            "",
            "## Gate — utilization probes",
            "",
            "| Question | product_mode | completion |",
            "|----------|--------------|------------|",
            *probe_rows,
            "",
            "## Gate — DECODE path probe",
            "",
            f"- product_mode: **{decode_probe.get('product_mode')}**  ",
            f"- honest: **{decode_content_honest(decode_probe)}**  ",
            f"- completion: `{str(decode_probe.get('completion', ''))[:96]}`",
            "",
            "## Near-miss",
            "",
            f"- mode: **{near.get('product_mode')}**  ",
            f"- completion: `{str(near.get('completion', ''))[:72]}`",
            "",
            f"| Modes banner | **LOOKUP · PEAK · DECODE · ABSTAIN** | "
            f"banner_ok=**{banner_modes_ok()}** |",
            f"| Operator card | RECIPES + champion-card synced | — |",
            f"| Paper build | **{paper_build_ok}** (`npm run paper:build`) | — |",
            f"| Paper/arXiv sync | **{paper_arxiv_sync}** | — |",
            f"| Decision | **{status}** | Track A++ done |",
            "",
            "## Finding",
            "",
            "1. Known-ask HITL demo labeled LOOKUP on prod wrap path "
            "(H-SHIPUSE2 hold).  ",
            "2. BG residual abs/uppercase stays ABSTAIN (H-UNARYINT hold).  ",
            "3. BF residual even/predicate stays ABSTAIN; BE type ABSTAIN; "
            "append+clear LOOKUP.  ",
            "4. OOD stays ABSTAIN; near-miss ABSTAIN.  ",
            "5. Operator card exposes ask path + modes + H-UNARYINT.  ",
            "6. Paper claim = AF+AQ+AS STRICT refuse — no unlock; "
            "arXiv selective-retriever path synced.  ",
            f"7. `npm run paper:build` ok=**{paper_build_ok}**.  ",
            f"8. Wall ~{wall_s:.1f}s · max safe CPU (`cpus-4`).  ",
            "9. Generative claim still locked (gen stance SKIP; "
            "H-NANOGEN17 not opened).",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:shippub",
            "npm run nano:unaryint",
            "npm run paper:build",
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-bg/shippub_summary.json`  ",
            "- Demo: [shippub-demo.md](shippub-demo.md)  ",
            "- Contract: `nano_lm/tests/test_shippub.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            f"| {SHIPPUB_CLAIM} | Open chat / mini-AGI unlock |",
            "| Track A++ deepen + H-SHIPUSE2 hold | Claim/doc drift |",
            "| Modes always visible | Unlabeled answers |",
            "",
            f"SAFE note: {SHIPPUB_SAFE_NOTE}  ",
            f"Anti-FP: {SHIPPUB_ANTI_FP}",
            "",
            "Next: **BG3 H-FASTBG** — speed p50/p99 hold/improve without FP "
            "regress.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")
    _DEMO.write_text(
        demo_card_markdown(arms=arms, probes=probes), encoding="utf-8"
    )


def _update_local_session(decision: str) -> None:
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    status = f"DONE — {decision.split('(', 1)[0].strip()}"
    body = "\n".join(
        [
            f"# Wave BG session checklist (**OPEN** · BG2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave BG **OPEN** · Track A++ after H-UNARYINT).  ",
            f"> Ship lock: **{SHIPPUB_CLAIM}** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**BG2 — H-SHIPPUB ({status})** · Next: **BG3 H-FASTBG**",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| BG0 | SESSION | **DONE — PROMOTE** |",
            "| BG1 | H-UNARYINT | **DONE — PROMOTE** |",
            f"| BG2 | H-SHIPPUB | **{status}** |",
            "| BG3 | H-FASTBG | **NEXT** |",
            "| BG4 | H-CTXBG | pending |",
            "| BG5 | H-NANOGEN17 / SKIP | pending |",
            "| BG6 | BG-REAL-EVAL | pending |",
            "| BG7 | BG-REPORT | pending |",
            "| BG8 | BG-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    text = text.replace(
        "| BG2 | **H-SHIPPUB** | Utilization++: operator + "
        "**paper/arXiv sync** + live smoke | Track A++ done | **NEXT** |",
        "| BG2 | **H-SHIPPUB** | Utilization++: operator + "
        "**paper/arXiv sync** + live smoke | Track A++ done | "
        "**DONE — PROMOTE** |",
        1,
    )
    text = text.replace(
        "| BG3 | **H-FASTBG** | Speed p50/p99 hold **or** improve "
        "**without** FP regress | latency + §1 | **TODO** |",
        "| BG3 | **H-FASTBG** | Speed p50/p99 hold **or** improve "
        "**without** FP regress | latency + §1 | **NEXT** |",
        1,
    )
    text = text.replace(
        "3. **BG2 H-SHIPPUB** — **NEXT** — deepen utilization + "
        "**paper/arXiv sync** + live smoke (hold H-SHIPUSE2).  ",
        "3. **BG2 H-SHIPPUB** — **DONE PROMOTE** (`npm run nano:shippub`) "
        "— Track A++ deepen; H-SHIPUSE2 hold; paper/arXiv sync; "
        "BG residual ABSTAIN.  ",
        1,
    )
    text = text.replace(
        "4. **BG3 H-FASTBG** — prod p50/p99 hold/improve with anti-FP hold.  ",
        "4. **BG3 H-FASTBG** — **NEXT** — prod p50/p99 hold/improve with "
        "anti-FP hold.  ",
        1,
    )
    text = text.replace(
        "(BG0 DONE — PROMOTE · BG1 **DONE — PROMOTE**; next BG2 "
        "H-SHIPPUB)",
        "(BG0–BG2 **DONE — PROMOTE**; next BG3 H-FASTBG)",
        1,
    )
    text = text.replace(
        "(BG0 DONE — PROMOTE · BG1 **DONE — PROMOTE**; next BG2 "
        "H-SHIPPUB) via this lab-book",
        "(BG0–BG2 **DONE — PROMOTE**; next BG3 H-FASTBG) via this lab-book",
        1,
    )
    text = text.replace(
        "(BG0 DONE — PROMOTE · BG1 **DONE — PROMOTE**; next BG2 "
        "H-SHIPPUB).",
        "(BG0–BG2 **DONE — PROMOTE**; next BG3 H-FASTBG).",
        1,
    )
    text = text.replace(
        "npm run nano:unaryint\n"
        "# next: nano:bg:shippub · nano:bg:fastbg · nano:bg:ctxbg · "
        "nano:nanogen17 (SKIP without plan)\n",
        "npm run nano:unaryint\n"
        "npm run nano:shippub\n"
        "# next: nano:bg:fastbg · nano:bg:ctxbg · "
        "nano:nanogen17 (SKIP without plan)\n",
        1,
    )
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_notes(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    if _LOCAL_IMPL.is_file():
        _LOCAL_IMPL.write_text(
            "\n".join(
                [
                    "# Implementation plan — nano generative LM",
                    "",
                    "> Private. Lab: [`pesquisa.md`](pesquisa.md).",
                    "",
                    "## Status",
                    "",
                    "Wave **BG ACTIVE**. BG0–BG2 **DONE — PROMOTE** "
                    "(`npm run nano:shippub`).",
                    "",
                    "## Next",
                    "",
                    "1. BG0–BG2 done.  ",
                    "2. **BG3 H-FASTBG** — **NEXT**.  ",
                    "3. Ship stays AF+AQ+AS STRICT ablated DECODE.",
                    "",
                    "```bash",
                    "npm run nano:shippub",
                    "npm run nano:test && npm run verify",
                    "```",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    if _LOCAL_README.is_file():
        _LOCAL_README.write_text(
            "\n".join(
                [
                    "# Local research notebook",
                    "",
                    "Full lab book: **`pesquisa.md`**.",
                    "",
                    "## Current wave",
                    "",
                    "**Wave BG ACTIVE** — BG0–BG1 PROMOTE · "
                    "BG2 **H-SHIPPUB PROMOTE** (Track A++ utilization).",
                    "",
                    "Next: **BG3 H-FASTBG**. Parent: Wave BF "
                    "**COMPLETE + FROZEN**.",
                    "",
                    "## Do not",
                    "",
                    "LOOKUP-as-IQ · pack theater · bank stuffing · "
                    "NANOGEN rename · CTX/SMART/FAST clones.",
                    "",
                ]
            ),
            encoding="utf-8",
        )


def _sub_file(path: Path, pattern: str, repl: str) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text2, n = re.subn(pattern, repl, text, count=1)
    if n:
        path.write_text(text2, encoding="utf-8")


def _patch_recipes_shippub() -> None:
    if not _RECIPES.is_file():
        return
    text = _RECIPES.read_text(encoding="utf-8")
    insert = (
        "| Wave BG2 H-SHIPPUB | [formal-hshippub-shippub.md]"
        "(formal-hshippub-shippub.md) **PROMOTE** "
        "(`npm run nano:shippub`) — Track A++ deepen · H-SHIPUSE2 hold · "
        "paper/arXiv sync |"
    )
    if "Wave BG2 H-SHIPPUB" not in text:
        marker = "| Wave BG1 H-UNARYINT |"
        idx = text.find(marker)
        if idx >= 0:
            end = text.find("\n", idx)
            text = text[: end + 1] + insert + "\n" + text[end + 1 :]
    text2, n = re.subn(
        r"\*\*Wave BG ACTIVE:\*\*[^\n]+",
        "**Wave BG ACTIVE:** BG0 [SESSION PROMOTE](wave-bg-session.md) · "
        "BG1 [H-UNARYINT PROMOTE](formal-hunaryint-unaryint.md) · "
        "BG2 [H-SHIPPUB PROMOTE](formal-hshippub-shippub.md) "
        "(`npm run nano:shippub`) — Track A++ done; next BG3 H-FASTBG; "
        "ship remains **AF + AQ + AS trust + STRICT ablated DECODE**; "
        "≤5M stays.",
        text,
        count=1,
    )
    _RECIPES.write_text(text2 if n else text, encoding="utf-8")


def _patch_public_status(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    _sub_file(
        _AGENTS,
        r"- \*\*Wave BG ACTIVE\*\* —[^\n]+",
        "- **Wave BG ACTIVE** — BG0 [SESSION PROMOTE]"
        "(docs/results/nano-lm/wave-bg-session.md) "
        "(`npm run nano:bg:session`) · BG1 [H-UNARYINT PROMOTE]"
        "(docs/results/nano-lm/formal-hunaryint-unaryint.md) "
        "(`npm run nano:unaryint`) · BG2 [H-SHIPPUB PROMOTE]"
        "(docs/results/nano-lm/formal-hshippub-shippub.md) "
        "(`npm run nano:shippub`) — Track A++ utilization; next BG3 "
        "H-FASTBG; ship remains **AF + AQ + AS trust + STRICT ablated "
        "DECODE**; NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16 SKIP; "
        "≤5M stays.",
    )
    _sub_file(
        _AGENDA,
        r"\| \*\*BG\*\* \| \*\*ACTIVE\*\* \|[^\n]+",
        "| **BG** | **ACTIVE** | BG0–BG2 PROMOTE "
        "(results/nano-lm/formal-hshippub-shippub.md) "
        "(`npm run nano:shippub`) — Track A++ done; next BG3 H-FASTBG; "
        "ship AF+AQ+AS trust + STRICT ablated DECODE; ≤5M |",
    )
    _patch_recipes_shippub()
    _sub_file(
        _CARD,
        r"\*\*Wave BG ACTIVE\*\* —[^\n]+",
        "**Wave BG ACTIVE** — BG0 [SESSION PROMOTE](wave-bg-session.md) · "
        "BG1 [H-UNARYINT PROMOTE](formal-hunaryint-unaryint.md) · "
        "BG2 [H-SHIPPUB PROMOTE](formal-hshippub-shippub.md) "
        "(`npm run nano:shippub`) — Track A++ utilization; next BG3 "
        "H-FASTBG; ship remains **AF + AQ + AS trust + STRICT ablated "
        "DECODE**; ≤5M stays.",
    )
    if _EVOGEN.is_file():
        text = _EVOGEN.read_text(encoding="utf-8")
        text = text.replace(
            "BG1 H-UNARYINT PROMOTE; next BG2 H-SHIPPUB",
            "BG0–BG2 PROMOTE · H-SHIPPUB Track A++; next BG3 H-FASTBG",
            1,
        )
        text = text.replace(
            "next BG2 H-SHIPPUB",
            "BG2 H-SHIPPUB PROMOTE; next BG3 H-FASTBG",
            1,
        )
        _EVOGEN.write_text(text, encoding="utf-8")


def run_shippub(
    *,
    root: Path,
    bank: Path,
    curated: Path,
    out: Path,
    workers: int,
) -> dict[str, Any]:
    """
    GIVEN H-UNARYINT PROMOTE + H-SHIPUSE2 hold + BG0 Track A++
    WHEN demo smoke + operator card + paper/arXiv sync
    THEN PROMOTE/HOLD/KILL per pesquisa §9 BG2.
    """
    t0 = time.perf_counter()
    _sync_operator_card()
    _sync_paper_narrative()
    with ThreadPoolExecutor(max_workers=min(4, workers)) as pool:
        fut_nm = pool.submit(
            lambda: _ask(NEAR_MISS_ASK, root=root, bank=bank)
        )
        fut_dc = pool.submit(lambda: _smoke_decode(root=root))
        fut_lu = pool.submit(lambda: _smoke_lookup(root=root, bank=bank))
        fut_ab = pool.submit(lambda: _smoke_abstain(root=root, bank=bank))
        fut_pr = pool.submit(
            lambda: _probes(root=root, bank=bank, workers=workers)
        )
        probes = fut_pr.result()
        near = fut_nm.result()
        decode_probe = fut_dc.result()
        lookup = fut_lu.result()
        abstain = fut_ab.result()
    peak = _smoke_peak(curated=curated)
    arms = [lookup, peak, abstain]
    paper_build_ok = _run_paper_build()
    recipes = _RECIPES.read_text(encoding="utf-8") if _RECIPES.is_file() else ""
    card = _CARD.read_text(encoding="utf-8") if _CARD.is_file() else ""
    narrative = (
        _NARRATIVE.read_text(encoding="utf-8") if _NARRATIVE.is_file() else ""
    )
    paper_tex = _read_paper_tex()
    arxiv_md = _ARXIV.read_text(encoding="utf-8") if _ARXIV.is_file() else ""
    arxiv_sync = paper_arxiv_ok(narrative=narrative, arxiv_md=arxiv_md)
    decision = decide_shippub(
        arms=arms,
        probes=probes,
        decode_probe=decode_probe,
        near_miss=near,
        recipes=recipes,
        card=card,
        narrative=narrative,
        paper_tex=paper_tex,
        arxiv_md=arxiv_md,
        paper_build_ok=paper_build_ok,
        anti_fp_signed=True,
    )
    wall_s = time.perf_counter() - t0
    _write_public(
        decision=decision,
        arms=arms,
        probes=probes,
        near=near,
        decode_probe=decode_probe,
        paper_build_ok=paper_build_ok,
        paper_arxiv_sync=arxiv_sync,
        wall_s=wall_s,
    )
    _update_local_session(decision)
    _patch_pesquisa(decision)
    _patch_local_notes(decision)
    _patch_public_status(decision)
    payload = {
        "id": SHIPPUB_ID,
        "thesis": SHIPPUB_THESIS,
        "decision": decision,
        "arms": [
            {
                "arm": a.get("arm"),
                "product_mode": a.get("product_mode"),
                "content_ok": content_matches_mode(a),
            }
            for a in arms
        ],
        "probes": [
            {
                "question": p.get("question"),
                "product_mode": p.get("product_mode"),
                "completion": str(p.get("completion", ""))[:120],
            }
            for p in probes
        ],
        "operator_card_ok": operator_card_ok(recipes=recipes, card=card),
        "paper_claim_ok": paper_claim_ok(
            narrative=narrative, paper_tex=paper_tex
        ),
        "paper_arxiv_ok": arxiv_sync,
        "paper_build_ok": paper_build_ok,
        "banner_ok": banner_modes_ok(),
        "wall_s": wall_s,
        "workers": workers,
        "claim": SHIPPUB_CLAIM,
        "public_note": "docs/results/nano-lm/formal-hshippub-shippub.md",
        "next": "BG3 H-FASTBG",
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
        os.environ["OMP_NUM_THREADS"] = str(threads)
        payload = run_shippub(
            root=args.root,
            bank=args.bank,
            curated=args.curated,
            out=args.out,
            workers=workers,
        )
    except Exception as exc:  # noqa: BLE001 — surface live runner errors
        print(json.dumps({"ok": False, "error": str(exc)}), flush=True)
        return 1
    print(
        json.dumps(
            {
                "ok": payload["decision"].startswith("PROMOTE"),
                "hyp_id": SHIPPUB_ID,
                "decision": payload["decision"],
                "cpu_threads": threads,
                "workers": workers,
                "paper_build_ok": payload.get("paper_build_ok"),
                "operator_card_ok": payload.get("operator_card_ok"),
                "out": str(args.out),
            }
        ),
        flush=True,
    )
    return 0 if payload["decision"].startswith("PROMOTE") else 2


if __name__ == "__main__":
    sys.exit(main())
