import logging
import math
from pathlib import Path
import sys
from typing import Iterable, List, Sequence, Tuple


Coord = Tuple[int, int]


def setup_logging() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    log_dir = Path(__file__).resolve().parent / "Logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | [%(levelname)-7s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "triangle_lab.log", encoding="utf-8"),
        ],
        force=True,
    )


def parse_float_value(raw_value: str) -> float:
    cleaned = raw_value.strip()
    value = float(cleaned)
    if not math.isfinite(value):
        raise ValueError("Число не является конечным.")
    return value


def classify_triangle(a: float, b: float, c: float) -> str:
    if a <= 0 or b <= 0 or c <= 0:
        return "не треугольник"

    if a + b <= c or a + c <= b or b + c <= a:
        return "не треугольник"

    tolerance = 1e-9
    if math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance) and math.isclose(b, c, rel_tol=tolerance, abs_tol=tolerance):
        return "равносторонний"
    if (
        math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)
        or math.isclose(a, c, rel_tol=tolerance, abs_tol=tolerance)
        or math.isclose(b, c, rel_tol=tolerance, abs_tol=tolerance)
    ):
        return "равнобедренный"
    return "разносторонний"


def calculate_triangle_vertices(a: float, b: float, c: float) -> List[Coord]:
    side_a, side_b, side_c = sorted((a, b, c))

    base_length = side_c
    if math.isclose(base_length, 0.0, abs_tol=1e-12):
        return [(-1, -1), (-1, -1), (-1, -1)]

    x3 = (side_a * side_a + base_length * base_length - side_b * side_b) / (2.0 * base_length)
    y3 = math.sqrt(max(0.0, side_a * side_a - x3 * x3))

    points = [(0.0, 0.0), (base_length, 0.0), (x3, y3)]
    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)

    width = max_x - min_x
    height = max_y - min_y
    scale = 1.0
    if width > 0 and height > 0:
        scale = min(70.0 / width, 70.0 / height)

    centroid_x = sum(point[0] for point in points) / len(points)
    centroid_y = sum(point[1] for point in points) / len(points)

    transformed: List[Coord] = []
    for px, py in points:
        x = (px - centroid_x) * scale + 50.0
        y = (py - centroid_y) * scale + 50.0
        transformed.append((int(round(x)), int(round(y))))

    for index, (x, y) in enumerate(transformed):
        transformed[index] = (max(0, min(99, x)), max(0, min(99, y)))

    return transformed


def process_triangle_input(raw_values: Sequence[str]) -> Tuple[str, List[Coord]]:
    if len(raw_values) != 3:
        logging.error("Ожидалось ровно 3 входа, получено %d.", len(raw_values))
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    parsed_values: List[float] = []
    parse_error = False
    numeric_error = False

    for raw in raw_values:
        try:
            value = parse_float_value(raw)
        except ValueError:
            parse_error = True
            break

        if not math.isfinite(value) or value <= 0:
            numeric_error = True
            continue

        parsed_values.append(value)

    if parse_error:
        logging.error("Получены нечисловые данные: %s", list(raw_values))
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    if len(parsed_values) != 3 or numeric_error:
        logging.warning("Неверный ввод числовых данных: %s", list(raw_values))
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    a, b, c = parsed_values
    triangle_type = classify_triangle(a, b, c)

    if triangle_type == "не треугольник":
        logging.warning("Треугольник не может быть сформирован сторонами %.2f, %.2f, %.2f.", a, b, c)
        return triangle_type, [(-1, -1), (-1, -1), (-1, -1)]

    vertices = calculate_triangle_vertices(a, b, c)
    logging.info("Вычислен тип треугольника '%s' для сторон %.2f, %.2f, %.2f: Вершины=%s.", triangle_type, a, b, c, vertices)
    return triangle_type, vertices


def read_triangle_input() -> List[str]:
    values: List[str] = []
    for index in range(3):
        raw = input().strip()
        values.append(raw)
    return values


def main() -> None:
    setup_logging()
    logging.info("Запущено приложение для анализа треугольников")

    try:
        raw_values = read_triangle_input()
        triangle_type, vertices = process_triangle_input(raw_values)
        print(triangle_type)
        print(vertices)

        if triangle_type:
            logging.info("Успешный запрос %s -> %s | %s", raw_values, triangle_type, vertices)
        else:
            logging.warning("Неуспешный запрос: %s -> Неверный нечисловой ввод.", raw_values)
    except EOFError:
        logging.exception("Программа не получила все 3 строки входных данных.")
        print("")
        print([(-2, -2), (-2, -2), (-2, -2)])
    except Exception:
        logging.exception("Произошла непредвиденная ошибка при обработке входных данных")
        print("")
        print([(-2, -2), (-2, -2), (-2, -2)])


if __name__ == "__main__":
    main()