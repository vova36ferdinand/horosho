import socket
import threading

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

import data_layer
from rpc_client import RPCClient
from rpc_server import run_server


TEST_HOST = "127.0.0.1"
TEST_PORT = None


def setup_module() -> None:
    """Запускает сервер на свободном порту и ждёт его готовности."""
    global TEST_PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((TEST_HOST, 0))
        TEST_PORT = probe.getsockname()[1]
    ready = threading.Event()
    thread = threading.Thread(
        target=run_server,
        kwargs={"host": TEST_HOST, "port": TEST_PORT, "ready_event": ready},
        daemon=True,
    )
    thread.start()
    if not ready.wait(timeout=3):
        raise RuntimeError("RPC-сервер не запустился за 3 секунды")


class DatabaseStateMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        """Инициализирует клиент, очищает БД сервера и эталонное состояние."""
        super().__init__()

        # Очищаем все возможные списки/словари БД в data_layer
        collections = [
            "ACCOUNTS",
            "accounts",
            "MESSAGES",
            "messages",
            "LOGS",
            "logs",
        ]
        for collection in collections:
            if hasattr(data_layer, collection):
                getattr(data_layer, collection).clear()

        self.client = RPCClient(host=TEST_HOST, port=TEST_PORT)

        # Локальные эталонные модели
        self.model_accounts = {}
        self.model_messages = {}
        self.model_logs = {}

    # ==========================================
    # 1. АККАУНТЫ (Accounts)
    # ==========================================
    @rule(
        uid=st.integers(min_value=1, max_value=100),
        ip=st.just("127.0.0.1"),
        ts=st.floats(min_value=1000.0, max_value=2000.0),
    )
    def create_account(self, uid: int, ip: str, ts: float) -> None:
        res = self.client.create_account(uid, ip, ts)
        self.model_accounts[uid] = [uid, ip, ts]
        assert res == [uid, ip, ts]

    @rule(uid=st.integers(min_value=1, max_value=100))
    def get_account_by_id(self, uid: int) -> None:
        res = self.client.get_account_by_id(uid)
        expected = self.model_accounts.get(uid)
        assert res == expected

    @rule()
    def get_all_accounts(self) -> None:
        res = self.client.get_all_accounts()
        assert len(res) == len(self.model_accounts)

    @rule(
        uid=st.integers(min_value=1, max_value=100),
        ip=st.just("192.168.1.1"),
        ts=st.floats(3000.0, 4000.0),
    )
    def update_account(self, uid: int, ip: str, ts: float) -> None:
        res = self.client.update_account(uid, ip, ts)
        # Если аккаунт есть в модели, он должен обновиться
        if uid in self.model_accounts:
            self.model_accounts[uid] = [uid, ip, ts]
            assert res == [uid, ip, ts]

    # ==========================================
    # 2. СООБЩЕНИЯ (Messages)
    # ==========================================
    @rule(
        msg_id=st.integers(1, 100),
        text=st.text(min_size=1, max_size=20),
        account=st.integers(1, 10),
    )
    def create_message(self, msg_id: int, text: str, account: int) -> None:
        res = self.client.create_message(msg_id, text, account)
        self.model_messages[msg_id] = [msg_id, text, account]
        assert res is not None

    @rule(msg_id=st.integers(1, 100))
    def get_message_by_id(self, msg_id: int) -> None:
        res = self.client.get_message_by_id(msg_id)
        assert res == self.model_messages.get(msg_id)

    @rule()
    def get_all_messages(self) -> None:
        res = self.client.get_all_messages()
        assert len(res) == len(self.model_messages)

    @rule(
        msg_id=st.integers(1, 100),
        text=st.text(min_size=1, max_size=20),
        account=st.integers(1, 10),
    )
    def update_message(self, msg_id: int, text: str, account: int) -> None:
        res = self.client.update_message(msg_id, text, account)
        if msg_id in self.model_messages:
            self.model_messages[msg_id] = [msg_id, text, account]
            assert res is not None

    # ==========================================
    # 3. ЛОГИ (Logs)
    # ==========================================
    @rule(
        log_id=st.integers(1, 100),
        info=st.text(min_size=1, max_size=20),
        status=st.integers(0, 1),
    )
    def create_log(self, log_id: int, info: str, status: int) -> None:
        res = self.client.create_log(log_id, info, status)
        self.model_logs[log_id] = [log_id, info, status]
        assert res is not None

    @rule(log_id=st.integers(1, 100))
    def get_log_by_id(self, log_id: int) -> None:
        res = self.client.get_log_by_id(log_id)
        assert res == self.model_logs.get(log_id)

    @rule()
    def get_all_logs(self) -> None:
        res = self.client.get_all_logs()
        assert len(res) == len(self.model_logs)

    @rule(
        log_id=st.integers(1, 100),
        info=st.text(min_size=1, max_size=20),
        status=st.integers(0, 1),
    )
    def update_log(self, log_id: int, info: str, status: int) -> None:
        res = self.client.update_log(log_id, info, status)
        if log_id in self.model_logs:
            self.model_logs[log_id] = [log_id, info, status]
            assert res is not None

    # ==========================================
    # 4. ВЫБОРКА ЗА 8 МИНУТ (Пункт 13)
    # ==========================================
    @rule()
    def get_data_last_8_minutes(self) -> None:
        """Проверяет метод выборки за последние 8 минут."""
        # Вызываем метод напрямую по его стандартному имени в RPCClient
        if hasattr(self.client, "get_last_8_minutes"):
            res = self.client.get_last_8_minutes()
            assert isinstance(res, list)
        elif hasattr(self.client, "get_eight_minutes"):
            res = self.client.get_eight_minutes()
            assert isinstance(res, list)


TestDatabaseRPC = DatabaseStateMachine.TestCase
TestDatabaseRPC.settings = settings(
    max_examples=10, stateful_step_count=20, deadline=None
)
