# Customer Loyalty Onboarding & Point Tier Upgrade Flow

> **Domain:** Customer Loyalty, Retail Rewards, Hospitality  
> **Key Objective:** Smoothly onboard new shoppers into the rewards program, track spending tiers, and trigger automated tier upgrades.

---

## 1. Process Flowchart

```mermaid
flowchart TD
    Shopper([Shopper at Checkout]) --> CashierAsk{Cashier asks: 'Are you a member?'}
    
    CashierAsk -->|No| PromptRegister[Prompt: 'Sign up in 30 seconds for 50 welcome points']
    PromptRegister --> EnterPhone[Customer enters Phone Number on PIN Pad]
    EnterPhone --> CreateMember[System creates Silver Tier Member Profile]
    CreateMember --> AwardBonus[Credit 50 Welcome Points immediately]

    CashierAsk -->|Yes| InputPhone[Scan Member QR / Input Phone]
    AwardBonus --> InputPhone

    InputPhone --> ProcessTx[Complete Purchase Transaction]
    ProcessTx --> CalculatePoints[Award 1 Point per $1.00 Spent]
    CalculatePoints --> TotalSpentCheck{Total Annual Spend >= $1,000?}

    TotalSpentCheck -->|No| StayTier[Remain in Current Tier]
    TotalSpentCheck -->|Yes| UpgradeGold[Upgrade to Gold VIP Tier]

    UpgradeGold --> Benefits[Unlock: 10% Permanent Discount + Free Birthday Coffee]
    Benefits --> SMSNotify[Send Congratulations SMS / WhatsApp]
    StayTier --> Receipt[Print Balance on Receipt Slip]
```
