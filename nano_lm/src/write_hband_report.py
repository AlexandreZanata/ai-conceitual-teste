"""Render H-BAND smoke vs H-CASC / H-DECK markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from band_ops import decide_hband
from matrix_report_lib import mean_by_family


def render(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    stats = mean_by_family(data["rows"])
    s = stats.get("H-BAND", {})
    decision = decide_hband(s, stats) if s else "needs H-BAND rows"
    lines = [
        "# H-BAND smoke vs H-CASC / H-DECK (UCB1 gene arms)",
        "",
        "Fixed gene arms; UCB1 allocates teacher scores (no mutate pop).",
        "Pull budget matched to H-CASC mid+final teacher scores.",
        "Kill if ≤ max(H-DECK, H-CASC).",
        "",
        "| family | mean teacher_lp | mean teacher_fwd | n |",
        "|--------|-----------------|------------------|---|",
    ]
    fwd: dict[str, list[float]] = {}
    for r in data["rows"]:
        fwd.setdefault(str(r["family"]), []).append(float(r["teacher_forwards"]))
    for fam in ("H-DECK", "H-CASC", "H-BAND"):
        if fam not in stats:
            continue
        st = stats[fam]
        fw = fwd.get(fam, [])
        mean_fw = sum(fw) / len(fw) if fw else float("nan")
        lines.append(
            f"| {fam} | {st['mean_lp']:.4f} | {mean_fw:.0f} | {int(st['n'])} |"
        )
    lines.extend(
        [
            "",
            f"**Decision: {decision}**",
            "",
            "Commands: `npm run nano:band` → `npm run nano:band:report`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/band_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hband-vs-hcasc.md"),
    )
    args = p.parse_args()
    text = render(args.smoke)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
