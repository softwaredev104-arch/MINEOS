# MineOS Reference Architecture

**Status:** Proposed reference architecture — review required

## 1. Architectural position

MineOS is a vendor-neutral intelligence and integration layer above existing industrial control, operational and enterprise systems. It complements rather than replaces customer systems of record and control.

Conceptual flow:

1. **Existing systems:** PLC, SCADA, DCS, SIS, historian, MES, CMMS, ERP and laboratory/LIMS systems.
2. **Industrial connectivity:** edge gateway, protocol adapters, API connectors and store-and-forward.
3. **Ingestion and data platform:** validation, normalization, time-series, events, context and lineage.
4. **Domain and application services:** organizations, sites, facilities, assets, processes and workflows.
5. **Operational applications and MineOS AI:** monitoring, analytics, anomaly detection, forecasting, equipment health and recommendations.
6. **User experience and APIs:** dashboards, web/mobile clients, external APIs and notifications.

Identity, tenant isolation, authorization, audit, observability, configuration, data governance and security apply across all layers.

## 2. Architecture layers

### Industrial systems and connectors
- Integrate with customer systems through approved protocols and APIs.
- Keep protocol-specific logic in adapters rather than domain services.
- Use read-oriented data acquisition as the initial default.
- Validate source identity, timestamps, units, quality and schema.
- Support edge buffering and store-and-forward where connectivity is unreliable.
- Connector credentials and network paths must follow customer OT security policy.
- Support heterogeneous systems in the same site, including vendor SCADA/DCS, historians, condition-monitoring platforms, OEM fleet telemetry and CMMS/EAM systems.
- Declare connector capabilities explicitly; do not assume every source exposes subscriptions, alarms, history, asset hierarchy or the same sampling frequency.

Potential technologies include OPC UA, MQTT 5 / Sparkplug B, REST / OpenAPI, GraphQL, SQL / ODBC, SOAP / WSDL, AEMP 2.0 / ISO 15143-3 and controlled file exchange. Product-specific SDKs or interfaces may be added behind replaceable adapters. The connector implementation order and evidence are maintained in the [Industrial Vendor and API Research Register](../integrations/INDUSTRIAL_VENDOR_API_REGISTRY.md).

See the [Industrial Connector Architecture](INDUSTRIAL_CONNECTOR_ARCHITECTURE.md) for adapter contracts, source envelopes, read-only controls, OT boundaries, resilience and connector testing.

### Ingestion and data platform
- Separate raw/landing data from normalized and curated data.
- Preserve original values and source metadata.
- Normalize timestamps, units, identifiers and quality states.
- Support telemetry, events, alarms, state changes, production records and contextual records.
- Track schema versions, lineage, late arrivals, duplicates and missing data.
- Design partitioning and retention around tenant, site, time and data classification.
- Distinguish source event time from MineOS ingestion time.
- Preserve raw source quality and identify stale, missing, uncertain, interpolated, aggregated and derived values.
- Retain asset/tag mapping versions and source provenance across transformations.

### Domain services
Core domain concepts should not depend on a specific cloud provider or deployment topology. Services own organization, site, facility, process, asset, user, operational event, recommendation and audit semantics.

### AI and decision services
AI services consume governed, contextualized data. Model inference, explanation, recommendation generation, approval and action records are separate concepts. A model prediction is not an instruction to control equipment.

PDM must join condition measurements and operating context with maintenance outcomes where available. Fixed-plant and mobile-fleet data paths may share asset and maintenance services but should not be forced into one universal feature schema. See [Predictive Maintenance Data and Model Strategy](../ai/PREDICTIVE_MAINTENANCE_DATA_AND_MODEL_STRATEGY.md).

### User experience and APIs
Expose versioned APIs and role-scoped experiences. Site dashboards use site-local operational context; group dashboards aggregate only data the user is authorized to see.

## 3. Multi-tenancy and organization isolation

Conceptual hierarchy:

- Platform
  - Tenant/customer organization
    - Optional business unit/operating group
      - Site/mine/industrial complex
        - Mine, processing plant, coke plant, coal preparation plant or other facility
          - Process area
            - Process unit/stage
              - Equipment/assets
                - Tags/measurements

The hierarchy is configurable; not every customer uses every level. Shared utilities, assets and process relationships may require explicit cross-hierarchy relationships.

Shared SaaS requires tenant-aware authorization and isolation across databases, object storage, search indexes, caches, queues, telemetry, background jobs, analytics and AI retrieval. Dedicated deployments may use isolated infrastructure while retaining compatible APIs and domain semantics.

Cross-tenant access is prohibited. Cross-site aggregation is allowed only within the same tenant and authorized scope.

## 4. Deployment patterns

### Shared multi-tenant SaaS
Shared platform services with enforced tenant isolation, tenant-level configuration, access policies, retention and residency controls.

### Dedicated customer deployment
An isolated application and data environment for one customer, aligned with customer network, identity and operational policies.

### On-premises
Customer-controlled infrastructure and network boundaries, local integration services and data persistence as required, with documented installation, upgrade, backup, monitoring and recovery.

### Hybrid
Workloads and data may be split between customer premises/edge and cloud. Synchronization, buffering, data residency and failure behavior must be explicit. Continuous cloud connectivity must not be assumed.

## 5. Resilience and edge behavior

Define behavior for loss of connectivity, delayed telemetry, duplicated events, clock skew, edge storage exhaustion, connector restart and recovery. Critical ingestion paths should buffer safely and report data gaps rather than silently invent continuity.

Connector polling, streaming and backfill must respect source rate limits, licensing, history retention and customer-approved sampling. Implement durable checkpoints, idempotent ingestion, bounded backfill windows and exponential backoff.

## 6. Architecture constraints

- No direct dependence on a single industrial vendor.
- No hardcoded assumption that all sites use the same process route.
- No direct PLC/SIS control in the initial product boundary.
- No tenant data leakage through AI prompts, embeddings, caches or observability systems.
- External integrations must be authenticated, authorized, observable and auditable.
- Prefer modular services and clear contracts; service decomposition and technology choices remain subject to implementation evaluation.
- A publicly readable API document does not provide authorization to connect to a mine or use customer data.
- For write-capable APIs, enforce allowlisted read operations; use read-only database principals and OPC UA roles/node allowlists.
- Connector credentials and certificates must be managed outside source code and ordinary logs.

## 7. Industrial connector design

Each connector is a bounded adapter with:
- Vendor, product, edition/version, endpoint and protocol identity.
- Connector and source schema/API version.
- Explicit capabilities for asset discovery, current values, subscriptions, history, alarms/events, maintenance records and other optional data.
- Authentication, authorization and credential-rotation requirements.
- Polling/streaming schedule, limits, checkpoints and backfill policy.
- Source timestamp, ingestion timestamp, original unit, quality and source identifiers.
- Health, freshness, data-gap and error reporting.
- Contract tests and a documented source-version support matrix.

Where possible, place the connector at a customer-approved edge gateway or OT DMZ boundary. Avoid inbound access to control networks from external MineOS services. Prefer customer-approved outbound data flows and source-to-edge publishing. The final network design remains subject to the mine's OT security architecture.

The initial connector scope is read-oriented. Do not use MineOS to write setpoints, controller parameters, PLC registers, DCS commands, SIS configuration, interlocks, trips or emergency-stop functions.

## 8. Heterogeneous integration and customer-controlled data destinations

A single mine, plant or industrial site may contain many operational areas, each using different equipment, vendors, control systems, protocols, historians and enterprise applications. MineOS must integrate with this heterogeneous environment rather than assume one standardized technology stack.

- Treat each integration as a bounded, replaceable adapter or connector. Protocol-specific behavior must not leak into the core domain model.
- Support multiple simultaneous source systems within the same site, facility, process area or equipment context.
- Maintain source-system identity and provenance when information from different systems is normalized and correlated.
- Distinguish the authoritative source of an operational record from any MineOS copy, normalized representation, cache, feature, event, report or AI output.
- Customers remain in control of their operational source data and applicable retention policies. MineOS may persist selected ingested copies and derived artifacts when configured and authorized; it is not required to become the sole or permanent system of record.
- Provide outbound delivery connectors for customer-controlled servers and storage destinations. Delivery must be authenticated, encrypted where supported, observable, retryable and auditable.
- Support data-class-specific routing and retention so customers can decide which information remains in MineOS and which is delivered to or retained in their own infrastructure.
- Treat Microsoft Graph as a potential enterprise integration surface for Microsoft 365 destinations and workflows (for example, SharePoint, OneDrive or Teams scenarios). Exact services, scopes, permissions and use cases must be validated before implementation. Microsoft Graph is not an industrial telemetry historian or a substitute for source control systems.
- Keep report generation separate from report delivery. A generated report may be viewed in MineOS, downloaded, or delivered to an authorized external destination according to customer configuration.

### 8.1 Data-flow responsibilities

1. **Source systems:** remain authoritative for the operational records they originate.
2. **MineOS ingestion:** acquires data, validates it, preserves source metadata and contextualizes it.
3. **MineOS processing:** may temporarily buffer and, when configured, persist normalized data and derived intelligence needed for product functions.
4. **Customer destinations:** may receive selected source copies, curated datasets, reports and derived outputs under customer-defined policy.
5. **Governance:** defines data ownership, permitted processing, retention, residency, export, deletion and secondary use for each deployment/customer agreement.

The architecture must not assume every customer permits the same data to be retained or sent to the same destination.
