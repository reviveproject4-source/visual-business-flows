# OAuth 2.0 / OpenID Connect Sign-In and Account Linking

> **Domain:** Identity, authentication, SaaS applications  
> **Document type:** To-Be reference workflow  
> **Status:** Reference design — validate with process owners before implementation  
> **Audience:** Business Analysts, Systems Analysts, product teams, and developers

## 1. Problem statement

Social sign-in can expose accounts to takeover or incorrect account linking when redirect validation, token verification, tenant authorization, and session lifecycle are incomplete.

## 2. Objective and scope

**Objective:** Authenticate users through a trusted identity provider using authorization code flow with PKCE, validate identity tokens, and issue least-privilege application sessions.

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
| End user | Starts sign-in and grants provider consent |
| Web/mobile client | Initiates authorization request and receives callback |
| Application backend | Exchanges code, validates tokens, and issues session |
| Identity provider | Authenticates user and returns authorization response |
| User database | Stores provider identity mapping and account status |
| Authorization service | Checks tenant membership and application roles |

## 4. Trigger, preconditions, and postconditions

**Trigger:** A user selects Google sign-in or starts an explicitly authorized Google account-linking action.

**Preconditions**
- OAuth client, exact redirect URI, allowed origins, and OIDC discovery/JWKS configuration are registered.
- Authorization Code Flow with PKCE is supported and state/nonce lifetimes are defined.
- Client ID, requested scopes, consent behavior, and account-linking policy are configured.
- Tenant invitation/signup rules and least-privilege role assignment are enforced by the backend.
- Session issuance, rotation, expiry, revocation, and secure cookie/storage controls are defined.

**Postconditions**
- Business object has an explicit final or pending status.
- Material decisions, external references, and exceptions are traceable.
- Related financial, inventory, customer, or access records are synchronized or visibly pending.

## 5. Business process view

This flow describes the human and organizational process, independent of a specific application architecture.

```mermaid
flowchart TD
    A([User selects Google sign-in]) --> B[Create state, nonce, and PKCE challenge]
    B --> C[Redirect to registered Google authorization endpoint]
    C --> D{User authenticates and consents?}
    D -->|No| X[Return denied or cancelled result]
    D -->|Yes| E[Receive authorization code and state]
    E --> F[Validate state and exchange code using PKCE]
    F --> G[Validate token signature, issuer, audience, expiry, and nonce]
    G --> H{Token valid?}
    H -->|No| X
    H -->|Yes| I[Resolve provider subject and tenant mapping]
    I --> J{Existing identity or authorized invitation?}
    J -->|No| X
    J -->|Yes| K[Apply account-linking and role/tenant authorization]
    K --> L{Authorization passes?}
    L -->|No| X
    L -->|Yes| M[Issue secure application session]
    M --> N[Record authentication outcome without storing tokens in logs]
    N --> O([Authenticated session established])
```

## 6. System interaction view

The sequence models browser authorization initiation, Google callback, state/PKCE and ID-token validation, identity/tenant resolution, and secure session issuance.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Browser
    participant App as Application Backend
    participant Google as Google Authorization Server
    participant Identity as Identity Store
    participant Session as Session Service
    participant Audit
    User->>Browser: Select Google sign-in
    Browser->>App: Start authorization
    App->>App: Create state, nonce, PKCE verifier/challenge
    App-->>Browser: Redirect with state, nonce, challenge, and redirect URI
    Browser->>Google: Authorization request
    Google-->>Browser: Return authorization code
    Browser->>App: Callback with code and state
    App->>App: Validate state and exchange code using PKCE
    App->>Google: Token request
    Google-->>App: ID token and access token
    App->>App: Validate signature, issuer, audience, expiry, and nonce
    App->>Identity: Resolve provider subject and tenant invitation policy
    alt Existing linked identity
        Identity-->>App: Existing internal user and tenant mapping
    else New identity allowed
        Identity->>Identity: Create identity mapping under signup policy
    else No invitation or signup prohibited
        Identity-->>App: Deny account creation
    end
    App->>Session: Issue secure session after authorization checks
    Session-->>Browser: Set secure session cookie
    App->>Audit: Record authentication outcome without tokens
    Browser-->>User: Show authenticated or denied result
```

## 7. Business rules

| ID | Rule |
|---|---|
| BR-001 | Use Authorization Code Flow with PKCE for public clients; never embed client secrets in browser/mobile code. |
| BR-002 | Validate state to mitigate CSRF and nonce to bind ID token to authorization request. |
| BR-003 | Validate ID token signature, issuer, audience, expiry, nonce, and relevant claims using provider metadata/JWKS. |
| BR-004 | Use provider subject (issuer + sub) as stable external identity key; email alone is not a safe account-link key. |
| BR-005 | Account linking requires authenticated existing session or separate verified linking challenge. |
| BR-006 | Default role assignment must be least privilege and must not grant privileged tenant roles from provider claims alone. |
| BR-007 | Redirect URIs must be exact registered values; reject open redirects and untrusted return URLs. |
| BR-008 | Sessions use secure, HttpOnly, appropriate SameSite cookies or platform-secure storage, with rotation and revocation controls. |

Policy-dependent rules must be confirmed by the process owner and recorded with an effective date or version before implementation.

## 8. Data requirements

| Entity | Minimum fields |
|---|---|
| ExternalIdentity | issuer, subject, user_id, linked_at, provider |
| AuthAttempt | state_hash, nonce_hash, pkce_challenge, redirect_uri, expires_at, status |
| User | user_id, status, created_at, verified_attributes |
| TenantMembership | user_id, tenant_id, role, status, granted_by |
| Session | session_id, user_id, issued_at, expires_at, revoked_at, device_ref |
| SecurityEvent | event_id, user_id, event_type, timestamp, risk_context |

Use stable identifiers, explicit timestamps/time zones, currency and unit definitions where relevant, and versioned policy/rule references. Financial values must use integer minor units or fixed-precision decimal types, not binary floating-point arithmetic.

## 9. State model

The state names and transitions below describe the proposed lifecycle for this workflow. Confirm guards, role permissions, timeout transitions, and terminal-state behavior with the process owner and implementation team before production use.

```mermaid
stateDiagram-v2
    [*] --> SIGNIN_STARTED
    SIGNIN_STARTED --> AUTH_REQUEST_CREATED
    AUTH_REQUEST_CREATED --> PROVIDER_AUTHENTICATION
    PROVIDER_AUTHENTICATION --> CALLBACK_RECEIVED: Authorization code returned
    PROVIDER_AUTHENTICATION --> USER_CANCELLED
    CALLBACK_RECEIVED --> STATE_VALIDATION
    STATE_VALIDATION --> DENIED: State mismatch or expired
    STATE_VALIDATION --> CODE_EXCHANGE
    CODE_EXCHANGE --> TOKEN_VALIDATION
    TOKEN_VALIDATION --> DENIED: Invalid issuer, audience, signature, or nonce
    TOKEN_VALIDATION --> IDENTITY_RESOLUTION: Token valid
    IDENTITY_RESOLUTION --> ACCOUNT_LINKED: Existing mapping
    IDENTITY_RESOLUTION --> ACCOUNT_CREATED: Signup/invitation policy allows
    IDENTITY_RESOLUTION --> DENIED: No authorized account mapping
    ACCOUNT_LINKED --> SESSION_ISSUED
    ACCOUNT_CREATED --> SESSION_ISSUED
    SESSION_ISSUED --> AUTHENTICATED
    AUTHENTICATED --> SESSION_REVOKED: Logout, expiry, or revocation
    DENIED --> [*]
    USER_CANCELLED --> [*]
    SESSION_REVOKED --> [*]
```

## 10. Exceptions and recovery

| Scenario | Expected behavior and recovery |
|---|---|
| State mismatch or missing state | Reject callback and restart authentication. |
| Code expired or reused | Reject exchange and initiate a fresh authorization request. |
| ID token claim invalid | Reject authentication and record security event without creating session. |
| Email matches existing account but subject differs | Do not auto-link; require explicit verified account-link process. |
| User not invited to tenant | Authenticate identity if allowed but deny tenant access and route to onboarding/request access. |
| Provider key rotation | Refresh trusted JWKS metadata and fail closed if signature cannot be verified. |
| Session refresh replay detected | Revoke token family and require reauthentication. |

Every retryable action should define idempotency, retry limits, backoff, timeout, and manual escalation. Never treat an unknown external result as success.

## 11. Authorization, privacy, and audit

- Enforce permissions on the server/service boundary; hiding a button is not authorization.
- Apply least privilege and separation of duties for sensitive approvals, financial actions, inventory adjustments, or account changes.
- Record actor/service identity, timestamp, object ID, action, prior and new state, reason, correlation ID, and external reference where applicable.
- Protect personal and commercially sensitive data through purpose limitation, access control, retention, and secure evidence storage.
- Preserve history through append-only events or controlled reversals; do not silently overwrite material decisions.

## 12. Acceptance criteria

- **AC-01:** Given callback contains invalid state, when processed, then authentication is rejected and no session is issued.
- **AC-02:** Given an ID token has invalid issuer, audience, signature, expiry, or nonce, when validated, then account creation and session issuance are blocked.
- **AC-03:** Given an email matches an existing user but provider subject is not linked, when sign-in occurs, then automatic account linking is not performed.
- **AC-04:** Given a user has no tenant membership, when accessing tenant resources, then authorization denies access despite successful authentication.
- **AC-05:** Given a public client starts Google sign-in, when authorization is initiated, then PKCE is used and no client secret is exposed in browser/mobile code.
- **AC-06:** Given a callback contains an unregistered redirect URI or untrusted return URL, when processed, then the request is rejected.
- **AC-07:** Given a session is issued, when it expires, rotates, or is revoked, then secure storage/cookie controls and session lifecycle rules are enforced.

## 13. Operational metrics

- Authentication success and failure rate by reason
- Account-linking review incidents
- Invalid token/callback rejection count
- Session revocation and refresh replay events
- Sign-in latency and provider availability

- **Authentication completion rate:** successful authenticated sessions ÷ valid sign-in starts.
- **Callback rejection rate:** rejected callbacks ÷ received callbacks, segmented by state, code, and token validation reason.
- **Account-linking incident count:** confirmed incorrect or disputed identity-link events per reporting period.
- **Sign-in latency:** session-issued timestamp minus sign-in-start timestamp; report median and P95. Review security events continuously.

Assign a named metric owner, reporting window, and baseline before setting a target. These are measurement definitions, not promised improvements.

## 14. Assumptions and open decisions

- Use current provider documentation and OIDC discovery metadata; this pattern is not a substitute for a security review.
- Provider-specific scopes, consent, refresh-token behavior, and account recovery must be documented separately.
- Confirm role names, authority limits, thresholds, timeouts, retention, and escalation ownership with stakeholders.
- Record unresolved decisions explicitly; do not silently convert assumptions into requirements.

## 15. Traceability

| Business rule | Acceptance criterion | Verification focus |
|---|---|---|
| BR-001 | AC-05 | Requirement and test coverage for the rule |
| BR-002 | AC-01 | Requirement and test coverage for the rule |
| BR-003 | AC-02 | Requirement and test coverage for the rule |
| BR-004 | AC-03 | Requirement and test coverage for the rule |
| BR-005 | AC-03 | Requirement and test coverage for the rule |
| BR-006 | AC-04 | Requirement and test coverage for the rule |
| BR-007 | AC-06 | Requirement and test coverage for the rule |
| BR-008 | AC-07 | Requirement and test coverage for the rule |

---

**Validation note:** This is a reusable reference pattern, not an approved policy for every organization. Confirm assumptions and provider-specific behavior before implementation.
