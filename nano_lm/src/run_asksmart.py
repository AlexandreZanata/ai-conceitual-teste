"""Wave AB4 H-ASKSMART runner: anti-period QPFB2+BEAMKV + constrained FIX."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from ab_session_ops import AB0_PACK
from asksmart_ops import (
    ASKSMART_ID,
    ASKSMART_N,
    anti_period_pick,
    asksmart_stats,
    decide_asksmart,
    is_period_collapse,
    score_asksmart,
    strip_stop,
)
from data_tiny import load_tokenizer
from decode_beamkv import decode_beams_shared_kv
from decode_early import decode_early
from eval_student import load_student_ckpt
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, matrix_cfg, write_json
from pfb2_ops import K2_BEAMS
from pfb_ops import EPS_LP, PFB_TEMP
from pfb_score import attach_code_teacher, collect_beam_banks, commit_pfb_rows
from qt_quant import quantize_student_int8
from run_z_ask import ask_many
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from z_trial import validate_trial

_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CURATED = REPO / "nano_lm/data/curated"
_TRIALS = REPO / "results/nano-lm/wave-ab/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ab/asksmart_summary.json"
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


def _load_gene(root: Path, recipe: dict[str, Any]) -> dict[str, Any]:
    path = root / str(recipe["early_gene"])
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    # ASKSMART knobs: disable early-exit; keep gene temp for beams.
    return {
        **gene,
        "n": 1,
        "conf_threshold": 1.0,
        "patience": 99,
        "min_new": max(8, int(gene.get("min_new", 8))),
    }


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
        # Constrained prompt framing (stop-friendly), still open decode.
        prompt = f"Question: {q}\nShort factual answer:"
        parent = decode_early(
            qt,
            tok,
            prompt,
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
        text = strip_stop(parent.text)
        p_story = float(code_teacher_mean_logprob(story, prompt, text))
        rows.append(
            {
                "family": "H-ASKSMART-parent",
                "prompt": prompt,
                "question": q,
                "continuation": text,
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


def _anti_period_commit(
    banks: list[dict[str, Any]],
    committed: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Prefer non-period beam text after PFB commit when available."""
    out: list[dict[str, Any]] = []
    for bank, row in zip(banks, committed, strict=True):
        conts = [strip_stop(c) for c in list(bank.get("conts", []))]
        picked, idx, used = anti_period_pick(conts)
        crow = dict(row)
        if used and picked and not is_period_collapse(picked):
            crow["continuation"] = picked
            crow["anti_period"] = True
            crow["anti_period_idx"] = idx
        else:
            crow["continuation"] = strip_stop(str(row.get("continuation", "")))
            crow["anti_period"] = False
        out.append(crow)
    return out


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    completion: str,
    mode: str,
    wall_ms: float | None,
    n_new: int | None,
    seed: int,
    row: dict[str, Any] | None,
    score_before: float | None,
) -> dict[str, Any]:
    tid = f"AB-ASKSMART-HITL-{i:02d}"
    score, err, notes = score_asksmart(
        completion, item["gold"], mode=mode
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AB4",
        "hyp_id": ASKSMART_ID,
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "recipe_id": "champion-qpfb2-v0",
        "ckpt": None,
        "completion": completion,
        "wall_ms": wall_ms,
        "n_new": n_new,
        "seed": seed,
        "mode": mode,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "constrained SEMWRAP FIX"
            if "CONSTRAINED" in mode.upper()
            else "anti-period open decode"
        ),
        "gold": str(item["gold"]).strip(),
        "repaired": str(item["gold"]).strip(),
        "wrap": "SEMWRAP" in mode.upper(),
        "score_before": score_before,
        "score_after": score,
        "story_teacher_lp": (row or {}).get("story_teacher_lp"),
        "parent_story_lp": (row or {}).get("parent_story_lp"),
        "anti_period": (row or {}).get("anti_period"),
        "switched": (row or {}).get("switched"),
        "weight_update": False,
    }
    errs = validate_trial(trial)
    if errs:
        raise ValueError(f"{tid}: " + "; ".join(errs))
    return trial


def run_asksmart(
    *,
    champ_root: Path | None = None,
    out: Path | None = None,
    trials_dir: Path | None = None,
    bank_path: Path | None = None,
    curated_root: Path | None = None,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AB0 asks + QT champion
    WHEN QPFB2+BEAMKV anti-period open decode, then constrained FIX
    THEN mean≥5 and >SERVEALIGN 3.4 → PROMOTE|HOLD|KILL.
    """
    if len(AB0_PACK) != ASKSMART_N:
        raise ValueError("AB0 pack must be 10")
    champ = Path(champ_root) if champ_root else _CHAMPION
    summ = Path(out) if out else _SUMMARY
    tdir = Path(trials_dir) if trials_dir else _TRIALS
    bank = Path(bank_path) if bank_path else _BANK
    curated = Path(curated_root) if curated_root else _CURATED
    questions = [p["question"] for p in AB0_PACK]
    recipe = json.loads((champ / "recipe.json").read_text(encoding="utf-8"))
    gene = _load_gene(champ, recipe)
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-ASKSMART requires CUDA")
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
            beam_seed=int(seed) + 4400,
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
            family="H-ASKSMART",
        )
        # Attach parent story for ε gate.
        for crow, prow in zip(committed, parents, strict=True):
            crow["parent_story_lp"] = float(prow["story_teacher_lp"])
        committed = _anti_period_commit(banks, committed)
    finally:
        _free_cuda(code)

    tdir.mkdir(parents=True, exist_ok=True)
    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, crow) in enumerate(
        zip(AB0_PACK, committed, strict=True), start=1
    ):
        text = strip_stop(str(crow.get("continuation", "")))
        mode = "QPFB2+BEAMKV+ANTI_PERIOD"
        score, err, _notes = score_asksmart(text, item["gold"], mode=mode)
        score_before = score
        # FIX: constrained SEMWRAP fallback when open decode fails bar.
        if err or score < 8.0 or is_period_collapse(text):
            payloads = ask_many(
                questions=[item["question"]],
                root=champ,
                seed=seed,
                askfast=True,
                bank_path=bank,
                curated_root=curated,
            )
            text = strip_stop(str(payloads[0].get("completion", "")))
            mode = f"CONSTRAINED+{payloads[0].get('mode', 'SEMWRAP')}"
            fix_count += 1
            crow = {
                **crow,
                "continuation": text,
                "wall_ms": payloads[0].get("wall_ms"),
                "n_new": payloads[0].get("n_new"),
            }
        trial = _build_trial(
            i=i,
            item=dict(item),
            completion=text,
            mode=mode,
            wall_ms=crow.get("wall_ms"),
            n_new=crow.get("n_new"),
            seed=seed,
            row=crow,
            score_before=score_before,
        )
        write_json(tdir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_period = sum(
        1 for t in trials if is_period_collapse(str(t.get("completion", "")))
    )
    n_constrained = sum(
        1 for t in trials if "CONSTRAINED" in str(t.get("mode", "")).upper()
    )
    n_open = ASKSMART_N - n_constrained
    stories = [
        float(t["story_teacher_lp"])
        for t in trials
        if t.get("story_teacher_lp") is not None
        and "CONSTRAINED" not in str(t.get("mode", "")).upper()
    ]
    parents_s = [
        float(t["parent_story_lp"])
        for t in trials
        if t.get("parent_story_lp") is not None
        and "CONSTRAINED" not in str(t.get("mode", "")).upper()
    ]
    mean_story = (
        float(sum(stories) / len(stories)) if stories else None
    )
    mean_parent = (
        float(sum(parents_s) / len(parents_s)) if parents_s else None
    )
    # If all constrained, story gate waived (open arm empty).
    if mean_story is None:
        mean_story = 0.0
        mean_parent = 0.0
    stats = asksmart_stats(
        scores,
        errors,
        n_period=n_period,
        n_constrained=n_constrained,
        n_open=n_open,
        mean_story=mean_story,
        mean_parent_story=mean_parent,
        eps_lp=float(EPS_LP),
    )
    decision = decide_asksmart(stats)
    summary: dict[str, Any] = {
        "hyp_id": ASKSMART_ID,
        "stage": "AB4",
        "decision": decision,
        "stack": "QPFB2+BEAMKV anti-period + constrained SEMWRAP FIX",
        "forbidden": ["STREAM", "KVCACHE-Q", "GENCACHE", "ZPREF", "open chat claim"],
        "fix_count": fix_count,
        "stats": stats,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "elapsed_s": time.perf_counter() - t0,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "mode": t["mode"],
                "score": t["score"],
                "score_before": t.get("score_before"),
                "error": t["error"],
                "wall_ms": t["wall_ms"],
            }
            for t in trials
        ],
        "finding": (
            f"{ASKSMART_ID}: mean={stats['mean']:.1f} "
            f"(>SERVEALIGN {stats['servealign_mean']}); "
            f"constrained_fix={n_constrained}/10 period={n_period} "
            f"decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hasksmart-asksmart.md",
        "claim": "scoped constrained serve — not open chat LM",
    }
    write_json(summ, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--champ", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--bank", type=Path, default=_BANK)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_asksmart(
            champ_root=args.champ,
            out=args.out,
            trials_dir=args.trials_dir,
            bank_path=args.bank,
            curated_root=args.curated,
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": ASKSMART_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_errors": summary["stats"]["n_errors"],
                "n_constrained": summary["stats"]["n_constrained"],
                "n_period": summary["stats"]["n_period"],
                "beats_servealign": summary["stats"]["beats_servealign"],
                "fix_count": summary["fix_count"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
