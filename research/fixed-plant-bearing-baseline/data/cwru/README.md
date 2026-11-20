# CWRU local dataset folder

Place the original Case Western Reserve University (CWRU) MATLAB `.mat` recordings in this directory and create `manifest.csv` from `manifest.example.csv`.

The official Bearing Data Center page describes normal and seeded single-point bearing defects, drive-end/fan-end/base channels, and 12 kHz and 48 kHz recording rates: <https://engineering.case.edu/bearingdatacenter/download-data-file>.

**Do not commit the downloaded dataset files.** The download page documents the files and experiments but does not state a dataset licence. The CWRU data is not covered by this pilot's MIT code licence. Confirm the institution's current terms and obtain permission where required before commercial use or redistribution. Record the source citation, date accessed, selected files and authorization in your local dataset notes.

The sample manifest is illustrative. Set `sample_rate_hz` to the actual rate for each downloaded file; do not infer it from a filename. Set `group_id` to the independent acquisition unit you are holding out. Using one group per file prevents windows from the same recording appearing in both training and validation, but it does not prove generalization to unseen physical bearings unless the group IDs represent distinct bearings.
