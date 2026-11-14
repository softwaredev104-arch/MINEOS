# Product Decisions and Open Questions

**Status:** Living decision register

This register separates decisions explicitly confirmed in product discussions from proposals and questions that still require validation.

## 1. Confirmed decisions

| ID | Decision | Status |
|---|---|---|
| DEC-001 | Support open-pit, underground, processing and beneficiation mining operations. | Confirmed |
| DEC-002 | Design for global customers from the beginning. | Confirmed |
| DEC-003 | Support cloud, on-premises and hybrid deployments. | Confirmed |
| DEC-004 | Support both shared multi-tenant SaaS and dedicated customer deployments. | Confirmed |
| DEC-005 | Initial operational scope is monitoring, predictions and human-approved recommendations. | Confirmed |
| DEC-006 | Supervisory control may be considered later, subject to separate requirements and approval. | Confirmed |
| DEC-007 | Support multiple companies, sites and facilities with different processing operations. | Confirmed |
| DEC-008 | MineOS is broader than mining alone: mining is the first major industry focus, with coal processing, coke production and other industrial facilities in the wider direction. | Confirmed |
| DEC-009 | MineOS interfaces with existing operational systems and equipment; it does not manufacture or replace them. A site may contain heterogeneous systems and technologies across different operational areas. | Confirmed |
| DEC-010 | Customer source systems remain authoritative for the operational data they originate. MineOS may retain configured, policy-approved copies and derived data needed for intelligence, analytics and reporting; it is not required to be the sole or permanent data repository. | Confirmed |
| DEC-011 | MineOS should support delivering selected data, reports and derived outputs to customer-controlled infrastructure and external enterprise services. Microsoft Graph is an intended integration direction, with exact use cases and scope to be specified. | Confirmed direction; implementation scope open |

## 2. Proposed architectural implications

These are design recommendations derived from confirmed decisions, not separate customer-validated requirements:
- Use a configurable tenant → organization → site → facility → process area → process unit → asset conceptual hierarchy.
- Use configurable process topologies rather than a fixed mine/plant schema.
- Keep tenant isolation consistent across application, data, analytics, AI and operational tooling.
- Keep domain contracts portable across SaaS, dedicated, on-premises and hybrid deployments.
- Use process templates as optional accelerators rather than mandatory workflows.
- Keep industrial connectors replaceable and vendor-neutral.
- Treat supervisory control as a separately governed future capability.
- Design for heterogeneous operational technology across areas within the same site; use independent, replaceable source adapters.
- Preserve customer source-of-record authority while allowing policy-controlled MineOS persistence of selected copies and derived outputs.
- Make customer-controlled outbound data/report destinations part of the integration architecture; treat Microsoft Graph as an enterprise integration surface, not an industrial historian.
- Model process topology as a typed, versioned graph separate from the organizational/asset containment hierarchy.
- Publish immutable, effective-dated configuration versions and preserve their references in analytics and AI outputs.
- Use template derivation and facility-specific configuration rather than one mandatory process template per industry.

## 3. Open product and architecture decisions

| ID | Question | Why it matters |
|---|---|---|
| OPEN-001 | Which industrial verticals beyond mining should be prioritized after the initial mining focus? | Determines product packaging, domain extensions and validation partners. |
| OPEN-002 | Which commodities and process routes should be used for first reference implementations? | Determines initial templates, KPIs and data requirements. |
| OPEN-003 | Which connector protocols and vendors are required for the first release? | Determines integration roadmap and OT deployment design. |
| OPEN-004 | What are expected tenant, site, asset and telemetry scales? | Determines sizing and architecture validation. |
| OPEN-005 | Which identity providers and enterprise authentication methods are required? | Determines identity integration and access policy. |
| OPEN-006 | What are data retention, residency, sovereignty and deletion requirements by customer/region? | Determines deployment and data lifecycle design. |
| OPEN-007 | Which languages and localization requirements are launch priorities? | Determines user experience and translation scope. |
| OPEN-008 | Which ERP, CMMS, MES, laboratory and enterprise integrations are highest priority? | Determines business workflow integration. |
| OPEN-009 | What mobile workflows are required, and which must work offline? | Determines mobile and edge scope. |
| OPEN-010 | What are required availability, latency, throughput, RTO and RPO targets? | Needed before service-level commitments. |
| OPEN-011 | What commercial packaging and licensing model should be used for SaaS and dedicated deployments? | Determines provisioning, metering and entitlement design. |
| OPEN-012 | What governance and validation process is required before any future supervisory-control capability? | Safety-critical future scope. |
| OPEN-013 | Should process topology be persisted as relational typed-edge tables, a graph database or a hybrid? | Decide from query patterns, transaction consistency, scale and operational complexity. |
| OPEN-014 | Which process templates and domain experts are needed for the first pilot routes? | Determines validation coverage and initial configuration UX. |
| OPEN-015 | What configuration changes require dual approval or formal management-of-change workflows? | Determines configuration governance and audit controls. |
| OPEN-016 | How should effective-dated corrections trigger historical KPI recomputation and AI feature/model impact assessment? | Needed for reproducible historical analysis. |
| OPEN-017 | Which customer-controlled storage targets, protocols, formats and synchronization patterns must be supported first? | Determines outbound connector architecture and delivery guarantees. |
| OPEN-018 | Which Microsoft Graph workloads are in scope (for example, SharePoint document libraries, OneDrive, Teams notifications/files), and what tenant-consent and permission model is required? | Prevents treating Microsoft Graph as one generic storage destination and defines least-privilege scopes. |
| OPEN-019 | Which data classes may MineOS retain, for how long, and which must remain only in customer infrastructure? | Determines storage, caching, reporting, AI history and deletion behavior. |
| OPEN-020 | What exact equipment operations, if any, should be considered for a future permissioned MineOS supervisory interface? | Defines a separately governed future scope; no real-equipment command capability is approved for the initial release. |

## 4. Decision change process

When a decision changes, record the decision ID, previous value, new value, rationale, date, affected requirements and architecture documents. Update downstream documentation and tests rather than silently changing assumptions.
