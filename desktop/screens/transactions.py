"""
PocketSense — Transactions Screen (Tkinter)
Scrollable list of all transactions with filters.
"""

import tkinter as tk
from theme import FONT_HEADING, FONT_MAIN, FONT_SMALL


class TransactionsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg_primary"])
        self.app = app
        self._page = 1
        self._icon_refs = []
        self._build()

    def _build(self):
        t = self.app.theme
        a = self.app.assets

        # Header
        header = tk.Frame(self, bg=t["bg_primary"])
        header.pack(fill="x", padx=20, pady=(15, 10))

        back_ico = a.icon("back", 22)
        self._icon_refs.append(back_ico)
        tk.Button(header, image=back_ico, bg=t["bg_primary"], relief="flat",
                  cursor="hand2", command=lambda: self.app.show_screen("DashboardScreen")
                  ).pack(side="left")

        hdr_ico = a.icon("cart", 26)
        self._icon_refs.append(hdr_ico)
        tk.Label(header, image=hdr_ico, bg=t["bg_primary"]).pack(side="left", padx=(8, 6))
        tk.Label(header, text="Transactions", font=FONT_HEADING,
                 bg=t["bg_primary"], fg=t["text_primary"]).pack(side="left")

        btn_frame = tk.Frame(header, bg=t["bg_primary"])
        btn_frame.pack(side="right")

        add_ico = a.icon("adding", 18)
        self._icon_refs.append(add_ico)
        income_ico = a.icon("income", 18)
        self._icon_refs.append(income_ico)

        tk.Button(btn_frame, text=" Expense", image=add_ico, compound="left",
                  font=FONT_SMALL,
                  bg=t["red"], fg="#fff", relief="flat", cursor="hand2", padx=10, pady=4,
                  command=lambda: self.app.show_screen("AddTransactionScreen", txn_type="expense")
                  ).pack(side="left", padx=3)
        tk.Button(btn_frame, text=" Income", image=income_ico, compound="left",
                  font=FONT_SMALL,
                  bg=t["accent"], fg="#fff", relief="flat", cursor="hand2", padx=10, pady=4,
                  command=lambda: self.app.show_screen("AddTransactionScreen", txn_type="income")
                  ).pack(side="left", padx=3)

        # Filter row
        filter_frame = tk.Frame(self, bg=t["bg_secondary"],
                                 highlightbackground=t["border"], highlightthickness=1,
                                 padx=15, pady=10)
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(filter_frame, text="Filter:", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_muted"]).pack(side="left")

        self.filter_var = tk.StringVar(value="all")
        for val, label in [("all", "All"), ("expense", "Expenses"), ("income", "Income")]:
            tk.Radiobutton(filter_frame, text=label, variable=self.filter_var,
                           value=val, font=FONT_SMALL, bg=t["bg_secondary"],
                           fg=t["text_secondary"], selectcolor=t["bg_card"],
                           activebackground=t["bg_secondary"],
                           command=self._refresh).pack(side="left", padx=5)

        # Scrollable list
        canvas = tk.Canvas(self, bg=t["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas, bg=t["bg_primary"])

        self.list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Pagination
        self.page_frame = tk.Frame(self, bg=t["bg_primary"])
        self.page_frame.pack(fill="x", padx=20, pady=10)

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _refresh(self):
        self._page = 1
        self.on_show()

    def on_show(self, **kwargs):
        t = self.app.theme
        for w in self.list_frame.winfo_children():
            w.destroy()

        try:
            ftype = self.filter_var.get()
            data = self.app.api.get_transactions(
                page=self._page,
                txn_type=ftype if ftype != "all" else None,
            )

            results = data.get("results", data) if isinstance(data, dict) else data
            txns = results if isinstance(results, list) else []

            if not txns:
                tk.Label(self.list_frame, text="No transactions found.",
                         font=FONT_MAIN, bg=t["bg_primary"],
                         fg=t["text_muted"]).pack(pady=30)
                return

            # Header row
            hdr = tk.Frame(self.list_frame, bg=t["bg_card"], padx=10, pady=6)
            hdr.pack(fill="x", pady=(0, 2))
            for col, w in [("Date", 12), ("Title", 20), ("Category", 12), ("Amount", 12)]:
                tk.Label(hdr, text=col, font=("Segoe UI", 8, "bold"), width=w,
                         bg=t["bg_card"], fg=t["text_muted"], anchor="w").pack(side="left")

            # Category icon mapping
            cat_icon_map = {
                "food": "food", "groceries": "cart", "transport": "travel",
                "travel": "travel", "shopping": "cart", "subscription": "subscription",
                "entertainment": "misc", "health": "misc", "bills": "recurring",
                "salary": "income", "freelance": "income", "investment": "income",
            }

            for tx in txns:
                row = tk.Frame(self.list_frame, bg=t["bg_secondary"],
                                highlightbackground=t["border"], highlightthickness=1,
                                padx=10, pady=6)
                row.pack(fill="x", pady=1)

                dt = tx.get("transaction_date", "")
                title = tx.get("title", "")
                cat = tx.get("category_name", "—")
                amt = float(tx.get("amount", 0))
                tx_type = tx.get("type", "expense")

                tk.Label(row, text=dt, font=FONT_SMALL, width=12,
                         bg=t["bg_secondary"], fg=t["text_secondary"], anchor="w").pack(side="left")
                tk.Label(row, text=title, font=FONT_MAIN, width=20,
                         bg=t["bg_secondary"], fg=t["text_primary"], anchor="w").pack(side="left")
                tk.Label(row, text=cat, font=FONT_SMALL, width=12,
                         bg=t["bg_secondary"], fg=t["text_muted"], anchor="w").pack(side="left")

                color = t["red"] if tx_type == "expense" else t["green"]
                sign = "-" if tx_type == "expense" else "+"
                tk.Label(row, text=f"{sign}₹{amt:,.2f}", font=("Segoe UI", 10, "bold"),
                         width=12, bg=t["bg_secondary"], fg=color, anchor="w").pack(side="left")

        except Exception as e:
            tk.Label(self.list_frame, text=f"Error loading: {e}",
                     font=FONT_SMALL, bg=t["bg_primary"],
                     fg=t["red"]).pack(pady=20)
