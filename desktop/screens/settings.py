"""
PocketSense — Settings Screen (Tkinter)
"""

import tkinter as tk
from theme import FONT_HEADING, FONT_MAIN, FONT_SMALL


class SettingsScreen(tk.Frame):
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

        hdr_ico = a.icon("settings", 26)
        self._icon_refs.append(hdr_ico)
        tk.Label(header, image=hdr_ico, bg=t["bg_primary"]).pack(side="left", padx=(8, 6))
        tk.Label(header, text="Settings", font=FONT_HEADING,
                 bg=t["bg_primary"], fg=t["text_primary"]).pack(side="left")

        card = tk.Frame(self, bg=t["bg_secondary"],
                         highlightbackground=t["border"], highlightthickness=1, padx=30, pady=25)
        card.pack(padx=20, pady=10, anchor="nw")

        # Theme toggle
        tk.Label(card, text="Appearance", font=("Segoe UI", 12, "bold"),
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(anchor="w")
        tk.Button(card, text="🌙 Toggle Theme", font=FONT_MAIN,
                  bg=t["bg_card"], fg=t["text_primary"], relief="flat", cursor="hand2",
                  padx=15, pady=6, command=self.app.toggle_theme).pack(anchor="w", pady=(5, 15))

        # Account info
        profile_ico = a.icon("profile", 22)
        self._icon_refs.append(profile_ico)
        acct_row = tk.Frame(card, bg=t["bg_secondary"])
        acct_row.pack(anchor="w")
        tk.Label(acct_row, image=profile_ico, bg=t["bg_secondary"]).pack(side="left", padx=(0, 6))
        tk.Label(acct_row, text="Account", font=("Segoe UI", 12, "bold"),
                 bg=t["bg_secondary"], fg=t["text_primary"]).pack(side="left")

        self.user_lbl = tk.Label(card, text="Logged in as: —", font=FONT_MAIN,
                                  bg=t["bg_secondary"], fg=t["text_secondary"])
        self.user_lbl.pack(anchor="w", pady=(5, 15))

        # Logout
        tk.Button(card, text="🚪 Logout", font=("Segoe UI", 11, "bold"),
                  bg=t["red"], fg="#fff", relief="flat", cursor="hand2",
                  padx=20, pady=8, command=self._logout).pack(anchor="w")

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        self._icon_refs.clear()
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def on_show(self, **kwargs):
        username = self.app.api.user or "—"
        self.user_lbl.config(text=f"Logged in as: {username}")

    def _logout(self):
        self.app.api.logout()
        self.app.show_screen("LoginScreen")
