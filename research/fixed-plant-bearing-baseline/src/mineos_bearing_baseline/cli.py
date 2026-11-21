"""Command-line entry point for the MineOS bearing research baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .comparison import compare_models
from .dataset import load_dataset
from .library_dataset import load_standardized_dataset
from .rul import compare_rul_models, load_xjtu_rul_dataset
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

    library = subparsers.add_parser(
        "train-library",
        help="train from a dataset built by the optional bearing-datasets library",
    )
    library.add_argument("--data-root", type=Path, required=True, help="root configured for bearing-datasets")
    library.add_argument("--dataset", default="cwru", help="built dataset name (default: cwru)")
    library.add_argument("--channel", default="DE", help="exact channel from dataset metadata")
    library.add_argument("--sample-rate", type=float, default=None, help="required when selected channel has multiple rates")
    library.add_argument("--out-dir", type=Path, default=Path("artifacts/cwru-library-baseline"))
    library.add_argument("--window-size", type=int, default=2048)
    library.add_argument("--stride", type=int, default=2048)
    library.add_argument("--cv-folds", type=int, default=5)
    library.add_argument("--random-state", type=int, default=42)
    library.add_argument("--export-onnx", action="store_true")

    compare = subparsers.add_parser(
        "compare-library",
        help="compare CPU classifiers on identical group-aware validation folds",
    )
    compare.add_argument("--data-root", type=Path, required=True)
    compare.add_argument("--dataset", default="cwru")
    compare.add_argument("--channel", default="DE")
    compare.add_argument("--sample-rate", type=float, required=True)
    compare.add_argument("--out-dir", type=Path, required=True)
    compare.add_argument("--window-size", type=int, default=2048)
    compare.add_argument("--stride", type=int, default=2048)
    compare.add_argument("--cv-folds", type=int, default=5)
    compare.add_argument("--random-state", type=int, default=42)

    rul = subparsers.add_parser(
        "train-rul-library",
        help="benchmark XJTU-SY run-to-failure RUL models with bearing/condition holdouts",
    )
    rul.add_argument("--data-root", type=Path, required=True)
    rul.add_argument("--out-dir", type=Path, required=True)
    rul.add_argument("--bearing-folds", type=int, default=5)
    rul.add_argument("--condition-folds", type=int, default=3)
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
        elif args.command == "train-library":
            dataset, manifest_path, source_metadata = load_standardized_dataset(
                root=args.data_root,
                dataset_name=args.dataset,
                channel=args.channel,
                sample_rate_hz=args.sample_rate,
                window_size=args.window_size,
                stride=args.stride,
                manifest_output=args.out_dir / "source_manifest.csv",
            )
            metrics = train_and_save(
                dataset,
                output_dir=args.out_dir,
                manifest_path=manifest_path,
                requested_folds=args.cv_folds,
                random_state=args.random_state,
                make_onnx=args.export_onnx,
                source_metadata=source_metadata,
            )
            print(json.dumps({
                "task": metrics["task"],
                "dataset": args.dataset,
                "sample_rate_hz": metrics["sample_rate_hz"],
                "actual_folds": metrics["actual_folds"],
                "n_windows": metrics["n_windows"],
                "n_groups": metrics["n_groups"],
                "accuracy": metrics["accuracy"],
                "macro_f1": metrics["macro_f1"],
                "deployment_status": metrics["deployment_status"],
                "source_manifest": str(manifest_path),
            }, indent=2))
        elif args.command == "compare-library":
            dataset, manifest_path, source_metadata = load_standardized_dataset(
                root=args.data_root,
                dataset_name=args.dataset,
                channel=args.channel,
                sample_rate_hz=args.sample_rate,
                window_size=args.window_size,
                stride=args.stride,
                manifest_output=args.out_dir / "comparison_source_manifest.csv",
            )
            comparison = compare_models(
                dataset,
                requested_folds=args.cv_folds,
                random_state=args.random_state,
            )
            comparison["source"] = source_metadata
            args.out_dir.mkdir(parents=True, exist_ok=True)
            output = args.out_dir / "model_comparison.json"
            output.write_text(json.dumps(comparison, indent=2, sort_keys=True), encoding="utf-8")
            print(json.dumps({
                name: {"accuracy": result["accuracy"], "macro_f1": result["macro_f1"]}
                for name, result in comparison["models"].items()
            }, indent=2))
        elif args.command == "train-rul-library":
            args.out_dir.mkdir(parents=True, exist_ok=True)
            bundle, manifest_path, source_metadata = load_xjtu_rul_dataset(
                root=args.data_root,
                manifest_output=args.out_dir / "source_manifest.csv",
            )
            metrics = compare_rul_models(
                bundle,
                bearing_folds=args.bearing_folds,
                condition_folds=args.condition_folds,
            )
            metrics["source"] = source_metadata
            metrics_path = args.out_dir / "metrics.json"
            metrics_path.write_text(
                json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8"
            )
            model_card = [
                "# MineOS XJTU-SY RUL research benchmark",
                "",
                "- Status: research-only; not approved for mine-site deployment",
                "- Task: remaining useful life regression, target in minutes",
                "- Grouping: complete run_id (bearing) and complete operating-condition holdouts",
                "- Inputs: horizontal and vertical vibration features plus known speed/load metadata",
                "- The terminal failure description is provenance only and is not a model input",
                "- Raw recordings are not committed or uploaded as workflow artifacts",
                "- Dataset licence is unspecified; commercial and redistribution rights are unconfirmed",
                "",
                "See metrics.json for group-aware MAE/RMSE/R² and per-bearing errors.",
            ]
            (args.out_dir / "model_card.md").write_text(
                "\\n".join(model_card) + "\\n", encoding="utf-8"
            )
            print(json.dumps({
                "task": metrics["task"],
                "snapshots": metrics["n_snapshots"],
                "bearings": metrics["n_bearings"],
                "conditions": metrics["n_operating_conditions"],
                "bearing_holdout": {
                    name: result["mae_minutes"]
                    for name, result in metrics["bearing_holdout"]["models"].items()
                },
                "condition_holdout": {
                    name: result["mae_minutes"]
                    for name, result in metrics["condition_holdout"]["models"].items()
                },
                "metrics": str(metrics_path),
                "source_manifest": str(manifest_path),
            }, indent=2))
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")
