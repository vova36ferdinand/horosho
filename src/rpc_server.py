"""TCP RPC server exposing the data-layer operations."""

import json
import socket

import data_layer


HOST = "127.0.0.1"
PORT = 8080
HEADER_SIZE_BYTES = 3
OPCODE_SIZE_BYTES = 1

LITTLE_ENDIAN = "little"

LOG_FILE = "journal.log"


def log_request(opcode: int, payload: dict) -> None:
    """Append a request to the server journal."""
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"Код: {opcode}, Данные: {payload}\n")


OPERATIONS = {
    1: (data_layer.create_account, ("uid", "timestamp", "ip")),
    2: (data_layer.get_all_accounts, ()),
    3: (data_layer.get_account_by_id, ("uid",)),
    4: (data_layer.update_account, ("uid", "timestamp", "ip")),
    5: (
        data_layer.create_message,
        ("uid", "timestamp", "argument", "account", "completed"),
    ),
    6: (data_layer.get_all_messages, ()),
    7: (data_layer.get_message_by_id, ("uid",)),
    8: (
        data_layer.update_message,
        ("uid", "timestamp", "argument", "account", "completed"),
    ),
    9: (
        data_layer.create_feedback,
        ("uid", "timestamp", "result", "status", "failure", "message"),
    ),
    10: (data_layer.get_all_feedbacks, ()),
    11: (data_layer.get_feedback_by_id, ("uid",)),
    12: (
        data_layer.update_feedback,
        ("uid", "timestamp", "result", "status", "failure", "message"),
    ),
    13: (data_layer.select_recent_messages, ("now_timestamp",)),
}


def process_request(opcode: int, data: dict) -> tuple[int, dict]:
    """Dispatch one of the thirteen variant 15 operations."""
    entry = OPERATIONS.get(opcode)
    if entry is None:
        return opcode, {"error": "Неизвестный код операции"}
    operation, fields = entry
    try:
        return opcode, {"result": operation(*(data[key] for key in fields))}
    except (KeyError, TypeError, ValueError) as error:
        return opcode, {"error": str(error)}


def run_server(host: str = HOST, port: int = PORT, ready_event=None) -> None:
    """Start the TCP server and process incoming connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        print(f"Сервер запущен на {host}:{port}")
        if ready_event is not None:
            ready_event.set()

        while True:
            connection, _ = server.accept()
            handle_connection(connection)


def _recv_exact(connection: socket.socket, size: int) -> bytes:
    """Receive up to the requested number of bytes."""
    chunks = bytearray()
    while len(chunks) < size:
        part = connection.recv(size - len(chunks))
        if not part:
            break
        chunks.extend(part)
    return bytes(chunks)


def handle_connection(connection: socket.socket) -> None:
    """Read one request, dispatch it, and send one response."""
    try:
        header_size = HEADER_SIZE_BYTES + OPCODE_SIZE_BYTES
        header = _recv_exact(connection, header_size)
        if len(header) != header_size:
            return

        body_length = int.from_bytes(
            header[:HEADER_SIZE_BYTES], byteorder=LITTLE_ENDIAN
        )
        opcode = int.from_bytes(
            header[HEADER_SIZE_BYTES:], byteorder=LITTLE_ENDIAN
        )
        body_bytes = _recv_exact(connection, body_length)
        if len(body_bytes) != body_length:
            return

        payload = json.loads(body_bytes.decode("utf-8"))
        log_request(opcode, payload)
        response_opcode, response_data = process_request(opcode, payload)

        response_bytes = json.dumps(response_data).encode("utf-8")
        response_length = len(response_bytes).to_bytes(
            HEADER_SIZE_BYTES, byteorder=LITTLE_ENDIAN
        )
        response_code = response_opcode.to_bytes(
            OPCODE_SIZE_BYTES, byteorder=LITTLE_ENDIAN
        )
        connection.sendall(response_length + response_code + response_bytes)
    finally:
        connection.close()


if __name__ == "__main__":
    run_server()
