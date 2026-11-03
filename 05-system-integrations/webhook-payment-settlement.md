# Asynchronous Webhook Payment Settlement & HMAC Signature Flow

> **Domain:** Payment Gateways (Stripe, Midtrans, PayPal), Fintech, Microservices  
> **Key Objective:** Securely process asynchronous payment confirmations, guard against replay attacks, and handle worker retries.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant Gateway as Payment Gateway (e.g. Stripe)
    participant EdgeIngress as Webhook Edge Endpoint
    participant Redis as Redis Deduplication Cache
    participant Queue as SQS / RabbitMQ Worker Queue
    participant OrderSvc as Core Order Service
    participant DB as Production Database

    Gateway->>EdgeIngress: POST /v1/webhooks/payments<br/>Header: X-Signature-256: `t=1700000000,v1=sha256...`
    
    EdgeIngress->>EdgeIngress: Verify Timestamp (Must be < 5 minutes old to prevent Replay Attack)
    EdgeIngress->>EdgeIngress: Verify HMAC-SHA256 signature using Secret Key
    
    alt Signature Invalid
        EdgeIngress-->>Gateway: HTTP 401 Unauthorized (Drop Request)
    else Signature Verified
        EdgeIngress->>Redis: SETNX event:evt_99120 (TTL 24h)
        alt Duplicate Webhook Delivery (Already Seen)
            Redis-->>EdgeIngress: Key already exists
            EdgeIngress-->>Gateway: HTTP 200 OK (Fast ACK: Already Processed)
        else First Time Receiving Event
            EdgeIngress->>Queue: Push event to High-Priority Processing Queue
            EdgeIngress-->>Gateway: HTTP 200 OK (Immediate Fast Acknowledge)
            
            Queue->>OrderSvc: Background Worker consumes event
            OrderSvc->>DB: UPDATE orders SET payment_status = 'PAID' WHERE id = tx_id
            OrderSvc->>DB: INSERT INTO ledger_entries (...)
            OrderSvc->>OrderSvc: Trigger Customer Push Notification & Receipt Email
            OrderSvc->>Queue: ACK Message (Remove from queue)
        end
    end
```
