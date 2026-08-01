"""Document cleaning filters for N32 pretraining text."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pyarrow.parquet as pq

from n32.data.io_utils import append_jsonl, iter_jsonl, write_json

ROOT = Path(__file__).resolve().parents[2]
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-. ]?)?(?:\(?\d{3}\)?[-. ]?)\d{3}[-. ]?\d{4}\b")
API_KEY_RE = re.compile(r"\b(?:sk|api|key|token)[-_]?[A-Za-z0-9]{16,}\b", re.I)
PRIVATE_IP_RE = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|127\.\d{1,3}\.\d{1,3}\.\d{1,3})\b"
)
# Gopher "symbol" = hash or ellipsis, not ordinary punctuation (datatrove/MassiveText).
GOPHER_SYMBOL_RE = re.compile(r"#|\.\.\.")


def strip_controls(text: str) -> str:
    return CONTROL_RE.sub("", text)


def redact_pii(text: str) -> str:
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    text = API_KEY_RE.sub("[SECRET]", text)
    text = PRIVATE_IP_RE.sub("[IP]", text)
    return text


def mean_word_length(words: list[str]) -> float:
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def symbol_to_word_ratio(text: str, words: list[str]) -> float:
    if not words:
        return 1.0
    symbols = len(GOPHER_SYMBOL_RE.findall(text))
    return symbols / max(len(words), 1)


def line_punct_ratio(lines: list[str]) -> float:
    if not lines:
        return 0.0
    good = sum(1 for ln in lines if ln and ln[-1] in ".!?;:")
    return good / len(lines)


def top_bigram_fraction(words: list[str]) -> float:
    if len(words) < 2:
        return 0.0
    counts: dict[tuple[str, str], int] = {}
    for a, b in zip(words, words[1:]):
        key = (a, b)
        counts[key] = counts.get(key, 0) + 1
    top = max(counts.values())
    return top / (len(words) - 1)


def max_line_repeat_fraction(lines: list[str]) -> float:
    if not lines:
        return 0.0
    counts: dict[str, int] = {}
    for ln in lines:
        counts[ln] = counts.get(ln, 0) + 1
    return max(counts.values()) / len(lines)


def gopher_ok(text: str, is_code: bool) -> bool:
    words = text.split()
    if not (3.0 <= mean_word_length(words) <= 10.0):
        return False
    if symbol_to_word_ratio(text, words) > 0.10:
        return False
    if is_code:
        return True
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # Spec: punctuation rule is prose-only. Short/header lines are not prose.
    prose_lines = [ln for ln in lines if len(ln) >= 40]
    if len(prose_lines) >= 5 and line_punct_ratio(prose_lines) < 0.80:
        return False
    return True


def repetition_ok(text: str) -> bool:
    words = text.split()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if top_bigram_fraction(words) > 0.20:
        return False
    if max_line_repeat_fraction(lines) > 0.30:
        return False
    return True


def length_ok(text: str) -> bool:
    n = len(text)
    return 200 <= n <= 1_000_000


def load_eval_13grams(eval_dir: Path) -> set[str]:
    grams: set[str] = set()
    if not eval_dir.exists():
        return grams
    for path in eval_dir.glob("*.txt"):
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        words = text.split()
        for i in range(max(0, len(words) - 12)):
            grams.add(" ".join(words[i : i + 13]))
    return grams


def contamination_hit(text: str, grams: set[str]) -> bool:
    if not grams:
        return False
    words = text.lower().split()
    for i in range(max(0, len(words) - 12)):
        if " ".join(words[i : i + 13]) in grams:
            return True
    return False


def clean_document(
    text: str, source_id: str, grams: set[str]
) -> tuple[str | None, str]:
    try:
        text.encode("utf-8")
    except UnicodeError:
        return None, "encoding"
    text = strip_controls(text)
    if not length_ok(text):
        return None, "length"
    # FineWeb-Edu already applied MassiveText/Gopher quality filters upstream.
    already_gophered = source_id in {"fineweb_edu"}
    is_code = source_id in {"stack_v2", "tech_docs_seed"}
    if not already_gophered and not gopher_ok(text, is_code=is_code):
        return None, "gopher"
    if not repetition_ok(text):
        return None, "repetition"
    if contamination_hit(text, grams):
        return None, "contamination"
    return redact_pii(text), "keep"


def iter_parquet_texts(path: Path):
    pf = pq.ParquetFile(path)
    for batch in pf.iter_batches(columns=["text"], batch_size=1024):
        for text in batch.column(0).to_pylist():
            if isinstance(text, str) and text:
                yield text


def iter_raw_texts(path: Path):
    if path.suffix == ".parquet":
        yield from iter_parquet_texts(path)
    elif path.suffix == ".txt":
        yield path.read_text(encoding="utf-8", errors="ignore")
    elif path.suffix == ".jsonl":
        for row in iter_jsonl(path):
            text = row.get("text")
            if isinstance(text, str):
                yield text


def clean_one_file(path: Path, out_path: Path, source_id: str, grams: set[str]) -> dict:
    drops: dict[str, int] = {}
    kept = 0
    contam = 0
    batch: list[dict] = []
    if out_path.exists():
        out_path.unlink()
    for text in iter_raw_texts(path):
        cleaned, reason = clean_document(text, source_id, grams)
        if cleaned is None:
            drops[reason] = drops.get(reason, 0) + 1
            if reason == "contamination":
                contam += 1
            continue
        kept += 1
        encoded = cleaned.encode("utf-8")
        batch.append(
            {
                "id": hashlib.sha256(encoded).hexdigest()[:16],
                "source_id": source_id,
                "text": cleaned,
                "bytes": len(encoded),
            }
        )
        if len(batch) >= 2000:
            append_jsonl(out_path, batch)
            batch = []
    if batch:
        append_jsonl(out_path, batch)
    return {"kept": kept, "drops": drops, "contamination_removed": contam}


def _clean_file_job(args: tuple[str, str, str, list[str]]) -> dict:
    path_s, out_s, source_id, gram_list = args
    grams = set(gram_list)
    return clean_one_file(Path(path_s), Path(out_s), source_id, grams)


def clean_tree(in_dir: Path, out_path: Path, eval_dir: Path, source_id: str) -> dict:
    grams = load_eval_13grams(eval_dir)
    gram_list = list(grams)
    files = [
        p
        for p in sorted(in_dir.rglob("*"))
        if p.is_file() and p.suffix in {".parquet", ".txt", ".jsonl"}
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    drops: dict[str, int] = {}
    kept = 0
    contam = 0
    part_paths = []
    jobs = []
    for i, path in enumerate(files):
        part = out_path.with_suffix(f".part{i}.jsonl")
        part_paths.append(part)
        jobs.append((str(path), str(part), source_id, gram_list))
    workers = min(4, max(1, len(jobs)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for report in pool.map(_clean_file_job, jobs):
            kept += report["kept"]
            contam += report["contamination_removed"]
            for k, v in report["drops"].items():
                drops[k] = drops.get(k, 0) + v
    with out_path.open("w", encoding="utf-8") as out:
        for part in part_paths:
            if part.exists():
                with part.open("r", encoding="utf-8") as inp:
                    for line in inp:
                        out.write(line)
                part.unlink()
    return {"kept": kept, "drops": drops, "contamination_removed": contam}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Clean N32 raw documents")
    p.add_argument("--in", dest="in_dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--source-id", type=str, required=True)
    p.add_argument("--eval-sets", type=Path, default=ROOT / "data" / "eval_sets")
    p.add_argument("--report", type=Path, default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    report = clean_tree(args.in_dir, args.out, args.eval_sets, args.source_id)
    if args.report:
        write_json(args.report, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
