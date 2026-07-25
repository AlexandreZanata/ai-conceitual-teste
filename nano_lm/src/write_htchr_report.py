"""Render H-TCHR smoke — dual story + code_teacher_lp on prog@128."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tchr_ops import decide_htchr


def render(path: Path, *, formal: bool = False) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    means = data.get("means") or {}
    code = data.get("code_teacher") or {}
    story = data.get("story_teacher") or {}
    decision = data.get("decision") or decide_htchr(
        code_teacher=code,
        mean_story_lp=float(means.get("mean_story_lp", float("-inf"))),
        mean_code_lp=float(means.get("mean_code_lp", float("-inf"))),
        n_rows=int(means.get("n", 0)),
    )
    title = "Formal H-TCHR" if formal else "H-TCHR smoke"
    pack = data.get("pack") or {}
    lines = [
        f"# {title} — tiny code teacher wire (prog@128)",
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
            "Wave X dual-teacher wire: score H-EARLY completions on **prog@128** "
            "with frozen TinyStories story teacher **and** a named tiny code LM. "
            "Teachers are never silently swapped. Kill if code_teacher_lp is "
            "non-finite or story_lp collapses below floor. Not a code-IQ claim "
            "(that is H-CKD).",
            f"Mode: `{data.get('mode')}`; pack=`{pack}`; "
            f"max_new=`{data.get('max_new')}`; "
            f"cpu_threads=`{data.get('cpu_threads')}`.",
            "",
            "## Teachers",
            "",
            f"| role | hf_id | params | license |",
            f"|------|-------|--------|---------|",
            f"| story | `{story.get('hf_id', '—')}` | 33M | TinyStories |",
            f"| code | `{code.get('hf_id', '—')}` | "
            f"{code.get('params', '—')} | {code.get('license', '—')} |",
            "",
            f"**Decision: {decision}**",
            "",
            "## Dual metrics (EARLY on prog@128)",
            "",
            "| family | mean story_teacher_lp | mean code_teacher_lp | "
            "mean wall_ms | n_code_finite | n |",
            "|--------|-----------------------|----------------------|"
            "--------------|---------------|---|",
            f"| H-EARLY | {float(means.get('mean_story_lp', float('nan'))):.4f} | "
            f"{float(means.get('mean_code_lp', float('nan'))):.4f} | "
            f"{float(means.get('mean_wall_ms', float('nan'))):.0f} | "
            f"{int(means.get('n_code_finite', 0))} | "
            f"{int(means.get('n', 0))} |",
            "",
        ]
    )
    cmd = (
        "`npm run nano:formal:htchr` → `npm run nano:formal:htchr:report`"
        if formal
        else "`npm run nano:tchr` → `npm run nano:tchr:report`"
    )
    lines.extend(
        [
            "Tips unchanged. Wave X code-teacher wire.",
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
        default=Path("results/nano-lm/student-matrix/htchr_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/htchr-code-teacher.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
