# Inter-Branch Stock Transfer and Transit Reconciliation

> **Domain:** Multi-branch retail, distributed inventory, logistics  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

Sending branch, carrier, and receiving branch may report different quantities. Removing stock from origin without tracking transit creates ghost inventory; automatically charging staff or drivers for unexplained shortages creates unsupported liability.

## 2. Objective and scope

**Objective:** Maintain custody and quantity traceability from transfer authorization through dispatch, transit, receipt, discrepancy investigation, and closure.

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
| Origin branch | Requests, picks, packs, and dispatches transfer |
| Origin supervisor | Verifies quantity and handover evidence |
| Carrier / driver | Accepts custody and transports shipment |
| Destination branch | Inspects package and counts received units |
| Inventory control | Investigates discrepancies and approves adjustments |
| Inventory system | Tracks in-transit and branch stock balances |

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
    A([Transfer requested]) --> B[Specify source, destination, SKU, and quantity]
    B --> C[Check source availability and destination need]
    C --> D{Transfer feasible?}
    D -->|No| X[Reject or revise request]
    D -->|Yes| E[Obtain approval under branch authority]
    E --> F{Approved?}
    F -->|No| X
    F -->|Yes| G[Pick and independently verify quantity]
    G --> H[Pack, seal, and record custody identifiers]
    H --> I[Handover shipment and move quantity to in-transit]
    I --> J[Destination checks seal and performs receipt count]
    J --> K{Received quantity matches?}
    K -->|Yes| L[Post accepted quantity to destination stock]
    K -->|No| M[Post accepted units and open variance investigation]
    M --> N{Variance resolved?}
    N -->|No| O[Keep transfer partially received]
    N -->|Yes| P[Reconcile source, in-transit, and destination ledgers]
    L --> P
    O --> N
    P --> Q([Close transfer])
```

## 6. System interaction view

This logical sequence shows system responsibilities. Adapt participants and messages to the selected architecture and provider contract.

```mermaid
sequenceDiagram
    autonumber
    actor Source as Source Branch
    actor Destination as Destination Branch
    participant Transfer
    participant Inventory
    participant Approver
    participant Carrier
    participant Audit
    Source->>Transfer: Request transfer with SKU and quantity
    Transfer->>Inventory: Check source availability and destination need
    Inventory-->>Transfer: Available and reserved quantities
    Transfer->>Approver: Request authorization
    Approver-->>Transfer: Approve or reject
    alt Rejected
        Transfer-->>Source: Return rejection reason
    else Approved
        Transfer->>Inventory: Reserve and pick approved quantity
        Source->>Transfer: Confirm independent count and package seal
        Transfer->>Carrier: Handover shipment and custody evidence
        Carrier-->>Destination: Deliver shipment
        Destination->>Transfer: Record seal condition and blind receipt count
        Transfer->>Inventory: Move accepted units to destination and discrepancies to investigation
        Transfer->>Audit: Record dispatch, custody, receipt, and variance
        Transfer-->>Source: Return transfer reconciliation status
    end
```

## 7. Business rules

| ID | Rule |
|---|---|
| BR-001 | A transfer has a unique ID, source, destination, and approved line quantities. |
| BR-002 | Dispatch reduces origin available stock and creates in-transit balance; it does not increase destination stock. |
| BR-003 | Custody changes only when parties record handover evidence required by policy. |
| BR-004 | Seal IDs and package counts are evidence, not proof by themselves that contents are correct. |
| BR-005 | Destination records actual received quantity independently of dispatched quantity. |
| BR-006 | Shortages, overages, and damage remain discrepancy cases until investigated and approved. |
| BR-007 | No automatic staff, driver, or branch liability may be assigned solely from a quantity variance. |
| BR-008 | Inventory adjustment requires approval, reason code, evidence, and immutable audit history. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| TransferHeader | transfer_id, source_location, destination_location, status, requested_by |
| TransferLine | sku, requested_qty, approved_qty, dispatched_qty, received_qty |
| Package | package_id, seal_id, weight, photo_refs, condition |
| CustodyEvent | transfer_id, from_party, to_party, accepted_at, evidence_ref |
| TransitBalance | transfer_id, sku, quantity, status |
| DiscrepancyCase | case_id, transfer_id, sku, variance_qty, reason, investigator, decision |
| InventoryAdjustment | adjustment_id, sku, location, quantity, approval_id, reason |

Use stable identifiers, explicit timestamps/time zones, currency and unit definitions where relevant, and versioned policy/rule references. Financial values must use integer minor units or fixed-precision decimal types, not binary floating-point arithmetic.

## 9. State model

The following is a lifecycle scaffold. Rename, add, or remove states to reflect the domain and define permitted transitions in the implementation specification.

```mermaid
stateDiagram-v2
    [*] --> REQUESTED
    REQUESTED --> STOCK_CHECK
    STOCK_CHECK --> REJECTED: Insufficient stock or invalid destination
    STOCK_CHECK --> APPROVAL_PENDING: Feasible
    APPROVAL_PENDING --> REJECTED: Declined
    APPROVAL_PENDING --> PICKING: Approved
    PICKING --> DISPATCH_READY: Count and seal verified
    DISPATCH_READY --> IN_TRANSIT: Custody accepted
    IN_TRANSIT --> RECEIVING: Shipment arrives
    RECEIVING --> RECEIVED: Quantity matches
    RECEIVING --> VARIANCE_REVIEW: Shortage, excess, or damage
    VARIANCE_REVIEW --> PARTIALLY_RECEIVED: Accepted quantity posted
    PARTIALLY_RECEIVED --> RECONCILED: Investigation resolved
    RECEIVED --> RECONCILED
    REJECTED --> [*]
    RECONCILED --> [*]
```

## 10. Exceptions and recovery

| Scenario | Expected behavior and recovery |
|---|---|
| Seal broken or mismatched | Photograph and record condition; conduct witnessed opening and count. |
| Quantity short | Receive actual quantity; keep difference in investigation status, not automatic expense assignment. |
| Destination refuses delivery | Retain goods in transit/exception custody and record refusal reason. |
| Carrier scan missing | Escalate custody gap and obtain alternate evidence before closing. |
| System unavailable at handover | Use controlled offline manifest and reconcile both acknowledgements. |
| Transfer cancelled after dispatch | Create return transfer or reversal movement; never delete dispatch history. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given a transfer is dispatched, when inventory is posted, then origin available stock decreases and equal in-transit quantity is created.
- **AC-02:** Given destination receives fewer units than dispatched, when receipt is posted, then actual units enter destination stock and difference remains an open discrepancy.
- **AC-03:** Given a seal is reported damaged, when receipt is recorded, then evidence and witnessed inspection are required before closure.
- **AC-04:** Given a variance is unresolved, when adjustment is requested, then automatic liability assignment is prohibited and authorized review is required.

## 13. Operational metrics

- Transfer lead time by lane
- Dispatch-to-receipt quantity variance rate
- Transit inventory age
- Discrepancy resolution time
- Transfers with complete custody evidence

Define numerator, denominator, source system, measurement window, owner, and baseline before setting targets. Metrics are measurement proposals, not promised improvements.

## 14. Assumptions and open decisions

- Custody and carrier liability depend on contract, insurance, local law, and evidence.
- Cycle-count and adjustment approval thresholds must be configured.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Rule group | Acceptance criteria | Implementation evidence |
|---|---|---|
| BR-001 to BR-008 | AC-01 to AC-04 | Unit/integration tests, audit events, and process-owner sign-off |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
