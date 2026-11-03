# Dormant Customer Detection & Re-Activation Workflow

> **Domain:** Customer Relationship Management (CRM), Retail Marketing, Direct-to-Consumer (D2C)  
> **Key Objective:** Automatically flag customers with prolonged inactivity and trigger personalized win-back offers before permanent churn.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant Cron as Nightly Analytics Job
    participant DB as Customer Database
    participant RuleEngine as CRM Rule Evaluator
    participant Messaging as WhatsApp / Email Automation
    actor Customer as Dormant Customer
    participant POS as Store POS / Online Web

    Cron->>DB: Query customers WHERE last_order_date < (NOW - 60 DAYS)
    DB-->>Cron: Return 420 dormant customer records
    
    loop For Each Dormant Customer
        Cron->>RuleEngine: Evaluate Customer Lifetime Value (LTV) & Total Orders
        alt Total Orders == 1 (One-Time Fluke Buyer)
            RuleEngine->>Messaging: Queue "We Miss You: 10% Off Your Next Order"
        else Total Orders > 3 (High-Value Former Regular)
            RuleEngine->>Messaging: Queue VIP Win-back: "Special VIP Free Gift Voucher"
        end
    end

    Messaging->>Customer: Dispatch Personalized WhatsApp Message with Unique Promo Code
    
    alt Customer Ignores Message within 14 Days
        RuleEngine->>DB: Tag Status: "CHURNED_STAGE_2" (Reduce marketing frequency)
    else Customer Clicks Promo Link & Buys at POS
        Customer->>POS: Redeems Promo Code during Checkout
        POS->>DB: Update Customer Status: "RE_ENGAGED"
        POS->>DB: Log Marketing Attribution: "Win-back Campaign Q4"
        POS-->>Customer: Receipt Issued with Thank-You Note
    end
```

---

## 2. Customer Health State Transitions

```mermaid
stateDiagram-v2
    [*] --> NEW_CUSTOMER : First Purchase
    NEW_CUSTOMER --> ACTIVE : Repeat purchase within 45 days
    ACTIVE --> AT_RISK : Inactivity reaches 45-60 days
    AT_RISK --> DORMANT : Inactivity reaches 61-90 days
    DORMANT --> CHURNED : Inactivity > 180 days
    
    AT_RISK --> ACTIVE : Purchase made
    DORMANT --> RE_ENGAGED : Win-back promo redeemed
    RE_ENGAGED --> ACTIVE : Subsequent regular purchase
```
