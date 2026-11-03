# Automated Low-Stock Alert & Supplier Purchase Order Flow

> **Domain:** Retail Inventory, Supermarket, Supply Chain  
> **Key Objective:** Automatically detect stock falling below minimum safety threshold, generate Purchase Orders (PO), and receive supplier shipments.

---

## 1. Process Flowchart

```mermaid
flowchart TD
    Sale[Customer Completes POS Sale] --> StockUpdate[Decrement Inventory Quantity]
    StockUpdate --> ThresholdCheck{Stock <= Safety Threshold?}

    ThresholdCheck -->|No| Normal[Normal Operations: No Action]
    ThresholdCheck -->|Yes| AutoAlert[Trigger `INVENTORY_LOW_ALERT`]

    AutoAlert --> CheckExistingPO{Existing Open PO for this SKU?}
    CheckExistingPO -->|Yes| AwaitArrival[Do Not Duplicate: Supplier shipment in progress]
    CheckExistingPO -->|No| DraftPO[System Auto-Drafts Purchase Order PO]

    DraftPO --> POAmount{PO Value Threshold}
    POAmount -->|Under $500 Auto-Reorder| SendSupplier[Auto-Transmit PO to Supplier via EDI / Email]
    POAmount -->|Over $500| ManagerApproval[Route to Purchasing Manager for Approval]
    
    ManagerApproval -->|Approved| SendSupplier
    ManagerApproval -->|Rejected / Adjusted| Modify[Purchasing Manager edits quantities] --> SendSupplier

    SendSupplier --> Shipment[Supplier Ships Goods]
    Shipment --> Receiving[Store Staff Scans Inbound Delivery Note]
    Receiving --> Restocked[(Restock Available Inventory & Close PO)]
```
