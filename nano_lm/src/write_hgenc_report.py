"""Render H-GENC smoke — genetic serve genome vs PACK/EARLY parent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from genc_ops import decide_hgenc


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
    parent = data.get("parent_means") or {}
    best = data.get("best_means") or {}
    decision = data.get("decision") or decide_hgenc(
        parent=parent, best=best, n_rows=int(best.get("n", 0))
    )
    pack = data.get("pack") or {}
    code = data.get("code_teacher") or {}
    story = data.get("story_teacher") or {}
    genes = data.get("best_genes") or []
    gene_s = json.dumps(genes[0] if genes else data.get("parent_gene"), sort_keys=True)
    title = "Formal H-GENC" if formal else "H-GENC smoke"
    lines = [
        f"# {title} — genetic context/serve genome under BUD",
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
            "Wave X genetics (narrow): evolve "
            "`{k_retrieve, chunk_len, stride, quant_bits, exit_depth}` "
            f"(pop≤{data.get('pop', 'smoke')}, gens={data.get('gens', 'frozen')}, "
            "fit≠eval) under BUD wall ceiling. Parent = PACK/EARLY default genome "
            "on prog@128. Gate: story+code ≥ parent−ε, wall≤BUD parent, and "
            "(code↑ or wall↓). Not tip-compose; retrieve gene ≠ RAG PROMOTE claim.",
            f"Mode: `{data.get('mode')}`; mechanism=`{data.get('mechanism')}`; "
            f"pack=`{pack}`; max_new=`{data.get('max_new')}`; "
            f"n_chunks=`{data.get('n_chunks')}`; "
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
            f"Best gene (seed0): `{gene_s}`",
            "",
            "## Arms (eval holdout)",
            "",
            "| arm | mean story_teacher_lp | mean code_teacher_lp | "
            "mean wall_ms | weight_bytes | n |",
            "|-----|-----------------------|----------------------|"
            "--------------|--------------|---|",
            _arm("PACK/EARLY parent", parent),
            _arm("H-GENC best", best),
            "",
            "Tips unchanged. Wave X GENC (context/serve genome).",
            "",
        ]
    )
    cmd = (
        "`npm run nano:formal:hgenc` → `npm run nano:formal:hgenc:report`"
        if formal
        else "`npm run nano:genc` → `npm run nano:genc:report`"
    )
    lines.extend([f"Commands: {cmd}.", ""])
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--smoke",
        type=Path,
        default=Path("results/nano-lm/student-matrix/hgenc_smoke.json"),
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("docs/results/nano-lm/hgenc-genome.md"),
    )
    args = p.parse_args()
    text = render(args.smoke, formal=False)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
