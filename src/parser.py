import logging
import re
from typing import List, Optional, TypedDict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup, Tag

from src.database import DatabaseRepository


logger = logging.getLogger(__name__)


class ParsedComment(TypedDict):
    id: int
    name: str
    message: str


class ForumParser:
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }
    TIMEOUT_SECONDS = 15
    POST_SELECTORS = (
        "article",
        ".post",
        ".comment",
        ".topic-body",
        ".comtr",
        "[data-post-id]",
        "[data-comment-id]",
        '[id^="post"]',
        '[id^="comment"]',
        '[id^="message"]',
    )
    AUTHOR_SELECTORS = (
        ".creator [itemprop='name']",
        "[itemprop='author']",
        ".comhead a[href^='user?id=']",
        ".username",
        ".user-name",
        ".post-author",
        ".comment-author",
        ".author",
        ".user",
    )
    MESSAGE_SELECTORS = (
        "[itemprop='text']",
        ".post-content",
        ".comment-content",
        ".post-message",
        ".comment-body",
        ".postbody",
        ".entry-content",
        ".post",
        ".commtext",
        ".message",
        ".content",
    )
    ID_PATTERN = re.compile(r"(?:post|comment|message)[_-]?(\d+)", re.IGNORECASE)

    def parse_page(self, url: str) -> List[ParsedComment]:
        if not isinstance(url, str):
            raise TypeError("url must be a string")
        parsed_url = urlparse(url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("url must be an absolute HTTP or HTTPS address")

        logger.info("Downloading forum page: %s", url)
        response = requests.get(
            url,
            headers=self.HEADERS,
            timeout=self.TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        parsed_data = self._extract_comments(soup)
        logger.info("Extracted %d comments from %s", len(parsed_data), url)
        return parsed_data

    def _extract_comments(self, soup: BeautifulSoup) -> List[ParsedComment]:
        candidates: List[Tag] = []
        seen_candidates = set()
        for selector in self.POST_SELECTORS:
            for candidate in soup.select(selector):
                identity = id(candidate)
                if identity not in seen_candidates:
                    candidates.append(candidate)
                    seen_candidates.add(identity)
        document_order = {
            id(element): index for index, element in enumerate(soup.find_all(True))
        }
        candidates.sort(key=lambda item: document_order[id(item)])

        comments: List[ParsedComment] = []
        seen_ids = set()
        for candidate in candidates:
            comment_id = self._extract_id(candidate)
            author = self._find_element(candidate, self.AUTHOR_SELECTORS)
            message = self._find_element(candidate, self.MESSAGE_SELECTORS)
            if comment_id is None or author is None or message is None:
                continue

            username = author.get_text(" ", strip=True)
            message_html = message.decode_contents().strip()
            if not username or comment_id in seen_ids:
                continue

            comments.append(
                {
                    "id": comment_id,
                    "name": username,
                    "message": message_html,
                }
            )
            seen_ids.add(comment_id)

        return comments

    @classmethod
    def _extract_id(cls, candidate: Tag) -> Optional[int]:
        for attribute in ("data-post-id", "data-comment-id", "data-id"):
            value = candidate.get(attribute)
            if isinstance(value, str) and value.isdigit():
                return int(value)

        element_id = candidate.get("id")
        if isinstance(element_id, str):
            if element_id.isdigit():
                return int(element_id)
            match = cls.ID_PATTERN.search(element_id)
            if match:
                return int(match.group(1))

        for link in candidate.select("a[href]"):
            href = link.get("href")
            if isinstance(href, str):
                match = cls.ID_PATTERN.search(href)
                if match:
                    return int(match.group(1))
        return None

    @staticmethod
    def _find_element(candidate: Tag, selectors: tuple) -> Optional[Tag]:
        for selector in selectors:
            element = candidate.select_one(selector)
            if element is not None:
                return element
        return None

    @staticmethod
    def save_to_db(
        parsed_data: List[ParsedComment],
        repository: DatabaseRepository,
        parse_id: int,
    ) -> int:
        saved_count = 0
        for comment in parsed_data:
            repository.add(
                parse_id=parse_id,
                comment_id=comment["id"],
                username=comment["name"],
                message=comment["message"],
            )
            saved_count += 1
        logger.info("Saved %d comments for parsing operation id=%s", saved_count, parse_id)
        return saved_count
