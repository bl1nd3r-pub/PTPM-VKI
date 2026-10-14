from src.controller.controller import Controller
from src.database.triangle_database import TriangleDatabase
from src.external_dependency.external_service import MockExternalDependency
from src.logging_config import configure_logging
from src.user_interface.user_interface import ConsoleUserInput


def main() -> None:
    configure_logging()
    controller = Controller(
        database=TriangleDatabase(),
        user_interface=ConsoleUserInput(),
        external_dependency=MockExternalDependency(),
    )
    print(controller.run())


if __name__ == "__main__":
    main()
