import os
import sys
import ctypes

# ──────────────────────────────────────────────────────────────
# 1. Загрузка библиотеки
# ──────────────────────────────────────────────────────────────

# sys.platform — строка вида "win32", "linux", "darwin".
# startswith("win") — True на Windows. Имя файла выбираем по ОС.

from ctypes import c_void_p, c_int, c_double, c_char_p, POINTER

if sys.platform.startswith("win"):
    _LIB_NAME = "MatrixLib.dll"
else:
    _LIB_NAME = "libMatrixLib.so"

# os.path.dirname(os.path.abspath(__file__)) — папка, где лежит ЭТОТ .py.
# os.path.join(...) — склеивает путь с именем файла кроссплатформенно.
# Абсолютный путь

_LIB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), _LIB_NAME)

# ctypes.CDLL — загружает DLL в процесс. Если файла нет или не хватает
# зависимостей — бросит OSError, и программа не стартует. Это нормально:
# без DLL делать нечего.

_lib = ctypes.CDLL(_LIB_PATH)


# ──────────────────────────────────────────────────────────────
# 2. Описание сигнатур всех функций
# ──────────────────────────────────────────────────────────────
#
# КАЖДАЯ функция должна быть описана: argtypes (типы аргументов) и
# restype (тип возврата). Без этого ctypes будет:
#   - передавать int как 32-битный, ломая double* на 64-битной системе;
#   - читать char* как int (вернёт число вместо байтов);
#   - «обрезать» void* до 32 бит → указатель в никуда → segfault.
#
# Типы:
#   c_void_p  — указатель (в Python это int или None)
#   c_int     — 32-битный знаковый int
#   c_double  — double (64-битный float)
#   c_char_p  — char* (при чтении вернёт bytes)
#   POINTER(X)— X* — типизированный указатель

_lib.matrix_last_error.argtypes = []
_lib.matrix_last_error.restype  = c_char_p

_lib.matrix_create.argtypes = [c_int, c_int]
_lib.matrix_create.restype  = c_void_p

_lib.matrix_create_filled.argtypes = [c_int, c_int, c_double]
_lib.matrix_create_filled.restype  = c_void_p

_lib.matrix_destroy.argtypes = [c_void_p]
_lib.matrix_destroy.restype  = None

_lib.matrix_clone.argtypes = [c_void_p]
_lib.matrix_clone.restype  = c_void_p

_lib.matrix_rows.argtypes = [c_void_p]
_lib.matrix_rows.restype  = c_int

_lib.matrix_cols.argtypes = [c_void_p]
_lib.matrix_cols.restype  = c_int

_lib.matrix_get_element.argtypes = [c_void_p, c_int, c_int, POINTER(c_double)]
_lib.matrix_get_element.restype  = c_int

_lib.matrix_set_element.argtypes = [c_void_p, c_int, c_int, c_double]
_lib.matrix_set_element.restype  = c_int

_lib.matrix_copy_from.argtypes = [c_void_p, POINTER(c_double), c_int]
_lib.matrix_copy_from.restype  = c_int

_lib.matrix_copy_to.argtypes = [c_void_p, POINTER(c_double), c_int]
_lib.matrix_copy_to.restype  = c_int

_lib.matrix_add.argtypes = [c_void_p, c_void_p]
_lib.matrix_add.restype  = c_void_p

_lib.matrix_multiply.argtypes = [c_void_p, c_void_p]
_lib.matrix_multiply.restype  = c_void_p

_lib.matrix_add_assign.argtypes = [c_void_p, c_void_p]
_lib.matrix_add_assign.restype  = c_int

_lib.matrix_to_string.argtypes = [c_void_p, c_char_p, c_int]
_lib.matrix_to_string.restype  = c_int

# ──────────────────────────────────────────────────────────────
# 3. Вспомогательные функции
# ──────────────────────────────────────────────────────────────

def _last_error() -> str:
    """Читает g_last_error из C++ и декодирует bytes → str."""
    raw = _lib.matrix_last_error()
    return raw.decode("utf-8") if raw else ""

def _check(ok: bool) -> None:
    """Если C++ вернул признак ошибки — бросаем Python-исключение."""
    if not ok:
        raise RuntimeError("MatrixLib: " + (_last_error() or "unknown error"))

class Matrix:
    """
    ладеет C++-объектом Matrix через непрозрачный указатель _ptr.
    """

    # запрет на добавление произвольных атрибутов.
    __slots__ = ("_ptr",)

    def __init__(self, rows, cols, fill=None):
        """
        Matrix(3, 3) → нулевая матрица 3×3
        Matrix(3, 3, 1.5) → заполненная 1.5
        """
        if fill is None:
            ptr = _lib.matrix_create(rows, cols)
        else:
            ptr = _lib.matrix_create_filled(rows, cols, float(fill))
        _check(bool(ptr))
        self._ptr = ptr

    def close(self):
        """Освободить объект немедленно"""
        if self._ptr:
            _lib.matrix_destroy(self._ptr)
            self._ptr = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def rows(self) -> int:
        return _lib.matrix_rows(self._ptr)

    @property
    def cols(self) -> int:
        return _lib.matrix_cols(self._ptr)

    @property
    def shape(self):
        return (self.rows, self.cols)

    def __getitem__(self, ij):
        i,j = ij
        out = c_double();
        _check(_lib.matrix_get_element(self._ptr, i, j, ctypes.byref(out)) == 0)
        return out.value

    def __setitem__(self, ij, value):
        i, j = ij
        _check(_lib.matrix_set_element(self._ptr, i, j, float(value)) == 0)


    def from_list(self, values):
        n = self.rows * self.cols
        if len(values) != n:
            raise ValueError(f"expected {n} values, got {len(values)}")
        buf = (c_double * n)(*values)
        _check(_lib.matrix_copy_from(self._ptr, buf, n) == 0)
        return self

    def to_list(self):
        n = self.rows * self.cols
        buf = (c_double * n)()
        _check(_lib.matrix_copy_to(self._ptr, buf, n) == 0)
        return list(buf)

    def to_2d_list(self):
        """Прочитать как список списков (по строкам)."""
        flat = self.to_list()
        r, c = self.rows, self.cols
        return [flat[i * c:(i + 1) * c] for i in range(r)]

    # ---------- операторы ----------

    def __add__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        ptr = _lib.matrix_add(self._ptr, other._ptr)
        _check(bool(ptr))
        return Matrix._wrap(ptr)

    def __iadd__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        _check(_lib.matrix_add_assign(self._ptr, other._ptr) == 0)
        return self

    def __mul__(self, other):
        if not isinstance(other, Matrix):
            return NotImplemented
        ptr = _lib.matrix_multiply(self._ptr, other._ptr)
        _check(bool(ptr))
        return Matrix._wrap(ptr)

    def copy(self):
        ptr = _lib.matrix_clone(self._ptr)
        _check(bool(ptr))
        return Matrix._wrap(ptr)

    def __repr__(self):
        needed = _lib.matrix_to_string(self._ptr, None, 0)
        if needed <= 0:
            return "<Matrix (error)>"
        buf = ctypes.create_string_buffer(needed)
        _lib.matrix_to_string(self._ptr, buf, needed)
        return f"Matrix{self.shape}:\n{buf.value.decode('utf-8')}"

    @classmethod
    def _wrap(cls, ptr):
        obj = cls.__new__(cls)
        obj._ptr = ptr
        return obj
