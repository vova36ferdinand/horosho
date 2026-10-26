"""Интерактивное меню для работы со слоем данных."""

import time
from data_layer import (
    create_account,
    create_log,
    create_message,
    get_account_by_id,
    get_all_accounts,
    get_all_logs,
    get_all_messages,
    get_log_by_id,
    get_message_by_id,
    select_recent_messages,
    update_account,
    update_log,
    update_message,
)

MENU_TEXT = (
    "\n=== МЕНЮ БАЗЫ ДАННЫХ ===\n"
    "1. Создать аккаунт       2. Все аккаунты        "
    "3. Аккаунт по ID       4. Изменить аккаунт\n"
    "5. Создать сообщение     6. Все сообщения      "
    "7. Сообщение по ID    8. Изменить сообщение\n"
    "9. Создать лог          10. Все логи          "
    "11. Лог по ID         12. Изменить лог\n"
    "13. Выборка за 8 минут  0. Выход\n"
    "Выберите команду: "
)


def run_repl() -> None:
    """Запускает интерактивный режим работы со слоем данных."""
    while True:
        choice = input(MENU_TEXT).strip()
        if choice == "0":
            break
        execute_command(choice)


def _command_create_account() -> None:
    """Создаёт аккаунт."""
    uid = int(input("Введите ID аккаунта: "))
    ip = input("Введите IP-адрес: ")
    res = create_account(uid, ip, time.time())
    print(f"Успешно создано: {res}")


def _command_list_accounts() -> None:
    """Выводит все аккаунты."""
    print(f"Все аккаунты: {get_all_accounts()}")


def _command_find_account() -> None:
    """Выводит аккаунт по ID."""
    uid = int(input("Введите ID аккаунта: "))
    print(f"Результат: {get_account_by_id(uid)}")


def _command_update_account() -> None:
    """Обновляет аккаунт."""
    uid = int(input("Введите ID аккаунта: "))
    ip = input("Введите новый IP: ")
    res = update_account(uid, ip, time.time())
    print(f"Результат обновления: {res}")


def _command_create_message() -> None:
    """Создаёт сообщение."""
    uid = int(input("Введите ID сообщения: "))
    arg = input("Введите текст: ")
    acc = int(input("Введите ID аккаунта: "))
    print(f"Создано: {create_message(uid, arg, acc)}")


def _command_list_messages() -> None:
    """Выводит все сообщения."""
    print(f"Все сообщения: {get_all_messages()}")


def _command_find_message() -> None:
    """Выводит сообщение по ID."""
    uid = int(input("Введите ID сообщения: "))
    print(f"Результат: {get_message_by_id(uid)}")


def _command_update_message() -> None:
    """Обновляет сообщение."""
    uid = int(input("Введите ID сообщения: "))
    arg = input("Введите новый текст: ")
    acc = int(input("Введите ID аккаунта: "))
    print(f"Результат: {update_message(uid, arg, acc)}")


def _command_create_log() -> None:
    """Создаёт лог."""
    uid = int(input("Введите ID лога: "))
    msg = int(input("Введите ID сообщения: "))
    st = input("Введите статус: ")
    print(f"Создано: {create_log(uid, msg, st)}")


def _command_list_logs() -> None:
    """Выводит все логи."""
    print(f"Все логи: {get_all_logs()}")


def _command_find_log() -> None:
    """Выводит лог по ID."""
    uid = int(input("Введите ID лога: "))
    print(f"Результат: {get_log_by_id(uid)}")


def _command_update_log() -> None:
    """Обновляет лог."""
    uid = int(input("Введите ID лога: "))
    msg = int(input("Введите ID сообщения: "))
    st = input("Введите новый статус: ")
    print(f"Результат: {update_log(uid, msg, st)}")


def _command_recent_messages() -> None:
    """Выводит выборку за последние восемь минут."""
    res = select_recent_messages(time.time())
    print(f"Результат выборки: {res}")


COMMAND_HANDLERS = {
    "1": _command_create_account,
    "2": _command_list_accounts,
    "3": _command_find_account,
    "4": _command_update_account,
    "5": _command_create_message,
    "6": _command_list_messages,
    "7": _command_find_message,
    "8": _command_update_message,
    "9": _command_create_log,
    "10": _command_list_logs,
    "11": _command_find_log,
    "12": _command_update_log,
    "13": _command_recent_messages,
}


def execute_command(choice: str) -> None:
    """Обрабатывает и выполняет выбранную команду меню."""
    handler = COMMAND_HANDLERS.get(choice)
    if handler is None:
        print("Неверный код команды!")
        return
    try:
        handler()
    except ValueError as err:
        print(f"Ошибка ввода данных: {err}")


if __name__ == "__main__":
    run_repl()
