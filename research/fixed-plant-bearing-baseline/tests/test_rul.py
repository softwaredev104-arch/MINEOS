import json
import sys
from types import SimpleNamespace

import numpy as np
import pandas as pd

from mineos_bearing_baseline.features import FEATURE_NAMES
from mineos_bearing_baseline.rul import compare_rul_models, load_xjtu_rul_dataset


def _fake_xjtu(tmp_path):
    rows = []
    signals = {}
    for run_index, (run_id, condition, rpm, load, failure) in enumerate(
        [
            ("Bearing1_1", "35Hz12kN", 2100.0, 12.0, "outer race"),
            ("Bearing1_2", "35Hz12kN", 2100.0, 12.0, "cage"),
            ("Bearing2_1", "37.5Hz11kN", 2250.0, 11.0, "inner race"),
        ]
    ):
        for snapshot_index in range(2):
            recording_id = f"{run_id}_{snapshot_index + 1:04d}"
            for channel_index, channel in enumerate(("horizontal", "vertical")):
                signal_id = f"{recording_id}/{channel}"
                rows.append(
                    {
                        "signal_id": signal_id,
                        "recording_id": recording_id,
                        "channel": channel,
                        "run_id": run_id,
                        "time_s": snapshot_index * 60.0,
                        "rul_s": (1 - snapshot_index) * 60.0,
                        "fs": 25600.0,
                        "speed_rpm": rpm,
                        "load": load,
                        "operating_condition": condition,
                        "failure": failure,
                    }
                )
                t = np.arange(1024, dtype=np.float64) / 25600.0
                signals[signal_id] = (
                    np.sin(2 * np.pi * (1200 + channel_index * 200) * t)
                    + 0.2 * np.sin(2 * np.pi * 150 * t)
                    + run_index * 0.03
                )
    (tmp_path / "manifest.json").write_text(json.dumps({"dataset": "xjtu_sy"}))
    fake_dataset = SimpleNamespace(
        path=tmp_path,
        metadata=lambda: pd.DataFrame(rows),
        signal=lambda signal_id: signals[signal_id],
        cite=lambda: "XJTU-SY citation",
    )
    fake_module = SimpleNamespace(
        __version__="test-version",
        open=lambda name, root=None: fake_dataset,
    )
    return fake_module


def test_xjtu_loader_pairs_axes_and_keeps_run_level_rul(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "bearing_datasets", _fake_xjtu(tmp_path))
    bundle, manifest, source = load_xjtu_rul_dataset(
        root=tmp_path,
        manifest_output=tmp_path / "source_manifest.csv",
        expected_signal_length=1024,
    )
    assert bundle.X.shape == (6, 2 * len(FEATURE_NAMES) + 2)
    assert set(bundle.groups) == {"Bearing1_1", "Bearing1_2", "Bearing2_1"}
    assert bundle.y_minutes.tolist() == [1.0, 0.0] * 3
    assert source["n_runs"] == 3
    assert source["n_snapshots"] == 6
    assert source["sample_rate_hz"] == 25600.0
    assert source["data_license"].startswith("unspecified")
    assert manifest.exists()
    frame = pd.read_csv(manifest)
    assert set(frame["horizontal_signal_id"].str.endswith("/horizontal")) == {True}
    assert set(frame["vertical_signal_id"].str.endswith("/vertical")) == {True}


def test_xjtu_rul_comparison_uses_bearing_and_condition_holdouts(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "bearing_datasets", _fake_xjtu(tmp_path))
    bundle, _, _ = load_xjtu_rul_dataset(
        root=tmp_path,
        manifest_output=tmp_path / "source_manifest.csv",
        expected_signal_length=1024,
    )
    result = compare_rul_models(bundle, bearing_folds=3, condition_folds=2)
    assert result["bearing_holdout"]["actual_folds"] == 3
    assert result["condition_holdout"]["actual_folds"] == 2
    assert set(result["bearing_holdout"]["models"]) == {
        "random_forest", "extra_trees", "hist_gradient_boosting", "ridge"
    }
    for split_name in ("bearing_holdout", "condition_holdout"):
        for model_result in result[split_name]["models"].values():
            assert model_result["mae_minutes"] >= 0
            assert model_result["rmse_minutes"] >= 0
