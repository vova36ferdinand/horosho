"""The interactive RPC menu must use a separate server process."""

import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import pytest

import data_layer
import repl
from rpc_client import RPCClient


@pytest.fixture
def remote_server(tmp_path):
    """Start an isolated server with its own memory and request journal."""
    source = Path(__file__).resolve().parents[1] / "src"
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    code = ("import sys; sys.path.insert(0, sys.argv[1]); "
            "from rpc_server import run_server; "
            "run_server(port=int(sys.argv[2]))")
    process = subprocess.Popen(
        [sys.executable, "-u", "-c", code, str(source), str(port)],
        cwd=tmp_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"),
    )
    try:
        for attempt in range(60):
            if process.poll() is not None:
                raise RuntimeError(process.communicate()[0].decode("utf-8"))
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=.1):
                    break
            except OSError:
                time.sleep(.05)
        else:
            raise RuntimeError("Test server did not start")
        yield RPCClient(port=port), tmp_path / "journal.log"
    finally:
        process.terminate()
        process.communicate(timeout=3)


@pytest.mark.usefixtures("empty_data")
def test_all_menu_operations_use_remote_server(
    remote_server, monkeypatch, capsys
):
    """All thirteen commands use server memory and leave local data empty."""
    backend, journal = remote_server
    answers = iter([
        "1", "1", "4000", "192.0.2.1", "2", "3", "1",
        "4", "1", "4000", "192.0.2.9",
        "5", "2", "1000", "hello", "1", "0", "6", "7", "2",
        "8", "2", "2000", "changed", "1", "1",
        "9", "3", "3000", "ok", "sent", "", "2", "10", "11", "3",
        "12", "3", "3001", "updated", "done", "", "2", "13", "0",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    monkeypatch.setattr(repl.time, "time", lambda: 4000)
    repl.run_repl(backend)
    codes = [int(line.split(",")[0].split(":")[1])
             for line in journal.read_text(encoding="utf-8").splitlines()]
    assert codes == list(range(1, 14))
    assert "Результат: [['192.0.2.9', 'changed']]" in capsys.readouterr().out
    other_client = RPCClient(host=backend.host, port=backend.port)
    assert other_client.get_account_by_id(1) == [1, 4000, "192.0.2.9"]
    assert other_client.get_message_by_id(2) == [2, 2000, "changed", 1, 1]
    assert other_client.get_feedback_by_id(3) == [
        3, 3001, "updated", "done", "", 2
    ]
    assert [data_layer.ACCOUNTS, data_layer.MESSAGES,
            data_layer.FEEDBACKS] == [[], [], []]


def test_rpc_menu_command_line(remote_server):
    """The documented --rpc command connects to the selected server port."""
    backend, journal = remote_server
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "src/repl.py", "--rpc", "--host", backend.host,
         "--port", str(backend.port)], cwd=root, input="2\n0\n",
        capture_output=True, text=True, encoding="utf-8", timeout=5,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"),
    )
    assert result.returncode == 0, result.stderr
    assert f"Режим RPC: {backend.host}:{backend.port}" in result.stdout
    assert "Результат: []" in result.stdout
    assert "Код: 2" in journal.read_text(encoding="utf-8")


def test_connection_error_does_not_exit_menu(monkeypatch, capsys):
    """A failed network request still allows the next menu command."""
    def fail():
        raise ConnectionRefusedError("connection refused")

    backend = RPCClient()
    monkeypatch.setattr(backend, "get_all_accounts", fail)
    answers = iter(["2", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    repl.run_repl(backend)
    assert "Ошибка подключения к серверу:" in capsys.readouterr().out
