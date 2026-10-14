import logging
from abc import ABC, abstractmethod
from typing import List


class UserInputInterface(ABC):
    @abstractmethod
    def get_triangle_data(self) -> List[str]:
        raise NotImplementedError


class ConsoleUserInput(UserInputInterface):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def get_triangle_data(self) -> List[str]:
        values: List[str] = []
        for index in range(3):
            raw_value = input(f"Введите сторону {index + 1}: ").strip()
            self.logger.info("Получена сторона %d: %s", index + 1, raw_value)
            values.append(raw_value)
        return values
