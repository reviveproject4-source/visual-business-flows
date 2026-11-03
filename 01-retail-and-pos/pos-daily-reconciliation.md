# End-of-Day POS Cashier Reconciliation & Drawer Balancing

> **Domain:** Retail, Food & Beverage, Brick-and-Mortar POS  
> **Key Objective:** Prevent internal cash leakage, enforce blind cash counting, and record verified ledger settlements.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Cashier as Cashier / Shift Operator
    participant POS as POS Software
    participant Drawer as Physical Cash Drawer
    participant Manager as Shift Supervisor
    participant Accounting as General Ledger DB

    Cashier->>POS: Select "Close Shift / Day-End Reconciliation"
    POS->>POS: Lock POS register from further sales transactions
    POS->>POS: Calculate System Expected Total (Cash + Card + QRIS) = $X
    
    Note over Cashier,Drawer: Blind Count (Cashier does not see expected total)
    Cashier->>Drawer: Count physical cash bills & coins
    Cashier->>POS: Submit actual physical counted amount = $Y
    
    POS->>POS: Compute Discrepancy = Y - X
    alt Variance == $0.00 (Perfect Match)
        POS->>Accounting: Record "Shift Closed: Clean Balance"
        POS-->>Cashier: Print Shift Settlement Slip
    else Variance != $0.00 (Over / Short Detected)
        POS->>POS: Display Discrepancy Warning Flag
        POS->>Manager: Notify: Register Discrepancy ($Y - $X)
        Manager->>Drawer: Supervise Secondary Cash Recount
        alt Recount Corrects Discrepancy (Human counting error)
            Cashier->>POS: Update Recount Amount
            POS->>Accounting: Record "Shift Closed: Balanced after recount"
        else True Shortage / Overage Confirmed
            Manager->>POS: Enter Supervisor Approval PIN & Reason Note
            POS->>Accounting: Post Discrepancy to "Cash Over/Short" Expense Account
            POS-->>Cashier: Print Audit Discrepancy Report
            POS-->>Manager: Alert Store Owner via SMS/Telegram
        end
    end
```

---

## 2. Business Invariants & Edge Cases

* **Blind Count Invariant:** The POS terminal must never show the cashier the system's expected cash total before they input their physical count. Showing the expected balance invites cashiers to adjust physical numbers to cover up missing cash.
* **Dual Authorization:** Any cash variance exceeding `±$10.00` must require a manager PIN before the register can be handed over to the next shift.
