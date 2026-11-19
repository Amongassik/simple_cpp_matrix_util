"""
parsing.py — преобразование между текстом, файлами и объектами Matrix.
"""

from matrix_lib import Matrix


# ──────────────────────────────────────────────────────────────
# 1. Парсинг текста из поля ввода
# ──────────────────────────────────────────────────────────────

def parse_matrix_text(text: str):
    tokens = text.replace(",", " ").split()

    if len(tokens) < 2:
        raise ValueError(
            "Ожидается строка 'строки столбцы' в начале.\n"
            f"Получено токенов: {len(tokens)}"
        )

    try:
        rows = int(tokens[0])
        cols = int(tokens[1])
    except ValueError:
        raise ValueError(
            f"Размеры должны быть целыми числами, получено: "
            f"'{tokens[0]}' и '{tokens[1]}'"
        )

    if rows <= 0 or cols <= 0:
        raise ValueError(
            f"Размеры должны быть положительными, получено: {rows}×{cols}"
        )

    values = []
    for idx, token in enumerate(tokens[2:], start=1):
        try:
            values.append(float(token))
        except ValueError:
            raise ValueError(
                f"Элемент #{idx} не является числом: '{token}'"
            )

    expected = rows * cols
    if len(values) != expected:
        raise ValueError(
            f"Для матрицы {rows}×{cols} нужно {expected} чисел, "
            f"введено {len(values)}"
        )

    return rows, cols, values


def create_matrix_from_text(text: str) -> Matrix:
    rows, cols, values = parse_matrix_text(text)
    m = Matrix(rows, cols)
    m.from_list(values)
    return m


def matrix_to_text(matrix: Matrix) -> str:
    rows = matrix.rows
    cols = matrix.cols
    lines = [f"{rows} {cols}"]
    flat = matrix.to_list()
    for i in range(rows):
        row_values = flat[i * cols:(i + 1) * cols]
        line = " ".join(_format_number(v) for v in row_values)
        lines.append(line)
    return "\n".join(lines)


def _format_number(value: float) -> str:
    """
    Красиво форматирует число: 3.0 -> "3.0", 1.5 -> "1.5".
    Без лишних нулей после запятой.
    """
    if value == int(value):
        return f"{int(value)}.0"
    return repr(value)


# ──────────────────────────────────────────────────────────────
# 3. Загрузка и сохранение файлов
# ──────────────────────────────────────────────────────────────

def load_matrix_from_file(path: str) -> Matrix:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return create_matrix_from_text(text)


def save_matrix_to_file(matrix: Matrix, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(matrix_to_text(matrix))
        f.write("\n")
