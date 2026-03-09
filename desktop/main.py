"""
PocketSense — Tkinter Desktop App
Entry point. Launches the themed expense tracker GUI.
"""

import sys
import os

# Add parent dir to path so we can import desktop modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import PocketSenseApp


def main():
    app = PocketSenseApp()
    app.mainloop()


if __name__ == "__main__":
    main()
