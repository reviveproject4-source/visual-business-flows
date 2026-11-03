# Customer Loyalty Enrollment and Tier Management

> **Domain:** Customer loyalty, retail rewards, hospitality  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

Loyalty enrollment and reward balances become inconsistent when identity matching, consent, point accrual, reversals, and tier qualification are not controlled.

## 2. Objective and scope

**Objective:** Create a transparent membership lifecycle with verified enrollment, auditable point movements, and reproducible tier evaluation.

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
| Customer | Provides enrollment details and consent |
| Frontline staff | Explains program and supports enrollment |
| Loyalty service | Creates member identity and calculates rewards |
| POS / commerce | Sends eligible purchase and return events |
| Program manager | Maintains reward and tier policy |

## 4. Trigger, preconditions, and postconditions

**Trigger:** A prospective customer submits a registration/enrollment request or accepts an authorized invitation.

**Preconditions**
- Required identity and contact fields, consent text, and terms version are available.
- Duplicate detection keys and manual-review rules are defined.
- Signup, invitation, and tenant/account eligibility policies are configured.
- Verification channels and expiry rules are available.
- Default role and access scope follow least-privilege policy.

**Postconditions**
- Business object has an explicit final or pending status.
- Material decisions, external references, and exceptions are traceable.
- Related financial, inventory, customer, or access records are synchronized or visibly pending.

## 5. Business process view

This flow describes the human and organizational process, independent of a specific application architecture.

```mermaid
flowchart TD
    A([Customer requests enrollment]) --> B[Present terms and capture affirmative consent]
    B --> C{Consent granted?}
    C -->|No| X[Stop enrollment and record refusal]
    C -->|Yes| D[Verify required identity/contact attributes]
    D --> E[Search for existing member identity]
    E --> F{Existing or ambiguous match?}
    F -->|Yes| G[Link existing account or route manual review]
    G --> H{Identity resolved?}
    H -->|No| X
    H -->|Yes| I[Activate member profile]
    F -->|No| J[Create member using current program rules]
    J --> I
    I --> K[Receive confirmed eligible purchase event]
    K --> L[Append points ledger transaction]
    L --> M[Evaluate tier and notify member]
    M --> N{Return, reversal, expiry, or closure event?}
    N -->|Yes| O[Apply approved ledger adjustment or closure]
    N -->|No| P[Maintain active membership]
    O --> Q([Record resulting balance and status])
    P --> Q
```

## 6. System interaction view

This logical sequence shows system responsibilities. Adapt participants and messages to the selected architecture and provider contract.

```mermaid
sequenceDiagram
    autonumber
    actor Customer
    participant Channel as Enrollment Channel
    participant Membership
    participant Identity as Identity/Deduplication
    participant POS
    participant Ledger as Points Ledger
    participant Notify as Notification Service
    Customer->>Channel: Review terms and request enrollment
    Channel->>Membership: Submit consent and profile data
    Membership->>Identity: Check existing member and identity attributes
    Identity-->>Membership: Match, no match, or manual review
    alt Duplicate or unresolved identity
        Membership-->>Channel: Link existing account or request review
    else New eligible member
        Membership->>Membership: Create member using active program version
        Membership-->>Channel: Return member identifier
        POS-->>Membership: Send confirmed eligible purchase event
        Membership->>Ledger: Calculate and append points transaction
        Ledger-->>Membership: New balance and ledger reference
        Membership->>Membership: Evaluate tier using effective rules
        Membership->>Notify: Send enrollment, balance, or tier notice
        Membership->>Ledger: Process approved reversal or expiry event
    end
    Channel-->>Customer: Show enrollment status
```

## 7. Business rules

| ID | Rule |
|---|---|
| BR-001 | Enrollment requires recorded consent to program terms and relevant communications. |
| BR-002 | Identity matching must avoid duplicate profiles based only on an unverified shared attribute. |
| BR-003 | Points are earned only on eligible net spend according to a versioned rule set. |
| BR-004 | Refunds and reversals create compensating ledger entries; historical point events are not overwritten. |
| BR-005 | Tier qualification uses a defined measurement period, qualifying spend, and effective date. |
| BR-006 | Benefits are checked at redemption against member status, exclusions, and expiry. |
| BR-007 | Staff cannot manually edit balances without an authorized reason and audit record. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| Member | member_id, verified_contact, enrollment_at, consent_version, status |
| PointLedger | entry_id, member_id, source_transaction, points_delta, rule_version, expires_at |
| TierHistory | member_id, tier, effective_from, effective_to, qualification_period |
| RewardRule | rule_version, eligible_spend_basis, earn_rate, exclusions |
| BenefitRedemption | member_id, benefit_id, transaction_id, status |
| ConsentRecord | member_id, purpose, channel, status, captured_at, policy_version |

Use stable identifiers, explicit timestamps/time zones, currency and unit definitions where relevant, and versioned policy/rule references. Financial values must use integer minor units or fixed-precision decimal types, not binary floating-point arithmetic.

## 9. State model

The state names and transitions below describe the proposed lifecycle for this workflow. Confirm guards, role permissions, timeout transitions, and terminal-state behavior with the process owner and implementation team before production use.

```mermaid
stateDiagram-v2
    [*] --> ENROLLMENT_STARTED
    ENROLLMENT_STARTED --> CONSENT_PENDING
    CONSENT_PENDING --> IDENTITY_CHECK
    CONSENT_PENDING --> WITHDRAWN: Consent declined
    IDENTITY_CHECK --> DUPLICATE_REVIEW: Possible existing member
    DUPLICATE_REVIEW --> LINKED: Existing account confirmed
    DUPLICATE_REVIEW --> PROFILE_CREATED: New identity approved
    IDENTITY_CHECK --> PROFILE_CREATED: No match
    PROFILE_CREATED --> ACTIVE
    ACTIVE --> POINTS_UPDATED: Eligible purchase posted
    POINTS_UPDATED --> ACTIVE
    ACTIVE --> SUSPENDED: Risk or policy hold
    SUSPENDED --> ACTIVE: Hold cleared
    ACTIVE --> CLOSED: Account closure approved
    LINKED --> ACTIVE
    WITHDRAWN --> [*]
    CLOSED --> [*]
```

## 10. Exceptions and recovery

| Scenario | Expected behavior and recovery |
|---|---|
| Possible duplicate member | Route to identity review; do not merge automatically without matching policy. |
| Purchase event received twice | Deduplicate by source transaction and event ID. |
| Purchase later refunded | Post a reversing points entry linked to original earning event. |
| Tier calculation job fails | Retain previous tier and retry with same period and rule version. |
| Customer withdraws consent | Apply program closure and communication suppression policy. |
| Manual point adjustment requested | Require reason, evidence, and approval based on configured limits. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given an existing member match is found, when enrollment is attempted, then duplicate account creation is prevented or routed to review.
- **AC-02:** Given the same purchase event is received twice, when points are calculated, then only one earning entry exists.
- **AC-03:** Given an eligible purchase is refunded, when the refund event is processed, then a linked compensating points entry is posted.
- **AC-04:** Given a tier rule changes, when a member is evaluated, then the applicable rule version and period are recorded.

## 13. Operational metrics

- Enrollment completion and duplicate profile rate
- Active member rate by cohort
- Point liability and expiry
- Tier upgrade/downgrade counts
- Reward redemption and reversal rates

Define numerator, denominator, source system, measurement window, owner, and baseline before setting targets. Metrics are measurement proposals, not promised improvements.

## 14. Assumptions and open decisions

- Point rates, tier thresholds, expiry, and benefit terms are merchant-specific and must be versioned.
- Identity verification strength depends on reward value and privacy requirements.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Rule group | Acceptance criteria | Implementation evidence |
|---|---|---|
| BR-001 to BR-007 | AC-01 to AC-04 | Unit/integration tests, audit events, and process-owner sign-off |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
