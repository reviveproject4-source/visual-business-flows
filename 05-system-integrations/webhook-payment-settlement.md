# Payment Webhook Processing and Reconciliation

> **Domain:** Payment integrations, POS, e-commerce  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

A provider may confirm payment while the merchant application is offline or webhook delivery is delayed. Blindly retrying payment or trusting screenshots can create duplicate charges or false paid status.

## 2. Objective and scope

**Objective:** Process provider notifications securely and idempotently, reconcile uncertain transactions against provider truth, and expose safe recovery states.

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
| Customer | Initiates payment and may provide reference details |
| Merchant application | Creates payment intent and controls order state |
| Payment provider | Authorizes, captures, reverses, and emits events |
| Webhook endpoint | Authenticates and records provider events |
| Reconciliation worker | Queries provider and resolves uncertain states |
| Support operator | Handles manual review under controlled permission |

## 4. Trigger, preconditions, and postconditions

**Trigger:** A payment provider sends an event to the merchant's registered webhook endpoint for a previously created payment intent or transaction reference.

**Preconditions**
- Merchant/provider account, endpoint, signing secret or verification key, and supported event schema are configured.
- Payment intent and merchant reference are persisted before asynchronous callback processing.
- Event identifiers, idempotency keys, and allowed payment-state transitions are defined.
- Durable event storage/queue and retry/dead-letter handling are available.
- Settlement reconciliation ownership and provider lookup capability are established.

**Postconditions**
- Business object has an explicit final or pending status.
- Material decisions, external references, and exceptions are traceable.
- Related financial, inventory, customer, or access records are synchronized or visibly pending.

## 5. Business process view

This flow describes the human and organizational process, independent of a specific application architecture.

```mermaid
flowchart TD
    A([Payment intent created]) --> B[Provider processes customer payment]
    B --> C[Webhook event received]
    C --> D[Validate signature, timestamp, merchant account, and schema]
    D --> E{Authentic and valid event?}
    E -->|No| X[Reject or quarantine event and log metadata]
    E -->|Yes| F[Persist event durably before acknowledgement]
    F --> G{Event already processed?}
    G -->|Yes| H[Acknowledge duplicate without reapplying]
    G -->|No| I[Apply allowed payment state transition idempotently]
    I --> J{State transition consistent?}
    J -->|No| K[Queue reconciliation against provider API]
    J -->|Yes| L[Update payment/order projection and ledger]
    K --> M[Resolve unmatched or out-of-order event]
    L --> N[Reconcile settlement reference]
    M --> N
    H --> N
    X --> N
    N --> O([Close event handling with audit reference])
```

## 6. System interaction view

The sequence models payment intent creation, provider webhook authentication, durable event persistence, deduplication, ledger state transition, and provider reconciliation.

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant App as Merchant Application
    participant Payment as Payment Provider
    participant Webhook as Webhook Endpoint
    participant Queue as Durable Event Queue
    participant Ledger
    participant Reconcile
    participant Audit
    Customer->>App: Initiate payment
    App->>Payment: Create payment intent with idempotency key
    Payment-->>App: Return payment reference and next action
    Payment->>Webhook: Send signed event
    Webhook->>Webhook: Validate signature, timestamp, account, and schema
    alt Invalid event
        Webhook-->>Payment: Reject according to provider contract
        Webhook->>Audit: Record rejected event metadata
    else Valid event
        Webhook->>Queue: Persist event durably before acknowledgement
        Queue-->>Webhook: Durable receipt
        Webhook-->>Payment: Acknowledge event
        Queue->>Ledger: Deliver event for idempotent processing
        Ledger->>Ledger: Enforce allowed payment transition and deduplication
        Ledger->>Audit: Record event and ledger reference
    end
    Reconcile->>Payment: Query provider for missing or contradictory state
    Payment-->>Reconcile: Return authoritative transaction status
    Reconcile->>Ledger: Post controlled reconciliation adjustment if approved
```

## 7. Business rules

| ID | Rule |
|---|---|
| BR-001 | A client redirect or customer screenshot is not authoritative proof of payment. |
| BR-002 | Webhook signatures and provider account identity are validated before processing. |
| BR-003 | Persist event identity and outcome; duplicate events must be harmless. |
| BR-004 | Payment state transitions follow provider-specific state machine and reject invalid regressions. |
| BR-005 | Use stable idempotency keys for payment creation, capture, refund, and retry where supported. |
| BR-006 | Do not ask a customer to pay again until original transaction state is checked with provider. |
| BR-007 | Manual confirmation requires privileged role, evidence, reason, and later reconciliation. |
| BR-008 | Authorization, capture, settlement, refund, and bank payout are distinct states. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| PaymentIntent | payment_id, order_id, provider, merchant_ref, amount, currency, idempotency_key |
| ProviderEvent | event_id, event_type, signature_valid, received_at, payload_hash, processing_status |
| PaymentStateHistory | payment_id, from_state, to_state, source_event, changed_at |
| ReconciliationCase | case_id, payment_id, reason, provider_status, resolution |
| Refund | refund_id, payment_id, amount, provider_ref, status |
| SettlementRecord | provider_batch, gross, fees, net, settlement_date, bank_reference |

Use stable identifiers, explicit timestamps/time zones, currency and unit definitions where relevant, and versioned policy/rule references. Financial values must use integer minor units or fixed-precision decimal types, not binary floating-point arithmetic.

## 9. State model

The state names and transitions below describe the proposed lifecycle for this workflow. Confirm guards, role permissions, timeout transitions, and terminal-state behavior with the process owner and implementation team before production use.

```mermaid
stateDiagram-v2
    [*] --> INTENT_CREATED
    INTENT_CREATED --> AWAITING_CUSTOMER
    AWAITING_CUSTOMER --> PROVIDER_PENDING
    PROVIDER_PENDING --> EVENT_RECEIVED
    EVENT_RECEIVED --> SIGNATURE_VALIDATION
    SIGNATURE_VALIDATION --> REJECTED_EVENT: Invalid signature or schema
    SIGNATURE_VALIDATION --> DURABLY_QUEUED: Valid and persisted
    DURABLY_QUEUED --> PROCESSING
    PROCESSING --> SUCCEEDED: Valid success transition
    PROCESSING --> FAILED: Valid failure transition
    PROCESSING --> DUPLICATE_IGNORED: Event already applied
    PROCESSING --> RECONCILIATION_REQUIRED: Unknown or out-of-order state
    RECONCILIATION_REQUIRED --> SUCCEEDED: Provider confirms success
    RECONCILIATION_REQUIRED --> FAILED: Provider confirms failure
    REJECTED_EVENT --> [*]
    DUPLICATE_IGNORED --> [*]
    SUCCEEDED --> [*]
    FAILED --> [*]
```

## 10. Exceptions and recovery

| Scenario | Expected behavior and recovery |
|---|---|
| Webhook signature invalid | Reject event, record security telemetry, and do not change payment state. |
| Webhook arrives before local order commit | Persist event for retry/reconciliation; do not drop it. |
| Webhook is duplicated | Acknowledge after deduplication without duplicate side effects. |
| Provider API unavailable | Keep payment UNKNOWN or RECONCILIATION_PENDING; retry with backoff. |
| Customer reports debit but provider status unknown | Open reconciliation case; do not initiate a second charge. |
| Amount or currency mismatch | Quarantine transaction and require finance/support review. |
| Out-of-order event | Fetch authoritative provider state and apply only valid transition. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given an invalid webhook signature, when received, then no payment state changes and the event is rejected.
- **AC-02:** Given the same provider event is delivered twice, when processed, then only one business side effect occurs.
- **AC-03:** Given a customer reports debit while provider state is unknown, when support opens a case, then a second payment request is blocked pending reconciliation.
- **AC-04:** Given provider amount or currency differs from order, when event is processed, then payment is quarantined for review.
- **AC-05:** Given a customer presents a redirect or screenshot, when payment is verified, then only provider-confirmed status can establish payment completion.
- **AC-06:** Given a provider event attempts an invalid payment-state regression, when processed, then the transition is rejected and the event is reconciled.
- **AC-07:** Given payment creation, capture, refund, or retry is submitted more than once, when the same idempotency key is used, then no duplicate financial side effect occurs.
- **AC-08:** Given a privileged operator manually confirms a transaction, when approval is absent or evidence/reason is missing, then the confirmation is blocked.
- **AC-09:** Given payment reaches authorization, capture, settlement, refund, or bank payout, when status is recorded, then each stage remains separately identifiable.

## 13. Operational metrics

- Webhook delivery-to-processing latency
- Duplicate event rate and deduplication count
- Unknown payment resolution time
- Payment/order state mismatch rate
- Settlement reconciliation variance

- **Webhook acceptance rate:** authenticated, schema-valid events durably acknowledged ÷ received events.
- **Processing latency:** ledger-application timestamp minus provider-event timestamp; report median and P99.
- **Duplicate suppression count:** duplicate event deliveries safely ignored, monitored alongside duplicate side-effect incidents.
- **Reconciliation lag:** time between provider final state and merchant ledger agreement. Review daily by provider/event type.

Assign a named metric owner, reporting window, and baseline before setting a target. These are measurement definitions, not promised improvements.

## 14. Assumptions and open decisions

- Signature validation, acknowledgement timing, and state transitions follow each provider's official contract.
- Offline/manual confirmation is not a generic bypass; use only provider-supported verification.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Business rule | Acceptance criterion | Verification focus |
|---|---|---|
| BR-001 | AC-05 | Requirement and test coverage for the rule |
| BR-002 | AC-01 | Requirement and test coverage for the rule |
| BR-003 | AC-02 | Requirement and test coverage for the rule |
| BR-004 | AC-06 | Requirement and test coverage for the rule |
| BR-005 | AC-07 | Requirement and test coverage for the rule |
| BR-006 | AC-03 | Requirement and test coverage for the rule |
| BR-007 | AC-08 | Requirement and test coverage for the rule |
| BR-008 | AC-09 | Requirement and test coverage for the rule |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
