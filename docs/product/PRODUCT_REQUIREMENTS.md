# MineOS Product Requirements

**Status:** Initial baseline — review required  
**Version:** 0.3

## 1. Product vision

MineOS is a global, vendor-neutral industrial operations intelligence platform. It connects to existing operational and enterprise systems and turns fragmented operational data into contextualized monitoring, analytics, predictions, recommendations and decision support.

Mining is the first major industry focus. The product must not be architected as a mining-only data model: it should be extensible to industrial processing facilities and other asset-intensive operations, including coal processing and coke production.

MineOS complements rather than replaces systems that directly operate or protect industrial equipment.

## 2. Confirmed product decisions

1. **Industrial coverage:** support open-pit, underground, processing and beneficiation mining operations. The wider direction includes other industrial processing facilities; coal processing and coke production were explicitly discussed as examples.
2. **Deployment:** support cloud, on-premises and hybrid deployment.
3. **Tenant deployment models:** support both shared multi-tenant SaaS and dedicated customer deployments.
4. **Operational authority:** initial scope includes monitoring, predictions and human-approved recommendations. Supervisory control may be considered later under separate requirements and approval.
5. **Market:** global mining and industrial customers from the beginning.
6. **Organization model:** support multiple companies, multiple sites and multiple plants/facilities with different processing operations.

## 3. Product principles

- Vendor-neutral and integration-first.
- Configurable rather than hardcoded to one commodity, mine, plant or process route.
- Multi-company and multi-site by design, with strict tenant isolation.
- Deployment-neutral architecture and support for constrained or disconnected industrial environments.
- Human accountability for consequential operational decisions.
- Explainable, uncertainty-aware and traceable AI outputs.
- Globalization and data governance designed in from the beginning.
- Reuse common platform capabilities while keeping site-specific process context independent.

## 4. Scope and operational coverage

### 4.1 Mining operations

The domain must be capable of representing:
- Open-pit and underground operations.
- Drilling, blasting, loading, hauling, extraction and material movement.
- Stockpiles, ROM handling, crushing and screening.
- Processing and beneficiation plants.
- Grinding and milling, flotation, leaching/hydrometallurgy, concentration/separation, dewatering/thickening, tailings and material handling.
- Water, energy, utilities and supporting infrastructure.

This is an initial coverage model, not a claim that every site uses every process.

### 4.2 Wider industrial processing

The architecture must be extensible beyond conventional mining facilities. Examples discussed include:
- Coal handling and coal processing.
- Coke production and associated plant operations.
- Other industrial facilities with process equipment, material/energy flows, operational constraints and measurable production outcomes.

The detailed industrial vertical roadmap remains open. Do not assume every industrial sector is committed for the first release.

### 4.3 Configurable facility and process models

Each facility must be able to define its own facility type, production context, process topology, process areas, stages, units, equipment hierarchy, material/energy/water/utility flows where relevant, telemetry mappings, engineering units, operating modes, shift calendars and KPIs.

Templates may accelerate configuration, but must remain adaptable and must not impose a universal process flow.

## 5. Organization and tenancy requirements

| ID | Requirement | Priority proposal |
|---|---|---|
| ORG-001 | Represent customer organizations/tenants as isolated security and configuration boundaries. | P0 |
| ORG-002 | Support multiple sites, mines and industrial facilities within an organization. | P0 |
| ORG-003 | Support multiple plants and operational areas within a facility. | P0 |
| ORG-004 | Apply role- and scope-based access at organization, site, facility and functional levels. | P0 |
| ORG-005 | Provide authorized group-level views across sites without exposing another tenant's data. | P1 |
| ORG-006 | Support shared SaaS and dedicated customer environments without changing core domain semantics. | P0 |

## 6. Functional requirements

Priorities are proposals for planning: P0 foundational, P1 important early capability, P2 later capability, P3 exploratory/future.

### 6.1 Asset and operational context
- **AST-001 (P0):** Maintain configurable organization, site, facility, area, process-unit and equipment hierarchies.
- **AST-002 (P0):** Associate assets with tags, telemetry points, metadata, engineering units and source systems.
- **AST-003 (P1):** Model explicitly defined relationships such as parent/child, contains, feeds and transfers-to.
- **AST-004 (P1):** Maintain asset criticality, operating state and relevant maintenance context.
- **AST-005 (P1):** Allow process topology and asset configuration to differ between facilities.

### 6.2 Industrial integration and data
- **DAT-001 (P0):** Ingest data from existing industrial and enterprise systems through secure, replaceable connectors.
- **DAT-002 (P0):** Preserve source identity, source timestamps, ingestion timestamps and data-quality metadata.
- **DAT-003 (P0):** Normalize data into canonical platform representations without losing source semantics.
- **DAT-004 (P1):** Support time-series telemetry, events, alarms, equipment states, production records and contextual data.
- **DAT-005 (P1):** Support buffering, retry, synchronization and controlled operation during intermittent connectivity.
- **DAT-006 (P1):** Provide connector health, ingestion observability and data-quality reporting.
- **DAT-007 (P2):** Expand connector coverage according to customer and industry priorities.

### 6.3 Operational monitoring and analytics
- **OPS-001 (P0):** Provide facility- and asset-aware operational monitoring.
- **OPS-002 (P1):** Support configurable dashboards, trends, events, alarms and operational KPIs.
- **OPS-003 (P1):** Provide comparisons across shifts, assets, process areas and authorized sites.
- **OPS-004 (P1):** Make data freshness, quality and missingness visible.
- **OPS-005 (P2):** Support configurable reports and cross-site benchmarking.

### 6.4 MineOS AI
- **AI-001 (P1):** Detect anomalies in telemetry and operational behavior.
- **AI-002 (P1):** Estimate equipment health and identify developing degradation.
- **AI-003 (P1):** Forecast failures and maintenance risk with uncertainty and evidence.
- **AI-004 (P1):** Forecast production and relevant process variables.
- **AI-005 (P1):** Support energy and water forecasting/analytics where data is available.
- **AI-006 (P2):** Correlate events and assist root-cause investigation.
- **AI-007 (P2):** Detect bottlenecks and process-performance deviations.
- **AI-008 (P2):** Generate contextual shift, daily and operational summaries.
- **AI-009 (P2):** Provide a natural-language copilot grounded in authorized operational data.
- **AI-010 (P0):** Record model version, input/data provenance, inference time, confidence or uncertainty, and explanation metadata for material predictions.
- **AI-011 (P1):** Monitor model performance, drift and data quality; support controlled rollback and revalidation.

### 6.5 Recommendations and decision workflows
- **REC-001 (P0):** Distinguish observed facts, detected anomalies, model predictions, recommendations, approvals and executed actions.
- **REC-002 (P1):** Present recommendations with rationale, supporting evidence, expected impact, uncertainty and relevant constraints.
- **REC-003 (P0):** Require an authorized human decision before consequential recommendations are treated as approved actions.
- **REC-004 (P0):** Record approver, decision, timestamp, context and subsequent outcome for controlled workflows.
- **REC-005 (P1):** Capture operator feedback and actual outcomes to support evaluation and governed improvement.

### 6.6 Digital twin, simulation and optimization
- **DT-001 (P2):** Support configurable process/asset models and simulation environments.
- **DT-002 (P2):** Support synthetic and scenario-based data for development, testing and validation.
- **OPT-001 (P2):** Explore constrained optimization and decision-support methods using site-specific objectives and limits.
- **OPT-002 (P3):** Research reinforcement learning and advanced optimization in simulation or approved offline environments before any real-world deployment consideration.

### 6.7 Reporting and global operations
- **RPT-001 (P1):** Generate configurable operational, maintenance, production and management reports.
- **GLB-001 (P0):** Store timestamps with unambiguous time-zone context and display them in configured local time.
- **GLB-002 (P0):** Support metric and imperial units and configurable engineering units, with explicit conversions.
- **GLB-003 (P1):** Support site-specific shifts, calendars and operating-day definitions.
- **GLB-004 (P1):** Support regional number/date formats, currencies for financial reporting and localization-ready interfaces.
- **GLB-005 (P1):** Support customer-specific data residency and retention policies where required.

### 6.8 Identity, access and audit
- **SEC-001 (P0):** Authenticate users and authorize access according to tenant, role and permitted organizational scope.
- **SEC-002 (P0):** Enforce tenant isolation across APIs, storage, jobs, analytics and AI retrieval.
- **SEC-003 (P0):** Audit security-sensitive and consequential user/system actions.
- **SEC-004 (P1):** Support enterprise identity integration and configurable authentication policies.
- **SEC-005 (P1):** Apply least privilege to users, services, connectors and AI agents.

## 7. Candidate user roles

Executive/group leadership; mine/site manager; plant manager; operations manager; control-room operator; shift supervisor; maintenance manager; reliability engineer; process engineer; mining engineer; energy manager; water/environment specialist; IT/OT or platform administrator; data engineer, data scientist or AI specialist.

Roles are not mutually exclusive. Authorization must be configurable and scoped to the customer's organization and facilities.

## 8. Deployment requirements

- **DEP-001 (P0):** Support shared multi-tenant SaaS.
- **DEP-002 (P0):** Support dedicated customer deployments.
- **DEP-003 (P0):** Support on-premises and hybrid topologies.
- **DEP-004 (P1):** Separate deployment-specific infrastructure concerns from portable domain and application logic.
- **DEP-005 (P1):** Support secure edge ingestion/buffering and defined behavior during loss of upstream connectivity.
- **DEP-006 (P1):** Document supported deployment topologies, upgrade procedures, backup, recovery and operational responsibilities.

## 9. Initial out-of-scope boundary

- Autonomous control of real equipment.
- Replacing PLC, SCADA, DCS, SIS, historians, ERP or CMMS.
- Bypassing or modifying safety interlocks, emergency stops or safety instrumented functions.
- Unreviewed AI actions that directly alter physical processes.
- Assuming every customer has identical equipment, process topology or operating procedures.

## 10. Requirement traceability

Every requirement entering an implementation milestone should have a unique ID, description, rationale, priority, release target, testable acceptance criteria, dependencies, applicable deployment/industry scope, verification method, status, owner and change history.

The priorities in this baseline are planning proposals, not contractual commitments. Detailed acceptance criteria and release sequencing remain to be completed with product and customer input.
