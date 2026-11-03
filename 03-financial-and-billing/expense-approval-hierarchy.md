# Operational Expense Request & Multi-Tier Approval Workflow

> **Domain:** Corporate Finance, Operations Management, Enterprise Resource Planning (ERP)  
> **Key Objective:** Enforce strict financial governance over company spending based on monetary approval limits.

---

## 1. Multi-Tier Approval Decision Tree

```mermaid
flowchart TD
    Employee([Staff Member Submits Expense Claim / Invoice]) --> Upload[Attach Itemized Receipt & Business Justification]
    Upload --> AmountCheck{Claim Amount Tier}

    AmountCheck -->|Tier 1: <= $100| DirectSupervisor[Direct Supervisor Approval]
    AmountCheck -->|Tier 2: $101 - $1,000| DeptHead[Department Head Approval]
    AmountCheck -->|Tier 3: > $1,000| Executive[Finance Director / Founder Approval]

    DirectSupervisor -->|Rejected| Denied([Return to Staff with Rejection Reason])
    DirectSupervisor -->|Approved| FinanceAudit[Finance Audit & Policy Compliance Check]

    DeptHead -->|Rejected| Denied
    DeptHead -->|Approved| FinanceAudit

    Executive -->|Rejected| Denied
    Executive -->|Approved| FinanceAudit

    FinanceAudit --> TaxValid{Receipt & Tax Invoice Valid?}
    TaxValid -->|No| FixReceipt[Request Corrected Tax Invoice] --> FinanceAudit
    TaxValid -->|Yes| ScheduleDisbursement[Queue in Weekly Accounts Payable Batch]
    ScheduleDisbursement --> DirectDeposit[Direct Bank Deposit to Employee / Vendor]
```
