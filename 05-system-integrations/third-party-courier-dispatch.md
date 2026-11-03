# Third-Party On-Demand Courier API Dispatch & Tracking Flow

> **Domain:** On-Demand Logistics (GrabExpress, GoSend, Lalamove, Uber Direct)  
> **Key Objective:** Automatically request nearest courier pickup, handle driver assignment, and stream real-time GPS tracking.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant StoreApp as Merchant POS / Admin Panel
    participant CourierAPI as 3rd-Party Courier API Gateway
    participant DriverApp as Driver Mobile App
    actor Driver as Courier Driver
    actor Customer as Recipient Customer

    StoreApp->>CourierAPI: POST /v1/deliveries/request<br/>{pickup_address, dropoff_address, package_size}
    CourierAPI-->>StoreApp: HTTP 202 Accepted {booking_id: "BKG-7712", tracking_url}
    
    CourierAPI->>DriverApp: Broadcast pickup job to nearby drivers
    Driver->>DriverApp: Driver accepts job
    CourierAPI->>StoreApp: Webhook: `driver.assigned` {driver_name: "Bambang", plate: "B 1234 CD"}
    
    Driver->>StoreApp: Driver arrives at store loading bay
    StoreApp->>Driver: Staff verifies Driver PIN & hands over package
    Driver->>DriverApp: Mark "PACKAGE_PICKED_UP"
    
    CourierAPI->>Customer: Send SMS/WhatsApp with live GPS tracking link
    
    Driver->>Customer: Arrives at customer doorstep
    Customer->>Driver: Confirms delivery via OTP PIN
    Driver->>DriverApp: Submits Delivery Confirmation & Photo
    
    CourierAPI->>StoreApp: Webhook: `delivery.completed` {delivered_at: "2026-11-03T08:00:00Z"}
    StoreApp->>StoreApp: Update Order Status to "DELIVERED"
```
