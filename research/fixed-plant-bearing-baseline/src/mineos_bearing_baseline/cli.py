"""Command-line entry point for the MineOS bearing research baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .dataset import load_dataset
from .train import train_and_save


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MineOS research-only bearing baseline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    train = subparsers.add_parser("train", help="run grouped CV and fit the reference baseline")
    train.add_argument("--data-dir", type=Path, required=True, help="directory containing manifest.csv and .mat files")
    train.add_argument("--out-dir", type=Path, default=Path("artifacts/cwru-bearing-baseline"))
    train.add_argument("--channel", choices=["DE", "FE", "BA"], default="DE")
    train.add_argument("--window-size", type=int, default=2048)
    train.add_argument("--stride", type=int, default=2048)
    train.add_argument("--cv-folds", type=int, default=5)
    train.add_argument("--random-state", type=int, default=42)
    train.add_argument("--export-onnx", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "train":
            dataset = load_dataset(
                args.data_dir,
                channel=args.channel,
                window_size=args.window_size,
                stride=args.stride,
            )
            metrics = train_and_save(
                dataset,
                output_dir=args.out_dir,
                manifest_path=args.data_dir / "manifest.csv",
                requested_folds=args.cv_folds,
                random_state=args.random_state,
                make_onnx=args.export_onnx,
            )
            print(json.dumps({k: metrics[k] for k in (
                "task", "actual_folds", "n_windows", "n_groups", "accuracy", "macro_f1",
                "deployment_status"
            )}, indent=2))
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
