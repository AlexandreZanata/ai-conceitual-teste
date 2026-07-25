"""Render H-QT smoke — int8 weight-only serve vs fp EARLY."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qt_ops import decide_hqt


def _arm(name: str, means: dict) -> str:
    return (
        f"| {name} | {float(means.get('mean_story_lp', float('nan'))):.4f} | "
        f"{float(means.get('mean_code_lp', float('nan'))):.4f} | "
        f"{float(means.get('mean_wall_ms', float('nan'))):.0f} | "
        f"{int(means.get('weight_bytes', 0))} | "
        f"{int(means.get('n', 0))} |"
    )


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    fp = data.get("fp_means") or {}
    qt = data.get("qt_means") or {}
    decision = data.get("decision") or decide_hqt(
        parent=fp, qt=qt, n_rows=int(qt.get("n", 0))
    )
    title = "Formal H-QT" if formal else "H-QT smoke"
    pack = data.get("pack") or {}
    code = data.get("code_teacher") or {}
    story = data.get("story_teacher") or {}
    lines = [
        f"# {title} — int8 weight-only PACK/EARLY serve",
        "",
    ]
    if formal:
        lines.extend(
            [
                f"Source: `{path}`",
                f"Wall clock: {data.get('wall_s', float('nan')):.1f}s",
                "",
            ]
        )
    lines.extend(
        [
            "Wave X quantized serve: replace student `nn.Linear` weights with "
            f"**int{data.get('bits', 8)}** + per-out-channel scale; dequant to "
            "activation dtype at decode (weights frozen otherwise). Parent = fp "
            "H-EARLY (PACK tip control) on prog@128. Gate: story_lp ≥ parent−ε "
            "and (wall↓ or weight_bytes↓).",
            f"Mode: `{data.get('mode')}`; mechanism=`{data.get('mechanism')}`; "
            f"pack=`{pack}`; max_new=`{data.get('max_new')}`; "
            f"cpu_threads=`{data.get('cpu_threads')}`.",
            "",
            "## Teachers",
            "",
            "| role | hf_id | params | license |",
            "|------|-------|--------|---------|",
            f"| story | `{story.get('hf_id', '—')}` | 33M | TinyStories |",
            f"| code | `{code.get('hf_id', '—')}` | "
            f"{code.get('params', '—')} | {code.get('license', '—')} |",
            "",
            f"**Decision: {decision}**",
            "",
            "## Arms",
            "",
            "| arm | mean story_teacher_lp | mean code_teacher_lp | "
            "mean wall_ms | weight_bytes | n |",
            "|-----|-----------------------|----------------------|"
            "--------------|--------------|---|",
            _arm("H-EARLY fp", fp),
            _arm(f"H-QT int{data.get('bits', 8)}", qt),
            "",
        ]
    )
    cmd = (
        "`npm run nano:formal:hqt` → `npm run nano:formal:hqt:report`"
        if formal
        else "`npm run nano:qt` → `npm run nano:qt:report`"
    )
    lines.extend(
        [
            "Tips unchanged. Wave X quantized PACK serve.",
            "",
            f"Commands: {cmd}.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hqt_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hqt-quantize.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
