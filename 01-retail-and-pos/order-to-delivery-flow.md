# Point-of-Sale Order to Fulfillment & Delivery Flow

> **Domain:** Omnichannel Retail, Fast Food / Restaurant, E-Commerce Express  
> **Key Objective:** Synchronize in-store orders with fulfillment dispatch and courier tracking.

---

## 1. Process Flowchart

```mermaid
flowchart TD
    Customer([Customer Places Order]) --> Channel{Order Channel}
    Channel -->|In-Store POS| Cashier[Cashier Registers Order]
    Channel -->|Online Web / App| WebStore[E-Commerce Gateway]

    Cashier --> Payment{Payment Status}
    WebStore --> Payment

    Payment -->|Cash / Card Confirmed| Paid[Mark as PAID & Issue Invoice]
    Payment -->|Pending Online Transfer| TimeoutCheck{Payment within 15 mins?}
    TimeoutCheck -->|No| Cancel[Auto-Cancel & Restock Inventory]
    TimeoutCheck -->|Yes| Paid

    Paid --> SplitOrder{Order Type}
    SplitOrder -->|Dine-In / Takeaway| Counter[Kitchen / Assembly Counter]
    SplitOrder -->|Delivery Needed| Warehouse[Warehouse Packing Station]

    Counter --> Handover([Customer Receives Order])
    Warehouse --> Pack[Pack Items & Affix Shipping Label]
    Pack --> CourierCall[Auto-Dispatch 3rd Party Courier API]
    CourierCall --> InTransit[Courier Picked Up - Status: IN_TRANSIT]
    InTransit --> Delivered([Customer Confirms Delivery via OTP / Photo])
```

---

## 2. Status Lifecycle Transitions

```mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> PAID : Payment received
    CREATED --> CANCELLED : 15m payment timeout
    PAID --> PACKING : Warehouse pick & pack
    PACKING --> READY_FOR_PICKUP : Label affixed
    READY_FOR_PICKUP --> ON_THE_WAY : Handed to driver
    ON_THE_WAY --> DELIVERED : Delivery confirmed
    ON_THE_WAY --> FAILED_DELIVERY : Customer unreachable
    FAILED_DELIVERY --> RETURNED_TO_STORE : Courier return
```
