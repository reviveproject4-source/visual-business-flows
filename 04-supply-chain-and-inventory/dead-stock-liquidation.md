# Dead-Stock Identification & Progressive Discount Liquidation Flow

> **Domain:** Retail Merchandising, Fashion / Apparel, Seasonal FMCG  
> **Key Objective:** Detect slow-moving inventory before it turns into dead loss and execute progressive markdown pricing.

---

## 1. Process Flowchart

```mermaid
flowchart TD
    MonthlyAudit[Monthly Stock Velocity Audit] --> VelocityCheck{Days Since Last Sale}

    VelocityCheck -->|< 30 Days| FastMoving[Fast / Normal Velocity: Maintain Full Price]
    VelocityCheck -->|31 - 60 Days| SlowMoving[Slow Moving: Flag for Store Floor Relocation]
    VelocityCheck -->|61 - 90 Days| AtRiskStock[At-Risk Dead Stock: Apply Tier 1 Markdown -20%]
    VelocityCheck -->|> 90 Days| TrueDeadStock[Confirmed Dead Stock: Urgent Liquidation Required]

    SlowMoving --> EndCapDisplay[Move to High-Traffic Cashier End-Cap Shelf]
    AtRiskStock --> PromoTag[Affix Yellow Discount Tag in POS System]

    TrueDeadStock --> LiquidationStrategy{Select Liquidation Strategy}
    LiquidationStrategy -->|Option A: Flash Sale| StepDown50[Markdown 50% Off / Clearance Rack]
    LiquidationStrategy -->|Option B: Bundle Deal| Bundle[Bundle as 'Buy 2 Get 1 Free' with Best-Sellers]
    LiquidationStrategy -->|Option C: B2B Wholesaler| BulkOffload[Sell to Bulk Liquidator at Cost Basis]

    StepDown50 --> SoldCheck{Sold within 30 days?}
    Bundle --> SoldCheck
    
    SoldCheck -->|Yes| RevenueRecovered[(Working Capital Restored to Cash Flow)]
    SoldCheck -->|No| WriteOff[Final Accounting Write-off & Donate to Charity]
```
