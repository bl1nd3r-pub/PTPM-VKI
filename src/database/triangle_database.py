import logging
import sqlite3
from typing import Optional, Dict, Any


class TriangleDatabase:
    def __init__(self, db_path: str = ":memory:") -> None:
        self.logger = logging.getLogger(__name__)
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.logger.info("Подключение к БД: %s", db_path)
        self._create_table()

    def _create_table(self) -> None:
        self.logger.info("Создание таблицы triangle_results, если её нет")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS triangle_results (
                length1 REAL NOT NULL,
                length2 REAL NOT NULL,
                length3 REAL NOT NULL,
                triangle_type TEXT NOT NULL,
                error_message TEXT,
                PRIMARY KEY (length1, length2, length3)
            )
            """
        )
        self.connection.commit()

    def add_record(self, length1: float, length2: float, length3: float, triangle_type: str, error_message: str = "") -> None:
        self.logger.info(
            "Сохранение результата в БД для сторон (%.2f, %.2f, %.2f): type=%s, error=%s",
            length1,
            length2,
            length3,
            triangle_type,
            error_message,
        )
        self.connection.execute(
            """
            INSERT OR REPLACE INTO triangle_results (length1, length2, length3, triangle_type, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (float(length1), float(length2), float(length3), triangle_type, error_message),
        )
        self.connection.commit()

    def get_record(self, length1: float, length2: float, length3: float) -> Optional[Dict[str, Any]]:
        self.logger.info("Поиск записи в БД для сторон (%.2f, %.2f, %.2f)", length1, length2, length3)
        row = self.connection.execute(
            """
            SELECT length1, length2, length3, triangle_type, error_message
            FROM triangle_results
            WHERE length1 = ? AND length2 = ? AND length3 = ?
            """,
            (float(length1), float(length2), float(length3)),
        ).fetchone()

        if row is None:
            self.logger.info("Запись в БД не найдена")
            return None

        result = {
            "length1": row["length1"],
            "length2": row["length2"],
            "length3": row["length3"],
            "triangle_type": row["triangle_type"],
            "error_message": row["error_message"],
        }
        self.logger.info("Запись в БД найдена: %s", result)
        return result

    def delete_record(self, length1: float, length2: float, length3: float) -> None:
        self.logger.warning("Удаление записи из БД для сторон (%.2f, %.2f, %.2f)", length1, length2, length3)
        self.connection.execute(
            "DELETE FROM triangle_results WHERE length1 = ? AND length2 = ? AND length3 = ?",
            (float(length1), float(length2), float(length3)),
        )
        self.connection.commit()

    def close(self) -> None:
        self.logger.info("Закрытие соединения с БД")
        self.connection.close()

    def __del__(self) -> None:
        try:
            self.connection.close()
        except Exception:
            pass
