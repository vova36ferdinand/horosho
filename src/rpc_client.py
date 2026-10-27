"""TCP client for the remote procedure call server."""

import json
import socket

HEADER_SIZE_BYTES = 3
OPCODE_SIZE_BYTES = 1
LITTLE_ENDIAN = "little"
REQUEST_TIMEOUT_SECONDS = 3


class RPCClient:
    """Client for calling database operations over TCP."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.host = host
        self.port = port

    def _send_request(self, opcode: int, payload: dict):
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
        if "error" in response:
            raise ValueError(response["error"])
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

    def create_account(self, uid: int, timestamp: int, ip: str) -> list:
        """Call create_account on the RPC server."""
        return self._send_request(
            1, {
                "uid": uid,
                "timestamp": timestamp,
                "ip": ip,
            }
        )

    def get_all_accounts(self) -> list:
        """Call get_all_accounts on the RPC server."""
        return self._send_request(2, {})

    def get_account_by_id(self, uid: int) -> list | None:
        """Call get_account_by_id on the RPC server."""
        return self._send_request(3, {"uid": uid})

    def update_account(self, uid: int, timestamp: int, ip: str) -> list | None:
        """Call update_account on the RPC server."""
        return self._send_request(
            4, {
                "uid": uid,
                "timestamp": timestamp,
                "ip": ip,
            }
        )

    def create_message(
        self, uid: int, timestamp: int, argument: str, account: int,
        completed: int
    ) -> list:
        """Call create_message on the RPC server."""
        return self._send_request(
            5, {
                "uid": uid,
                "timestamp": timestamp,
                "argument": argument,
                "account": account,
                "completed": completed,
            }
        )

    def get_all_messages(self) -> list:
        """Call get_all_messages on the RPC server."""
        return self._send_request(6, {})

    def get_message_by_id(self, uid: int) -> list | None:
        """Call get_message_by_id on the RPC server."""
        return self._send_request(7, {"uid": uid})

    def update_message(
        self, uid: int, timestamp: int, argument: str, account: int,
        completed: int
    ) -> list | None:
        """Call update_message on the RPC server."""
        return self._send_request(
            8, {
                "uid": uid,
                "timestamp": timestamp,
                "argument": argument,
                "account": account,
                "completed": completed,
            }
        )

    def create_feedback(
        self, uid: int, timestamp: int, result: str, status: str,
        failure: str, message: int
    ) -> list:
        """Call create_feedback on the RPC server."""
        return self._send_request(
            9, {
                "uid": uid,
                "timestamp": timestamp,
                "result": result,
                "status": status,
                "failure": failure,
                "message": message,
            }
        )

    def get_all_feedbacks(self) -> list:
        """Call get_all_feedbacks on the RPC server."""
        return self._send_request(10, {})

    def get_feedback_by_id(self, uid: int) -> list | None:
        """Call get_feedback_by_id on the RPC server."""
        return self._send_request(11, {"uid": uid})

    def update_feedback(
        self, uid: int, timestamp: int, result: str, status: str,
        failure: str, message: int
    ) -> list | None:
        """Call update_feedback on the RPC server."""
        return self._send_request(
            12, {
                "uid": uid,
                "timestamp": timestamp,
                "result": result,
                "status": status,
                "failure": failure,
                "message": message,
            }
        )

    def select_recent_messages(self, now_timestamp: float) -> list:
        """Call select_recent_messages on the RPC server."""
        return self._send_request(13, {"now_timestamp": now_timestamp})
