"""Grouped cross-validation and reference CPU classifier."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .dataset import DatasetBundle


def make_model(random_state: int = 42) -> Pipeline:
    """Create a small, interpretable CPU baseline."""
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
        ]
    )


def evaluate_grouped_cv(
    dataset: DatasetBundle,
    *,
    requested_folds: int = 5,
    random_state: int = 42,
) -> tuple[dict, np.ndarray]:
    """Generate out-of-fold predictions with no group crossing a fold boundary."""
    if requested_folds < 2:
        raise ValueError("requested_folds must be at least 2")
    labels = sorted(set(dataset.y.tolist()))
    groups_by_label = {
        label: len(set(dataset.groups[dataset.y == label].tolist())) for label in labels
    }
    minimum_groups = min(groups_by_label.values(), default=0)
    n_splits = min(requested_folds, minimum_groups)
    if n_splits < 2:
        raise ValueError(
            "At least two independent groups per label are required for grouped validation; "
            f"observed groups per label: {groups_by_label}"
        )

    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    predictions = np.empty(dataset.y.shape, dtype=object)
    predictions[:] = ""
    fold_summaries = []
    for fold_number, (train_indices, test_indices) in enumerate(
        splitter.split(dataset.X, dataset.y, groups=dataset.groups), start=1
    ):
        train_groups = set(dataset.groups[train_indices].tolist())
        test_groups = set(dataset.groups[test_indices].tolist())
        if train_groups & test_groups:
            raise RuntimeError("Group leakage detected between a training and validation fold")
        if set(dataset.y[train_indices].tolist()) != set(labels):
            raise ValueError(
                f"Fold {fold_number} training partition does not contain every label; "
                "add independent recordings or revise the grouping"
            )
        model = make_model(random_state + fold_number)
        model.fit(dataset.X[train_indices], dataset.y[train_indices])
        predictions[test_indices] = model.predict(dataset.X[test_indices]).astype(str)
        fold_summaries.append(
            {
                "fold": fold_number,
                "train_groups": len(train_groups),
                "validation_groups": len(test_groups),
                "validation_windows": int(len(test_indices)),
            }
        )

    if np.any(predictions == ""):
        raise RuntimeError("Grouped cross-validation did not produce a prediction for every window")
    report = classification_report(
        dataset.y,
        predictions.astype(str),
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    metrics = {
        "task": "bearing_fault_classification",
        "validation": "stratified_group_k_fold_out_of_fold",
        "requested_folds": requested_folds,
        "actual_folds": n_splits,
        "labels": labels,
        "groups_per_label": groups_by_label,
        "n_windows": int(len(dataset.y)),
        "n_recordings": int(len(set(dataset.recording_ids.tolist()))),
        "n_groups": int(len(set(dataset.groups.tolist()))),
        "sample_rate_hz": dataset.sample_rate_hz,
        "accuracy": float(accuracy_score(dataset.y, predictions)),
        "macro_f1": float(f1_score(dataset.y, predictions, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(dataset.y, predictions, labels=labels).tolist(),
        "classification_report": report,
        "folds": fold_summaries,
        "sklearn_version": sklearn.__version__,
    }
    return metrics, predictions.astype(str)


def export_onnx(model: Pipeline, sample: np.ndarray, output_path: Path) -> dict:
    """Export and smoke-test ONNX Runtime inference; raise if parity fails."""
    try:
        from onnxruntime import InferenceSession
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
    except ImportError as exc:
        raise RuntimeError(
            "ONNX export requires the optional dependencies; install with: pip install -e '.[onnx]'"
        ) from exc
    onnx_model = convert_sklearn(
        model,
        initial_types=[("features", FloatTensorType([None, sample.shape[1]]))],
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(onnx_model.SerializeToString())
    session = InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    actual = session.run(None, {input_name: np.asarray(sample, dtype=np.float32)})[0]
    expected = model.predict(sample)
    actual_labels = np.asarray(actual).astype(str).reshape(-1)
    if not np.array_equal(actual_labels, expected.astype(str)):
        output_path.unlink(missing_ok=True)
        raise RuntimeError("ONNX Runtime labels do not match the native scikit-learn model")
    return {
        "onnx_runtime_version": __import__("onnxruntime").__version__,
        "onnx_input_name": input_name,
        "parity_rows_checked": int(len(sample)),
        "label_parity": True,
    }


def train_and_save(
    dataset: DatasetBundle,
    *,
    output_dir: str | Path,
    manifest_path: str | Path,
    requested_folds: int = 5,
    random_state: int = 42,
    make_onnx: bool = False,
    source_metadata: dict | None = None,
) -> dict:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    metrics, _ = evaluate_grouped_cv(
        dataset, requested_folds=requested_folds, random_state=random_state
    )
    model = make_model(random_state)
    model.fit(dataset.X, dataset.y)
    joblib.dump(model, output_path / "model.joblib")

    manifest_bytes = Path(manifest_path).read_bytes()
    metrics["manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    metrics["feature_names"] = list(dataset.feature_names)
    metrics["feature_dtype"] = "float32"
    metrics["model"] = "StandardScaler + class-balanced LogisticRegression"
    metrics["random_state"] = random_state
    if source_metadata:
        metrics["source"] = source_metadata
    metrics["deployment_status"] = "research_only_not_site_validated"

    if make_onnx:
        metrics["onnx_export"] = export_onnx(
            model, dataset.X[: min(16, len(dataset.X))], output_path / "model.onnx"
        )
    (output_path / "metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8"
    )
    schema = {
        "schema_version": "1.0.0",
        "task": "bearing_fault_classification",
        "feature_names": list(dataset.feature_names),
        "feature_dtype": "float32",
        "sample_rate_hz": dataset.sample_rate_hz,
        "labels": sorted(set(dataset.y.tolist())),
        "channel": "from dataset manifest and CLI configuration",
        "missing_value_policy": "reject non-finite signal windows; no silent imputation",
    }
    (output_path / "feature_schema.json").write_text(
        json.dumps(schema, indent=2), encoding="utf-8"
    )
    model_card = f"""# MineOS bearing baseline model card

- **Model:** StandardScaler + class-balanced LogisticRegression
- **Task:** Bearing fault classification (normal / inner race / ball / outer race)
- **Status:** Research only; not site validated and not approved for maintenance decisions
- **Validation:** {metrics['validation']} ({metrics['actual_folds']} folds)
- **Windows:** {metrics['n_windows']}
- **Recordings:** {metrics['n_recordings']}
- **Groups:** {metrics['n_groups']}
- **Accuracy:** {metrics['accuracy']:.4f}
- **Macro F1:** {metrics['macro_f1']:.4f}
- **Manifest SHA-256:** {metrics['manifest_sha256']}
- **Source:** {metrics.get('source', {}).get('dataset_name', 'manifest-based local files')}

## Intended use

Reproducible method/pipeline baseline for vibration-based bearing fault classification on the dataset represented by the accompanying manifest. This is not a remaining-useful-life (RUL), future failure-risk or field-deployment model.

## Important limitations

The CWRU test-rig dataset contains seeded bearing defects. Laboratory data does not establish performance on mine equipment, installed sensors, different bearing designs, variable loads, mounting positions, real operating noise or natural degradation. Grouped validation only protects the group definition supplied in the manifest; it does not prove unseen-asset generalization unless those groups correctly represent independent assets.

## Operational restrictions

Do not use this model for autonomous actions, safety functions, maintenance approval or work-order creation. MineOS domain experts must review the task, data rights, validation design and prospective shadow results before any customer-facing pilot.
"""
    (output_path / "model_card.md").write_text(model_card, encoding="utf-8")
    return metrics
