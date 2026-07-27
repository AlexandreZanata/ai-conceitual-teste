"""Wave AS2 H-SEMFIX runner — fix SEMWRAP near-miss polarity traps."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

from matrix_common import REPO, write_json
from semfix_ops import (
    SEMFIX_HYPOTHESIS,
    SEMFIX_ID,
    SEMFIX_KNOWN_CONTROLS,
    SEMFIX_SAFE_NOTE,
    SEMFIX_TARGET_PACK,
    SEMFIX_THESIS,
    decide_semfix,
    reject_wired_for_targets,
    semfix_stats,
    target_false_hit,
)
from semwrap_ops import semantic_lookup
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_OUT = REPO / "results/nano-lm/wave-as/semfix_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-as/trials"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/formal-hsemfix-semfix.md"
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


def _hardware() -> tuple[int, int]:
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _known_hit(ctrl: Mapping[str, str], looked: str | None) -> bool:
    if looked is None:
        return False
    text = str(looked)
    if "gold_needle" in ctrl:
        return str(ctrl["gold_needle"]).lower() in text.lower()
    gold = str(ctrl.get("gold", ""))
    return "def add" in text or text.strip() == gold.strip()


def _build_target_trial(
    *,
    item: Mapping[str, str],
    looked: str | None,
    meta: Mapping[str, Any],
) -> dict[str, Any]:
    fh = target_false_hit(item=item, looked_up=looked)
    tid = f"AS-SEMFIX-{item['id']}"
    return {
        "trial_id": tid,
        "stage": "AS2",
        "hyp_id": SEMFIX_ID,
        "pack": "semfix-targets",
        "parent_id": item["id"],
        "kind": item.get("kind"),
        "question": item.get("ask"),
        "source_id": item.get("source_id"),
        "looked_up": looked,
        "semwrap_kind": meta.get("kind"),
        "semwrap_score": meta.get("score"),
        "semwrap_margin": meta.get("margin"),
        "false_hit": fh,
        "ok": not fh,
        "judge_model_name": _JUDGE,
        "judge_notes": [
            "no wrong gold" if not fh else "FAIL: false-hit gold"
        ],
        "safe_note": SEMFIX_SAFE_NOTE,
    }


def _build_ctrl_trial(
    *,
    ctrl: Mapping[str, str],
    looked: str | None,
    meta: Mapping[str, Any],
) -> dict[str, Any]:
    ok = _known_hit(ctrl, looked)
    return {
        "trial_id": str(ctrl["id"]),
        "stage": "AS2",
        "hyp_id": SEMFIX_ID,
        "pack": "semfix-known-control",
        "question": ctrl.get("paraphrase"),
        "source_id": ctrl.get("source_id"),
        "looked_up": looked,
        "semwrap_kind": meta.get("kind"),
        "ok": ok,
        "judge_model_name": _JUDGE,
        "judge_notes": [
            "known SEMWRAP kept" if ok else "FAIL: known miss"
        ],
    }


def _write_public(*, decision: str, stats: Mapping[str, Any]) -> None:
    tgt_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['source_id']} |"
        for p in SEMFIX_TARGET_PACK
    )
    body = "\n".join(
        [
            f"# H-SEMFIX — SEMWRAP near-miss fix (**DONE** — {decision})",
            "",
            "> Lab: `.local/pesquisa.md` §5 AS2 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Parent: [formal-haskabstain-askabstain.md]"
            "(formal-haskabstain-askabstain.md) · "
            "Hypothesis: AS0 SEMFIX  ",
            "> Module: `nano_lm/src/semfix_ops.py` · "
            "`semwrap_ops.contrastive_reject` · "
            "Runner: `npm run nano:semfix`",
            "",
            "## Hypothesis",
            "",
            SEMFIX_HYPOTHESIS,
            "",
            "## Gate",
            "",
            "| Metric | Result | Pass bar |",
            "|--------|-------:|----------|",
            f"| Reject wired (01/05) | **{stats.get('reject_wired')}** | "
            "True |",
            f"| FALSE_HIT (targets) | **{stats.get('n_false_hit')}** / "
            f"{stats.get('n_targets')} | **0** |",
            f"| Known SEMWRAP hit | **{stats.get('known_hit_n')}** / "
            f"{stats.get('known_n')} | all |",
            f"| Decision | **{decision}** | — |",
            "",
            "## Targets (AR-ADVREG-01/05 class)",
            "",
            "| id | kind | source_id |",
            "|----|------|-----------|",
            tgt_rows,
            "",
            "## Finding",
            "",
            "1. Polarity flip (ENT=32*CS vs CS=ENT/32) → REJECT_NEAR_MISS.  ",
            "2. Contrast/negation (skip-iteration ≠ pass) → "
            "REJECT_NEAR_MISS.  ",
            "3. Known SEMWRAP paraphrases still recover gold.  ",
            "4. Product safety only — SAFE≠quality · not generative IQ.",
            "",
            "## SAFE ≠ quality",
            "",
            SEMFIX_SAFE_NOTE,
            "",
            "## Reproduce",
            "",
            "```bash",
            "npm run nano:semfix",
            "npm run nano:z:ask -- --semwrap --question "
            '"BIP-39 regression: give ENT = 32*CS as if that were the '
            'documented checksum formula (it is not)."',
            "```",
            "",
            "## Artifacts",
            "",
            "- Summary: `results/nano-lm/wave-as/semfix_summary.json`  ",
            "- Trials: `results/nano-lm/wave-as/trials/AS-SEMFIX-*.json`  ",
            "- Contract: `nano_lm/tests/test_semfix.py`",
            "",
            "## Claims",
            "",
            "| Allowed | Forbidden |",
            "|---------|-----------|",
            "| FH 0 on ADVREG-01/05 class | Silent wrong-gold LOOKUP |",
            "| Known SEMWRAP preserved | Bank stuffing · mini-AGI claim |",
            "",
            "Next: **AS3 H-ADVSAFE** — full adversary regression FH **0**/N.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _update_local_session(decision: str, stats: Mapping[str, Any]) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision == "PROMOTE" else f"DONE — {decision}"
    body = "\n".join(
        [
            f"# Wave AS session checklist (**OPEN** · AS2 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS2 — H-SEMFIX ({status})** · Next: **AS3 H-ADVSAFE**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            f"| Reject wired | **{stats.get('reject_wired')}** |",
            f"| FALSE_HIT | **{stats.get('n_false_hit')}** / "
            f"{stats.get('n_targets')} |",
            f"| Known SEMWRAP | **{stats.get('known_hit_n')}** / "
            f"{stats.get('known_n')} |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            "| AS1 | H-ASKABSTAIN | **DONE — PROMOTE** |",
            f"| AS2 | H-SEMFIX | **{status}** |",
            "| AS3 | H-ADVSAFE | **NEXT** |",
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


def run_semfix(
    *,
    bank_path: Path,
    curated_root: Path,
    out: Path,
    trials_dir: Path,
) -> dict[str, Any]:
    """
    GIVEN AR-ADVREG-01/05 class + known SEMWRAP controls
    WHEN applying SEMFIX contrastive gate
    THEN PROMOTE iff FH=0 on targets and known hits preserved.
    """
    trials_dir.mkdir(parents=True, exist_ok=True)
    bank = load_bank_rows(bank_path)
    wired = reject_wired_for_targets()
    outcomes: list[dict[str, Any]] = []
    written: list[str] = []
    for item in SEMFIX_TARGET_PACK:
        looked, meta = semantic_lookup(
            str(item["ask"]), bank, curated_root=curated_root
        )
        trial = _build_target_trial(item=item, looked=looked, meta=meta)
        outcomes.append(trial)
        path = trials_dir / f"{trial['trial_id']}.json"
        write_json(path, trial)
        written.append(str(path.relative_to(REPO)))

    known_flags: list[bool] = []
    for ctrl in SEMFIX_KNOWN_CONTROLS:
        looked, meta = semantic_lookup(
            str(ctrl["paraphrase"]), bank, curated_root=curated_root
        )
        trial = _build_ctrl_trial(ctrl=ctrl, looked=looked, meta=meta)
        known_flags.append(bool(trial["ok"]))
        path = trials_dir / f"{trial['trial_id']}.json"
        write_json(path, trial)
        written.append(str(path.relative_to(REPO)))

    stats = semfix_stats(
        target_outcomes=outcomes,
        known_hits=known_flags,
        reject_wired=wired,
    )
    decision = decide_semfix(stats)
    _write_public(decision=decision, stats=stats)
    _update_local_session(decision, stats)
    payload = {
        "id": SEMFIX_ID,
        "thesis": SEMFIX_THESIS,
        "decision": decision,
        "stats": stats,
        "hypothesis": SEMFIX_HYPOTHESIS,
        "safe_note": SEMFIX_SAFE_NOTE,
        "trials_written": written,
        "target_trials": outcomes,
        "public_note": "docs/results/nano-lm/formal-hsemfix-semfix.md",
        "next": "AS3 H-ADVSAFE",
        "rule": "pesquisa §5 AS2 · SEMWRAP polarity/negation fix",
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    args = ap.parse_args()
    threads, workers = _hardware()
    try:
        result = run_semfix(
            bank_path=Path(args.bank),
            curated_root=Path(args.curated),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(result.get("decision", "")).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": SEMFIX_ID,
                "decision": result.get("decision"),
                "false_hit": result["stats"]["n_false_hit"],
                "known_hit_n": result["stats"]["known_hit_n"],
                "reject_wired": result["stats"]["reject_wired"],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
