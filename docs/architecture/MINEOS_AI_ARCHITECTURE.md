# MineOS AI Architecture

**Status:** Proposed AI architecture — review required

## 1. Role of MineOS AI

MineOS AI is the intelligence subsystem of MineOS. It consumes governed operational context and provides detection, forecasting, diagnosis assistance, prediction and recommendations. It does not own industrial safety authority and does not directly control real equipment in the initial scope.

## 2. Intelligence capabilities

### Statistical and rules-based intelligence
Engineering limits, process constraints, deterministic calculations, statistical process monitoring and domain consistency checks such as mass/energy balance where data supports them.

### Classical machine learning
Candidate methods include tree ensembles, gradient boosting, anomaly detection, clustering and classification. Model choice must be justified against baselines and operational data quality.

### Deep learning and time-series models
Candidate methods include MLPs, CNNs, LSTM/GRU, temporal convolution, transformers, autoencoders and suitable time-series foundation models. These are options, not mandatory technology choices.

### Process-aware and physics-informed intelligence
Combine learned models with engineering limits, process topology, conservation relationships and domain constraints when valid. A model must not be described as physics-informed unless those constraints are actually represented and evaluated.

### Simulation and digital twins
Use configurable simulators and digital-twin models for scenario testing, synthetic data, workflow validation and safe optimization research. Clearly label simulated data and results; synthetic training performance is not proof of real-site performance.

## 3. Initial AI use cases

- Anomaly detection.
- Equipment health estimation.
- Predictive maintenance and failure-risk forecasting.
- Production and process-variable forecasting.
- Energy and water forecasting/analytics where relevant.
- Event correlation and root-cause investigation assistance.
- Bottleneck and performance-deviation detection.
- Shift and daily operational summaries.
- Evidence-grounded operational copilot.

Prioritize use cases according to available data, measurable customer value, risk and validation feasibility.

## 4. Data strategy

Use distinct data categories:
1. Public benchmark datasets for method development and reproducible experimentation.
2. MineOS synthetic simulation data for schema, process relationships, controlled scenarios, fault injection and simulation testing.
3. Customer operational data only when lawfully and contractually authorized.

Public datasets must not be described as mine-specific unless provenance supports that claim. Synthetic and public benchmark results must be distinguished from customer-site validation.

For predictive maintenance, preserve the distinction between high-frequency condition data, ordinary process telemetry, low-frequency fleet utilization, and maintenance outcome records. Fixed-plant and mobile-fleet models may share platform services but should have separate feature contracts and validation plans where their signals and failure mechanisms differ.

See [Predictive Maintenance Data and Model Strategy](../ai/PREDICTIVE_MAINTENANCE_DATA_AND_MODEL_STRATEGY.md) for canonical data contracts, public research datasets, candidate model families, leakage-aware evaluation, maintenance feedback and promotion gates.

## 5. Prediction-to-outcome lifecycle

Governed operational data → context and feature generation → model inference/deterministic analysis → prediction with uncertainty and evidence → separate recommendation → human review and approval → customer-controlled action outside MineOS → outcome and feedback capture → evaluation and governed model update.

A recommendation is not an approval. An approval is not proof that an action was executed. An executed action and its outcome must be recorded separately.

## 6. Model governance

For each production model, record model identity/version/artifact provenance, training data lineage and permitted use, feature definitions and schema versions, evaluation datasets/metrics/limitations, intended and excluded use, operating envelope, inference timestamp, model version, relevant input context, uncertainty and explanation metadata, monitoring, review owner and rollback path.

Require validation before promotion. Monitor performance and data drift. Retraining must be governed; feedback must not automatically alter a production model without evaluation and approval.

## 7. Tenant-aware AI

Tenant and user authorization must be enforced before retrieval, feature access, inference and result delivery. Embeddings, vector stores, caches, training datasets, prompts, logs and model evaluation must not create cross-tenant leakage. Customer data use for shared model training requires explicit policy and authorization; it must not be assumed.

## 8. Research and prototype boundary

Notebook/Colab environments are for research, simulation and prototyping—not production runtime. Mature code should be extracted into tested packages and deployable services, with versioned APIs and appropriate edge/cloud inference options.

Potential API capability families include anomaly detection, equipment health, maintenance risk, production forecasting, event analysis, root-cause assistance and report generation. Exact routes and contracts belong in API specifications.

## 9. Optimization and reinforcement learning

Optimization and reinforcement learning are research capabilities. Initial experimentation must use simulation, synthetic scenarios or approved offline datasets. Any future proposal involving real equipment or operational setpoints requires separate safety, cybersecurity, validation, authorization and change-management review. Direct real-equipment RL control is not in the initial scope.

## 10. Predictive-maintenance implementation direction

- Treat PDM as a family of asset- and task-specific models, not one universal model for every machine.
- Establish transparent engineering/statistical baselines before adopting more complex deep-learning models.
- Distinguish anomaly detection, fault classification, horizon-specific failure risk and remaining-useful-life (RUL) estimation. They require different labels, assumptions and evaluation.
- Join sensor/condition measurements with operating mode, duty/load context, asset/component identity and verified maintenance outcomes.
- Preserve raw source signals or source-derived features with source time, ingestion time, units, quality and lineage.
- Do not infer a failure solely from a shutdown, alarm or work-order closure.
- Use temporal, asset and (where possible) site holdouts to reduce data leakage and measure generalization.
- Evaluate calibration, false-alert burden, missed failures and lead time alongside conventional model metrics.
- Run prospective shadow evaluation before operational promotion.
- Require human review for consequential maintenance recommendations; the model does not approve or perform maintenance.

The detailed dataset, feature, maintenance-event, evaluation and model-promotion requirements are maintained in the PDM strategy document.

## 11. Reusable model engineering and ONNX

MineOS adopts a reuse-first, CPU-first model-engineering lifecycle with versioned datasets, feature contracts, baseline-first model selection, leakage-aware evaluation, immutable artifacts, and governed promotion. ONNX is the preferred interchange path only when the selected model can be exported without behavioral loss and passes runtime parity checks; it is not a requirement for every algorithm or a training framework.

See [Reusable Model Engineering and ONNX Standard](../ai/REUSABLE_MODEL_ENGINEERING_AND_ONNX_STANDARD.md) for candidate open-source tooling, licence review, model/feature versioning, ONNX export gates, CPU benchmarking, tenant isolation, model lifecycle and the per-model release checklist. Apply it together with the PDM strategy and connector/governance requirements; it does not supersede those domain-specific controls.


## 12. Initial fixed-plant reference implementation

The first fixed-plant reference pipeline is maintained in [research/fixed-plant-bearing-baseline](../../research/fixed-plant-bearing-baseline/README.md). It starts with vibration-based bearing fault classification and grouped validation. It is an engineering pilot only: it does not claim mine-site validity, future failure-risk forecasting or RUL estimation, and it does not connect to or write to operational control systems.
