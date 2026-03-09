"""
PocketSense — Asset Loader
Loads, resizes, and caches PNG icons and sprite-sheet frames from assets/.
Requires Pillow (PIL).
"""

import os
from pathlib import Path
from PIL import Image, ImageTk

# Resolve paths relative to this file → project root
_DESKTOP_DIR = Path(__file__).resolve().parent
_PROJECT_DIR = _DESKTOP_DIR.parent
_ICONS_DIR = _PROJECT_DIR / "assets" / "icons"
_SPRITES_DIR = _PROJECT_DIR / "assets" / "sprites"


class AssetLoader:
    """Load and cache resized icons and sprite frames as PhotoImage objects."""

    def __init__(self):
        self._cache: dict[tuple, ImageTk.PhotoImage] = {}

    # ── Public API ───────────────────────────────────────

    def icon(self, name: str, size: int = 24) -> ImageTk.PhotoImage:
        """Load an icon from assets/icons/<name>.png, resized to size×size."""
        key = ("icon", name, size)
        if key not in self._cache:
            path = _ICONS_DIR / f"{name}.png"
            img = Image.open(path).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
            self._cache[key] = ImageTk.PhotoImage(img)
        return self._cache[key]

    def sprite_frame(
        self, name: str, cols: int, rows: int, index: int, size: int = 64
    ) -> ImageTk.PhotoImage:
        """Extract a single frame from a sprite sheet and resize it.

        Args:
            name:  sprite file stem, e.g. "less-savings"
            cols:  number of columns in the sprite sheet
            rows:  number of rows in the sprite sheet
            index: 0-based frame index (left-to-right, top-to-bottom)
            size:  target height/width in pixels
        """
        key = ("sprite", name, cols, rows, index, size)
        if key not in self._cache:
            path = _SPRITES_DIR / f"{name}.png"
            sheet = Image.open(path).convert("RGBA")
            fw = sheet.width // cols
            fh = sheet.height // rows
            col = index % cols
            row = index // cols
            frame = sheet.crop((col * fw, row * fh, (col + 1) * fw, (row + 1) * fh))
            frame = frame.resize((size, size), Image.LANCZOS)
            self._cache[key] = ImageTk.PhotoImage(frame)
        return self._cache[key]

    def sprite_frame_col_major(
        self, name: str, cols: int, rows: int, index: int, size: int = 64
    ) -> ImageTk.PhotoImage:
        """Extract a frame using column-major order (top-to-bottom, then next column).

        index 0→(row0,col0), 1→(row1,col0), …, rows→(row0,col1), etc.
        """
        key = ("sprite_cm", name, cols, rows, index, size)
        if key not in self._cache:
            path = _SPRITES_DIR / f"{name}.png"
            sheet = Image.open(path).convert("RGBA")
            fw = sheet.width // cols
            fh = sheet.height // rows
            col = index // rows
            row = index % rows
            frame = sheet.crop((col * fw, row * fh, (col + 1) * fw, (row + 1) * fh))
            frame = frame.resize((size, size), Image.LANCZOS)
            self._cache[key] = ImageTk.PhotoImage(frame)
        return self._cache[key]

    def savings_icon(self, pct: float, size: int = 64) -> ImageTk.PhotoImage:
        """Return the correct savings jar frame based on fill percentage.

        Sprite sheets (left-to-right, row-major):
            no-savings   → 4 cols × 3 rows (10 frames) — empty jar, cobwebs
            less-savings → 2 cols × 3 rows (6 frames)  — few coins
            more-savings → 2 cols × 3 rows (5 frames)  — half full
            full-savings → 2 cols × 2 rows (4 frames)  — overflowing
        """
        if pct <= 0:
            return self.sprite_frame("no-savings", cols=4, rows=3, index=0, size=size)
        elif pct < 33:
            return self.sprite_frame("less-savings", cols=2, rows=3, index=0, size=size)
        elif pct < 66:
            return self.sprite_frame("more-savings", cols=2, rows=3, index=0, size=size)
        else:
            return self.sprite_frame("full-savings", cols=2, rows=2, index=0, size=size)

    def wallet_icon(self, size: int = 80) -> ImageTk.PhotoImage:
        """Return the first frame of the wallet-opening sprite (top-to-bottom)."""
        return self.sprite_frame_col_major(
            "wallet-opening", cols=2, rows=4, index=0, size=size
        )
