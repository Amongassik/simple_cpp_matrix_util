"""
widgets.py — визуальные компоненты:
- MatrixPanel — панель одной матрицы
- OperationPanel — сетка кнопок операций
"""

import random
import tkinter as tk
from tkinter import ttk, simpledialog, filedialog

from matrix_lib import Matrix
from .parsing import (
    create_matrix_from_text,
    matrix_to_text,
    load_matrix_from_file,
)
from .safety import safe_call


class MatrixPanel(ttk.LabelFrame):
    """
    Панель матрицы: заголовок + поле ввода + 4 кнопки.
    Наружу торчат:
      - get_text() / set_text(s)
      - get_matrix() → Matrix (парсит текст заново)
      - set_matrix(m) → заполняет поле и обновляет заголовок
    """

    def __init__(self, master, title, on_status):
        super().__init__(master, text=title)
        self._title = title
        self._on_status = on_status  

        self.text = tk.Text(
            self,
            width=30,
            height=12,
            font=("Consolas", 11),
            undo=True,             
            wrap="none",           
        )
        self.text.grid(row=0, column=0, columnspan=4, padx=6, pady=(6, 3), sticky="nsew")

        self.btn_create = ttk.Button(self, text="Создать",    command=self._on_create)
        self.btn_load   = ttk.Button(self, text="Загрузить",  command=self._on_load)
        self.btn_random = ttk.Button(self, text="Случайная",  command=self._on_random)
        self.btn_clear  = ttk.Button(self, text="Очистить",   command=self._on_clear)

        self.btn_create.grid(row=1, column=0, padx=3, pady=(0, 6), sticky="ew")
        self.btn_load.grid  (row=1, column=1, padx=3, pady=(0, 6), sticky="ew")
        self.btn_random.grid(row=1, column=2, padx=3, pady=(0, 6), sticky="ew")
        self.btn_clear.grid (row=1, column=3, padx=3, pady=(0, 6), sticky="ew")

        for col in range(4):
            self.grid_columnconfigure(col, weight=1)
        self.grid_rowconfigure(0, weight=1)

    

    def get_text(self):
        return self.text.get("1.0", tk.END)

    def set_text(self, s):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", s)

    def get_matrix(self):
        """Парсит текущий текст и возвращает Matrix. Бросает ValueError."""
        return create_matrix_from_text(self.get_text())

    def set_matrix(self, m):
        """Показывает m в поле и меняет заголовок на 'Матрица A (3x3)'."""
        self.set_text(matrix_to_text(m))
        self._set_title(m.rows, m.cols)

    

    def _set_title(self, rows, cols):
        self.configure(text=f"{self._title} ({rows}x{cols})")

    @safe_call
    def _on_create(self):
        rows = simpledialog.askinteger(
            "Создать матрицу", "Строк:",
            parent=self, minvalue=1, maxvalue=50,
        )
        if rows is None:
            return
        cols = simpledialog.askinteger(
            "Создать матрицу", "Столбцов:",
            parent=self, minvalue=1, maxvalue=50,
        )
        if cols is None:
            return

        with Matrix(rows, cols) as m:
            self.set_matrix(m)
        self._on_status(f"Создана матрица {rows}x{cols} в {self._title}")

    @safe_call
    def _on_load(self):
        path = filedialog.askopenfilename(
            parent=self,
            title=f"Загрузить {self._title}",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        )
        if not path:
            return
        with load_matrix_from_file(path) as m:
            self.set_matrix(m)
        self._on_status(f"Загружено: {path}")

    @safe_call
    def _on_random(self):
        rows = simpledialog.askinteger(
            "Случайная матрица", "Строк:",
            parent=self, minvalue=1, maxvalue=50,
        )
        if rows is None:
            return
        cols = simpledialog.askinteger(
            "Случайная матрица", "Столбцов:",
            parent=self, minvalue=1, maxvalue=50,
        )
        if cols is None:
            return
        values = [random.uniform(0.0, 10.0) for _ in range(rows * cols)]
        with Matrix(rows, cols) as m:
            m.from_list(values)
            self.set_matrix(m)
        self._on_status(f"Случайная матрица {rows}x{cols} в {self._title}")

    @safe_call
    def _on_clear(self):
        self.set_text("")
        self.configure(text=self._title)  
        self._on_status(f"{self._title} очищена")


class OperationPanel(ttk.LabelFrame):
    def __init__(self, master, callbacks):
        super().__init__(master, text="Операции")
        buttons = [
            ("A + B",   callbacks["add"]),
            ("A * B",   callbacks["mul"]),
            ("A += B",  callbacks["iadd"]),
            ("A -> C",  callbacks["a_to_c"]),
            ("B -> C",  callbacks["b_to_c"]),
            ("A <-> B", callbacks["swap"]),
        ]

        for idx, (label, cmd) in enumerate(buttons):
            ttk.Button(self, text=label, command=cmd).grid(
                row=idx // 3, column=idx % 3,
                padx=6, pady=6, sticky="ew",
            )

        for col in range(3):
            self.grid_columnconfigure(col, weight=1)