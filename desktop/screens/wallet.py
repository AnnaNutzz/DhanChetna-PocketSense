"""
PocketSense — Wallet Screen (Tkinter)
Shows balance, total income/expenses.
"""

import tkinter as tk
from theme import FONT_HEADING, FONT_MAIN, FONT_SMALL, FONT_LARGE


class WalletScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg_primary"])
        self.app = app
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

        hdr_ico = a.icon("wallet", 26)
        self._icon_refs.append(hdr_ico)
        tk.Label(header, image=hdr_ico, bg=t["bg_primary"]).pack(side="left", padx=(8, 6))
        tk.Label(header, text="Wallet", font=FONT_HEADING,
                 bg=t["bg_primary"], fg=t["text_primary"]).pack(side="left")

        # Wallet card
        card = tk.Frame(self, bg=t["bg_secondary"],
                         highlightbackground=t["border"], highlightthickness=1,
                         padx=30, pady=30)
        card.pack(padx=20, pady=10)

        # Large wallet sprite
        wallet_img = a.wallet_icon(size=80)
        self._icon_refs.append(wallet_img)
        tk.Label(card, image=wallet_img, bg=t["bg_secondary"]).pack()

        tk.Label(card, text="Your Balance", font=("Segoe UI", 14),
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(pady=(5, 0))

        self.balance_lbl = tk.Label(card, text="₹0", font=("Segoe UI", 32, "bold"),
                                     bg=t["bg_secondary"], fg=t["accent"])
        self.balance_lbl.pack()

        # Income / Expense row
        row = tk.Frame(card, bg=t["bg_secondary"])
        row.pack(pady=20)

        inc_frame = tk.Frame(row, bg=t["bg_card"],
                              highlightbackground=t["border"], highlightthickness=1,
                              padx=20, pady=10)
        inc_frame.pack(side="left", padx=10)
        tk.Label(inc_frame, text="TOTAL INCOME", font=("Segoe UI", 8),
                 bg=t["bg_card"], fg=t["text_muted"]).pack()
        self.income_lbl = tk.Label(inc_frame, text="₹0", font=("Segoe UI", 16, "bold"),
                                    bg=t["bg_card"], fg=t["green"])
        self.income_lbl.pack()

        exp_frame = tk.Frame(row, bg=t["bg_card"],
                              highlightbackground=t["border"], highlightthickness=1,
                              padx=20, pady=10)
        exp_frame.pack(side="left", padx=10)
        tk.Label(exp_frame, text="TOTAL SPENT", font=("Segoe UI", 8),
                 bg=t["bg_card"], fg=t["text_muted"]).pack()
        self.expense_lbl = tk.Label(exp_frame, text="₹0", font=("Segoe UI", 16, "bold"),
                                     bg=t["bg_card"], fg=t["red"])
        self.expense_lbl.pack()

        # Action buttons
        btns = tk.Frame(self, bg=t["bg_primary"])
        btns.pack(pady=10)

        add_ico = a.icon("adding", 20)
        self._icon_refs.append(add_ico)
        income_ico = a.icon("income", 20)
        self._icon_refs.append(income_ico)

        tk.Button(btns, text=" Expense", image=add_ico, compound="left",
                  font=FONT_MAIN,
                  bg=t["red"], fg="#fff", relief="flat", cursor="hand2", padx=15, pady=6,
                  command=lambda: self.app.show_screen("AddTransactionScreen", txn_type="expense")
                  ).pack(side="left", padx=5)
        tk.Button(btns, text=" Income", image=income_ico, compound="left",
                  font=FONT_MAIN,
                  bg=t["accent"], fg="#fff", relief="flat", cursor="hand2", padx=15, pady=6,
                  command=lambda: self.app.show_screen("AddTransactionScreen", txn_type="income")
                  ).pack(side="left", padx=5)

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def on_show(self, **kwargs):
        try:
            data = self.app.api.get_transactions()
            results = data.get("results", data) if isinstance(data, dict) else data
            txns = results if isinstance(results, list) else []

            total_income = sum(float(t.get("amount", 0)) for t in txns if t.get("type") == "income")
            total_expenses = sum(float(t.get("amount", 0)) for t in txns if t.get("type") == "expense")
            balance = total_income - total_expenses

            self.balance_lbl.config(text=f"₹{balance:,.0f}")
            self.income_lbl.config(text=f"₹{total_income:,.0f}")
            self.expense_lbl.config(text=f"₹{total_expenses:,.0f}")
        except Exception:
            pass
