import numpy as np
import pytest

from mineos_bearing_baseline.dataset import DatasetBundle
from mineos_bearing_baseline.train import evaluate_grouped_cv


def _bundle():
    rng = np.random.default_rng(5)
    rows, labels, groups = [], [], []
    for label_index, label in enumerate(("normal", "inner_race", "ball")):
        for group_index in range(4):
            group = f"{label}_{group_index}"
            for _ in range(5):
                rows.append(rng.normal(loc=label_index * 2.5, scale=0.3, size=16))
                labels.append(label)
                groups.append(group)
    return DatasetBundle(
        X=np.asarray(rows, dtype=np.float32),
        y=np.asarray(labels),
        groups=np.asarray(groups),
        recording_ids=np.asarray(groups),
    )


def test_grouped_cv_returns_complete_oof_predictions():
    data = _bundle()
    metrics, predictions = evaluate_grouped_cv(data, requested_folds=4)
    assert metrics["actual_folds"] == 4
    assert predictions.shape == data.y.shape
    assert 0 <= metrics["macro_f1"] <= 1


def test_group_validation_requires_multiple_groups_per_label():
    data = DatasetBundle(
        X=np.zeros((4, 16), dtype=np.float32),
        y=np.asarray(["normal", "normal", "ball", "ball"]),
        groups=np.asarray(["n1", "n1", "b1", "b1"]),
        recording_ids=np.asarray(["n1", "n1", "b1", "b1"]),
    )
    with pytest.raises(ValueError, match="At least two independent groups"):
        evaluate_grouped_cv(data)
