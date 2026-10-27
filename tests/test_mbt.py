"""Model-based tests of all thirteen variant 15 operations over real TCP."""

import socket
import threading

from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, rule

import data_layer
from rpc_client import RPCClient
from rpc_server import run_server
from tests.model_oracle import selection_oracle

TEST_HOST = "127.0.0.1"
UIDS = st.integers(1, 8)
TIMESTAMPS = st.sampled_from([0, 3519, 3520, 3999, 4000, 4001])
IPS = st.sampled_from(["192.0.2.1", "192.0.2.2"])
TEXTS = st.text(max_size=12)
test_port = None


def setup_module() -> None:
    """Start the RPC server on a free local port."""
    global test_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((TEST_HOST, 0))
        test_port = probe.getsockname()[1]
    ready = threading.Event()
    thread = threading.Thread(
        target=run_server,
        kwargs={"host": TEST_HOST, "port": test_port, "ready_event": ready},
        daemon=True,
    )
    thread.start()
    if not ready.wait(timeout=3):
        raise RuntimeError("RPC-сервер не запустился за 3 секунды")


class DatabaseStateMachine(RuleBasedStateMachine):
    """Compare RPC results with tuple models and an independent SQL oracle."""

    def __init__(self) -> None:
        super().__init__()
        for table in (data_layer.ACCOUNTS, data_layer.MESSAGES,
                      data_layer.FEEDBACKS):
            table.clear()
        self.client = RPCClient(host=TEST_HOST, port=test_port)
        self.models = {"account": {}, "message": {}, "feedback": {}}

    def _check_entity(self, entity, initial, updated):
        """Exercise empty, create, read, update and recreate paths over TCP."""
        create = getattr(self.client, f"create_{entity}")
        update = getattr(self.client, f"update_{entity}")
        get_by_id = getattr(self.client, f"get_{entity}_by_id")
        get_all = getattr(self.client, f"get_all_{entity}s")
        assert get_by_id(initial[0]) is None
        assert get_all() == []
        assert update(*updated) is None
        assert create(*initial) == list(initial)
        self._assert_entity_state(entity, initial)
        assert update(*updated) == list(updated)
        self._assert_entity_state(entity, updated)
        assert create(*initial) == list(initial)
        self.models[entity][initial[0]] = initial

    def _assert_entity_state(self, entity, row):
        """Check full records returned by both read operations."""
        assert getattr(self.client, f"get_{entity}_by_id")(row[0]) == list(row)
        assert getattr(self.client, f"get_all_{entity}s")() == [list(row)]

    def _assert_selection(self, now_timestamp):
        """Compare the RPC projection with independent SQL, including NULLs."""
        expected = selection_oracle(self.models["account"].values(),
                                    self.models["message"].values(),
                                    now_timestamp)
        actual = self.client.select_recent_messages(now_timestamp)
        assert {tuple(row) for row in actual} == expected
        assert len(actual) == len(expected)

    @initialize()
    def initialize_database(self):
        """Include all thirteen methods and join edge cases in each example."""
        self._assert_selection(4000)
        self._check_entity("account", (1, 3520, "192.0.2.1"),
                           (1, 3519, "192.0.2.2"))
        self._assert_selection(4000)
        self._check_entity("message", (1, 0, "hello", 1, 0),
                           (1, 9999, "changed", 99, 1))
        self._check_entity("feedback", (1, 1, "ok", "sent", "", 1),
                           (1, 2, "bad", "failed", "timeout", 2))
        self.create_account(2, 3519, "192.0.2.2")
        self.create_account(3, 4001, "192.0.2.1")
        self.create_account(4, 4000, "192.0.2.4")
        self.create_message(2, 4000, "hello", 1, 1)
        self.create_message(3, 1, "hello", 3, 0)
        self.create_message(4, 99999, "old account", 2, 0)
        self.create_message(5, 4000, "orphan", 99, 0)
        self._assert_selection(4000)

    @rule(uid=UIDS, timestamp=TIMESTAMPS, ip=IPS)
    def create_account(self, uid, timestamp, ip):
        """Create or replace an Account tuple through RPC."""
        row = (uid, timestamp, ip)
        assert self.client.create_account(*row) == list(row)
        self.models["account"][uid] = row

    @rule(uid=UIDS)
    def get_account_by_id(self, uid):
        """Read one existing or missing account."""
        expected = self.models["account"].get(uid)
        assert self.client.get_account_by_id(uid) == (
            list(expected) if expected is not None else None
        )

    @rule()
    def get_all_accounts(self):
        """Compare complete account records with the model."""
        assert self.client.get_all_accounts() == [
            list(row) for row in self.models["account"].values()
        ]

    @rule(uid=UIDS, timestamp=TIMESTAMPS, ip=IPS)
    def update_account(self, uid, timestamp, ip):
        """Update an account without inserting a missing ID."""
        row = (uid, timestamp, ip)
        expected = None
        if uid in self.models["account"]:
            self.models["account"][uid] = row
            expected = list(row)
        assert self.client.update_account(*row) == expected

    @rule(uid=UIDS, timestamp=TIMESTAMPS, argument=TEXTS,
          account=UIDS, completed=st.integers(0, 1))
    def create_message(self, uid, timestamp, argument, account, completed):
        """Create a Message with all five ER fields."""
        row = (uid, timestamp, argument, account, completed)
        assert self.client.create_message(*row) == list(row)
        self.models["message"][uid] = row

    @rule(uid=UIDS)
    def get_message_by_id(self, uid):
        """Read one existing or missing message."""
        expected = self.models["message"].get(uid)
        assert self.client.get_message_by_id(uid) == (
            list(expected) if expected is not None else None
        )

    @rule()
    def get_all_messages(self):
        """Compare complete message records with the model."""
        assert self.client.get_all_messages() == [
            list(row) for row in self.models["message"].values()
        ]

    @rule(uid=UIDS, timestamp=TIMESTAMPS, argument=TEXTS,
          account=UIDS, completed=st.integers(0, 1))
    def update_message(self, uid, timestamp, argument, account, completed):
        """Update a message without inserting a missing ID."""
        row = (uid, timestamp, argument, account, completed)
        expected = None
        if uid in self.models["message"]:
            self.models["message"][uid] = row
            expected = list(row)
        assert self.client.update_message(*row) == expected

    @rule(uid=UIDS, timestamp=TIMESTAMPS, result=TEXTS, status=TEXTS,
          failure=TEXTS, message=UIDS)
    def create_feedback(
        self, uid, timestamp, result, status, failure, message
    ):
        """Create Feedback with all six ER fields."""
        row = (uid, timestamp, result, status, failure, message)
        assert self.client.create_feedback(*row) == list(row)
        self.models["feedback"][uid] = row

    @rule(uid=UIDS)
    def get_feedback_by_id(self, uid):
        """Read one existing or missing feedback record."""
        expected = self.models["feedback"].get(uid)
        assert self.client.get_feedback_by_id(uid) == (
            list(expected) if expected is not None else None
        )

    @rule()
    def get_all_feedbacks(self):
        """Compare complete feedback records with the model."""
        assert self.client.get_all_feedbacks() == [
            list(row) for row in self.models["feedback"].values()
        ]

    @rule(uid=UIDS, timestamp=TIMESTAMPS, result=TEXTS, status=TEXTS,
          failure=TEXTS, message=UIDS)
    def update_feedback(
        self, uid, timestamp, result, status, failure, message
    ):
        """Update feedback without inserting a missing ID."""
        row = (uid, timestamp, result, status, failure, message)
        expected = None
        if uid in self.models["feedback"]:
            self.models["feedback"][uid] = row
            expected = list(row)
        assert self.client.update_feedback(*row) == expected

    @rule(now_timestamp=st.integers(3998, 4002))
    def select_recent_messages(self, now_timestamp):
        """Verify the full join projection after arbitrary state changes."""
        self._assert_selection(now_timestamp)


TestDatabaseRPC = DatabaseStateMachine.TestCase
TestDatabaseRPC.settings = settings(
    max_examples=25, stateful_step_count=40, deadline=None,
    derandomize=True,
)
