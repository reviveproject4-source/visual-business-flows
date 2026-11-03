# Third-Party Courier Booking and Delivery Tracking

> **Domain:** Last-mile logistics, marketplace, retail fulfillment  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

Courier assignment and tracking are external dependencies. Repeated booking requests can create duplicate pickups, and unverified callbacks can cause premature delivery completion.

## 2. Objective and scope

**Objective:** Create and track courier jobs using idempotent booking, authenticated status updates, custody evidence, and exception recovery.

**In scope**
- Operational lifecycle from initiation through resolution and recordkeeping.
- Business decisions, system responsibilities, exception handling, and audit evidence.
- Minimum data and acceptance criteria needed for implementation planning.

**Out of scope**
- Organization-specific legal, tax, accounting, labor, or contractual conclusions.
- Fixed thresholds, fees, SLA targets, or financial outcomes not validated by the organization.
- Vendor-specific API contracts unless documented by the selected provider.

## 3. Actors and systems

| Actor / system | Responsibility |
|---|---|
| Merchant application | Requests booking and maintains order/shipment state |
| Dispatch operator | Reviews booking and manages exceptions |
| Courier platform | Assigns driver and emits delivery events |
| Courier driver | Collects and delivers package |
| Recipient | Receives package and confirms handover |

## 4. Trigger, preconditions, and postconditions

**Trigger:** A valid business event or authorized user action initiates the workflow.

**Preconditions**
- Initiating actor or service is authenticated.
- Required master data, policy versions, and reference records are available.
- Requested object is in a state that permits the operation.
- Required permissions and segregation-of-duty controls are configured.

**Postconditions**
- Business object has an explicit final or pending status.
- Material decisions, external references, and exceptions are traceable.
- Related financial, inventory, customer, or access records are synchronized or visibly pending.

## 5. Business process view

This flow describes the human and organizational process, independent of a specific application architecture.

```mermaid
flowchart TD
    Start([Trigger]) --> S1
    S1[Validate package, pickup, drop-off, serviceability, and delivery window]
    S2[Create booking request with merchant shipment reference and idempotency key]
    S3[Receive booking ID and estimated service details]
    S4[Process driver assignment and notify pickup location]
    S5[Verify driver identity and package handover at pickup]
    S6[Track courier status updates and exceptions]
    S7[Capture delivery proof using provider-supported method]
    S8[Reconcile final courier status to merchant shipment and order]
    S9[Handle failed delivery, cancellation, return, or claim]
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> S8
    S8 --> S9
    S9 --> End([Outcome])
```

## 6. System interaction view

This logical sequence shows system responsibilities. Adapt participants and messages to the selected architecture and provider contract.

```mermaid
sequenceDiagram
    autonumber
    actor User as Business actor
    participant App as Business application
    participant Core as Domain service
    participant External as External system
    participant Audit as Audit/event store
    User->>App: Submit request or business event
    App->>Core: Validate identity, scope, and business rules
    Core->>Core: Evaluate state and authorization
    Core->>Audit: Persist decision and correlation reference
    Core->>External: Send authorized request when required
    External-->>Core: Return result or asynchronous event
    Core->>Core: Validate response and apply allowed transition
    Core->>Audit: Record outcome and processing status
    Core-->>App: Return current status and next action
    App-->>User: Show outcome or actionable exception
```

## 7. Business rules

| ID | Rule |
|---|---|
| BR-001 | A shipment has one merchant reference and stable booking idempotency key. |
| BR-002 | Do not create a second booking while the first is unresolved; query provider status first. |
| BR-003 | Driver identity and pickup handover follow merchant/provider controls. |
| BR-004 | Callbacks are authenticated, deduplicated, and checked against valid status transitions. |
| BR-005 | Delivered status requires provider-confirmed proof according to service contract. |
| BR-006 | Customer location and contact details are shared only as necessary for fulfillment. |
| BR-007 | Cancellation fees, redelivery, insurance, and return-to-origin rules must be explicit. |
| BR-008 | Courier completion does not automatically prove customer acceptance for high-risk goods unless policy says so. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| Shipment | shipment_id, order_id, carrier, merchant_reference, status |
| BookingRequest | request_id, idempotency_key, payload_version, response_code |
| CourierBooking | provider_booking_id, tracking_url, service_level, quoted_cost |
| DriverAssignment | driver_id, vehicle_ref, assigned_at, verified_by |
| ShipmentEvent | provider_event_id, event_type, occurred_at, received_at |
| DeliveryProof | proof_type, evidence_ref, recipient_confirmation, captured_at |

Use stable identifiers, explicit timestamps/time zones, currency and unit definitions where relevant, and versioned policy/rule references. Financial values must use integer minor units or fixed-precision decimal types, not binary floating-point arithmetic.

## 9. State model

The following is a lifecycle scaffold. Rename, add, or remove states to reflect the domain and define permitted transitions in the implementation specification.

```mermaid
stateDiagram-v2
    [*] --> REQUESTED
    REQUESTED --> VALIDATING
    VALIDATING --> IN_PROGRESS: Valid
    VALIDATING --> REJECTED: Invalid
    IN_PROGRESS --> AWAITING_REVIEW: Exception or approval required
    AWAITING_REVIEW --> IN_PROGRESS: Approved / retry permitted
    AWAITING_REVIEW --> REJECTED: Declined
    IN_PROGRESS --> COMPLETED: Success conditions met
    REQUESTED --> CANCELLED: Authorized cancellation
    COMPLETED --> [*]
    REJECTED --> [*]
    CANCELLED --> [*]
```

## 10. Exceptions and recovery

| Scenario | Expected behavior and recovery |
|---|---|
| Booking request times out | Query provider by merchant reference before retrying. |
| No driver assigned | Keep shipment in BOOKING_PENDING and retry or route to manual dispatch. |
| Driver identity mismatch | Do not hand over package; escalate and reassign. |
| Pickup scan missing | Record custody exception and obtain documented confirmation. |
| Delivery attempt fails | Record reason and follow recipient contact/redelivery policy. |
| Duplicate or out-of-order callback | Deduplicate and reconcile provider's current shipment state. |
| Provider outage | Keep order ready for dispatch and use approved alternate carrier workflow. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given booking request times out, when retry is initiated, then provider lookup occurs before a second booking is created.
- **AC-02:** Given driver identity does not match provider assignment, when pickup is attempted, then handover is blocked and an exception is recorded.
- **AC-03:** Given a duplicate delivered callback arrives, when processed, then shipment is completed once and audit history is preserved.
- **AC-04:** Given delivery fails, when failure callback is received, then shipment enters a recoverable exception state rather than DELIVERED.

## 13. Operational metrics

- Booking success and driver assignment time
- Pickup and delivery SLA attainment
- Failed delivery rate by reason
- Duplicate booking prevention count
- Courier invoice versus quoted cost variance

Define numerator, denominator, source system, measurement window, owner, and baseline before setting targets. Metrics are measurement proposals, not promised improvements.

## 14. Assumptions and open decisions

- Provider APIs, proof-of-delivery mechanisms, serviceability, insurance, and cancellation rules differ by carrier.
- Tracking links may expose personal data; access and expiry should be controlled.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Rule group | Acceptance criteria | Implementation evidence |
|---|---|---|
| BR-001 to BR-008 | AC-01 to AC-04 | Unit/integration tests, audit events, and process-owner sign-off |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
