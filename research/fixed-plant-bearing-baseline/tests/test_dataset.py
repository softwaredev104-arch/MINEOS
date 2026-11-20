import csv
from pathlib import Path

import numpy as np
import pytest
from scipy.io import savemat

from mineos_bearing_baseline.dataset import load_dataset


def _write_recording(root: Path, name: str, label: str, group: str, frequency: float):
    t = np.arange(8192, dtype=np.float64)
    signal = np.sin(2 * np.pi * frequency * t) + 0.05 * np.sin(2 * np.pi * 0.31 * t)
    savemat(root / name, {"X_DE_time": signal.reshape(-1, 1), "X_RPM": np.array([[1797]])})
    return {"recording_id": name, "filename": name, "label": label, "sample_rate_hz": 12000, "group_id": group}


def test_manifest_loader_creates_windows_and_preserves_groups(tmp_path):
    rows = []
    rows.extend(_write_recording(tmp_path, f"normal_{i}.mat", "normal", f"normal_{i}", 0.04) for i in range(2))
    rows.extend(_write_recording(tmp_path, f"inner_{i}.mat", "inner_race", f"inner_{i}", 0.16) for i in range(2))
    with (tmp_path / "manifest.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    data = load_dataset(tmp_path, window_size=2048, stride=2048)
    assert data.X.shape == (16, 16)
    assert set(data.y) == {"normal", "inner_race"}
    assert len(set(data.groups)) == 4
    assert data.recording_ids.shape == data.y.shape


def test_path_traversal_is_rejected(tmp_path):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "recording_id,filename,label,sample_rate_hz,group_id\nr1,../outside.mat,normal,12000,g1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="inside dataset root"):
        load_dataset(tmp_path)


def test_unknown_label_is_rejected(tmp_path):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "recording_id,filename,label,sample_rate_hz,group_id\nr1,x.mat,broken,12000,g1\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unsupported label"):
        load_dataset(tmp_path)


def test_mixed_sample_rates_are_rejected(tmp_path):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(
        "recording_id,filename,label,sample_rate_hz,group_id\n"
        "normal_a,a.mat,normal,12000,g1\n"
        "normal_b,b.mat,normal,48000,g2\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="same sample_rate_hz"):
        load_dataset(tmp_path)
