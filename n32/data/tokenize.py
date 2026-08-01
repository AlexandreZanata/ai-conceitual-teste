"""Tokenize deduplicated text into uint16 shards with a document-level holdout."""

from __future__ import annotations

import argparse
import array
import json
from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel

from n32.data.io_utils import iter_jsonl, write_json

ROOT = Path(__file__).resolve().parents[2]
EOT = "<|endoftext|>"
VOCAB_SIZE = 16_384


def train_tokenizer(
    sample_paths: list[Path], out_path: Path, vocab_size: int = VOCAB_SIZE
) -> Tokenizer:
    tokenizer = Tokenizer(BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=False)
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=["<unk>", EOT],
        show_progress=False,
    )

    def iterator():
        n = 0
        for path in sample_paths:
            for row in iter_jsonl(path):
                yield row["text"]
                n += 1
                if n >= 200_000:
                    return

    tokenizer.train_from_iterator(iterator(), trainer=trainer)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tokenizer.save(str(out_path))
    return tokenizer


def load_or_train_tokenizer(
    tokenizer_path: Path, sample_paths: list[Path]
) -> Tokenizer:
    if tokenizer_path.exists():
        return Tokenizer.from_file(str(tokenizer_path))
    return train_tokenizer(sample_paths, tokenizer_path)


def encode_doc(tokenizer: Tokenizer, text: str) -> list[int]:
    ids = tokenizer.encode(text).ids
    eot_id = tokenizer.token_to_id(EOT)
    if eot_id is None:
        raise RuntimeError("tokenizer missing <|endoftext|>")
    ids.append(eot_id)
    return ids


def write_uint16_shard(path: Path, token_ids: array.array) -> None:
    if token_ids.typecode != "H":
        raise ValueError("expected uint16 array")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        token_ids.tofile(f)


def tokenize_corpus(
    in_path: Path,
    tokenizer: Tokenizer,
    out_dir: Path,
    shard_tokens: int,
    holdout_tokens: int,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("train_*.bin"):
        old.unlink()
    held = out_dir / "heldout.bin"
    if held.exists():
        held.unlink()

    train_ids: array.array = array.array("H")
    hold_ids: array.array = array.array("H")
    hold_docs = 0
    train_docs = 0
    shard_idx = 0
    holdout_doc_ids: set[str] = set()
    train_doc_ids: set[str] = set()
    train_token_count = 0

    def flush_train() -> None:
        nonlocal train_ids, shard_idx, train_token_count
        if not train_ids:
            return
        write_uint16_shard(out_dir / f"train_{shard_idx:05d}.bin", train_ids)
        train_token_count += len(train_ids)
        shard_idx += 1
        train_ids = array.array("H")
        print(
            f"[tokenize] shard={shard_idx} train_tokens={train_token_count}",
            flush=True,
        )

    for row in iter_jsonl(in_path):
        ids = encode_doc(tokenizer, row["text"])
        if any(t > 65535 for t in ids):
            raise ValueError("token id exceeds uint16; vocab_size must be <= 65536")
        doc_id = row["id"]
        if len(hold_ids) < holdout_tokens:
            hold_ids.extend(ids)
            hold_docs += 1
            holdout_doc_ids.add(doc_id)
            continue
        if doc_id in holdout_doc_ids:
            continue
        train_ids.extend(ids)
        train_docs += 1
        train_doc_ids.add(doc_id)
        if len(train_ids) >= shard_tokens:
            flush_train()
    flush_train()
    write_uint16_shard(out_dir / "heldout.bin", hold_ids)
    overlap = len(holdout_doc_ids & train_doc_ids)
    return {
        "train_tokens": train_token_count,
        "heldout_tokens": len(hold_ids),
        "train_docs": train_docs,
        "heldout_docs": hold_docs,
        "doc_overlap": overlap,
        "shards": shard_idx,
        "vocab_size": tokenizer.get_vocab_size(),
    }


def count_bin_tokens(path: Path) -> int:
    return path.stat().st_size // 2


def recount_train_tokens(out_dir: Path) -> int:
    return sum(count_bin_tokens(p) for p in out_dir.glob("train_*.bin"))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Tokenize N32 deduplicated corpus")
    p.add_argument("--in", dest="in_path", type=Path, required=True)
    p.add_argument(
        "--tokenizer",
        type=Path,
        default=ROOT / "artifacts" / "tokenizer" / "n32-16k.json",
    )
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--shard-tokens", type=int, default=100_000_000)
    p.add_argument("--holdout-tokens", type=int, default=10_000_000)
    p.add_argument("--dtype", type=str, default="uint16")
    p.add_argument("--report", type=Path, default=None)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.dtype != "uint16":
        raise SystemExit("only uint16 is supported")
    tokenizer = load_or_train_tokenizer(args.tokenizer, [args.in_path])
    report = tokenize_corpus(
        args.in_path,
        tokenizer,
        args.out,
        shard_tokens=args.shard_tokens,
        holdout_tokens=args.holdout_tokens,
    )
    report["train_tokens"] = recount_train_tokens(args.out)
    if args.report:
        write_json(args.report, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
