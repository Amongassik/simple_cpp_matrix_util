"""
app.py — класс MatrixApp: макет, меню, обработчики операций.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from .parsing import (
    load_matrix_from_file,
    save_matrix_to_file,
)
from .safety import safe_call
from .themes import apply_theme
from .widgets import MatrixPanel, OperationPanel


class MatrixApp:
    """Корневое окно и вся логика приложения."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Матричный калькулятор")
        self.root.geometry("1100x780")
        self.root.minsize(900, 600)

        self.current_theme = "light"

        self._build_menu()
        self._build_layout()

        apply_theme(self.root, self.current_theme)

    # ---------- макет ----------

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть в A...", command=self.on_open_a)
        file_menu.add_command(label="Открыть в B...", command=self.on_open_b)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить C...", command=self.on_save_c)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        theme_menu = tk.Menu(menubar, tearoff=0)
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_menu.add_radiobutton(
            label="Светлая", variable=self.theme_var,
            value="light", command=self.on_theme_change,
        )
        theme_menu.add_radiobutton(
            label="Тёмная", variable=self.theme_var,
            value="dark", command=self.on_theme_change,
        )
        menubar.add_cascade(label="Тема", menu=theme_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.on_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.root.config(menu=menubar)

    def _build_layout(self):
        self.status_var = tk.StringVar(value="Готово")
        self.status = ttk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            relief="sunken",
            padding=(6, 3),
        )
        self.status.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.panel_a = MatrixPanel(self.root, "Матрица A", on_status=self.set_status)
        self.panel_a.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        self.panel_b = MatrixPanel(self.root, "Матрица B", on_status=self.set_status)
        self.panel_b.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        self.ops = OperationPanel(self.root, {
            "add":     self.on_add,
            "mul":     self.on_mul,
            "iadd":    self.on_iadd,
            "a_to_c":  self.on_a_to_c,
            "b_to_c":  self.on_b_to_c,
            "swap":    self.on_swap,
        })
        self.ops.grid(row=1, column=0, columnspan=2, padx=6, pady=6, sticky="ew")

        self.panel_c = MatrixPanel(self.root, "Результат C", on_status=self.set_status)
        self.panel_c.grid(row=2, column=0, columnspan=2, padx=6, pady=6, sticky="nsew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

    # ---------- статус ----------

    def set_status(self, msg, error=False):
        self.status_var.set(msg)
        if error:
            self.status.configure(foreground="red")
        else:
            self.status.configure(foreground="")

    # ---------- операции ----------

    @safe_call
    def on_add(self):
        with self.panel_a.get_matrix() as a, self.panel_b.get_matrix() as b:
            with a + b as c:
                self.panel_c.set_matrix(c)
        self.set_status("Готово: C = A + B")

    @safe_call
    def on_mul(self):
        with self.panel_a.get_matrix() as a, self.panel_b.get_matrix() as b:
            with a * b as c:
                self.panel_c.set_matrix(c)
        self.set_status("Готово: C = A * B")

    @safe_call
    def on_iadd(self):
        with self.panel_a.get_matrix() as a, self.panel_b.get_matrix() as b:
            a += b
            self.panel_a.set_matrix(a)
        self.set_status("Готово: A += B")

    @safe_call
    def on_a_to_c(self):
        with self.panel_a.get_matrix() as a:
            with a.copy() as c:
                self.panel_c.set_matrix(c)
        self.set_status("Готово: C = A")

    @safe_call
    def on_b_to_c(self):
        with self.panel_b.get_matrix() as b:
            with b.copy() as c:
                self.panel_c.set_matrix(c)
        self.set_status("Готово: C = B")

    @safe_call
    def on_swap(self):
        a_text = self.panel_a.get_text()
        b_text = self.panel_b.get_text()
        self.panel_a.set_text(b_text)
        self.panel_b.set_text(a_text)
        self.set_status("Готово: A <-> B")

    # ---------- файлы ----------

    @safe_call
    def on_open_a(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Открыть в A",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        with load_matrix_from_file(path) as m:
            self.panel_a.set_matrix(m)
        self.set_status(f"Загружено в A: {path}")

    @safe_call
    def on_open_b(self):
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Открыть в B",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        with load_matrix_from_file(path) as m:
            self.panel_b.set_matrix(m)
        self.set_status(f"Загружено в B: {path}")

    @safe_call
    def on_save_c(self):
        with self.panel_c.get_matrix() as c:
            path = filedialog.asksaveasfilename(
                parent=self.root,
                title="Сохранить C",
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt")],
            )
            if not path:
                return
            save_matrix_to_file(c, path)
        self.set_status(f"Сохранено: {path}")

    # ---------- тема и справка ----------

    def on_theme_change(self):
        self.current_theme = self.theme_var.get()
        apply_theme(self.root, self.current_theme)
        self.set_status(f"Тема: {self.current_theme}")

    def on_about(self):
        messagebox.showinfo(
            "О программе",
            "Матричный калькулятор\n"
            "Вычисления — C++ (MatrixLib.dll)\n"
            "Интерфейс — Python + Tkinter\n\n"
            "Операции: A+B, A*B, A+=B, A->C, B->C, A<->B",
        )

    # ---------- запуск ----------

    def run(self):
        self.root.mainloop()