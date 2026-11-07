# Business Expense Request and Approval

> **Domain:** Finance operations, procurement, ERP  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

Expense requests can bypass budget ownership, split purchases to avoid approval limits, or be reimbursed without sufficient evidence and duplicate checks.

## 2. Objective and scope

**Objective:** Route expense commitments and reimbursements through documented authority, budget, evidence, and payment controls.

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
| Requester | Submits purpose, amount, supplier, and evidence |
| Budget owner | Confirms business need and budget availability |
| Approver | Approves within delegated authority |
| Finance reviewer | Checks policy, tax evidence, and duplicate claims |
| Accounts payable | Schedules and records payment |

## 4. Trigger, preconditions, and postconditions

**Trigger:** An employee or authorized requester submits an expense or purchase request for approval.

**Preconditions**
- Requester, legal entity, department/cost center, budget period, and expense category are identifiable.
- Approval thresholds and delegation rules have an effective version and currency basis.
- Required receipts, invoice, business purpose, and vendor details are specified by category.
- Self-approval is blocked where segregation-of-duties policy prohibits it.
- Duplicate submission and budget reservation behavior are defined.

**Postconditions**
- Business object has an explicit final or pending status.
- Material decisions, external references, and exceptions are traceable.
- Related financial, inventory, customer, or access records are synchronized or visibly pending.

## 5. Business process view

This flow describes the human and organizational process, independent of a specific application architecture.

```mermaid
flowchart TD
    A([Expense or purchase request]) --> B[Capture amount, category, cost center, payee, and evidence]
    B --> C[Validate budget and policy eligibility]
    C --> D{Eligible and within budget?}
    D -->|No| X[Return for revision or reject with reason]
    D -->|Yes| E[Determine approval route and authority]
    E --> F[Obtain approval from independent authorized approver]
    F --> G{Approved?}
    G -->|No| X
    G -->|Yes| H[Finance validates invoice, tax, duplicate, and payee]
    H --> I{Finance checks pass?}
    I -->|No| J[Place on hold and request correction]
    J --> H
    I -->|Yes| K[Execute payment through approved channel]
    K --> L{Payment confirmed?}
    L -->|No or unknown| M[Reconcile provider status before retry]
    M --> K
    L -->|Yes| N[Post settlement and archive approval evidence]
    N --> O([Close request])
    X --> O
```

## 6. System interaction view

The sequence models expense submission, evidence and duplicate checks, budget validation, delegation-of-authority routing, reapproval after material change, and accounts-payable handoff.

```mermaid
sequenceDiagram
    autonumber
    actor Requester
    participant Workflow as Expense Workflow
    participant Budget as Budget Service
    participant Approver
    participant Finance
    participant Bank as Payment Provider
    participant Ledger
    participant Audit
    Requester->>Workflow: Submit request, category, amount, and evidence
    Workflow->>Budget: Validate budget and cost center
    Budget-->>Workflow: Availability and policy result
    Workflow->>Workflow: Determine approval route and segregation of duties
    alt Ineligible or over budget
        Workflow-->>Requester: Return for revision or reject with reason
    else Eligible
        Workflow->>Approver: Request approval at configured authority level
        Approver-->>Workflow: Approve, reject, or request changes
        alt Approved
            Workflow->>Finance: Validate invoice, tax, duplicate, and payee evidence
            Finance->>Bank: Execute authorized payment instruction
            Bank-->>Finance: Payment result and reference
            Finance->>Ledger: Post payable settlement or reimbursement
            Ledger-->>Finance: Posting reference
            Workflow->>Audit: Store approvals, evidence, and payment references
        else Rejected or returned
            Workflow->>Audit: Record decision and reason
        end
    end
```

## 7. Business rules

| ID | Rule |
|---|---|
| BR-001 | Approval thresholds and roles come from a version-controlled delegation-of-authority matrix. |
| BR-002 | Requesters cannot approve their own expense or reimbursement. |
| BR-003 | Related transactions are evaluated for split-purchase avoidance. |
| BR-004 | Budget availability is checked at the correct cost center and period. |
| BR-005 | Receipts, invoices, and business purpose are mandatory according to category and policy. |
| BR-006 | Duplicate detection considers supplier, invoice number, amount, date, and currency. |
| BR-007 | Material changes to amount, supplier, or cost center after approval require reapproval. |
| BR-008 | Payment release and accounting posting are traceable to the approved request. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| ExpenseRequest | request_id, requester_id, category, amount, currency, cost_center, purpose |
| BudgetCheck | period, cost_center, available_amount, checked_at |
| Approval | request_id, approver_id, authority_version, decision, reason |
| Evidence | document_ref, supplier, invoice_no, invoice_date, amount, hash |
| Payable | payable_id, request_id, due_date, payment_status |
| Payment | payment_ref, amount, paid_at, bank_reference, status |

Use stable identifiers, explicit timestamps/time zones, currency and unit definitions where relevant, and versioned policy/rule references. Financial values must use integer minor units or fixed-precision decimal types, not binary floating-point arithmetic.

## 9. State model

The state names and transitions below describe the proposed lifecycle for this workflow. Confirm guards, role permissions, timeout transitions, and terminal-state behavior with the process owner and implementation team before production use.

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> SUBMITTED
    SUBMITTED --> VALIDATING
    VALIDATING --> REVISION_REQUIRED: Missing data or budget issue
    REVISION_REQUIRED --> SUBMITTED
    VALIDATING --> APPROVAL_PENDING: Eligible
    APPROVAL_PENDING --> APPROVED: Authorized approver accepts
    APPROVAL_PENDING --> REJECTED: Approver declines
    APPROVAL_PENDING --> REVISION_REQUIRED: Changes requested
    APPROVED --> FINANCE_REVIEW
    FINANCE_REVIEW --> PAYMENT_PENDING: Evidence valid
    FINANCE_REVIEW --> FINANCE_HOLD: Duplicate or compliance issue
    FINANCE_HOLD --> FINANCE_REVIEW: Issue resolved
    PAYMENT_PENDING --> PAID: Provider confirms
    PAYMENT_PENDING --> PAYMENT_EXCEPTION: Failure or unknown result
    PAYMENT_EXCEPTION --> PAYMENT_PENDING: Reconciled retry
    PAID --> RECONCILED
    REJECTED --> [*]
    RECONCILED --> [*]
```

## 10. Exceptions and recovery

| Scenario | Expected behavior and recovery |
|---|---|
| Budget unavailable | Return for revision or route to authorized budget exception approval. |
| Missing or invalid receipt | Place claim on hold and request corrected evidence. |
| Potential duplicate claim | Block payment pending finance review. |
| Approver unavailable | Use a formally designated delegate; do not bypass authority. |
| Material request change | Invalidate prior approval and restart required approval steps. |
| Payment rejected | Keep payable open and reconcile rejection reason. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given a requester submits their own claim for approval, when approval is attempted, then self-approval is rejected.
- **AC-02:** Given amount exceeds the current approver limit, when routed, then it moves to a higher authorized approver.
- **AC-03:** Given an approved request changes supplier or amount materially, when saved, then reapproval is required.
- **AC-04:** Given a duplicate invoice is detected, when payment is scheduled, then it is blocked for finance review.
- **AC-05:** Given related requests are submitted separately, when approval risk is evaluated, then related transactions are assessed for split-purchase avoidance.
- **AC-06:** Given a request is submitted, when budget availability is checked, then the correct cost center and budget period are used.
- **AC-07:** Given an expense category requires evidence, when a receipt, invoice, or business purpose is missing, then submission is blocked or routed to exception review.
- **AC-08:** Given payment is released, when accounting posting occurs, then both actions reference the approved request and retain audit evidence.

## 13. Operational metrics

- Approval cycle time by amount/category
- Claims returned for missing evidence
- Duplicate claims prevented
- Budget variance by cost center
- Payment rejection and overdue payable rate

- **Approval cycle time:** final decision timestamp minus submission timestamp; report median and P90 by approval path.
- **Policy exception rate:** requests approved with documented policy exception ÷ submitted requests.
- **Budget variance:** actual approved spend minus budget allocation, shown by cost center and period.
- **Rework rate:** requests returned for missing/incorrect information ÷ submitted requests. Review monthly with budget owners.

Assign a named metric owner, reporting window, and baseline before setting a target. These are measurement definitions, not promised improvements.

## 14. Assumptions and open decisions

- Approval limits, budget ownership, allowable categories, tax evidence, and retention rules are company-specific.
- Purchase commitment and employee reimbursement may require separate routes.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Business rule | Acceptance criterion | Verification focus |
|---|---|---|
| BR-001 | AC-02 | it moves to a higher authorized approver |
| BR-002 | AC-01 | self-approval is rejected |
| BR-003 | AC-05 | related transactions are assessed for split-purchase avoidance |
| BR-004 | AC-06 | the correct cost center and budget period are used |
| BR-005 | AC-07 | submission is blocked or routed to exception review |
| BR-006 | AC-04 | it is blocked for finance review |
| BR-007 | AC-03 | reapproval is required |
| BR-008 | AC-08 | both actions reference the approved request and retain audit evidence |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
