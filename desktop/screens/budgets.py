"""
PocketSense — Budgets Screen (Tkinter)
"""

import tkinter as tk
from theme import FONT_HEADING, FONT_MAIN, FONT_SMALL, FONT_ACCENT


class BudgetsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg_primary"])
        self.app = app
        self._icon_refs = []
        self._build()

    def _build(self):
        t = self.app.theme
        a = self.app.assets

        header = tk.Frame(self, bg=t["bg_primary"])
        header.pack(fill="x", padx=20, pady=(15, 10))

        back_ico = a.icon("back", 22)
        self._icon_refs.append(back_ico)
        tk.Button(header, image=back_ico, bg=t["bg_primary"], relief="flat",
                  cursor="hand2",
                  command=lambda: self.app.show_screen("DashboardScreen")).pack(side="left")

        hdr_ico = a.icon("coin", 26)
        self._icon_refs.append(hdr_ico)
        tk.Label(header, image=hdr_ico, bg=t["bg_primary"]).pack(side="left", padx=(8, 6))
        tk.Label(header, text="Budgets", font=FONT_HEADING,
                 bg=t["bg_primary"], fg=t["text_primary"]).pack(side="left")

        add_ico = a.icon("adding", 18)
        self._icon_refs.append(add_ico)
        tk.Button(header, text=" New Budget", image=add_ico, compound="left",
                  font=FONT_SMALL, bg=t["accent"],
                  fg="#fff", relief="flat", cursor="hand2", padx=10, pady=4,
                  command=self._show_create).pack(side="right")

        self.list_frame = tk.Frame(self, bg=t["bg_primary"])
        self.list_frame.pack(fill="both", expand=True, padx=20)

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def on_show(self, **kwargs):
        t = self.app.theme
        for w in self.list_frame.winfo_children():
            w.destroy()
        try:
            data = self.app.api.get_budgets()
            budgets = data if isinstance(data, list) else data.get("results", [])
            if not budgets:
                coin_ico = self.app.assets.icon("coin", 48)
                self._icon_refs.append(coin_ico)
                tk.Label(self.list_frame, image=coin_ico,
                         bg=t["bg_primary"]).pack(pady=(30, 10))
                tk.Label(self.list_frame, text="No budgets set.", font=FONT_MAIN,
                         bg=t["bg_primary"], fg=t["text_muted"]).pack()
                return
            for b in budgets:
                self._render_budget(b)
        except Exception as e:
            tk.Label(self.list_frame, text=f"Error: {e}", font=FONT_SMALL,
                     bg=t["bg_primary"], fg=t["red"]).pack(pady=20)

    def _render_budget(self, b):
        t = self.app.theme
        card = tk.Frame(self.list_frame, bg=t["bg_secondary"],
                         highlightbackground=t["border"], highlightthickness=1, padx=20, pady=15)
        card.pack(fill="x", pady=5)

        cat = b.get("category_name", "Overall")
        limit = float(b.get("limit_amount", 0))
        spent = float(b.get("spent", 0))
        remaining = limit - spent
        pct = min(100, round(spent / limit * 100)) if limit > 0 else 0
        status = "over" if pct >= 100 else "warning" if pct >= 80 else "ok"
        colors = {"ok": t["green"], "warning": t["orange"], "over": t["red"]}

        top = tk.Frame(card, bg=t["bg_secondary"])
        top.pack(fill="x")

        # Show warning icon for over/warning budgets
        if status in ("over", "warning"):
            warn_ico = self.app.assets.icon("warning", 18)
            self._icon_refs.append(warn_ico)
            tk.Label(top, image=warn_ico, bg=t["bg_secondary"]).pack(side="left", padx=(0, 6))

        tk.Label(top, text=cat, font=("Segoe UI", 12, "bold"),
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(side="left")
        tk.Label(top, text=status.upper(), font=("Segoe UI", 8, "bold"),
                 bg=t["bg_secondary"], fg=colors[status]).pack(side="right")

        tk.Label(card, text=f"₹{spent:,.0f} / ₹{limit:,.0f}", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_muted"]).pack(anchor="w", pady=(8, 0))

        bar_bg = tk.Frame(card, bg=t["bg_input"], height=8)
        bar_bg.pack(fill="x", pady=(5, 0))
        bar_bg.pack_propagate(False)
        bar_fill = tk.Frame(bar_bg, bg=colors[status])
        bar_fill.place(relwidth=pct / 100, relheight=1.0)

        rem_color = t["green"] if remaining >= 0 else t["red"]
        tk.Label(card, text=f"₹{remaining:,.0f} remaining", font=FONT_ACCENT,
                 bg=t["bg_secondary"], fg=rem_color).pack(pady=(8, 0))

    def _show_create(self):
        t = self.app.theme
        d = tk.Toplevel(self)
        d.title("New Budget")
        d.geometry("320x250")
        d.configure(bg=t["bg_secondary"])
        d.resizable(False, False)
        d.transient(self)
        d.grab_set()

        hdr_ico = self.app.assets.icon("coin", 32)
        self._icon_refs.append(hdr_ico)
        tk.Label(d, image=hdr_ico, bg=t["bg_secondary"]).pack(pady=(15, 5))
        tk.Label(d, text="New Budget", font=FONT_HEADING,
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(pady=(0, 10))

        f = tk.Frame(d, bg=t["bg_secondary"], padx=20)
        f.pack(fill="x")

        tk.Label(f, text="Limit (₹)", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w")
        amt = tk.Entry(f, bg=t["bg_input"], fg=t["text_primary"], font=FONT_MAIN,
                       relief="flat", highlightbackground=t["border"], highlightthickness=1)
        amt.pack(fill="x", ipady=5)

        def create():
            try:
                val = float(amt.get().strip())
                if val > 0:
                    self.app.api.create_budget(val)
                    d.destroy()
                    self.on_show()
            except Exception:
                pass

        tk.Button(d, text="Create", font=("Segoe UI", 11, "bold"), bg=t["accent"],
                  fg="#fff", relief="flat", cursor="hand2", command=create).pack(pady=12)
