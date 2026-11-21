"""XJTU-SY run-to-failure loading and group-aware RUL model comparison."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

from .features import FEATURE_NAMES, extract_features


@dataclass(frozen=True)
class RULBundle:
    X: np.ndarray
    y_minutes: np.ndarray
    groups: np.ndarray
    recording_ids: np.ndarray
    time_minutes: np.ndarray
    operating_conditions: np.ndarray
    failures: np.ndarray
    feature_names: tuple[str, ...]


def load_xjtu_rul_dataset(
    *,
    root: str | Path,
    manifest_output: str | Path,
    expected_sample_rate_hz: float = 25600.0,
    expected_signal_length: int = 32768,
) -> tuple[RULBundle, Path, dict]:
    """Pair horizontal/vertical snapshots and preserve run-level RUL provenance.

    The upstream XJTU-SY builder derives RUL from each complete run's last snapshot.
    Splits must be made by run_id (bearing) or operating_condition, never by snapshot.
    """
    try:
        import bearing_datasets as bd
    except ImportError as exc:
        raise RuntimeError(
            "The optional bearing-datasets bridge is not installed. "
            "Install with: pip install -e '.[datasets]'"
        ) from exc

    root_path = Path(root).expanduser().resolve()
    ds = bd.open("xjtu_sy", root=root_path)
    metadata = ds.metadata()
    required = {
        "signal_id", "recording_id", "channel", "run_id", "time_s", "rul_s",
        "fs", "speed_rpm", "load", "operating_condition", "failure",
    }
    missing = required - set(metadata.columns)
    if missing:
        raise ValueError(f"XJTU-SY metadata is missing columns: {sorted(missing)}")

    selected = metadata[
        metadata["channel"].astype(str).str.lower().isin({"horizontal", "vertical"})
    ].copy()
    if selected.empty:
        raise ValueError("XJTU-SY contains no horizontal/vertical vibration channels")

    rates = sorted({float(v) for v in selected["fs"].tolist()})
    if rates != [float(expected_sample_rate_hz)]:
        raise ValueError(
            f"Expected XJTU-SY at {expected_sample_rate_hz:g} Hz; found {rates}"
        )

    feature_names = tuple(
        [f"horizontal__{name}" for name in FEATURE_NAMES]
        + [f"vertical__{name}" for name in FEATURE_NAMES]
        + ["metadata__speed_rpm", "metadata__load_kN"]
    )
    feature_rows: list[np.ndarray] = []
    targets: list[float] = []
    groups: list[str] = []
    recording_ids: list[str] = []
    times: list[float] = []
    conditions: list[str] = []
    failures: list[str] = []
    manifest_rows: list[dict[str, str]] = []

    for recording_id, snapshot in selected.groupby("recording_id", sort=True):
        by_channel = {
            str(row["channel"]).lower(): row
            for _, row in snapshot.iterrows()
        }
        if set(by_channel) != {"horizontal", "vertical"} or len(snapshot) != 2:
            raise ValueError(
                f"{recording_id}: expected exactly one horizontal and one vertical signal"
            )

        horizontal = by_channel["horizontal"]
        vertical = by_channel["vertical"]
        shared_fields = (
            "run_id", "time_s", "rul_s", "fs", "speed_rpm", "load",
            "operating_condition", "failure",
        )
        for field in shared_fields:
            if str(horizontal[field]) != str(vertical[field]):
                raise ValueError(f"{recording_id}: channel metadata disagrees for {field}")

        run_id = str(horizontal["run_id"])
        time_s = float(horizontal["time_s"])
        rul_s = float(horizontal["rul_s"])
        speed_rpm = float(horizontal["speed_rpm"])
        load_kn = float(horizontal["load"])
        condition = str(horizontal["operating_condition"])
        failure = str(horizontal["failure"])
        if not np.all(np.isfinite([time_s, rul_s, speed_rpm, load_kn])):
            raise ValueError(f"{recording_id}: non-finite RUL or operating metadata")
        if time_s < 0 or rul_s < 0 or speed_rpm <= 0 or load_kn <= 0:
            raise ValueError(f"{recording_id}: invalid time, RUL, speed or load")

        channel_features = []
        signal_ids = []
        for channel_name in ("horizontal", "vertical"):
            row = by_channel[channel_name]
            signal_id = str(row["signal_id"])
            signal = np.asarray(ds.signal(signal_id), dtype=np.float64).reshape(-1)
            if signal.size != expected_signal_length:
                raise ValueError(
                    f"{signal_id}: expected {expected_signal_length} samples, got {signal.size}"
                )
            if not np.all(np.isfinite(signal)):
                raise ValueError(f"{signal_id}: signal contains NaN or infinite values")
            channel_features.append(
                extract_features(signal, sample_rate_hz=expected_sample_rate_hz)
            )
            signal_ids.append(signal_id)

        feature_rows.append(
            np.concatenate(
                [channel_features[0], channel_features[1], [speed_rpm, load_kn]]
            )
        )
        targets.append(rul_s / 60.0)
        groups.append(run_id)
        recording_ids.append(str(recording_id))
        times.append(time_s / 60.0)
        conditions.append(condition)
        failures.append(failure)
        manifest_rows.append(
            {
                "recording_id": str(recording_id),
                "run_id": run_id,
                "horizontal_signal_id": signal_ids[0],
                "vertical_signal_id": signal_ids[1],
                "time_s": f"{time_s:g}",
                "rul_s": f"{rul_s:g}",
                "rul_minutes": f"{rul_s / 60.0:g}",
                "sample_rate_hz": f"{expected_sample_rate_hz:g}",
                "speed_rpm": f"{speed_rpm:g}",
                "load_kN": f"{load_kn:g}",
                "operating_condition": condition,
                "terminal_failure": failure,
            }
        )

    if not feature_rows:
        raise ValueError("XJTU-SY produced no paired vibration snapshots")

    manifest_path = Path(manifest_output)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)

    run_table = pd.DataFrame(
        {
            "run_id": groups,
            "time_minutes": times,
            "rul_minutes": targets,
        }
    )
    for run_id, run in run_table.groupby("run_id"):
        run = run.sort_values("time_minutes")
        if run["time_minutes"].duplicated().any():
            raise ValueError(f"{run_id}: duplicate snapshot time")
        if not np.all(np.diff(run["time_minutes"].to_numpy()) > 0):
            raise ValueError(f"{run_id}: snapshot time must increase strictly")
        if not np.all(np.diff(run["rul_minutes"].to_numpy()) <= 0):
            raise ValueError(f"{run_id}: RUL must be non-increasing")
        if not np.isclose(float(run["rul_minutes"].iloc[-1]), 0.0):
            raise ValueError(f"{run_id}: final snapshot must have zero RUL")

    upstream_manifest = Path(ds.path) / "manifest.json"
    upstream_hash = (
        hashlib.sha256(upstream_manifest.read_bytes()).hexdigest()
        if upstream_manifest.is_file() else None
    )
    source_info = {
        "dataset_name": "xjtu_sy",
        "dataset_citation": ds.cite() if hasattr(ds, "cite") else (
            "Wang, B., Lei, Y., Li, N., & Li, N. (2020). A Hybrid Prognostics Approach "
            "for Estimating Remaining Useful Life of Rolling Element Bearings. "
            "IEEE Transactions on Reliability, 69(1), 401-412. doi:10.1109/TR.2018.2882682"
        ),
        "dataset_library": "bearing-datasets",
        "dataset_library_version": getattr(bd, "__version__", "unknown"),
        "upstream_manifest_sha256": upstream_hash,
        "data_license": "unspecified; public prognostics validation is stated by authors; commercial/redistribution rights unconfirmed",
        "sample_rate_hz": float(expected_sample_rate_hz),
        "samples_per_channel": int(expected_signal_length),
        "snapshot_duration_seconds": float(expected_signal_length / expected_sample_rate_hz),
        "snapshot_interval_seconds": 60.0,
        "target": "rul_s converted to minutes; terminal snapshot has zero RUL",
        "grouping": "run_id (one complete bearing run)",
        "split_warning": "Never split snapshots randomly; hold out complete run_id groups or operating conditions",
        "n_snapshots": int(len(recording_ids)),
        "n_runs": int(len(set(groups))),
        "operating_conditions": sorted(set(conditions)),
        "terminal_failures": sorted(set(failures)),
        "raw_data_committed": False,
    }
    bundle = RULBundle(
        X=np.vstack(feature_rows).astype(np.float32),
        y_minutes=np.asarray(targets, dtype=np.float32),
        groups=np.asarray(groups, dtype=str),
        recording_ids=np.asarray(recording_ids, dtype=str),
        time_minutes=np.asarray(times, dtype=np.float32),
        operating_conditions=np.asarray(conditions, dtype=str),
        failures=np.asarray(failures, dtype=str),
        feature_names=feature_names,
    )
    return bundle, manifest_path, source_info


def _rul_models(random_state: int) -> dict:
    return {
        "random_forest": RandomForestRegressor(
            n_estimators=160,
            max_features=0.7,
            min_samples_leaf=3,
            n_jobs=-1,
            random_state=random_state,
        ),
        "extra_trees": ExtraTreesRegressor(
            n_estimators=160,
            max_features=0.7,
            min_samples_leaf=3,
            n_jobs=-1,
            random_state=random_state,
        ),
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=140,
            learning_rate=0.06,
            max_leaf_nodes=15,
            l2_regularization=1.0,
            random_state=random_state,
        ),
        "ridge": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("regressor", Ridge(alpha=10.0)),
            ]
        ),
    }


def _evaluate_split(bundle: RULBundle, *, split_by: str, requested_folds: int) -> dict:
    if split_by == "bearing":
        groups = bundle.groups
        n_groups = len(set(groups.tolist()))
        split_count = min(requested_folds, n_groups)
        splitter = GroupKFold(n_splits=split_count)
        split_label = "GroupKFold by run_id (complete bearings held out)"
    elif split_by == "condition":
        groups = bundle.operating_conditions
        n_groups = len(set(groups.tolist()))
        split_count = min(requested_folds, n_groups)
        splitter = GroupKFold(n_splits=split_count)
        split_label = "GroupKFold by operating_condition (complete conditions held out)"
    else:
        raise ValueError("split_by must be 'bearing' or 'condition'")

    splits = list(splitter.split(bundle.X, bundle.y_minutes, groups=groups))
    results = {}
    for model_name in _rul_models(42):
        predictions = np.full(bundle.y_minutes.shape, np.nan, dtype=np.float64)
        fold_summaries = []
        for fold_number, (train_idx, test_idx) in enumerate(splits, start=1):
            train_groups = set(groups[train_idx].tolist())
            test_groups = set(groups[test_idx].tolist())
            if train_groups & test_groups:
                raise RuntimeError("Group leakage detected in RUL validation")
            model = _rul_models(42 + fold_number)[model_name]
            model.fit(bundle.X[train_idx], bundle.y_minutes[train_idx])
            predictions[test_idx] = np.maximum(
                0.0, model.predict(bundle.X[test_idx]).astype(np.float64)
            )
            fold_summaries.append(
                {
                    "fold": fold_number,
                    "train_groups": len(train_groups),
                    "validation_groups": len(test_groups),
                    "validation_snapshots": int(len(test_idx)),
                }
            )

        if not np.all(np.isfinite(predictions)):
            raise RuntimeError(f"{model_name} did not predict every RUL snapshot")

        per_run_mae = []
        for run_id in sorted(set(bundle.groups.tolist())):
            mask = bundle.groups == run_id
            if np.any(mask):
                per_run_mae.append(
                    float(mean_absolute_error(bundle.y_minutes[mask], predictions[mask]))
                )
        results[model_name] = {
            "mae_minutes": float(mean_absolute_error(bundle.y_minutes, predictions)),
            "rmse_minutes": float(
                np.sqrt(mean_squared_error(bundle.y_minutes, predictions))
            ),
            "r2": float(r2_score(bundle.y_minutes, predictions)),
            "mean_per_bearing_mae_minutes": float(np.mean(per_run_mae)),
            "per_bearing_mae_minutes": {
                run_id: float(
                    mean_absolute_error(
                        bundle.y_minutes[bundle.groups == run_id],
                        predictions[bundle.groups == run_id],
                    )
                )
                for run_id in sorted(set(bundle.groups.tolist()))
            },
            "folds": fold_summaries,
        }

    return {
        "split_by": split_by,
        "validation": split_label,
        "requested_folds": requested_folds,
        "actual_folds": split_count,
        "n_snapshots": int(len(bundle.y_minutes)),
        "n_groups": int(n_groups),
        "models": results,
    }


def compare_rul_models(
    bundle: RULBundle,
    *,
    bearing_folds: int = 5,
    condition_folds: int = 3,
) -> dict:
    """Evaluate RUL models with bearing-held-out and condition-held-out validation."""
    return {
        "task": "remaining_useful_life_regression",
        "target_unit": "minutes",
        "nonnegative_predictions": True,
        "n_snapshots": int(len(bundle.y_minutes)),
        "n_bearings": int(len(set(bundle.groups.tolist()))),
        "n_operating_conditions": int(len(set(bundle.operating_conditions.tolist()))),
        "feature_names": list(bundle.feature_names),
        "sklearn_version": sklearn.__version__,
        "bearing_holdout": _evaluate_split(
            bundle, split_by="bearing", requested_folds=bearing_folds
        ),
        "condition_holdout": _evaluate_split(
            bundle, split_by="condition", requested_folds=condition_folds
        ),
    }
