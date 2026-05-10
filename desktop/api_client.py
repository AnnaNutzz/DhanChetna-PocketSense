"""
PocketSense — API Client
Handles all HTTP communication with the Django backend.
Uses session auth (cookies) — same as the web frontend.
"""

import requests


class APIClient:
    """Thin wrapper around the Django backend REST API."""

    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.user = None

    # ── Helpers ──────────────────────────────────────────────

    def _url(self, path):
        return f"{self.base_url}{path}"

    def _get_csrf(self):
        """Fetch CSRF token from the login page cookie."""
        self.session.get(self._url("/login/"))
        return self.session.cookies.get("csrftoken", "")

    def _api_get(self, path, params=None):
        r = self.session.get(self._url(path), params=params)
        r.raise_for_status()
        return r.json()

    def _api_post(self, path, data=None, json_data=None):
        csrf = self.session.cookies.get("csrftoken", "")
        headers = {"X-CSRFToken": csrf}
        if json_data:
            headers["Content-Type"] = "application/json"
            r = self.session.post(self._url(path), json=json_data, headers=headers)
        else:
            r = self.session.post(self._url(path), data=data, headers=headers)
        r.raise_for_status()
        return r

    # ── Auth ─────────────────────────────────────────────────

    def login(self, username, password):
        """Login via Django session auth. Returns True on success."""
        csrf = self._get_csrf()
        r = self.session.post(
            self._url("/login/"),
            data={
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": csrf,
            },
            allow_redirects=False,
        )
        # Django redirects to dashboard on successful login
        if r.status_code in (301, 302) and "/login/" not in r.headers.get("Location", "/login/"):
            self.user = username
            return True
        return False

    def register(self, first_name, username, email, password):
        """Register a new account. Returns (success, error_msg)."""
        csrf = self._get_csrf()
        r = self.session.post(
            self._url("/register/"),
            data={
                "first_name": first_name,
                "username": username,
                "email": email,
                "password1": password,
                "password2": password,
                "csrfmiddlewaretoken": csrf,
            },
            allow_redirects=False,
        )
        if r.status_code in (301, 302) and "/register/" not in r.headers.get("Location", "/register/"):
            self.user = username
            return True, ""
        return False, "Registration failed. Username or email may already exist."

    def logout(self):
        self.session.get(self._url("/logout/"))
        self.user = None

    # ── Transactions (REST API) ──────────────────────────────

    def get_transactions(self, page=1, txn_type=None, category=None):
        params = {"page": page}
        if txn_type:
            params["type"] = txn_type
        if category:
            params["category"] = category
        return self._api_get("/api/v1/transactions/", params)

    def add_transaction(self, title, amount, txn_type, category_id=None, date=None, description=""):
        data = {
            "title": title,
            "amount": str(amount),
            "type": txn_type,
            "description": description,
        }
        if category_id:
            data["category"] = category_id
        if date:
            data["transaction_date"] = date
        return self._api_post("/api/v1/transactions/", json_data=data)

    def delete_transaction(self, txn_id):
        csrf = self.session.cookies.get("csrftoken", "")
        r = self.session.delete(
            self._url(f"/api/v1/transactions/{txn_id}/"),
            headers={"X-CSRFToken": csrf},
        )
        r.raise_for_status()
        return r

    # ── Categories ───────────────────────────────────────────

    def get_categories(self):
        return self._api_get("/api/v1/categories/")

    # ── Budgets ──────────────────────────────────────────────

    def get_budgets(self):
        return self._api_get("/api/v1/budgets/")

    def create_budget(self, limit_amount, period="monthly", category_id=None):
        data = {"limit_amount": str(limit_amount), "period": period}
        if category_id:
            data["category"] = category_id
        return self._api_post("/api/v1/budgets/", json_data=data)

    # ── Savings Goals ────────────────────────────────────────

    def get_savings_goals(self):
        return self._api_get("/api/v1/savings-goals/")

    def create_savings_goal(self, name, target_amount, target_date=None):
        data = {"name": name, "target_amount": str(target_amount)}
        if target_date:
            data["target_date"] = target_date
        return self._api_post("/api/v1/savings-goals/", json_data=data)

    def deposit_to_goal(self, goal_id, amount):
        return self._api_post(
            f"/api/v1/savings-goals/{goal_id}/deposit/",
            json_data={"amount": str(amount)},
        )

    # ── Analytics ────────────────────────────────────────────

    def get_dashboard_stats(self):
        return self._api_get("/api/v1/analytics/summary/")

    def get_category_split(self):
        """Category breakdown for current month (pie chart data)."""
        return self._api_get("/api/v1/analytics/category-split/")

    def get_weekly_trend(self):
        """Daily spending for last 7 days."""
        return self._api_get("/api/v1/analytics/weekly/")

    # ── Profile ──────────────────────────────────────────────

    def get_profile(self):
        return self._api_get("/api/v1/auth/profile/")

    def update_profile(self, data):
        return self._api_post("/api/v1/auth/profile/", json_data=data)
