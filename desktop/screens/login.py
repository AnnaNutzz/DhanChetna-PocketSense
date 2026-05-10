"""
PocketSense — Login Screen (Tkinter)
Handles login and registration with the Django backend.
"""

import tkinter as tk
from tkinter import messagebox
from theme import FONT_HEADING, FONT_MAIN, FONT_LARGE


class LoginScreen(tk.Frame):
    """Login / Register screen — first thing the user sees."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg_primary"])
        self.app = app
        self._mode = "login"  # or "register"
        self._build()

    def _build(self):
        t = self.app.theme

        # Center card
        self.card = tk.Frame(self, bg=t["bg_secondary"], padx=40, pady=35,
                             highlightbackground=t["border"], highlightthickness=1)
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # Logo (custom asset)
        self._logo_img = self.app.assets.icon("logo", 72)
        self.logo_lbl = tk.Label(self.card, image=self._logo_img,
                                  bg=t["bg_secondary"])
        self.logo_lbl.pack(pady=(0, 5))

        self.title_lbl = tk.Label(self.card, text="Welcome Back",
                                   font=FONT_HEADING, bg=t["bg_secondary"],
                                   fg=t["text_primary"])
        self.title_lbl.pack()

        self.sub_lbl = tk.Label(self.card, text="Track smart. Save smarter.",
                                 font=("Segoe UI", 9), bg=t["bg_secondary"],
                                 fg=t["text_muted"])
        self.sub_lbl.pack(pady=(2, 20))

        # Error label
        self.error_lbl = tk.Label(self.card, text="", font=("Segoe UI", 9),
                                   bg=t["bg_secondary"], fg=t["red"], wraplength=280)
        self.error_lbl.pack()

        # Fields container
        self.fields = tk.Frame(self.card, bg=t["bg_secondary"])
        self.fields.pack(fill="x")

        # Name field (register only)
        self.name_lbl = tk.Label(self.fields, text="Name", font=("Segoe UI", 9),
                                  bg=t["bg_secondary"], fg=t["text_secondary"])
        self.name_entry = tk.Entry(self.fields, bg=t["bg_input"], fg=t["text_primary"],
                                    insertbackground=t["text_primary"], font=FONT_MAIN,
                                    relief="flat", highlightbackground=t["border"],
                                    highlightthickness=1, highlightcolor=t["accent"])

        # Email field (register only)
        self.email_lbl = tk.Label(self.fields, text="Email", font=("Segoe UI", 9),
                                   bg=t["bg_secondary"], fg=t["text_secondary"])
        self.email_entry = tk.Entry(self.fields, bg=t["bg_input"], fg=t["text_primary"],
                                     insertbackground=t["text_primary"], font=FONT_MAIN,
                                     relief="flat", highlightbackground=t["border"],
                                     highlightthickness=1, highlightcolor=t["accent"])

        # Username
        self.user_lbl = tk.Label(self.fields, text="Username", font=("Segoe UI", 9),
                                  bg=t["bg_secondary"], fg=t["text_secondary"])
        self.user_lbl.pack(anchor="w", pady=(10, 2))
        self.user_entry = tk.Entry(self.fields, bg=t["bg_input"], fg=t["text_primary"],
                                    insertbackground=t["text_primary"], font=FONT_MAIN,
                                    relief="flat", highlightbackground=t["border"],
                                    highlightthickness=1, highlightcolor=t["accent"])
        self.user_entry.pack(fill="x", ipady=6)

        # Password
        self.pass_lbl = tk.Label(self.fields, text="Password", font=("Segoe UI", 9),
                                  bg=t["bg_secondary"], fg=t["text_secondary"])
        self.pass_lbl.pack(anchor="w", pady=(10, 2))
        self.pass_entry = tk.Entry(self.fields, bg=t["bg_input"], fg=t["text_primary"],
                                    insertbackground=t["text_primary"], font=FONT_MAIN,
                                    relief="flat", show="•", highlightbackground=t["border"],
                                    highlightthickness=1, highlightcolor=t["accent"])
        self.pass_entry.pack(fill="x", ipady=6)

        # Submit button
        self.submit_btn = tk.Button(
            self.card, text="Sign In", font=("Segoe UI", 11, "bold"),
            bg=t["accent"], fg="#ffffff", relief="flat", cursor="hand2",
            activebackground=t["accent_hover"], activeforeground="#ffffff",
            command=self._submit,
        )
        self.submit_btn.pack(fill="x", ipady=8, pady=(20, 10))

        # Toggle link
        self.toggle_frame = tk.Frame(self.card, bg=t["bg_secondary"])
        self.toggle_frame.pack()
        self.toggle_text = tk.Label(self.toggle_frame, text="Don't have an account? ",
                                     font=("Segoe UI", 9), bg=t["bg_secondary"],
                                     fg=t["text_secondary"])
        self.toggle_text.pack(side="left")
        self.toggle_link = tk.Label(self.toggle_frame, text="Sign Up",
                                     font=("Segoe UI", 9, "underline"),
                                     bg=t["bg_secondary"], fg=t["accent"],
                                     cursor="hand2")
        self.toggle_link.pack(side="left")
        self.toggle_link.bind("<Button-1>", lambda e: self._toggle_mode())

        # ── Demo account button ──────────────────────────────
        demo_sep = tk.Frame(self.card, bg=t["border"], height=1)
        demo_sep.pack(fill="x", pady=(15, 10))

        self.demo_btn = tk.Button(
            self.card, text="🎮  Try Demo Account",
            font=("Segoe UI", 10), bg=t["bg_card"], fg=t["teal"],
            relief="flat", cursor="hand2",
            activebackground=t["bg_input"], activeforeground=t["teal"],
            command=self._demo_login,
        )
        self.demo_btn.pack(fill="x", ipady=6)

        tk.Label(
            self.card, text="No sign-up needed — explore with sample data",
            font=("Segoe UI", 8), bg=t["bg_secondary"], fg=t["text_muted"],
        ).pack(pady=(2, 0))

        # Bind Enter key
        self.pass_entry.bind("<Return>", lambda e: self._submit())
        self.user_entry.bind("<Return>", lambda e: self.pass_entry.focus())

    def _toggle_mode(self):
        self._mode = "register" if self._mode == "login" else "login"
        self.error_lbl.config(text="")

        if self._mode == "register":
            self.title_lbl.config(text="Create Account")
            self.sub_lbl.config(text="Start tracking your expenses today")
            self.submit_btn.config(text="Create Account")
            self.toggle_text.config(text="Already have an account? ")
            self.toggle_link.config(text="Sign In")
            # Show name and email fields
            self.name_lbl.pack(in_=self.fields, before=self.user_lbl, anchor="w", pady=(10, 2))
            self.name_entry.pack(in_=self.fields, before=self.user_lbl, fill="x", ipady=6)
            self.email_lbl.pack(in_=self.fields, before=self.user_lbl, anchor="w", pady=(10, 2))
            self.email_entry.pack(in_=self.fields, before=self.user_lbl, fill="x", ipady=6)
        else:
            self.title_lbl.config(text="Welcome Back")
            self.sub_lbl.config(text="Track smart. Save smarter.")
            self.submit_btn.config(text="Sign In")
            self.toggle_text.config(text="Don't have an account? ")
            self.toggle_link.config(text="Sign Up")
            self.name_lbl.pack_forget()
            self.name_entry.pack_forget()
            self.email_lbl.pack_forget()
            self.email_entry.pack_forget()

    def _submit(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            self.error_lbl.config(text="Please fill in all fields.")
            return

        try:
            if self._mode == "login":
                ok = self.app.api.login(username, password)
                if ok:
                    self.app.show_screen("DashboardScreen")
                else:
                    self.error_lbl.config(text="Invalid username or password.")
            else:
                name = self.name_entry.get().strip()
                email = self.email_entry.get().strip()
                if not name or not email:
                    self.error_lbl.config(text="Please fill in all fields.")
                    return
                ok, msg = self.app.api.register(name, username, email, password)
                if ok:
                    self.app.show_screen("DashboardScreen")
                else:
                    self.error_lbl.config(text=msg)
        except Exception as e:
            self.error_lbl.config(text=f"Connection error: {e}")

    def _demo_login(self):
        """One-click login with the demo account."""
        self.error_lbl.config(text="")
        self.user_entry.delete(0, "end")
        self.pass_entry.delete(0, "end")
        self.user_entry.insert(0, "demo")
        self.pass_entry.insert(0, "demo1234")
        self._submit()

    def apply_theme(self, theme):
        """Rebuild UI with updated theme colors."""
        self.configure(bg=theme["bg_primary"])
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def on_show(self, **kwargs):
        self.error_lbl.config(text="")
        self.user_entry.delete(0, "end")
        self.pass_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
