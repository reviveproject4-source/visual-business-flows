# Low-Stock Detection and Replenishment

> **Domain:** Retail inventory, procurement, supply chain  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

Replenishment based only on on-hand quantity can create duplicate purchase orders, stockouts, and excess inventory when open orders, reservations, lead times, or supplier constraints are ignored.

## 2. Objective and scope

**Objective:** Calculate replenishment need using available inventory and outstanding supply, then route purchase proposals through purchasing controls.

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
| Inventory service | Maintains stock ledger and availability |
| Store or warehouse operator | Reports count and receiving exceptions |
| Buyer | Reviews demand and supplier options |
| Approver | Approves purchase commitments within authority |
| Supplier | Confirms and fulfills purchase order |

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
    S1[Record sales, adjustments, reservations, and receipt movements]
    S2[Calculate available-to-promise and inventory position per SKU/location]
    S3[Compare inventory position with reorder point and lead-time demand]
    S4[Check open purchase orders and transfers before proposing replenishment]
    S5[Create purchase requisition with suggested quantity and supplier]
    S6[Validate budget, minimum order quantity, pack size, and approval authority]
    S7[Approve and issue purchase order]
    S8[Track supplier acknowledgement and expected arrival]
    S9[Receive goods and reconcile quantity and quality]
    S10[Recalculate inventory position and close replenishment task]
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> S8
    S8 --> S9
    S9 --> S10
    S10 --> End([Outcome])
```

## 6. System interaction view

This logical sequence shows system responsibilities. Adapt participants and messages to the selected architecture and provider contract.

```mermaid
sequenceDiagram
    autonumber
    participant Inventory as Inventory Service
    participant Planner as Replenishment Service
    participant Buyer
    participant Approver
    participant Supplier
    participant Receiving
    participant Audit
    Inventory->>Planner: Publish stock movement or scheduled snapshot
    Planner->>Planner: Calculate inventory position and lead-time demand
    Planner->>Planner: Check open POs, transfers, MOQ, and pack size
    alt No replenishment required
        Planner->>Audit: Record evaluation and no-action reason
    else Replenishment proposed
        Planner->>Buyer: Present requisition proposal and assumptions
        Buyer->>Planner: Confirm supplier and requested quantity
        Planner->>Approver: Request approval within configured authority
        alt Rejected or returned
            Approver-->>Planner: Reject or request revision with reason
            Planner->>Audit: Record decision
        else Approved
            Planner->>Supplier: Issue purchase order with unique reference
            Supplier-->>Planner: Acknowledge or reject PO
            Supplier->>Receiving: Deliver goods
            Receiving->>Inventory: Post accepted quantity and quarantine discrepancies
            Inventory-->>Receiving: Receipt and stock ledger reference
            Planner->>Audit: Record PO, receipt, and replenishment outcome
        end
    end
```

## 7. Business rules

| ID | Rule |
|---|---|
| BR-001 | Inventory position must account for on-hand, reserved, allocated, and confirmed inbound quantities. |
| BR-002 | Reorder points and safety stock are business parameters, not universal constants. |
| BR-003 | A new requisition must check open POs and transfers to avoid duplicate replenishment. |
| BR-004 | Suggested quantity must respect pack size, minimum order quantity, and supplier constraints. |
| BR-005 | Purchase order creation and supplier transmission must be idempotent. |
| BR-006 | Only authorized buyers may approve or transmit commitments within configured limits. |
| BR-007 | Receiving discrepancies must remain open against the PO until resolved. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| InventoryPosition | sku, location, on_hand, reserved, allocated, inbound, available, calculated_at |
| ReplenishmentPolicy | sku, location, reorder_point, safety_stock, lead_time, review_period |
| PurchaseRequisition | request_id, suggested_qty, supplier_id, reason, status |
| PurchaseOrder | po_id, lines, approved_by, supplier_ack, expected_date, status |
| Receipt | receipt_id, po_id, received_qty, rejected_qty, discrepancy |
| Supplier | supplier_id, lead_time, MOQ, pack_multiple, status |

Use stable identifiers, explicit timestamps/time zones, currency and unit definitions where relevant, and versioned policy/rule references. Financial values must use integer minor units or fixed-precision decimal types, not binary floating-point arithmetic.

## 9. State model

The following is a lifecycle scaffold. Rename, add, or remove states to reflect the domain and define permitted transitions in the implementation specification.

```mermaid
stateDiagram-v2
    [*] --> MONITORING
    MONITORING --> EVALUATING: Stock event or scheduled run
    EVALUATING --> NO_ACTION: Above reorder threshold
    EVALUATING --> PROPOSAL_READY: Replenishment needed
    PROPOSAL_READY --> REVIEW_PENDING
    REVIEW_PENDING --> REVISION_REQUIRED: Returned for changes
    REVISION_REQUIRED --> REVIEW_PENDING
    REVIEW_PENDING --> REJECTED: Rejected
    REVIEW_PENDING --> PO_ISSUED: Approved
    PO_ISSUED --> SUPPLIER_ACK_PENDING
    SUPPLIER_ACK_PENDING --> ACKNOWLEDGED: Supplier confirms
    SUPPLIER_ACK_PENDING --> SUPPLIER_EXCEPTION: Rejected or no response
    SUPPLIER_EXCEPTION --> SUPPLIER_ACK_PENDING: Resolved
    ACKNOWLEDGED --> PARTIALLY_RECEIVED
    PARTIALLY_RECEIVED --> RECEIVED: Remaining quantity resolved
    ACKNOWLEDGED --> RECEIVED: Full receipt
    RECEIVED --> RECONCILED
    NO_ACTION --> [*]
    REJECTED --> [*]
    RECONCILED --> [*]
```

## 10. Exceptions and recovery

| Scenario | Expected behavior and recovery |
|---|---|
| Stock ledger is stale | Flag calculation as provisional and request synchronization or count. |
| Existing PO is delayed | Escalate supplier risk; do not blindly create a duplicate order. |
| Supplier discontinues SKU | Route to approved substitute or assortment decision. |
| Budget or approval rejected | Keep requisition in REJECTED or NEEDS_REVISION with reason. |
| Partial delivery | Receive actual quantity and retain remaining PO balance as open/backordered. |
| Quality failure | Quarantine rejected units and initiate supplier claim. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given an open PO already covers replenishment need, when the reorder job runs, then it does not create a duplicate requisition.
- **AC-02:** Given inventory data is stale, when reorder calculation runs, then the proposal is marked provisional or blocked.
- **AC-03:** Given a PO is partially received, when receipt is posted, then received units update stock and the outstanding balance remains open.
- **AC-04:** Given a requisition exceeds an approver's authority, when submitted, then it routes to the next authorized level.

## 13. Operational metrics

- Stockout frequency and duration
- Reorder proposal acceptance rate
- Duplicate PO prevention count
- Supplier on-time/in-full delivery
- Inventory days on hand and excess stock value

Define numerator, denominator, source system, measurement window, owner, and baseline before setting targets. Metrics are measurement proposals, not promised improvements.

## 14. Assumptions and open decisions

- Demand forecast, safety stock, reorder point, and supplier lead time require business calibration.
- The reference does not automatically transmit POs without configured approval.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Rule group | Acceptance criteria | Implementation evidence |
|---|---|---|
| BR-001 to BR-007 | AC-01 to AC-04 | Unit/integration tests, audit events, and process-owner sign-off |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
