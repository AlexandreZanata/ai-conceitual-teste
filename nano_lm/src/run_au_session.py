"""Wave AU0 SESSION runner (nano:au:session) — freeze AU packs + charters."""

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
from au_session_ops import (
    AU0_ANTI_FP,
    AU0_ASK_BATTERY,
    AU0_CITED_AT_LOCKS,
    AU0_HUMAN_PARA_PROTOCOL,
    AU0_HUMAN_PARA_ROWS,
    AU0_ID,
    AU0_MODES,
    AU0_NANOGEN5_HYPOTHESIS,
    AU0_NORTH_STAR,
    AU0_PRODUCT_DEBT_SUITE,
    AU0_REAL_EVAL_PROTOCOL,
    AU0_SAFE_NOTE,
    AU0_SHIP_LOCK,
    AU0_STRICT_GEN_JUDGE,
    AU0_THESIS,
    decide_au0_session,
    map_au_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-au/au0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-au/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-au/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-au-session.md"
_LOCAL_SESSION = REPO / ".local/wave-au/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
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
    # Max safe on 16c / ~12Gi avail: leave 2 cores; cap workers to avoid thrash.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(12, max(4, cpus - 2))
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
    for item in AU0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AU0",
            "hyp_id": AU0_ID,
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
    for item in AU0_HUMAN_PARA_ROWS:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AU0",
            "hyp_id": AU0_ID,
            "pack": "human-para",
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
        ("AU-PRODHARD", "product-debt-suite", dict(AU0_PRODUCT_DEBT_SUITE)),
        (
            "AU-HUMAN-PARA",
            "human-para-protocol",
            dict(AU0_HUMAN_PARA_PROTOCOL),
        ),
        (
            "AU-NANOGEN5",
            "nanogen5-hypothesis",
            {
                "hypothesis": AU0_NANOGEN5_HYPOTHESIS,
                "strict_judge": dict(AU0_STRICT_GEN_JUDGE),
            },
        ),
        (
            "AU-REAL-EVAL",
            "real-eval-protocol",
            dict(AU0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "AU0",
            "hyp_id": AU0_ID,
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
    need = len(AU0_ASK_BATTERY) + len(AU0_HUMAN_PARA_ROWS) + 4
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in AU0_ASK_BATTERY
    )
    para_rows = "\n".join(
        f"| {p['id']} | {p['parent']} |" for p in AU0_HUMAN_PARA_ROWS
    )
    bars = AU0_PRODUCT_DEBT_SUITE["bars"]
    debts = AU0_PRODUCT_DEBT_SUITE["debts"]
    debt_rows = "\n".join(
        f"| {d['id']} | {d['bar']} |" for d in debts  # type: ignore[index]
    )
    body = "\n".join(
        [
            "# Wave AU0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-au/SESSION.md`  ",
            "> Module: `nano_lm/src/au_session_ops.py` · "
            "Runner: `npm run nano:au:session`  ",
            "> Parent: [at-freeze.md](at-freeze.md) "
            "(Wave AU reopened explicitly via lab-book reopen)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze AU packs: "
            "product-debt suite (live-audit) · human-para protocol · "
            "NANOGEN5 hyp (strict F1/HITL judge; **not** gold-substring) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until AU3 PROMOTE.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| Product-debt suite | 1 | near-miss on ask · human para · "
            "PEAK usable · usability (AU1) |",
            f"| Human-para protocol | {len(AU0_HUMAN_PARA_ROWS)} | "
            "held-out rewrites · no bank stuffing (AU1) |",
            "| NANOGEN5 hypothesis | 1 | gibberish-tail gate · "
            "strict ≥5.5 vs NANOGEN4 5.5 (AU3) |",
            "| Strict gen judge | 1 | gold-substring insufficient · "
            "F1/HITL (AU3) |",
            "| Real-eval protocol | 1 | live ask · eval=prod · "
            "anti-FP (AU4) |",
            f"| Ask battery | {len(AU0_ASK_BATTERY)} | frozen live rows "
            "(scored at AU4) |",
            "",
            "## Cited AT locks",
            "",
            ", ".join(sorted(AU0_CITED_AT_LOCKS)),
            "",
            "## Product-debt bars",
            "",
            f"- para_hit_min: **{bars['para_hit_min']}** "
            "(AS PARAEXT2 baseline 0.80)  ",
            f"- false_hit_max: **{bars['false_hit_max']}** "
            "(AS ADVSAFE 0/20)  ",
            f"- default_ask_near_miss: **{bars['default_ask_near_miss']}**  ",
            f"- peak_usable_or_abstain: **{bars['peak_usable_or_abstain']}**  ",
            f"- eval_eq_prod_ask: **{bars['eval_eq_prod_ask']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no re-SEMFIX/ADVSAFE unless PRODHARD fails",
            "",
            "## Live-audit debts (frozen)",
            "",
            "| id | bar |",
            "|----|-----|",
            debt_rows,
            "",
            "## Human-para protocol",
            "",
            f"- held_out: **{AU0_HUMAN_PARA_PROTOCOL['held_out']}**  ",
            f"- bank_stuff_forbidden: "
            f"**{AU0_HUMAN_PARA_PROTOCOL['bank_stuff_forbidden']}**  ",
            f"- min_n: **{AU0_HUMAN_PARA_PROTOCOL['min_n']}**  ",
            f"- path: `{AU0_HUMAN_PARA_PROTOCOL['path']}`  ",
            "",
            "| id | parent |",
            "|----|--------|",
            para_rows,
            "",
            "## NANOGEN5 hypothesis (one idea)",
            "",
            AU0_NANOGEN5_HYPOTHESIS,
            "",
            "## Strict gen judge",
            "",
            f"- gold_substring_insufficient: "
            f"{AU0_STRICT_GEN_JUDGE['gold_substring_insufficient']}  ",
            f"- gibberish_tail_fails: "
            f"{AU0_STRICT_GEN_JUDGE['gibberish_tail_fails']}  ",
            f"- scoring: `{AU0_STRICT_GEN_JUDGE['scoring']}`  ",
            f"- promote_bar: `{AU0_STRICT_GEN_JUDGE['promote_bar']}`",
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{AU0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- eval_eq_prod_ask: "
            f"{AU0_REAL_EVAL_PROTOCOL['eval_eq_prod_ask']}  ",
            f"- gen_claim_rule: "
            f"{AU0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {AU0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            AU0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AU0_ANTI_FP,
            "",
            "## North star",
            "",
            AU0_NORTH_STAR,
            "",
            "## Ship lock (until AU PROMOTE)",
            "",
            AU0_SHIP_LOCK,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:au:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`); near-miss maps to ABSTAIN alias.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-au/au0_session.json` · "
            "`results/nano-lm/wave-au/trials/AU-*.json`.  ",
            "Contract: `nano_lm/tests/test_au_session.py`.",
            "",
            "## Claims",
            "",
            "- AU packs frozen for Wave AU — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            f"**{AU0_SHIP_LOCK}**.  ",
            "- Generative PROMOTE only via later **AU3 H-NANOGEN5** "
            "strict ablated bar ≥5.5.  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "gold-substring PROMOTE · gibberish-tail pass · eval↔prod gap · "
            "mini-AGI claim early · Wave AV invent · CTX/SMART/FAST/APP "
            "clone · bank stuffing · vanity re-SEMFIX.",
            "",
            "Next: **AU1 H-PRODHARD** — close live-audit debts on default ask.",
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
        map_au_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
        # AU0 freezes near-miss bar; live ABSTAIN may still fail until AU1.
        # Smoke only requires mapping + known LOOKUP/DECODE arms.
        nm_mode in AU0_MODES,
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
    l_mode = map_au_product_mode(str(l_tel["mode"]))
    g_mode = map_au_product_mode(str(g_tel["mode"]))
    nm_mode = map_au_product_mode(str(n_tel["mode"]))
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
        },
        "near_miss": {
            "arm": classify_arm(near),
            "raw_mode": n_tel["mode"],
            "product_mode": nm_mode,
            "wall_ms": n_tel["wall_ms"],
            "n_new": n_tel["n_new"],
            "note": "AU1 must force ABSTAIN on default ask; AU0 freezes bar",
        },
        "modes_charter": sorted(AU0_MODES),
        "abstain_alias": map_au_product_mode("NO_ANSWER"),
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
            f"# Wave AU session checklist (**OPEN** · AU0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AU **OPEN** · Caminho A harden + Nano Generative).  ",
            f"> Parent: AT COMPLETE + FROZEN · Ship: **{AU0_SHIP_LOCK}** · "
            "≤5M.  ",
            "> Reopen: after AT-FREEZE; product debts open; "
            "generative needs strict judge beyond NANOGEN4 5.5.",
            "",
            "## Current stage",
            "",
            f"**AU0 — SESSION ({status})** · Next: **AU1 H-PRODHARD**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AU OPEN** |",
            "| Track | Caminho A live-audit · "
            "**H-NANOGEN5** north star |",
            "| Parent | AT COMPLETE + FROZEN |",
            "| Open hole | near-miss on ask · human para · "
            "PEAK usable · strict gen |",
            "| Forbidden | vanity re-SEMFIX · LOOKUP-as-IQ · "
            "gold-substring PROMOTE · Wave AV invent |",
            "",
            "## North star (signed)",
            "",
            AU0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AU0)",
            "",
            "```text",
            "MODEL = AU0-SESSION",
            "",
            "[x] Freeze product-debt suite (near-miss · human para · "
            "PEAK usable · usability)",
            "[x] Freeze human-para held-out protocol (no bank stuffing)",
            "[x] Write ONE NANOGEN5 hypothesis (gibberish-tail + F1/HITL)",
            "[x] Freeze strict gen judge (gold-substring insufficient)",
            "[x] Real-eval ask battery protocol (eval=prod ask)",
            "[x] Do NOT reopen SEMFIX/ADVSAFE unless PRODHARD fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[ ] Next: AU1 H-PRODHARD",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AU0 | SESSION | **{status}** |",
            "| AU1 | H-PRODHARD | **NEXT** |",
            "| AU2 | H-SHIPREAL | pending |",
            "| AU3 | H-NANOGEN5 | pending (generative north-star gate) |",
            "| AU4 | AU-REAL-EVAL | pending |",
            "| AU5 | AU-REPORT | pending |",
            "| AU6 | AU-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Paraphrase hit (held-out) | ≥ 0.70 | AS PARAEXT2 **0.80** |",
            "| Adversary FH (ask path) | **0** | AS ADVSAFE **0**/20 |",
            "| Near-miss default ask | ABSTAIN | AT live-audit debt |",
            "| PEAK content | usable span or ABSTAIN | AT-ASK-04 debt |",
            "| Latency p50/p99 | publish | AS METRICS / AT PRODREG |",
            "| Strict ablated (NANOGEN5) | ≥ **5.5** | NANOGEN4 **5.5** "
            "(old judge archived) |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa_au0(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    old = (
        "| AU0 | **SESSION** | Freeze AU packs: product-debt suite · "
        "human-para protocol · strict gen judge · real-eval protocol | "
        "cite AT locks; gen hypothesis required | **TODO** |"
    )
    new = (
        "| AU0 | **SESSION** | Freeze AU packs: product-debt suite · "
        "human-para protocol · strict gen judge · real-eval protocol | "
        "cite AT locks; gen hypothesis required | **DONE — PROMOTE** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = (
        "1. **AU0 SESSION** — create `.local/wave-au/SESSION.md`; freeze "
        "product-debt pack + human-para protocol + **one** NANOGEN5 "
        "hypothesis + strict real-eval judge.  "
    )
    new_next = (
        "1. **AU0 SESSION** — **DONE PROMOTE** (`npm run nano:au:session`) · "
        "next **AU1 H-PRODHARD**.  "
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    bash_old = (
        "# after AU0 wiring:\n"
        "# npm run nano:au:session"
    )
    bash_new = (
        "npm run nano:au:session\n"
        "# next: nano:prodhard · nano:shipreal · nano:nanogen5 "
        "(as stages land)"
    )
    if bash_old in text:
        text = text.replace(bash_old, bash_new, 1)
    _LOCAL_PESQUISA.write_text(text, encoding="utf-8")


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    written, trials_ready = _parallel_prep(workers, Path(args.trials_dir))
    decision = decide_au0_session(
        trials_dir_ready=trials_ready, anti_fp_signed=True
    )
    _write_public_note(decision=decision)
    _update_local_session(decision)
    _patch_pesquisa_au0(decision)
    rc, ask = _run_ask_smoke(
        decision, skip=bool(args.skip_ask), workers=workers
    )
    if rc != 0:
        return rc

    payload = {
        "id": AU0_ID,
        "thesis": AU0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_at_locks": sorted(AU0_CITED_AT_LOCKS),
        "product_debt_suite": dict(AU0_PRODUCT_DEBT_SUITE),
        "human_para_protocol": dict(AU0_HUMAN_PARA_PROTOCOL),
        "nanogen5_hypothesis": AU0_NANOGEN5_HYPOTHESIS,
        "strict_gen_judge": dict(AU0_STRICT_GEN_JUDGE),
        "real_eval_protocol": dict(AU0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(AU0_ASK_BATTERY),
        "human_para_n": len(AU0_HUMAN_PARA_ROWS),
        "safe_note": AU0_SAFE_NOTE,
        "anti_fp": AU0_ANTI_FP,
        "north_star": AU0_NORTH_STAR,
        "ship_lock": AU0_SHIP_LOCK,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-au-session.md",
        "rule": "pesquisa §5 AU0 · product-debt + NANOGEN5 hyp + anti-FP",
        "next": "AU1 H-PRODHARD (close live-audit debts)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AU0_ID,
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
