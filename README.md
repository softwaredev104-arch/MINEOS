# MineOS

MineOS is a vendor-neutral industrial operations intelligence platform. It connects to existing operational and enterprise systems, contextualizes operational data, and provides monitoring, analytics, predictions, recommendations and decision support across industrial sites.

Mining is the first major industry focus. The platform is designed to support different mine types, processing plants and, over time, other industrial operations such as coal processing and coke production.

MineOS is an intelligence and integration layer—not a replacement for PLC, SCADA, DCS, SIS, historians, ERP or CMMS systems.

## Product principles
- Vendor-neutral integration with heterogeneous systems and equipment across every operational area.
- Customer control of operational source data, with configurable MineOS retention of permitted copies and derived intelligence.
- Delivery of reports and approved outputs to customer-controlled storage and enterprise services.
- Support open-pit, underground, processing and beneficiation operations.
- Extensible to industrial facilities with different process configurations.
- Multiple companies, sites and plants with strict tenant isolation.
- Shared multi-tenant SaaS and dedicated customer deployments.
- Cloud, on-premises and hybrid deployment.
- Human-approved decision workflows and evidence-led AI.
- Global readiness for units, time zones, calendars, localization and data residency.

## Documentation
- [Product requirements](docs/product/PRODUCT_REQUIREMENTS.md)
- [Reference architecture](docs/architecture/REFERENCE_ARCHITECTURE.md)
- [Domain and process model](docs/architecture/DOMAIN_AND_PROCESS_MODEL.md)
- [Process Configuration Engine](docs/architecture/PROCESS_CONFIGURATION_ENGINE.md)
- [MineOS AI architecture](docs/architecture/MINEOS_AI_ARCHITECTURE.md)
- [Safety, security and AI governance](docs/governance/SAFETY_SECURITY_AI_GOVERNANCE.md)
- [Non-functional requirements and acceptance](docs/engineering/NFR_AND_ACCEPTANCE.md)
- [Decisions and open questions](docs/decisions/DECISIONS_AND_OPEN_QUESTIONS.md)

## Status
This is the initial requirements baseline captured from product discussions. Confirmed decisions are distinguished from proposals and unresolved questions. It does not claim that documented capabilities are already implemented.

## Data ownership and persistence
Customer operational systems remain authoritative sources of record. MineOS ingests and contextualizes data and may retain selected copies, normalized records, events, features, reports and AI outputs according to customer policy and deployment configuration. Customers may choose approved customer-controlled storage destinations; MineOS is not required to be the sole or permanent repository for customer data.

## Initial operational boundary
MineOS initially observes, analyzes, predicts and recommends. Existing control and safety systems remain authoritative for equipment protection, interlocks, emergency stops and safety instrumented functions. MineOS does not autonomously command real equipment in the initial scope.
