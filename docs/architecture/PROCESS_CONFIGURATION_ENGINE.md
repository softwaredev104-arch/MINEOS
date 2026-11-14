# MineOS Process Configuration Engine

**Status:** Proposed architecture specification — review required  
**Version:** 0.1

## 1. Purpose

The Process Configuration Engine allows each customer to model the physical and operational structure of its sites and facilities using governed configuration rather than bespoke application code.

MineOS must support facilities with materially different process routes while reusing common platform capabilities for assets, telemetry, events, analytics, AI, workflows and reporting.

Illustrative examples:
- An open-pit mine feeding a copper concentrator.
- An underground mine feeding a different beneficiation route.
- A coal preparation plant with its own material streams and product qualities.
- A coke production facility with ovens, gas/by-product handling, utilities and downstream process areas.

These examples demonstrate required flexibility. They are not claims that a complete industry template is already specified.

## 2. Design principles

1. Configuration before customization: common facility differences should be expressed as configuration, not customer-specific forks.
2. Templates are optional: templates accelerate onboarding but never constrain a facility to a universal process route.
3. Explicit semantics: process units, assets, flows, measurements and KPIs have typed meaning, not just display labels.
4. Versioned configuration: every meaningful configuration change is reviewable, attributable and effective-dated.
5. Tenant and facility isolation: configuration, data and derived results remain within authorized scopes.
6. Runtime safety: configuration describes and contextualizes operations; it does not create authority to bypass control-system protections.
7. Extensible domain: new process types and verticals can be introduced without changing the meaning of existing records.
8. AI consumes context: AI features use the approved configuration version and its mappings, not assumptions inferred from names alone.

## 3. Conceptual model

| Concept | Meaning |
|---|---|
| Organization / tenant | Customer security, policy and commercial boundary. |
| Site | Geographic/operational location with timezone, calendars and local settings. |
| Facility | A mine, concentrator, coal preparation plant, coke plant or other operational facility. |
| Process area | A logical or physical subdivision of a facility. |
| Process unit | A configured process function or stage, such as crushing, flotation, screening or coking. |
| Process graph | Versioned directed graph of process units and typed connections. |
| Flow / stream | Material, energy, water, gas, utility or other defined transfer between process boundaries. |
| Asset | Physical equipment or infrastructure performing a role. |
| Asset role | The function an asset performs in a process context; one asset may have multiple relationships/roles. |
| Tag / measurement point | A source-linked signal or measured variable with unit and quality semantics. |
| Operating mode | A named, governed operating context such as startup, normal operation, shutdown or maintenance, where applicable. |
| KPI definition | Versioned calculation with formula, scope, unit, aggregation and data dependencies. |
| Configuration version | Immutable published snapshot of facility/process configuration with lifecycle metadata. |

The organization/site/facility hierarchy is not itself the process graph. A facility can contain multiple process graphs, shared utility systems and cross-area connections.

## 4. Process graph

### 4.1 Nodes and edges

A process graph consists of typed nodes and typed edges.

Node types may include process unit/stage, equipment or equipment group, storage/stockpile/tank/silo, source or sink boundary, measurement/observation point, and utility system or shared service.

Edges represent explicit relationships such as material feed/product transfer, energy transfer, water transfer, gas/utility transfer, information/measurement association, equipment performs process function, and asset belongs to/is located in a process area.

Do not encode all relationships as a generic parent-child tree. Containment, process flow, asset function and measurement association have different meanings and validation rules.

### 4.2 Graph constraints

The engine should validate:
- Node and edge types are supported by the relevant schema version.
- Referenced nodes and assets exist within the same authorized tenant/facility scope, except explicitly modelled shared infrastructure.
- Edge endpoints are compatible with the edge type.
- Units and material/flow semantics are compatible where defined.
- Required process boundaries and stream attributes are present for the selected template or validation profile.
- Cycles are permitted only where the process model explicitly supports recirculation/feedback; otherwise they are reported.
- Parallel, optional, bypass and recirculating routes can be represented explicitly.
- A graph can be incomplete during draft configuration, but cannot be published if it violates its selected publication rules.

A validator must distinguish errors that block publication from warnings that require acknowledgement. The applicable validation profile must be visible.

## 5. Streams and process quantities

A flow/stream may describe stream identity and type, source and destination process boundaries, material or utility identity, quantity/rate and engineering unit, composition/grade/quality/state where applicable, temperature/pressure/moisture or other relevant properties, measurement sources and calculated estimates, validity interval and data-quality/provenance metadata.

The model must not require every stream to have every property. Property sets depend on stream type and facility configuration.

Material, energy and water balance calculations should be configurable and domain-reviewed. The engine must not silently infer missing measurements or claim a balance is valid when boundaries, units, timing or data coverage are inadequate.

## 6. Asset and tag binding

A process configuration associates existing asset records with process functions. It must not duplicate the asset registry as a second source of truth.

Tag bindings should include source system and stable source identifier, canonical tag/measurement identity, associated asset/process node/stream, measurement meaning and engineering unit, data type and expected sampling/aggregation behavior where known, quality mapping and timestamp semantics, and effective interval/mapping version.

Support aliases and source-specific naming differences. A tag name alone is not a reliable semantic identifier.

## 7. Templates and reusable configuration

Templates should be versioned, tenant-safe starting points. They may define suggested process stages, common asset roles, stream types, tag/measurement concepts, KPI definitions and validation rules.

Template application must:
- Create a facility-specific configuration copy or governed derivation.
- Preserve template source/version.
- Allow local additions, removals and modifications.
- Avoid silently changing existing facility configurations when a template is updated.
- Support controlled template upgrades with a diff and explicit approval.

Templates should be organized by industry, facility type, process route and version. They must not assume two plants with the same label have identical topology or instrumentation.

## 8. Configuration lifecycle

Recommended lifecycle:
1. **Draft:** editable configuration; incomplete graphs allowed.
2. **Validated:** validation has run; errors and warnings are recorded.
3. **In review:** submitted for designated technical/operational review.
4. **Approved:** authorized reviewer accepts the configuration.
5. **Published:** immutable version becomes available to runtime consumers.
6. **Superseded:** a newer version replaces it for a later effective period.
7. **Retired:** no longer used for new operational interpretation.

Each transition records actor/service identity, timestamp, version, validation report, comments and relevant approvals. Published versions are immutable; changes create a new version.

Support effective-from/effective-to semantics so historical telemetry and AI results can be interpreted against the configuration valid at the time. Corrections to historical configuration must be explicit, audited and trigger an impact assessment for affected analytics/models.

## 9. Runtime behavior and downstream consumers

The configuration engine exposes versioned APIs/events or equivalent contracts to asset/facility services, industrial data normalization and tag mapping, operational dashboards, KPI calculation/reporting, AI feature engineering/inference/explanation, simulation/digital-twin services, and recommendation/approval workflows.

Every derived result that materially depends on process configuration should identify the configuration version used. If a configuration is invalid, stale or unavailable, the consuming service must follow an explicit fallback policy and surface the limitation.

## 10. Authorization and governance

- Draft editing, technical review, approval and publication are separately permissionable actions.
- Scope permissions by tenant, site and facility.
- Prevent one tenant from reading or modifying another tenant's templates or configurations.
- Shared platform templates may be distributed read-only; customer-specific variants remain tenant-scoped.
- Audit changes to topology, asset bindings, tag mappings, operating modes, limits and KPI formulas.
- High-impact configuration changes require review appropriate to the customer's governance process.

## 11. Example configurations (illustrative only)

### Example A: mineral processing facility

ROM/stockpile → crushing → screening → grinding → flotation → thickening/dewatering → concentrate and tailings.

A real facility may omit stages, add parallel trains, use a different separation process or have recirculating streams. This is not a mandatory copper-plant schema.

### Example B: coal preparation facility

Run-of-mine coal receipt/storage → sizing/crushing → separation/washing → dewatering → product and reject handling.

The actual process route, quality measurements and equipment vary by site and product specification.

### Example C: coke production facility

Coal handling/blending → preparation → coke ovens/carbonization → coke handling/screening, with separately modelled gas, by-product, emissions and utility systems where applicable.

This is a high-level illustration, not an engineering process design. Detailed process definitions require qualified domain review.

## 12. Acceptance scenarios

1. Different facilities: two facilities with different process graphs can be configured and published independently without requiring identical stages or equipment.
2. Parallel route: a process with parallel trains and a shared downstream stage is represented without flattening it into a false linear sequence.
3. Recirculation: a recycle stream is permitted only when selected process rules explicitly allow it and the cycle is recorded.
4. Template customization: a facility administrator can derive a local configuration, alter stages/mappings and retain the source template/version.
5. Version history: a published configuration change creates a new version; historical results continue to reference the version used at calculation time.
6. Tag mapping: source tags with different vendor naming conventions can map to the same canonical measurement concept without losing source identity.
7. Tenant isolation: a user from Tenant A cannot list, read, modify or publish Tenant B configuration, even by guessing identifiers.
8. Invalid publication: a graph with a blocking edge-type or endpoint error cannot be published; the validator returns a machine-readable error with node/edge references.
9. KPI reproducibility: a KPI result identifies its formula version, configuration version, input data window, unit and quality limitations.
10. AI provenance: an AI inference that uses facility topology or tag mappings identifies the configuration version and relevant feature provenance.

## 13. Proposed API surface

Candidate resource boundaries, not finalized endpoint contracts:
- Facility configuration lifecycle and version retrieval.
- Process graph nodes and edges.
- Stream and flow definitions.
- Asset/process-role associations.
- Tag/measurement bindings.
- Template catalog, template derivation and upgrade diff.
- Validation reports.
- KPI definitions and versioned calculation metadata.

API schemas, authorization policy, concurrency control, pagination, event contracts and error formats must be specified before implementation.

## 14. Open design questions

- Should process graphs use a property graph store, relational tables with typed edges, or a hybrid? Decide from query patterns, consistency needs and operational scale; do not choose a graph database merely because topology is graph-shaped.
- Which configuration schema and validation engine should be used?
- Which process templates are required for the first customer pilots?
- Which process quantities and domain ontologies should be standardized first?
- How are shared utilities and cross-facility flows represented where organizational boundaries differ?
- Which changes require dual approval or formal management-of-change workflows?
- How should effective-dated corrections trigger recomputation of historical KPIs and model features?

## 15. Implementation sequence proposal

1. Define canonical domain entities, IDs, typed relationships and schema versioning.
2. Implement tenant-scoped facility/process configuration CRUD and draft validation.
3. Implement immutable versioning, review/approval and publication lifecycle.
4. Implement asset and tag binding with source provenance.
5. Implement template derivation and controlled upgrade diffs.
6. Integrate configuration versions into ingestion normalization, KPI calculation and AI feature provenance.
7. Add process visualization and customer-facing configuration UX.
8. Expand process-specific validation, balances, simulation and vertical templates with domain experts.

This sequence is a proposal; pilot requirements and integration constraints may change ordering.
