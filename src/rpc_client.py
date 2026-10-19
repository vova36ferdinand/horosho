"""TCP client for the remote procedure call server."""

import json
import socket

HEADER_SIZE_BYTES = 3
OPCODE_SIZE_BYTES = 1
LITTLE_ENDIAN = "little"
REQUEST_TIMEOUT_SECONDS = 3


# Клиент для выполнения удалённых вызовов процедур по TCP
class RPCClient:
    """Client for calling database operations over TCP."""

    # Инициализирует адрес сервера
    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host = host
        self.port = port

    # Отправляет запрос серверу по бинарному протоколу
    def _send_request(self, opcode: int, payload: dict) -> dict:
        """Send a request and return the server's result."""
        body_bytes = json.dumps(payload).encode("utf-8")
        length_bytes = len(body_bytes).to_bytes(
            HEADER_SIZE_BYTES, byteorder=LITTLE_ENDIAN
        )
        code_byte = opcode.to_bytes(OPCODE_SIZE_BYTES, byteorder=LITTLE_ENDIAN)
        header_size = HEADER_SIZE_BYTES + OPCODE_SIZE_BYTES

        with socket.create_connection(
            (self.host, self.port), timeout=REQUEST_TIMEOUT_SECONDS
        ) as client:
            client.settimeout(REQUEST_TIMEOUT_SECONDS)
            client.sendall(length_bytes + code_byte + body_bytes)
            header = self._recv_exact(client, header_size)
            if len(header) != header_size:
                raise ConnectionError(
                    "Сервер вернул неполный заголовок ответа"
                )

            response_length = int.from_bytes(
                header[:HEADER_SIZE_BYTES], byteorder=LITTLE_ENDIAN
            )
            response_bytes = self._recv_exact(client, response_length)
            if len(response_bytes) != response_length:
                raise ConnectionError("Сервер вернул неполный ответ")

        response = json.loads(response_bytes.decode("utf-8"))
        return response.get("result")

    @staticmethod
    def _recv_exact(client: socket.socket, size: int) -> bytes:
        """Receive up to the requested number of bytes."""
        chunks = bytearray()
        while len(chunks) < size:
            part = client.recv(size - len(chunks))
            if not part:
                break
            chunks.extend(part)
        return bytes(chunks)

    # Это все функции из data_layer.py, которые мы вызываем
    def create_account(self, uid: int, ip: str, timestamp: float) -> tuple:
        return self._send_request(
            1, {"uid": uid, "ip": ip, "timestamp": timestamp}
        )

    def get_all_accounts(self) -> list:
        return self._send_request(2, {})

    def get_account_by_id(self, uid: int) -> tuple | None:
        return self._send_request(3, {"uid": uid})

    def update_account(
        self, uid: int, ip: str, timestamp: float
    ) -> tuple | None:
        return self._send_request(
            4, {"uid": uid, "ip": ip, "timestamp": timestamp}
        )

    def create_message(self, uid: int, argument: str, account: int) -> tuple:
        return self._send_request(
            5, {"uid": uid, "argument": argument, "account": account}
        )

    def get_all_messages(self) -> list:
        return self._send_request(6, {})

    def get_message_by_id(self, uid: int) -> tuple | None:
        return self._send_request(7, {"uid": uid})

    def update_message(
        self, uid: int, argument: str, account: int
    ) -> tuple | None:
        return self._send_request(
            8, {"uid": uid, "argument": argument, "account": account}
        )

    def create_log(self, uid: int, message: int, status: str) -> tuple:
        return self._send_request(
            9, {"uid": uid, "message": message, "status": status}
        )

    def get_all_logs(self) -> list:
        return self._send_request(10, {})

    def get_log_by_id(self, uid: int) -> tuple | None:
        return self._send_request(11, {"uid": uid})

    def update_log(self, uid: int, message: int, status: str) -> tuple | None:
        return self._send_request(
            12, {"uid": uid, "message": message, "status": status}
        )

    def select_recent_messages(self, now_timestamp: float) -> list:
        return self._send_request(13, {"now_timestamp": now_timestamp})
