# Safety, Security and AI Governance

**Status:** Foundational policy baseline — specialist and customer review required

## 1. Safety boundary

MineOS is an operational intelligence and decision-support layer. Existing customer control and protection systems remain authoritative for PLC-based control, SCADA/DCS control functions, safety instrumented systems (SIS), emergency stops, trips, interlocks and equipment protection.

The initial MineOS scope is monitoring, analytics, prediction, recommendations and human-approved decision workflows. MineOS must not bypass, disable, override or weaken safety functions.

## 2. No autonomous real-equipment control initially

- AI outputs are advisory unless reviewed and approved through a defined workflow.
- No model or agent may directly write control commands to real equipment in the initial release.
- Supervisory control, if considered later, is a separate product and safety case—not an implicit extension of recommendations.
- Any future control integration requires hazard analysis, OT cybersecurity assessment, authorization design, independent validation, change management, testing and customer approval.

## 3. Prediction and recommendation separation

The system must distinguish source observation/measurement, source alarm/event, MineOS-detected anomaly, model prediction/forecast, AI-generated recommendation, human review and approval/rejection, actual action, and outcome/feedback.

Never represent a prediction as a confirmed fault, a recommendation as an approved instruction, or an approval as proof of execution.

## 4. Human accountability and audit

Consequential workflows should record the user, role, scope, recommendation version, evidence shown, decision, timestamp, reason/comment where applicable, resulting action reference and outcome. Approval authority must be configurable and enforced.

## 5. OT and IT security

- Follow customer OT network segmentation and approved conduits.
- Prefer controlled, least-privilege, read-oriented integration in initial releases.
- Protect credentials and certificates; never embed secrets in code, notebooks or logs.
- Authenticate and authorize connectors, services, users and agents.
- Encrypt data in transit and at rest where supported by the deployment.
- Maintain secure configuration, patching, vulnerability management and audit trails.
- Define backup, recovery, incident response and security monitoring responsibilities for each deployment model.

## 6. Tenant and data protection

Tenant isolation applies to APIs, databases, object storage, queues, caches, search, analytics, AI retrieval, embeddings, model workflows, logs and support tooling. Cross-tenant data access is prohibited unless an explicit, authorized and audited mechanism is defined.

Customer data retention, residency, export, deletion and secondary use must be governed by contract and applicable law. Customer data must not be used to train shared models by default.

## 7. AI governance

- Define intended use and limitations for every material model.
- Validate models on representative data before operational use.
- Report data quality, uncertainty and known limitations.
- Monitor drift and model performance.
- Keep model and feature versions traceable.
- Require controlled approval for model promotion and rollback.
- Preserve human oversight for consequential decisions.
- Prevent unauthorized retrieval across tenant boundaries in AI applications.
- Evaluate AI-generated summaries and recommendations for grounding, completeness and harmful overconfidence.

## 8. Governance note

This document is a product-level baseline, not a substitute for site-specific hazard studies, legal advice, a formal safety case, OT security architecture or applicable regulatory compliance assessment. Applicable standards and assurance requirements must be identified with qualified specialists for each deployment and jurisdiction.
