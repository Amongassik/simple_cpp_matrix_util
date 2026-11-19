"""
themes.py — цветовые схемы для ttk-виджетов.
"""

import tkinter as tk
from tkinter import ttk


# Светлая тема
LIGHT = {
    "bg": "#f0f0f0",
    "fg": "#1e1e1e",
    "select_bg": "#0078d4",
    "select_fg": "#ffffff",
    "text_bg": "#ffffff",
    "text_fg": "#1e1e1e",
    "text_insert": "#000000",
    "button_bg": "#e1e1e1",
    "button_active_bg": "#d0d0d0",
    "panel_bg": "#ffffff",
    "panel_border": "#c0c0c0",
    "status_bg": "#e0e0e0",
    "status_fg": "#1e1e1e",
}

# Тёмная тема
DARK = {
    "bg": "#2b2b2b",
    "fg": "#e0e0e0",
    "select_bg": "#264f78",
    "select_fg": "#ffffff",
    "text_bg": "#1e1e1e",
    "text_fg": "#e0e0e0",
    "text_insert": "#ffffff",
    "button_bg": "#3c3c3c",
    "button_active_bg": "#4a4a4a",
    "panel_bg": "#252525",
    "panel_border": "#555555",
    "status_bg": "#333333",
    "status_fg": "#e0e0e0",
}


def apply_theme(root: tk.Tk, theme_name: str):
    palette = LIGHT if theme_name == "light" else DARK

    style = ttk.Style(root)

    style.theme_use("clam")

    root.configure(bg=palette["bg"])

    style.configure(
        "TButton",
        background=palette["button_bg"],
        foreground=palette["fg"],
        bordercolor=palette["panel_border"],
        focuscolor=palette["select_bg"],
        padding=4,
    )
    style.map(
        "TButton",
        background=[("active", palette["button_active_bg"])],
    )

    style.configure(
        "TLabel",
        background=palette["bg"],
        foreground=palette["fg"],
    )

    style.configure(
        "TFrame",
        background=palette["bg"],
    )

    style.configure(
        "TLabelframe",
        background=palette["bg"],
        foreground=palette["fg"],
        bordercolor=palette["panel_border"],
    )
    style.configure(
        "TLabelframe.Label",
        background=palette["bg"],
        foreground=palette["fg"],
    )

    style.configure(
        "TMenu",
        background=palette["panel_bg"],
        foreground=palette["fg"],
    )

    _paint_text_widgets(root, palette)


def _paint_text_widgets(widget, palette):
    """
    Рекурсивно находит все tk.Text, tk.Entry и перекрашивает их.
    """
    if isinstance(widget, tk.Text):
        widget.configure(
            bg=palette["text_bg"],
            fg=palette["text_fg"],
            insertbackground=palette["text_insert"],
            selectbackground=palette["select_bg"],
            selectforeground=palette["select_fg"],
        )
    elif isinstance(widget, tk.Entry):
        widget.configure(
            bg=palette["text_bg"],
            fg=palette["text_fg"],
            insertbackground=palette["text_insert"],
            selectbackground=palette["select_bg"],
            selectforeground=palette["select_fg"],
        )

    for child in widget.winfo_children():
        _paint_text_widgets(child, palette)