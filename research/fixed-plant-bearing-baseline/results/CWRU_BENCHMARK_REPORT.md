# CWRU bearing baseline — automated research benchmark

**Status:** Research-only; not approved for mine-site or production use  
**Benchmark run:** GitHub Actions run [#87](https://github.com/softwaredev104-arch/MINEOS/actions/runs/44873866851)  
**Benchmark source commit:** `ef4da92ed1f6d27af7380532e52b11a31940feb0`  
**Dataset adapter:** `bearing-datasets 0.3.0`  
**Upstream dataset manifest SHA-256:** `037c50a5392080336a79a51e4726d82fcc78e9ecf480abb1e6a34baba3680e97`  
**Sensor:** Drive-end (DE)  
**Window duration:** 0.1706667 seconds for both sample-rate cohorts

## Data-integrity controls

- CWRU healthy recordings are available in the 48 kHz cohort; the 12 kHz cohort is fault-only.
- DE-channel experiments include DE-bearing faults only. The 12 kHz adapter excluded 45 fault recordings whose seeded defect was at the opposite (FE) bearing position; 48 kHz excluded 0.
- Fault recordings are grouped by the upstream `bearing_id`; healthy recordings use recording-level groups.
- The upstream CWRU builder states that same-bearing identity across loads is an assumption, not source-confirmed physical traceability.
- The source page does not state a data licence. The adapter/library code licence does not grant rights to CWRU data. Do not assume commercial-use or redistribution rights.
- Raw recordings were built only in an ephemeral hosted runner. They were not committed or uploaded as artifacts. Only metrics, model cards, feature schema, source manifest and comparison JSON were retained.

## Results

### 12 kHz — three-class fault-type classification

| Measure | Result |
|---|---:|
| Windows | 3,539 |
| Recordings | 60 |
| Independent groups | 11 |
| Groups per class | ball 4; inner race 4; outer race 3 |
| Grouped folds | 3 |
| Logistic regression accuracy | 0.3696 |
| Logistic regression macro-F1 | 0.3711 |

Per-class F1 for the logistic baseline:

| Class | F1 |
|---|---:|
| Ball / rolling element | 0.4339 |
| Inner race | 0.3973 |
| Outer race | 0.2823 |

CPU model comparison (same grouped folds):

| Model | Accuracy | Macro-F1 |
|---|---:|---:|
| Logistic regression | 0.3696 | 0.3711 |
| Random Forest | 0.3201 | 0.3135 |
| RBF SVM | 0.3371 | 0.3082 |
| Extra Trees | 0.2552 | 0.2250 |

Logistic regression is the strongest candidate in this cohort, but the class-wise results are too weak for operational diagnosis.

### 48 kHz — four-class classification

| Measure | Result |
|---|---:|
| Windows | 2,793 |
| Recordings | 56 |
| Independent groups | 13 |
| Groups per class | ball 3; inner race 3; normal 4; outer race 3 |
| Grouped folds | 3 |
| Logistic regression accuracy | 0.2696 |
| Logistic regression macro-F1 | 0.3702 |

CPU model comparison (same grouped folds):

| Model | Accuracy | Macro-F1 |
|---|---:|---:|
| Random Forest | 0.3677 | 0.4299 |
| Extra Trees | 0.2757 | 0.3792 |
| RBF SVM | 0.2764 | 0.3758 |
| Logistic regression | 0.2696 | 0.3702 |

Random Forest's per-class F1:

| Class | F1 |
|---|---:|
| Ball / rolling element | 0.2297 |
| Inner race | 0.0000 |
| Normal | 0.9880 |
| Outer race | 0.5017 |

The macro-F1 improvement is misleading if read alone: Random Forest completely misses the inner-race class in this grouped evaluation. It is not a suitable deployment candidate.

## Runtime validation

- ONNX Runtime CPU export completed for the logistic baseline in both cohorts.
- Native/ONNX label parity passed on 16 rows per cohort.
- ONNX parity confirms interface/runtime consistency only; it does not improve or validate classification quality.
- Unit tests passed on Python 3.10, 3.11 and 3.12 in the subsequent hosted CI run.

## Decision and next work

**Do not promote either classifier.** The 12 kHz task remains weak, and the 48 kHz result has an unacceptable inner-race blind spot despite a higher aggregate macro-F1 for Random Forest.

Next research work:
1. Evaluate the new Hilbert-envelope features against the original 16-feature baseline and retain the comparison report.
2. Add independent bearing datasets with their own licence/citation review; do not tune only against CWRU.
3. Keep RUL/run-to-failure prognostics as a separate model track (for example XJTU-SY), with its own data-rights review, temporal split and metrics.
4. Before any site trial, require sensor/asset metadata, field-confirmed maintenance labels, operating-condition coverage, false-alert budget and human review.

No model from this benchmark is site-validated.


## Reproducibility follow-up

The comparison implementation and its tests are committed in this feature branch. Hosted CI run #91 passed the branch test suite on Python 3.10, 3.11 and 3.12 after the comparison module was added to the branch. The next tagged benchmark run re-executes the full CWRU download/build/train/compare workflow against the branch's own source tree.
