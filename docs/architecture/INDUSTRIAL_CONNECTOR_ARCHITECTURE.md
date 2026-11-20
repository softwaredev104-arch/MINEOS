# MineOS Industrial Connector Architecture

**Status:** Proposed architecture baseline — implementation and site-specific OT review required  
**Related research:** [Industrial Vendor and API Research Register](../integrations/INDUSTRIAL_VENDOR_API_REGISTRY.md)  
**Date:** 20 November 2026

## 1. Purpose

MineOS must connect to heterogeneous mining and industrial environments without becoming coupled to one SCADA, DCS, historian, equipment OEM or cloud provider.

A customer site may use several vendors simultaneously: for example, one SCADA platform in a processing area, a different control platform underground, a separate historian, OEM fleet telemetry, condition-monitoring sensors and a CMMS/EAM system. Integration is therefore a composable set of replaceable adapters, not one universal SCADA connector.

The connector layer acquires customer-approved data and preserves source provenance. It does not replace control systems or become a new safety authority.

## 2. Architectural flow

~~~text
PLCs / RTUs / SCADA / DCS / SIS read-only views
Historians / MES / CMMS / EAM / LIMS
OEM fleet telematics / condition monitoring / sensors
                         |
             Customer-controlled OT boundary
                         |
         Approved edge gateway / OT DMZ conduit
                         |
       +-----------------+-----------------+
       |                 |                 |
    OPC UA          MQTT / Sparkplug     Vendor API
    adapter             adapter          adapters
       |                 |                 |
       +-----------------+-----------------+
                         |
             Connector runtime / scheduler
     discovery / polling / subscriptions / checkpoints
     retries / buffering / health / schema / rate limits
                         |
              Raw landing + source envelope
                         |
          Validation / mapping / normalization
                         |
         Asset identity + process context + lineage
                         |
          Time-series / event / maintenance services
                         |
                  MineOS AI and PDM
~~~

The preferred topology is a customer-approved edge connector or gateway close to the operational source, with a controlled data path to the MineOS deployment. Whether data moves to customer-hosted MineOS, a dedicated environment or shared SaaS is a customer and deployment decision. Continuous cloud connectivity must not be assumed.

## 3. Connector families

| Connector family | Initial protocols / products | Primary responsibility |
|---|---|---|
| Industrial object access | OPC UA | Browse approved namespaces, read values, subscribe to changes, collect supported events/history. |
| Industrial messaging | MQTT 5, Sparkplug B | Consume authorized telemetry topics and birth/death/state metadata; handle retained messages and sequence semantics. |
| HTTP API | REST, OpenAPI | Poll documented read endpoints, pagination, time-series windows, events, status and hierarchy. |
| Graph query API | GraphQL | Use approved queries, pagination, schema versioning and bounded result sizes. |
| Legacy services | SOAP / WSDL | Support explicitly required legacy systems. |
| Relational / historian | SQL, ODBC, vendor SDK | Read approved views and bounded historian queries using read-only principals. |
| Fleet telemetry | AEMP 2.0 / ISO 15143-3 and OEM APIs | Discover authorized equipment and retrieve available utilization / telemetry data. |
| Batch / export | CSV, JSON and vendor-approved file exports | Import controlled extracts while preserving original file and export metadata. |
| Sensor / condition monitoring | Vendor gateway, IO-Link-derived platform data, vendor APIs | Acquire condition indicators and supported high-frequency data from the system that owns them. |

Connectors must declare what they actually support. OPC UA, REST, GraphQL, MQTT and AEMP do not guarantee identical data types, time semantics, history, alarm support or update frequency.

## 4. Connector contract

Every adapter should implement a common lifecycle and capability contract. The exact programming interface will be defined in implementation specifications; this section describes expected behavior rather than requiring a specific language or framework.

### Required lifecycle capabilities
- Validate configuration and test source connectivity.
- Identify vendor, product, edition, endpoint, schema/API version and connector version.
- Discover supported assets, equipment hierarchy, tags, measurements and event resources where available.
- Expose an explicit capability declaration.
- Read approved current values and/or historical windows.
- Subscribe to streams or events where supported.
- Maintain durable checkpoints for polling cursors, timestamps, offsets or sequence numbers.
- Report connector health, last successful read, source latency, errors, rate-limit state and data gaps.
- Support controlled restart, retry, backfill and graceful shutdown.

### Optional capabilities
- Read alarm and event history.
- Read historian aggregates or interpolated values.
- Read OEM maintenance/fleet records.
- Read sensor waveform or spectral data.
- Read CMMS work orders and completed work events.
- Read equipment metadata, process topology and engineering unit definitions.

A connector must not claim an optional capability merely because the protocol supports it in theory. The source product and configured endpoint must expose it.

### Capability declaration

Each configured connector should declare fields equivalent to:

~~~json
{
  "connector_id": "site-a-adroit-edge-01",
  "vendor": "Adroit Technologies",
  "product": "Adroit Edge Gateway",
  "product_version": "customer-verified-version",
  "connector_version": "0.1.0",
  "protocol": "opc_ua",
  "api_or_schema_version": "customer-verified",
  "capabilities": {
    "browse_assets": true,
    "read_current_values": true,
    "subscribe_values": true,
    "read_history": false,
    "read_alarms_events": false,
    "read_maintenance": false,
    "write_control": false
  }
}
~~~

These values are illustrative configuration metadata, not a real vendor payload. Capability flags must be established by an integration test against the actual source.

## 5. Acquisition modes

A connector may use one or more of these patterns:

1. **Subscription / stream:** OPC UA subscriptions or MQTT topics where the source supports and the customer approves them.
2. **Scheduled polling:** REST, GraphQL, ODBC or source-specific reads at a configured interval.
3. **Historical backfill:** Bounded time-window reads with checkpointing and duplicate protection.
4. **Event delivery:** Source alarms, events or webhooks where documented.
5. **Batch exchange:** Customer-approved scheduled exports for systems without an acceptable online interface.

For each path, define sampling and polling frequency from the use case and the source's supported limits. Do not poll faster than the source, licence or vendor terms permit. Prefer subscriptions or incremental cursors when the product supports them.

Every connector must implement:
- Pagination and server-side result limits.
- Exponential backoff with jitter for transient errors and HTTP 429 responses.
- Retry limits and dead-letter / quarantine handling for persistent invalid records.
- Durable checkpoints and idempotent ingestion.
- Clock-skew and late-arrival handling.
- Bounded query windows and request timeouts.
- Source health and data-freshness indicators.
- A manual, auditable backfill operation.

## 6. Canonical source envelope

Raw readings should be retained with their source identity before canonical mapping. Normalized records should include at least:

| Field | Meaning |
|---|---|
| tenant_id | Customer/tenant security scope, resolved before data is exposed. |
| site_id / facility_id | Mine and facility context, when mapped. |
| process_area_id / process_unit_id | Process context, when known. |
| asset_id | Canonical MineOS asset identity, when mapped. |
| source_system_id | Stable identity for the originating vendor system. |
| source_asset_id | Original source equipment identifier / path. |
| source_point_id | Original tag, node, measurement or API resource identifier. |
| measurement_code | Canonical measurement concept, separate from vendor tag naming. |
| event_time | Source measurement/event timestamp. |
| ingest_time | Time MineOS received the record. |
| value | Original value and type. |
| engineering_unit | Original source unit and canonical conversion metadata where applied. |
| quality | Original quality/status and MineOS normalized quality. |
| source_timezone | Time-zone context supplied by the source, if known. |
| operating_state | Running, stopped, idle, startup, maintenance or source-specific state where available. |
| connector_id / version | Adapter provenance. |
| source_schema_version | Source payload or interface version. |
| lineage_id | Traceable ingestion / transformation reference. |

The complete data contract may add sample period, aggregation method, uncertainty, counter semantics, calibration status, data owner, confidentiality class, retention class, configuration version and tags.

Do not discard the original tag path, source timestamp, quality status or unit after mapping.

### Quality states

The canonical quality model must distinguish at minimum:
- Good / source-confirmed.
- Uncertain / questionable.
- Bad / invalid.
- Missing / not received.
- Stale / older than configured freshness threshold.
- Substituted / interpolated / calculated.
- Unknown / source did not provide quality.

A stale or missing value must not be silently converted into a valid zero. Interpolated, aggregated and derived values must be marked as such.

## 7. Asset and tag mapping

Source identifiers are not global identifiers. The same tag name can exist on different devices or systems.

Mapping workflow:
1. Discover source hierarchy and point metadata where supported.
2. Resolve the source equipment against a canonical MineOS asset using an explicit mapping.
3. Link source tag/node/resource to a canonical measurement concept.
4. Capture unit, scaling, data type, range, sample rate and quality semantics.
5. Assign process and equipment context through the versioned process configuration.
6. Validate the mapping against customer/site engineering documentation or an authorized reviewer.
7. Version every mapping change with author, approval, effective time and reason.

Do not automatically merge two assets because their names are similar. Preserve multiple source bindings and effective-dated mapping history.

## 8. Security and OT deployment boundaries

### Required security controls
- Integrate only through customer-approved network paths and OT security architecture.
- Prefer an OT DMZ or approved edge gateway between control networks and enterprise/MineOS environments.
- Use least-privilege service identities, API scopes, read-only database users and certificate-based trust where supported.
- Store credentials in the deployment's approved secret manager / credential vault; never in source code, committed configuration, notebooks, sample data or logs.
- Encrypt communication in transit where the product and deployment support it.
- Rotate/revoke credentials and certificates through documented operating procedures.
- Restrict connector egress, destination hosts, ports and topic/path scopes.
- Record connector administration, configuration changes, access attempts, ingestion health and privileged actions.
- Separate tenant credentials, queues, buffers, caches and data access.
- Validate source identity and certificate trust; do not disable certificate validation to make a connection work.

### Read-only boundary
The initial MineOS industrial connector contract has no equipment-control write capability.

- Do not write setpoints, commands, PLC registers, DCS parameters, controller logic, SIS configuration, interlocks or emergency-stop functions.
- For an API with write-capable methods, allowlist approved GET/read operations and block POST, PUT, PATCH, DELETE and control methods unless a separate, explicitly approved non-control workflow is specified.
- For OPC UA, configure read-only identities/roles and explicit node allowlists. Do not expose methods or writable nodes to MineOS.
- For SQL/ODBC, use read-only principals and approved views; prohibit arbitrary write statements and unbounded queries.
- Treat alarm acknowledgement and work-order creation as separate workflow capabilities, not implicit parts of telemetry connectivity.
- Any future write/supervisory interface requires a separate product decision, hazard analysis, OT cybersecurity assessment, independent validation, customer authorization and change-management process.

## 9. Vendor-specific implementation notes

| Product family | Adapter approach | Important caveat |
|---|---|---|
| Ignition | Gateway OpenAPI and/or OPC UA | OpenAPI is dynamically generated from installed modules; use its local specification and read-only route allowlist. |
| AVEVA PI | PI Web API / approved PI interfaces | PI Web API can manipulate data; MineOS must scope read operations and respect historian limits. |
| Emerson DeltaV Edge | Edge REST API or OPC UA | Available namespace depends on Edge subscriptions/configuration. |
| Adroit Edge | OPC UA Gateway or HTTP/MQTT microservice | Customer configures the gateway's connections and publishers. |
| Siemens Insights Hub | OpenAPI / AsyncAPI-based services | Tenant, service entitlement, region and access scopes apply. |
| Siemens Senseye | GraphQL / approved machine-data interfaces | External PdM service integration; honor ingestion frequency and supported vibration workflows. |
| Proficy Historian | Version-specific API, SQL/ODBC and/or MQTT path | Confirm the exact installed historian version and licensed API. |
| Geo SCADA Expert | Vendor-supported Python/C# client/API or supported protocol | Python Driver requires Geo SCADA Expert 2025 or later. |
| FactoryTalk Optix | OPC UA | Read only from explicitly published, authorized nodes. |
| ABB Genix | Customer-configured Knowledge Services Hub APIs | Obtain tenant/deployment-specific API catalogue and schemas. |
| ifm moneo | REST API | PAT permissions and documented endpoint rate limits apply. |
| Cat / John Deere | ISO 15143-3 / AEMP 2.0 APIs | Organization, equipment subscription and OEM access are prerequisites. |

The authoritative, current vendor findings and source links are maintained in the [Industrial Vendor and API Research Register](../integrations/INDUSTRIAL_VENDOR_API_REGISTRY.md).

## 10. Resilience and operational behavior

Connector runtime must handle:
- Site WAN / cloud outage and edge-to-platform outage.
- Source server restart and endpoint failover.
- Expired token, revoked certificate and credential rotation.
- Rate limits, API schema change and source version upgrade.
- Delayed, duplicate, out-of-order and missing measurements.
- Store-and-forward queue pressure and disk exhaustion.
- Timestamp drift, daylight-saving transitions and site timezone configuration.
- Partial source outage where one area works and another fails.

The connector must make data gaps visible. It must not fabricate continuity or silently replace unavailable data with estimates.

Buffering and retention limits must be configurable per customer/site and data classification. Define what happens when a buffer is full before deploying it.

## 11. Connector test and release requirements

Every connector requires:
- Contract tests using official vendor schemas / OpenAPI / AsyncAPI / WSDL where available.
- A simulator or deterministic fixture for repeatable development and CI.
- An approved test instance before customer-site certification.
- Authentication, authorization and denied-access tests.
- Read-only tests proving no control writes are possible.
- Pagination, rate-limit, timeout, retry, restart and checkpoint tests.
- Unit, timezone, quality-state, duplicate and late-arrival tests.
- Tenant/site isolation tests.
- Throughput and backpressure tests at an agreed safe rate.
- Evidence that all source payloads retain provenance.
- A documented support matrix including product version, tested capabilities and known limitations.

A simulator pass establishes connector behavior against the simulator contract. It does not prove interoperability with a live vendor installation.

## 12. Open implementation decisions

- Select the initial edge packaging/runtime and its supported customer deployment models.
- Select the first durable message/queue and time-series persistence implementation based on workload and on-premises constraints.
- Define connector configuration storage, secrets integration and certificate lifecycle.
- Choose the first supported OPC UA security profiles and subscription strategy.
- Define MQTT broker support and Sparkplug B version/profile scope.
- Define the minimum canonical source envelope and quality-state mapping.
- Confirm the first pilot site, asset classes, source vendors and available sample data.
- Define buffering, retention, recovery objectives, throughput and freshness targets.
