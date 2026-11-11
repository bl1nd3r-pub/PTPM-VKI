import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, TypedDict, Union


logger = logging.getLogger(__name__)


class Comment(TypedDict):
    parse_id: int
    id: int
    name: str
    message: str


class DatabaseRepository:
    MAX_NAME_LENGTH = 256
    MAX_MESSAGE_LENGTH = 8096

    def __init__(self, database_path: Union[str, Path]) -> None:
        self.database_path = str(database_path)
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(self.database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._create_table()
        logger.info("Database repository initialized")

    def _create_table(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS parsing_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            table_exists = self._connection.execute(
                """
                SELECT 1 FROM sqlite_master
                WHERE type = 'table' AND name = 'comments'
                """
            ).fetchone()
            if table_exists:
                columns = {
                    row["name"]
                    for row in self._connection.execute(
                        "PRAGMA table_info(comments)"
                    ).fetchall()
                }
                if "parse_id" not in columns:
                    self._migrate_legacy_comments()
                    return

            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS comments (
                    parse_id INTEGER NOT NULL,
                    id INTEGER NOT NULL,
                    name TEXT NOT NULL CHECK(length(name) <= 256),
                    message TEXT NOT NULL CHECK(length(message) <= 8096),
                    PRIMARY KEY (parse_id, id),
                    FOREIGN KEY (parse_id) REFERENCES parsing_operations(id)
                )
                """
            )
            self._connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_comments_name ON comments(name)"
            )

    def _migrate_legacy_comments(self) -> None:
        self._connection.execute(
            "INSERT OR IGNORE INTO parsing_operations (id, source_url) VALUES (0, ?)",
            ("legacy-import",),
        )
        self._connection.execute("ALTER TABLE comments RENAME TO comments_legacy")
        self._connection.execute(
            """
            CREATE TABLE comments (
                parse_id INTEGER NOT NULL,
                id INTEGER NOT NULL,
                name TEXT NOT NULL CHECK(length(name) <= 256),
                message TEXT NOT NULL CHECK(length(message) <= 8096),
                PRIMARY KEY (parse_id, id),
                FOREIGN KEY (parse_id) REFERENCES parsing_operations(id)
            )
            """
        )
        self._connection.execute(
            """
            INSERT INTO comments (parse_id, id, name, message)
            SELECT 0, id, name, message FROM comments_legacy
            """
        )
        self._connection.execute("DROP TABLE comments_legacy")
        self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_comments_name ON comments(name)"
        )
        logger.info("Migrated legacy comments into composite-key schema")

    @classmethod
    def _validate_id(cls, value: int, field_name: str) -> None:
        if type(value) is not int:
            raise TypeError(f"{field_name} must be an integer")

    @classmethod
    def _validate_name(cls, username: str) -> None:
        if not isinstance(username, str):
            raise TypeError("username must be a string")
        if len(username) > cls.MAX_NAME_LENGTH:
            raise ValueError(
                f"username cannot be longer than {cls.MAX_NAME_LENGTH} characters"
            )

    @classmethod
    def _validate_message(cls, message: str) -> None:
        if not isinstance(message, str):
            raise TypeError("message must be a string")
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"message cannot be longer than {cls.MAX_MESSAGE_LENGTH} characters"
            )

    @staticmethod
    def _as_comment(row: sqlite3.Row) -> Comment:
        return {
            "parse_id": row["parse_id"],
            "id": row["id"],
            "name": row["name"],
            "message": row["message"],
        }

    def create_parse_operation(self, source_url: str) -> int:
        if not isinstance(source_url, str):
            raise TypeError("source_url must be a string")
        with self._connection:
            cursor = self._connection.execute(
                "INSERT INTO parsing_operations (source_url) VALUES (?)",
                (source_url,),
            )
            operation_id = cursor.lastrowid
            if operation_id is None:
                raise sqlite3.DatabaseError("SQLite did not return an operation ID")
        logger.info("Created parsing operation id=%s", operation_id)
        return operation_id

    def get_by_id(self, parse_id: int, comment_id: int) -> Optional[Comment]:
        self._validate_id(parse_id, "parse_id")
        self._validate_id(comment_id, "comment_id")
        row = self._connection.execute(
            """
            SELECT parse_id, id, name, message
            FROM comments WHERE parse_id = ? AND id = ?
            """,
            (parse_id, comment_id),
        ).fetchone()
        return self._as_comment(row) if row is not None else None

    def get_by_name(self, username: str) -> List[Comment]:
        self._validate_name(username)
        rows = self._connection.execute(
            """
            SELECT parse_id, id, name, message FROM comments
            WHERE name = ? ORDER BY parse_id, id
            """,
            (username,),
        ).fetchall()
        return [self._as_comment(row) for row in rows]

    def get_all(self) -> List[Comment]:
        rows = self._connection.execute(
            "SELECT parse_id, id, name, message FROM comments ORDER BY parse_id, id"
        ).fetchall()
        return [self._as_comment(row) for row in rows]

    def add(
        self,
        parse_id: int,
        comment_id: int,
        username: str,
        message: str,
    ) -> bool:
        self._validate_id(parse_id, "parse_id")
        self._validate_id(comment_id, "comment_id")
        self._validate_name(username)
        self._validate_message(message)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO comments (parse_id, id, name, message)
                VALUES (?, ?, ?, ?)
                """,
                (parse_id, comment_id, username, message),
            )
        logger.info("Stored comment key=%s-%s", parse_id, comment_id)
        return True

    def update(self, parse_id: int, comment_id: int, new_message: str) -> bool:
        self._validate_id(parse_id, "parse_id")
        self._validate_id(comment_id, "comment_id")
        self._validate_message(new_message)
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE comments SET message = ?
                WHERE parse_id = ? AND id = ?
                """,
                (new_message, parse_id, comment_id),
            )
        updated = cursor.rowcount > 0
        if updated:
            logger.info("Updated comment key=%s-%s", parse_id, comment_id)
        else:
            logger.info("No comment found to update key=%s-%s", parse_id, comment_id)
        return updated

    def delete(self, parse_id: int, comment_id: int) -> bool:
        self._validate_id(parse_id, "parse_id")
        self._validate_id(comment_id, "comment_id")
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM comments WHERE parse_id = ? AND id = ?",
                (parse_id, comment_id),
            )
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("Deleted comment key=%s-%s", parse_id, comment_id)
        else:
            logger.info("No comment found to delete key=%s-%s", parse_id, comment_id)
        return deleted

    def close(self) -> None:
        self._connection.close()
        logger.info("Database repository closed")

    def __enter__(self) -> "DatabaseRepository":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
