import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if __package__ in {None, ""}:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import DatabaseRepository
from src.logger.config import configure_logging
from src.parser import ForumParser


DATABASE_PATH = PROJECT_ROOT / "data" / "comments.sqlite3"
logger = logging.getLogger(__name__)


def show_database(repository: DatabaseRepository) -> None:
    rows = repository.get_all()
    if not rows:
        print("В базе данных пока нет записей.")
        return

    print("\nСохраненные комментарии:")
    for comment in rows:
        print(
            f"\nID: {comment['parse_id']}-{comment['id']} | "
            f"Автор: {comment['name']}\n"
            f"{comment['message']}"
        )


def parse_urls(parser: ForumParser, repository: DatabaseRepository) -> None:
    while True:
        try:
            url = input(
                "Введите URL страницы (пустой ввод — назад в меню):\n"
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВозврат в меню.")
            logger.info("URL input interrupted; returning to menu")
            return

        if not url:
            return

        try:
            parsed_data = parser.parse_page(url)
            parse_id = repository.create_parse_operation(url)
            saved_count = parser.save_to_db(parsed_data, repository, parse_id)
            if saved_count:
                print(
                    f"Операция №{parse_id}: сохранено комментариев: {saved_count}"
                )
            else:
                print(
                    f"Операция №{parse_id}: подходящие комментарии на странице "
                    "не найдены."
                )
        except Exception as error:
            logger.error("Could not parse page %s: %s", url, error)
            print("Не удалось обработать страницу. Подробности записаны в журнал.")

# Воообщееее, у меня были мысли перенести весь консольный интерфейс в отдельный класс в отдельном файле
# Ну типо использовать паттерн Service-Provider, в роде того
# Но потом подумал, что так париться - немножко лишнее в рамках этой небольшой лабы,
#   где можно в этом плане чуть-чуть да поговнокодить)))

def run_menu() -> None:
    configure_logging()
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    parser = ForumParser()

    with DatabaseRepository(DATABASE_PATH) as repository:
        while True:
            print(
                "\n*PARSER OVER9000*\n"
                "1) Провести парсинг\n"
                "2) Просмотреть SQLite БД (только чтение)\n"
                "3) Выйти"
            )
            try:
                choice = input("Выберите пункт меню:\n").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nЗавершение работы.")
                logger.info("Application stopped by input interruption")
                return

            if choice == "1":
                parse_urls(parser, repository)
            elif choice == "2":
                try:
                    show_database(repository)
                except Exception as error:
                    logger.error("Could not read the database: %s", error)
                    print("Не удалось прочитать базу данных. Подробности записаны в журнал.")
            elif choice == "3":
                logger.info("Application stopped by user")
                print("До свидания!")
                return
            else:
                print("Выберите пункт 1, 2 или 3.")


def main() -> None:
    try:
        run_menu()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nРабота приложения прервана.")
    except Exception as error:
        logger.error("Application failed to start or continue: %s", error)
        print("Не удалось запустить приложение. Подробности записаны в журнале.")


if __name__ == "__main__":
    main()
