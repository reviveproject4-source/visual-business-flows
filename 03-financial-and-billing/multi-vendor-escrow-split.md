# Multi-Vendor Marketplace Payment Split & Escrow Settlement

> **Domain:** E-Commerce Marketplaces, Ride-Hailing, On-Demand Platforms  
> **Key Objective:** Hold customer payments safely in escrow, deduct platform commissions, and release net earnings to vendors upon delivery confirmation.

---

## 1. Process Flowchart

```mermaid
flowchart TD
    Buyer([Customer Purchases Cart Total: $100]) --> Payment[Credit Card / QRIS Charged via Gateway]
    Payment --> EscrowHold[(Funds Placed in Secure Escrow Vault)]
    
    EscrowHold --> OrderDispatched[Vendor Fulfills & Ships Goods]
    OrderDispatched --> DeliveryConfirmed[Customer Confirms Receipt OR 48h Auto-Confirm]

    DeliveryConfirmed --> DisputeCheck{Dispute or Return Claim Filed?}
    
    DisputeCheck -->|Yes| FreezeEscrow[Freeze Escrow: Route to Dispute Resolution]
    FreezeEscrow --> Decision{Dispute Outcome}
    Decision -->|Buyer Wins| FullRefund[100% Refund to Customer Card]
    Decision -->|Vendor Wins| CalculateSplit

    DisputeCheck -->|No Dispute| CalculateSplit[Trigger Financial Settlement Calculation]

    CalculateSplit --> DeductFee[Deduct 10% Marketplace Commission: $10.00]
    DeductFee --> PlatformAcc[(Credit Platform Revenue Account)]
    
    CalculateSplit --> NetPayout[Calculate 90% Vendor Net Payout: $90.00]
    NetPayout --> VendorWallet[(Credit Vendor Merchant Balance)]

    VendorWallet --> PayoutSchedule{Weekly Auto-Payout Schedule}
    PayoutSchedule --> BankTransfer[Direct Automated Bank Transfer via Clearing House]
```
