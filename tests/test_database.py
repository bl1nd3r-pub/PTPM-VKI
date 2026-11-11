import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Optional

from src.database import Comment, DatabaseRepository


class DatabaseRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = DatabaseRepository(":memory:")
        self.parse_id = self.repository.create_parse_operation("https://example.test/1")

    def tearDown(self) -> None:
        self.repository.close()

    def add_comment(
        self,
        comment_id: int,
        username: str = "alice",
        message: str = "hello",
        parse_id: Optional[int] = None,
    ) -> bool:
        return self.repository.add(
            self.parse_id if parse_id is None else parse_id,
            comment_id,
            username,
            message,
        )

    def require_comment(self, parse_id: int, comment_id: int) -> Comment:
        comment = self.repository.get_by_id(parse_id, comment_id)
        if comment is None:
            self.fail(f"Expected comment {parse_id}-{comment_id} to exist")
        return comment

    def test_add_stores_record_and_returns_true(self) -> None:
        self.assertTrue(self.add_comment(1))
        self.assertEqual(
            self.repository.get_by_id(self.parse_id, 1),
            {
                "parse_id": self.parse_id,
                "id": 1,
                "name": "alice",
                "message": "hello",
            },
        )

    def test_add_duplicate_composite_key_raises_integrity_error(self) -> None:
        self.add_comment(1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.add_comment(1, username="bob", message="duplicate")

    def test_same_comment_id_can_be_saved_in_different_operations(self) -> None:
        self.add_comment(1, message="first parse")
        second_parse_id = self.repository.create_parse_operation(
            "https://example.test/2"
        )
        self.repository.add(second_parse_id, 1, "alice", "second parse")

        self.assertEqual(
            self.require_comment(self.parse_id, 1)["message"],
            "first parse",
        )
        self.assertEqual(
            self.require_comment(second_parse_id, 1)["message"],
            "second parse",
        )

    def test_add_rejects_invalid_lengths_and_types(self) -> None:
        with self.assertRaises(ValueError):
            self.repository.add(self.parse_id, 1, "a" * 257, "message")
        with self.assertRaises(ValueError):
            self.repository.add(self.parse_id, 1, "alice", "m" * 8097)
        with self.assertRaises(TypeError):
            self.repository.add(self.parse_id, True, "alice", "message")

    def test_get_by_id_returns_record_when_present(self) -> None:
        self.add_comment(3)
        self.assertEqual(
            self.require_comment(self.parse_id, 3)["name"],
            "alice",
        )

    def test_get_by_id_returns_none_when_missing(self) -> None:
        self.assertIsNone(self.repository.get_by_id(self.parse_id, 99))

    def test_get_by_name_returns_all_matching_records_in_key_order(self) -> None:
        self.add_comment(3, message="third")
        self.add_comment(1, message="first")
        self.add_comment(2, username="bob", message="other")
        self.assertEqual(
            [
                comment["id"]
                for comment in self.repository.get_by_name("alice")
            ],
            [1, 3],
        )

    def test_get_by_name_returns_empty_list_when_missing(self) -> None:
        self.assertEqual(self.repository.get_by_name("nobody"), [])

    def test_get_all_returns_records_in_composite_key_order(self) -> None:
        self.add_comment(3, username="carol", message="third")
        self.add_comment(1, message="first")
        self.add_comment(2, username="bob", message="second")

        self.assertEqual(
            self.repository.get_all(),
            [
                {
                    "parse_id": self.parse_id,
                    "id": 1,
                    "name": "alice",
                    "message": "first",
                },
                {
                    "parse_id": self.parse_id,
                    "id": 2,
                    "name": "bob",
                    "message": "second",
                },
                {
                    "parse_id": self.parse_id,
                    "id": 3,
                    "name": "carol",
                    "message": "third",
                },
            ],
        )

    def test_get_all_returns_empty_list_for_empty_database(self) -> None:
        self.assertEqual(self.repository.get_all(), [])

    def test_update_changes_record_with_matching_composite_key(self) -> None:
        self.add_comment(1, message="old")
        self.assertTrue(self.repository.update(self.parse_id, 1, "new"))
        self.assertEqual(
            self.require_comment(self.parse_id, 1)["message"],
            "new",
        )

    def test_update_returns_false_for_missing_composite_key(self) -> None:
        self.assertFalse(self.repository.update(self.parse_id, 99, "new"))

    def test_update_rejects_overlong_message(self) -> None:
        with self.assertRaises(ValueError):
            self.repository.update(self.parse_id, 1, "m" * 8097)

    def test_delete_removes_existing_composite_key_and_returns_true(self) -> None:
        self.add_comment(1)
        self.assertTrue(self.repository.delete(self.parse_id, 1))
        self.assertIsNone(self.repository.get_by_id(self.parse_id, 1))

    def test_delete_returns_false_for_missing_composite_key(self) -> None:
        self.assertFalse(self.repository.delete(self.parse_id, 99))

    def test_legacy_database_migrates_existing_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "legacy.sqlite3"
            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE comments (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        message TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    "INSERT INTO comments (id, name, message) VALUES (7, 'old', 'saved')"
                )
                connection.commit()
            finally:
                connection.close()

            with DatabaseRepository(database_path) as migrated_repository:
                self.assertEqual(
                    migrated_repository.get_all(),
                    [
                        {
                            "parse_id": 0,
                            "id": 7,
                            "name": "old",
                            "message": "saved",
                        }
                    ],
                )
                new_parse_id = migrated_repository.create_parse_operation(
                    "https://example.test/new"
                )
                self.assertEqual(new_parse_id, 1)
                self.assertTrue(
                    migrated_repository.add(new_parse_id, 7, "new", "new record")
                )


if __name__ == "__main__":
    unittest.main()
