"""Framing, complete reads and error responses for the TCP protocol."""

import json
import socket
import threading

import pytest

import rpc_client
import rpc_server


def test_tcp_full_outer_join_and_request_journal(
    tmp_path, monkeypatch, empty_data
):
    """A real RPC response preserves NULL and logs its 3+1 byte request."""
    import data_layer

    data_layer.create_account(1, 3520, "192.0.2.1")
    journal = tmp_path / "journal.log"
    monkeypatch.setattr(rpc_server, "LOG_FILE", journal)
    client, server = socket.socketpair()
    with client:
        thread = threading.Thread(target=rpc_server.handle_connection,
                                  args=(server,))
        thread.start()
        body = json.dumps({"now_timestamp": 4000}).encode("utf-8")
        client.sendall(len(body).to_bytes(3, "little") + b"\x0d" + body)
        header = rpc_server._recv_exact(client, 4)
        assert header[3] == 13
        response = rpc_server._recv_exact(
            client, int.from_bytes(header[:3], "little")
        )
        assert json.loads(response) == {"result": [["192.0.2.1", None]]}
        thread.join(timeout=3)
    assert "Код: 13" in journal.read_text(encoding="utf-8")


def test_unknown_opcode():
    """An unknown operation yields an error response without dispatching."""
    assert "error" in rpc_server.process_request(255, {})[1]


def test_missing_required_field():
    """A missing payload field yields an error response."""
    assert "error" in rpc_server.process_request(1, {})[1]


def test_rpc_client_raises_remote_errors(monkeypatch):
    """The client exposes server errors instead of returning silent None."""
    class FakeConnection:
        def __init__(self):
            self.body = json.dumps({"error": "missing uid"}).encode()
            self.parts = iter([len(self.body).to_bytes(3, "little") + b"\x01",
                               self.body])

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def settimeout(self, timeout):
            return None

        def sendall(self, data):
            return None

        def recv(self, size):
            return next(self.parts)

    monkeypatch.setattr(rpc_client.socket, "create_connection",
                        lambda *args, **kwargs: FakeConnection())
    with pytest.raises(ValueError, match="missing uid"):
        rpc_client.RPCClient()._send_request(1, {})
