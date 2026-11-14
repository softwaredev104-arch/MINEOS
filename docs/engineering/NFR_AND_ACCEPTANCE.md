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
