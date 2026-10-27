"""Интерактивное меню для схемы данных варианта 15."""

import time

import data_layer

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
    "1": (data_layer.create_account, ACCOUNT_FIELDS),
    "2": (data_layer.get_all_accounts, ()),
    "3": (data_layer.get_account_by_id, ACCOUNT_FIELDS[:1]),
    "4": (data_layer.update_account, ACCOUNT_FIELDS),
    "5": (data_layer.create_message, MESSAGE_FIELDS),
    "6": (data_layer.get_all_messages, ()),
    "7": (data_layer.get_message_by_id, MESSAGE_FIELDS[:1]),
    "8": (data_layer.update_message, MESSAGE_FIELDS),
    "9": (data_layer.create_feedback, FEEDBACK_FIELDS),
    "10": (data_layer.get_all_feedbacks, ()),
    "11": (data_layer.get_feedback_by_id, FEEDBACK_FIELDS[:1]),
    "12": (data_layer.update_feedback, FEEDBACK_FIELDS),
}


def execute_command(choice: str) -> None:
    """Выполняет команду, сообщая об ошибках пользовательского ввода."""
    if choice == "13":
        print(f"Результат: {data_layer.select_recent_messages(time.time())}")
        return
    entry = COMMANDS.get(choice)
    if entry is None:
        print("Неверный код команды!")
        return
    operation, fields = entry
    try:
        print(f"Результат: {operation(*_read_fields(fields))}")
    except ValueError as error:
        print(f"Ошибка ввода данных: {error}")


def run_repl() -> None:
    """Выполняет команды до ввода нуля."""
    while True:
        choice = input(MENU_TEXT).strip()
        if choice == "0":
            return
        execute_command(choice)


if __name__ == "__main__":
    run_repl()
