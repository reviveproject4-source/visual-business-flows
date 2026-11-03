# Customer Complaint & Support Ticket Escalation Flow

> **Domain:** Customer Service, Helpdesk, After-Sales Support  
> **Key Objective:** Ensure timely complaint resolution, enforce SLA response times, and prevent unresolved escalations.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Dissatisfied Customer
    participant Channel as WhatsApp / Helpdesk Widget
    actor Agent as Tier 1 Support Agent
    actor Lead as Shift Supervisor / Ops Manager
    participant CRM as CRM Ticket System

    Customer->>Channel: Submits Complaint ("Order arrived cold and incomplete")
    Channel->>CRM: Auto-create Ticket #TK-9021 (Severity: MEDIUM)
    CRM->>Agent: Route ticket based on agent availability
    
    Agent->>Customer: Respond within 15m: "We apologize, reviewing your order details."
    Agent->>CRM: Verify Order Logs & Kitchen Dispatch Times
    
    alt Resolved by Frontline Agent ($20 compensation voucher limit)
        Agent->>Customer: Offer instant $10 store credit + free re-delivery
        Customer-->>Agent: Accepts resolution
        Agent->>CRM: Mark Ticket as RESOLVED (Outcome: Voucher Issued)
    else Complex Dispute / Customer Demands Full Cash Refund ($50+)
        Agent->>CRM: Escalate to Supervisor (Exceeds Agent Financial Limit)
        CRM->>Lead: Priority Alert: Ticket #TK-9021 Escalated (SLA: 2 hours)
        Lead->>Customer: Direct Phone Call / Senior Response
        Lead->>CRM: Authorize Special Bank Refund Adjustment
        Lead->>CRM: Mark Ticket as RESOLVED (Escalation Approved)
    end
    
    CRM->>Customer: Automated CSAT Survey: "How satisfied were you with this resolution? (1-5)"
```
