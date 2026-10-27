"""Tuple storage and regressions for the full outer join projection."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

import data_layer
from tests.model_oracle import selection_oracle


@pytest.mark.parametrize(
    "entity,initial,updated,recreated",
    [
        ("account", (1, 1000, "192.0.2.1"), (1, 2000, "192.0.2.2"),
         (1, 3000, "192.0.2.3")),
        ("message", (1, 1000, "first", 1, 0), (1, 2000, "updated", 2, 1),
         (1, 3000, "again", 3, 0)),
        ("feedback", (1, 1000, "ok", "new", "", 1),
         (1, 2000, "error", "failed", "timeout", 2),
         (1, 3000, "ok", "done", "", 3)),
    ],
)
@pytest.mark.usefixtures("empty_data")
def test_tuple_records_after_update(entity, initial, updated, recreated):
    """Every CRUD operation keeps complete tuple records in schema order."""
    create = getattr(data_layer, f"create_{entity}")
    update = getattr(data_layer, f"update_{entity}")
    get_by_id = getattr(data_layer, f"get_{entity}_by_id")
    get_all = getattr(data_layer, f"get_all_{entity}s")
    assert get_by_id(1) is None
    assert update(*updated) is None
    assert create(*initial) == initial
    assert update(*updated) == updated
    assert create(*recreated) == recreated
    assert get_by_id(1) == recreated
    assert get_all() == [recreated]
    assert isinstance(get_all()[0], tuple)


@pytest.mark.usefixtures("empty_data")
def test_full_outer_join_selection():
    """Retain recent unmatched accounts, discard orphans, deduplicate pairs."""
    data_layer.create_account(1, 3520, "192.0.2.1")
    data_layer.create_account(2, 3519, "192.0.2.2")
    data_layer.create_account(3, 4000, "192.0.2.3")
    data_layer.create_account(4, 4001, "192.0.2.4")
    data_layer.create_account(5, 3999, "192.0.2.1")
    data_layer.create_message(1, 0, "boundary", 1, 0)
    data_layer.create_message(2, 9999, "old account", 2, 1)
    data_layer.create_message(3, 4000, "orphan", 99, 0)
    data_layer.create_message(4, 1, "boundary", 1, 1)
    data_layer.create_message(5, 1, "boundary", 5, 0)
    result = data_layer.select_recent_messages(4000)
    assert set(result) == {
        ("192.0.2.1", "boundary"), ("192.0.2.3", None),
        ("192.0.2.4", None)
    }
    assert len(result) == 3


@pytest.mark.usefixtures("empty_data")
def test_accounts_with_no_messages_are_not_lost():
    """An empty Message relation still retains recent accounts."""
    data_layer.create_account(1, 3520, "192.0.2.1")
    data_layer.create_account(2, 3520, "192.0.2.1")
    data_layer.create_account(3, 3519, "192.0.2.2")
    assert data_layer.select_recent_messages(4000) == [("192.0.2.1", None)]


@given(
    accounts=st.lists(
        st.tuples(st.integers(1, 6), st.integers(3518, 4002),
                  st.sampled_from(["192.0.2.1", "192.0.2.2"])),
        unique_by=lambda row: row[0], max_size=6,
    ),
    messages=st.lists(
        st.tuples(st.integers(1, 8), st.integers(0, 9999),
                  st.text(max_size=5), st.integers(1, 8), st.integers(0, 1)),
        unique_by=lambda row: row[0], max_size=8,
    ),
)
def test_selection_matches_sql_oracle(accounts, messages):
    """Generated relations agree with an independent SQL implementation."""
    data_layer.ACCOUNTS[:] = accounts
    data_layer.MESSAGES[:] = messages
    try:
        actual = data_layer.select_recent_messages(4000)
        assert set(actual) == selection_oracle(accounts, messages, 4000)
        assert len(actual) == len(set(actual))
    finally:
        data_layer.ACCOUNTS.clear()
        data_layer.MESSAGES.clear()
