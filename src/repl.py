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


def execute_command(choice: str) -> None:
    """Обрабатывает и выполняет выбранную команду меню."""
    try:
        if choice == "1":
            uid = int(input("Введите ID аккаунта: "))
            ip = input("Введите IP-адрес: ")
            res = create_account(uid, ip, time.time())
            print(f"Успешно создано: {res}")
        elif choice == "2":
            print(f"Все аккаунты: {get_all_accounts()}")
        elif choice == "3":
            uid = int(input("Введите ID аккаунта: "))
            print(f"Результат: {get_account_by_id(uid)}")
        elif choice == "4":
            uid = int(input("Введите ID аккаунта: "))
            ip = input("Введите новый IP: ")
            res = update_account(uid, ip, time.time())
            print(f"Результат обновления: {res}")
        elif choice == "5":
            uid = int(input("Введите ID сообщения: "))
            arg = input("Введите текст: ")
            acc = int(input("Введите ID аккаунта: "))
            print(f"Создано: {create_message(uid, arg, acc)}")
        elif choice == "6":
            print(f"Все сообщения: {get_all_messages()}")
        elif choice == "7":
            uid = int(input("Введите ID сообщения: "))
            print(f"Результат: {get_message_by_id(uid)}")
        elif choice == "8":
            uid = int(input("Введите ID сообщения: "))
            arg = input("Введите новый текст: ")
            acc = int(input("Введите ID аккаунта: "))
            print(f"Результат: {update_message(uid, arg, acc)}")
        elif choice == "9":
            uid = int(input("Введите ID лога: "))
            msg = int(input("Введите ID сообщения: "))
            st = input("Введите статус: ")
            print(f"Создано: {create_log(uid, msg, st)}")
        elif choice == "10":
            print(f"Все логи: {get_all_logs()}")
        elif choice == "11":
            uid = int(input("Введите ID лога: "))
            print(f"Результат: {get_log_by_id(uid)}")
        elif choice == "12":
            uid = int(input("Введите ID лога: "))
            msg = int(input("Введите ID сообщения: "))
            st = input("Введите новый статус: ")
            print(f"Результат: {update_log(uid, msg, st)}")
        elif choice == "13":
            res = select_recent_messages(time.time())
            print(f"Результат выборки: {res}")
        else:
            print("Неверный код команды!")
    except ValueError as err:
        print(f"Ошибка ввода данных: {err}")


if __name__ == "__main__":
    run_repl()
