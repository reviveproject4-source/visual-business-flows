# Social OAuth 2.0 (Google / Apple) Authentication Flow

> **Domain:** User Identity, Single Sign-On (SSO), Authentication & Security  
> **Key Objective:** Securely authenticate customers using Google/Apple OAuth without storing raw passwords in your application database.

---

## 1. Process Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Store Operator / Customer
    participant App as Web Frontend (Next.js)
    participant Backend as Backend API Service
    participant Google as Google Identity Provider (OAuth2)
    participant DB as User Database

    User->>App: Clicks "Sign in with Google"
    App->>Google: Redirects to Google Consent Screen<br/>(client_id, redirect_uri, scope: email+profile)
    
    User->>Google: Enters Google credentials & grants consent
    Google-->>App: Redirects to callback with Authorization Code (`?code=AUTH_CODE_xyz`)
    
    App->>Backend: POST /v1/auth/google/callback {code: AUTH_CODE_xyz}
    Backend->>Google: Exchange Code for Access Token & ID Token (POST https://oauth2.googleapis.com/token)
    Google-->>Backend: Returns ID Token (Cryptographically signed JWT with email & name)
    
    Backend->>Backend: Validate JWT signature against Google Public Keys
    Backend->>DB: Query user by email
    alt User Does Not Exist (First Time Login)
        Backend->>DB: INSERT INTO users (email, name, provider='GOOGLE', role='CASHIER')
    else User Exists
        Backend->>DB: UPDATE users SET last_login_at = NOW()
    end

    Backend->>Backend: Generate internal Session JWT (Short-lived 15m) + Rotating Refresh Token
    Backend-->>App: Set HTTP-Only Secure Cookie + Return User Profile
    App-->>User: Redirect to Store Dashboard
```
