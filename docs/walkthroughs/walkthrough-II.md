# Walkthrough II — Django Web Frontend

**Date:** 18 Feb 2026, 5:10 PM – 5:40 PM IST

---

## What Was Built

Complete server-side rendered Django web frontend with dark/light theme.

### Pages Created (9 total)

| Page         | URL              | Features                                                                          |
| ------------ | ---------------- | --------------------------------------------------------------------------------- |
| Login        | `/login/`        | Session auth, redirect if already logged in                                       |
| Register     | `/register/`     | Validation, auto-login on success                                                 |
| Dashboard    | `/`              | Stats cards, quick actions, budget progress, recent transactions, savings preview |
| Transactions | `/transactions/` | Filterable table (type/category/month), pagination, soft delete                   |
| Add Expense  | `/add-expense/`  | Category select, date picker, budget warning toasts                               |
| Add Income   | `/add-income/`   | Shared template with expense, adapts UI                                           |
| Wallet       | `/wallet/`       | Balance display, income/expense totals, income sources list                       |
| Savings Jar  | `/savings/`      | Goal cards with progress bars, inline deposit, create modal                       |
| Budgets      | `/budgets/`      | Status cards (ok/warning/over), remaining amounts, create modal                   |
| Analytics    | `/analytics/`    | Chart.js doughnut (category split) + line chart (weekly trend), monthly summary   |
| Settings     | `/settings/`     | Profile form (financial context for advice engine), CSV export                    |

### Key Files

```
backend/
├── pocketsense/
│   ├── web_views.py     — All 17 view functions
│   ├── web_urls.py      — URL routing for web frontend
│   └── urls.py          — Main URLconf (web at root, API at /api/v1/)
├── templates/
│   ├── base.html        — Sidebar layout, theme toggle, toasts
│   ├── auth_base.html   — Auth layout (no sidebar)
│   └── web/
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── transactions.html
│       ├── add_transaction.html
│       ├── wallet.html
│       ├── savings.html
│       ├── budgets.html
│       ├── analytics.html
│       └── settings.html
└── static/
    └── css/style.css    — 600+ line design system (dark/light themes)
```

### Design System

- **Font Stack:** Outfit (headings/body) + Caveat (amounts/labels)
- **Dark Theme:** Purple-navy gradient (`#1a1a2e` → `#2d2d5e`)
- **Light Theme:** Pink-rose gradient (`#fce4ec` → `#f8bbd0`)
- **Accent Colors:** Purple `#6C5CE7`, Green `#2ecc71`, Red `#ff6b6b`, Orange `#f39c12`
- **Components:** Stat cards, budget bars, savings jar, auth cards, toasts, modals, pagination
- **Responsive:** Sidebar collapses on mobile with hamburger menu

### Features

- **Budget Warnings:** Adding an expense automatically checks budgets — warns if over 80% or exceeded
- **Theme Toggle:** Persisted to `localStorage`
- **CSV Export:** Download all transactions
- **Soft Delete:** Transactions are marked `is_deleted` not removed
- **Chart.js:** Category doughnut + weekly spending line chart

## Verification

- ✅ Server starts with 0 issues
- ✅ Root `/` redirects to `/login/` (302)
- ✅ Login page loads (200, 1822 bytes)
- ✅ All URL patterns resolve without errors
