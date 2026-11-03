# Customer Return, Defect Inspection, and Refund Flow

> **Domain:** Retail, E-Commerce, Consumer Electronics  
> **Key Objective:** Manage customer return requests, inspect item condition, adjust inventory, and issue proper financial refunds or store credits.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer
    actor Staff as Frontline Store Staff
    participant POS as Store POS System
    participant Inventory as Inventory System
    participant Accounting as Financial Ledger
    participant Gateway as Payment Gateway

    Customer->>Staff: Request Return (Item + Original Receipt)
    Staff->>POS: Lookup Invoice / Receipt Number
    
    alt Receipt Not Found or > 30 Days Old
        POS-->>Staff: Return Window Expired / Invalid
        Staff-->>Customer: Decline Return per Policy
    else Valid Receipt Found
        Staff->>Staff: Inspect Item Condition
        alt Damaged by Customer (Not Manufacturer Defect)
            Staff-->>Customer: Return Denied (Misuse / Altered)
        else Resellable / Verified Manufacturer Defect
            Staff->>POS: Initiate Return Request (Select Return Reason)
            alt Resellable Condition
                POS->>Inventory: Increment Active Warehouse Stock (+1)
            else Defective Unit
                POS->>Inventory: Route Item to "Defective Quarantine Buffer"
            end

            Staff->>Customer: Select Refund Method (Store Credit or Original Payment)
            alt Store Credit Selected
                POS->>Accounting: Issue Digital Gift Voucher / Credit Code
                POS-->>Customer: Handover Store Credit Voucher
            else Original Payment Refund Selected
                POS->>Gateway: POST /v1/refunds (Original Tx ID, Amount)
                Gateway-->>POS: Refund Acknowledged (Arrival 3-5 Business Days)
                POS->>Accounting: Record Refund Debit to Revenue Account
                POS-->>Customer: Issue Refund Confirmation Slip
            end
        end
    end
```
