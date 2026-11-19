"""
safety.py — единая точка обработки ошибок в GUI.
"""

import functools
from tkinter import messagebox


def safe_call(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            _report_status(self, f"Ошибка ввода: {e}")
            return None
        except RuntimeError as e:
            messagebox.showerror("Ошибка операции", str(e))
            _report_status(self, f"Ошибка операции: {e}")
            return None

    return wrapper


def _report_status(obj, message):
    if hasattr(obj, "set_status"):
        obj.set_status(message, error=True)
    elif hasattr(obj, "_on_status"):
        obj._on_status(message, error=True)