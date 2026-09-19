# ⚡ SubSphere — Modern Enterprise Subscription & Billing Platform

[![CI Pipeline](https://github.com/Funkevi/SubSphere/actions/workflows/ci.yml/badge.svg)](https://github.com/Funkevi/SubSphere/actions)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

SubSphere is a full-stack, enterprise-grade **Subscription & Billing Management System**. It enables businesses to configure tiered subscription plans, process mock transactions, track subscriber lifecycles, and monitor core revenue analytics like Monthly Recurring Revenue (MRR), Annual Run Rate (ARR), and Churn metrics in real-time.

---

## ✨ Features

### 👤 Subscriber Experience
- **Interactive Plan Browser**: Explore plans with monthly vs. annual billing toggle (with instant 20% discount calculation).
- **Subscription Management**: Instant subscription activation, pause/resume billing cycles, or cancel subscriptions.
- **Payment Gateway Simulator**: Integrated mock payment verification and transaction state tracking.
- **Account Health Dashboard**: Monitor renewal dates, active rates, and payment methods.

### 👑 Admin & Financial Intelligence
- **Live Revenue Analytics**: Real-time stats for MRR, projected ARR, active vs. paused breakdown, and platform churn.
- **Plan Management Suite**: Full CRUD operations for subscription products with tier badges, custom pricing, and visibility controls.
- **Search & Filter Oversight**: Instantly search across subscription plans and active subscribers.

### 🔐 Security & Infrastructure
- **Role-Based Access Control (RBAC)**: Enforced middleware for `subscriber`, `admin`, and `finance` roles.
- **FastAPI Async Core**: Microsecond request handling with OpenAPI / Swagger interactive documentation (`/docs`).
- **Flexible Database**: Configured for Supabase / PostgreSQL with zero-config SQLite local development fallback.
- **Comprehensive Test Coverage**: Over 260+ unit and integration tests across backend pytest and React testing suites.

---

## 🏗️ Architecture & Tech Stack

```
 ┌─────────────────────────────────────────────────────────┐
 │               SubSphere React 18 SPA                    │
 │    (Dark Glassmorphism UI, Responsive Dashboards)       │
 └────────────────────────────┬────────────────────────────┘
                              │ REST API
 ┌────────────────────────────▼────────────────────────────┐
 │               FastAPI Backend Engine                    │
 │   - JWT Authentication & RBAC Router                    │
 │   - Subscription Lifecycle & Renewal Workers            │
 │   - Analytics Aggregation Endpoint                      │
 └────────────────────────────┬────────────────────────────┘
                              │ SQL Engine
 ┌────────────────────────────▼────────────────────────────┐
 │           Supabase / PostgreSQL / SQLite                │
 └─────────────────────────────────────────────────────────┘
```

- **Frontend**: React 18, React Router v6, Vanilla Glassmorphism CSS, Google Fonts (Plus Jakarta Sans, Inter).
- **Backend**: Python 3.12+, FastAPI, Uvicorn, Pydantic v2, PyJWT, AsyncIO.
- **Database**: Supabase Client / PostgREST & SQLite.
- **Testing**: Pytest, Pytest-Asyncio, Coverage, React Testing Library.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate environment (Windows)
.\venv\Scripts\activate
# (macOS/Linux: source venv/bin/activate)

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn src.main:app --reload --port 8000
```

Backend will be live at `http://localhost:8000` with interactive API docs at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start React development server
npm start
```

Frontend application will open automatically at `http://localhost:3000`.

---

## 🧪 Running Test Suites

### Backend Unit & Integration Tests
```bash
cd backend
python -m pytest
```

### Frontend Tests
```bash
cd frontend
npm test -- --watchAll=false
```

---

## 📄 API Reference Overview

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new user account | Public |
| `POST` | `/api/auth/login` | Authenticate & get JWT token | Public |
| `GET` | `/api/plans` | Fetch all active subscription plans | Public |
| `POST` | `/api/plans` | Create a new subscription plan | Admin |
| `POST` | `/api/subscriptions` | Create user subscription | Authenticated |
| `POST` | `/api/payments/mock` | Process mock payment token | Authenticated |
| `GET` | `/api/analytics/overview` | Platform MRR & revenue metrics | Admin/Finance |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.