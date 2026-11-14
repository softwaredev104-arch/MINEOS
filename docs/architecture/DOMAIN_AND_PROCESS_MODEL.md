# MineOS Domain and Process Model

**Status:** Proposed domain foundation — review required

## 1. Design objective

Represent multiple organizations, sites and facilities with different industrial processes without forcing them into one universal mine or plant schema.

The domain model distinguishes:
- Organizational structure that owns and governs operations.
- Physical facilities and assets.
- Process topology and material/energy/utility flows.
- Time-series, events and operational records associated with assets and processes.
- Operational meaning of measurements and outcomes.

## 2. Core hierarchy

Tenant/organization → optional operating group → site/complex → facility → process area → process unit/stage → equipment/asset → tags/measurements.

Facility examples include open-pit mine, underground mine, mineral processing/beneficiation plant, coal handling/preparation facility, coke production facility and other industrial process facilities.

This is a conceptual hierarchy, not a mandatory fixed tree. Real facilities may share utilities, assets or process stages. Explicit relationships should represent those cases.

## 3. Facility and industry configuration

A facility should have a configurable type and operating profile. Industry and facility templates are starting configurations, not immutable schemas. New verticals and process types should be introduced through governed metadata/configuration and versioned domain extensions.

## 4. Process topology

Represent process units as nodes and material, energy, water, utility or information transfers as typed relationships/flows where applicable.

A process model should support:
- Inputs and outputs.
- Feed and product streams.
- Intermediate materials and stockpiles.
- Process stages and parallel or optional routes.
- Equipment performing one or more process functions.
- Operating modes and valid state transitions where known.
- Site-specific constraints and KPI definitions.
- Effective dates and version history for topology changes.

Do not assume all facilities have the same process stages or that a named process always has identical instrumentation or operating limits.

## 5. Asset model

Candidate asset categories include mobile equipment, fixed plant equipment, electrical assets, instrumentation, utilities and infrastructure. Asset records may include stable asset ID and source-system identifiers, name/type, manufacturer/model where available, parent/child and process relationships, location, criticality, operational role, telemetry/tag mappings, engineering units, maintenance references and configuration history.

## 6. Measurements and events

Measurements should carry value, event time, ingestion time, source, unit, quality status and relevant asset/process context. Events should distinguish source alarms, operator-entered events, maintenance events, state changes and AI-generated detections.

Never silently treat missing, stale, invalid or substituted values as valid measurements. Preserve quality and provenance through transformations.

## 7. Global and site context

Store canonical timestamps in a consistent unambiguous representation and retain source timezone context when supplied. Configure site-local display timezone, shift calendar, operating day, units, locale and currency separately. Unit conversions must be explicit and traceable.

## 8. KPIs and metrics

KPI definitions should be configurable and versioned, including formula, unit, aggregation window, exclusions, source dependencies and ownership. Examples may include throughput, recovery, availability, utilization, energy intensity, water intensity, downtime and product quality, depending on facility type.

Do not compare KPIs across sites unless definitions, units, boundaries and data quality are sufficiently aligned. Group comparisons should expose differences in definitions and context.

## 9. Data isolation

Every domain object and relationship must be scoped to a tenant. Cross-site relationships must remain within authorized organization boundaries. AI feature generation, retrieval and reporting must preserve the same access scope.


## 10. Process configuration engine

The Process Configuration Engine is the governed mechanism for creating, validating, versioning and publishing facility-specific process models. Its detailed specification is maintained in [PROCESS_CONFIGURATION_ENGINE.md](PROCESS_CONFIGURATION_ENGINE.md).

Key domain constraints:
- A facility may contain multiple process graphs and shared utility systems.
- Process topology is a typed graph, not merely the organizational containment tree.
- Containment, material/energy/water flow, equipment function and measurement association are distinct relationship types.
- Parallel, optional and recirculating routes must be represented explicitly; cycles require applicable process-rule validation.
- Facility templates are versioned starting points that can be customized independently.
- Published configurations are immutable snapshots with effective dates and audit metadata.
- Historical analytics and AI outputs must retain the configuration version used.
- Draft configurations may be incomplete; publication applies a selected validation profile and blocks configured critical errors.

The process configuration engine does not replace the asset registry, industrial control system or safety system. It contextualizes assets and measurements for operational intelligence.

## Heterogeneous operational technology context

A facility may contain multiple process areas and operational systems that perform different tasks and use different equipment manufacturers, protocols, control platforms and historians. The domain model must represent operational areas and process relationships independently of the technology used to monitor or control them.

An asset or measurement may have multiple source-system identities or bindings over time. Preserve source identity, source timestamps, quality semantics and connector provenance rather than treating a vendor tag name as a globally unique domain identity. Integration configuration belongs at the boundary between the canonical domain model and source-specific adapters.

The customer source system remains authoritative for records it originates. MineOS may maintain policy-approved copies and derived records, but those copies must retain lineage to the originating source and must not silently become the authoritative record.
