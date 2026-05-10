"""
PocketSense — Tkinter Application Shell
Root window, theme engine, and screen manager.
"""

import tkinter as tk
from theme import DARK, LIGHT, FONT_MAIN, FONT_HEADING
from api_client import APIClient


class PocketSenseApp(tk.Tk):
    """Root application window — manages screens and theme."""

    def __init__(self):
        super().__init__()

        self.title("PocketSense — Smart Expense Tracker")
        self.geometry("1000x700")
        self.minsize(800, 600)
        self.configure(bg=DARK["bg_primary"])

        # State
        self.api = APIClient()
        self.theme = DARK
        self._screens = {}
        self._current = None

        # Asset loader for icons and sprites
        from asset_loader import AssetLoader
        self.assets = AssetLoader()

        # Container for all screens
        self.container = tk.Frame(self, bg=self.theme["bg_primary"])
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Register screens (lazy import to avoid circular deps)
        from screens.login import LoginScreen
        from screens.dashboard import DashboardScreen
        from screens.transactions import TransactionsScreen
        from screens.add_transaction import AddTransactionScreen
        from screens.wallet import WalletScreen
        from screens.savings import SavingsScreen
        from screens.budgets import BudgetsScreen
        from screens.settings import SettingsScreen
        from screens.analytics import AnalyticsScreen

        for ScreenClass in (
            LoginScreen, DashboardScreen, TransactionsScreen,
            AddTransactionScreen, WalletScreen, SavingsScreen,
            BudgetsScreen, SettingsScreen, AnalyticsScreen,
        ):
            screen = ScreenClass(self.container, self)
            self._screens[ScreenClass.__name__] = screen
            screen.grid(row=0, column=0, sticky="nsew")

        self.show_screen("LoginScreen")

    # ── Screen Navigation ────────────────────────────────────

    def show_screen(self, name, **kwargs):
        """Switch to a screen by class name."""
        screen = self._screens[name]
        if hasattr(screen, "on_show"):
            screen.on_show(**kwargs)
        screen.tkraise()
        self._current = name

    # ── Theme ────────────────────────────────────────────────

    def toggle_theme(self):
        """Switch between dark and light themes."""
        self.theme = LIGHT if self.theme["name"] == "dark" else DARK
        self.configure(bg=self.theme["bg_primary"])
        self.container.configure(bg=self.theme["bg_primary"])
        for screen in self._screens.values():
            if hasattr(screen, "apply_theme"):
                screen.apply_theme(self.theme)
        # Re-show the current screen so it's on top and data refreshes
        if self._current:
            self.show_screen(self._current)

    # ── Helpers ──────────────────────────────────────────────

    def make_card(self, parent, **kw):
        """Create a styled card frame."""
        return tk.Frame(
            parent,
            bg=self.theme["bg_secondary"],
            highlightbackground=self.theme["border"],
            highlightthickness=1,
            padx=20, pady=15,
            **kw,
        )

    def make_button(self, parent, text, command, style="primary", **kw):
        """Create a styled button."""
        colors = {
            "primary": (self.theme["accent"], "#ffffff"),
            "danger": (self.theme["red"], "#ffffff"),
            "outline": (self.theme["bg_secondary"], self.theme["accent"]),
        }
        bg, fg = colors.get(style, colors["primary"])
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg, fg=fg,
            font=FONT_MAIN,
            relief="flat",
            cursor="hand2",
            padx=20, pady=8,
            activebackground=self.theme["accent_hover"],
            activeforeground="#ffffff",
            **kw,
        )
        return btn

    def make_entry(self, parent, placeholder="", show=None, **kw):
        """Create a styled entry field."""
        entry = tk.Entry(
            parent,
            bg=self.theme["bg_input"],
            fg=self.theme["text_primary"],
            insertbackground=self.theme["text_primary"],
            font=FONT_MAIN,
            relief="flat",
            highlightbackground=self.theme["border"],
            highlightthickness=1,
            highlightcolor=self.theme["accent"],
            **kw,
        )
        if show:
            entry.configure(show=show)
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg=self.theme["text_muted"])
            entry.bind("<FocusIn>", lambda e: _on_focus_in(e, placeholder))
            entry.bind("<FocusOut>", lambda e: _on_focus_out(e, placeholder))
        return entry

    def make_label(self, parent, text, style="normal", **kw):
        """Create a styled label."""
        fonts = {
            "normal": FONT_MAIN,
            "heading": FONT_HEADING,
            "muted": ("Segoe UI", 9),
        }
        colors = {
            "normal": self.theme["text_primary"],
            "heading": self.theme["text_primary"],
            "muted": self.theme["text_muted"],
        }
        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=colors.get(style, self.theme["text_primary"]),
            font=fonts.get(style, FONT_MAIN),
            **kw,
        )


def _on_focus_in(event, placeholder):
    w = event.widget
    if w.get() == placeholder:
        w.delete(0, "end")
        w.config(fg=w.master.master.master.theme["text_primary"]
                 if hasattr(w.master, "master") else "#ffffff")


def _on_focus_out(event, placeholder):
    w = event.widget
    if not w.get():
        w.insert(0, placeholder)
        w.config(fg=w.master.master.master.theme["text_muted"]
                 if hasattr(w.master, "master") else "#8888aa")
