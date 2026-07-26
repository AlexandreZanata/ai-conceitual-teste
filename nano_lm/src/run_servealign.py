"""Wave AA2 H-SERVEALIGN: QPFB2+BEAMKV open HITL×10 no wrap (nano:servealign)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from decode_beamkv import decode_beams_shared_kv
from decode_early import decode_early
from eval_student import load_student_ckpt
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, matrix_cfg, write_json
from pfb2_ops import K2_BEAMS
from pfb_ops import PFB_TEMP
from pfb_score import attach_code_teacher, collect_beam_banks, commit_pfb_rows
from qt_quant import quantize_student_int8
from servealign_ops import (
    SERVEALIGN_ID,
    decide_servealign,
    score_open_completion,
    servealign_stats,
)
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from z_trial import validate_trial

_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_TRIALS_Z = REPO / "results/nano-lm/wave-z/trials"
_TRIALS = REPO / "results/nano-lm/wave-aa/trials"
_SUMMARY = REPO / "results/nano-lm/wave-aa/servealign_summary.json"
_JUDGE = "cursor-composer-frontier-chat"
_MAX_NEW = 64


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


def _free_cuda(*objs: object) -> None:
    for obj in objs:
        del obj
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def _load_z1_pack() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(1, 11):
        data = json.loads((_TRIALS_Z / f"Z1-{i:02d}.json").read_text(encoding="utf-8"))
        rows.append(
            {
                "i": i,
                "question": str(data["question"]),
                "source_id": str(data["source_id"]),
                "gold": str(data.get("gold") or data.get("repaired") or ""),
            }
        )
    return rows


def _load_gene(root: Path, recipe: dict[str, Any]) -> dict[str, Any]:
    path = root / str(recipe["early_gene"])
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return {**gene, "n": 1}


def _parent_rows(
    *,
    qt: Any,
    tok: Any,
    story: Any,
    questions: list[str],
    gene: dict[str, Any],
    device: torch.device,
    seed: int,
) -> list[dict[str, Any]]:
    from tchr_score import code_teacher_mean_logprob

    rows: list[dict[str, Any]] = []
    for i, q in enumerate(questions):
        parent = decode_early(
            qt,
            tok,
            q,
            n=1,
            max_new_tokens=_MAX_NEW,
            min_new=int(gene["min_new"]),
            conf_threshold=float(gene["conf_threshold"]),
            patience=int(gene["patience"]),
            temperature=1e-6,
            top_p=float(gene["top_p"]),
            seed=int(seed) + i,
            device=device,
        )
        p_story = float(code_teacher_mean_logprob(story, q, parent.text))
        rows.append(
            {
                "family": "H-QT-EARLY-n1",
                "prompt": q,
                "continuation": parent.text,
                "story_teacher_id": STORY_TEACHER_ID,
                "story_teacher_lp": p_story,
                "wall_ms": float(parent.wall_ms),
                "n_new": len(parent.token_ids),
                "seed": int(seed),
                "unique": 1.0,
                "k": 1.0,
                "pick": 0.0,
                "n_elig": 1.0,
                "switched": 0.0,
            }
        )
    return rows


def _build_trial(
    *,
    i: int,
    pack: dict[str, Any],
    row: dict[str, Any],
) -> dict[str, Any]:
    tid = f"AA2-{i:02d}"
    score, err, notes = score_open_completion(
        str(row.get("continuation", "")),
        str(pack["gold"]),
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AA2",
        "hyp_id": SERVEALIGN_ID,
        "question": pack["question"],
        "source_id": pack["source_id"],
        "recipe_id": "champion-qpfb2-v0",
        "ckpt": None,
        "completion": row.get("continuation"),
        "wall_ms": row.get("wall_ms"),
        "n_new": row.get("n_new"),
        "seed": row.get("seed", 0),
        "mode": "QPFB2+BEAMKV",
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": "open decode stack; no wrap",
        "gold": str(pack["gold"]).strip(),
        "repaired": str(pack["gold"]).strip(),
        "wrap": False,
        "pick": row.get("pick"),
        "n_elig": row.get("n_elig"),
        "switched": row.get("switched"),
        "code_teacher_lp": row.get("code_teacher_lp"),
        "story_teacher_lp": row.get("story_teacher_lp"),
    }
    errs = validate_trial(trial)
    if errs:
        raise ValueError(f"{tid}: " + "; ".join(errs))
    return trial


def run_servealign(
    *,
    champ_root: Path | None = None,
    out: Path | None = None,
    trials_dir: Path | None = None,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN champion QT + Z1 questions
    WHEN QPFB2 commit on BEAMKV shared K=2 beams (no wrap)
    THEN HITL×10; decide PROMOTE|HOLD|KILL.
    """
    champ = Path(champ_root) if champ_root else _CHAMPION
    summ = Path(out) if out else _SUMMARY
    tdir = Path(trials_dir) if trials_dir else _TRIALS
    pack = _load_z1_pack()
    questions = [r["question"] for r in pack]
    recipe = json.loads((champ / "recipe.json").read_text(encoding="utf-8"))
    gene = _load_gene(champ, recipe)
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-SERVEALIGN requires CUDA")
    tok = load_tokenizer(str(recipe["tokenizer_id"]), c["cache"])
    t0 = time.perf_counter()
    story = load_causal_lm(
        STORY_TEACHER_ID, str(recipe["tokenizer_id"]), cache_dir=c["cache"], use_fp16=True
    )
    student = load_student_ckpt(champ / str(recipe["ckpt"]), tok, device)
    qt = quantize_student_int8(student)  # type: ignore[arg-type]
    qt.to(device)
    try:
        parents = _parent_rows(
            qt=qt,
            tok=tok,
            story=story,
            questions=questions,
            gene=gene,
            device=device,
            seed=seed,
        )
        banks = collect_beam_banks(
            story_teacher=story,
            student=qt,
            parent_rows=parents,
            gene=gene,
            max_new=_MAX_NEW,
            beam_seed=int(seed) + 2200,
            k=K2_BEAMS,
            temperature=PFB_TEMP,
            decode_beams_fn=decode_beams_shared_kv,
        )
    finally:
        _free_cuda(story, student, qt)

    meta = code_teacher_meta()
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    try:
        parents = attach_code_teacher(code, parents)
        parent_code = {
            (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
            for r in parents
        }
        committed = commit_pfb_rows(
            code,
            banks,
            parent_code_by_key=parent_code,
            family="H-SERVEALIGN",
        )
    finally:
        _free_cuda(code)

    if len(committed) != 10:
        raise RuntimeError(f"expected 10 commits, got {len(committed)}")

    tdir.mkdir(parents=True, exist_ok=True)
    trials: list[dict[str, Any]] = []
    for row_pack, crow in zip(pack, committed, strict=True):
        trial = _build_trial(i=int(row_pack["i"]), pack=row_pack, row=crow)
        write_json(tdir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    stats = servealign_stats(scores, errors)
    decision = decide_servealign(stats)
    summary: dict[str, Any] = {
        "hyp_id": SERVEALIGN_ID,
        "stage": "AA2",
        "decision": decision,
        "stack": "QT∘QPFB2+BEAMKV shared K=2 (no wrap)",
        "stats": stats,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "score": t["score"],
                "error": t["error"],
                "mode": t["mode"],
                "wall_ms": t["wall_ms"],
                "switched": t.get("switched"),
            }
            for t in trials
        ],
        "finding": (
            f"{SERVEALIGN_ID}: mean={stats['mean']:.1f} "
            f"errors={stats['n_errors']}/10 beats_z1={stats['beats_z1']} "
            f"pass_bar={stats['pass_bar']} decision={decision}."
        ),
        "note": (
            "Open decode only; product known-ask path remains H-ZWRAP. "
            "PROMOTE requires HITL pass bar; HOLD = beats Z1+0.5 only."
        ),
    }
    write_json(summ, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--champ", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        summary = run_servealign(
            champ_root=args.champ,
            out=args.out,
            trials_dir=args.trials_dir,
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    summary["ok"] = True
    summary["cpu_threads"] = threads
    print(json.dumps(summary))
    decision = str(summary["decision"])
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
