"""CWRU-style MATLAB recording ingestion with an explicit data manifest."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.io import loadmat

from .features import FEATURE_NAMES, extract_features

ALLOWED_LABELS = {"normal", "inner_race", "ball", "outer_race"}
REQUIRED_COLUMNS = {"recording_id", "filename", "label", "sample_rate_hz", "group_id"}


@dataclass(frozen=True)
class DatasetBundle:
    X: np.ndarray
    y: np.ndarray
    groups: np.ndarray
    recording_ids: np.ndarray
    feature_names: tuple[str, ...] = FEATURE_NAMES
    sample_rate_hz: float | None = None


def _read_manifest(root: Path) -> list[dict[str, str]]:
    manifest_path = root / "manifest.csv"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Required manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"manifest.csv is missing required columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError("manifest.csv contains no recording rows")

    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    group_labels: dict[str, str] = {}
    for line_number, row in enumerate(rows, start=2):
        recording_id = row["recording_id"].strip()
        filename = row["filename"].strip()
        label = row["label"].strip().lower()
        group_id = row["group_id"].strip()
        if not recording_id or not filename or not group_id:
            raise ValueError(f"manifest.csv line {line_number}: IDs and filename cannot be blank")
        if recording_id in seen_ids:
            raise ValueError(f"manifest.csv line {line_number}: duplicate recording_id {recording_id!r}")
        if filename in seen_files:
            raise ValueError(f"manifest.csv line {line_number}: duplicate filename {filename!r}")
        if label not in ALLOWED_LABELS:
            raise ValueError(
                f"manifest.csv line {line_number}: unsupported label {label!r}; "
                f"expected one of {sorted(ALLOWED_LABELS)}"
            )
        try:
            sample_rate = float(row["sample_rate_hz"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"manifest.csv line {line_number}: invalid sample_rate_hz") from exc
        if not np.isfinite(sample_rate) or sample_rate <= 0:
            raise ValueError(f"manifest.csv line {line_number}: sample_rate_hz must be positive")

        relative_path = Path(filename)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ValueError(f"manifest.csv line {line_number}: filename must stay inside dataset root")
        if relative_path.suffix.lower() != ".mat":
            raise ValueError(f"manifest.csv line {line_number}: expected a MATLAB .mat file")

        previous_label = group_labels.setdefault(group_id, label)
        if previous_label != label:
            raise ValueError(
                f"group_id {group_id!r} has multiple labels; use groups that represent one labelled unit"
            )
        seen_ids.add(recording_id)
        seen_files.add(filename)
    return rows


def _load_channel(path: Path, channel: str) -> np.ndarray:
    try:
        contents = loadmat(path)
    except NotImplementedError as exc:
        raise ValueError(
            f"{path.name} appears to use MATLAB v7.3/HDF5; convert it to a supported .mat file first"
        ) from exc
    suffix = f"_{channel.upper()}_time"
    keys = [key for key in contents if key.endswith(suffix)]
    if len(keys) != 1:
        raise ValueError(
            f"{path.name}: expected exactly one {channel.upper()} vibration channel ending in {suffix}; "
            f"found {keys}"
        )
    signal = np.asarray(contents[keys[0]], dtype=np.float64).reshape(-1)
    if signal.size == 0 or not np.all(np.isfinite(signal)):
        raise ValueError(f"{path.name}: selected vibration signal is empty or contains non-finite values")
    return signal


def load_dataset(
    root: str | Path,
    *,
    channel: str = "DE",
    window_size: int = 2048,
    stride: int = 2048,
) -> DatasetBundle:
    """Load full windows from manifest-listed MATLAB files.

    Group IDs are supplied by the dataset manifest and are used for grouped
    cross-validation. Never use a window-level random split for this data.
    """
    if channel.upper() not in {"DE", "FE", "BA"}:
        raise ValueError("channel must be one of DE, FE or BA")
    if window_size < 16:
        raise ValueError("window_size must be at least 16 samples")
    if stride < 1 or stride > window_size:
        raise ValueError("stride must be between 1 and window_size")

    root_path = Path(root).resolve()
    rows = _read_manifest(root_path)
    sample_rates = {float(row["sample_rate_hz"]) for row in rows}
    if len(sample_rates) != 1:
        raise ValueError(
            "All recordings in one baseline run must use the same sample_rate_hz; "
            "build separate cohorts for 12 kHz and 48 kHz recordings"
        )
    sample_rate_hz = next(iter(sample_rates))
    feature_rows: list[np.ndarray] = []
    labels: list[str] = []
    groups: list[str] = []
    recording_ids: list[str] = []
    for row in rows:
        file_path = (root_path / row["filename"].strip()).resolve()
        if root_path not in file_path.parents:
            raise ValueError(f"Recording path escapes dataset root: {row['filename']!r}")
        if not file_path.is_file():
            raise FileNotFoundError(f"Recording file not found: {file_path}")
        signal = _load_channel(file_path, channel)
        starts = range(0, signal.size - window_size + 1, stride)
        added = 0
        for start in starts:
            feature_rows.append(extract_features(signal[start : start + window_size], sample_rate_hz=sample_rate_hz))
            labels.append(row["label"].strip().lower())
            groups.append(row["group_id"].strip())
            recording_ids.append(row["recording_id"].strip())
            added += 1
        if added == 0:
            raise ValueError(
                f"{file_path.name}: signal has {signal.size} samples, shorter than window_size={window_size}"
            )
    return DatasetBundle(
        X=np.vstack(feature_rows).astype(np.float32),
        y=np.asarray(labels, dtype=str),
        groups=np.asarray(groups, dtype=str),
        recording_ids=np.asarray(recording_ids, dtype=str),
        sample_rate_hz=sample_rate_hz,
    )
