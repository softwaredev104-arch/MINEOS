"""Leakage-aware comparison of lightweight CPU classifiers on bearing features."""

from __future__ import annotations

import numpy as np
import sklearn
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .dataset import DatasetBundle
from .train import make_model


def _candidate_models(random_state: int) -> dict:
    return {
        "logistic_regression": make_model(random_state),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=250,
            max_features="sqrt",
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1,
            random_state=random_state,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            max_features="sqrt",
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=random_state,
        ),
        "rbf_svm": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("classifier", SVC(C=2.0, kernel="rbf", class_weight="balanced")),
            ]
        ),
    }


def compare_models(
    dataset: DatasetBundle,
    *,
    requested_folds: int = 5,
    random_state: int = 42,
) -> dict:
    """Compare CPU baselines using identical StratifiedGroupKFold partitions."""
    if requested_folds < 2:
        raise ValueError("requested_folds must be at least 2")

    labels = sorted(set(dataset.y.tolist()))
    groups_by_label = {
        label: len(set(dataset.groups[dataset.y == label].tolist())) for label in labels
    }
    n_splits = min(requested_folds, min(groups_by_label.values(), default=0))
    if n_splits < 2:
        raise ValueError(
            "At least two independent groups per label are required for grouped comparison; "
            f"observed groups per label: {groups_by_label}"
        )

    splitter = StratifiedGroupKFold(
        n_splits=n_splits, shuffle=True, random_state=random_state
    )
    splits = list(splitter.split(dataset.X, dataset.y, groups=dataset.groups))
    for fold_number, (train_indices, test_indices) in enumerate(splits, start=1):
        train_groups = set(dataset.groups[train_indices].tolist())
        test_groups = set(dataset.groups[test_indices].tolist())
        if train_groups & test_groups:
            raise RuntimeError("Group leakage detected between comparison folds")
        if set(dataset.y[train_indices].tolist()) != set(labels):
            raise ValueError(
                f"Fold {fold_number} training partition does not contain every label; "
                "add independent recordings or revise the grouping"
            )

    results = {}
    for model_name in _candidate_models(random_state):
        predictions = np.empty(dataset.y.shape, dtype=object)
        predictions[:] = ""
        fold_summaries = []
        for fold_number, (train_indices, test_indices) in enumerate(splits, start=1):
            model = _candidate_models(random_state + fold_number)[model_name]
            model.fit(dataset.X[train_indices], dataset.y[train_indices])
            predictions[test_indices] = model.predict(dataset.X[test_indices]).astype(str)
            fold_summaries.append(
                {
                    "fold": fold_number,
                    "train_groups": len(set(dataset.groups[train_indices].tolist())),
                    "validation_groups": len(set(dataset.groups[test_indices].tolist())),
                    "validation_windows": int(len(test_indices)),
                }
            )

        if np.any(predictions == ""):
            raise RuntimeError(f"{model_name} did not produce predictions for every window")
        predicted = predictions.astype(str)
        results[model_name] = {
            "accuracy": float(accuracy_score(dataset.y, predicted)),
            "macro_f1": float(
                f1_score(dataset.y, predicted, average="macro", zero_division=0)
            ),
            "confusion_matrix": confusion_matrix(
                dataset.y, predicted, labels=labels
            ).tolist(),
            "classification_report": classification_report(
                dataset.y,
                predicted,
                labels=labels,
                output_dict=True,
                zero_division=0,
            ),
            "folds": fold_summaries,
        }

    return {
        "task": "bearing_fault_classification",
        "validation": "identical_stratified_group_k_fold_out_of_fold_partitions",
        "requested_folds": requested_folds,
        "actual_folds": n_splits,
        "labels": labels,
        "groups_per_label": groups_by_label,
        "n_windows": int(len(dataset.y)),
        "n_recordings": int(len(set(dataset.recording_ids.tolist()))),
        "n_groups": int(len(set(dataset.groups.tolist()))),
        "sample_rate_hz": dataset.sample_rate_hz,
        "feature_names": list(dataset.feature_names),
        "sklearn_version": sklearn.__version__,
        "models": results,
    }
