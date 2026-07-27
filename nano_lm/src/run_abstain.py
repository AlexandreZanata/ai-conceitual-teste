"""Wave AR1 H-ABSTAIN runner (nano:abstain) — refuse junk DECODE."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from abstain_ops import (
    ABSTAIN_ID,
    ABSTAIN_KNOWN_ASK,
    ABSTAIN_OOD_PACK,
    ABSTAIN_THESIS,
    MIN_OOD_ABSTAIN_RATE,
    NO_ANSWER,
    abstain_stats,
    apply_abstain,
    decide_abstain,
    is_false_hit_completion,
    mode_labeled,
)
from ar_session_ops import AR0_ABSTAIN_PROTOCOL, AR0_SAFE_NOTE
from matrix_common import REPO, write_json
from run_z_ask import ask_many, ask_once
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_OUT = REPO / "results/nano-lm/wave-ar/abstain_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ar/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-habstain-abstain.md"
_LOCAL_SESSION = REPO / ".local/wave-ar/SESSION.md"
_JUDGE = "cursor-composer-frontier-chat"


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


def _hardware() -> int:
    cpus = int(os.cpu_count() or 4)
    return tune_cpu_threads(max(4, cpus - 2))


def _ask_text(item: Mapping[str, str]) -> str:
    ask = str(item.get("ask", ""))
    if str(item.get("id")) == "AR-ADVREG-19" and not ask.strip():
        return "[ABSTAIN whitespace-only miss — must not LOOKUP any gold]"
    return ask


def _bank_golds(bank: list[dict[str, Any]]) -> list[str]:
    out: list[str] = []
    for row in bank:
        gold = str(row.get("gold", "") or "").strip()
        if gold:
            out.append(gold)
    return out


def _build_ood_trial(
    *,
    item: Mapping[str, str],
    payload: Mapping[str, Any],
    bank_golds: list[str],
) -> dict[str, Any]:
    gated = apply_abstain(dict(payload))
    pm = str(gated.get("product_mode", ""))
    fh = is_false_hit_completion(
        completion=str(gated.get("completion", "")),
        product_mode=pm,
        bank_golds=bank_golds,
    )
    ok = bool(gated.get("abstained")) and pm == "ABSTAIN" and not fh
    return {
        "trial_id": str(item["id"]),
        "stage": "AR1",
        "hyp_id": ABSTAIN_ID,
        "pack": "abstain-ood",
        "kind": item.get("kind"),
        "question": item.get("ask"),
        "source_id": item.get("source_id"),
        "completion": gated.get("completion"),
        "pre_abstain_completion": gated.get("pre_abstain_completion"),
        "wall_ms": gated.get("wall_ms"),
        "n_new": gated.get("n_new"),
        "mode": gated.get("mode"),
        "product_mode": pm,
        "abstained": bool(gated.get("abstained")),
        "false_hit": fh,
        "ok": ok,
        "mode_labeled": mode_labeled(gated),
        "judge_model_name": _JUDGE,
        "judge_notes": [
            "ABSTAIN on junk DECODE" if ok else "FAIL: expected ABSTAIN"
        ],
        "safe_note": AR0_SAFE_NOTE,
    }


def _build_known_trial(payload: Mapping[str, Any]) -> dict[str, Any]:
    gated = apply_abstain(dict(payload))
    pm = str(gated.get("product_mode", ""))
    text = str(gated.get("completion", ""))
    ok = pm == "LOOKUP" and "def add" in text and not bool(gated.get("abstained"))
    return {
        "trial_id": "AR-ABSTAIN-KNOWN",
        "stage": "AR1",
        "hyp_id": ABSTAIN_ID,
        "pack": "abstain-known-lookup",
        "question": ABSTAIN_KNOWN_ASK,
        "completion": text,
        "wall_ms": gated.get("wall_ms"),
        "n_new": gated.get("n_new"),
        "mode": gated.get("mode"),
        "product_mode": pm,
        "abstained": bool(gated.get("abstained")),
        "ok": ok,
        "mode_labeled": mode_labeled(gated),
        "judge_model_name": _JUDGE,
        "judge_notes": [
            "LOOKUP control kept" if ok else "FAIL: known LOOKUP broken"
        ],
    }


def _write_public(*, decision: str, stats: Mapping[str, Any]) -> None:
    ood_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['source_id']} |"
        for p in ABSTAIN_OOD_PACK
    )
    body = "\n".join(
        [
            f"# H-ABSTAIN — refuse junk DECODE (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AR1 · Session: "
            "`.local/wave-ar/SESSION.md`  ",
            "> Parent: [wave-ar-session.md](wave-ar-session.md) · "
            "Protocol: AR0 abstention  ",
            "> Module: `nano_lm/src/abstain_ops.py` · "
            "Runner: `npm run nano:abstain`",
            "",
            "## Hypothesis",
            "",
            "Junk DECODE on OOD/miss (period-collapse · empty · TinyStories "
            "sludge) must surface as `NO_ANSWER` / `mode=ABSTAIN` — not "
            "unlabeled garbage. Known LOOKUP stays LOOKUP. False-hit stays 0.",
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| OOD abstain rate | **{stats.get('ood_abstain_rate')}** "
            f"({stats.get('ood_abstained_n')}/{stats.get('ood_n')}) | "
            f"≥ {MIN_OOD_ABSTAIN_RATE} |",
            f"| FALSE_HIT | **{stats.get('n_false_hit')}** | **0** |",
            f"| Known LOOKUP ok | **{stats.get('known_lookup_ok')}** | True |",
            f"| Modes labeled | **{stats.get('modes_labeled')}** | True |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Abstention protocol (from AR0)",
            "",
            f"- trigger: {AR0_ABSTAIN_PROTOCOL['trigger']}  ",
            f"- action: `{AR0_ABSTAIN_PROTOCOL['action']}` → "
            f"`{AR0_ABSTAIN_PROTOCOL['product_mode']}`  ",
            f"- anti-FP: {AR0_ABSTAIN_PROTOCOL['anti_fp']}",
            "",
            "## OOD / miss pack",
            "",
            "| id | kind | source_id |",
            "|----|------|-----------|",
            ood_rows,
            "",
            "## Finding",
            "",
            "1. Pure DECODE on OOD/miss under max safe CPU (`cpus-2`).  ",
            "2. `apply_abstain` maps junk → `NO_ANSWER` / ABSTAIN.  ",
            "3. Known-ask WRAP_LOOKUP control must not abstain.  ",
            "4. Product honesty only — **not** generative IQ / mini-AGI.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:abstain",
            "npm run nano:z:ask -- --question "
            '"Which nation hosted the 2016 Summer Olympics?"',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-ar/abstain_summary.json`  ",
            "- Trials: `results/nano-lm/wave-ar/trials/AR-ADVREG-*.json`  ",
            "- Contract: `nano_lm/tests/test_abstain.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| ABSTAIN / NO_ANSWER on junk DECODE | Unlabeled garbage answer |",
            "| OOD abstain↑ with FH 0 | LOOKUP-as-IQ · SAFE-as-quality |",
            "| Product honesty gate | mini-AGI claim · Wave AS invent |",
            "",
            "Next: **AR2 H-SHIPDEMO** — ship/demo UI shows all four modes.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, stats: Mapping[str, Any]) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    rate = stats.get("ood_abstain_rate")
    body = "\n".join(
        [
            f"# Wave AR session checklist (**OPEN** · AR1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AR **OPEN**).  ",
            "> Parent: AQ COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AR1 — H-ABSTAIN ({status})** · Next: **AR2 H-SHIPDEMO**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AR OPEN** |",
            f"| OOD abstain rate | **{rate}** "
            f"({stats.get('ood_abstained_n')}/{stats.get('ood_n')}) |",
            f"| FALSE_HIT | **{stats.get('n_false_hit')}** |",
            f"| Known LOOKUP | **{stats.get('known_lookup_ok')}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AR0 | SESSION | **DONE — PROMOTE** |",
            f"| AR1 | H-ABSTAIN | **{status}** |",
            "| AR2 | H-SHIPDEMO | **NEXT** |",
            "| AR3 | H-PARAEXT | pending |",
            "| AR4 | H-ADVREG | pending |",
            "| AR5 | H-NANOGEN2 | pending |",
            "| AR6 | AR-DUAL-HITL | pending |",
            "| AR7 | AR-REPORT | pending |",
            "| AR8 | AR-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_abstain(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AR0 OOD/miss pack + known LOOKUP control
    WHEN DECODE then apply_abstain
    THEN PROMOTE iff OOD abstain↑ · FH 0 · LOOKUP ok · modes labeled.
    """
    trials_dir.mkdir(parents=True, exist_ok=True)
    bank = load_bank_rows(bank_path)
    golds = _bank_golds(bank)
    questions = [_ask_text(p) for p in ABSTAIN_OOD_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=False,
        bank_path=bank_path,
        curated_root=curated_root,
    )
    if len(payloads) != len(ABSTAIN_OOD_PACK):
        raise RuntimeError("OOD payload count mismatch")

    ood_trials: list[dict[str, Any]] = []
    for item, payload in zip(ABSTAIN_OOD_PACK, payloads, strict=True):
        trial = _build_ood_trial(item=item, payload=payload, bank_golds=golds)
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        ood_trials.append(trial)

    known_raw = ask_once(
        question=ABSTAIN_KNOWN_ASK,
        root=root,
        seed=seed,
        wrap=True,
        bank_path=bank_path,
        curated_root=curated_root,
    )
    known = _build_known_trial(known_raw)
    write_json(trials_dir / f"{known['trial_id']}.json", known)

    ood_flags = [bool(t["abstained"]) for t in ood_trials]
    n_fh = sum(1 for t in ood_trials if t["false_hit"])
    labeled = all(bool(t["mode_labeled"]) for t in ood_trials) and bool(
        known["mode_labeled"]
    )
    stats = abstain_stats(
        ood_abstained=ood_flags,
        known_lookup_ok=bool(known["ok"]),
        n_false_hit=n_fh,
        modes_labeled=labeled,
    )
    decision = decide_abstain(stats)
    _write_public(decision=decision, stats=stats)
    _update_local_session(decision, stats)
    summary: dict[str, Any] = {
        "hyp_id": ABSTAIN_ID,
        "stage": "AR1",
        "thesis": ABSTAIN_THESIS,
        "decision": decision,
        "stats": stats,
        "ood_trials": [t["trial_id"] for t in ood_trials],
        "known_trial": known["trial_id"],
        "compose": ["DECODE", "apply_abstain", "AR0-ood+trap"],
        "no_answer": NO_ANSWER,
        "public_note": "docs/results/nano-lm/formal-habstain-abstain.md",
        "next": "AR2 H-SHIPDEMO",
        "anti_fp": (
            "ABSTAIN labeled; never LOOKUP-as-IQ; SAFE≠quality; "
            "generative bar = AR5 only"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    threads = _hardware()
    try:
        summary = run_abstain(
            bank_path=Path(args.bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2

    decision = str(summary.get("decision", ""))
    ok = decision == "PROMOTE"
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": ABSTAIN_ID,
                "decision": decision,
                "cpu_threads": threads,
                "ood_abstain_rate": summary["stats"]["ood_abstain_rate"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
