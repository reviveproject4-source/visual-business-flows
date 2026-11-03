# Inbound Warehouse Receiving & Quality Control (QC) Flow

> **Domain:** Warehouse Management System (WMS), Supply Chain, Logistics  
> **Key Objective:** Inspect inbound deliveries, reconcile against Purchase Orders (PO), quarantine damaged goods, and update available inventory.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Driver as Supplier Delivery Driver
    actor Receiver as Warehouse Inbound Staff
    participant WMS as Warehouse Management System
    participant QC as Quality Control Inspector
    participant InventoryDB as Inventory Database

    Driver->>Receiver: Arrives with Shipment & Physical Delivery Order (DO)
    Receiver->>WMS: Scan PO Barcode on delivery document
    WMS-->>Receiver: Display Expected Items, Batch Numbers, and Quantities
    
    Receiver->>Receiver: Unload Pallets & Perform Physical Count
    alt Quantity Discrepancy (Missing / Short-shipped items)
        Receiver->>WMS: Log Shortage Exception: "Received 80 of 100 units"
        Receiver->>Driver: Endorse DO with "Discrepancy Verified" signature
    end

    Receiver->>QC: Submit Batch for Quality Control Inspection
    QC->>QC: Inspect sample packaging, expiry dates, and product integrity
    
    alt Defect / Spoilage Detected
        QC->>WMS: Flag Defective Items to "Quarantine Buffer"
        WMS->>WMS: Auto-generate Supplier Return Material Authorization (RMA)
        WMS-->>Receiver: Print Quarantine Labels (Red Tag)
    else Passed Inspection
        QC->>WMS: Approve Batch Inspection
        WMS->>WMS: Assign Warehouse Bin / Rack Location (e.g. Rack-B-04)
        WMS->>InventoryDB: Increment Active Available Stock
        WMS-->>Receiver: Print Put-away Barcode Slip
    end
```
