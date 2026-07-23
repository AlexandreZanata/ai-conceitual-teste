"""Render H-DECK smoke vs H-DEC markdown from matrix.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from deck_ops import decide_hdeck
from matrix_report_lib import mean_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    s = stats.get("H-DECK", {})
    decision = decide_hdeck(s, stats) if s else "needs H-DECK rows"
    hdec = stats.get("H-DEC", {})
    delta = s.get("mean_lp", float("nan")) - hdec.get("mean_lp", float("nan"))
    lines = [
        "# H-DECK smoke vs H-DEC (proxy rank + teacher top-k)",
        "",
        "Search: student self-logprob ranks pop; teacher rescores top-k only.",
        "Claim: teacher_lp on eval; wall_save = fewer teacher forwards than full H-DEC.",
        "",
        "| family | mean teacher_lp | Δ vs H-DEC | wall_save | n |",
        "|--------|-----------------|------------|-----------|---|",
    ]
    for fam in ("H-DEC", "H-DECK"):
        if fam not in stats:
            continue
        st = stats[fam]
        d = "—" if fam == "H-DEC" else f"{delta:+.4f}"
        save = "—" if fam == "H-DEC" else ("yes" if st.get("wall_save", 0) > 0 else "no")
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {d} | {save} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:deck` → `npm run nano:deck:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--matrix",
        type=Path,
        default=Path("results/nano-lm/student-matrix/matrix.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hdeck-vs-hdec.md"),
    )
    args = p.parse_args()
    text = render(args.matrix)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
