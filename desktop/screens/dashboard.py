"""
PocketSense — Dashboard Screen (Tkinter)
Shows stats, recent transactions, and quick actions.
"""

import tkinter as tk
from theme import FONT_HEADING, FONT_MAIN, FONT_LARGE, FONT_ACCENT, FONT_SMALL


class DashboardScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg_primary"])
        self.app = app
        self._icon_refs = []  # prevent GC of PhotoImage objects
        self._build()

    def _build(self):
        t = self.app.theme

        # Scrollable canvas
        canvas = tk.Canvas(self, bg=t["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=t["bg_primary"])

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._build_content(self.scroll_frame)

    def _build_content(self, parent):
        t = self.app.theme
        a = self.app.assets

        # ── Top bar (hamburger + logo + gear) ────────────
        topbar = tk.Frame(parent, bg=t["bg_secondary"], pady=10, padx=20)
        topbar.pack(fill="x", pady=(0, 15))

        # Hamburger button
        tk.Button(topbar, text="☰", font=("Segoe UI", 18),
                  bg=t["bg_secondary"], fg=t["text_primary"],
                  relief="flat", cursor="hand2", bd=0,
                  command=self._open_sidebar).pack(side="left")

        # Logo + brand
        logo_img = a.icon("logo", 28)
        self._icon_refs.append(logo_img)
        tk.Label(topbar, image=logo_img, bg=t["bg_secondary"]).pack(side="left", padx=(10, 6))
        tk.Label(topbar, text="PocketSense", font=FONT_HEADING,
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(side="left")

        # Settings gear
        gear_ico = a.icon("settings", 20)
        self._icon_refs.append(gear_ico)
        tk.Button(topbar, image=gear_ico,
                  bg=t["bg_secondary"], relief="flat", cursor="hand2",
                  command=lambda: self.app.show_screen("SettingsScreen")
                  ).pack(side="right")

        # ── Greeting ─────────────────────────────────────
        self.greeting_lbl = tk.Label(parent, text="Good evening 👋",
                                      font=("Segoe UI", 20, "bold"),
                                      bg=t["bg_primary"], fg=t["text_primary"])
        self.greeting_lbl.pack(anchor="w", padx=20, pady=(10, 5))

        tk.Label(parent, text="Here's your financial snapshot",
                 font=FONT_SMALL, bg=t["bg_primary"],
                 fg=t["text_muted"]).pack(anchor="w", padx=20)

        # ── Stats row ────────────────────────────────────
        stats_frame = tk.Frame(parent, bg=t["bg_primary"])
        stats_frame.pack(fill="x", padx=20, pady=15)

        self.stat_cards = {}
        for i, (key, label, color) in enumerate([
            ("today_spent", "SPENT TODAY", t["red"]),
            ("month_income", "MONTH INCOME", t["green"]),
            ("month_expenses", "MONTH EXPENSES", t["red"]),
            ("wallet_balance", "WALLET BALANCE", t["accent"]),
        ]):
            card = tk.Frame(stats_frame, bg=t["bg_secondary"],
                            highlightbackground=t["border"], highlightthickness=1,
                            padx=15, pady=12)
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            stats_frame.grid_columnconfigure(i, weight=1)

            # Color bar
            bar = tk.Frame(card, bg=color, width=4, height=50)
            bar.pack(side="left", fill="y", padx=(0, 10))

            info = tk.Frame(card, bg=t["bg_secondary"])
            info.pack(side="left", fill="both", expand=True)

            tk.Label(info, text=label, font=("Segoe UI", 8),
                     bg=t["bg_secondary"], fg=t["text_muted"]).pack(anchor="w")
            val_lbl = tk.Label(info, text="₹0", font=FONT_ACCENT,
                                bg=t["bg_secondary"], fg=color)
            val_lbl.pack(anchor="w")
            self.stat_cards[key] = val_lbl

        # ── Quick actions ────────────────────────────────
        qa_frame = tk.Frame(parent, bg=t["bg_primary"])
        qa_frame.pack(fill="x", padx=20, pady=(0, 15))

        qa_items = [
            ("adding", "Add Expense", lambda: self.app.show_screen("AddTransactionScreen", txn_type="expense")),
            ("income", "Add Income",  lambda: self.app.show_screen("AddTransactionScreen", txn_type="income")),
            ("savejar", "Savings Jar",  lambda: self.app.show_screen("SavingsScreen")),
            ("cart",    "Transactions",  lambda: self.app.show_screen("TransactionsScreen")),
        ]

        for icon_name, label, cmd in qa_items:
            ico = a.icon(icon_name, 22)
            self._icon_refs.append(ico)
            b = tk.Button(qa_frame, text=f" {label}", image=ico, compound="left",
                          font=FONT_MAIN,
                          bg=t["bg_card"], fg=t["text_primary"],
                          relief="flat", cursor="hand2", padx=15, pady=10,
                          command=cmd)
            b.pack(side="left", padx=5)

        # ── Recent transactions ──────────────────────────
        recent_card = tk.Frame(parent, bg=t["bg_secondary"],
                                highlightbackground=t["border"], highlightthickness=1,
                                padx=20, pady=15)
        recent_card.pack(fill="x", padx=20, pady=(0, 15))

        # Section header with icon
        txn_ico = a.icon("cart", 20)
        self._icon_refs.append(txn_ico)
        hdr_row = tk.Frame(recent_card, bg=t["bg_secondary"])
        hdr_row.pack(anchor="w", pady=(0, 10))
        tk.Label(hdr_row, image=txn_ico, bg=t["bg_secondary"]).pack(side="left", padx=(0, 6))
        tk.Label(hdr_row, text="Recent Transactions", font=("Segoe UI", 12, "bold"),
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(side="left")

        self.recent_frame = tk.Frame(recent_card, bg=t["bg_secondary"])
        self.recent_frame.pack(fill="x")

        self.no_txn_lbl = tk.Label(self.recent_frame, text="No transactions yet.",
                                    font=FONT_SMALL, bg=t["bg_secondary"],
                                    fg=t["text_muted"])
        self.no_txn_lbl.pack()

    def on_show(self, **kwargs):
        """Refresh dashboard data from the API."""
        try:
            data = self.app.api.get_transactions(page=1)
            results = data.get("results", data) if isinstance(data, dict) else data

            # Calculate basic stats from transactions
            from datetime import date
            today = date.today()
            month_start = today.replace(day=1)

            today_spent = 0
            month_income = 0
            month_expenses = 0
            total_income = 0
            total_expenses = 0

            txns = results if isinstance(results, list) else []

            for tx in txns:
                amt = float(tx.get("amount", 0))
                tx_date = tx.get("transaction_date", "")
                tx_type = tx.get("type", "")

                if tx_type == "expense":
                    total_expenses += amt
                    if tx_date == str(today):
                        today_spent += amt
                    if tx_date >= str(month_start):
                        month_expenses += amt
                elif tx_type == "income":
                    total_income += amt
                    if tx_date >= str(month_start):
                        month_income += amt

            wallet_balance = total_income - total_expenses

            self.stat_cards["today_spent"].config(text=f"₹{today_spent:,.0f}")
            self.stat_cards["month_income"].config(text=f"₹{month_income:,.0f}")
            self.stat_cards["month_expenses"].config(text=f"₹{month_expenses:,.0f}")
            self.stat_cards["wallet_balance"].config(text=f"₹{wallet_balance:,.0f}")

            # Recent list
            for w in self.recent_frame.winfo_children():
                w.destroy()

            recent = txns[:5]
            if recent:
                t = self.app.theme
                for tx in recent:
                    row = tk.Frame(self.recent_frame, bg=t["bg_secondary"])
                    row.pack(fill="x", pady=2)

                    title = tx.get("title", "")
                    amt = float(tx.get("amount", 0))
                    tx_type = tx.get("type", "expense")
                    cat = tx.get("category_name", "")
                    dt = tx.get("transaction_date", "")

                    tk.Label(row, text=f"{title}", font=FONT_MAIN,
                             bg=t["bg_secondary"], fg=t["text_primary"]).pack(side="left")
                    tk.Label(row, text=f"  {cat} · {dt}", font=FONT_SMALL,
                             bg=t["bg_secondary"], fg=t["text_muted"]).pack(side="left")

                    color = t["red"] if tx_type == "expense" else t["green"]
                    sign = "-" if tx_type == "expense" else "+"
                    tk.Label(row, text=f"{sign}₹{amt:,.0f}", font=("Segoe UI", 11, "bold"),
                             bg=t["bg_secondary"], fg=color).pack(side="right")
            else:
                tk.Label(self.recent_frame, text="No transactions yet. Start tracking!",
                         font=FONT_SMALL, bg=self.app.theme["bg_secondary"],
                         fg=self.app.theme["text_muted"]).pack()

        except Exception:
            # If API fails, show defaults
            pass

    # ── Sidebar ───────────────────────────────────────

    def _open_sidebar(self):
        """Create and display the sidebar overlay."""
        if hasattr(self, "_sidebar_overlay") and self._sidebar_overlay:
            return  # already open

        t = self.app.theme
        a = self.app.assets

        # Semi-transparent overlay (click to close)
        self._sidebar_overlay = tk.Frame(self, bg=t["bg_primary"])
        self._sidebar_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._sidebar_overlay.bind("<Button-1>", lambda e: self._close_sidebar())

        # Sidebar panel
        sidebar = tk.Frame(self._sidebar_overlay, bg=t["bg_secondary"],
                           padx=20, pady=15)
        sidebar.place(relx=0, rely=0, relwidth=0.35, relheight=1)
        sidebar.bind("<Button-1>", lambda e: "break")  # prevent closing on sidebar click

        # Back arrow
        back_ico = a.icon("back", 22)
        self._icon_refs.append(back_ico)
        tk.Button(sidebar, image=back_ico, bg=t["bg_secondary"], relief="flat",
                  cursor="hand2", command=self._close_sidebar
                  ).pack(anchor="e", pady=(0, 15))

        # Main nav items
        main_nav = [
            ("profile",    "Profile",     "SettingsScreen"),
            ("wallet",     "Wallet",      "WalletScreen"),
            ("analytics",  "Analytics",   "AnalyticsScreen"),
            ("savejar",    "Savings jar", "SavingsScreen"),
        ]
        for icon_name, label, screen in main_nav:
            ico = a.icon(icon_name, 22)
            self._icon_refs.append(ico)
            btn = tk.Button(sidebar, text=f"  {label}", image=ico, compound="left",
                            font=FONT_MAIN, anchor="w",
                            bg=t["bg_secondary"], fg=t["text_primary"],
                            relief="flat", cursor="hand2", padx=5, pady=8,
                            command=lambda s=screen: self._nav_to(s))
            btn.pack(fill="x")

        # Separator
        tk.Frame(sidebar, bg=t["border"], height=1).pack(fill="x", pady=15)

        # Secondary nav items
        secondary_nav = [
            ("sync",       "Sync"),
            ("settings",   "Settings"),
            ("profile",    "Support"),
            ("ai",         "AI Advice"),
        ]
        for icon_name, label in secondary_nav:
            ico = a.icon(icon_name, 20)
            self._icon_refs.append(ico)
            btn = tk.Button(sidebar, text=f"  {label}", image=ico, compound="left",
                            font=FONT_SMALL, anchor="w",
                            bg=t["bg_secondary"], fg=t["text_secondary"],
                            relief="flat", cursor="hand2", padx=5, pady=6,
                            command=lambda l=label: self._nav_to(
                                "SettingsScreen" if l == "Settings" else None))
            btn.pack(fill="x")

        # Theme toggle at the bottom
        toggle_frame = tk.Frame(sidebar, bg=t["bg_secondary"])
        toggle_frame.pack(side="bottom", fill="x", pady=(15, 5))

        theme_icon = "☀️" if t["name"] == "dark" else "🌙"
        theme_label = "Light Mode" if t["name"] == "dark" else "Dark Mode"
        tk.Button(toggle_frame, text=f" {theme_icon}  {theme_label}",
                  font=FONT_MAIN, anchor="w",
                  bg=t["bg_card"], fg=t["text_primary"],
                  relief="flat", cursor="hand2", padx=15, pady=8,
                  command=self._toggle_theme_from_sidebar
                  ).pack(fill="x")

    def _close_sidebar(self):
        """Remove the sidebar overlay."""
        if hasattr(self, "_sidebar_overlay") and self._sidebar_overlay:
            self._sidebar_overlay.destroy()
            self._sidebar_overlay = None

    def _nav_to(self, screen_name):
        """Close sidebar and navigate to a screen."""
        self._close_sidebar()
        if screen_name:
            self.app.show_screen(screen_name)

    def _toggle_theme_from_sidebar(self):
        """Toggle theme and reopen sidebar so it reflects the new colors."""
        self._close_sidebar()
        self.app.toggle_theme()

    # ── Theme ────────────────────────────────────────

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _logout(self):
        self.app.api.logout()
        self.app.show_screen("LoginScreen")
