# MineOS Industrial Vendor and API Research Register

**Status:** Research baseline — vendor capabilities and access conditions require deployment-level verification  
**Research snapshot:** 20 November 2026  
**Scope:** South African and international mining, process automation, industrial data, condition monitoring, fleet telematics and maintenance platforms.

This register records publicly discoverable product documentation and integration surfaces relevant to MineOS. It is a research shortlist, not a complete census of every supplier or a statement that a product is installed at any particular mine.

## 1. How to read API availability

“Public documentation” does not mean an unauthenticated or free production API. A publicly readable developer guide may describe an API that still requires a paid product, installed gateway, customer tenant, organization approval, subscription, dealer relationship, credentials or vendor support.

| Evidence class | Meaning | MineOS treatment |
|---|---|---|
| **A — Public developer documentation** | Official developer/API documentation is accessible publicly. | Build a connector spike against the documented contract; verify product entitlement and customer authorization. |
| **B — Product-documented interface** | The vendor documents an API, SDK, gateway or protocol as part of a product. | Connector depends on installed version, licensed modules and site configuration. |
| **C — Standard protocol / gateway** | The product communicates through an industry protocol or an approved edge gateway. | Implement the standard adapter; the customer must configure and authorize the source. |
| **D — Access validation required** | The platform is known, but a current official public API contract was not verified in this research. | Do not advertise an API connector until vendor/customer documentation is obtained. |

No entry below authorizes MineOS to access a customer network, production system or machine. The mine/customer must approve the system, data classes, access method and credentials.

## 2. Executive findings

1. **SCADA is not the only integration target.** Historians, OEM fleet platforms, condition-monitoring products and CMMS/EAM systems often provide more useful historical, equipment-context and maintenance-outcome data for predictive maintenance.
2. **OPC UA is a foundational cross-vendor interface.** It should be a first-class MineOS adapter alongside MQTT/Sparkplug B and authenticated HTTP APIs.
3. **Publicly documented APIs are often authenticated and licensed.** “Public” describes documentation availability, not production data availability or free access.
4. **AEMP 2.0 / ISO 15143-3 is a valuable fleet standard.** It can reduce OEM-specific work where a fleet provider exposes the standard, but available fields depend on machine telematics hardware, subscription and OEM authorization.
5. **MineOS must normalize data without erasing source identity, event time, quality, unit, equipment context or lineage.**
6. **MineOS PDM requires maintenance outcomes as well as sensor data.** Work orders, failure modes, repairs, replaced components and verified outcomes are essential for model evaluation and learning.

## 3. South African vendor and integration ecosystem

South Africa has local SCADA, industrial data, instrumentation, condition-monitoring and systems-integration suppliers. They should not all be labelled API vendors: some develop a software platform, some provide gateways or sensors, and others implement third-party platforms.

| Supplier | Role / relevant offering | Public integration evidence found | MineOS position |
|---|---|---|---|
| **Adroit Technologies** | South African SCADA software; Adroit SCADA, MAPS and Adroit Edge Gateway | Official Edge Gateway documents HTTP, MQTT and OPC UA microservices and gateway modes. | High-priority local connector discovery. Start with customer-configured Edge Gateway publishing or OPC UA; verify installed product/version. |
| **Industrial Data Xchange (IDX)** | Industrial data integration, communications and Nexus data platform | Public product material describes industrial data / gateway / protocol capabilities; a general unrestricted public REST API contract was not established. | Engage for protocol, historian and edge architecture discovery; classify exact Nexus interfaces only after receiving the deployed-version specification. |
| **4Sight OT Automation** | Industrial automation and operational technology integration | Integrator ecosystem; no single universal 4Sight SCADA API verified. | Potential integration / delivery partner, not a single connector target. |
| **Iritron** | Industrial control systems engineering and integration | Works across third-party industrial control ecosystems; no universal Iritron data API verified. | Potential implementation and site-integration partner. |
| **Proconics** | Process automation, control and engineering | Integrator / engineering services; no universal public telemetry API verified. | Partner and systems-discovery lead. |
| **Martec** | Condition monitoring and reliability technology in Southern Africa | Product portfolio and supplier representation; individual manufacturer APIs must be evaluated separately. | Local route to vibration, ultrasound, thermography and reliability expertise; connector depends on the selected device/platform. |
| **Omniflex** | Remote telemetry, monitoring and industrial communications | Product-specific communications interfaces; no universal public API verified in this review. | Evaluate for remote monitoring and gateway use cases. |
| **Dueltron / syTechnologies / AMS Haden** | Local automation, instrumentation and integration suppliers | Public evidence is insufficient to claim a common vendor API. | Maintain as supplier/partner leads; validate exact equipment, software and data interface during discovery. |

### South African source links

- [Adroit Edge Gateway](https://adroitscada.com/adroit-edge-gateway/)
- [Adroit technical document downloads](https://adroitscada.com/document-download-page/)
- [IDX](https://idx.co.za/)
- [4Sight OT Automation](https://www.4sightot.co.za/)
- [Iritron](https://iritron.co.za/)
- [Martec](https://www.martec.co.za/)

**Evidence note:** Adroit is the clearest locally developed SCADA/edge integration target in this initial register because its official materials explicitly identify HTTP, MQTT and OPC UA microservices. The other local firms should be treated as platform, engineering, instrumentation or partner leads until their exact product-level interface is documented.

## 4. International SCADA, DCS, historian and industrial software vendors

| Vendor / product family | Publicly documented interface or capability | Access and implementation considerations | Evidence |
|---|---|---|---|
| **Inductive Automation — Ignition** | Gateway HTTP API with dynamically generated OpenAPI documentation; OPC UA | OpenAPI routes depend on the installed Gateway version and modules. Most endpoints require a Gateway API token. Some routes can mutate Gateway configuration; MineOS must use a read-only allowlist and must not expose configuration-management operations. | [Ignition 8.3 Gateway API documentation](https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi) |
| **AVEVA — PI System / PI Web API** | REST API for PI Data Archive time-series data and PI Asset Framework / Event Frame data; AF SDK and PI SQL interfaces also exist | Installed PI infrastructure, configured identity/authentication and licensing are required. PI Web API supports read and manipulate operations; MineOS must restrict itself to approved read operations. | [PI Web API getting started](https://docs.aveva.com/bundle/pi-web-api-reference/page/help/getting-started.html) · [AVEVA developer technologies](https://www.aveva.com/en/products/aveva-pi-system-developer-technologies/) |
| **Siemens — Insights Hub** | HTTP APIs with OpenAPI specifications; messaging APIs with AsyncAPI specifications | Requires an authorized Insights Hub tenant, service entitlement, regional endpoint and appropriate token/access scopes. | [Insights Hub API index](https://developer.siemens.com/insights-hub/docs/apis/index.html) |
| **Siemens — Senseye PdM** | GraphQL API; machine-data and work-order integration; ingestion options include API, MQTT, email and S3/Azure Blob; historian integration | Customer account and access token required. Work Events can represent completed maintenance activity; this is important for PDM feedback. Senseye documents a 1 Hz maximum for an individual time-series measure, so high-frequency vibration must be processed or supplied through supported vibration workflows. | [Senseye developer overview](https://developer.siemens.com/senseye/overview.html) · [GraphQL API](https://developer.siemens.com/senseye/introduction/graphql.html) · [machine data](https://developer.siemens.com/senseye/machine/index.html) · [work orders](https://developer.siemens.com/senseye/workorders/index.html) |
| **GE Vernova — Proficy Historian / iFIX / CIMPLICITY** | Historian data access and API capabilities; product-family interfaces include REST API, SQL/ODBC and MQTT/Sparkplug-related integrations depending on edition | Exact routes, supported operations, authentication and throughput depend on installed product/version and customer documentation. Do not assume every Proficy installation exposes the same REST schema. | [Proficy product documentation](https://www.gevernova.com/software/product-documentation) · [Historian product information](https://www.gevernova.com/software/products/proficy/historian) |
| **Emerson — DeltaV Edge Environment** | Documented REST API and OPC UA server for hierarchy, runtime parameters, history, alarms/events and batch events | Local Edge Node endpoint with authentication token; address space and data visibility depend on subscriptions/configuration. Use the official sample/client code as a connector reference. | [DeltaV Edge GitHub](https://github.com/EmersonDeltaV/deltav-edge) · [REST API guide](https://github.com/EmersonDeltaV/deltav-edge/blob/main/developer-guide/rest-api/rest-api.md) · [OPC UA guide](https://github.com/EmersonDeltaV/deltav-edge/blob/main/developer-guide/opc-ua/opc-ua.md) |
| **Schneider Electric — EcoStruxure Geo SCADA Expert** | Geo SCADA APIs, Python Driver/API from version 2025 onwards, C# examples and Sparkplug B-related sample repositories | The Python interface is version-dependent and requires compatible Geo SCADA 2025-or-later servers/clients. It is not evidence of a generic public REST API. Use vendor-supported client interfaces and approved deployment patterns. | [Python Driver Guide](https://product-help.schneider-electric.com/RemoteOperations/Geo%20SCADA%20Expert%202025/Content/PythonGuide/Welcome.htm) · [Geo SCADA GitHub](https://github.com/GeoSCADA) |
| **Rockwell Automation — FactoryTalk Optix** | OPC UA client and server capabilities; published nodes and event access | OPC UA access is configured through the Optix project/runtime and security permissions. Do not assume every FactoryTalk product shares the Optix interface. | [FactoryTalk Optix OPC UA documentation](https://www.rockwellautomation.com/en-us/docs/factorytalk-optix/1-00/contents-ditamap/using-the-software/opc-ua.html) |
| **ABB — Ability Genix** | Genix Knowledge Services Hub acts as an API gateway for prebuilt and custom APIs over contextualized industrial/business data | Product, deployment and customer configuration determine available APIs, data domains and access permissions. Treat Genix as an enterprise integration product, not as proof that every ABB 800xA installation exposes the same API. | [Genix architecture](https://new.abb.com/process-automation/genix/genix-architecture) |
| **Adroit Technologies — Adroit Edge Gateway / SCADA** | OPC UA gateway; HTTP, MQTT and OPC UA microservices | Site-configured gateway connections and publishers. This supports controlled data publishing from multiple Adroit systems and sources. | [Adroit Edge Gateway](https://adroitscada.com/adroit-edge-gateway/) · [technical downloads](https://adroitscada.com/document-download-page/) |
| **Trihedral — VTScada** | SOAP Web Services for historical database and application functions; newer VTScada ODBC driver also provides a REST interface | Web Services / Remote Data Access availability is a separately licensed capability. Exact version, driver and permissions must be verified. | [VTScada Web Services](https://www.vtscada.com/web-services/) · [Web Services and XML help](https://www.vtscada.com/help/Content/Scripting/Tasks/pro_WebServices.htm) |
| **Honeywell — Experion** | Product-specific industrial connectivity, including OPC UA and other supported industrial interfaces | Verify Experion release, licensed options, topology, access policy and official interface specification for each site. | [Honeywell](https://process.honeywell.com/) |
| **Yokogawa — CENTUM / Exaquantum / Exaopc** | Product-specific OPC and historian interfaces | Confirm exact OPC interface, data licensing, server/client role and available history with the customer/vendor. | [Yokogawa](https://www.yokogawa.com/) |
| **PTC — Kepware KEPServerEX** | Industrial protocol server and OPC interfaces for connecting heterogeneous devices and applications | Kepware is commonly a gateway/driver layer, not a universal cloud API. The supported driver and tags are configured per installation. | [Kepware](https://www.ptc.com/en/products/kepware) |

### Other industrial automation suppliers to retain in the global compatibility register

- Mitsubishi Electric — MELSEC PLC and industrial automation ecosystem.
- Omron — Sysmac PLC and automation systems.
- Beckhoff — TwinCAT / ADS and OPC UA.
- Moxa — industrial networking and edge connectivity.
- Phoenix Contact — PLCnext and industrial connectivity.
- Bosch Rexroth — ctrlX AUTOMATION.
- Festo — automation and IO-Link ecosystems.

For these suppliers, MineOS should first test the applicable standard interface (often OPC UA, MQTT, Modbus or a gateway) rather than assume a single common REST API. Product, firmware, licensing and configured communication modules must be checked.

## 5. Condition monitoring and predictive-maintenance platforms

These products may already calculate machine-health indicators or predictive-maintenance cases. MineOS should integrate with them where customers have deployed and licensed them, rather than automatically replace their proprietary analytics.

| Vendor / product | Documented integration surface | Data / value to MineOS | Access notes |
|---|---|---|---|
| **ifm — moneo** | Public API documentation for Platform, Track & Trace and OEE APIs; bearer Personal Access Tokens | Historical process data, topology, tickets, OEE and traceability | PAT inherits its user's permissions. Documented limit is 100 requests/minute per endpoint per moneo instance; implement backoff and rate-limit handling. [API docs](https://api-docs.moneo.ifm/) |
| **Schaeffler — OPTIME** | OPTIME Customer REST API | KPIs, raw data, metadata, resources and alarms for condition monitoring | Cloud/customer access and authorization required. [Developer use case](https://developer.schaeffler.com/use-cases/schaeffler-optime) |
| **Siemens — Senseye PdM** | GraphQL API and machine-data/work-order integrations | Cases, asset hierarchy, time-series/vibration ingestion and maintenance Work Events | Authenticated customer access. See the Senseye links in Section 4. |
| **SKF — Enlight Centre** | Public product/API support documentation is available | Potential equipment hierarchy, condition monitoring and maintenance information | Obtain the specific tenant/API version, authentication method and product entitlement before committing a connector. [Enlight Centre support](https://enlight-support.zendesk.com/hc/en-us/categories/360002436413-Enlight-Centre) |
| **ABB — Ability Genix** | Knowledge Services Hub / product API gateway | Contextualized industrial data and analytics services | Deployment-specific API catalogue and access scopes required. |
| **Augury — Machine Health** | Vendor/partner integration routes are advertised; a complete unrestricted self-service API contract was not verified | Machine-health cases, diagnostics and maintenance workflow integration | Obtain current partner/API specifications and commercial access confirmation. [Augury](https://www.augury.com/) |
| **Emerson — AMS / machinery health portfolio** | Product-specific condition monitoring and asset-management integration | Vibration and machinery health evidence | Verify current product edition, data export and supported interface. [Emerson](https://www.emerson.com/) |
| **Baker Hughes — Bently Nevada System 1** | Product-specific machinery condition monitoring and data interfaces | Rotating equipment vibration, diagnostics and machinery health | Validate System 1 release, data access method and customer entitlement. [Bently Nevada](https://www.bakerhughes.com/bently-nevada) |

For local condition monitoring, Martec and other South African specialists may supply or service products from these manufacturers. The connector must target the actual deployed sensor platform or gateway, not the distributor name.

## 6. Mining fleet and mobile-equipment OEMs

Mobile fleet telemetry is a separate integration family from plant SCADA.

| OEM / platform | Publicly evidenced interface | Data and limitations | Status |
|---|---|---|---|
| **Caterpillar — Cat Digital Marketplace / Product Link** | ISO 15143-3 (AEMP 2.0) API | Fleet snapshot and individual-equipment time-series views. Credentials and organization/customer/dealer access are required. Data availability depends on Product Link hardware, machine reporting and subscription. | Public API documentation; access is customer/dealer controlled. |
| **John Deere — Operations Center** | ISO 15143-3 (AEMP 2.0) API | Header, location, operating hours, idle hours, fuel, load count, payload and distance where available. App profile, organization and account setup are required; not every machine provides every field. | Public developer documentation; customer authorization required. |
| **Komatsu — KOMTRAX / Modular Mining** | OEM telematics and fleet ecosystem | Fleet health, machine utilization and operational context may be relevant. A universal unrestricted public API was not verified. | Vendor/customer integration validation required. |
| **Sandvik — Digital Mining Solutions** | Product- and deployment-specific equipment/fleet integrations | Underground and surface equipment data, depending on installed systems and agreements. | Vendor/customer integration validation required. |
| **Epiroc — 6th Sense** | Product- and deployment-specific digital mining integrations | Machine data, fleet and operational context, depending on supported equipment and subscription. | Vendor/customer integration validation required. |
| **Hitachi Construction Machinery — ConSite** | Product-specific telematics service | Equipment health and utilization information. | API and data-export entitlement must be confirmed. |
| **Liebherr — LiDAT** | Product-specific fleet telematics service | Machine position, performance and operating data, depending on machine and subscription. | API and data-export entitlement must be confirmed. |
| **Volvo CE — CareTrack** | Product-specific fleet telematics service | Fleet location, machine use and service-related information, depending on equipment and access. | API and data-export entitlement must be confirmed. |

Official starting points:
- [Cat Digital Marketplace documentation](https://digital.cat.com/documentation)
- [Cat ISO 15143-3 (AEMP 2.0) API](https://digital.cat.com/apis/products/prod/iso-15143-3-aemp-20-api)
- [Cat Digital Marketplace API catalogue and access FAQ](https://digital.cat.com/api-catalog-overview)
- [John Deere ISO 15143-3 developer documentation](https://developer.deere.com/dev-docs/aemp)

**AEMP caveat:** ISO 15143-3 is not a universal raw machine-bus interface. It provides a standardized fleet/telematics exchange where the OEM/provider supports it. It does not guarantee high-frequency vibration waveforms, internal CAN/J1939 signals, every machine field or free access. MineOS must retain an OEM-specific adapter where a provider's implementation or extensions differ.

## 7. CMMS / EAM / ERP systems — maintenance outcome integrations

Predictive maintenance requires outcomes, not just sensor streams. The following enterprise systems should be considered for work orders, notifications, asset identities, failure codes, repairs and maintenance costs.

| Platform | API / interface family | Intended MineOS use | Access notes |
|---|---|---|---|
| **IBM Maximo Manage** | REST / JSON API | Asset master data, locations, work orders, work logs, service requests and maintenance status | Requires authorized Maximo environment, API permissions and tenant/version validation. [IBM Maximo documentation](https://www.ibm.com/docs/en/masv-and-l/maximo-manage) |
| **SAP S/4HANA Asset Management** | SAP OData / released APIs | Equipment, functional locations, maintenance notifications and maintenance orders | Use released APIs and customer-specific SAP authorization; avoid direct database reads. [SAP API Business Hub](https://api.sap.com/) |
| **Infor EAM / CloudSuite** | Infor REST / ION API ecosystem | Assets, work orders and maintenance outcomes | Verify the deployed Infor product/version, API catalogue, tenant and OAuth scopes. [Infor documentation](https://docs.infor.com/) |

## 8. Industrial standards and transport interfaces

These are not all equivalent to a REST API. They are protocol or information-model standards that make adapters reusable across vendors.

| Standard / interface | Role | MineOS connector treatment |
|---|---|---|
| **OPC UA** | Secure industrial client/server information model, discovery, subscriptions, events and methods; supported capabilities vary by server | First-class adapter. Use certificates, trust lists, endpoint security policies and per-node read allowlists. |
| **MQTT 5** | Lightweight publish/subscribe messaging | First-class message-broker adapter with TLS, client identity, topic ACLs and bounded subscriptions. |
| **Sparkplug B** | MQTT topic/payload/state conventions for industrial edge applications | Support as a structured industrial telemetry profile on top of MQTT. |
| **Modbus TCP / RTU** | Register-based industrial communications | Support only through an approved site gateway or isolated OT segment. Define register maps, signedness, scale and byte order explicitly. |
| **DNP3** | Common remote-telemetry and utility protocol | Candidate adapter for remote infrastructure and electrical/utility telemetry; require site-approved secure deployment. |
| **IEC 61850 / IEC 60870-5** | Electrical substation and power-system automation communications | Future electrical and power-distribution integration family; do not assume these are present at every site. |
| **REST / OpenAPI** | HTTP resource APIs with machine-readable contract | Generic versioned connector with token/OAuth/certificate support, rate limiting, pagination and checkpoints. |
| **GraphQL** | Typed query/mutation interface | Schema-aware connector with pagination, query limits, token handling and explicit query allowlists. |
| **SQL / ODBC** | Relational and historian query access | Read-only database principals, approved views, query timeouts and bounded result windows. |
| **SOAP / WSDL** | Legacy enterprise and industrial web-service interface | Compatibility adapter where required by a customer deployment. |
| **AEMP 2.0 / ISO 15143-3** | Standardized fleet telematics data exchange | Fleet-specific adapter with OEM-specific authentication, field mapping and subscription checks. |
| **File / batch exchange** | Scheduled export/import, including CSV, JSON and approved vendor exports | Controlled fallback for systems without an approved network API; preserve original file and ingestion provenance. |

Reference links:
- [OPC Foundation — OPC UA](https://opcfoundation.org/about/opc-technologies/opc-ua/)
- [MQTT](https://mqtt.org/)
- [Eclipse Sparkplug](https://sparkplug.eclipse.org/)
- [Modbus specifications](https://www.modbus.org/specs.php)
- [DNP Users Group](https://www.dnp.org/)

## 9. MineOS vendor access classification and connector backlog

The register supports a staged connector strategy:

### Initial proof-of-connectivity shortlist
1. OPC UA reference server and a customer-approved OPC UA gateway.
2. MQTT 5 / Sparkplug B broker.
3. Ignition Gateway OpenAPI (read-only subset).
4. AVEVA PI Web API (read-only subset).
5. Emerson DeltaV Edge REST / OPC UA.
6. Adroit Edge Gateway HTTP / MQTT / OPC UA.
7. ifm moneo REST API.
8. Siemens Senseye GraphQL API (as an external PdM platform integration).
9. Cat ISO 15143-3 API and John Deere AEMP API (fleet track).

This is a research/test order, not a claim that any vendor has been selected by a customer or that MineOS has already implemented these adapters.

### Subsequent validation queue
- GE Vernova Proficy Historian.
- Schneider Geo SCADA Expert 2025+ Python interface.
- Rockwell FactoryTalk Optix OPC UA.
- ABB Genix Knowledge Services Hub.
- VTScada Web Services.
- Schaeffler OPTIME and SKF Enlight Centre.
- IBM Maximo, SAP Asset Management and Infor.
- Komatsu, Sandvik, Epiroc, Hitachi, Liebherr and Volvo fleet platforms.
- Honeywell and Yokogawa process/historian deployments.

### Required evidence before calling a vendor integration “supported”
For every connector, record:
- Vendor, product, edition, firmware/software version and deployment topology.
- Official interface/documentation URL and date checked.
- Connector protocol, endpoint discovery and API schema/version.
- Authentication and authorization method, scopes, certificate trust and credential rotation.
- Licensing, tenant approval, subscription and contractual conditions.
- Supported data domains, tags, events, asset hierarchy and historical-query semantics.
- Polling limits, event throughput, rate limits, retention and known data latency.
- Source timestamp, ingestion timestamp, time zone and quality semantics.
- Read-only verification, test fixtures, failure handling and observability.
- Vendor support contact / escalation path and customer approval evidence.

## 10. Non-negotiable MineOS integration rules

- Source systems remain authoritative for the records they create.
- Customer authorization is mandatory; a public API document never grants access to a mine.
- The initial integration surface is read-oriented. No connector may issue PLC, DCS, SIS or equipment-control writes.
- For products whose APIs include mutation routes, explicitly allowlist only approved read methods and resources.
- Do not embed customer credentials, certificates or machine secrets in source code, notebooks, logs or sample data.
- Respect API licences, rate limits, data residency, retention, vendor terms and customer agreements.
- Retain original source identifiers, timestamps, units, quality and lineage when normalizing data.
- A missing interface is not evidence that the system is impossible to integrate; ask for an approved gateway, historian export, vendor adapter or controlled batch feed.
- Do not describe a vendor as a supported MineOS connector until a versioned implementation has passed integration tests against an approved instance or faithful simulator.

## 11. Research limitations and next validation work

This register is a public-documentation research baseline as of 20 November 2026. It does not establish:
- Which products are installed at any specific mine.
- Whether a mine has enabled or licensed an optional API.
- Whether the mine's OEM contract permits third-party ingestion.
- Whether the API is accessible from the customer's OT network or cloud tenant.
- Whether a particular data point is enabled, sampled at a useful frequency or retained for the period required by PDM.
- Whether a public product page is the complete technical contract for the installed release.

Next research work should obtain current vendor interface specifications and customer-approved sample payloads for the chosen pilot equipment and historian products, then update this register with exact versions, authentication, schemas and test status.
