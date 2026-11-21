"""Optional bridge to the MIT-licensed bearing-datasets acquisition/normalization library.

The library's code licence does not grant rights to the underlying datasets. Each
source retains its own terms; see the MineOS pilot README before building data.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np

from .dataset import DatasetBundle
from .features import FEATURE_NAMES, extract_features

FAULT_LABELS = {
    "normal": "normal",
    "inner": "inner_race",
    "outer": "outer_race",
    "rolling_element": "ball",
}


def load_standardized_dataset(
    *,
    root: str | Path,
    dataset_name: str = "cwru",
    channel: str = "DE",
    sample_rate_hz: float | None = None,
    window_size: int = 2048,
    stride: int = 2048,
    manifest_output: str | Path,
) -> tuple[DatasetBundle, Path, dict]:
    """Load one channel and one sample-rate cohort from a built bearing-datasets set.

    Faulty CWRU rows use the library's bearing_id to keep the four load recordings
    for an assumed physical damaged bearing together. Healthy CWRU rows use
    recording_id because the upstream builder assigns all healthy records the
    same generic bearing_id ("healthy"). The upstream builder documents that
    damaged-bearing identity across loads is an assumption, not a source-confirmed
    physical traceability fact; the output metadata records this grouping caveat.
    """
    if window_size < 16:
        raise ValueError("window_size must be at least 16 samples")
    if stride < 1 or stride > window_size:
        raise ValueError("stride must be between 1 and window_size")

    try:
        import bearing_datasets as bd
    except ImportError as exc:
        raise RuntimeError(
            "The optional bearing-datasets bridge is not installed. "
            "Install with: pip install -e '.[datasets]'"
        ) from exc

    root_path = Path(root).expanduser().resolve()
    ds = bd.open(dataset_name, root=root_path)
    metadata = ds.metadata()
    required = {"signal_id", "recording_id", "channel", "fault_type", "fs"}
    if dataset_name.lower() == "cwru" and channel.upper() in {"DE", "FE"}:
        required.add("fault_location")
    missing = required - set(metadata.columns)
    if missing:
        raise ValueError(f"Standardized dataset is missing metadata columns: {sorted(missing)}")

    selected = metadata[metadata["channel"].astype(str).str.upper() == channel.upper()].copy()
    if selected.empty:
        available = sorted(metadata["channel"].astype(str).unique().tolist())
        raise ValueError(f"No {channel.upper()} channel in {dataset_name}; available: {available}")

    unsupported_labels = sorted(
        set(selected["fault_type"].astype(str).str.strip().str.lower()) - set(FAULT_LABELS)
    )
    if unsupported_labels:
        raise ValueError(
            f"Unsupported fault_type values {unsupported_labels}; this baseline requires one of "
            f"{sorted(FAULT_LABELS)}"
        )

    rates = sorted({float(value) for value in selected["fs"].tolist()})
    if sample_rate_hz is not None:
        selected = selected[selected["fs"].astype(float) == float(sample_rate_hz)].copy()
        if selected.empty:
            raise ValueError(
                f"No {channel.upper()} recordings at {sample_rate_hz:g} Hz; available rates: {rates}"
            )
    else:
        if len(rates) != 1:
            raise ValueError(
                f"Dataset has multiple sample rates {rates}; choose one with --sample-rate"
            )
        sample_rate_hz = rates[0]

    # A CWRU recording may contain both DE and FE sensor channels while the seeded
    # defect exists at only one bearing position. Never transfer that fault label to
    # the opposite bearing sensor. The base-plate channel can observe either position.
    excluded_nonmatching_fault_location_signals = 0
    fault_location_filter = "all fault locations"
    if dataset_name.lower() == "cwru" and channel.upper() in {"DE", "FE"}:
        expected_location = {
            "DE": "motor_bearing_de",
            "FE": "motor_bearing_nde",
        }[channel.upper()]
        is_fault = selected["fault_type"].astype(str).str.lower() != "normal"
        matches_sensor = selected["fault_location"].astype(str).str.lower() == expected_location
        keep = ~is_fault | matches_sensor
        excluded_nonmatching_fault_location_signals = int((~keep).sum())
        selected = selected[keep].copy()
        fault_location_filter = expected_location
        if selected.empty:
            raise ValueError(
                f"No {channel.upper()} signals remain after matching faults to {expected_location}"
            )

    selected_rates = sorted({float(value) for value in selected["fs"].tolist()})
    if len(selected_rates) != 1:
        raise ValueError("One model run must use a single sample rate")
    cohort_rate = selected_rates[0]

    feature_rows: list[np.ndarray] = []
    labels: list[str] = []
    groups: list[str] = []
    recording_ids: list[str] = []
    manifest_rows: list[dict[str, str]] = []

    for _, row in selected.iterrows():
        raw_label = str(row["fault_type"]).strip().lower()
        if raw_label not in FAULT_LABELS:
            raise ValueError(
                f"Unsupported fault_type {raw_label!r}; this baseline requires one of "
                f"{sorted(FAULT_LABELS)}"
            )
        label = FAULT_LABELS[raw_label]
        recording_id = str(row["recording_id"])
        signal_id = str(row["signal_id"])
        bearing_id = str(row.get("bearing_id", "unknown"))
        if label != "normal" and bearing_id not in {"", "nan", "unknown", "none"}:
            group_id = f"bearing:{bearing_id}"
        else:
            group_id = f"recording:{recording_id}"

        signal = np.asarray(ds.signal(signal_id), dtype=np.float64).reshape(-1)
        if signal.size < window_size or not np.all(np.isfinite(signal)):
            raise ValueError(
                f"{signal_id}: signal is shorter than one window or contains non-finite values"
            )
        starts = range(0, signal.size - window_size + 1, stride)
        count = 0
        for start in starts:
            feature_rows.append(extract_features(signal[start : start + window_size]))
            labels.append(label)
            groups.append(group_id)
            recording_ids.append(recording_id)
            count += 1
        manifest_rows.append(
            {
                "recording_id": recording_id,
                "signal_id": signal_id,
                "channel": channel.upper(),
                "label": label,
                "fault_location": str(row.get("fault_location", "unknown")),
                "sample_rate_hz": f"{cohort_rate:g}",
                "group_id": group_id,
                "bearing_id_source": bearing_id,
                "windows": str(count),
            }
        )

    if not feature_rows:
        raise ValueError("Selected dataset cohort produced no signal windows")

    manifest_path = Path(manifest_output)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(manifest_rows[0])
    with manifest_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)

    upstream_manifest = Path(ds.path) / "manifest.json"
    upstream_manifest_sha256 = (
        hashlib.sha256(upstream_manifest.read_bytes()).hexdigest()
        if upstream_manifest.is_file() else None
    )
    source_info = {
        "upstream_manifest_sha256": upstream_manifest_sha256,
        "dataset_name": dataset_name,
        "dataset_citation": ds.cite() if hasattr(ds, "cite") else "Citation not supplied by loader",
        "dataset_library": "bearing-datasets",
        "dataset_library_version": getattr(bd, "__version__", "unknown"),
        "channel": channel.upper(),
        "sample_rate_hz": cohort_rate,
        "fault_location_filter": fault_location_filter,
        "excluded_nonmatching_fault_location_signals": excluded_nonmatching_fault_location_signals,
        "selected_signal_count": int(len(selected)),
        "grouping": (
            "faults grouped by upstream bearing_id; healthy records grouped by recording_id"
        ),
        "grouping_caveat": (
            "CWRU upstream metadata assumes the same damaged bearing was used across loads; "
            "the source does not confirm physical bearing traceability"
        ) if dataset_name.lower() == "cwru" else (
            "Use the source's physical bearing/run identifier where available"
        ),
        "raw_data_committed": False,
    }
    return (
        DatasetBundle(
            X=np.vstack(feature_rows).astype(np.float32),
            y=np.asarray(labels, dtype=str),
            groups=np.asarray(groups, dtype=str),
            recording_ids=np.asarray(recording_ids, dtype=str),
            feature_names=FEATURE_NAMES,
            sample_rate_hz=cohort_rate,
        ),
        manifest_path,
        source_info,
    )
