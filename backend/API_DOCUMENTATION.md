# API Documentation

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
Most endpoints require authentication using Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 📋 Table of Contents
- [Authentication Endpoints](#authentication-endpoints)
- [Subscription Endpoints](#subscription-endpoints)
- [Plans Endpoints](#plans-endpoints)
- [Payment Endpoints](#payment-endpoints)
- [Admin Endpoints](#admin-endpoints)

---

## Authentication Endpoints

### 1. Register User
**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Validations:**
- Email must be valid format
- Password minimum 8 characters
- Password must contain uppercase, lowercase, digit, and special character

**Error Responses:**
- `400` - Invalid email or password format
- `409` - User already exists

---

### 2. Login
**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "subscriber",
  "email": "user@example.com",
  "message": "Login successful"
}
```

**Error Responses:**
- `400` - Invalid email format
- `401` - Invalid credentials

---

### 3. Get Current User
**GET** `/api/auth/me`

Get authenticated user information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "subscriber"
}
```

**Error Responses:**
- `401` - Missing or invalid token

---

## Subscription Endpoints

### 1. Activate Trial
**POST** `/api/subscriptions/trial`

**Story:** SIM-89 - Activate 14-day trial period for subscription

**Authentication:** Required (subscriber, admin)

**Request Body:**
```json
{
  "plan_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (201):**
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "trial",
  "trial_start": "2025-11-19T09:00:00+00:00",
  "trial_end": "2025-12-03T09:00:00+00:00",
  "next_billing_date": "2025-12-04T09:00:00+00:00",
  "created_at": "2025-11-19T09:00:00+00:00"
}
```

**Business Logic:**
- Trial period: 14 days
- Status set to 'trial'
- Next billing date: day after trial ends
- Validates plan exists and is active
- Prevents duplicate trials for same plan

**Error Responses:**
- `400` - Invalid plan_id format or user already has active/trial subscription
- `404` - Plan not found or inactive
- `401` - Unauthorized
- `500` - Server error

---

### 2. List User Subscriptions
**GET** `/api/subscriptions`

Get all subscriptions for the authenticated user.

**Authentication:** Required (subscriber, admin)

**Query Parameters:**
- `status` (optional): Filter by status (trial, active, cancelled, expired)
- `limit` (optional): Number of results (1-100, default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response (200):**
```json
{
  "subscriptions": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "plan_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "trial",
      "trial_start": "2025-11-19T09:00:00+00:00",
      "trial_end": "2025-12-03T09:00:00+00:00",
      "next_billing_date": "2025-12-04T09:00:00+00:00",
      "created_at": "2025-11-19T09:00:00+00:00"
    }
  ],
  "total": 1
}
```

**Error Responses:**
- `401` - Unauthorized
- `500` - Server error

---

### 3. Get Subscription by ID
**GET** `/api/subscriptions/{subscription_id}`

Get details of a specific subscription.

**Authentication:** Required (subscriber, admin)

**Path Parameters:**
- `subscription_id`: UUID of subscription

**Response (200):**
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "trial",
  "trial_start": "2025-11-19T09:00:00+00:00",
  "trial_end": "2025-12-03T09:00:00+00:00",
  "next_billing_date": "2025-12-04T09:00:00+00:00",
  "started_at": "2025-11-19T09:00:00+00:00",
  "expires_at": "2025-12-03T09:00:00+00:00",
  "created_at": "2025-11-19T09:00:00+00:00"
}
```

**Authorization:**
- Users can only view their own subscriptions
- Admins can view all subscriptions

**Error Responses:**
- `400` - Invalid subscription_id format
- `403` - Access denied
- `404` - Subscription not found
- `401` - Unauthorized
- `500` - Server error

---

### 4. Get User Subscriptions (Admin)
**GET** `/api/subscriptions/user/{user_id}`

Get all subscriptions for a specific user (includes plan details).

**Authentication:** Required (admin, subscriber)

**Path Parameters:**
- `user_id`: UUID of user

**Response (200):**
```json
[
  {
    "id": "650e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "active",
    "started_at": "2025-11-19T09:00:00+00:00",
    "expires_at": "2025-12-19T09:00:00+00:00",
    "subscription_plans": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Premium",
      "price": 29.99,
      "duration_days": 30
    }
  }
]
```

**Error Responses:**
- `400` - Error fetching subscriptions
- `401` - Unauthorized

---

### 5. Update Subscription
**PUT** `/api/subscriptions/{subscription_id}`

Update subscription status or plan.

**Authentication:** Required (admin, subscriber)

**Request Body:**
```json
{
  "subscription": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "active"
  }
}
```

**Response (200):**
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "updated_at": "2025-11-19T10:00:00+00:00"
}
```

**Error Responses:**
- `400` - Error updating subscription
- `404` - Subscription not found
- `401` - Unauthorized

---

## Plans Endpoints

### 1. Create Plan
**POST** `/api/plans`

**Story:** SIM-71 - Create subscription plan

**Authentication:** Required (admin only)

**Request Body:**
```json
{
  "plan": {
    "name": "Premium",
    "description": "Premium subscription with all features",
    "price": 29.99,
    "duration_days": 30,
    "features": [
      {
        "name": "Unlimited Access",
        "description": "Access to all premium content"
      },
      {
        "name": "Priority Support",
        "description": "24/7 priority customer support"
      }
    ]
  }
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Premium",
  "description": "Premium subscription with all features",
  "price": 29.99,
  "duration_days": 30,
  "features": [
    {
      "name": "Unlimited Access",
      "description": "Access to all premium content"
    }
  ],
  "is_active": true,
  "created_at": "2025-11-19T09:00:00+00:00"
}
```

**Error Responses:**
- `400` - Failed to create plan
- `401` - Unauthorized
- `403` - Insufficient permissions

---

### 2. List Plans
**GET** `/api/plans`

Get all subscription plans.

**Authentication:** Not required

**Query Parameters:**
- `active_only` (optional): Boolean, default: true

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Basic",
    "description": "Basic subscription",
    "price": 9.99,
    "duration_days": 30,
    "features": [
      {
        "name": "Basic Access",
        "description": "Access to basic features"
      }
    ],
    "is_active": true,
    "created_at": "2025-11-19T09:00:00+00:00"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Premium",
    "description": "Premium subscription",
    "price": 29.99,
    "duration_days": 30,
    "features": [],
    "is_active": true,
    "created_at": "2025-11-19T09:00:00+00:00"
  }
]
```

**Error Responses:**
- `500` - Error fetching plans

---

### 3. Get Plan by ID
**GET** `/api/plans/{plan_id}`

Get details of a specific plan.

**Authentication:** Not required

**Path Parameters:**
- `plan_id`: UUID of plan

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Premium",
  "description": "Premium subscription with all features",
  "price": 29.99,
  "duration_days": 30,
  "features": [
    {
      "name": "Unlimited Access",
      "description": "Access to all premium content"
    }
  ],
  "is_active": true,
  "created_at": "2025-11-19T09:00:00+00:00"
}
```

**Error Responses:**
- `404` - Plan not found

---

### 4. Update Plan
**PUT** `/api/plans/{plan_id}`

**Story:** SIM-71 - Update subscription plan

**Authentication:** Required (admin only)

**Request Body:**
```json
{
  "plan": {
    "name": "Premium Plus",
    "price": 39.99,
    "description": "Updated premium plan",
    "duration_days": 30,
    "features": [
      {
        "name": "Everything in Premium",
        "description": "Plus additional features"
      }
    ]
  }
}
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Premium Plus",
  "description": "Updated premium plan",
  "price": 39.99,
  "duration_days": 30,
  "features": [
    {
      "name": "Everything in Premium",
      "description": "Plus additional features"
    }
  ],
  "is_active": true,
  "updated_at": "2025-11-19T10:00:00+00:00"
}
```

**Error Responses:**
- `400` - Error updating plan
- `404` - Plan not found
- `401` - Unauthorized
- `403` - Insufficient permissions

---

### 5. Delete Plan (Soft Delete)
**DELETE** `/api/plans/{plan_id}`

**Story:** SIM-71 - Soft delete subscription plan

**Authentication:** Required (admin only)

**Path Parameters:**
- `plan_id`: UUID of plan

**Response (204):**
No content

**Error Responses:**
- `400` - Error deleting plan
- `404` - Plan not found
- `401` - Unauthorized
- `403` - Insufficient permissions

---

## Payment Endpoints

### 1. Mock Payment
**POST** `/api/payments/mock`

**Story:** SIM-83 - Mock payment endpoint for testing

**Authentication:** Not required (testing endpoint)

**Request Body:**
```json
{
  "payment": {
    "subscription_id": "650e8400-e29b-41d4-a716-446655440000",
    "amount": 29.99,
    "should_succeed": true
  }
}
```

**Response (201):**
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440000",
  "subscription_id": "650e8400-e29b-41d4-a716-446655440000",
  "amount": 29.99,
  "status": "success",
  "transaction_id": "TXN-A1B2C3D4",
  "payment_method": "mock",
  "created_at": "2025-11-19T09:00:00+00:00"
}
```

**Payment Status:**
- `should_succeed: true` → status: "success", generates transaction_id
- `should_succeed: false` → status: "failed", transaction_id: null

**Error Responses:**
- `400` - Failed to create payment record or error processing payment

---

### 2. Get Payment History
**GET** `/api/payments/history/{subscription_id}`

Get all payments for a subscription.

**Authentication:** Required (admin, subscriber)

**Path Parameters:**
- `subscription_id`: UUID of subscription

**Response (200):**
```json
{
  "subscription_id": "650e8400-e29b-41d4-a716-446655440000",
  "payments": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440000",
      "subscription_id": "650e8400-e29b-41d4-a716-446655440000",
      "amount": 29.99,
      "status": "success",
      "transaction_id": "TXN-A1B2C3D4",
      "payment_method": "mock",
      "created_at": "2025-11-19T09:00:00+00:00"
    }
  ],
  "total_payments": 1,
  "total_amount": 29.99
}
```

**Error Responses:**
- `400` - Error fetching payment history
- `401` - Unauthorized

---

### 3. Get Payment Status
**GET** `/api/payments/status/{payment_id}`

Get details of a specific payment.

**Authentication:** Required (admin, subscriber)

**Path Parameters:**
- `payment_id`: UUID of payment

**Response (200):**
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440000",
  "subscription_id": "650e8400-e29b-41d4-a716-446655440000",
  "amount": 29.99,
  "status": "success",
  "transaction_id": "TXN-A1B2C3D4",
  "payment_method": "mock",
  "created_at": "2025-11-19T09:00:00+00:00"
}
```

**Error Responses:**
- `404` - Payment not found
- `401` - Unauthorized

---

## Admin Endpoints

### 1. Admin Dashboard
**GET** `/api/admin/dashboard`

Access admin dashboard.

**Authentication:** Required (admin only)

**Response (200):**
```json
{
  "message": "Welcome to admin dashboard",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "admin"
}
```

**Error Responses:**
- `401` - Unauthorized
- `403` - Insufficient permissions

---

### 2. List Users
**GET** `/api/admin/users`

Get list of all users.

**Authentication:** Required (admin only)

**Response (200):**
```json
{
  "message": "List of all users",
  "admin_user": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses:**
- `401` - Unauthorized
- `403` - Insufficient permissions

---

### 3. Get Statistics
**GET** `/api/admin/stats`

Get system statistics.

**Authentication:** Required (admin, finance)

**Response (200):**
```json
{
  "message": "System statistics",
  "accessible_by": ["admin", "finance"],
  "current_role": "admin"
}
```

**Error Responses:**
- `401` - Unauthorized
- `403` - Insufficient permissions

---

## Role-Based Access Control (RBAC)

### Available Roles:
- **subscriber** - Regular users
- **admin** - Administrative users
- **finance** - Finance team members

### Role UUID Mapping:
- `422b8113-a6d2-404f-9cf0-9ccdf48c0c03` → subscriber
- `ea31bc06-c648-4361-b611-d5f028c2b117` → admin
- `49d95cb2-0f50-4842-8a55-a324a6a0f404` → finance

---

## Common Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message describing what went wrong"
}
```

### 401 Unauthorized
```json
{
  "detail": "Missing authorization header"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## Interactive API Documentation

FastAPI provides interactive documentation at:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

These interfaces allow you to test endpoints directly in your browser.

---

## Testing with cURL

### Example: Register User
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

### Example: Login
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

### Example: Activate Trial (with auth)
```bash
curl -X POST "http://127.0.0.1:8000/api/subscriptions/trial" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"plan_id":"550e8400-e29b-41d4-a716-446655440000"}'
```

---

## Version History

- **v1.0** - Initial API release with authentication, subscriptions, plans, payments, and admin endpoints
- Story implementations: SIM-45, SIM-52, SIM-71, SIM-83, SIM-89, SIM-92, SIM-93
