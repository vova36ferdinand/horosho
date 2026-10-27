"""Python client demonstrating all thirteen operations on the RPC server."""

import argparse
import time

from src.rpc_client import RPCClient


def demonstrate(client: RPCClient, timestamp: int) -> None:
    """Run the assignment's data operations through the TCP RPC client."""
    print("1. Создать Account:",
          client.create_account(1, timestamp, "127.0.0.1"))
    print("2. Все Account:", client.get_all_accounts())
    print("3. Account по ID:", client.get_account_by_id(1))
    print("4. Изменить Account:",
          client.update_account(1, timestamp, "127.0.0.1"))
    print("5. Создать Message:",
          client.create_message(1, timestamp, "Привет!", 1, 0))
    print("6. Все Message:", client.get_all_messages())
    print("7. Message по ID:", client.get_message_by_id(1))
    print("8. Изменить Message:",
          client.update_message(1, timestamp, "Сообщение обновлено", 1, 1))
    print("9. Создать Feedback:",
          client.create_feedback(1, timestamp, "ok", "sent", "", 1))
    print("10. Все Feedback:", client.get_all_feedbacks())
    print("11. Feedback по ID:", client.get_feedback_by_id(1))
    print("12. Изменить Feedback:",
          client.update_feedback(1, timestamp, "ok", "done", "", 1))
    print("13. Выборка по формуле:",
          client.select_recent_messages(timestamp))


def main() -> int:
    """Connect the Python script to the selected RPC server."""
    parser = argparse.ArgumentParser(description="Python-клиент RPC")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Порт должен быть от 1 до 65535")
    print(f"Выполнение операций на сервере {args.host}:{args.port}")
    try:
        demonstrate(RPCClient(args.host, args.port), int(time.time()))
    except (OSError, ValueError) as error:
        print(f"Ошибка RPC: {error}")
        print("Запустите сервер командой: py src/rpc_server.py")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
