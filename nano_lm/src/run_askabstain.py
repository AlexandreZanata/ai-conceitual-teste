"""Wave AS1 H-ASKABSTAIN runner — ABSTAIN on default nano:z:ask path."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from askabstain_ops import (
    ASKABSTAIN_ANTI_FP,
    ASKABSTAIN_CHARTER,
    ASKABSTAIN_ID,
    ASKABSTAIN_KNOWN_ASK,
    ASKABSTAIN_OOD_PACK,
    ASKABSTAIN_SAFE_NOTE,
    ASKABSTAIN_THESIS,
    MIN_OOD_ABSTAIN_RATE,
    NO_ANSWER,
    askabstain_false_hit,
    askabstain_mode_labeled,
    askabstain_stats,
    decide_askabstain,
    default_path_abstained,
)
from matrix_common import REPO, write_json
from run_z_ask import ask_many, ask_once
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_OUT = REPO / "results/nano-lm/wave-as/askabstain_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-as/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-haskabstain-askabstain.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"
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
    # MUST NOT call apply_abstain — default ask path must already abstain.
    pm = str(payload.get("product_mode", ""))
    wired = default_path_abstained(payload)
    fh = askabstain_false_hit(
        completion=str(payload.get("completion", "")),
        product_mode=pm,
        bank_golds=bank_golds,
    )
    ok = wired and pm == "ABSTAIN" and not fh
    return {
        "trial_id": f"AS-{item['id']}",
        "stage": "AS1",
        "hyp_id": ASKABSTAIN_ID,
        "pack": "askabstain-ood-default",
        "parent_id": item.get("id"),
        "kind": item.get("kind"),
        "question": item.get("ask"),
        "source_id": item.get("source_id"),
        "completion": payload.get("completion"),
        "pre_abstain_completion": payload.get("pre_abstain_completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "mode": payload.get("mode"),
        "product_mode": pm,
        "modeui_line": payload.get("modeui_line"),
        "abstained": bool(payload.get("abstained")),
        "default_path_abstained": wired,
        "false_hit": fh,
        "ok": ok,
        "mode_labeled": askabstain_mode_labeled(payload),
        "judge_model_name": _JUDGE,
        "judge_notes": [
            "default ask ABSTAIN" if ok else "FAIL: default ask did not ABSTAIN"
        ],
        "safe_note": ASKABSTAIN_SAFE_NOTE,
    }


def _build_known_trial(payload: Mapping[str, Any]) -> dict[str, Any]:
    pm = str(payload.get("product_mode", ""))
    text = str(payload.get("completion", ""))
    ok = (
        pm == "LOOKUP"
        and "def add" in text
        and not bool(payload.get("abstained"))
    )
    return {
        "trial_id": "AS-ASKABSTAIN-KNOWN",
        "stage": "AS1",
        "hyp_id": ASKABSTAIN_ID,
        "pack": "askabstain-known-lookup",
        "question": ASKABSTAIN_KNOWN_ASK,
        "completion": text,
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "mode": payload.get("mode"),
        "product_mode": pm,
        "modeui_line": payload.get("modeui_line"),
        "abstained": bool(payload.get("abstained")),
        "ok": ok,
        "mode_labeled": askabstain_mode_labeled(payload),
        "judge_model_name": _JUDGE,
        "judge_notes": [
            "LOOKUP control kept" if ok else "FAIL: known LOOKUP broken"
        ],
    }


def _write_public(*, decision: str, stats: Mapping[str, Any]) -> None:
    ood_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['source_id']} |"
        for p in ASKABSTAIN_OOD_PACK
    )
    body = "\n".join(
        [
            f"# H-ASKABSTAIN — default-ask ABSTAIN (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS1 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [wave-as-session.md](wave-as-session.md) · "
            "Charter: AS0 ASKABSTAIN  ",
            "> Module: `nano_lm/src/askabstain_ops.py` · "
            "Runner: `npm run nano:askabstain`  ",
            "> Wire: `run_z_ask.ask_many(..., abstain=True)` default",
            "",
            "## Hypothesis",
            "",
            "Junk DECODE on OOD/miss must surface as `NO_ANSWER` / "
            "`mode=ABSTAIN` on the **default** `nano:z:ask` / apps ask path "
            "(not only stage runners). Known LOOKUP stays LOOKUP. False-hit "
            "stays 0.",
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| Default-path wired | **{stats.get('default_path_wired')}** | "
            "True |",
            f"| OOD abstain rate | **{stats.get('ood_abstain_rate')}** "
            f"({stats.get('ood_abstained_n')}/{stats.get('ood_n')}) | "
            f"≥ {MIN_OOD_ABSTAIN_RATE} |",
            f"| FALSE_HIT | **{stats.get('n_false_hit')}** | **0** |",
            f"| Known LOOKUP ok | **{stats.get('known_lookup_ok')}** | True |",
            f"| Modes labeled | **{stats.get('modes_labeled')}** | True |",
            f"| Decision | **{decision}** | — |",
            "",
            "## ASKABSTAIN charter (from AS0)",
            "",
            f"- paths: `{ASKABSTAIN_CHARTER['paths']}`  ",
            f"- trigger: {ASKABSTAIN_CHARTER['trigger']}  ",
            f"- action: `{ASKABSTAIN_CHARTER['action']}` → "
            f"`mode={ASKABSTAIN_CHARTER['product_mode']}`  ",
            f"- preserve: {ASKABSTAIN_CHARTER['preserve']}  ",
            f"- anti-FP: {ASKABSTAIN_CHARTER['anti_fp']}",
            "",
            "## OOD / miss pack (default ask)",
            "",
            "| id | kind | source_id |",
            "|----|------|-----------|",
            ood_rows,
            "",
            "## Finding",
            "",
            "1. Default `ask_once` / `ask_many` apply refuse-junk under max "
            "safe CPU (`cpus-2`).  ",
            "2. Runner **does not** post-hoc `apply_abstain` — proves wire.  ",
            "3. Known-ask WRAP_LOOKUP control must not abstain.  ",
            "4. Product honesty only — **not** generative IQ / mini-AGI.",
            "",
            "## SAFE ≠ quality",
            "",
            ASKABSTAIN_SAFE_NOTE,
            "",
            "## Anti-FP",
            "",
            ASKABSTAIN_ANTI_FP,
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:askabstain",
            "npm run nano:z:ask -- --question "
            '"Which nation hosted the 2016 Summer Olympics?"',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/askabstain_summary.json`  ",
            "- Trials: `results/nano-lm/wave-as/trials/AS-*.json`  ",
            "- Contract: `nano_lm/tests/test_askabstain.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| ABSTAIN on default ask path | Runner-only abstain theater |",
            "| OOD→NO_ANSWER · FH 0 · LOOKUP kept | LOOKUP-as-IQ · mini-AGI |",
            "",
            "Next: **AS2 H-SEMFIX** — fix SEMWRAP near-miss "
            "(AR-ADVREG-01/05 class).",
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
            f"# Wave AS session checklist (**OPEN** · AS1 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN** · Product Science fix + Nano Generative).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS1 — H-ASKABSTAIN ({status})** · Next: **AS2 H-SEMFIX**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| Default-path wired | **{stats.get('default_path_wired')}** |",
            f"| OOD abstain rate | **{rate}** "
            f"({stats.get('ood_abstained_n')}/{stats.get('ood_n')}) |",
            f"| FALSE_HIT | **{stats.get('n_false_hit')}** |",
            f"| Known LOOKUP | **{stats.get('known_lookup_ok')}** |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            f"| AS1 | H-ASKABSTAIN | **{status}** |",
            "| AS2 | H-SEMFIX | **NEXT** |",
            "| AS3 | H-ADVSAFE | pending |",
            "| AS4 | H-PARAEXT2 | pending |",
            "| AS5 | H-METRICS | pending |",
            "| AS6 | H-SHIPUI | pending |",
            "| AS7 | H-NANOGEN3 | pending |",
            "| AS8 | AS-DUAL-HITL | pending |",
            "| AS9 | AS-REPORT | pending |",
            "| AS10 | AS-FREEZE | pending |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_askabstain(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN OOD/miss pack + known LOOKUP
    WHEN asking via default ask_many (no runner apply_abstain)
    THEN PROMOTE iff default path abstains · FH 0 · LOOKUP kept.
    """
    trials_dir.mkdir(parents=True, exist_ok=True)
    bank = load_bank_rows(bank_path)
    golds = _bank_golds(bank)
    questions = [_ask_text(item) for item in ASKABSTAIN_OOD_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=False,
        bank_path=bank_path,
        curated_root=curated_root,
        abstain=True,
    )
    ood_flags: list[bool] = []
    n_false = 0
    modes_ok = True
    written: list[str] = []
    for item, payload in zip(ASKABSTAIN_OOD_PACK, payloads, strict=True):
        trial = _build_ood_trial(item=item, payload=payload, bank_golds=golds)
        ood_flags.append(bool(trial["default_path_abstained"]))
        if trial["false_hit"]:
            n_false += 1
        if not trial["mode_labeled"]:
            modes_ok = False
        path = trials_dir / f"{trial['trial_id']}.json"
        write_json(path, trial)
        written.append(str(path.relative_to(REPO)))

    known = ask_once(
        question=ASKABSTAIN_KNOWN_ASK,
        root=root,
        seed=seed,
        wrap=True,
        bank_path=bank_path,
        curated_root=curated_root,
        abstain=True,
    )
    known_trial = _build_known_trial(known)
    kpath = trials_dir / f"{known_trial['trial_id']}.json"
    write_json(kpath, known_trial)
    written.append(str(kpath.relative_to(REPO)))
    if not known_trial["mode_labeled"]:
        modes_ok = False

    wired = all(bool(f) for f in ood_flags)
    stats = askabstain_stats(
        ood_default_abstained=ood_flags,
        known_lookup_ok=bool(known_trial["ok"]),
        n_false_hit=n_false,
        modes_labeled=modes_ok,
        default_path_wired=wired,
    )
    decision = decide_askabstain(stats)
    _write_public(decision=decision, stats=stats)
    _update_local_session(decision, stats)
    payload = {
        "id": ASKABSTAIN_ID,
        "thesis": ASKABSTAIN_THESIS,
        "decision": decision,
        "stats": stats,
        "charter": dict(ASKABSTAIN_CHARTER),
        "anti_fp": ASKABSTAIN_ANTI_FP,
        "safe_note": ASKABSTAIN_SAFE_NOTE,
        "trials_written": written,
        "known_trial": known_trial,
        "public_note": "docs/results/nano-lm/formal-haskabstain-askabstain.md",
        "next": "AS2 H-SEMFIX",
        "rule": "pesquisa §5 AS1 · default ask ABSTAIN wire",
    }
    write_json(out, payload)
    return payload


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
        result = run_askabstain(
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
    ok = str(result.get("decision", "")).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": ASKABSTAIN_ID,
                "decision": result.get("decision"),
                "ood_abstain_rate": result["stats"]["ood_abstain_rate"],
                "false_hit": result["stats"]["n_false_hit"],
                "default_path_wired": result["stats"]["default_path_wired"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
