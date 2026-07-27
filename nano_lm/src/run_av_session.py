"""Wave AV0 SESSION runner (nano:av:session) — freeze AV packs + charters."""

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
from av_session_ops import (
    AV0_ANTI_FP,
    AV0_ASK_BATTERY,
    AV0_CITED_AU_LOCKS,
    AV0_EXTERNAL_PARA_PROTOCOL,
    AV0_EXTERNAL_PARA_ROWS,
    AV0_ID,
    AV0_MODES,
    AV0_NANOGEN6_HYPOTHESIS,
    AV0_NORTH_STAR,
    AV0_PRODUCT_SHIP_CHARTER,
    AV0_REAL_EVAL_PROTOCOL,
    AV0_SAFE_NOTE,
    AV0_SHIP_LOCK,
    AV0_THESIS,
    AV0_TRUE_GEN_JUDGE,
    decide_av0_session,
    map_av_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-av/av0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-av/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-av/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-av-session.md"
_LOCAL_SESSION = REPO / ".local/wave-av/SESSION.md"
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
    for item in AV0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AV0",
            "hyp_id": AV0_ID,
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
    for item in AV0_EXTERNAL_PARA_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AV0",
            "hyp_id": AV0_ID,
            "pack": "external-para",
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
        ("AV-PRODSHIP", "product-ship-charter", dict(AV0_PRODUCT_SHIP_CHARTER)),
        (
            "AV-EXTERNAL-PARA",
            "external-para-protocol",
            dict(AV0_EXTERNAL_PARA_PROTOCOL),
        ),
        (
            "AV-NANOGEN6",
            "nanogen6-hypothesis",
            {
                "hypothesis": AV0_NANOGEN6_HYPOTHESIS,
                "true_gen_judge": dict(AV0_TRUE_GEN_JUDGE),
            },
        ),
        (
            "AV-REAL-EVAL",
            "real-eval-protocol",
            dict(AV0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "AV0",
            "hyp_id": AV0_ID,
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
    need = len(AV0_ASK_BATTERY) + len(AV0_EXTERNAL_PARA_ROWS) + 4
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in AV0_ASK_BATTERY
    )
    para_rows = "\n".join(
        f"| {p['id']} | {p['parent']} |" for p in AV0_EXTERNAL_PARA_ROWS
    )
    bars = AV0_PRODUCT_SHIP_CHARTER["bars"]
    debts = AV0_PRODUCT_SHIP_CHARTER["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    body = "\n".join(
        [
            "# Wave AV0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-av/SESSION.md`  ",
            "> Module: `nano_lm/src/av_session_ops.py` · "
            "Runner: `npm run nano:av:session`  ",
            "> Parent: [au-freeze.md](au-freeze.md) "
            "(Wave AV reopened explicitly via lab-book reopen)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze AV packs: "
            "product-ship charter · external-para protocol (N≥20 ≠ AU) · "
            "NANOGEN6 hyp (true continue; **span-fallback ≠ gen IQ**) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone · "
            "**not** NANOGEN5+rename.  ",
            "Anti-FP signed. Generative claim locked until AV3 PROMOTE.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Product-ship charter | 1 | DECODE content · external para · "
            "FH0 · modes · KB · latency (AV1) |",
            f"| External-para protocol | {len(AV0_EXTERNAL_PARA_ROWS)} | "
            "held-out ≠ AU · no bank stuffing (AV1) |",
            "| NANOGEN6 hypothesis | 1 | refuse-or-continue · "
            "span-fallback = PEAK/LOOKUP credit only (AV3) |",
            "| True gen judge | 1 | span-fallback ≠ gen · "
            "telemetry ≠ content_ok (AV3) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "anti-FP (AV4) |",
            f"| Ask battery | {len(AV0_ASK_BATTERY)} | frozen live rows "
            "(scored at AV4) |",
            "",
            "## Cited AU locks",
            "",
            ", ".join(sorted(AV0_CITED_AU_LOCKS)),
            "",
            "## Product-ship bars",
            "",
            f"- para_hit_min: **{bars['para_hit_min']}** "
            "(AU PRODHARD baseline 1.0)  ",
            f"- false_hit_max: **{bars['false_hit_max']}**  ",
            f"- external_para_min_n: **{bars['external_para_min_n']}**  ",
            f"- decode_gibberish_neq_content_ok: "
            f"**{bars['decode_gibberish_neq_content_ok']}**  ",
            f"- default_ask_near_miss: **{bars['default_ask_near_miss']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no re-SEMFIX/ADVSAFE unless PRODSHIP fails",
            "",
            "## Post-AU debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## External-para protocol",
            "",
            f"- held_out: **{AV0_EXTERNAL_PARA_PROTOCOL['held_out']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{AV0_EXTERNAL_PARA_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- neq_au_pack: **{AV0_EXTERNAL_PARA_PROTOCOL['neq_au_pack']}**  ",
            f"- min_n: **{AV0_EXTERNAL_PARA_PROTOCOL['min_n']}**  ",
            f"- path: `{AV0_EXTERNAL_PARA_PROTOCOL['path']}`  ",
            "",
            "| id | parent |",
            "|----|--------|",
            para_rows,
            "",
            "## NANOGEN6 hypothesis (one idea)",
            "",
            AV0_NANOGEN6_HYPOTHESIS,
            "",
            "## True gen judge",
            "",
            f"- span_fallback_neq_gen: "
            f"{AV0_TRUE_GEN_JUDGE['span_fallback_neq_gen']}  ",
            f"- gold_substring_insufficient: "
            f"{AV0_TRUE_GEN_JUDGE['gold_substring_insufficient']}  ",
            f"- gibberish_tail_fails: "
            f"{AV0_TRUE_GEN_JUDGE['gibberish_tail_fails']}  ",
            f"- telemetry_neq_content_ok: "
            f"{AV0_TRUE_GEN_JUDGE['telemetry_neq_content_ok']}  ",
            f"- scoring: `{AV0_TRUE_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{AV0_TRUE_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{AV0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{AV0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- span_fallback_neq_gen: "
            f"{AV0_REAL_EVAL_PROTOCOL['span_fallback_neq_gen']}  ",
            f"- gen_claim_rule: "
            f"{AV0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {AV0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            AV0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AV0_ANTI_FP,
            "",
            "## North star",
            "",
            AV0_NORTH_STAR,
            "",
            "## Ship lock (until AV PROMOTE)",
            "",
            AV0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:av:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`); near-miss maps to ABSTAIN alias.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-av/av0_session.json` · "
            "`results/nano-lm/wave-av/trials/AV-*.json`.  ",
            "Contract: `nano_lm/tests/test_av_session.py`.",
            "",
            "## Claims",
            "",
            "- AV packs frozen for Wave AV — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{AV0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **AV3 H-NANOGEN6** "
            "true_continue_ablated (span-fallback ≠ gen credit).  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "gold-substring PROMOTE · truncate-to-span as gen · "
            "DECODE telemetry-only content_ok · eval↔prod gap · "
            "mini-AGI claim early · Wave AW invent · CTX/SMART/FAST/APP "
            "clone · NANOGEN5+rename · bank stuffing · vanity re-SEMFIX.",
            "",
            "Next: **AV1 H-PRODSHIP** — accept Caminho A; close DECODE "
            "content debt; publish external para · FH · p50/p99 · KB.",
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
        map_av_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        nm_mode in AV0_MODES,
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
    l_mode = map_av_product_mode(str(l_tel["mode"]))
    g_mode = map_av_product_mode(str(g_tel["mode"]))
    nm_mode = map_av_product_mode(str(n_tel["mode"]))
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
            "note": "AV1 must fail gibberish content_ok; AV0 freezes bar",
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AU PRODHARD locked ABSTAIN; AV0 verifies mapping",
        },
        "modes_charter": sorted(AV0_MODES),
        "abstain_alias": map_av_product_mode("NO_ANSWER"),
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
            f"# Wave AV session checklist (**OPEN** · AV0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AV **OPEN** · Caminho A ship + Nano Generative).  ",
            f"> Parent: AU COMPLETE + FROZEN · Ship: **{AV0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after AU-FREEZE; product ship open; "
            "generative needs true continue beyond NANOGEN5 truncate bar.",
            "",
            "## Current stage",
            "",
            f"**AV0 — SESSION ({status})** · Next: **AV1 H-PRODSHIP**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AV OPEN** |",
            "| Track | Caminho A product-ship · "
            "**H-NANOGEN6** north star |",
            "| Parent | AU COMPLETE + FROZEN |",
            "| Open hole | DECODE content · external para N≥20 · "
            "true continue (no span-fallback gen) |",
            "| Forbidden | vanity re-SEMFIX · LOOKUP-as-IQ · "
            "truncate-as-gen · NANOGEN5+rename · Wave AW invent |",
            "",
            "## North star (signed)",
            "",
            AV0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AV0)",
            "",
            "```text",
            "MODEL = AV0-SESSION",
            "",
            "[x] Freeze product-ship charter (DECODE content · external "
            "para · FH0 · modes · KB · latency)",
            "[x] Freeze external-para held-out protocol (N≥20 ≠ AU)",
            "[x] Write ONE NANOGEN6 hypothesis (true continue; "
            "span-fallback ≠ gen)",
            "[x] Freeze true gen judge (telemetry ≠ content_ok)",
            "[x] Real-eval ask battery protocol (eval=prod ask)",
            "[x] Do NOT reopen SEMFIX/ADVSAFE unless PRODSHIP fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[x] Do NOT clone NANOGEN5 5.5 truncate bar as NANOGEN6",
            "[ ] Next: AV1 H-PRODSHIP",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AV0 | SESSION | **{status}** |",
            "| AV1 | H-PRODSHIP | **NEXT** |",
            "| AV2 | H-SHIPUI2 | pending |",
            "| AV3 | H-NANOGEN6 | pending (generative north-star gate) |",
            "| AV4 | AV-REAL-EVAL | pending |",
            "| AV5 | AV-REPORT | pending |",
            "| AV6 | AV-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| External para hit | ≥ 0.70 | AU PRODHARD **1.0**/8 (≠ set) |",
            "| Adversary FH (ask path) | **0** | AS ADVSAFE **0**/20 |",
            "| DECODE content | usable or ABSTAIN | AU-ASK-05 debt |",
            "| Latency p50/p99 | publish | AU PRODHARD / AS METRICS |",
            "| True continue (NANOGEN6) | PROMOTE else HOLD | "
            "NANOGEN5 truncate bar **archived** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa_av0(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    old = (
        "| AV0 | **SESSION** | Freeze AV packs: product ship charter · "
        "external-para protocol · true-gen hypothesis (**one idea**) · "
        "real-eval forbidding span-fallback-as-IQ | cite AU locks; "
        "gen hypothesis required | **TODO** |"
    )
    new = (
        "| AV0 | **SESSION** | Freeze AV packs: product ship charter · "
        "external-para protocol · true-gen hypothesis (**one idea**) · "
        "real-eval forbidding span-fallback-as-IQ | cite AU locks; "
        "gen hypothesis required | **DONE — PROMOTE** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = (
        "1. **AV0 SESSION** — create `.local/wave-av/SESSION.md`; freeze "
        "product-ship charter + external-para protocol + **one** NANOGEN6 "
        "hypothesis that is **not** truncate-bar clone + true real-eval "
        "judge.  "
    )
    new_next = (
        "1. **AV0 SESSION** — **DONE PROMOTE** (`npm run nano:av:session`) · "
        "next **AV1 H-PRODSHIP**.  "
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    bash_old = (
        "# after AV0 wiring:\n"
        "# npm run nano:av:session"
    )
    bash_new = (
        "npm run nano:av:session\n"
        "# next: nano:prodship · nano:shipui2 · nano:nanogen6 "
        "(as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def _patch_local_impl(decision: str) -> None:
    if not _LOCAL_IMPL.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_IMPL.read_text(encoding="utf-8")
    old = (
        "1. **AV0 SESSION** — packs + one NANOGEN6 hypothesis "
        "(not AU truncate clone).  \n"
        "2. **AV1 H-PRODSHIP** — ship Caminho A; close DECODE content "
        "debt; external human para.  "
    )
    new = (
        "1. **AV0 SESSION** — **DONE PROMOTE** (`npm run nano:av:session`).  \n"
        "2. **AV1 H-PRODSHIP** — **NEXT** — ship Caminho A; close DECODE "
        "content debt; external human para.  "
    )
    if old in text:
        text = text.replace(old, new, 1)
    _LOCAL_IMPL.write_text(text, encoding="utf-8")


def _patch_local_readme(decision: str) -> None:
    if not _LOCAL_README.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_README.read_text(encoding="utf-8")
    old = "Session: `wave-av/SESSION.md` (create at AV0)."
    new = (
        "Session: `wave-av/SESSION.md` (AV0 **DONE — PROMOTE**; "
        "next AV1 H-PRODSHIP)."
    )
    if old in text:
        text = text.replace(old, new, 1)
        _LOCAL_README.write_text(text, encoding="utf-8")


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_av0_session(
        trials_dir_ready=trials_ready, anti_fp_signed=True
    )
    _write_public_note(decision=decision)
    _update_local_session(decision)
    _patch_pesquisa_av0(decision)
    _patch_local_impl(decision)
    _patch_local_readme(decision)
    rc, ask = _run_ask_smoke(
        decision, skip=bool(args.skip_ask), workers=workers
    )
    if rc != 0:
        return rc

    payload = {
        "id": AV0_ID,
        "thesis": AV0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_au_locks": sorted(AV0_CITED_AU_LOCKS),
        "product_ship_charter": dict(AV0_PRODUCT_SHIP_CHARTER),
        "external_para_protocol": dict(AV0_EXTERNAL_PARA_PROTOCOL),
        "nanogen6_hypothesis": AV0_NANOGEN6_HYPOTHESIS,
        "true_gen_judge": dict(AV0_TRUE_GEN_JUDGE),
        "real_eval_protocol": dict(AV0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(AV0_ASK_BATTERY),
        "external_para_n": len(AV0_EXTERNAL_PARA_ROWS),
        "safe_note": AV0_SAFE_NOTE,
        "anti_fp": AV0_ANTI_FP,
        "north_star": AV0_NORTH_STAR,
        "ship_lock": AV0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-av-session.md",
        "rule": "pesquisa §5 AV0 · product-ship + NANOGEN6 hyp + anti-FP",
        "next": "AV1 H-PRODSHIP (close DECODE content + external para)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AV0_ID,
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
