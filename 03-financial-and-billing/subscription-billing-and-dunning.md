# Subscription Billing, Failed Payment Recovery, and Dunning

> **Domain:** SaaS subscriptions, memberships, recurring billing  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

Recurring charges can fail because of expired credentials, insufficient funds, provider outages, or authentication requirements. Immediate access termination and unsafe retries can harm customers or create duplicate charges.

## 2. Objective and scope

**Objective:** Manage invoices and payment retries with idempotency, clear communication, configurable grace policy, and accurate access states.

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
| Billing scheduler | Creates invoices and schedules collection attempts |
| Payment provider | Authorizes, declines, or reports payment status |
| Subscriber | Updates payment method or resolves balance |
| Subscription service | Maintains entitlement and access state |
| Finance/support | Handles disputes and unresolved collection cases |

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
    S1[Generate invoice from active subscription and pricing version]
    S2[Submit collection request with stable idempotency key]
    S3[Process provider result and normalize payment state]
    S4[On success, mark invoice paid and extend entitlement]
    S5[On failure, classify retryable versus non-retryable reason]
    S6[Apply configured grace and access policy]
    S7[Notify subscriber with secure payment update route]
    S8[Schedule bounded retry using provider-aware rules]
    S9[Reconcile late success, dispute, refund, or cancellation]
    S10[Close dunning journey when balance is settled or subscription terminates]
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
| BR-001 | Each invoice and collection attempt must have stable unique identifiers. |
| BR-002 | Payment retries use provider-supported idempotency and must not create duplicate charges. |
| BR-003 | Retry schedule, grace period, and access restriction are business policy parameters. |
| BR-004 | Do not retry hard declines, revoked authorization, or non-retryable errors without customer action. |
| BR-005 | Webhook events must be authenticated, deduplicated, and reconciled against provider status. |
| BR-006 | Entitlement state is separate from invoice state and follows documented grace policy. |
| BR-007 | Cancellation and access termination follow contract, notice, and data-retention policy. |
| BR-008 | Payment update links must be short-lived, scoped, and must not expose raw credentials. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| Subscription | subscription_id, customer_id, plan_id, status, current_period_start/end |
| Invoice | invoice_id, pricing_version, amount, currency, due_at, status |
| PaymentAttempt | attempt_id, invoice_id, provider_ref, idempotency_key, failure_code, status |
| Entitlement | customer_id, product_id, access_state, effective_from/to |
| DunningEvent | invoice_id, step, scheduled_at, channel, delivery_status |
| PaymentEvent | provider_event_id, signature_valid, received_at, processed_at |

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
| Provider timeout after charge attempt | Query provider by idempotency key/reference before retrying. |
| Late success after access restriction | Reconcile invoice and restore entitlement according to policy; preserve event chronology. |
| Hard decline or authentication required | Request customer action; do not run blind automatic retries. |
| Duplicate webhook | Deduplicate by provider event ID and preserve one posting. |
| Invoice amount differs after plan change | Apply effective-dated pricing and proration rules; trace the calculation. |
| Refund or chargeback | Create linked reversal/dispute state and update entitlement only under policy. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given collection request times out, when retry logic runs, then provider status is checked before another charge is attempted.
- **AC-02:** Given a non-retryable decline occurs, when classified, then automatic retry stops and customer action is requested.
- **AC-03:** Given a valid late-success event arrives, when processed, then invoice and entitlement are reconciled without duplicate posting.
- **AC-04:** Given a duplicate webhook is delivered, when processed, then it has no duplicate financial or entitlement effect.

## 13. Operational metrics

- Collection success by attempt and failure code
- Involuntary churn rate using a defined denominator
- Duplicate-charge and duplicate-webhook incidents
- Days sales outstanding for subscription invoices
- Time from payment success to entitlement restoration

Define numerator, denominator, source system, measurement window, owner, and baseline before setting targets. Metrics are measurement proposals, not promised improvements.

## 14. Assumptions and open decisions

- Grace duration, retry cadence, access restrictions, cancellation notices, and proration are contract and policy decisions.
- Payment providers differ in decline codes, idempotency guarantees, and webhook semantics; implement provider adapters.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Rule group | Acceptance criteria | Implementation evidence |
|---|---|---|
| BR-001 to BR-008 | AC-01 to AC-04 | Unit/integration tests, audit events, and process-owner sign-off |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
