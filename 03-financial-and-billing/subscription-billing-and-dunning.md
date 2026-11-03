# SaaS Recurring Subscription Billing & Smart Dunning Flow

> **Domain:** Subscription SaaS, Digital Memberships, Recurring Billing  
> **Key Objective:** Maximize revenue recovery from involuntary churn (expired cards, insufficient funds) using automated dunning retries.

---

## 1. Dunning Retry Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant BillingJob as Daily Billing Engine
    participant Gateway as Stripe / Payment Gateway
    participant Customer as Subscriber
    participant Notification as Email & In-App Notice
    participant AppSvc as SaaS Feature Access Service

    BillingJob->>Gateway: Attempt Recurring Charge ($49/month)
    Gateway-->>BillingJob: Declined: `insufficient_funds` (Attempt 0)
    
    BillingJob->>Notification: Send Friendly Dunning Email: "Payment issue - please check card"
    BillingJob->>AppSvc: Maintain Full Access (Grace Period Active)
    
    Note over BillingJob: Smart Wait: 3 Days (Allows customer payday)
    BillingJob->>Gateway: Retry Attempt #1
    alt Retry #1 Succeeds
        Gateway-->>BillingJob: Charge Succeeded ($49)
        BillingJob->>Notification: Send Receipt & Thank You
    else Retry #1 Fails
        Gateway-->>BillingJob: Declined
        BillingJob->>Notification: Urgent Notice: "Action Required: Update card to avoid interruption"
        
        Note over BillingJob: Wait: 4 Days
        BillingJob->>Gateway: Final Retry Attempt #2
        alt Final Retry Succeeds
            BillingJob->>Notification: Payment Recovered
        else Final Retry Fails (Day 7)
            BillingJob->>AppSvc: Downgrade Account: "SUSPENDED_READ_ONLY"
            BillingJob->>Notification: Final Notice: "Your subscription has been paused"
        end
    end
```

---

## 2. Subscription Account State Transitions

```mermaid
stateDiagram-v2
    [*] --> TRIALING : Sign up without card
    TRIALING --> ACTIVE : Enters payment details
    TRIALING --> EXPIRED : Trial period ends without payment

    ACTIVE --> RENEWAL_SUCCESS : Monthly charge OK
    ACTIVE --> PAST_DUE : Card declined (Day 0)

    PAST_DUE --> ACTIVE : Dunning retry collects payment
    PAST_DUE --> SUSPENDED : 14 days without resolution
    
    SUSPENDED --> ACTIVE : Customer updates card & pays invoice
    SUSPENDED --> CANCELLED : 60 days in suspension (Voluntary Churn)

    EXPIRED --> [*]
    CANCELLED --> [*]
```
