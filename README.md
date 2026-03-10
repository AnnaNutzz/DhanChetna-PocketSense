# 💰 PocketSense

> A context-aware expense tracker for students who actually need to save money.

PocketSense is a **full-stack personal finance application** with a Django REST API backend, a server-rendered web frontend, and a Tkinter desktop app. It tracks expenses, income, budgets, savings goals, and provides analytics — all with a premium dark UI.

---

## ✨ Features

| Feature                 | Description                                                 |
| ----------------------- | ----------------------------------------------------------- |
| 💸 **Transactions**     | Add/view/delete expenses & income with categories           |
| 👛 **Wallet**           | Real-time balance (total income − total expenses)           |
| 🎯 **Budgets**          | Monthly spending limits with progress bars & warnings       |
| 🏺 **Savings Jar**      | Goal-based savings with progress tracking & deposits        |
| 📈 **Analytics**        | Category breakdown, weekly spending trends, monthly summary |
| 🌙 **Dark/Light Theme** | Toggle between dark and light modes                         |
| 🎮 **Demo Account**     | One-click demo login with pre-loaded sample data            |

---

## 🏗️ Architecture

```
PocketSense/
├── backend/           # Django REST API + Web Frontend
│   ├── apps/
│   │   ├── accounts/      # Auth, user profiles
│   │   ├── transactions/  # Expenses, income, categories
│   │   ├── budgets/       # Budget limits, savings goals
│   │   ├── analytics/     # Dashboard summary, charts, trends
│   │   ├── advice/        # AI advice engine (Phase 2)
│   │   └── sync/          # Offline sync (Phase 2)
│   ├── templates/         # Server-rendered web pages
│   └── static/            # CSS design system
├── desktop/           # Tkinter Desktop App
│   ├── app.py             # Root window + screen manager
│   ├── api_client.py      # HTTP client for Django backend
│   ├── theme.py           # Dark/Light theme tokens
│   └── screens/           # 9 screens (login → analytics)
└── assets/            # Icons & sprites
```

### Tech Stack

| Layer        | Technology                                               |
| ------------ | -------------------------------------------------------- |
| Backend      | **Django 5.2** + **Django REST Framework**               |
| Auth         | **Firebase Auth** (token verification) + Django sessions |
| Database     | **SQLite** (dev) / **PostgreSQL** (production)           |
| Web Frontend | Django templates + **Chart.js** + vanilla CSS            |
| Desktop App  | **Tkinter** (Python standard library)                    |
| API Client   | **requests** (session-based auth)                        |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** (comes with Python)

### 1. Clone & Set Up

```bash
git clone https://github.com/AnnaNutzz/DHanChetna-PocketSense.git
cd PocketSense

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
# Linux
python3 -m pip install -r backend/requirements.txt
```

### 2. Initialize the Database

```bash
cd backend

# Run migrations
python manage.py migrate

# Seed default categories (Food, Travel, Shopping, etc.)
python manage.py seed_categories

# Create the demo account (optional but recommended)
python manage.py seed_demo_user
```

### 3. Start the Backend

```bash
python manage.py runserver
```

The web app is live at **http://127.0.0.1:8000/**

### 4. Launch the Desktop App

Open a **second terminal** (keep the backend running):

```bash
cd desktop
python main.py
```

> Click **"🎮 Try Demo Account"** on the login screen to explore instantly with sample data.

---

## 🎮 Demo Account

Both the web and desktop apps have a **one-click demo login** button. No registration needed.

|              |            |
| ------------ | ---------- |
| **Username** | `demo`     |
| **Password** | `demo1234` |

The demo comes pre-loaded with:

- 📋 20 sample transactions (expenses & income over 14 days)
- 🎯 2 budgets (Food ₹5,000 + Shopping ₹3,000)
- 🏺 2 savings goals (Emergency Fund 37% + Laptop 100%)

To re-seed fresh demo data: `python manage.py seed_demo_user`

---

## 📡 API Endpoints

All API endpoints are under `/api/v1/` and require authentication.

| Group              | Endpoints                                                              |
| ------------------ | ---------------------------------------------------------------------- |
| **Auth**           | `POST /api/v1/auth/verify/`, `GET/PUT /api/v1/auth/profile/`           |
| **Transactions**   | Full CRUD at `/api/v1/transactions/`                                   |
| **Categories**     | Full CRUD at `/api/v1/categories/`                                     |
| **Income Sources** | Full CRUD at `/api/v1/income-sources/`                                 |
| **Budgets**        | Full CRUD at `/api/v1/budgets/`                                        |
| **Savings**        | Full CRUD at `/api/v1/savings-goals/` + `PUT .../deposit/`             |
| **Analytics**      | `GET /api/v1/analytics/summary/`, `.../category-split/`, `.../weekly/` |
| **Advice**         | `GET /api/v1/advice/` _(Phase 2)_                                      |
| **Sync**           | `POST /api/v1/sync/push/`, `GET /api/v1/sync/pull/` _(Phase 2)_        |

Admin panel: **http://127.0.0.1:8000/admin/** (create a superuser first: `python manage.py createsuperuser`)

---

## 🖥️ Desktop App Screens

| Screen               | Description                                              |
| -------------------- | -------------------------------------------------------- |
| **Login / Register** | Session auth + demo login button                         |
| **Dashboard**        | Stats cards, quick actions, recent transactions, nav bar |
| **Transactions**     | Filterable list (All / Expenses / Income)                |
| **Add Transaction**  | Form for new expense or income entry                     |
| **Wallet**           | Balance display + income/expense totals                  |
| **Savings Jar**      | Goals with progress bars + deposit form                  |
| **Budgets**          | Budget limits with usage bars + creation dialog          |
| **Analytics**        | Category breakdown bars + weekly spending chart          |
| **Settings**         | Theme toggle + account info + logout                     |

---

## 🗄️ Database Models

| Model              | Purpose                                           |
| ------------------ | ------------------------------------------------- |
| `User`             | Custom user (extends AbstractUser)                |
| `UserProfile`      | Financial profile (income type, living situation) |
| `Transaction`      | Expenses and income entries                       |
| `Category`         | System defaults + user-custom categories          |
| `IncomeSource`     | Registered income streams                         |
| `RecurringPattern` | Detected spending patterns                        |
| `Budget`           | Monthly spending limits per category              |
| `SavingsGoal`      | Target-based savings with deposits                |
| `DeviceSync`       | Multi-device sync tracking                        |
| `AuditLog`         | Change history for accountability                 |

---

## 🛣️ Roadmap

- [x] **Phase 1** — Backend API, Web Frontend, Desktop App
- [ ] **Phase 2** — AI auto-categorization, advice engine, CSV/PDF export, offline sync
- [ ] **Phase 3** — Spending prediction, anomaly detection, receipt scanning (OCR)
- [ ] **Mobile** — Kivy app or PWA

---

## 📄 License

This project is for educational purposes.
