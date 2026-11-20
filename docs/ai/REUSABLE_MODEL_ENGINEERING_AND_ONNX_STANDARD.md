# MineOS Reusable Model Engineering and ONNX Standard

**Status:** Proposed engineering standard — implementation gates must be completed per model  
**Scope:** Shared MineOS AI engineering practices for fixed plant, mobile fleet, process analytics and future industrial domains  
**Related documents:** [MineOS AI Architecture](../architecture/MINEOS_AI_ARCHITECTURE.md), [Predictive Maintenance Data and Model Strategy](PREDICTIVE_MAINTENANCE_DATA_AND_MODEL_STRATEGY.md), [Industrial Connector Architecture](../architecture/INDUSTRIAL_CONNECTOR_ARCHITECTURE.md), [Safety, Security and AI Governance](../governance/SAFETY_SECURITY_AI_GOVERNANCE.md)

## 1. Purpose

This standard adopts a reusable, CPU-first model-engineering approach for MineOS. It is intended to reduce duplicated research and implementation across use cases while keeping each model specific to its asset class, task, data contract and validated operating envelope.

The standard covers the full path from a governed source dataset to a versioned model artifact, validated inference, monitoring and controlled promotion. It does not prescribe one universal model, one mandatory framework, or one deployment topology.

**Reuse before rebuild.** Before implementing an algorithm or connector, check whether a maintained open-source project, an existing MineOS capability, a customer-deployed EHS/PdM platform, an OEM diagnostic service, or a documented vendor interface already provides the required function. Integrate and contextualize an existing capability when that is more reliable than recreating it.

MineOS remains an intelligence and integration layer. It does not replace PLC, SCADA, DCS, SIS, historians, CMMS/EAM or OEM systems. Existing systems remain authoritative for their source records and safety/control functions.

## 2. Engineering principles

1. **Start with a measurable baseline.** Establish engineering rules, deterministic calculations, robust statistics or a simple classical ML model before considering a complex neural network.
2. **Choose the smallest adequate model.** Model complexity must be justified by better validated performance or a necessary capability, not novelty.
3. **Design for CPU first.** Every proposed use case must have a credible CPU inference path. GPU use is optional and must have a measured business and operational justification.
4. **Separate research from runtime.** Notebooks and hosted notebooks are for exploration. Production training and inference logic must be reproducible, tested code with explicit inputs and outputs.
5. **Keep domain contracts independent of vendors.** Normalize data through industrial connector and canonical data contracts before feature engineering. A model must not depend directly on a vendor's tag naming or proprietary payload shape.
6. **Preserve customer and tenant boundaries.** Authorization applies to data retrieval, feature computation, training, model evaluation, inference, logs, caches and output delivery.
7. **Make every result traceable.** A prediction must be linked to model, artifact, feature set, source lineage, time window, operating context and evaluation status.
8. **Permit abstention.** Missing, stale, invalid or out-of-envelope inputs must produce an explicit degraded/abstain response rather than a confident-looking guess.
9. **Keep humans and existing control systems in authority.** Predictions and recommendations do not approve or execute maintenance or equipment actions.
10. **Optimize only after measurement.** Record quality, latency, memory and artifact size before applying quantization, pruning, distillation or other complexity.

## 3. MineOS model-engineering flow

```text
Customer-approved sources and existing industrial applications
                           |
              Replaceable source connectors
                           |
         Source envelope + identity + provenance
                           |
       Validation / canonical context / data quality
                           |
       Versioned feature definitions and feature sets
                           |
        Rules / statistics / ML model candidates
                           |
       Evaluation, calibration and domain review
                           |
        Versioned model package and registry entry
                           |
      Framework inference or validated ONNX Runtime
                           |
 Prediction + uncertainty + evidence + abstention state
                           |
     Separate recommendation and human review workflow
                           |
    Customer maintenance / operational system action
                           |
       Verified outcome and governed evaluation loop
```

This flow is logical rather than a requirement to deploy every stage as a separate microservice. A first implementation may be a tested Python package or an in-process CPU inference component. Introduce a separate service, edge runtime or queue only when isolation, deployment, scaling, latency or OT boundary requirements justify it.

### Responsibilities by layer

- **Connectors:** acquire only authorized source data; preserve source IDs, timestamps, units, quality and connector/API version. Use the connector's declared and tested capabilities.
- **Canonicalization:** map source identifiers to MineOS tenant/site/facility/asset/component identities and preserve original source values and lineage.
- **Feature pipeline:** apply versioned transformations, time windows, unit conversions, operating-state filters and data-quality exclusions.
- **Model selection:** compare candidate methods against the same leakage-safe baseline and holdout design.
- **Inference:** load an approved immutable artifact, validate its input contract, execute within the declared operating envelope and return a typed result.
- **Governance:** approve model promotion, monitor operating performance and drift, and preserve a rollback path.
- **Feedback:** capture inspections and completed work as separate outcome records; do not treat a recommendation or work-order closure alone as proof of a failure.

## 4. Reuse-first open-source tool strategy

The following are candidate components, not a mandatory dependency bundle. Select the smallest set needed for the use case and verify repository activity, supported Python/runtime versions, transitive dependencies, upstream licence, model/weight licence and security posture at the time of adoption.

| Engineering need | Candidate projects | MineOS use |
|---|---|---|
| Core numerical work | NumPy, SciPy, pandas, Polars | Tabular, signal and numerical transformations |
| Queryable local research data | DuckDB | Reproducible analysis of Parquet/CSV extracts without standing database infrastructure |
| Classical ML | scikit-learn, LightGBM, XGBoost, CatBoost | Transparent baselines, classification, regression and risk models |
| Anomaly detection | PyOD and suitable scikit-learn estimators | Compare robust statistical and classical anomaly methods |
| Time-series exploration | Darts, Merlion, Kats or task-specific signal libraries | Evaluate forecasting and condition-monitoring methods; use only where maintained and compatible |
| Graph features | NetworkX; PyTorch Geometric or DGL only when justified | Process/asset topology, event relationships and, later, graph ML |
| Optimisation / experiments | Optuna | Controlled parameter search after a baseline is established |
| Model interchange / runtime | ONNX, ONNX Runtime | Portable inference artifacts and CPU execution where export is supported |
| Experiment / dataset tracking | MLflow, DVC | Record experiments, artifact lineage and large dataset versions when useful |
| Data contracts / validation | Pandera and explicit schema tests | Validate feature tables, units, nullability and expected ranges |
| Explainability | SHAP or other task-appropriate methods | Supporting evidence for review; explanations must not be presented as causal proof |
| Text / semantic retrieval | Sentence Transformers and FAISS or hnswlib | Optional document/event retrieval; enforce tenant-scoped indexes and source permissions |

Avoid installing all candidates at once. Use a project-local dependency decision record showing why a package is needed, its exact version, licence, known vulnerabilities, optional dependencies and whether it is required at training time, runtime or both.

### Licence and model-weight policy

- Prefer permissive upstream licences such as MIT, Apache-2.0 and BSD-family licences where feasible.
- Review GPL, AGPL, LGPL, SSPL, Business Source License, source-available, custom and unclear terms before inclusion. Escalate any uncertainty rather than treating a repository as permissively licensed.
- Check the licence of pretrained weights, datasets, tokenizer files, sample data and bundled binaries separately from the source-code repository.
- A permissively licensed code library does not make its downloaded model weights, training dataset or third-party API rights permissive.
- Record the licence URL and review date in the dependency/model register. Recheck at upgrades and before customer distribution.

## 5. Model selection and training workflow

Every model project must complete these stages, even where a stage is intentionally marked not applicable.

### Stage A — define the task

Specify:
- Business/engineering question and intended decision support.
- Prediction subject: asset, component, process unit, fleet item or event.
- Task type: rule breach, anomaly, classification, horizon-specific failure risk, forecast, RUL, ranking or text extraction.
- Prediction horizon and units, where applicable.
- Required inputs, source frequency, history depth and expected freshness.
- Operating conditions and asset classes included and excluded.
- Consequence of false positives, false negatives and abstention.
- Intended user, reviewer and prohibited use.

Do not collapse anomaly detection, fault classification, failure-risk forecasting and RUL into one interchangeable output. Their labels, assumptions and metrics differ.

### Stage B — prove data readiness

- Confirm lawful/contractual authority for the dataset and its permitted purpose.
- Record source system, source version, dataset snapshot, tenant/site scope and extraction window.
- Verify canonical asset/component mapping and maintenance-label provenance.
- Check timestamps, timezone, units, sampling interval, quality, duplicates, gaps, late data, sensor health and operating state.
- Identify synthetic, simulated, public, augmented and customer observations explicitly.
- Confirm that the data represents the intended operating envelope.
- Document exclusions and missingness; never silently coerce missing measurements to zero.

For PDM, join condition measurements with asset/component identity, operating context and verified maintenance outcomes. Keep fixed-plant condition signals distinct from low-frequency mobile-fleet utilization unless a specific model contract deliberately combines them.

### Stage C — establish baselines

Use, in order as appropriate:
1. Existing engineering/OEM limits and deterministic calculations.
2. Statistical process monitoring and trend/change detection.
3. Simple interpretable classifiers or regressors.
4. Tree ensembles or other classical models.
5. Deep learning, graph neural networks or foundation models only when a measured need and representative data support them.

Record a baseline result before tuning. A more complex candidate is not accepted unless it improves task-relevant, operationally meaningful metrics or provides a required capability without unacceptable cost.

### Stage D — reproducible evaluation

- Use temporal holdouts for time-dependent data.
- Use asset holdouts when the deployment claim includes unseen assets.
- Use site holdouts when the deployment claim includes cross-site generalization and sufficient data exists.
- Prevent leakage through overlapping windows, repeated asset records, future-derived labels, post-maintenance values and feature normalization fitted on holdout data.
- For imbalanced failure events, report class-wise precision/recall, PR-AUC and alert burden rather than accuracy alone.
- Evaluate calibration and uncertainty where probabilities or risk scores are shown.
- Include false alerts per asset/time period, missed events, lead time and reviewer burden for operational alerting.
- Use a prospective shadow period before a model can affect consequential maintenance workflows.

Public benchmarks and synthetic simulation support pipeline tests and method comparison; they do not prove performance at a mine or customer site.

## 6. Feature and model versioning

Treat the feature set as a versioned interface. A model artifact is not portable or reproducible without its preprocessing and postprocessing contract.

Each feature definition must specify:
- Stable feature name and semantic meaning.
- Source concept and source mapping, not only display label.
- Data type, unit and allowed/null semantics.
- Sampling/aggregation method and time window.
- Operating-state assumptions and quality filters.
- Missing-data behavior and imputation policy, if any.
- Transformation code/version and dependency version.
- Source/connector lineage and effective-dated mapping rules.

Each model version must bind to an immutable feature-set version. A change in units, windowing, identity mapping, missing-value policy, scaling, tokenization or column order is a compatibility change and requires explicit versioning and evaluation.

## 7. ONNX export and CPU inference standard

ONNX is an interchange format for supported model graphs; ONNX Runtime is an inference runtime. Neither is a requirement to train every model in ONNX. The training framework may remain the appropriate research/training environment, while a validated ONNX artifact is used for deployment when conversion preserves behavior and required operators are supported.

### Export decision

Export to ONNX when:
- The model and preprocessing operations are supported by the chosen exporter/runtime.
- The production inference path benefits from a portable artifact or runtime isolation.
- Conversion parity can be demonstrated on representative and boundary inputs.
- The target CPU/edge runtime supports the operators, opset and data types required.

Do not force ONNX for models whose algorithms, custom operators, dynamic behavior or preprocessing cannot be converted reliably. A tested native CPU implementation is preferable to an incorrect or fragile export.

### Required ONNX release checks

1. Record training framework/version, exporter/version, ONNX opset and ONNX Runtime version.
2. Run the ONNX checker and load the artifact using the exact target runtime.
3. Validate input/output names, tensor types, shapes, dynamic dimensions and batch behavior.
4. Compare framework and ONNX outputs on a versioned golden dataset, representative data, boundary values and missing/invalid-input cases.
5. Define task-specific numeric tolerances before accepting parity; do not use one universal tolerance for all models.
6. Test the intended CPU execution provider and target operating environment.
7. Measure cold-start and steady-state latency, throughput, peak memory and artifact size on representative hardware.
8. Test single-item and supported batch paths, concurrent requests where relevant, and graceful failure on contract violations.
9. Verify that preprocessing, feature ordering, scaling, class mapping, thresholds and postprocessing match the training pipeline.
10. Record limitations, approved deployment targets, rollback artifact and model-card details.

A successful export or unit test does not by itself establish predictive validity. Both numerical parity and task-level holdout performance are required.

### CPU-first optimisation sequence

Apply only after a baseline is measured:
1. Reduce unnecessary feature computation and data copying.
2. Use efficient vectorized operations and sensible batch sizes.
3. Apply ONNX graph optimisations supported by the runtime.
4. Evaluate dynamic or static quantization, including task-level accuracy and calibration impacts.
5. Consider distillation or structured pruning only when simpler optimisation is insufficient.
6. Re-run the full parity, quality, latency, memory and operating-envelope suite after every optimization.

Do not assume INT8 or another low-precision format is automatically faster on every CPU. Hardware, operator coverage and model shape matter. Retain the approved higher-precision artifact as a rollback option.

For high-frequency vibration or other high-volume signals, evaluate signal acquisition and feature extraction at the customer-approved edge/condition-monitoring layer. Send MineOS the approved features or summaries when that is the appropriate topology; do not assume all raw waveforms should be transmitted to a central service.

## 8. Model package and inference contract

A deployable model package must include, as applicable:

- Immutable model ID, semantic version and artifact checksum.
- Task definition, intended use, excluded use and operating envelope.
- Artifact format, runtime/framework, supported architecture and dependency lock.
- Feature-set and schema versions.
- Preprocessing and postprocessing implementation/version.
- Training dataset references, authorization classification and lineage.
- Evaluation protocol, holdout design, metrics, calibration and limitations.
- Export/parity test report and target hardware benchmark.
- Model card, owner, reviewer, approval date and rollback reference.
- Monitoring signals, thresholds and retraining/review policy.

A prediction response should carry:
- Prediction ID and creation timestamp.
- Tenant/site/facility/asset/component identity.
- Task type, model ID/version and feature-set version.
- Input time window, source lineage and data-quality summary.
- Output score or value, units and risk horizon where applicable.
- Calibrated probability only when calibration is demonstrated.
- Uncertainty/interval and explicit abstention/degraded state.
- Evidence or contributing measurements with source references.
- Intended-use limitations and review status.

Prediction, recommendation, human approval, work order, executed action and verified outcome remain separate records. The model output must not be represented as a confirmed root cause or a completed action.

## 9. Runtime, security and tenant isolation

- Resolve authorization before data retrieval and before each inference/output path; do not rely on an opaque model endpoint as the security boundary.
- Scope feature materialization, temporary files, model evaluation, embeddings, vector indexes, caches, logs and output records to the authorized tenant/site.
- Do not train shared models on customer data by default. Explicit authorization and contractual governance are required for any cross-customer use.
- Keep secrets outside source control and model artifacts. Use least-privilege source credentials and read-only OT access for the initial connector scope.
- Validate input size, tensor dimensions, types and values before inference. Bound compute, memory and request duration.
- Treat model files and external metadata as supply-chain artifacts: pin versions, verify checksums, scan dependencies and restrict artifact write access.
- Avoid embedding customer-sensitive source records in model metadata, logs or exception messages.
- Support customer-controlled edge/on-premises inference where OT policy, latency, availability or residency requires it.
- Preserve a deterministic rules-based or previously approved fallback where the use case requires one. A missing model must not silently disable source-system protections.

## 10. Monitoring and lifecycle governance

Monitor more than service uptime:
- Input availability, freshness, quality and schema changes.
- Feature distributions, missingness and operating-envelope coverage.
- Prediction distribution, abstention rate and inference errors.
- Model latency, memory and runtime compatibility.
- Calibration, alert burden and verified outcomes when labels mature.
- Drift by asset class, site, operating mode and relevant cohort.

Drift is a signal for investigation, not automatic permission to retrain. Production retraining and promotion require versioned data, leakage-safe evaluation, domain review, approval and rollback readiness. Feedback records may be incomplete, delayed or biased by maintenance decisions and must be reviewed before becoming labels.

Use lifecycle states such as **research**, **candidate**, **shadow**, **approved**, **degraded**, **retired** and **rolled back**. Record who changed a state, when, why, which evaluation passed and which previous artifact remains available.

## 11. MineOS-specific boundaries

- **Vendor neutrality:** use customer-approved source connectors and canonical contracts. Do not couple model code to one SCADA, historian, OEM or CMMS payload.
- **Existing analytics:** when an installed, licensed EHS, condition-monitoring or PdM application already supplies a validated capability, MineOS should ingest and contextualize its outputs rather than duplicate the function without a clear gap.
- **OT safety:** initial model outputs are read-side intelligence and advisory evidence. They do not write to PLC, SCADA, DCS or SIS and do not alter setpoints or protection logic.
- **Maintenance:** predictions can support prioritization and review; qualified personnel and customer maintenance workflows retain decision authority.
- **Data ownership:** follow the customer policy and MineOS data-governance configuration. Do not assume all customers permit central persistence or shared training.
- **Deployment portability:** keep the model package and contracts usable in cloud, dedicated, on-premises and hybrid installations where the chosen runtime supports them.

## 12. Per-model release checklist

- [ ] Task, intended use, prohibited use and prediction horizon documented.
- [ ] Data rights, tenant/site scope, provenance and dataset version recorded.
- [ ] Canonical asset identity, units, timestamps, operating context and quality validated.
- [ ] Feature-set schema and transformations versioned and tested.
- [ ] Engineering/statistical baseline measured.
- [ ] Temporal and relevant asset/site holdouts completed without leakage.
- [ ] Metrics include operational costs, calibration/uncertainty and abstention where relevant.
- [ ] Domain/reliability review completed and limitations documented.
- [ ] Framework-to-ONNX parity passed, if ONNX is used.
- [ ] Target CPU runtime, latency, memory and failure behavior tested.
- [ ] Model card, checksums, dependency/licence record and artifact provenance stored.
- [ ] Tenant isolation, authorization and secure artifact handling tested.
- [ ] Shadow evaluation and promotion criteria met.
- [ ] Monitoring owner, rollback and fallback behavior documented.
- [ ] Human review and customer-system action remain separate from prediction.

A model that has not passed its task-specific release gates remains a research or shadow artifact and must not be presented as production-validated.

## 13. Adoption sequence for MineOS

1. **Documentation baseline:** adopt this standard and link it to MineOS AI and PDM architecture.
2. **Repository inspection:** map actual MineOS source modules, runtime, dependency management, test framework and deployment profiles before choosing implementation paths.
3. **Small reference pipeline:** select one low-risk use case and one representative asset/task; implement data contract checks, a transparent baseline, reproducible evaluation and a model card.
4. **CPU inference proof:** benchmark a native CPU path and export to ONNX only if parity and runtime checks pass.
5. **Connector-to-model integration:** consume a simulator first, then an approved read-only source and verified maintenance outcomes.
6. **Shadow pilot:** evaluate prospectively with domain reviewers and approved acceptance thresholds.
7. **Reusable package extraction:** after the pilot proves stable interfaces, extract shared utilities into a versioned internal package with optional extras. Do not create a premature universal framework.
8. **Cross-project reuse:** document which components can be safely reused by other Bokang-owned projects without sharing customer data, credentials, tenant state or proprietary model artifacts.

No model, connector or runtime is considered implemented merely because it is listed in this standard. Implementation status must be established by repository code, automated tests and deployment evidence.
