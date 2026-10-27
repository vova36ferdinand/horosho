"""Интерактивное меню для схемы данных варианта 15."""

import argparse
import time

import data_layer
from rpc_client import RPCClient

MENU_TEXT = (
    "\n=== МЕНЮ БАЗЫ ДАННЫХ ===\n"
    "1. Создать аккаунт       2. Все аккаунты        "
    "3. Аккаунт по ID       4. Изменить аккаунт\n"
    "5. Создать сообщение     6. Все сообщения      "
    "7. Сообщение по ID    8. Изменить сообщение\n"
    "9. Создать обратную связь  10. Вся обратная связь\n"
    "11. Обратная связь по ID   12. Изменить обратную связь\n"
    "13. Выборка за 8 минут  0. Выход\n"
    "Выберите команду: "
)


ACCOUNT_FIELDS = (
    ("ID аккаунта", int),
    ("Временная метка аккаунта", int),
    ("IP-адрес", str),
)

MESSAGE_FIELDS = (
    ("ID сообщения", int),
    ("Временная метка сообщения", int),
    ("Текст сообщения", str),
    ("ID аккаунта", int),
    ("Признак завершения", int),
)

FEEDBACK_FIELDS = (
    ("ID обратной связи", int),
    ("Временная метка обратной связи", int),
    ("Результат", str),
    ("Статус", str),
    ("Ошибка", str),
    ("ID сообщения", int),
)


def _read_fields(fields: tuple) -> list:
    """Считывает поля записи с преобразованием числовых значений."""
    return [convert(input(f"{title}: ")) for title, convert in fields]


COMMANDS = {
    "1": ("create_account", ACCOUNT_FIELDS),
    "2": ("get_all_accounts", ()),
    "3": ("get_account_by_id", ACCOUNT_FIELDS[:1]),
    "4": ("update_account", ACCOUNT_FIELDS),
    "5": ("create_message", MESSAGE_FIELDS),
    "6": ("get_all_messages", ()),
    "7": ("get_message_by_id", MESSAGE_FIELDS[:1]),
    "8": ("update_message", MESSAGE_FIELDS),
    "9": ("create_feedback", FEEDBACK_FIELDS),
    "10": ("get_all_feedbacks", ()),
    "11": ("get_feedback_by_id", FEEDBACK_FIELDS[:1]),
    "12": ("update_feedback", FEEDBACK_FIELDS),
}


def execute_command(choice: str, backend=data_layer) -> None:
    """Выполняет команду, сообщая об ошибках пользовательского ввода."""
    try:
        if choice == "13":
            result = backend.select_recent_messages(time.time())
        else:
            entry = COMMANDS.get(choice)
            if entry is None:
                print("Неверный код команды!")
                return
            name, fields = entry
            result = getattr(backend, name)(*_read_fields(fields))
        print(f"Результат: {result}")
    except ValueError as error:
        print(f"Ошибка ввода данных: {error}")
    except OSError as error:
        print(f"Ошибка подключения к серверу: {error}")
        print("Проверьте, что RPC-сервер запущен по указанному адресу.")


def run_repl(backend=data_layer) -> None:
    """Выполняет команды до ввода нуля."""
    while True:
        choice = input(MENU_TEXT).strip()
        if choice == "0":
            return
        execute_command(choice, backend)


def main() -> None:
    """Запускает локальное меню или подключает его к TCP RPC-серверу."""
    parser = argparse.ArgumentParser(description="Меню базы данных")
    parser.add_argument("--rpc", action="store_true",
                        help="Выполнять команды через RPC-сервер")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Адрес RPC-сервера")
    parser.add_argument("--port", type=int, default=8080,
                        help="Порт RPC-сервера")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Порт должен быть от 1 до 65535")
    backend = RPCClient(args.host, args.port) if args.rpc else data_layer
    if args.rpc:
        print(f"Режим RPC: {args.host}:{args.port}")
    run_repl(backend)


if __name__ == "__main__":
    main()
