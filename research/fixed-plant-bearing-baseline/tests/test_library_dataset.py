import json
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mineos_bearing_baseline.library_dataset import load_standardized_dataset


class FakeDataset:
    def __init__(self, rows, path):
        self._rows = rows
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / "manifest.json").write_text(json.dumps({"dataset": "cwru"}), encoding="utf-8")

    def metadata(self):
        return pd.DataFrame(self._rows)

    def signal(self, signal_id):
        t = np.arange(4096, dtype=np.float64)
        index = int(signal_id.split("/")[0].replace("rec", ""))
        return np.sin(2 * np.pi * (0.02 + (index % 5) * 0.01) * t)

    def cite(self):
        return "Synthetic fixture only"


def _install_fake(monkeypatch, rows):
    fake = types.SimpleNamespace(
        __version__="test",
        open=lambda name, root=None: FakeDataset(rows, Path(root) / name),
    )
    monkeypatch.setitem(sys.modules, "bearing_datasets", fake)


def _rows():
    rows = []
    for label, bearing in (
        ("normal", "healthy"),
        ("normal", "healthy"),
        ("inner", "DE_IR007"),
        ("inner", "DE_IR007"),
        ("outer", "DE_OR007"),
        ("outer", "DE_OR007"),
        ("rolling_element", "DE_B007"),
        ("rolling_element", "DE_B007"),
    ):
        index = len(rows)
        rows.append({
            "signal_id": f"rec{index}/DE",
            "recording_id": f"rec{index}",
            "channel": "DE",
            "fault_type": label,
            "bearing_id": bearing,
            "fs": 12000,
        })
    return rows


def test_standardized_bridge_builds_grouped_feature_bundle(tmp_path, monkeypatch):
    _install_fake(monkeypatch, _rows())
    bundle, manifest, source = load_standardized_dataset(
        root=tmp_path,
        manifest_output=tmp_path / "out" / "manifest.csv",
        window_size=2048,
        stride=2048,
    )
    assert bundle.X.shape == (16, 16)
    assert set(bundle.y) == {"normal", "inner_race", "outer_race", "ball"}
    assert bundle.sample_rate_hz == 12000
    assert len(set(bundle.groups[bundle.y == "normal"])) == 2
    assert len(set(bundle.groups[bundle.y == "inner_race"])) == 1
    assert manifest.is_file()
    assert source["dataset_library"] == "bearing-datasets"


def test_standardized_bridge_requires_explicit_sample_rate_for_mixed_rates(tmp_path, monkeypatch):
    rows = _rows()
    rows[-1]["fs"] = 48000
    _install_fake(monkeypatch, rows)
    with pytest.raises(ValueError, match="multiple sample rates"):
        load_standardized_dataset(
            root=tmp_path,
            manifest_output=tmp_path / "manifest.csv",
        )


def test_standardized_bridge_rejects_unknown_fault_types(tmp_path, monkeypatch):
    rows = _rows()
    rows[0]["fault_type"] = "misalignment"
    _install_fake(monkeypatch, rows)
    with pytest.raises(ValueError, match="Unsupported fault_type"):
        load_standardized_dataset(
            root=tmp_path,
            manifest_output=tmp_path / "manifest.csv",
        )
