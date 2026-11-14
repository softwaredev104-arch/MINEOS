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

Potential technologies include OPC UA, MQTT, REST APIs, database/file exchange and vendor-specific interfaces. The first supported connector set remains an open decision.

### Ingestion and data platform
- Separate raw/landing data from normalized and curated data.
- Preserve original values and source metadata.
- Normalize timestamps, units, identifiers and quality states.
- Support telemetry, events, alarms, state changes, production records and contextual records.
- Track schema versions, lineage, late arrivals, duplicates and missing data.
- Design partitioning and retention around tenant, site, time and data classification.

### Domain services
Core domain concepts should not depend on a specific cloud provider or deployment topology. Services own organization, site, facility, process, asset, user, operational event, recommendation and audit semantics.

### AI and decision services
AI services consume governed, contextualized data. Model inference, explanation, recommendation generation, approval and action records are separate concepts. A model prediction is not an instruction to control equipment.

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

## 6. Architecture constraints

- No direct dependence on a single industrial vendor.
- No hardcoded assumption that all sites use the same process route.
- No direct PLC/SIS control in the initial product boundary.
- No tenant data leakage through AI prompts, embeddings, caches or observability systems.
- External integrations must be authenticated, authorized, observable and auditable.
- Prefer modular services and clear contracts; service decomposition and technology choices remain subject to implementation evaluation.
