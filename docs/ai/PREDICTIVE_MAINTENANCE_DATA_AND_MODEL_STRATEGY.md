# MineOS Predictive Maintenance Data and Model Strategy

**Status:** Proposed research and engineering baseline — not a production-validated model specification  
**Date:** 20 November 2026  
**Related documents:** [MineOS AI Architecture](../architecture/MINEOS_AI_ARCHITECTURE.md), [Industrial Connector Architecture](../architecture/INDUSTRIAL_CONNECTOR_ARCHITECTURE.md), [Industrial Vendor and API Research Register](../integrations/INDUSTRIAL_VENDOR_API_REGISTRY.md)

## 1. Purpose and scope

MineOS Predictive Maintenance (PDM) will estimate equipment health, detect abnormal behavior, support fault diagnosis, forecast failure risk and, where data supports it, estimate remaining useful life (RUL).

MineOS must support two related but distinct data tracks:

1. **Fixed plant:** crushers, mills, conveyors, gearboxes, bearings, motors, pumps, compressors, fans and other stationary process assets.
2. **Mobile fleet:** haul trucks, loaders, excavators, drills, dozers and underground equipment.

The tracks may share asset, maintenance and model-governance services, but they must not be forced into a single feature schema or model. Their measurement rates, operating context, failure mechanisms and available telemetry differ.

PDM is an advisory intelligence capability. It does not replace condition-monitoring instruments, OEM diagnostic systems, maintenance engineering judgement, statutory inspections, protective relays, PLC/DCS control or SIS functions.

## 2. Data sources required

Reliable PDM combines condition, operating context and maintenance outcomes.

| Data group | Examples | Typical source |
|---|---|---|
| Condition measurements | Vibration waveform, RMS, velocity, acceleration, spectral features, bearing temperature, oil debris, acoustic/ultrasound, motor current, pressure | Condition-monitoring sensors, vibration analyzers, motor protection devices, SCADA, specialist platforms |
| Operating context | RPM, torque, load, power, temperature, pressure, flow, throughput, feed type, operating mode, start/stop, speed, duty cycle | PLC/SCADA/DCS, historian, process instruments |
| Utilization / fleet context | Engine hours, idle time, fuel use, payload, cycle/load count, distance, location, travel state | OEM telematics, AEMP 2.0 / ISO 15143-3, fleet management |
| Maintenance outcomes | Work order, inspection, symptom, failure code, component, repair action, parts replaced, downtime, return-to-service time, technician findings | CMMS/EAM, maintenance logs, reliability systems |
| Environmental context | Ambient temperature, dust, humidity, water ingress, altitude, mine/plant conditions | Site sensors and authorized environmental systems |
| Engineering context | OEM limits, asset criticality, component hierarchy, expected duty, lubrication specification, maintenance strategy | Asset register, engineering documents and OEM information |

### Data availability and model suitability

- Low-frequency fleet telemetry such as operating hours, idle time and fuel use is useful for utilization, exposure, maintenance intervals and some failure-risk context. It does not replace high-frequency condition data for bearing or gearbox diagnosis.
- Vibration fault diagnosis may require waveform data at a much higher sampling rate than ordinary SCADA trends. Some PdM services accept processed condition indicators rather than raw waveform data.
- A source API may return only selected tags or an OEM-defined snapshot. The connector must verify sampling frequency, query limits, field availability, historical retention and missing-data semantics.
- Work orders without accurate asset IDs, dates, failure modes and completed-work details are weak learning labels.
- Equipment operating states matter. A measurement during startup, shutdown, idle, maintenance or an abnormal operating mode may not be comparable with steady operation.

## 3. Canonical PDM data contracts

### 3.1 Time-series measurement

Each measurement used for PDM should retain:

- Tenant, site, facility, process area and canonical asset ID.
- Original source system, source asset ID and source point/tag/node.
- Measurement concept, value, data type and original engineering unit.
- Event timestamp, ingestion timestamp and source timezone where supplied.
- Sample interval or aggregation period, and whether the value is raw, sampled, averaged, minimum, maximum or otherwise derived.
- Source quality, MineOS quality and freshness state.
- Operating mode/state and relevant process context when available.
- Connector ID/version, source schema/API version and lineage.
- Calibration or sensor status when the source exposes it.

A derived feature must identify its source window, calculation/version, units and data-quality exclusions.

### 3.2 Maintenance / work event

Where available, capture:

- Source work-order/event ID and canonical asset/component ID.
- Event type: inspection, planned work, corrective repair, breakdown, replacement, lubrication, adjustment, overhaul or other mapped activity.
- Reported symptom and observed condition.
- Failure mode, failure mechanism and component affected.
- Failure start/detection time, work start/end and return-to-service time, with timezone context.
- Corrective/preventive action and component/part replaced.
- Downtime and production impact, if measured.
- Work status, verification status and source record provenance.
- Human-confirmed vs inferred fields, including confidence and reviewer where applicable.

Do not infer that a machine failed just because it was stopped or a work order was opened. Distinguish planned maintenance, operator stop, process interruption, safety trip, equipment failure and data outage.

### 3.3 Asset and component identity

PDM needs a stable equipment/component hierarchy. A pump, its motor, coupling, gearbox and bearings may need separate asset or component identities and explicit parent/child and functional relationships.

Vendor tag names and OEM serial numbers are source identifiers, not canonical MineOS IDs. Maintain explicit mappings and effective-dated identity changes. Never join a maintenance event to a sensor stream based on a similar display name alone.

## 4. Data preparation and quality controls

Before feature generation or inference:

1. Validate source identity, timestamp, unit, type and quality.
2. Normalize time to a consistent internal representation while retaining source timezone context.
3. Detect duplicates, gaps, late data, clock drift and out-of-order events.
4. Apply documented unit conversions; preserve the original value/unit.
5. Separate raw waveforms, high-frequency features, ordinary process trends and low-frequency fleet telemetry.
6. Align measurements to operating state and duty cycle where possible.
7. Identify startup, shutdown, idle, maintenance, trip and steady-state windows.
8. Check sensor health, calibration, clipping, flatline, impossible values and changes in sensor placement.
9. Mark imputed, interpolated, resampled and aggregated values explicitly.
10. Record the data-quality exclusions used for every feature and prediction.

Missing or stale measurements must not silently become zero. A model should abstain or reduce its confidence where the required inputs are absent, stale, invalid or outside the training/validated operating envelope.

## 5. Model family strategy

MineOS should maintain a model family rather than one universal predictive-maintenance model.

| Capability | Candidate approaches | Expected output |
|---|---|---|
| Engineering/rule monitoring | OEM/engineering limits, deterministic rules, process constraints | Threshold breach, limit deviation and evidence |
| Statistical condition monitoring | Trend limits, control charts, robust statistics, change-point detection | Degradation trend or unusual operating shift |
| Anomaly detection | Isolation Forest, robust covariance, one-class methods, autoencoders where justified | Anomaly score and contributing measurements |
| Fault classification | Gradient-boosted trees, random forests, calibrated classifiers, selected deep models | Ranked fault hypotheses with evidence and uncertainty |
| Failure-risk forecasting | Survival analysis, calibrated classification and time-dependent hazard models | Risk over a specified future horizon |
| Remaining useful life | Survival / degradation models, regression, sequence models where supported | RUL distribution or interval, assumptions and uncertainty |
| Root-cause assistance | Event correlation, process topology, rules and evidence-grounded language models | Candidate contributing factors, never an unverified confirmed cause |

Start with transparent engineering rules and classical statistical / tree-based baselines. Use deep sequence models only when data volume, sampling, label quality and cross-asset validation justify the extra complexity.

A model can be described as physics-informed only when engineering constraints or process relationships are explicitly represented and tested.

## 6. Separate fixed-plant and mobile-fleet modeling

### Fixed plant

Potential equipment groups:
- Rotating equipment: motors, pumps, fans, compressors, gearboxes and bearings.
- Material handling: conveyors, pulleys, idlers, crushers and feeders.
- Comminution and processing: mills, screens, flotation and separation equipment.
- Electrical assets: transformers, switchgear and motors where approved electrical-condition data exists.

Potential measurements include vibration, bearing temperature, current, power, pressure, flow, speed, torque, lubrication indicators and process load.

High-frequency vibration should be processed at an appropriate edge or condition-monitoring layer when raw data volume, network policy or vendor design makes continuous central ingestion impractical. MineOS should retain provenance for both the raw source and derived condition indicators.

### Mobile fleet

Potential equipment groups:
- Haul trucks and articulated trucks.
- Loaders, LHDs and excavators.
- Drills, bolters and underground production equipment.
- Dozers, graders and support vehicles.

Potential inputs include operating/idle hours, fuel, payload, cycle counts, engine/drive temperatures, pressure, fault codes, location, duty cycle and OEM condition indicators.

AEMP 2.0 / ISO 15143-3 is useful for compatible fleet telemetry, but it is not a raw CANbus/J1939 feed and does not guarantee access to every machine signal. When higher-resolution fault data is needed, use an OEM-approved diagnostic, gateway or customer-approved equipment interface.

## 7. Training datasets and research strategy

Public data can validate the ML pipeline and compare methods, but it cannot establish mine-site accuracy by itself.

| Dataset | Relevant use | Limitation |
|---|---|---|
| **NASA C-MAPSS / Prognostics Data Repository** | Degradation forecasting and RUL research | Simulated turbofan engine trajectories; not mining equipment or direct evidence of mine performance. |
| **UCI AI4I 2020 Predictive Maintenance** | Baseline classification, feature pipeline and repeatable CI tests | Synthetic manufacturing dataset; not real operational mining data. |
| **PHM Society public datasets** | Machinery degradation and fault-diagnosis experiments, depending on challenge/dataset | Rig, sensor and failure distribution may not represent a mine; dataset-specific licensing and provenance must be checked. |
| **Case Western Reserve University Bearing Data Center** | Bearing fault signal processing and classification | Laboratory bearing faults and test conditions; not proof of field generalization. |
| **FEMTO / PRONOSTIA bearing dataset** | Bearing degradation and RUL experiments | Accelerated test-rig conditions differ from real operating duty and maintenance practice. |

Useful starting points:
- [NASA Prognostics Data Repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/)
- [UCI AI4I 2020 dataset](https://archive.ics.uci.edu/dataset/601/ai4i)
- [PHM Society public datasets](https://phmsociety.org/public-data-sets/)
- [Case Western Reserve Bearing Data Center](https://engineering.case.edu/bearingdatacenter)
- [FEMTO / PRONOSTIA dataset information](https://www.femto-st.fr/en/Research-departments/AS2M/Research-groups/PHM)

Research rules:
- Record dataset owner, source URL, version, licence, intended use, signal schema and known limitations.
- Separate real, simulated, synthetic and augmented examples.
- Keep synthetic labels and simulated operating profiles identifiable in dataset lineage.
- Never claim a model is validated for mines solely because it performs well on a public benchmark.
- Use public data for reproducible method research, unit tests, baseline comparisons and pretraining experiments where legally permitted.
- Customer data is used only under the relevant customer agreement and data policy.

## 8. Evaluation and validation

Randomly splitting individual time-series rows can leak information from the same equipment or operating period into both training and test sets. Use leakage-aware evaluation.

### Required evaluation design
- **Temporal holdout:** train on earlier periods and evaluate on later unseen periods.
- **Asset holdout:** evaluate generalization to assets not used for training where the intended deployment requires it.
- **Site holdout:** where data volume permits, evaluate transfer to a different site or process environment.
- **Prospective shadow evaluation:** run predictions without influencing work decisions, then compare with verified outcomes over a defined period.
- **Operating-envelope assessment:** report which equipment types, duty conditions, sensor configurations and data-quality conditions are represented.

### Metrics

| Model task | Metrics and operational measures |
|---|---|
| Fault classification | Precision, recall, class-wise F1, confusion matrix, PR-AUC for imbalanced failures, calibration |
| Anomaly detection | Precision / review yield at an agreed alert budget, false alerts per asset-month, detection lead time and missed-event review |
| Failure-risk forecasting | Horizon-specific precision/recall, calibration, Brier score where appropriate, lead-time distribution, false alerts and missed failures |
| RUL | MAE / median absolute error, prediction-interval coverage, error by remaining-life horizon, prognostic horizon and censoring-aware analysis |
| Operational usefulness | Verified actionable alerts, maintenance review burden, avoidable downtime evidence, lead time, recommendation acceptance and outcome quality |

No single metric is sufficient. Alert thresholds must account for maintenance capacity, asset criticality, cost of false alarms, consequence of missed failures and the availability of confirmatory inspections.

### Production promotion gates

A model may be promoted only after:
- Its intended asset classes and use are defined.
- Training-data lineage, permissions and quality exclusions are recorded.
- Baselines and acceptance metrics are approved.
- Temporal and relevant asset/site holdouts are completed.
- Uncertainty and calibration are evaluated.
- Failure modes, false-alert burden and abstention behavior are reviewed with domain experts.
- A shadow or controlled pilot meets the agreed acceptance criteria.
- An owner, monitoring plan, rollback path and retraining policy are assigned.

## 9. Prediction and maintenance feedback lifecycle

~~~text
Authorized source telemetry + asset context + maintenance history
                              |
                     Data quality validation
                              |
                 Time alignment and feature windows
                              |
             Rules / statistical checks / model inference
                              |
          Risk or anomaly + horizon + uncertainty + evidence
                              |
                Separate recommendation record
                              |
                Human reliability / maintenance review
                              |
               Customer maintenance system / work order
                              |
               Completed work and verified outcome
                              |
               Evaluation and governed model update
~~~

The prediction, recommendation, approval, work order, executed repair and verified outcome are distinct records.

A maintenance action is not proof a prediction was correct. The feedback record must capture whether inspection confirmed the suspected fault, what was actually found, whether a component was replaced, whether the alert was unrelated, and whether no fault was found.

MineOS may integrate completed work from Maximo, SAP, Infor or a customer's maintenance system. It must not assume every work order is a failure label or automatically treat every work-order closure as verified ground truth.

## 10. PDM prediction record

A versioned prediction should include at least:

- Tenant/site/facility/asset/component identity.
- Prediction ID, creation timestamp and evaluation window.
- Task type: anomaly, fault classification, risk forecast, RUL or other declared output.
- Model ID, model version, feature-set version and connector/source lineage.
- Input time window, operating mode and data-quality summary.
- Risk horizon or RUL unit where applicable.
- Score, calibrated probability where justified, uncertainty/interval and abstention state.
- Evidence: measurements, trends, events and contextual inputs that contributed.
- Intended use, excluded conditions and known model limitations.
- Human review and recommendation references as separate records.

Do not emit a precise failure date unless the model and evidence support that level of precision. Prefer a calibrated interval or risk horizon and state assumptions.

## 11. Model operations and governance

- Maintain model registry, signed/versioned artifacts, feature definitions and reproducible training code.
- Track training dataset versions, data permissions, source lineage and label provenance.
- Monitor missingness, feature drift, operating-envelope shifts, calibration and verified outcomes.
- Alert when input distributions or source schemas change.
- Do not automatically retrain or promote a production model from unreviewed feedback.
- Maintain rollback to a previously approved model and a safe rules-based fallback where appropriate.
- Keep customer data, feature stores, caches, embeddings, model evaluation and logs tenant-isolated.
- Do not use customer data to train shared models by default. Require explicit authorization and contractual governance for any secondary use.
- Allow on-premises or customer-controlled edge inference where required by OT policy, latency, availability or data-residency constraints.

## 12. Initial research and implementation sequence

1. Select representative fixed-plant and mobile-fleet asset classes for research; do not attempt every equipment type at once.
2. Obtain public datasets and build reproducible ingestion, data-quality and evaluation pipelines.
3. Implement canonical time-series and maintenance-event contracts.
4. Build rule/statistical and tree-based baselines before testing deep time-series models.
5. Create deterministic simulated equipment streams and controlled fault scenarios for connector and workflow testing.
6. Connect one simulator and one approved industrial source through the connector contract.
7. Add work-order and completed-maintenance feedback from an approved CMMS/EAM source.
8. Run offline evaluation, then prospective shadow validation on authorized site data.
9. Promote only use cases whose evidence and operational acceptance criteria are met.

## 13. Explicit exclusions

- No autonomous control of real equipment or modification of PLC/DCS/SIS logic.
- No bypassing alarms, trips, interlocks or protective functions.
- No declaration of confirmed failure based only on an anomaly score.
- No claims of mine-wide failure prediction from generic public datasets.
- No RUL output where there is insufficient degradation history, failure/censoring evidence or a valid operating envelope.
- No shared-model training on customer data without explicit authorization.
- No automatic work-order creation or maintenance execution without a separately approved workflow and customer permissions.

## 14. Initial fixed-plant bearing reference pilot

A research-only reference implementation now exists at [research/fixed-plant-bearing-baseline](../../research/fixed-plant-bearing-baseline/README.md). It provides a MATLAB vibration loader, deterministic time/spectral features, a class-balanced logistic-regression baseline, grouped cross-validation, model-card/metrics output and optional ONNX export with ONNX Runtime CPU label-parity checking.

The first task is **bearing fault classification** (normal, inner race, rolling element/ball and outer race), not failure-risk forecasting or remaining-useful-life estimation. The initial public source under evaluation is the CWRU Bearing Data Center. Its files are not included in the repository; the official download page does not state a dataset licence, so verify current terms and obtain permission where necessary before commercial use or redistribution. The source describes laboratory recordings with seeded defects and 12 kHz / 48 kHz acquisition rates. These data are useful for an initial diagnostic pipeline exercise but do not validate MineOS for mine-site operating conditions.

The pilot uses synthetic MATLAB recordings in its automated tests so the code path can be verified without redistributing external data. It uses StratifiedGroupKFold over manifest-provided group IDs and fails when fewer than two independent groups per class are available. Its validation claim is only as strong as the supplied grouping; filename-level groups do not establish unseen-bearing generalization.

This CWRU classifier pilot does not implement a customer connector, real-site model, production inference endpoint or operational recommendation workflow. A separate XJTU-SY run-to-failure RUL research track is now implemented below; it is a distinct task and is not evidence of mine-site predictive capability. All classifier and RUL artifacts remain research outputs until model-specific MineOS release gates and customer/domain approvals are met.


## 15. Reproducible bearing dataset acquisition bridge

The fixed-plant bearing pilot now supports the MIT-licensed [BearingDatasets](https://github.com/VictorBauler/BearingDatasets) project as an optional dataset acquisition and standardized Parquet layer. Reuse this maintained loader rather than implementing another general-purpose downloader or Parquet format. Its MIT licence covers the library code only; each underlying dataset retains its own terms.

For CWRU, the upstream metadata explicitly labels the data licence as unspecified. Treat commercial use and redistribution as unconfirmed until the source owner confirms the terms. Do not put raw datasets, derived customer data or trained artifacts in Git.

The MineOS adapter selects one channel and one sample-rate cohort, reads signals one at a time, creates the existing deterministic feature windows, writes a local source manifest, and records the upstream dataset manifest hash and citation in metrics. CWRU DE 12 kHz and 48 kHz runs must be trained separately. Fault recordings are grouped by the upstream `bearing_id`; this reflects the upstream builder's stated assumption that the same damaged bearing was used across loads, not source-confirmed physical traceability. Healthy records are grouped by recording ID.

Install and build locally:

```bash
python -m pip install -e '.[datasets]'
bearing-datasets build cwru --root /data/bearing-datasets
mineos-bearing-baseline train-library --data-root /data/bearing-datasets --dataset cwru --channel DE --sample-rate 12000 --out-dir artifacts/cwru-de-12k
mineos-bearing-baseline train-library --data-root /data/bearing-datasets --dataset cwru --channel DE --sample-rate 48000 --out-dir artifacts/cwru-de-48k
```

The hosted CI workflow has now built CWRU in an ephemeral runner and completed two real-data cohorts, with sensor-position label filtering, grouped validation, four CPU model comparisons and ONNX parity checks. See [CWRU benchmark report](../../research/fixed-plant-bearing-baseline/results/CWRU_BENCHMARK_REPORT.md). The measured performance is weak and one model misses the inner-race class entirely; neither cohort is approved for deployment. CWRU's data licence remains unspecified, so commercial rights are unconfirmed. Synthetic tests continue to validate adapter behavior separately.


### CWRU channel/defect-position label integrity

For CWRU, a recording can contain DE, FE and base channels while the seeded defect is located at only one bearing position. The MineOS adapter must not copy a recording-level fault label onto a sensor mounted at the opposite bearing. DE-channel experiments retain only DE-bearing faults, FE-channel experiments retain only FE-bearing faults, and the base-plate channel may retain either position. The selected fault-location filter and excluded signal count are written into source provenance. This is a dataset-label integrity requirement, not an optional model-tuning choice.

The hosted research benchmark downloads/builds CWRU only in an ephemeral runner, trains separate sample-rate/channel cohorts, validates ONNX Runtime CPU label parity, and retains metrics/model cards/source manifests only. Raw recordings are not uploaded as CI artifacts or committed to Git. Dataset licence terms remain separate from the MIT-licensed adapter/library code.


### CPU model comparison and physical window consistency

The bearing research pilot includes a grouped comparison of Logistic Regression, Extra Trees, Random Forest and RBF SVM. Candidate models must use identical StratifiedGroupKFold partitions and be compared using per-class precision, recall and F1, not accuracy alone. For the CWRU sample-rate experiments, use approximately equal physical windows (2048 samples at 12 kHz and 8192 samples at 48 kHz, approximately 0.171 seconds each). The 12 kHz fault-only task and 48 kHz four-class task remain different label sets and their scores must not be compared as if they were one task. Model selection remains a research decision; no candidate is automatically promoted.


### Envelope-spectrum feature experiment

The bearing pilot's feature interface now includes Hilbert-envelope demodulation, envelope RMS/kurtosis, dominant/centroid envelope frequencies and physical-Hz envelope energy bands (0–50, 50–100, 100–200, 200–400, 400–800, 800–1600 and above 1600 Hz). The actual documented sample rate is passed into feature extraction and stored with window duration; it must never be inferred. These features are an experimental diagnostic baseline and must be evaluated with the same asset/group holdout rules as the original feature set.


## XJTU-SY run-to-failure RUL track

The XJTU-SY prognostics task is separate from CWRU seeded-fault classification. It contains 15 complete accelerated bearing runs across three operating conditions; each snapshot contains 32,768 samples per axis at 25.6 kHz (1.28 seconds), collected once per minute. The standardized metadata provides `run_id`, `time_s`, `rul_s`, speed, load, operating condition and terminal failure description.

The loader pairs horizontal and vertical channels for each snapshot, computes the same sample-rate-aware vibration feature family per axis, adds known speed/load metadata, and converts `rul_s` to minutes. Terminal failure type is provenance only; it is not an input feature. Validation has two separate holdout views: complete `run_id` bearings and complete operating conditions. Models are compared using MAE/RMSE in minutes, R² and per-bearing MAE. Random snapshot splitting is prohibited.

The XJTU-SY dataset metadata marks its licence as unspecified. The authors state it is publicly available for prognostics validation and request citation of the 2020 paper, but commercial-use and redistribution rights remain unconfirmed. The hosted workflow uses an ephemeral runner, deletes the cached source archives after building, and uploads only metrics, a model card and a source manifest. It never uploads raw vibration signals.
