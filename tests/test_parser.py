import unittest
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

from src.database import DatabaseRepository
from src.parser import ForumParser, ParsedComment


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "forum_page.html"


class ForumParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = ForumParser()
        self.html = FIXTURE_PATH.read_text(encoding="utf-8")

    @patch("src.parser.requests.get")
    def test_parse_page_extracts_posts_and_preserves_inner_html(
        self,
        mock_get: Mock,
    ) -> None:
        response = Mock()
        response.text = self.html
        mock_get.return_value = response

        parsed = self.parser.parse_page("https://example.test/topic")

        self.assertEqual(
            parsed,
            [
                {
                    "id": 101,
                    "name": "alice",
                    "message": "Hello <strong>forum</strong>!",
                },
                {"id": 202, "name": "bob", "message": "<p>Second comment</p>"},
                {"id": 303, "name": "carol", "message": "<p>Discourse reply</p>"},
                {"id": 404, "name": "dave", "message": "Hacker News reply"},
            ],
        )
        mock_get.assert_called_once()
        self.assertIn("User-Agent", mock_get.call_args.kwargs["headers"])

    @patch("src.parser.requests.get")
    def test_parse_page_rejects_invalid_url_without_network_request(
        self,
        mock_get: Mock,
    ) -> None:
        with self.assertRaises(ValueError):
            self.parser.parse_page("not-a-url")
        mock_get.assert_not_called()

    def test_save_to_db_stores_comments_under_parse_operation(self) -> None:
        parsed_comments: List[ParsedComment] = [
            {"id": 101, "name": "alice", "message": "first"},
            {"id": 101, "name": "alice", "message": "second"},
        ]
        repository = Mock(spec=DatabaseRepository)

        saved_count = self.parser.save_to_db(parsed_comments, repository, 8)

        self.assertEqual(saved_count, 2)
        self.assertEqual(repository.add.call_count, 2)
        repository.add.assert_any_call(
            parse_id=8,
            comment_id=101,
            username="alice",
            message="first",
        )
        repository.add.assert_any_call(
            parse_id=8,
            comment_id=101,
            username="alice",
            message="second",
        )


if __name__ == "__main__":
    unittest.main()
