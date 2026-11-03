# Contributing to Visual Business Flows

Thank you for helping make practical business and system workflows clearer. Contributions are welcome from business analysts, systems analysts, product managers, developers, operators, and domain specialists.

You do not need to be an expert in Mermaid. Accuracy, explicit assumptions, and useful exception handling matter more than diagram complexity.

## Before you contribute

1. Search the catalog and open issues to avoid duplicating an existing workflow.
2. For a new domain or a large workflow, open an issue first and describe the problem and intended audience.
3. Use the [workflow template](./docs/workflow-template.md) for new files.
4. Never include confidential company data, personal information, credentials, real customer records, or proprietary process material without permission.

## What a strong contribution includes

As applicable to the workflow, document:

- Business problem, objective, scope, and out-of-scope items.
- Actors, systems, trigger, preconditions, and postconditions.
- A business process view and a distinct system interaction view.
- Numbered business rules (BR-001, BR-002, ...).
- Assumptions, policy-dependent decisions, and open questions.
- Main path, alternate paths, failure handling, and recovery.
- Data inputs/outputs, state transitions, authorization, and audit events.
- Testable acceptance criteria (AC-01, AC-02, ...).
- Traceability between rules and acceptance criteria.

Do not invent universal thresholds, legal requirements, financial outcomes, or performance claims. Label illustrative values as examples and identify decisions that need stakeholder validation.

## Diagram guidelines

- Use standard Mermaid syntax supported by GitHub.
- Prefer a small number of readable diagrams over one overloaded diagram.
- Use `flowchart` for business process decisions, `sequenceDiagram` for system interactions, `stateDiagram-v2` for lifecycle states, and `erDiagram` for data relationships.
- Keep human actions and automated system behavior distinguishable.
- Name decisions as questions and label outgoing paths.
- Include failure and recovery paths where relevant.
- Keep diagram labels concise; explain detail in prose and tables.
- Preview diagrams in GitHub or [Mermaid Live Editor](https://mermaid.live).

## File and naming conventions

- Use lowercase kebab-case filenames, for example `supplier-invoice-approval.md`.
- Place files in the closest existing domain folder.
- If no folder fits, propose a new numbered domain folder in an issue first.
- Use stable IDs for business rules (`BR-001`) and acceptance criteria (`AC-01`).
- Update the README catalog when adding or renaming a workflow.
- Keep links relative where possible.

## Pull request checklist

Before submitting, confirm:

- [ ] The workflow addresses a specific operational problem.
- [ ] Assumptions and policy-dependent decisions are explicit.
- [ ] Business and system views are not conflated.
- [ ] Main, alternate, exception, and recovery paths are covered.
- [ ] Business rules are numbered and unambiguous.
- [ ] Acceptance criteria are testable and traceable to rules.
- [ ] Roles, authorization, data, and audit requirements are considered.
- [ ] Mermaid diagrams render correctly.
- [ ] README catalog and links are updated when needed.
- [ ] No confidential or personal data is included.
- [ ] No unsupported claims or guaranteed outcomes are presented.

## Submit a pull request

1. Fork the repository.
2. Create a focused branch, for example `docs/add-supplier-approval-flow`.
3. Make a small, reviewable change.
4. Preview every Mermaid diagram.
5. Explain the problem, scope, assumptions, and validation performed in the pull request.
6. Respond to review feedback and update the documentation as needed.

## Review principles

Maintainers may request changes where a workflow:
- Presents assumptions as universal facts.
- Omits material failure paths or authorization controls.
- Uses ambiguous roles or undefined terms.
- Makes unsupported quantitative, legal, accounting, or security claims.
- Cannot be rendered or is difficult to understand.
- Duplicates an existing pattern without explaining the difference.

A contribution is a reusable starting point, not a substitute for domain-owner validation.
