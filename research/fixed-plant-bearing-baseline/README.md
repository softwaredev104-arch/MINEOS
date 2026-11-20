# MineOS Fixed-Plant Bearing Baseline (Research Pilot)

**Status:** Initial reference implementation; research only, not site-validated.  
**Task:** Vibration-window classification into normal, inner-race, ball and outer-race bearing classes.  
**Initial data source:** Case Western Reserve University (CWRU) Bearing Data Center.

## Why this first pilot

Rotating equipment (motors, pumps, fans, gearboxes and crushers) often contains bearing fault signatures, making vibration-based bearing diagnosis a useful first reusable pipeline. CWRU provides documented laboratory recordings with normal bearings and seeded bearing faults. The official dataset describes drive-end, fan-end and base accelerometer channels and 12 kHz / 48 kHz acquisition rates.

**Important scope limit:** CWRU is a seeded-fault laboratory benchmark. This pilot is fault classification, not remaining-useful-life estimation or a mine-site predictive-maintenance model. It cannot establish field performance, natural-degradation forecasting or transfer to another asset/sensor configuration.

## Repository layout

- `src/mineos_bearing_baseline/features.py` — deterministic time/spectral feature extraction.
- `src/mineos_bearing_baseline/dataset.py` — explicit manifest and MATLAB `.mat` loader.
- `src/mineos_bearing_baseline/train.py` — group-aware cross-validation, CPU baseline, model card and optional ONNX export/parity check.
- `src/mineos_bearing_baseline/cli.py` — command-line entry point.
- `tests/` — generated-signal tests; no external bearing dataset is required to run them.
- `data/cwru/manifest.example.csv` — illustrative source manifest; the dataset itself is not stored here.

## Dataset rights and handling

The official download page is <https://engineering.case.edu/bearingdatacenter/download-data-file>. It describes the experiment and downloadable MATLAB files but does not state a data licence on that page. The MIT licence in this pilot applies to source code only, not to CWRU data. Confirm current data terms and authorization before commercial use or redistribution. Downloaded `.mat` files, caches and trained customer-data artifacts must not be committed.

## Setup

Python 3.10 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
pytest
```

For ONNX export and CPU Runtime smoke testing:

```bash
python -m pip install -e '.[test,onnx]'
```

## Prepare the dataset

1. Obtain the appropriate files from the official CWRU Bearing Data Center, subject to its terms.
2. Place the `.mat` files under `data/cwru/` (or another local directory outside source control).
3. Copy `data/cwru/manifest.example.csv` to `manifest.csv` and edit it to match the files actually obtained.
4. Use the correct `sample_rate_hz` for each file (the source includes both 12 kHz and 48 kHz data groups). One training run must use a single sampling rate; build separate 12 kHz and 48 kHz cohorts rather than mixing them.
5. Assign group IDs that reflect the independent acquisition unit intended for holdout. Do not claim unseen-bearing validation if the IDs are only filenames.
6. Confirm labels from the source's experiment documentation; do not rely on automatic filename guesses.

The manifest columns are:

| Column | Meaning |
|---|---|
| `recording_id` | Unique recording identifier |
| `filename` | `.mat` filename relative to the dataset directory |
| `label` | `normal`, `inner_race`, `ball` or `outer_race` |
| `sample_rate_hz` | Documented sample rate for that recording |
| `group_id` | Group kept together during cross-validation |

Each MATLAB file must contain exactly one selected channel key ending with `_DE_time`, `_FE_time` or `_BA_time` according to the channel selected at runtime. MATLAB v7.3/HDF5 files are not currently supported by this loader.

## Run the baseline

From this directory:

```bash
mineos-bearing-baseline train \
  --data-dir data/cwru \
  --out-dir artifacts/cwru-bearing-baseline \
  --channel DE \
  --window-size 2048 \
  --stride 2048 \
  --cv-folds 5
```

Add `--export-onnx` after installing the optional dependencies to export and compare ONNX Runtime CPU predictions against the native classifier.

The loader rejects malformed manifests and invalid signals. Cross-validation uses `StratifiedGroupKFold`; windows from a single declared group cannot cross training/validation boundaries. If there are too few independent groups per class, it stops rather than silently falling back to a random window split.

## Outputs

- `model.joblib` — fitted research model.
- `metrics.json` — out-of-fold classification metrics, group/fold counts and manifest hash.
- `feature_schema.json` — ordered feature interface.
- `model_card.md` — intended use, evaluation summary and limitations.
- `model.onnx` — optional ONNX artifact after parity smoke testing.

The metrics are out-of-fold predictions across groups, not independent mine-site validation. The final fitted model is trained on all supplied rows after grouped evaluation.

## Known constraints and next evaluation steps

- Statistical/spectral features are intentionally small and deterministic; they are a baseline, not a complete vibration diagnostic system.
- Sampling rate and source channel must be recorded accurately. Frequency features are expressed relative to Nyquist; the loader does not infer physical frequencies or RPM.
- The current grouping guarantees only the grouping semantics provided in `manifest.csv`.
- No failure horizon, natural degradation, maintenance label, causal explanation or RUL estimate is produced.
- A future generalization experiment should add an independently sourced run-to-failure dataset (for example, FEMTO/PRONOSTIA or XJTU-SY) after its original data licence and citation have been checked.
- Before any site pilot, agree data rights, asset mapping, sensor placement, operating envelope, maintenance verification, false-alert budget, lead-time expectations and human review with the customer.

This package is not an OT connector and has no interfaces that write to PLC, SCADA, DCS or SIS systems.
