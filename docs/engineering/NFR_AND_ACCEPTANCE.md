# Non-Functional Requirements and Acceptance Framework

**Status:** Initial baseline — targets to be agreed

## 1. Non-functional requirement categories

| ID | Category | Baseline requirement |
|---|---|---|
| NFR-REL-001 | Reliability | Ingestion and application services handle transient failures with bounded retries and observable recovery. |
| NFR-REL-002 | Resilience | Edge and hybrid deployments define buffering, synchronization and behavior during connectivity loss. |
| NFR-SCL-001 | Scalability | Scale by tenant, site, asset count, telemetry volume, retention and concurrent users. |
| NFR-INT-001 | Interoperability | Use documented, versioned interfaces and replaceable integration adapters. |
| NFR-SEC-001 | Security | Enforce least privilege, secure secrets, authenticated interfaces and auditable access. |
| NFR-ISO-001 | Isolation | Demonstrate tenant isolation across every data and compute path, including AI. |
| NFR-PER-001 | Performance | Define measurable ingestion, query, dashboard and inference latency targets per deployment profile. |
| NFR-AVA-001 | Availability | Define service-level objectives, maintenance windows and recovery targets per deployment. |
| NFR-DAT-001 | Integrity | Preserve source timestamps, units, quality, provenance and transformation lineage. |
| NFR-OBS-001 | Observability | Provide logs, metrics, traces, connector health and actionable failure diagnostics. |
| NFR-PORT-001 | Portability | Keep domain behavior portable across SaaS, dedicated, on-premises and hybrid environments. |
| NFR-MNT-001 | Maintainability | Use modular boundaries, documented APIs, automated tests and controlled migrations. |
| NFR-AUD-001 | Auditability | Record consequential actions, approvals, configuration changes and model lifecycle events. |
| NFR-GLB-001 | Global readiness | Support time zones, units, locale, shift calendars and data residency configuration. |

## 2. Acceptance criteria examples

### Tenant isolation
Given two separate tenants, a user authenticated in Tenant A cannot retrieve Tenant B records through APIs, dashboards, search, exports, background jobs or AI retrieval. Attempts are denied and security-relevant events are logged without leaking protected data.

### Process configurability
Given two facilities with different process topologies, each can represent its own process units, assets, flows, tags and KPIs without requiring the other facility to adopt the same topology. A configuration change at one facility does not silently alter another.

### Data provenance
Given an ingested measurement, the platform can identify its source, source timestamp, ingestion timestamp, unit, quality state and applied transformations. Invalid or stale data is not silently presented as healthy current data.

### Recommendation workflow
Given a consequential recommendation, the platform records its evidence, model/rule version, uncertainty, reviewer, decision and timestamp. The recommendation cannot be represented as an executed action without a separately recorded action outcome.

### Deployment portability
For each supported deployment profile, installation and upgrade procedures are documented and domain/API contracts behave consistently within the supported configuration.

## 3. Test strategy

- Unit tests for domain rules, transformations, authorization and calculations.
- Contract tests for APIs and industrial connectors.
- Integration tests for ingestion, persistence, events and synchronization.
- Security tests for tenant isolation, privilege boundaries and secrets handling.
- Data-quality tests for duplicates, gaps, late events, clock skew, unit mismatch and schema drift.
- AI evaluation for baselines, representative holdouts, calibration/uncertainty where relevant, drift and site differences.
- Simulation tests for process scenarios, equipment failures and recovery behavior.
- End-to-end tests for recommendation review, approval, audit and feedback.
- Deployment tests for cloud, dedicated, on-premises and hybrid profiles as supported.

## 4. Targets that must not be invented

The following require product, customer and engineering agreement before being treated as SLOs or acceptance thresholds: availability percentages; ingestion throughput and maximum telemetry volume; end-to-end data latency; dashboard/API response times; AI inference latency and forecast horizons; recovery time and recovery point objectives; retention periods and storage limits; maximum tenant/site/asset scale; supported languages and accessibility targets; and model performance thresholds for each use case.

## 5. Requirement readiness

A requirement is ready for implementation when it has an owner, priority, scope, rationale, measurable acceptance criteria, dependencies, data/security/safety implications and a verification plan. Unresolved assumptions must remain visible rather than hidden in implementation.

## 5. Additional integration and data-governance acceptance scenarios

### Heterogeneous site integration
Given one site with multiple operational areas using different vendors, protocols and control platforms, MineOS can ingest from each through independent connectors. A failure or schema change in one connector does not silently corrupt or disable unrelated source integrations.

### Source-of-record and MineOS retention
Given a source measurement, an authorized user can identify the originating system and distinguish it from any MineOS-retained copy or derived result. Configured retention policies are applied by data class, and MineOS does not imply that its copy supersedes the source record.

### Customer-controlled destination
Given a configured customer-owned destination, an authorized administrator can define the data classes or reports eligible for delivery. Delivery is authenticated, access-scoped, encrypted where supported, observable and auditable; transient failures are retried without creating unintended duplicate deliveries.

### External enterprise integration
Given an enabled enterprise connector such as a Microsoft Graph integration, only explicitly granted scopes and configured destinations are used. Revoked credentials or permissions cause delivery to fail safely and produce an actionable audit/health event.

### Permissioned future equipment operation
If a future supervisory-operation capability is separately approved, tests demonstrate that unauthorized users cannot request or approve actions, permitted commands remain subject to the existing control system's interlocks and permissives, and MineOS distinguishes command request, acknowledgement and confirmed execution outcome.

## 6. Additional non-functional requirements

| ID | Category | Baseline requirement |
|---|---|---|
| NFR-INT-002 | Heterogeneous integration | Multiple vendor/protocol connectors can coexist within one site without coupling core domain behavior to any single source. |
| NFR-DAT-002 | Data ownership | Source-of-record identity and lineage remain distinguishable from MineOS copies and derived artifacts. |
| NFR-DAT-003 | Configurable retention | Retention, export and deletion behavior can be configured by customer, data class and deployment. |
| NFR-INT-003 | Outbound integration | Customer-controlled destinations use scoped credentials, delivery observability, retry and auditable synchronization. |
| NFR-SEC-002 | External destination security | Outbound connectors enforce least privilege, tenant/site scope and secure credential handling. |

Targets and exact connector support remain subject to customer and engineering validation.
