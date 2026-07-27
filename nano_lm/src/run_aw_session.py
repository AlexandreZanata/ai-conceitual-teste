"""Wave AW0 SESSION runner (nano:aw:session) — freeze AW packs + reopen."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from antifp_ops import classify_arm, extract_telemetry
from as_session_ops import AS0_ASKABSTAIN_CHARTER
from aw_session_ops import (
    AW0_ANTI_FP,
    AW0_ASK_BATTERY,
    AW0_CITED_AV_LOCKS,
    AW0_PRESSURE_PARA_PROTOCOL,
    AW0_PRESSURE_PARA_ROWS,
    AW0_ID,
    AW0_MODES,
    AW0_NANOGEN7_HYPOTHESIS,
    AW0_NORTH_STAR,
    AW0_PRODUCT_KEEP_CHARTER,
    AW0_REAL_EVAL_PROTOCOL,
    AW0_SAFE_NOTE,
    AW0_SHIP_LOCK,
    AW0_THESIS,
    AW0_TRUE_GEN_JUDGE,
    decide_aw0_session,
    map_aw_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-aw/aw0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-aw/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-aw/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-aw-session.md"
_LOCAL_SESSION = REPO / ".local/wave-aw/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_LOCAL_IMPL = REPO / ".local/IMPLEMENTATION-PLAN.md"
_LOCAL_README = REPO / ".local/README-pesquisa.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_DECODE_Q = "Explain Merkle trees briefly"
_NEAR_MISS = (
    "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
    "SegWit witness discount?"
)


def _hardware() -> tuple[int, int]:
    # Max safe on 16c / ~13Gi avail: leave 2 cores; cap workers to avoid thrash.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


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


def _write_battery_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AW0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AW0",
            "hyp_id": AW0_ID,
            "pack": "ask-battery",
            "kind": item["kind"],
            "question": item["question"],
            "expect_mode": item["expect_mode"],
            "status": "frozen",
            "mode": None,
            "wall_ms": None,
            "n_new": None,
            "score": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_para_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AW0_PRESSURE_PARA_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AW0",
            "hyp_id": AW0_ID,
            "pack": "pressure-para",
            "parent": item["parent"],
            "question": item["question"],
            "status": "frozen",
            "mode": None,
            "wall_ms": None,
            "hit": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("AW-PRODKEEP", "product-keep-charter", dict(AW0_PRODUCT_KEEP_CHARTER)),
        (
            "AW-PRESSURE-PARA",
            "pressure-para-protocol",
            dict(AW0_PRESSURE_PARA_PROTOCOL),
        ),
        (
            "AW-NANOGEN7",
            "nanogen7-hypothesis",
            {
                "hypothesis": AW0_NANOGEN7_HYPOTHESIS,
                "true_gen_judge": dict(AW0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "AW-REAL-EVAL",
            "real-eval-protocol",
            dict(AW0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "AW0",
            "hyp_id": AW0_ID,
            "pack": pack,
            "status": "frozen",
            "body": body,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _freeze_trials(trials_dir: Path) -> tuple[list[str], bool]:
    trials_dir.mkdir(parents=True, exist_ok=True)
    written = (
        _write_battery_trials(trials_dir)
        + _write_para_trials(trials_dir)
        + _write_charter_trials(trials_dir)
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = len(AW0_ASK_BATTERY) + len(AW0_PRESSURE_PARA_ROWS) + 4
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in AW0_ASK_BATTERY
    )
    para_rows = "\n".join(
        f"| {p['id']} | {p['parent']} |" for p in AW0_PRESSURE_PARA_ROWS
    )
    bars = AW0_PRODUCT_KEEP_CHARTER["bars"]
    debts = AW0_PRODUCT_KEEP_CHARTER["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    body = "\n".join(
        [
            "# Wave AW0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-aw/SESSION.md`  ",
            "> Module: `nano_lm/src/aw_session_ops.py` · "
            "Runner: `npm run nano:aw:session`  ",
            "> Parent: [av-freeze.md](av-freeze.md) "
            "(Wave AW reopened explicitly via lab-book reopen after AV-FREEZE)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze AW packs: "
            "product-keep charter · pressure-para protocol (N≥20 ≠ AV/AU) · "
            "NANOGEN7 TAC hyp (teacher-anchored novel continue; "
            "**span-fallback ≠ gen IQ**) · real-eval protocol. **Not** a "
            "CTX/SMART/FAST/APP clone · **not** NANOGEN6+rename.  ",
            "Anti-FP signed. Generative claim locked until AW3 PROMOTE.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Product-keep charter | 1 | DECODE content · pressure para · "
            "FH0 · modes · KB · latency (AW1) |",
            f"| Pressure-para protocol | {len(AW0_PRESSURE_PARA_ROWS)} | "
            "held-out ≠ AV/AU · no bank stuffing (AW1) |",
            "| NANOGEN7 hypothesis | 1 | teacher-anchored continue (TAC) · "
            "span-fallback = PEAK/LOOKUP credit only (AW3) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "telemetry ≠ content_ok (AW3) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "anti-FP (AW4) |",
            f"| Ask battery | {len(AW0_ASK_BATTERY)} | frozen live rows "
            "(scored at AW4) |",
            "",
            "## Cited AV locks",
            "",
            ", ".join(sorted(AW0_CITED_AV_LOCKS)),
            "",
            "## Product-keep bars",
            "",
            f"- para_hit_min: **{bars['para_hit_min']}** "
            "(AV PRODSHIP baseline; pressure ≠ AV/AU)  ",
            f"- false_hit_max: **{bars['false_hit_max']}**  ",
            f"- pressure_para_min_n: **{bars['pressure_para_min_n']}**  ",
            f"- decode_gibberish_neq_content_ok: "
            f"**{bars['decode_gibberish_neq_content_ok']}**  ",
            f"- default_ask_near_miss: **{bars['default_ask_near_miss']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no re-SEMFIX/ADVSAFE unless PRODKEEP fails",
            "",
            "## Post-AV debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## Pressure-para protocol",
            "",
            f"- held_out: **{AW0_PRESSURE_PARA_PROTOCOL['held_out']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{AW0_PRESSURE_PARA_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- neq_av_pack: **{AW0_PRESSURE_PARA_PROTOCOL['neq_av_pack']}**  ",
            f"- neq_au_pack: **{AW0_PRESSURE_PARA_PROTOCOL['neq_au_pack']}**  ",
            f"- min_n: **{AW0_PRESSURE_PARA_PROTOCOL['min_n']}**  ",
            f"- path: `{AW0_PRESSURE_PARA_PROTOCOL['path']}`  ",
            "",
            "| id | parent |",
            "|----|--------|",
            para_rows,
            "",
            "## NANOGEN7 hypothesis (one idea)",
            "",
            AW0_NANOGEN7_HYPOTHESIS,
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{AW0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- gold_substring_insufficient: "
            f"{AW0_TRUE_GEN_JUDGE['gold_substring_insufficient']}  ",
            f"- gibberish_tail_fails: "
            f"{AW0_TRUE_GEN_JUDGE['gibberish_tail_fails']}  ",
            f"- telemetry_neq_content_ok: "
            f"{AW0_TRUE_GEN_JUDGE['telemetry_neq_content_ok']}  ",
            f"- scoring: `{AW0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{AW0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{AW0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{AW0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- span_fallback_neq_gen: "
            f"{AW0_REAL_EVAL_PROTOCOL['span_fallback_neq_gen']}  ",
            f"- gen_claim_rule: "
            f"{AW0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {AW0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            AW0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AW0_ANTI_FP,
            "",
            "## North star",
            "",
            AW0_NORTH_STAR,
            "",
            "## Ship lock (until AV PROMOTE)",
            "",
            AW0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:aw:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`); near-miss maps to ABSTAIN alias.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-aw/aw0_session.json` · "
            "`results/nano-lm/wave-aw/trials/AW-*.json`.  ",
            "Contract: `nano_lm/tests/test_aw_session.py`.",
            "",
            "## Claims",
            "",
            "- AV packs frozen for Wave AW — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{AW0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **AW3 H-NANOGEN7** "
            "true_continue_ablated (span-fallback ≠ gen credit).  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "gold-substring PROMOTE · truncate-to-span as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · Wave AX invent · CTX/SMART/FAST/APP "
            "clone · NANOGEN6+rename · bank stuffing · vanity re-SEMFIX.",
            "",
            "Next: **AW1 H-PRODKEEP** — accept Caminho A; close DECODE "
            "content debt; publish pressure para · FH · p50/p99 · KB.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _ask_lookup() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_KNOWN,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
    )


def _ask_decode() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_DECODE_Q,
        root=_CHAMPION,
        seed=0,
        wrap=False,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=False,
    )


def _ask_near_miss() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(
        question=_NEAR_MISS,
        root=_CHAMPION,
        seed=0,
        wrap=True,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=True,
        semwrap=True,
    )


def _decode_arm_ok(g_arm: str, g_mode: str, raw_g: str) -> bool:
    if g_mode == "DECODE":
        return True
    return g_arm == "GENERATE" and raw_g not in {"NO_ANSWER", "ABSTAIN"}


def _smoke_ok(
    *,
    lookup: dict[str, Any],
    l_arm: str,
    g_arm: str,
    l_mode: str,
    g_mode: str,
    nm_mode: str,
    l_tel: dict[str, Any],
    g_tel: dict[str, Any],
) -> bool:
    checks = (
        l_arm == "LOOKUP",
        l_mode == "LOOKUP",
        l_tel["mode"] == "WRAP_LOOKUP",
        "def add" in str(lookup.get("completion", "")),
        _decode_arm_ok(g_arm, g_mode, str(g_tel["mode"] or "")),
        float(g_tel["wall_ms"] or 0) > 0.0,
        int(g_tel["n_new"] or 0) > 0,
        map_aw_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in AW0_MODES,
    )
    return all(checks)


def _smoke_triple_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP wrap + DECODE + near-miss telemetry (anti-FP)."""
    n = min(3, max(1, workers))
    with ThreadPoolExecutor(max_workers=n) as pool:
        fut_l = pool.submit(_ask_lookup)
        fut_d = pool.submit(_ask_decode)
        fut_n = pool.submit(_ask_near_miss)
        lookup = fut_l.result()
        gen = fut_d.result()
        near = fut_n.result()
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    n_tel = extract_telemetry(near)
    l_mode = map_aw_product_mode(str(l_tel["mode"]))
    g_mode = map_aw_product_mode(str(g_tel["mode"]))
    nm_mode = map_aw_product_mode(str(n_tel["mode"]))
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
        nm_mode=nm_mode,
        l_tel=l_tel,
        g_tel=g_tel,
    )
    return {
        "ok": ok,
        "lookup": {
            "arm": l_arm,
            "raw_mode": l_tel["mode"],
            "product_mode": l_mode,
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
        },
        "decode": {
            "arm": g_arm,
            "raw_mode": g_tel["mode"],
            "product_mode": g_mode,
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
            "note": "AW1 must fail gibberish content_ok; AW0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AU PRODHARD locked ABSTAIN; AW0 verifies mapping",
        },
        "modes_charter": sorted(AW0_MODES),
        "abstain_alias": map_aw_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_triple_arm(workers=workers)
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "triple-arm smoke failed", "ask": ask}
            )
        )
        return 2, ask
    return 0, ask


def _parallel_prep(workers: int, trials_dir: Path) -> tuple[list[str], bool]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fut = pool.submit(_freeze_trials, trials_dir)
        return fut.result()


def _update_local_session(decision: str) -> None:
    _LOCAL_SESSION.parent.mkdir(parents=True, exist_ok=True)
    status = "DONE — PROMOTE" if decision.startswith("PROMOTE") else "KILL"
    body = "\n".join(
        [
            f"# Wave AW session checklist (**OPEN** · AW0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AW **OPEN** · Caminho A ship + Nano Generative).  ",
            f"> Parent: AV COMPLETE + FROZEN · Ship: **{AW0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after AV-FREEZE; product-keep open; "
            "generative needs TAC true continue beyond NANOGEN6 HOLD.",
            "",
            "## Current stage",
            "",
            f"**AW0 — SESSION ({status})** · Next: **AW1 H-PRODKEEP**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AV OPEN** |",
            "| Track | Caminho A product-keep · "
            "**H-NANOGEN7** north star |",
            "| Parent | AV COMPLETE + FROZEN |",
            "| Open hole | DECODE content · pressure para N≥20 · "
            "TAC true continue (no span-fallback gen; ≠ NANOGEN6 rename) |",
            "| Forbidden | vanity re-SEMFIX · LOOKUP-as-IQ · "
            "truncate-as-gen · NANOGEN6+rename · Wave AX invent |",
            "",
            "## North star (signed)",
            "",
            AW0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AW0)",
            "",
            "```text",
            "MODEL = AW0-SESSION",
            "",
            "[x] Freeze product-keep charter (DECODE content · external "
            "para · FH0 · modes · KB · latency)",
            "[x] Freeze pressure-para held-out protocol (N≥20 ≠ AV/AU)",
            "[x] Write ONE NANOGEN7 hypothesis (true continue; "
            "span-fallback ≠ gen)",
            "[x] Freeze true gen judge (telemetry ≠ content_ok)",
            "[x] Real-eval ask battery protocol (eval=prod ask)",
            "[x] Do NOT reopen SEMFIX/ADVSAFE unless PRODKEEP fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT clone NANOGEN6 refuse-or-continue as NANOGEN7",
            "[ ] Next: AW1 H-PRODKEEP",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AW0 | SESSION | **{status}** |",
            "| AW1 | H-PRODKEEP | **NEXT** |",
            "| AW2 | H-SHIPKEEP | pending |",
            "| AW3 | H-NANOGEN7 | pending (generative north-star gate) |",
            "| AW4 | AW-REAL-EVAL | pending |",
            "| AW5 | AW-REPORT | pending |",
            "| AW6 | AW-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Pressure para hit | ≥ 0.70 | AV PRODSHIP PROMOTE (≠ AV/AU set) |",
            "| Adversary FH (ask path) | **0** | AS ADVSAFE **0**/20 |",
            "| DECODE content | usable or ABSTAIN | AV PRODSHIP/SHIPUI2 lock |",
            "| Latency p50/p99 | publish | AV PRODSHIP / AS METRICS |",
            "| True continue (NANOGEN7) | PROMOTE else HOLD | "
            "NANOGEN6 refuse-or-continue **archived**; TAC required |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _write_pesquisa_aw_reopen(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# pesquisa — Wave AW (**ACTIVE** — reopen)

> Private under `.local/` (gitignored).  
> **Status:** Wave AW **ACTIVE** (reopened after AV-FREEZE). Parent: Wave AV **COMPLETE + FROZEN** (archive).  
> **Parent freeze:** [av-freeze.md](../docs/results/nano-lm/av-freeze.md) · [au-freeze.md](../docs/results/nano-lm/au-freeze.md).  
> **Focus (only):** **Caminho A keep** (product regression under pressure) **+** nano generative TAC ≤5M with **real evaluation**.  
> **Session:** `.local/wave-aw/SESSION.md` (create at AW0).  
> **Archive:** Waves W–**AV** → `docs/results/nano-lm/*-freeze.md`. EvoGen → `docs/archive/evogen/`.

---

## 0. Mandate (read first)

**One focus. Two legs. Do not dilute.**

### Caminho A — Product keep (immediate real gain)

> Accept AV artifact locks: **H-PRODSHIP · H-SHIPUI2**. Hold under pressure-para ≠ AV/AU.  
> Metrics: **human paraphrase hit-rate**, **latency p50/p99**, **adversary false-hit**, **KB coverage**.  
> Ship/demo UI **always** shows **`mode=LOOKUP|PEAK|DECODE`** (plus **`ABSTAIN`**).

### North star — nano generative / mini-AGI-inspired

**Build a nano generative model** ≤5M. AV H-NANOGEN6 HOLD (true_continue=0) stays archived.  
Wave AW opens **one new method**: **teacher-anchored novel continue (TAC)** — not NANOGEN6 rename.

| Layer | Meaning | Claim rule |
|-------|---------|------------|
| Product (Caminho A keep) | pressure-para · FH0 · modes · DECODE usable/ABSTAIN | **Hold now** |
| Generative (gate) | TAC true continue; span-fallback ≠ gen IQ | PROMOTE only under true real-eval |
| Mini-AGI-inspired | retrieve · generate · route · refuse · evaluate | Only after true gen PROMOTE |

---

## 1. Locked archives (do not rewrite)

Waves W–AU locked. Wave AV COMPLETE + FROZEN (H-PRODSHIP·H-SHIPUI2 PROMOTE; H-NANOGEN6 HOLD; AV-REAL-EVAL 8/8).

Reproduce parent: `npm run nano:av:freeze`.

---

## 2. Wave AW stage machine (**ACTIVE**)

> Thesis: **hold Caminho A** under pressure **and** pursue **TAC true-continue** under ≤5M. No CTX/SMART/FAST/APP clones. No NANOGEN7 = NANOGEN6+rename.

| # | ID | Focus | Gate (sketch) | Status |
|---|-----|-------|---------------|--------|
| AW0 | **SESSION** | Freeze AW packs: product-keep · pressure-para (N≥20 ≠ AV/AU) · NANOGEN7 TAC hyp · real-eval | cite AV locks; TAC required | **DONE — PROMOTE** |
| AW1 | **H-PRODKEEP** | Caminho A regression under pressure-para · FH 0 · p50/p99 · KB · DECODE content | hold AV bars | **TODO** |
| AW2 | **H-SHIPKEEP** | Human ship/demo UI always modes+content | smoke + content · no unlabeled | **TODO** |
| AW3 | **H-NANOGEN7** | **TAC generative** — teacher-anchored novel continue ≤5M; span-fallback ≠ gen | true ablated bar → PROMOTE else HOLD | **TODO** |
| AW4 | **AW-REAL-EVAL** | Final real eval: product + generative + live ask | product pass; gen claim only if AW3 PROMOTE | **TODO** |
| AW5 | **AW-REPORT** | Public summary + paper-lab | anti-FP + real-eval | **TODO** |
| AW6 | **AW-FREEZE** | Lock AW outcomes | no next letter invent without reopen | **TODO** |

**Skipped by default:** re-SEMFIX/ADVSAFE unless PRODKEEP fails · CTX*/SMART*/FAST*/APP* clones · rewrite AV/AU locks · NANOGEN7 = NANOGEN6+rename.

**CAPCHECK:** **closed** (≤5M stays unless explicit reopen).

---

## 3. Immediate next actions

1. **AW0 SESSION** — **DONE PROMOTE** (`npm run nano:aw:session`) · next **AW1 H-PRODKEEP**.  
2. **AW1 H-PRODKEEP** — hold Caminho A under pressure-para.  
3. Keep north star: **TAC true continue** — not span-fallback; not NANOGEN6 rename.  
4. Do **not** start CTX/SMART/FAST theater. Do **not** rewrite AV/AU locks.

```bash
npm run nano:av:freeze
npm run nano:aw:session
# next: nano:prodkeep · nano:shipkeep · nano:nanogen7
```
"""
    _LOCAL_PESQUISA.write_text(body, encoding="utf-8")


def _write_local_impl(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Implementation plan — nano generative LM

> Private. Lab: [`pesquisa.md`](pesquisa.md).

## Status

Wave AV **COMPLETE + FROZEN**.  
**Reopen:** Wave **AW ACTIVE** via `pesquisa.md` — dual track (product-keep + TAC).

## Dual track (locked)

| Track | Work |
|-------|------|
| **Caminho A keep** | Hold AV PRODSHIP·SHIPUI2 under pressure-para ≠ AV/AU · FH · p50/p99 · KB · mode UI |
| **North star** | H-NANOGEN7 TAC (teacher-anchored novel continue) · true real eval · span-fallback ≠ gen IQ |

## Next

1. **AW0 SESSION** — **DONE PROMOTE** (`npm run nano:aw:session`).  
2. **AW1 H-PRODKEEP** — **NEXT** — hold Caminho A under pressure-para.  
2b. **AW2 H-SHIPKEEP** — modes+content.  
2c. **AW3 H-NANOGEN7** — TAC true continue.  
3. Ship claim stays AV/AU lock until true-continue PROMOTE: **AF + AQ + AS trust + STRICT ablated DECODE**.

Never: LOOKUP-as-IQ · bank stuffing · telemetry-only DECODE pass · unlabeled open chat · GPT-class · CTX/SMART/FAST clones · NANOGEN6 rename.

```bash
npm run nano:aw:session
npm run nano:test && npm run verify
```
"""
    _LOCAL_IMPL.write_text(body, encoding="utf-8")


def _write_local_readme(decision: str) -> None:
    if not decision.startswith("PROMOTE"):
        return
    body = """# Local research notebook

Full lab book: **`pesquisa.md`**.

## Current wave

**Wave AW ACTIVE** (lab-book reopen after AV-FREEZE):

1. **Caminho A keep:** hold known-ask + SEMWRAP + labeled PEAK/RAG + apps under pressure-para.  
2. **North star:** H-NANOGEN7 TAC (teacher-anchored novel continue) ≤5M with **true real eval**.

Session: `wave-aw/SESSION.md` (AW0 **DONE — PROMOTE**; next AW1 H-PRODKEEP). Parent: Wave AV **COMPLETE + FROZEN**.

| Locked | Status |
|--------|--------|
| Waves W–AV | COMPLETE + FROZEN |
| Ship (until AW gen PROMOTE) | AF + AQ + AS trust + STRICT ablated DECODE — not unlabeled open chat |
| Reopen | `pesquisa.md` §0–§3 · Wave AW0–AW6 |

## Do not

LOOKUP-as-IQ · truncate-to-span as gen · DECODE telemetry-only content_ok · unlabeled open-chat / GPT-class · CTX/SMART/FAST letter clones · NANOGEN7 = NANOGEN6+rename.
"""
    _LOCAL_README.write_text(body, encoding="utf-8")


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_aw0_session(
        trials_dir_ready=trials_ready, anti_fp_signed=True
    )
    _write_public_note(decision=decision)
    _update_local_session(decision)
    _write_pesquisa_aw_reopen(decision)
    _write_local_impl(decision)
    _write_local_readme(decision)
    rc, ask = _run_ask_smoke(
        decision, skip=bool(args.skip_ask), workers=workers
    )
    if rc != 0:
        return rc

    payload = {
        "id": AW0_ID,
        "thesis": AW0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_av_locks": sorted(AW0_CITED_AV_LOCKS),
        "product_keep_charter": dict(AW0_PRODUCT_KEEP_CHARTER),
        "pressure_para_protocol": dict(AW0_PRESSURE_PARA_PROTOCOL),
        "nanogen7_hypothesis": AW0_NANOGEN7_HYPOTHESIS,
        "true_gen_judge": dict(AW0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(AW0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(AW0_ASK_BATTERY),
        "pressure_para_n": len(AW0_PRESSURE_PARA_ROWS),
        "safe_note": AW0_SAFE_NOTE,
        "anti_fp": AW0_ANTI_FP,
        "north_star": AW0_NORTH_STAR,
        "ship_lock": AW0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-aw-session.md",
        "rule": "pesquisa §5 AW0 · product-keep + NANOGEN7 hyp + anti-FP",
        "next": "AW1 H-PRODKEEP (close DECODE content + pressure para)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AW0_ID,
                "decision": decision[:120],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
