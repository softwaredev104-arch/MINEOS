import numpy as np
import pytest

from mineos_bearing_baseline.comparison import compare_models
from mineos_bearing_baseline.dataset import DatasetBundle
from mineos_bearing_baseline.features import FEATURE_NAMES


def _bundle():
    rng = np.random.default_rng(21)
    rows, labels, groups = [], [], []
    for label_index, label in enumerate(("ball", "inner_race", "outer_race")):
        for group_index in range(4):
            group = f"{label}_{group_index}"
            for _ in range(5):
                rows.append(rng.normal(loc=label_index * 2.0, scale=0.4, size=len(FEATURE_NAMES)))
                labels.append(label)
                groups.append(group)
    return DatasetBundle(
        X=np.asarray(rows, dtype=np.float32),
        y=np.asarray(labels, dtype=str),
        groups=np.asarray(groups, dtype=str),
        recording_ids=np.asarray(groups, dtype=str),
        sample_rate_hz=12000,
    )


def test_model_comparison_uses_same_grouped_folds_for_every_candidate():
    result = compare_models(_bundle(), requested_folds=4, random_state=11)
    assert result["actual_folds"] == 4
    assert set(result["models"]) == {
        "logistic_regression",
        "extra_trees",
        "random_forest",
        "rbf_svm",
    }
    for model_result in result["models"].values():
        assert 0 <= model_result["accuracy"] <= 1
        assert 0 <= model_result["macro_f1"] <= 1
        assert len(model_result["folds"]) == 4


def test_model_comparison_requires_multiple_groups_per_label():
    data = DatasetBundle(
        X=np.zeros((4, len(FEATURE_NAMES)), dtype=np.float32),
        y=np.asarray(["normal", "normal", "ball", "ball"]),
        groups=np.asarray(["n1", "n1", "b1", "b1"]),
        recording_ids=np.asarray(["n1", "n1", "b1", "b1"]),
    )
    with pytest.raises(ValueError, match="At least two independent groups"):
        compare_models(data)
