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

## 2. Proposed architectural implications

These are design recommendations derived from confirmed decisions, not separate customer-validated requirements:
- Use a configurable tenant → organization → site → facility → process area → process unit → asset conceptual hierarchy.
- Use configurable process topologies rather than a fixed mine/plant schema.
- Keep tenant isolation consistent across application, data, analytics, AI and operational tooling.
- Keep domain contracts portable across SaaS, dedicated, on-premises and hybrid deployments.
- Use process templates as optional accelerators rather than mandatory workflows.
- Keep industrial connectors replaceable and vendor-neutral.
- Treat supervisory control as a separately governed future capability.

## 3. Open product decisions

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

## 4. Decision change process

When a decision changes, record the decision ID, previous value, new value, rationale, date, affected requirements and architecture documents. Update downstream documentation and tests rather than silently changing assumptions.
