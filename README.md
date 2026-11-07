# Visual Business Flows

**An open-source library of practical business process and system workflow patterns for Business Analysts, Systems Analysts, product teams, and developers.**

The library translates operational problems into explicit actors, decisions, business rules, exception paths, and system responsibilities. Diagrams use Mermaid and are maintained as Markdown so they can be reviewed and versioned alongside product documentation.

[Browse workflows](#workflow-catalog) · [Use a workflow](#how-to-use-this-library) · [Contribute](./CONTRIBUTING.md) · [Workflow template](./docs/workflow-template.md) · [Developer readiness checklist](./docs/developer-implementation-readiness.md)

---

## What this library is — and is not

**It is:**
- A reusable starting point for process discovery, analysis, and solution design.
- A set of illustrative workflow patterns with assumptions and decision points made visible.
- A practical bridge between business operations and software requirements.

**It is not:**
- A substitute for stakeholder interviews, policy review, legal or accounting advice, or domain validation.
- A guarantee that a workflow fits every organization or jurisdiction.
- Evidence that a proposed control has achieved a particular fraud reduction, time saving, or financial result.

Adapt every workflow to the organization's policies, risk appetite, systems, roles, and applicable regulations before implementation.

## Why diagrams as code?

- **Reviewable:** Mermaid source is text, so changes can be reviewed in pull requests.
- **Portable:** Markdown can live with requirements, architecture notes, and implementation documentation.
- **Traceable:** Git history records how a workflow evolves.
- **Accessible:** Readers can inspect the process without needing a proprietary diagramming application.

## Workflow catalog

The repository currently contains **16 workflow files across five domains**.

### 1. Retail and POS

| Workflow | Focus |
|---|---|
| [POS daily reconciliation](./01-retail-and-pos/pos-daily-reconciliation.md) | Blind count, variance investigation, authorization, and settlement |
| [Order to delivery](./01-retail-and-pos/order-to-delivery-flow.md) | Order capture, fulfillment, and handover |
| [Returns and refunds](./01-retail-and-pos/returns-and-refunds.md) | Return validation, inspection, disposition, and refund |
| [Low-stock alert and restock](./01-retail-and-pos/low-stock-alert-and-restock.md) | Reorder trigger and replenishment |

### 2. CRM and customer retention

| Workflow | Focus |
|---|---|
| [Dormant customer reactivation](./02-crm-and-customer-retention/dormant-customer-reactivation.md) | Inactivity identification and win-back |
| [Customer loyalty enrollment and tier management](./02-crm-and-customer-retention/customer-loyalty-enrollment.md) | Registration and activation |
| [Complaint and ticket resolution](./02-crm-and-customer-retention/complaint-and-ticket-resolution.md) | Triage, escalation, and resolution |

### 3. Financial and billing

| Workflow | Focus |
|---|---|
| [Subscription billing and dunning](./03-financial-and-billing/subscription-billing-and-dunning.md) | Renewal, failed payment, retry, and access states |
| [Marketplace vendor settlement](./03-financial-and-billing/marketplace-vendor-settlement.md) | Conditional settlement and allocation |
| [Expense approval hierarchy](./03-financial-and-billing/expense-approval-hierarchy.md) | Approval routing and authorization |

### 4. Supply chain and inventory

| Workflow | Focus |
|---|---|
| [Warehouse goods receipt](./04-supply-chain-and-inventory/warehouse-goods-receipt.md) | Receiving, quantity checks, and quarantine |
| [Inter-branch stock transfer](./04-supply-chain-and-inventory/inter-branch-stock-transfer.md) | Dispatch, in-transit custody, and receipt variance |
| [Dead-stock review](./04-supply-chain-and-inventory/dead-stock-liquidation.md) | Slow-moving stock review and disposition |

### 5. System integrations

| Workflow | Focus |
|---|---|
| [Payment webhook settlement](./05-system-integrations/webhook-payment-settlement.md) | Signature validation, idempotency, retries, and reconciliation |
| [Third-party courier dispatch](./05-system-integrations/third-party-courier-dispatch.md) | External dispatch and status synchronization |
| [Google OAuth login](./05-system-integrations/oauth-google-login-flow.md) | Authentication and account linking |

## How to use this library

1. Select the workflow closest to the business problem.
2. Read its context, scope, assumptions, and business rules before copying the diagram.
3. Validate actors, policies, thresholds, permissions, and exception handling with stakeholders.
4. Adapt the workflow to the target organization's **As-Is** process and agreed **To-Be** design.
5. Convert confirmed rules into requirements, user stories, data definitions, and acceptance criteria.
6. Record unresolved questions rather than silently inventing answers.

Mermaid diagrams can be previewed in GitHub and edited with the [Mermaid Live Editor](https://mermaid.live/).

## Workflow quality standard

New and materially revised workflows should include, where relevant:

- Problem statement, objective, scope, and out-of-scope items.
- Actors, systems, trigger, preconditions, and postconditions.
- Business process view and system interaction view, kept distinct.
- Numbered business rules and explicit assumptions.
- Main success path, alternate paths, failure recovery, and unresolved decisions.
- Data requirements, authorization, audit events, and state transitions.
- Testable acceptance criteria and operational controls.

See the [contributor guide](./CONTRIBUTING.md) and [workflow template](./docs/workflow-template.md).

## Relationship to other projects

- [OpenBSA](https://github.com/reviveproject4-source/OpenBSA) — a related analyst toolkit for structuring business and system analysis deliverables.

These projects are related but independently usable. This repository focuses on reusable workflow patterns; OpenBSA focuses on analysis artifacts and specification structure.

## Contributing

Contributions are welcome from business analysts, system analysts, operators, product managers, and developers. You do not need to be a Mermaid expert.

- Read [CONTRIBUTING.md](./CONTRIBUTING.md).
- Start from [docs/workflow-template.md](./docs/workflow-template.md).
- Open an issue to discuss a substantial new domain or workflow before investing in a large contribution.
- Submit a pull request with assumptions and validation notes.

## Maintainer

**Tri Raida** · [GitHub profile](https://github.com/reviveproject4-source)

For professional workflow analysis and system specification enquiries, contact
[tri.raida.consulting@gmail.com](mailto:tri.raida.consulting@gmail.com).

## License

MIT. See [LICENSE](./LICENSE).

---

*Practical patterns, not universal prescriptions. Validate before implementation.*
