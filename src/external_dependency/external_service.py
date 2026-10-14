import logging
from abc import ABC, abstractmethod
from typing import List


class ExternalDependency(ABC):
    @abstractmethod
    def send_result(self, message: str) -> bool:
        raise NotImplementedError


class MockExternalDependency(ExternalDependency):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.sent_messages: List[str] = []

    def send_result(self, message: str) -> bool:
        self.logger.info("Отправка результата во внешнюю зависимость: %s", message)
        self.sent_messages.append(message)
        return True
