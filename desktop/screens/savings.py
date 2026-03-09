"""
PocketSense — Savings Screen (Tkinter)
Shows savings goals with progress bars, sprites, and deposit functionality.
"""

import tkinter as tk
from theme import FONT_HEADING, FONT_MAIN, FONT_SMALL, FONT_ACCENT


class SavingsScreen(tk.Frame):
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

        hdr_ico = a.icon("savejar", 26)
        self._icon_refs.append(hdr_ico)
        tk.Label(header, image=hdr_ico, bg=t["bg_primary"]).pack(side="left", padx=(8, 6))
        tk.Label(header, text="Savings Jar", font=FONT_HEADING,
                 bg=t["bg_primary"], fg=t["text_primary"]).pack(side="left", padx=0)

        add_ico = a.icon("adding", 18)
        self._icon_refs.append(add_ico)
        tk.Button(header, text=" New Goal", image=add_ico, compound="left",
                  font=FONT_SMALL,
                  bg=t["accent"], fg="#fff", relief="flat", cursor="hand2",
                  padx=10, pady=4, command=self._show_create_dialog
                  ).pack(side="right")

        # Scrollable goals
        canvas = tk.Canvas(self, bg=t["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.goals_frame = tk.Frame(canvas, bg=t["bg_primary"])

        self.goals_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.goals_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def on_show(self, **kwargs):
        t = self.app.theme
        for w in self.goals_frame.winfo_children():
            w.destroy()

        try:
            data = self.app.api.get_savings_goals()
            goals = data if isinstance(data, list) else data.get("results", [])

            if not goals:
                # Show empty jar sprite
                empty_img = self.app.assets.savings_icon(0, size=80)
                self._icon_refs.append(empty_img)
                tk.Label(self.goals_frame, image=empty_img,
                         bg=t["bg_primary"]).pack(pady=(30, 10))
                tk.Label(self.goals_frame, text="No savings goals yet.\nCreate one to start saving!",
                         font=FONT_MAIN, bg=t["bg_primary"], fg=t["text_muted"],
                         justify="center").pack(pady=(0, 20))
                return

            for g in goals:
                self._render_goal(g)

        except Exception as e:
            tk.Label(self.goals_frame, text=f"Error: {e}", font=FONT_SMALL,
                     bg=t["bg_primary"], fg=t["red"]).pack(pady=20)

    def _render_goal(self, goal):
        t = self.app.theme
        card = tk.Frame(self.goals_frame, bg=t["bg_secondary"],
                         highlightbackground=t["border"], highlightthickness=1,
                         padx=20, pady=15)
        card.pack(fill="x", pady=5)

        # Icon + info row
        row = tk.Frame(card, bg=t["bg_secondary"])
        row.pack(fill="x")

        # Calculate progress
        current = float(goal.get("current_amount", 0))
        target = float(goal.get("target_amount", 1))
        pct = min(100, round(current / target * 100)) if target > 0 else 0
        status = goal.get("status", "active")

        # Show appropriate savings sprite based on progress
        jar_img = self.app.assets.savings_icon(pct, size=56)
        self._icon_refs.append(jar_img)
        tk.Label(row, image=jar_img, bg=t["bg_secondary"]).pack(side="left", padx=(0, 15))

        info = tk.Frame(row, bg=t["bg_secondary"])
        info.pack(side="left", fill="x", expand=True)

        name = goal.get("name", "Goal")
        tk.Label(info, text=name, font=("Segoe UI", 13, "bold"),
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(anchor="w")
        tk.Label(info, text=f"₹{current:,.0f} / ₹{target:,.0f}",
                 font=FONT_ACCENT, bg=t["bg_secondary"], fg=t["accent"]).pack(anchor="w")

        # Progress bar
        bar_bg = tk.Frame(info, bg=t["bg_input"], height=8)
        bar_bg.pack(fill="x", pady=(5, 0))
        bar_bg.pack_propagate(False)

        fill_color = t["green"] if pct < 100 else t["accent"]
        bar_fill = tk.Frame(bar_bg, bg=fill_color)
        bar_fill.place(relwidth=pct / 100, relheight=1.0)

        tk.Label(info, text=f"{pct}% complete", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_muted"]).pack(anchor="w", pady=(3, 0))

        # Deposit form for active goals
        if status == "active":
            dep_frame = tk.Frame(card, bg=t["bg_secondary"])
            dep_frame.pack(fill="x", pady=(10, 0))

            dep_entry = tk.Entry(dep_frame, bg=t["bg_input"], fg=t["text_primary"],
                                  insertbackground=t["text_primary"], font=FONT_MAIN,
                                  relief="flat", width=15,
                                  highlightbackground=t["border"], highlightthickness=1)
            dep_entry.pack(side="left", ipady=4)
            dep_entry.insert(0, "Amount")

            coin_ico = self.app.assets.icon("coin", 18)
            self._icon_refs.append(coin_ico)
            goal_id = goal.get("id")
            tk.Button(dep_frame, text=" Deposit", image=coin_ico, compound="left",
                      font=FONT_SMALL,
                      bg=t["accent"], fg="#fff", relief="flat", cursor="hand2",
                      padx=10, pady=4,
                      command=lambda eid=goal_id, e=dep_entry: self._deposit(eid, e)
                      ).pack(side="left", padx=(8, 0))
        elif status == "completed":
            tk.Label(card, text="🎉 Goal completed!", font=("Segoe UI", 11, "bold"),
                     bg=t["bg_secondary"], fg=t["green"]).pack(anchor="w", pady=(8, 0))

    def _deposit(self, goal_id, entry):
        try:
            amount = float(entry.get())
            if amount <= 0:
                return
            self.app.api.deposit_to_goal(goal_id, amount)
            self.on_show()
        except (ValueError, Exception):
            pass

    def _show_create_dialog(self):
        t = self.app.theme
        dialog = tk.Toplevel(self)
        dialog.title("New Savings Goal")
        dialog.geometry("350x280")
        dialog.configure(bg=t["bg_secondary"])
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        hdr_ico = self.app.assets.icon("savejar", 32)
        self._icon_refs.append(hdr_ico)
        tk.Label(dialog, image=hdr_ico, bg=t["bg_secondary"]).pack(pady=(15, 5))
        tk.Label(dialog, text="New Savings Goal", font=FONT_HEADING,
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(pady=(0, 10))

        fields = tk.Frame(dialog, bg=t["bg_secondary"], padx=20)
        fields.pack(fill="x")

        tk.Label(fields, text="Goal Name", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w", pady=(5, 2))
        name_entry = tk.Entry(fields, bg=t["bg_input"], fg=t["text_primary"],
                               font=FONT_MAIN, relief="flat",
                               highlightbackground=t["border"], highlightthickness=1)
        name_entry.pack(fill="x", ipady=5)

        tk.Label(fields, text="Target Amount (₹)", font=FONT_SMALL,
                 bg=t["bg_secondary"], fg=t["text_secondary"]).pack(anchor="w", pady=(10, 2))
        amount_entry = tk.Entry(fields, bg=t["bg_input"], fg=t["text_primary"],
                                 font=FONT_MAIN, relief="flat",
                                 highlightbackground=t["border"], highlightthickness=1)
        amount_entry.pack(fill="x", ipady=5)

        def create():
            name = name_entry.get().strip()
            try:
                target = float(amount_entry.get().strip())
            except ValueError:
                return
            if name and target > 0:
                try:
                    self.app.api.create_savings_goal(name, target)
                    dialog.destroy()
                    self.on_show()
                except Exception:
                    pass

        tk.Button(dialog, text="Create Goal", font=("Segoe UI", 11, "bold"),
                  bg=t["accent"], fg="#fff", relief="flat", cursor="hand2",
                  padx=20, pady=8, command=create).pack(pady=15)
