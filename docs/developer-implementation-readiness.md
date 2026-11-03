# Developer Implementation Readiness Checklist

Use this checklist before treating a workflow as an implementation specification. A passing Markdown or Mermaid check proves document/render integrity only; it does not prove that the business process is correct.

## 1. Process-owner validation
- [ ] Process owner and approving authority are named by role.
- [ ] As-Is facts are separated from To-Be recommendations and assumptions.
- [ ] Policy-dependent decisions, thresholds, SLAs, and legal/accounting/security constraints are confirmed.
- [ ] Scope boundaries, trigger, preconditions, and postconditions are specific to this workflow.

## 2. Business and system behavior
- [ ] Business process diagram covers the happy path, decisions, alternate paths, exceptions, and recovery.
- [ ] System sequence diagram identifies logical components, request/response direction, synchronous vs asynchronous behavior, and failure handling.
- [ ] State model lists valid states, transition triggers, guards, terminal states, and prohibited transitions.
- [ ] Human actions and automated behavior are distinguishable.
- [ ] No diagram contains unresolved generic placeholders or contradictory paths.

## 3. Requirements and traceability
- [ ] Every business rule has a stable ID, an unambiguous statement, source/type (policy, observed fact, or assumption), and system implication.
- [ ] Every acceptance criterion is independently testable in Given/When/Then form.
- [ ] Traceability maps each material business rule to one or more acceptance criteria and relevant data/process elements.
- [ ] Negative, boundary, duplicate, timeout, retry, and authorization scenarios are covered where relevant.
- [ ] Open decisions are explicit; implementation must not silently invent missing policy.

## 4. Data, security, and operations
- [ ] Entities, identifiers, relationships, required fields, validation, sensitivity, and retention are defined.
- [ ] Authorization is specified at the server/service boundary, including segregation of duties for sensitive actions.
- [ ] Audit events include actor/service, timestamp, object, action, outcome, reason, and correlation/external reference where relevant.
- [ ] Concurrency, idempotency, transaction boundaries, retry policy, and recovery ownership are specified where relevant.
- [ ] Metrics have formulas, numerator/denominator, source, window, owner, and baseline requirement.

## 5. Developer handoff
- [ ] API/event contracts, payload examples, error codes, and integration ownership are documented when needed.
- [ ] Data model and state transition constraints are implementable without guessing.
- [ ] Acceptance criteria can be converted into unit, integration, and end-to-end tests.
- [ ] Mermaid blocks pass automated parsing/rendering in CI.
- [ ] A developer and process owner have reviewed the adapted workflow.

## Readiness decision

- **Reference pattern:** Useful for discovery and solution design; significant local decisions remain.
- **Implementation-ready after adaptation:** All material policy and architecture decisions are confirmed; tests and traceability are actionable.
- **Approved for implementation:** Process owner, product owner, security/domain reviewers, and engineering have signed off.

Do not assign a numerical readiness score unless evidence for each dimension is recorded. A passing CI pipeline is not a substitute for stakeholder approval or implementation testing.
