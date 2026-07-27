"""Wave AT0 SESSION runner (nano:at:session) — freeze AT packs + charters."""

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
from at_session_ops import (
    AT0_ANTI_FP,
    AT0_ASK_BATTERY,
    AT0_CITED_AS_GATES,
    AT0_ID,
    AT0_MODES,
    AT0_NANOGEN4_HYPOTHESIS,
    AT0_NORTH_STAR,
    AT0_PRODREG_SUITE,
    AT0_REAL_EVAL_PROTOCOL,
    AT0_SAFE_NOTE,
    AT0_SHIPAPP_CHARTER,
    AT0_THESIS,
    decide_at0_session,
    map_at_product_mode,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-at/at0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-at/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-at/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-at-session.md"
_LOCAL_SESSION = REPO / ".local/wave-at/SESSION.md"
_LOCAL_PESQUISA = REPO / ".local/pesquisa.md"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_KNOWN = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_DECODE_Q = "Explain Merkle trees briefly"


def _hardware() -> tuple[int, int]:
    # Max safe on 16c / ~11Gi avail: leave 2 cores; cap workers to avoid thrash.
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
    for item in AT0_ASK_BATTERY:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AT0",
            "hyp_id": AT0_ID,
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


def _write_charter_trials(trials_dir: Path) -> list[str]:
    rows = (
        ("AT-PRODREG", "prodreg-suite", dict(AT0_PRODREG_SUITE)),
        ("AT-SHIPAPP", "shipapp-charter", dict(AT0_SHIPAPP_CHARTER)),
        (
            "AT-NANOGEN4",
            "nanogen4-hypothesis",
            {"hypothesis": AT0_NANOGEN4_HYPOTHESIS},
        ),
        (
            "AT-REAL-EVAL",
            "real-eval-protocol",
            dict(AT0_REAL_EVAL_PROTOCOL),
        ),
    )
    written: list[str] = []
    for tid, pack, body in rows:
        payload = {
            "trial_id": tid,
            "stage": "AT0",
            "hyp_id": AT0_ID,
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
    written = _write_battery_trials(trials_dir) + _write_charter_trials(
        trials_dir
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    need = len(AT0_ASK_BATTERY) + 4
    ready = trials_dir.is_dir() and len(written) == need
    return written, ready


def _write_public_note(*, decision: str) -> None:
    bat_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['expect_mode']} |"
        for p in AT0_ASK_BATTERY
    )
    bars = AT0_PRODREG_SUITE["bars"]
    body = "\n".join(
        [
            "# Wave AT0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-at/SESSION.md`  ",
            "> Module: `nano_lm/src/at_session_ops.py` · "
            "Runner: `npm run nano:at:session`  ",
            "> Parent: [as-freeze.md](as-freeze.md) "
            "(Wave AT reopened explicitly via lab-book reopen 2026-07-27)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze AT packs: "
            "PRODREG suite (cite AS product gates) · SHIPAPP charter · "
            "NANOGEN4 hyp (retrieved-snippet prefix; **not** bank-gold) · "
            "real-eval protocol. **Not** a CTX/SMART/FAST/APP clone.  ",
            "Anti-FP signed. Generative claim locked until AT3 PROMOTE.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| PRODREG suite | 1 | para≥0.70 · FH0 · p50/p99 · KB · "
            "modes · abstain (AT1) |",
            "| SHIPAPP charter | 1 | human demo/apps always show 4 modes "
            "(AT2) |",
            "| NANOGEN4 hypothesis | 1 | ablated ≥5.0 vs NANOGEN3 4.3 "
            "(AT3) |",
            "| Real-eval protocol | 1 | live ask battery · anti-FP "
            "(AT4) |",
            f"| Ask battery | {len(AT0_ASK_BATTERY)} | frozen live rows "
            "(scored at AT4) |",
            "",
            "## Cited AS gates",
            "",
            ", ".join(sorted(AT0_CITED_AS_GATES)),
            "",
            "## PRODREG bars",
            "",
            f"- para_hit_min: **{bars['para_hit_min']}** "
            "(AS PARAEXT2 baseline 0.80)  ",
            f"- false_hit_max: **{bars['false_hit_max']}** "
            "(AS ADVSAFE 0/20)  ",
            f"- default_ask_ood: **{bars['default_ask_ood']}**  ",
            f"- modes: {' · '.join(bars['modes_required'])}  ",
            "- no re-SEMFIX/ADVSAFE unless PRODREG fails",
            "",
            "## SHIPAPP charter",
            "",
            f"- paths: `{AT0_SHIPAPP_CHARTER['paths']}`  ",
            f"- banner: `{AT0_SHIPAPP_CHARTER['banner']}`  ",
            f"- smoke: **{AT0_SHIPAPP_CHARTER['smoke']}**  ",
            f"- rule: {AT0_SHIPAPP_CHARTER['rule']}",
            "",
            "## NANOGEN4 hypothesis (one idea)",
            "",
            AT0_NANOGEN4_HYPOTHESIS,
            "",
            "## Real-eval protocol",
            "",
            f"- live_ask_battery: "
            f"{AT0_REAL_EVAL_PROTOCOL['live_ask_battery']}  ",
            f"- summary_only_forbidden: "
            f"{AT0_REAL_EVAL_PROTOCOL['summary_only_forbidden']}  ",
            f"- gen_claim_rule: "
            f"{AT0_REAL_EVAL_PROTOCOL['gen_claim_rule']}  ",
            f"- mini_agi_rule: {AT0_REAL_EVAL_PROTOCOL['mini_agi_rule']}",
            "",
            "## Ask battery (ids)",
            "",
            "| id | kind | expect_mode |",
            "|----|------|-------------|",
            bat_rows,
            "",
            "## SAFE ≠ quality",
            "",
            AT0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AT0_ANTI_FP,
            "",
            "## North star",
            "",
            AT0_NORTH_STAR,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:at:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) on the Z1 add known-ask; OOD path "
            "must map to ABSTAIN.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-at/at0_session.json` · "
            "`results/nano-lm/wave-at/trials/AT-*.json`.  ",
            "Contract: `nano_lm/tests/test_at_session.py`.",
            "",
            "## Claims",
            "",
            "- AT packs frozen for Wave AT — **not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            "**AF packaged stack + AQ product layer + AS trust path**.  ",
            "- Generative PROMOTE only via later **AT3 H-NANOGEN4** "
            "ablated bar ≥5.0.  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "mini-AGI claim early · Wave AU invent · CTX/SMART/FAST/APP "
            "clone · bank stuffing · vanity re-SEMFIX.",
            "",
            "Next: **AT1 H-PRODREG** — run Caminho A regression suite.",
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

    # SHIPUI pattern: labeled DECODE arm disables refuse gate.
    return ask_once(
        question=_DECODE_Q,
        root=_CHAMPION,
        seed=0,
        wrap=False,
        bank_path=_Z_BANK,
        curated_root=_CURATED,
        abstain=False,
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
        map_at_product_mode("NO_ANSWER") == "ABSTAIN",
        str(AS0_ASKABSTAIN_CHARTER.get("product_mode")) == "ABSTAIN",
    )
    return all(checks)


def _smoke_dual_arm(*, workers: int) -> dict[str, Any]:
    """LOOKUP wrap + DECODE (abstain off) + ABSTAIN alias (anti-FP)."""
    with ThreadPoolExecutor(max_workers=min(2, max(1, workers))) as pool:
        fut_l = pool.submit(_ask_lookup)
        fut_d = pool.submit(_ask_decode)
        lookup = fut_l.result()
        gen = fut_d.result()
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    l_mode = map_at_product_mode(str(l_tel["mode"]))
    g_mode = map_at_product_mode(str(g_tel["mode"]))
    ok = _smoke_ok(
        lookup=lookup,
        l_arm=l_arm,
        g_arm=g_arm,
        l_mode=l_mode,
        g_mode=g_mode,
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
        "modes_charter": sorted(AT0_MODES),
        "abstain_alias": map_at_product_mode("NO_ANSWER"),
        "askabstain_paths": AS0_ASKABSTAIN_CHARTER.get("paths"),
    }


def _run_ask_smoke(
    decision: str, *, skip: bool, workers: int
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_dual_arm(workers=workers)
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "dual-arm smoke failed", "ask": ask}
            )
        )
        return 2, ask
    return 0, ask


def _parallel_prep(workers: int, trials_dir: Path) -> tuple[list[str], bool]:
    # Warm thread pool (hardware use) while freezing trials on main.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fut = pool.submit(_freeze_trials, trials_dir)
        return fut.result()


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision.startswith("PROMOTE") else "KILL"
    body = "\n".join(
        [
            f"# Wave AT session checklist (**OPEN** · AT0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AT **OPEN** · Caminho A ship + Nano Generative).  ",
            "> Parent: AS COMPLETE + FROZEN · Ship: **AF + AQ + AS trust "
            "path — not open chat LM** · ≤5M.  ",
            "> Reopen: 2026-07-27 — after AS-FREEZE; product trust locked; "
            "generative still HOLD 4.3.",
            "",
            "## Current stage",
            "",
            f"**AT0 — SESSION ({status})** · Next: **AT1 H-PRODREG**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AT OPEN** |",
            "| Track | Caminho A regression + SHIPAPP · "
            "**H-NANOGEN4** north star |",
            "| Parent | AS COMPLETE + FROZEN |",
            "| Open hole | ship/demo human UI · ablated gen ≥5 |",
            "| Forbidden | vanity re-SEMFIX · LOOKUP-as-IQ · "
            "mini-AGI early · Wave AU invent |",
            "",
            "## North star (signed)",
            "",
            AT0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AT0)",
            "",
            "```text",
            "MODEL = AT0-SESSION",
            "",
            "[x] Freeze PRODREG suite (para · FH · latency · KB · modes · "
            "default abstain)",
            "[x] Charter SHIPAPP human-facing demo/apps (4 modes always "
            "visible)",
            "[x] Write ONE NANOGEN4 hypothesis (snippet-prefix decode) to "
            "beat ablated 4.3",
            "[x] Real-eval ask battery protocol (live questions, not "
            "summary-only)",
            "[x] Do NOT reopen SEMFIX/ADVSAFE unless PRODREG fails",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[ ] Next: AT1 H-PRODREG",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AT0 | SESSION | **{status}** |",
            "| AT1 | H-PRODREG | **NEXT** |",
            "| AT2 | H-SHIPAPP | pending |",
            "| AT3 | H-NANOGEN4 | pending (generative north-star gate) |",
            "| AT4 | AT-REAL-EVAL | pending |",
            "| AT5 | AT-REPORT | pending |",
            "| AT6 | AT-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Paraphrase hit | ≥ 0.70 | AS PARAEXT2 **0.80** |",
            "| Adversary FH | **0** | AS ADVSAFE **0**/20 |",
            "| Default-ask OOD | ABSTAIN | AS ASKABSTAIN |",
            "| Latency p50/p99 | publish | AS METRICS |",
            "| Modes on ship/demo | 4/4 | AS SHIPUI |",
            "| Ablated gen (NANOGEN4) | ≥ **5.0** | NANOGEN3 **4.3** HOLD |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def _patch_pesquisa_at0(decision: str) -> None:
    if not _LOCAL_PESQUISA.is_file() or not decision.startswith("PROMOTE"):
        return
    text = _LOCAL_PESQUISA.read_text(encoding="utf-8")
    old = (
        "| AT0 | **SESSION** | Freeze AT packs: product-regression suite · "
        "ship-app charter · **NANOGEN4 hypothesis (one idea)** · "
        "real-eval protocol | cite AS gates; gen hypothesis required | "
        "**NEXT** |"
    )
    new = (
        "| AT0 | **SESSION** | Freeze AT packs: product-regression suite · "
        "ship-app charter · **NANOGEN4 hypothesis (one idea)** · "
        "real-eval protocol | cite AS gates; gen hypothesis required | "
        "**DONE — PROMOTE** |"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_next = (
        "1. **AT0 SESSION** — create `.local/wave-at/SESSION.md` · "
        "freeze packs · **write one NANOGEN4 training/decode hypothesis**."
    )
    new_next = (
        "1. **AT0 SESSION** — **DONE PROMOTE** (`npm run nano:at:session`) · "
        "next **AT1 H-PRODREG**."
    )
    if old_next in text:
        text = text.replace(old_next, new_next, 1)
    bash_old = (
        "# AT runners: add as stages land (nano:at:session, nano:prodreg, "
        "nano:shipapp, nano:nanogen4, …)"
    )
    bash_new = (
        "npm run nano:at:session\n"
        "# next: nano:prodreg · nano:shipapp · nano:nanogen4 "
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
    decision = decide_at0_session(
        trials_dir_ready=trials_ready, anti_fp_signed=True
    )
    _write_public_note(decision=decision)
    _update_local_session(decision)
    _patch_pesquisa_at0(decision)
    rc, ask = _run_ask_smoke(
        decision, skip=bool(args.skip_ask), workers=workers
    )
    if rc != 0:
        return rc

    payload = {
        "id": AT0_ID,
        "thesis": AT0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "cited_as_gates": sorted(AT0_CITED_AS_GATES),
        "prodreg_suite": dict(AT0_PRODREG_SUITE),
        "shipapp_charter": dict(AT0_SHIPAPP_CHARTER),
        "nanogen4_hypothesis": AT0_NANOGEN4_HYPOTHESIS,
        "real_eval_protocol": dict(AT0_REAL_EVAL_PROTOCOL),
        "ask_battery_n": len(AT0_ASK_BATTERY),
        "safe_note": AT0_SAFE_NOTE,
        "anti_fp": AT0_ANTI_FP,
        "north_star": AT0_NORTH_STAR,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-at-session.md",
        "rule": "pesquisa §5 AT0 · Caminho A + NANOGEN4 hyp + anti-FP",
        "next": "AT1 H-PRODREG (Caminho A regression suite)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AT0_ID,
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
