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


def process_request(opcode: int, data: dict) -> tuple[int, dict]:
    """Dispatch a request to the corresponding data-layer function."""
    operations = {
        1: lambda: data_layer.create_account(
            data["uid"], data["ip"], data["timestamp"]
        ),
        2: data_layer.get_all_accounts,
        3: lambda: data_layer.get_account_by_id(data["uid"]),
        4: lambda: data_layer.update_account(
            data["uid"], data["ip"], data["timestamp"]
        ),
        5: lambda: data_layer.create_message(
            data["uid"], data["argument"], data["account"]
        ),
        6: data_layer.get_all_messages,
        7: lambda: data_layer.get_message_by_id(data["uid"]),
        8: lambda: data_layer.update_message(
            data["uid"], data["argument"], data["account"]
        ),
        9: lambda: data_layer.create_log(
            data["uid"], data["message"], data["status"]
        ),
        10: data_layer.get_all_logs,
        11: lambda: data_layer.get_log_by_id(data["uid"]),
        12: lambda: data_layer.update_log(
            data["uid"], data["message"], data["status"]
        ),
        13: lambda: data_layer.select_recent_messages(
            data["now_timestamp"]
        ),
    }

    operation = operations.get(opcode)
    if operation is None:
        return opcode, {"error": "Неизвестный код операции"}

    return opcode, {"result": operation()}


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
