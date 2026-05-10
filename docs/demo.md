# 🎓 DhanChetna 

> **Pre-requisites:** Server running at `http://127.0.0.1:8000`
> Run these before the demo:
> ```
> cd D:\DhanChetna\backend
> python manage.py migrate
> python manage.py seed_categories
> python manage.py seed_demo_user
> python manage.py detect_patterns
> python manage.py runserver
> ```

---

## 🗺️ Demo Flow 

### 1. Login Page — Auth System
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) |
| **What to show** | Dark-themed login with demo button |
| **Click** | 🎮 "Try Demo Account" button |
| **Say** | *"Session-based auth for web, Firebase token auth for API/desktop clients"* |
| **Code** | [web_views.py](file:///d:/DhanChetna/backend/pocketsense/web_views.py#L28-L43) — `login_view` |
| | [authentication.py](file:///d:/DhanChetna/backend/apps/accounts/authentication.py) — Firebase DRF backend |

---

### 2. Dashboard — Financial Snapshot
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) |
| **What to show** | 4 stat cards (spent today, monthly income/expense, wallet balance), budget bars, recent transactions, savings preview |
| **Say** | *"Real-time aggregation from Django ORM. Budget bars animate to show consumption percentage."* |
| **Code** | [web_views.py](file:///d:/DhanChetna/backend/pocketsense/web_views.py#L132-L167) — `dashboard_view` |
| | [dashboard.html](file:///d:/DhanChetna/backend/templates/web/dashboard.html) |

---

### 3. Transactions — CRUD with Soft Deletes
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/transactions/](http://127.0.0.1:8000/transactions/) |
| **What to show** | Filterable transaction list (by type, category, month), pagination |
| **Click** | Try the filters, show delete button |
| **Say** | *"Soft deletes — financial data is never hard-deleted. is_deleted flag preserves audit trail."* |
| **Code** | [models.py](file:///d:/DhanChetna/backend/apps/transactions/models.py) — `Transaction`, `Category`, `RecurringPattern` |

---

### 4. Add Expense — With Budget Warnings
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/add-expense/](http://127.0.0.1:8000/add-expense/) |
| **What to show** | Add an expense (e.g. "Swiggy Order", ₹300, Food category) |
| **Watch for** | Toast notification if budget threshold exceeded |
| **Say** | *"On save, the expense classifier auto-tags it as minor/major/minor_repetitive based on income ratio and frequency. Budget status is checked and warns the user."* |
| **Code** | [classifier.py](file:///d:/DhanChetna/backend/apps/transactions/classifier.py) — rules-based classifier |
| | [views.py](file:///d:/DhanChetna/backend/apps/transactions/views.py#L55-L63) — `perform_create` hook |

---

### 5. Wallet — Balance Display
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/wallet/](http://127.0.0.1:8000/wallet/) |
| **What to show** | Gradient wallet card with total income, expenses, and balance |
| **Say** | *"Balance = sum(all income) - sum(all expenses). No manual balance tracking needed."* |

---

### 6. Savings Jar — Goal Tracking
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/savings/](http://127.0.0.1:8000/savings/) |
| **What to show** | Emergency Fund (37% — active), New Laptop (100% — completed) |
| **Click** | Deposit ₹500 into Emergency Fund |
| **Say** | *"4-state fill mapping (no/less/more/full) based on percentage. Auto-completes when target reached."* |
| **Code** | [models.py](file:///d:/DhanChetna/backend/apps/budgets/models.py#L48-L103) — `SavingsGoal.fill_state` property |

---

### 7. Budgets — Spending Limits
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/budgets/](http://127.0.0.1:8000/budgets/) |
| **What to show** | Food ₹3,500, Transport ₹1,500, Entertainment ₹1,000 with progress bars |
| **Say** | *"Per-category and overall budgets. Bars are color-coded: green < 80%, yellow 80-99%, red ≥ 100%."* |

---

### 8. Analytics — Charts & Insights
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/analytics/](http://127.0.0.1:8000/analytics/) |
| **What to show** | Monthly summary, category pie chart, weekly trend line |
| **Say** | *"Chart.js renders on client. Data comes from Django ORM aggregations — category split and daily totals."* |
| **Code** | [analytics/views.py](file:///d:/DhanChetna/backend/apps/analytics/views.py) — `category_split`, `weekly_trend` |

---

### 9. 🧠 Smart Advice — THE KILLER FEATURE
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/advice/](http://127.0.0.1:8000/advice/) |
| **What to show** | Context-aware advice cards with profile context at top |
| **Say** | *"This is the core innovation. The advice engine uses 4 rules from our paper:"* |
| | 1. Food > 45% for hostel students → suggest mess plan |
| | 2. Entertainment > 20% → review subscriptions |
| | 3. Budget > 90% before 20th → defer non-essential |
| | 4. ≥3 recurring patterns → show committed expenses |
| | *"It's context-aware — a hostel student with meals included gets different advice than a rented apartment student."* |
| **Code** | [engine.py](file:///d:/DhanChetna/backend/apps/advice/engine.py) — all rules |

---

### 10. Settings — User Profile Context
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/settings/](http://127.0.0.1:8000/settings/) |
| **What to show** | Profile: Student, Pocket Money, Hostel, Food Provided ✓ |
| **Say** | *"This profile data is what makes the advice engine context-aware. Different settings produce different advice."* |
| **Code** | [models.py](file:///d:/DhanChetna/backend/apps/accounts/models.py#L31-L110) — `UserProfile` |

---

### 11. Dark/Light Theme Toggle
| | |
|---|---|
| **Where** | Sidebar bottom — moon/sun toggle |
| **Click** | Toggle it live |
| **Say** | *"CSS variables swap the entire palette. Persisted in localStorage."* |

---

### 12. CSV Export
| | |
|---|---|
| **URL** | [http://127.0.0.1:8000/export/csv/](http://127.0.0.1:8000/export/csv/) |
| **What happens** | Downloads a CSV file |
| **Say** | *"One-click export of all transactions. Paper mentions CSV/PDF export as Phase 2 feature."* |

---

## 🔧"Show Me The Code"

| Topic | File to Open |
|-------|-------------|
| **Database models** | `D:\DhanChetna\backend\apps\transactions\models.py` — Transaction, Category, RecurringPattern |
| **User & profile** | `D:\DhanChetna\backend\apps\accounts\models.py` — User (UUID PK, Firebase UID), UserProfile |
| **Budget & savings** | `D:\DhanChetna\backend\apps\budgets\models.py` — Budget, SavingsGoal with fill_state |
| **REST API** | `D:\DhanChetna\backend\apps\transactions\views.py` — ViewSets with soft delete |
| **Advice engine** | `D:\DhanChetna\backend\apps\advice\engine.py` — 4 paper rules |
| **Recurring detection** | `D:\DhanChetna\backend\apps\transactions\pattern_detector.py` — fuzzy matching |
| **Expense classifier** | `D:\DhanChetna\backend\apps\transactions\classifier.py` — minor/major/repetitive |
| **Audit logging** | `D:\DhanChetna\backend\apps\sync\signals.py` — post_save signals |
| **Sync push/pull** | `D:\DhanChetna\backend\apps\sync\views.py` — offline sync endpoints |
| **CSS design system** | `D:\DhanChetna\backend\static\css\style.css` — 800+ lines, dark/light |
| **Django settings** | `D:\DhanChetna\backend\pocketsense\settings.py` — DRF config, Firebase, etc. |
| **URL routing** | `D:\DhanChetna\backend\pocketsense\urls.py` — API v1 + web frontend |

---

## 📡 REST API Endpoints (if asked)

Open `http://127.0.0.1:8000/api/v1/` in browser (browsable API in debug mode).

| Endpoint | Method | What it does |
|----------|--------|-------------|
| `/api/v1/transactions/` | GET/POST | List/create transactions |
| `/api/v1/categories/` | GET/POST | List/create categories |
| `/api/v1/budgets/` | GET/POST | List/create budgets |
| `/api/v1/budgets/status_check/` | GET | Budget consumption check |
| `/api/v1/savings/` | GET/POST | List/create savings goals |
| `/api/v1/savings/{id}/deposit/` | PUT | Add money to jar |
| `/api/v1/summary/` | GET | Dashboard data |
| `/api/v1/analytics/category-split/` | GET | Pie chart data |
| `/api/v1/analytics/weekly/` | GET | Weekly trend |
| `/api/v1/advice/` | GET | Context-aware advice |
| `/api/v1/sync/push/` | POST | Upload offline transactions |
| `/api/v1/sync/pull/` | GET | Pull latest |
| `/admin/` | — | Django admin panel |

---

## 💬 Key Talking Points for the Viva

1. **"Why monolith?"** — Solo dev, modular Django apps can be extracted later. This is how GitHub and Shopify started.
2. **"Why Logistic Regression?"** — 87.3% accuracy, 0.8ms inference (18× faster than Random Forest), 43KB model vs 8.2MB.
3. **"Why rule-based recurring detection?"** — 88.4% precision, 91.2% recall, zero training data needed. LSTM needs 90+ days per user.
4. **"Why not Firebase for everything?"** — Firebase = auth door, Django = the house. We learn actual backend engineering.
5. **"Why PostgreSQL?"** — ACID compliance for financial data. SQLite for dev, Postgres for prod — one-line settings change.
6. **"What makes this different?"** — Context-aware: knows if you're a hostel student with meals provided. Generic trackers say "reduce food spending" — we say "your hostel provides meals, this might be compensatory spending."
