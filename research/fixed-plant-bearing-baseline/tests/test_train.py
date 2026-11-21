import numpy as np
import pytest

from mineos_bearing_baseline.dataset import DatasetBundle
from mineos_bearing_baseline.features import FEATURE_NAMES
from mineos_bearing_baseline.train import evaluate_grouped_cv


def _bundle():
    rng = np.random.default_rng(5)
    rows, labels, groups = [], [], []
    for label_index, label in enumerate(("normal", "inner_race", "ball")):
        for group_index in range(4):
            group = f"{label}_{group_index}"
            for _ in range(5):
                rows.append(rng.normal(loc=label_index * 2.5, scale=0.3, size=len(FEATURE_NAMES)))
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
        X=np.zeros((4, len(FEATURE_NAMES)), dtype=np.float32),
        y=np.asarray(["normal", "normal", "ball", "ball"]),
        groups=np.asarray(["n1", "n1", "b1", "b1"]),
        recording_ids=np.asarray(["n1", "n1", "b1", "b1"]),
    )
    with pytest.raises(ValueError, match="At least two independent groups"):
        evaluate_grouped_cv(data)


def test_train_and_save_writes_research_artifacts(tmp_path):
    from mineos_bearing_baseline.train import train_and_save

    data = _bundle()
    manifest = tmp_path / "manifest.csv"
    manifest.write_text("recording_id,filename,label,sample_rate_hz,group_id\\nr1,dummy.mat,normal,12000,g1\\n", encoding="utf-8")
    output = tmp_path / "artifacts"
    metrics = train_and_save(
        data,
        output_dir=output,
        manifest_path=manifest,
        requested_folds=3,
        source_metadata={"dataset_name": "cwru", "channel": "DE"},
    )
    assert metrics["source"]["dataset_name"] == "cwru"
    assert "Source:** cwru" in (output / "model_card.md").read_text(encoding="utf-8")
    assert metrics["deployment_status"] == "research_only_not_site_validated"
    assert metrics["sample_rate_hz"] is None
    for name in ("model.joblib", "metrics.json", "feature_schema.json", "model_card.md"):
        assert (output / name).is_file()


def test_onnx_export_parity_when_optional_dependencies_exist(tmp_path):
    pytest.importorskip("skl2onnx")
    pytest.importorskip("onnxruntime")
    from mineos_bearing_baseline.train import export_onnx, make_model

    data = _bundle()
    model = make_model()
    model.fit(data.X, data.y)
    result = export_onnx(model, data.X[:8], tmp_path / "model.onnx")
    assert result["label_parity"] is True
    assert (tmp_path / "model.onnx").is_file()
