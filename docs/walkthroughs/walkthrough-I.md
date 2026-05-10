# Walkthrough I — Backend Foundation Setup

**Date:** 18 Feb 2026, 3:00 PM – 5:10 PM IST

---

## What Was Built

Complete Django REST API backend for PocketSense — the single backend that all frontends (Tkinter, Django Web, Kivy) will connect to.

### 6 Django Apps

| App            | Purpose                                | Status                   |
| -------------- | -------------------------------------- | ------------------------ |
| `accounts`     | User + profile + Firebase auth         | ✅ Complete              |
| `transactions` | Expenses, income, categories, patterns | ✅ Complete              |
| `budgets`      | Budget limits + savings jar            | ✅ Complete              |
| `analytics`    | Dashboard summary, charts, trends      | ✅ Complete              |
| `advice`       | AI advice engine                       | 🔲 Placeholder (Phase 2) |
| `sync`         | Offline push/pull                      | 🔲 Placeholder (Phase 2) |

### 10 Database Models

`User` → `UserProfile` → `Transaction` → `Category` → `IncomeSource` → `RecurringPattern` → `Budget` → `SavingsGoal` → `DeviceSync` → `AuditLog`

### API Endpoints (20+)

| Endpoint Group | URLs                                                                |
| -------------- | ------------------------------------------------------------------- |
| Auth           | `POST /api/v1/auth/verify/`, `GET/PUT /api/v1/auth/profile/`        |
| Transactions   | Full CRUD at `/api/v1/transactions/` (soft delete)                  |
| Categories     | Full CRUD at `/api/v1/categories/`                                  |
| Income Sources | Full CRUD at `/api/v1/income-sources/`                              |
| Patterns       | Read-only at `/api/v1/patterns/`                                    |
| Budgets        | Full CRUD at `/api/v1/budgets/` + `GET /budgets/status_check/`      |
| Savings        | Full CRUD at `/api/v1/savings/` + `PUT /savings/{id}/deposit/`      |
| Analytics      | `GET /summary/`, `/analytics/category-split/`, `/analytics/weekly/` |
| Advice         | `GET /api/v1/advice/` (placeholder)                                 |
| Sync           | `POST /sync/push/`, `GET /sync/pull/` (placeholder)                 |

### Key Files Created

```
backend/
├── pocketsense/settings.py    — Split SQLite/PostgreSQL config via env vars
├── pocketsense/urls.py        — API v1 routing
├── apps/
│   ├── accounts/
│   │   ├── models.py          — Custom User + UserProfile (financial context)
│   │   ├── authentication.py  — Firebase token verification for DRF
│   │   ├── serializers.py     — User/Profile serializers
│   │   ├── views.py           — Token verify + profile CRUD
│   │   └── admin.py
│   ├── transactions/
│   │   ├── models.py          — Transaction, Category, IncomeSource, RecurringPattern
│   │   ├── serializers.py     — Read/Create serializers with validation
│   │   ├── views.py           — ViewSets with soft delete + filtering
│   │   ├── admin.py
│   │   └── management/commands/seed_categories.py
│   ├── budgets/
│   │   ├── models.py          — Budget + SavingsGoal (with fill_state property)
│   │   ├── serializers.py     — Including deposit serializer
│   │   ├── views.py           — Budget status check + savings deposit
│   │   └── admin.py
│   ├── analytics/views.py     — Dashboard summary, category split, weekly trend
│   ├── advice/views.py        — Placeholder
│   └── sync/
│       ├── models.py          — DeviceSync + AuditLog
│       └── views.py           — Placeholder
├── .env / .env.example
└── requirements.txt
```

## Verification Results

- ✅ `makemigrations` — Clean migrations for all 4 app models
- ✅ `migrate` — All applied against SQLite
- ✅ `seed_categories` — 7 defaults: Food, Travel, Shopping, Subscriptions, Income, Recurring, Miscellaneous
- ✅ `runserver` — Starts with 0 issues
- ✅ API auth — Unauthenticated requests return `403 Forbidden`

## How to Run

```bash
cd PocketSense
.\venv\Scripts\activate
cd backend
python manage.py createsuperuser   # Create admin account
python manage.py runserver         # http://127.0.0.1:8000/admin/
```

## Decisions Made

| Decision        | Choice                                  | Why                                    |
| --------------- | --------------------------------------- | -------------------------------------- |
| Frontend mobile | Kivy + Buildozer                        | Python-native, cross-platform          |
| Database        | PostgreSQL (SQLite for dev)             | ACID for financial data                |
| Architecture    | Modular monolith                        | Solo dev, no microservices overhead    |
| Auth            | Firebase Auth → Django validates tokens | Firebase = door, Django = house        |
| Amounts         | DecimalField                            | Floats cause precision bugs with money |
| Deletes         | Soft delete (is_deleted flag)           | Never lose financial data              |
