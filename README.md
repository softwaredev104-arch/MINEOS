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
- Replaceable industrial adapters for protocols, vendor APIs, historians, OEM telematics and maintenance systems.
- Predictive-maintenance models must be validated against representative operating data and verified maintenance outcomes before operational promotion.

## Documentation

### Product and domain
- [Product requirements](docs/product/PRODUCT_REQUIREMENTS.md)
- [Domain and process model](docs/architecture/DOMAIN_AND_PROCESS_MODEL.md)
- [Process Configuration Engine](docs/architecture/PROCESS_CONFIGURATION_ENGINE.md)

### Architecture and integrations
- [Reference architecture](docs/architecture/REFERENCE_ARCHITECTURE.md)
- [Industrial connector architecture](docs/architecture/INDUSTRIAL_CONNECTOR_ARCHITECTURE.md)
- [Industrial vendor and API research register](docs/integrations/INDUSTRIAL_VENDOR_API_REGISTRY.md)

### AI and governance
- [MineOS AI architecture](docs/architecture/MINEOS_AI_ARCHITECTURE.md)
- [Predictive maintenance data and model strategy](docs/ai/PREDICTIVE_MAINTENANCE_DATA_AND_MODEL_STRATEGY.md)
- [Safety, security and AI governance](docs/governance/SAFETY_SECURITY_AI_GOVERNANCE.md)

### Engineering and decisions
- [Non-functional requirements and acceptance](docs/engineering/NFR_AND_ACCEPTANCE.md)
- [Decisions and open questions](docs/decisions/DECISIONS_AND_OPEN_QUESTIONS.md)

## Status
The repository contains a product requirements baseline, proposed architecture, governance rules and a public-documentation research baseline for industrial vendor interfaces and predictive maintenance. Confirmed decisions are distinguished from proposals and unresolved questions. Documentation of a vendor interface does not mean a MineOS connector has been implemented, tested against a live system, commercially licensed or approved by a customer.

## Data ownership and persistence
Customer operational systems remain authoritative sources of record. MineOS ingests and contextualizes data and may retain selected copies, normalized records, events, features, reports and AI outputs according to customer policy and deployment configuration. Customers may choose approved customer-controlled storage destinations; MineOS is not required to be the sole or permanent repository for customer data.

## Initial operational boundary
MineOS initially observes, analyzes, predicts and recommends. Existing control and safety systems remain authoritative for equipment protection, interlocks, emergency stops and safety instrumented functions. MineOS does not autonomously command real equipment in the initial scope.
