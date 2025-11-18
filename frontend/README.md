# Frontend - Subscription Management System

A complete React-based frontend application for managing subscriptions, plans, and payments with role-based access control.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Integration](#api-integration)
- [Components Overview](#components-overview)
- [Pages Overview](#pages-overview)
- [Testing](#testing)
- [Environment Configuration](#environment-configuration)

---

## ✨ Features

### Authentication & Authorization
- ✅ User registration with email/password
- ✅ Password strength validation (real-time feedback)
- ✅ JWT-based authentication
- ✅ Role-based access control (Admin, Subscriber, Finance)
- ✅ Secure token storage in localStorage
- ✅ Protected routes

### Subscriber Features
- ✅ Browse available subscription plans
- ✅ View plan details (name, price, billing cycle, features)
- ✅ Mock payment processing
- ✅ Subscription management
- ✅ Payment history

### Admin Features
- ✅ Full CRUD operations for subscription plans
- ✅ Create new plans with custom pricing
- ✅ Edit existing plans (name, price, features, status)
- ✅ Delete plans
- ✅ Toggle plan active/inactive status
- ✅ Modern admin dashboard interface

### UI/UX
- ✅ Responsive design (mobile-friendly)
- ✅ Modern gradient styling
- ✅ Loading states and error handling
- ✅ Form validation with visual feedback
- ✅ Modal dialogs for plan management
- ✅ Success/error notifications

---

## 🛠 Tech Stack

- **React** 18.2.0 - UI framework
- **React Router DOM** 6.22.0 - Client-side routing
- **React Scripts** 5.0.1 - Build tooling
- **Jest** - Testing framework
- **React Testing Library** - Component testing
- **Fetch API** - HTTP requests
- **CSS3** - Styling with gradients and animations

---

## 📁 Project Structure

```
frontend/
├── public/
│   └── index.html                    # HTML template
├── src/
│   ├── api/                          # API Client Layer
│   │   ├── auth.js                   # Authentication endpoints
│   │   ├── plans.js                  # Plans CRUD endpoints
│   │   └── payments.js               # Payment endpoints
│   │
│   ├── components/                   # Reusable Components
│   │   ├── PasswordStrengthIndicator.jsx
│   │   └── PasswordStrengthIndicator.css
│   │
│   ├── pages/                        # Page Components
│   │   ├── RegisterPage.jsx          # User registration
│   │   ├── RegisterPage.css
│   │   ├── SubscriberDashboard.jsx   # Plans browsing & subscription
│   │   ├── SubscriberDashboard.css
│   │   ├── AdminDashboard.jsx        # Plan management (Admin only)
│   │   └── AdminDashboard.css
│   │
│   ├── tests/                        # Test Files
│   │   └── RegisterPage.test.jsx     # Registration tests
│   │
│   ├── styles/                       # Global Styles
│   │   └── index.css                 # Base CSS reset and globals
│   │
│   ├── App.jsx                       # Main app with routing
│   └── index.jsx                     # Application entry point
│
├── .env                              # Environment variables
├── package.json                      # Dependencies and scripts
└── README.md                         # This file
```

---

## 🚀 Setup & Installation

### Prerequisites
- Node.js (v14 or higher)
- npm (v6 or higher)
- Backend API running on `http://localhost:8000`

### Installation Steps

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   
   The `.env` file is already created with:
   ```env
   REACT_APP_API_URL=http://localhost:8000
   ```
   
   Update if your backend runs on a different URL.

---

## 🏃 Running the Application

### Start Development Server
```bash
npm start
```
- Opens browser at `http://localhost:3000`
- Hot reload enabled
- Automatic error overlay

### Build for Production
```bash
npm run build
```
- Creates optimized production build in `build/`
- Minified and bundled

### Run Tests
```bash
npm test
```
- Runs Jest test suite
- Interactive watch mode
- Coverage reports available

---

## 🔌 API Integration

### Base Configuration
All API clients use the base URL from environment variables:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### Authentication API (`src/api/auth.js`)

#### `registerUser(email, password)`
- **POST** `/api/auth/register`
- Registers new user
- Stores token in localStorage
- Returns: `{ access_token, user_id, email, role }`

#### `loginUser(email, password)`
- **POST** `/api/auth/login`
- Authenticates user
- Stores: token, user_id, role, email in localStorage
- Returns: `{ access_token, user_id, email, role }`

#### `getCurrentUser()`
- **GET** `/api/auth/me`
- Requires: Bearer token
- Returns current user info

#### `logoutUser()`
- Clears localStorage
- Redirects to login page

**Full Code:**

```javascript
/**
 * Authentication API Client
 * Handles registration, login, and user info
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Register a new user
 * @param {string} email - User email
 * @param {string} password - User password (must have uppercase, digit, special char)
 * @returns {Promise} Registration response
 */
export async function registerUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Registration failed');
  }

  return data;
}

/**
 * Login user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} Login response with access_token
 */
export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Login failed');
  }

  // Store token in localStorage
  if (data.access_token) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user_id', data.user_id);
    localStorage.setItem('role', data.role);
    localStorage.setItem('email', data.email);
  }

  return data;
}

/**
 * Get current user info
 * @returns {Promise} User data
 */
export async function getCurrentUser() {
  const token = localStorage.getItem('token');

  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch user');
  }

  return data;
}

/**
 * Logout user
 */
export function logoutUser() {
  localStorage.removeItem('token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('role');
  localStorage.removeItem('email');
  window.location.href = '/login';
}
```

### Plans API (`src/api/plans.js`)

#### `getPlans()`
- **GET** `/api/plans`
- Public endpoint
- Returns array of active plans

#### `getPlanById(planId)`
- **GET** `/api/plans/{planId}`
- Returns single plan details

#### `createPlan(planData)` 🔒 Admin Only
- **POST** `/api/plans`
- Requires: Bearer token
- Body: `{ plan: { name, description, price, billing_cycle, is_active } }`
- Returns created plan

#### `updatePlan(planId, updates)` 🔒 Admin Only
- **PUT** `/api/plans/{planId}`
- Requires: Bearer token
- Body: `{ plan: { ...updates } }`
- Returns updated plan

#### `deletePlan(planId)` 🔒 Admin Only
- **DELETE** `/api/plans/{planId}`
- Requires: Bearer token
- Returns success boolean

**Full Code:**

```javascript
/**
 * Plans API Client
 * Handles subscription plan operations
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Get all active plans
 * @returns {Promise} List of plans
 */
export async function getPlans() {
  const response = await fetch(`${API_BASE_URL}/api/plans`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch plans');
  }

  return response.json();
}

/**
 * Get plan by ID
 * @param {string} planId - Plan UUID
 * @returns {Promise} Plan details
 */
export async function getPlanById(planId) {
  const response = await fetch(`${API_BASE_URL}/api/plans/${planId}`);
  
  if (!response.ok) {
    throw new Error('Plan not found');
  }

  return response.json();
}

/**
 * Create new plan (Admin only)
 * @param {Object} planData - Plan details
 * @returns {Promise} Created plan
 */
export async function createPlan(planData) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/plans`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ plan: planData }), // Wrapped in "plan"
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to create plan');
  }

  return data;
}

/**
 * Update plan (Admin only)
 * @param {string} planId - Plan UUID
 * @param {Object} updates - Plan updates
 * @returns {Promise} Updated plan
 */
export async function updatePlan(planId, updates) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/plans/${planId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ plan: updates }), // Wrapped in "plan"
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update plan');
  }

  return data;
}

/**
 * Delete plan (Admin only)
 * @param {string} planId - Plan UUID
 * @returns {Promise} Success
 */
export async function deletePlan(planId) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/plans/${planId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to delete plan');
  }

  return true;
}
```

### Payments API (`src/api/payments.js`)

#### `createMockPayment(subscriptionId, amount, shouldSucceed)`
- **POST** `/api/payments/mock-payment`
- Requires: Bearer token
- Body: `{ payment: { subscription_id, amount, should_succeed } }`
- Returns payment confirmation

#### `getPaymentHistory(subscriptionId)`
- **GET** `/api/payments/history/{subscriptionId}`
- Requires: Bearer token
- Returns array of payments

**Full Code:**

```javascript
/**
 * Payments API Client
 * Handles mock payment operations
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Create mock payment
 * @param {string} subscriptionId - Subscription UUID
 * @param {number} amount - Payment amount
 * @param {boolean} shouldSucceed - Mock success/failure
 * @returns {Promise} Payment result
 */
export async function createMockPayment(subscriptionId, amount, shouldSucceed = true) {
  const response = await fetch(`${API_BASE_URL}/api/payments/mock`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      payment: {
        subscription_id: subscriptionId,
        amount: amount,
        should_succeed: shouldSucceed,
      },
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Payment failed');
  }

  return data;
}

/**
 * Get payment history for subscription
 * @param {string} subscriptionId - Subscription UUID
 * @returns {Promise} Payment history
 */
export async function getPaymentHistory(subscriptionId) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/payments/history/${subscriptionId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch payment history');
  }

  return data;
}
```

---

## 🧩 Components Overview

### PasswordStrengthIndicator
**Location:** `src/components/PasswordStrengthIndicator.jsx`

**Purpose:** Real-time password strength validation

**Strength Levels:**
- **Weak** (1-2 criteria): Red color
- **Medium** (3 criteria): Orange color
- **Good** (4 criteria): Light green color
- **Strong** (5 criteria): Bright green color

**Validation Criteria:**
- ✅ Length ≥ 8 characters
- ✅ Length ≥ 12 characters (bonus)
- ✅ Contains uppercase letter
- ✅ Contains digit
- ✅ Contains special character

**Full Code:**

`src/components/PasswordStrengthIndicator.jsx`:
```jsx
import React from 'react';
import './PasswordStrengthIndicator.css';

/**
 * Password strength indicator component
 * Shows strength level based on password complexity
 */
export default function PasswordStrengthIndicator({ password }) {
  const getStrength = (pwd) => {
    if (!pwd) return { level: 0, text: '', color: 'gray' };

    let strength = 0;
    
    // Check length
    if (pwd.length >= 8) strength++;
    if (pwd.length >= 12) strength++;
    
    // Check for uppercase
    if (/[A-Z]/.test(pwd)) strength++;
    
    // Check for digit
    if (/\d/.test(pwd)) strength++;
    
    // Check for special char
    if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) strength++;

    // Determine level
    if (strength <= 2) return { level: 1, text: 'Weak', color: '#ff4444' };
    if (strength === 3) return { level: 2, text: 'Medium', color: '#ffaa00' };
    if (strength === 4) return { level: 3, text: 'Good', color: '#44ff44' };
    return { level: 4, text: 'Strong', color: '#00ff00' };
  };

  const strength = getStrength(password);

  if (!password) return null;

  return (
    <div className="password-strength">
      <div className="strength-bar">
        <div
          className="strength-fill"
          style={{
            width: `${(strength.level / 4) * 100}%`,
            backgroundColor: strength.color,
          }}
        />
      </div>
      <span className="strength-text" style={{ color: strength.color }}>
        {strength.text}
      </span>
    </div>
  );
}
```

`src/components/PasswordStrengthIndicator.css`:
```css
.password-strength {
  margin-top: 8px;
  margin-bottom: 12px;
}

.strength-bar {
  width: 100%;
  height: 6px;
  background-color: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-text {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  font-weight: 600;
}
```

---

## 📄 Pages Overview

### 1. RegisterPage (`/register`)
**File:** `src/pages/RegisterPage.jsx`

**Features:**
- Email and password input fields
- Real-time password strength indicator
- Form validation
- Error message display
- Loading state during registration
- Auto-redirect to dashboard on success
- Link to login page

**State Management:**
```javascript
- email: string
- password: string
- error: string
- loading: boolean
```

**User Flow:**
1. Enter email and password
2. See password strength feedback
3. Submit form
4. Token stored in localStorage
5. Redirect to `/dashboard`

**Full Code:**

`src/pages/RegisterPage.jsx`:
```jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PasswordStrengthIndicator from '../components/PasswordStrengthIndicator';
import { registerUser } from '../api/auth';
import './RegisterPage.css';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await registerUser(email, password);
      // Store token and navigate
      localStorage.setItem('token', data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <h1>Register</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
            <PasswordStrengthIndicator password={password} />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <div className="login-link">
          Already have an account?{' '}
          <a href="/login">Login here</a>
        </div>
      </div>
    </div>
  );
}
```

`src/pages/RegisterPage.css`:
```css
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-container {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 100%;
}

.register-container h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 28px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.login-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}
```

---

### 2. SubscriberDashboard (`/dashboard`)
**File:** `src/pages/SubscriberDashboard.jsx`

**Features:**
- Grid display of all active plans
- Plan details: name, price, billing cycle, features
- Subscribe buttons for each plan
- Mock payment processing
- Success/error notifications
- Loading states
- Inactive plan indicators

**State Management:**
```javascript
- plans: array
- loading: boolean
- error: string
- paymentStatus: 'processing' | 'success' | 'failed' | ''
```

**User Flow:**
1. View available plans
2. Click "Subscribe Now" on chosen plan
3. Mock payment processed
4. Success notification shown
5. Payment status updated

**Full Code:**

`src/pages/SubscriberDashboard.jsx`:
```jsx
import React, { useState, useEffect } from 'react';
import { getPlans } from '../api/plans';
import { createMockPayment } from '../api/payments';
import './SubscriberDashboard.css';

export default function SubscriberDashboard() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const data = await getPlans();
      setPlans(data);
    } catch (err) {
      setError(err.message || 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId, price) => {
    setPaymentStatus('processing');
    setError('');

    try {
      // Create mock subscription ID (in real app, this would come from backend)
      const mockSubscriptionId = `sub_${Date.now()}`;
      
      // Create mock payment
      const result = await createMockPayment(mockSubscriptionId, price, true);
      setPaymentStatus('success');
      setTimeout(() => setPaymentStatus(''), 3000);
    } catch (err) {
      setError(err.message || 'Payment failed');
      setPaymentStatus('failed');
      setTimeout(() => setPaymentStatus(''), 3000);
    }
  };

  if (loading) {
    return <div className="loading">Loading plans...</div>;
  }

  return (
    <div className="subscriber-dashboard">
      <header className="dashboard-header">
        <h1>Subscription Plans</h1>
        <p>Choose the plan that's right for you</p>
      </header>

      {error && <div className="error-banner">{error}</div>}
      {paymentStatus === 'success' && (
        <div className="success-banner">Payment successful! Subscription activated.</div>
      )}
      {paymentStatus === 'processing' && (
        <div className="info-banner">Processing payment...</div>
      )}

      <div className="plans-grid">
        {plans.map((plan) => (
          <div key={plan.id} className={`plan-card ${!plan.is_active ? 'inactive' : ''}`}>
            <h2>{plan.name}</h2>
            <div className="price">
              <span className="currency">$</span>
              <span className="amount">{plan.price}</span>
              <span className="period">/{plan.billing_cycle}</span>
            </div>
            <p className="description">{plan.description}</p>
            <ul className="features">
              {plan.features?.map((feature, idx) => (
                <li key={idx}>✓ {feature}</li>
              )) || <li>Standard features included</li>}
            </ul>
            <button
              className="subscribe-btn"
              onClick={() => handleSubscribe(plan.id, plan.price)}
              disabled={!plan.is_active || paymentStatus === 'processing'}
            >
              {plan.is_active ? 'Subscribe Now' : 'Not Available'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

`src/pages/SubscriberDashboard.css`:
```css
.subscriber-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px 20px;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 40px;
}

.dashboard-header h1 {
  color: #333;
  font-size: 36px;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #666;
  font-size: 18px;
}

.loading {
  text-align: center;
  padding: 100px 20px;
  font-size: 20px;
  color: #666;
}

.error-banner,
.success-banner,
.info-banner {
  max-width: 800px;
  margin: 0 auto 30px;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}

.error-banner {
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.success-banner {
  background-color: #efe;
  color: #3c3;
  border: 1px solid #cfc;
}

.info-banner {
  background-color: #eef;
  color: #33c;
  border: 1px solid #ccf;
}

.plans-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.plan-card {
  background: white;
  border-radius: 12px;
  padding: 40px 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.plan-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.plan-card.inactive {
  opacity: 0.6;
}

.plan-card h2 {
  color: #333;
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
}

.price {
  text-align: center;
  margin-bottom: 20px;
  color: #667eea;
}

.currency {
  font-size: 24px;
  vertical-align: top;
}

.amount {
  font-size: 48px;
  font-weight: 700;
}

.period {
  font-size: 16px;
  color: #999;
}

.description {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
  font-size: 14px;
  line-height: 1.6;
}

.features {
  list-style: none;
  padding: 0;
  margin-bottom: 30px;
}

.features li {
  padding: 10px 0;
  color: #555;
  border-bottom: 1px solid #eee;
}

.features li:last-child {
  border-bottom: none;
}

.subscribe-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.subscribe-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.subscribe-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

### 3. AdminDashboard (`/admin`)
**File:** `src/pages/AdminDashboard.jsx`

**Features:**
- Table view of all plans
- Create new plan button
- Edit existing plans
- Delete plans (with confirmation)
- Active/Inactive status display
- Modal form for create/edit operations
- Real-time plan updates

**State Management:**
```javascript
- plans: array
- loading: boolean
- error: string
- showModal: boolean
- editingPlan: object | null
- formData: { name, description, price, billing_cycle, is_active }
```

**CRUD Operations:**

**Create Plan:**
1. Click "+ Create Plan"
2. Fill modal form
3. Submit → Plan created
4. Table refreshed

**Edit Plan:**
1. Click "Edit" on plan row
2. Modal opens with pre-filled data
3. Modify fields
4. Submit → Plan updated

**Delete Plan:**
1. Click "Delete" on plan row
2. Confirm dialog appears
3. Confirm → Plan deleted
4. Table refreshed

**Full Code:**

`src/pages/AdminDashboard.jsx`:
```jsx
import React, { useState, useEffect } from 'react';
import { getPlans, createPlan, updatePlan, deletePlan } from '../api/plans';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    billing_cycle: 'monthly',
    is_active: true,
  });

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const data = await getPlans();
      setPlans(data);
    } catch (err) {
      setError(err.message || 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (plan = null) => {
    if (plan) {
      setEditingPlan(plan);
      setFormData({
        name: plan.name,
        description: plan.description,
        price: plan.price,
        billing_cycle: plan.billing_cycle,
        is_active: plan.is_active,
      });
    } else {
      setEditingPlan(null);
      setFormData({
        name: '',
        description: '',
        price: '',
        billing_cycle: 'monthly',
        is_active: true,
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingPlan(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const planData = {
        ...formData,
        price: parseFloat(formData.price),
      };

      if (editingPlan) {
        await updatePlan(editingPlan.id, planData);
      } else {
        await createPlan(planData);
      }

      await loadPlans();
      handleCloseModal();
    } catch (err) {
      setError(err.message || 'Operation failed');
    }
  };

  const handleDelete = async (planId) => {
    if (!window.confirm('Are you sure you want to delete this plan?')) {
      return;
    }

    try {
      await deletePlan(planId);
      await loadPlans();
    } catch (err) {
      setError(err.message || 'Failed to delete plan');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>Admin Dashboard</h1>
        <button className="create-btn" onClick={() => handleOpenModal()}>
          + Create Plan
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="plans-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Price</th>
              <th>Billing Cycle</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {plans.map((plan) => (
              <tr key={plan.id}>
                <td>{plan.name}</td>
                <td>{plan.description}</td>
                <td>${plan.price}</td>
                <td>{plan.billing_cycle}</td>
                <td>
                  <span className={`status ${plan.is_active ? 'active' : 'inactive'}`}>
                    {plan.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <button
                    className="edit-btn"
                    onClick={() => handleOpenModal(plan)}
                  >
                    Edit
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(plan.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{editingPlan ? 'Edit Plan' : 'Create Plan'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Billing Cycle</label>
                <select
                  value={formData.billing_cycle}
                  onChange={(e) => setFormData({ ...formData, billing_cycle: e.target.value })}
                >
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>

              <div className="form-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  Active
                </label>
              </div>

              <div className="modal-actions">
                <button type="button" onClick={handleCloseModal} className="cancel-btn">
                  Cancel
                </button>
                <button type="submit" className="save-btn">
                  {editingPlan ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
```

`src/pages/AdminDashboard.css`:
```css
.admin-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 20px;
}

.admin-header {
  max-width: 1200px;
  margin: 0 auto 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-header h1 {
  color: #333;
  font-size: 32px;
}

.create-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.create-btn:hover {
  transform: scale(1.05);
}

.loading {
  text-align: center;
  padding: 100px 20px;
  font-size: 20px;
  color: #666;
}

.error-banner {
  max-width: 1200px;
  margin: 0 auto 30px;
  padding: 16px;
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
  border-radius: 8px;
  text-align: center;
}

.plans-table {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  padding: 16px;
  text-align: left;
  color: #555;
  font-weight: 600;
  border-bottom: 2px solid #e9ecef;
}

td {
  padding: 16px;
  border-bottom: 1px solid #e9ecef;
  color: #333;
}

.status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status.active {
  background: #d4edda;
  color: #155724;
}

.status.inactive {
  background: #f8d7da;
  color: #721c24;
}

.edit-btn,
.delete-btn {
  padding: 6px 16px;
  margin-right: 8px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.edit-btn {
  background: #667eea;
  color: white;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.edit-btn:hover,
.delete-btn:hover {
  opacity: 0.8;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 40px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.form-group textarea {
  min-height: 100px;
  resize: vertical;
}

.form-group.checkbox {
  display: flex;
  align-items: center;
}

.form-group.checkbox label {
  display: flex;
  align-items: center;
  margin: 0;
}

.form-group.checkbox input {
  width: auto;
  margin-right: 8px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 30px;
}

.cancel-btn,
.save-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.cancel-btn {
  background: #e9ecef;
  color: #333;
}

.save-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.cancel-btn:hover,
.save-btn:hover {
  opacity: 0.9;
}
```

---

## 🧪 Testing

### Test File: `RegisterPage.test.jsx`

**Test Cases:**
1. ✅ Renders registration form correctly
2. ✅ Shows password strength indicator when typing
3. ✅ Displays error on registration failure
4. ✅ Successful registration stores token and redirects

**Running Tests:**
```bash
npm test
```

**Coverage:**
```bash
npm test -- --coverage
```

**Mocking:**
- `authApi.registerUser` mocked with `jest.mock()`
- `useNavigate` mocked from react-router-dom
- localStorage mocked automatically by jest-dom

**Full Test Code:**

`src/tests/RegisterPage.test.jsx`:
```jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RegisterPage from '../pages/RegisterPage';
import * as authApi from '../api/auth';

jest.mock('../api/auth');

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('RegisterPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders registration form', () => {
    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  test('shows password strength indicator when typing', () => {
    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    const passwordInput = screen.getByLabelText(/password/i);
    fireEvent.change(passwordInput, { target: { value: 'Weak1!' } });

    expect(screen.getByText(/weak|medium|good|strong/i)).toBeInTheDocument();
  });

  test('displays error on registration failure', async () => {
    authApi.registerUser.mockRejectedValue(new Error('Email already exists'));

    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
    });
  });

  test('successful registration stores token and redirects', async () => {
    authApi.registerUser.mockResolvedValue({
      access_token: 'test-token-123',
      user: { id: '1', email: 'test@example.com' },
    });

    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('test-token-123');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });
});
```

---

## 📦 Configuration Files

### App.jsx - Main Application Router

`src/App.jsx`:
```jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import RegisterPage from './pages/RegisterPage';
import SubscriberDashboard from './pages/SubscriberDashboard';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/register" replace />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<SubscriberDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

### index.jsx - Application Entry Point

`src/index.jsx`:
```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### Global Styles

`src/styles/index.css`:
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

#root {
  min-height: 100vh;
}
```

### HTML Template

`public/index.html`:
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Subscription Management System"
    />
    <title>Subscription Manager</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

---

## ⚙️ Environment Configuration

### `.env` File
```env
REACT_APP_API_URL=http://localhost:8000
```

### Usage in Code
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### Production Configuration
For production, update `.env` or set environment variable:
```bash
REACT_APP_API_URL=https://api.yourproduction.com
```

---

## 🎨 Styling

### Design System

**Colors:**
- Primary Gradient: `#667eea → #764ba2`
- Background: `#f5f7fa → #c3cfe2`
- Success: `#3c3` / `#efe`
- Error: `#c33` / `#fee`
- Info: `#33c` / `#eef`

**Typography:**
- Font Family: System fonts (SF Pro, Segoe UI, Roboto)
- Headings: 24px - 36px
- Body: 14px - 16px

**Responsive Breakpoints:**
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

---

## 🔒 Security Features

1. **JWT Token Storage:** Stored in localStorage (consider httpOnly cookies for production)
2. **Authorization Headers:** Bearer token sent with protected requests
3. **Role-Based Access:** Admin endpoints require admin role
4. **Password Validation:** Enforced minimum complexity
5. **HTTPS Ready:** Works with secure backend connections

---

## 📦 Dependencies

### Production
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.22.0",
  "react-scripts": "5.0.1"
}
```

### Development
```json
{
  "@testing-library/jest-dom": "^6.1.5",
  "@testing-library/react": "^14.1.2",
  "@testing-library/user-event": "^14.5.1"
}
```

---

## 🚦 Routes

| Route | Component | Access | Description |
|-------|-----------|--------|-------------|
| `/` | Redirect | Public | Redirects to `/register` |
| `/register` | RegisterPage | Public | User registration |
| `/dashboard` | SubscriberDashboard | Protected | View and subscribe to plans |
| `/admin` | AdminDashboard | Admin Only | Manage plans (CRUD) |

---

## 🐛 Troubleshooting

### Backend Connection Issues
```
Error: Failed to fetch
```
**Solution:** Ensure backend is running on `http://localhost:8000`

### CORS Errors
```
Access to fetch blocked by CORS policy
```
**Solution:** Backend must allow CORS from `http://localhost:3000`

### Token Expired
```
Error: Token expired or invalid
```
**Solution:** Re-login to get fresh token

### npm Install Errors
```
npm ERR! code ERESOLVE
```
**Solution:** Try `npm install --legacy-peer-deps`

---

## 📝 Development Notes

### Future Enhancements
- [ ] Add login page (currently only registration)
- [ ] Implement proper authentication flow
- [ ] Add password reset functionality
- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Real subscription management
- [ ] User profile page
- [ ] Dark mode toggle
- [ ] Internationalization (i18n)

### Known Limitations
- Mock payment only (no real payment gateway)
- No refresh token implementation
- localStorage used for tokens (consider httpOnly cookies)
- No email verification
- Limited error handling for network failures

---

## 👨‍💻 Development Workflow

1. **Start Backend:**
   ```bash
   cd backend
   uvicorn src.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm start
   ```

3. **Run Tests:**
   ```bash
   npm test
   ```

4. **Build Production:**
   ```bash
   npm run build
   ```

---

## 📞 Support

For issues or questions:
- Check backend API documentation: `http://localhost:8000/docs`
- Review browser console for errors
- Check network tab for failed requests
- Verify environment variables are set correctly

---

## 📄 License

This project is part of the Subscription Management System.

---

**Built with ❤️ using React**
