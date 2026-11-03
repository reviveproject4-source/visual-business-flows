# Inter-Branch Store Inventory Transfer & Reconciliation Flow

> **Domain:** Multi-Store Retail, Chain Stores, Distributed Warehouses  
> **Key Objective:** Transfer stock between two physical retail locations safely without inventory disappearing in transit.

---

## 1. Process Flowchart

```mermaid
flowchart TD
    StoreA([Store A: Low Stock Demand]) --> Request[Store A Manager requests 50 units from Store B]
    Request --> StoreBApproval{Store B Manager Reviews Availability}

    StoreBApproval -->|Declined: Insufficient Stock| Rejected([Transfer Request Cancelled])
    StoreBApproval -->|Approved| PickAndPack[Store B picks items from shelf & packs box]

    PickAndPack --> DeductB[Deduct Stock from Store B: Move to 'IN_TRANSIT_BUFFER']
    DeductB --> Dispatched[Handover box to Internal Courier / Logistics]

    Dispatched --> InTransit{Box in Transit on Highway}
    
    InTransit --> ArrivedStoreA[Box arrives at Store A loading dock]
    ArrivedStoreA --> ScanCount[Store A staff scans barcode & counts physical units]

    ScanCount --> MatchCheck{Count matches Manifest exactly?}
    MatchCheck -->|Yes: 50 of 50 units| CommitA[(Increment Store A Available Inventory)]
    MatchCheck -->|No: Damaged / Lost in Transit| Variance[Log Transit Discrepancy Flag: -2 units lost]
    
    Variance --> SettleVariance[Charge Loss to Logistics Insurance / Write-off]
    SettleVariance --> CommitA
    CommitA --> Completed([Transfer Status: CLOSED])
```
