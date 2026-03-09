"""
PocketSense — Add Transaction Screen (Tkinter)
Shared screen for adding expenses and income.
"""

import tkinter as tk
from datetime import date
from theme import FONT_HEADING, FONT_MAIN, FONT_SMALL


class AddTransactionScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg_primary"])
        self.app = app
        self._txn_type = "expense"
        self._categories = []
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

        self._add_ico = a.icon("adding", 26)
        self._icon_refs.append(self._add_ico)
        self._income_ico = a.icon("income", 26)
        self._icon_refs.append(self._income_ico)

        self.hdr_icon_lbl = tk.Label(header, image=self._add_ico, bg=t["bg_primary"])
        self.hdr_icon_lbl.pack(side="left", padx=(8, 6))

        self.title_lbl = tk.Label(header, text="Add Expense", font=FONT_HEADING,
                                   bg=t["bg_primary"], fg=t["text_primary"])
        self.title_lbl.pack(side="left")

        # Form card
        self.card = tk.Frame(self, bg=t["bg_secondary"],
                              highlightbackground=t["border"], highlightthickness=1,
                              padx=30, pady=25)
        self.card.pack(padx=20, pady=10, anchor="w")

        # Title field
        tk.Label(self.card, text="Title", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w", pady=(0, 3))
        self.title_entry = tk.Entry(self.card, bg=t["bg_input"], fg=t["text_primary"],
                                     insertbackground=t["text_primary"], font=FONT_MAIN,
                                     relief="flat", width=40,
                                     highlightbackground=t["border"], highlightthickness=1,
                                     highlightcolor=t["accent"])
        self.title_entry.pack(fill="x", ipady=6)

        # Amount field
        tk.Label(self.card, text="Amount (₹)", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w", pady=(12, 3))
        self.amount_entry = tk.Entry(self.card, bg=t["bg_input"], fg=t["text_primary"],
                                      insertbackground=t["text_primary"], font=FONT_MAIN,
                                      relief="flat", width=40,
                                      highlightbackground=t["border"], highlightthickness=1,
                                      highlightcolor=t["accent"])
        self.amount_entry.pack(fill="x", ipady=6)

        # Category dropdown
        tk.Label(self.card, text="Category", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w", pady=(12, 3))
        self.cat_var = tk.StringVar(value="— Select —")
        self.cat_menu = tk.OptionMenu(self.card, self.cat_var, "— Select —")
        self.cat_menu.config(bg=t["bg_input"], fg=t["text_primary"], font=FONT_MAIN,
                              relief="flat", highlightbackground=t["border"],
                              highlightthickness=1, activebackground=t["bg_card"])
        self.cat_menu.pack(fill="x")

        # Date field
        tk.Label(self.card, text="Date", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w", pady=(12, 3))
        self.date_entry = tk.Entry(self.card, bg=t["bg_input"], fg=t["text_primary"],
                                    insertbackground=t["text_primary"], font=FONT_MAIN,
                                    relief="flat", width=40,
                                    highlightbackground=t["border"], highlightthickness=1,
                                    highlightcolor=t["accent"])
        self.date_entry.pack(fill="x", ipady=6)

        # Notes field
        tk.Label(self.card, text="Notes (optional)", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w", pady=(12, 3))
        self.notes_entry = tk.Entry(self.card, bg=t["bg_input"], fg=t["text_primary"],
                                     insertbackground=t["text_primary"], font=FONT_MAIN,
                                     relief="flat", width=40,
                                     highlightbackground=t["border"], highlightthickness=1,
                                     highlightcolor=t["accent"])
        self.notes_entry.pack(fill="x", ipady=6)

        # Error label
        self.error_lbl = tk.Label(self.card, text="", font=FONT_SMALL,
                                   bg=t["bg_secondary"], fg=t["red"])
        self.error_lbl.pack(pady=(10, 0))

        # Submit button
        self.submit_btn = tk.Button(self.card, text="Record Expense",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=t["red"], fg="#fff", relief="flat",
                                     cursor="hand2", padx=20, pady=8,
                                     command=self._submit)
        self.submit_btn.pack(fill="x", ipady=4, pady=(15, 0))

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def on_show(self, txn_type="expense", **kwargs):
        self._txn_type = txn_type
        t = self.app.theme

        if txn_type == "expense":
            self.title_lbl.config(text="Add Expense")
            self.hdr_icon_lbl.config(image=self._add_ico)
            self.submit_btn.config(text="Record Expense", bg=t["red"])
        else:
            self.title_lbl.config(text="Add Income")
            self.hdr_icon_lbl.config(image=self._income_ico)
            self.submit_btn.config(text="Record Income", bg=t["accent"])

        # Clear fields
        self.title_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, str(date.today()))
        self.notes_entry.delete(0, "end")
        self.error_lbl.config(text="")

        # Load categories
        try:
            cats = self.app.api.get_categories()
            cat_list = cats if isinstance(cats, list) else cats.get("results", [])
            self._categories = cat_list

            menu = self.cat_menu["menu"]
            menu.delete(0, "end")
            menu.add_command(label="— Select —", command=lambda: self.cat_var.set("— Select —"))
            for c in cat_list:
                name = c.get("name", "")
                menu.add_command(label=name, command=lambda n=name: self.cat_var.set(n))
        except Exception:
            pass

    def _submit(self):
        title = self.title_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        dt = self.date_entry.get().strip()
        notes = self.notes_entry.get().strip()
        cat_name = self.cat_var.get()

        if not title or not amount_str:
            self.error_lbl.config(text="Title and amount are required.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.error_lbl.config(text="Enter a valid positive amount.")
            return

        # Find category ID
        cat_id = None
        for c in self._categories:
            if c.get("name") == cat_name:
                cat_id = c.get("id")
                break

        try:
            self.app.api.add_transaction(
                title=title, amount=amount, txn_type=self._txn_type,
                category_id=cat_id, date=dt, description=notes,
            )
            self.app.show_screen("TransactionsScreen")
        except Exception as e:
            self.error_lbl.config(text=f"Error: {e}")
