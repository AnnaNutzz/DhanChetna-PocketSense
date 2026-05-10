"""
PocketSense — Analytics Screen (Tkinter)
Category breakdown bars, weekly spending chart, monthly summary.
Charts drawn on tk.Canvas — no external dependencies.
"""

import tkinter as tk
from theme import FONT_HEADING, FONT_MAIN, FONT_SMALL, FONT_ACCENT, FONT_LARGE

# Fallback palette when backend doesn't supply colors
_PALETTE = [
    "#6C5CE7", "#ff6b6b", "#2ecc71", "#f39c12",
    "#45b7d1", "#4ecdc4", "#e17055", "#a29bfe",
    "#fd79a8", "#00cec9", "#ffeaa7", "#dfe6e9",
]


class AnalyticsScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg_primary"])
        self.app = app
        self._icon_refs = []
        self._build()

    # ── Layout ───────────────────────────────────────────────

    def _build(self):
        t = self.app.theme

        # Scrollable canvas wrapper
        outer = tk.Frame(self, bg=t["bg_primary"])
        outer.pack(fill="both", expand=True)

        canvas = tk.Canvas(outer, bg=t["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=t["bg_primary"])

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        self._build_content(self.scroll_frame)

    def _build_content(self, parent):
        t = self.app.theme

        # Header
        header = tk.Frame(parent, bg=t["bg_primary"])
        header.pack(fill="x", padx=20, pady=(15, 10))

        a = self.app.assets
        back_ico = a.icon("back", 22)
        self._icon_refs.append(back_ico)
        tk.Button(
            header, image=back_ico, bg=t["bg_primary"], relief="flat", cursor="hand2",
            command=lambda: self.app.show_screen("DashboardScreen"),
        ).pack(side="left")

        hdr_ico = a.icon("analytics", 26)
        self._icon_refs.append(hdr_ico)
        tk.Label(header, image=hdr_ico, bg=t["bg_primary"]).pack(side="left", padx=(8, 6))
        tk.Label(
            header, text="Analytics", font=FONT_HEADING,
            bg=t["bg_primary"], fg=t["text_primary"],
        ).pack(side="left")

        # ── Monthly summary cards ────────────────────────────
        summary_card = tk.Frame(
            parent, bg=t["bg_secondary"],
            highlightbackground=t["border"], highlightthickness=1,
            padx=20, pady=15,
        )
        summary_card.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            summary_card, text="Monthly Summary",
            font=("Segoe UI", 12, "bold"),
            bg=t["bg_secondary"], fg=t["text_primary"],
        ).pack(anchor="w", pady=(0, 10))

        self.summary_row = tk.Frame(summary_card, bg=t["bg_secondary"])
        self.summary_row.pack(fill="x")

        self.stat_labels = {}
        for key, label, color in [
            ("spent", "TOTAL SPENT", t["red"]),
            ("income", "TOTAL INCOME", t["green"]),
            ("net", "NET", t["accent"]),
        ]:
            box = tk.Frame(
                self.summary_row, bg=t["bg_card"],
                highlightbackground=t["border"], highlightthickness=1,
                padx=18, pady=10,
            )
            box.pack(side="left", padx=5, fill="x", expand=True)

            tk.Label(
                box, text=label, font=("Segoe UI", 8),
                bg=t["bg_card"], fg=t["text_muted"],
            ).pack()
            val_lbl = tk.Label(
                box, text="₹0", font=("Segoe UI", 18, "bold"),
                bg=t["bg_card"], fg=color,
            )
            val_lbl.pack()
            self.stat_labels[key] = val_lbl

        # ── Category breakdown (horizontal bars) ─────────────
        cat_card = tk.Frame(
            parent, bg=t["bg_secondary"],
            highlightbackground=t["border"], highlightthickness=1,
            padx=20, pady=15,
        )
        cat_card.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            cat_card, text="Category Breakdown — This Month",
            font=("Segoe UI", 12, "bold"),
            bg=t["bg_secondary"], fg=t["text_primary"],
        ).pack(anchor="w", pady=(0, 10))

        self.cat_canvas = tk.Canvas(
            cat_card, bg=t["bg_secondary"],
            highlightthickness=0, height=200,
        )
        self.cat_canvas.pack(fill="x")

        self.cat_empty_lbl = tk.Label(
            cat_card, text="", font=FONT_SMALL,
            bg=t["bg_secondary"], fg=t["text_muted"],
        )
        self.cat_empty_lbl.pack()

        # ── Weekly trend (bar chart) ─────────────────────────
        week_card = tk.Frame(
            parent, bg=t["bg_secondary"],
            highlightbackground=t["border"], highlightthickness=1,
            padx=20, pady=15,
        )
        week_card.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            week_card, text="Daily Spending — Last 7 Days",
            font=("Segoe UI", 12, "bold"),
            bg=t["bg_secondary"], fg=t["text_primary"],
        ).pack(anchor="w", pady=(0, 10))

        self.week_canvas = tk.Canvas(
            week_card, bg=t["bg_secondary"],
            highlightthickness=0, height=220,
        )
        self.week_canvas.pack(fill="x")

        self.week_empty_lbl = tk.Label(
            week_card, text="", font=FONT_SMALL,
            bg=t["bg_secondary"], fg=t["text_muted"],
        )
        self.week_empty_lbl.pack()

    # ── Data refresh ─────────────────────────────────────────

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def on_show(self, **kwargs):
        self._load_summary()
        self._load_category_split()
        self._load_weekly_trend()

    def _load_summary(self):
        t = self.app.theme
        try:
            data = self.app.api.get_dashboard_stats()
            month = data.get("this_month", {})
            spent = month.get("total_spent", 0)
            income = month.get("total_income", 0)
            net = month.get("net", income - spent)

            self.stat_labels["spent"].config(text=f"₹{spent:,.0f}")
            self.stat_labels["income"].config(text=f"₹{income:,.0f}")
            self.stat_labels["net"].config(
                text=f"₹{net:,.0f}",
                fg=t["green"] if net >= 0 else t["red"],
            )
        except Exception:
            pass

    # ── Category horizontal bars ─────────────────────────────

    def _load_category_split(self):
        t = self.app.theme
        self.cat_canvas.delete("all")
        self.cat_empty_lbl.config(text="")

        try:
            data = self.app.api.get_category_split()
            cats = data if isinstance(data, list) else data.get("results", [])

            if not cats:
                self.cat_empty_lbl.config(text="No spending data this month.")
                self.cat_canvas.config(height=1)
                return

            max_total = max(c.get("total", 0) for c in cats) or 1
            bar_h = 26
            gap = 8
            canvas_h = len(cats) * (bar_h + gap) + gap
            self.cat_canvas.config(height=canvas_h)

            # Wait for canvas to render so winfo_width is available
            self.cat_canvas.update_idletasks()
            canvas_w = max(self.cat_canvas.winfo_width(), 400)
            label_w = 120
            amount_w = 80
            chart_w = canvas_w - label_w - amount_w - 20

            for i, cat in enumerate(cats):
                y = gap + i * (bar_h + gap)
                name = cat.get("category", "Other")
                total = cat.get("total", 0)
                color = cat.get("color", _PALETTE[i % len(_PALETTE)])
                bar_width = max(4, (total / max_total) * chart_w)

                # Category label
                self.cat_canvas.create_text(
                    label_w - 5, y + bar_h // 2,
                    text=name, anchor="e",
                    fill=t["text_primary"], font=("Segoe UI", 10),
                )

                # Bar
                self.cat_canvas.create_rectangle(
                    label_w, y, label_w + bar_width, y + bar_h,
                    fill=color, outline="",
                )

                # Amount label
                self.cat_canvas.create_text(
                    label_w + bar_width + 8, y + bar_h // 2,
                    text=f"₹{total:,.0f}", anchor="w",
                    fill=t["text_secondary"], font=("Segoe UI", 9, "bold"),
                )
        except Exception:
            self.cat_empty_lbl.config(text="Could not load category data.")
            self.cat_canvas.config(height=1)

    # ── Weekly bar chart ─────────────────────────────────────

    def _load_weekly_trend(self):
        t = self.app.theme
        self.week_canvas.delete("all")
        self.week_empty_lbl.config(text="")

        try:
            data = self.app.api.get_weekly_trend()
            days = data if isinstance(data, list) else data.get("results", [])

            if not days:
                self.week_empty_lbl.config(text="No spending data in the last 7 days.")
                self.week_canvas.config(height=1)
                return

            max_total = max(d.get("total", 0) for d in days) or 1
            self.week_canvas.update_idletasks()
            canvas_w = max(self.week_canvas.winfo_width(), 400)
            canvas_h = 220
            self.week_canvas.config(height=canvas_h)

            padding_bottom = 35
            padding_top = 15
            chart_h = canvas_h - padding_bottom - padding_top
            n = len(days)
            bar_total_w = canvas_w / max(n, 1)
            bar_w = max(20, bar_total_w * 0.6)
            bar_gap = (bar_total_w - bar_w) / 2

            for i, day in enumerate(days):
                total = day.get("total", 0)
                date_str = day.get("date", "")
                short_date = date_str[5:] if len(date_str) >= 10 else date_str

                bar_h = max(3, (total / max_total) * chart_h)
                x1 = i * bar_total_w + bar_gap
                x2 = x1 + bar_w
                y2 = canvas_h - padding_bottom
                y1 = y2 - bar_h

                # Bar (gradient effect: darker at bottom)
                self.week_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=t["accent"], outline=t["accent_hover"],
                )

                # Amount above bar
                self.week_canvas.create_text(
                    (x1 + x2) / 2, y1 - 5,
                    text=f"₹{total:,.0f}", anchor="s",
                    fill=t["text_secondary"],
                    font=("Segoe UI", 8, "bold"),
                )

                # Date label below bar
                self.week_canvas.create_text(
                    (x1 + x2) / 2, y2 + 5,
                    text=short_date, anchor="n",
                    fill=t["text_muted"], font=("Segoe UI", 8),
                )

            # Baseline
            base_y = canvas_h - padding_bottom
            self.week_canvas.create_line(
                0, base_y, canvas_w, base_y,
                fill=t["border"], width=1,
            )

        except Exception:
            self.week_empty_lbl.config(text="Could not load weekly data.")
            self.week_canvas.config(height=1)
