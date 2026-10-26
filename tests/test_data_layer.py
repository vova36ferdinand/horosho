"""Регрессии для обновления записей и границы временной выборки."""

import pytest

import data_layer


@pytest.fixture(autouse=True)
def clear_data():
    """Каждый тест получает пустое хранилище."""
    data_layer.ACCOUNTS.clear()
    data_layer.MESSAGES.clear()
    data_layer.LOGS.clear()
    yield
    data_layer.ACCOUNTS.clear()
    data_layer.MESSAGES.clear()
    data_layer.LOGS.clear()


@pytest.mark.parametrize(
    "entity,initial,updated,recreated",
    [
        ("account", (1, "127.0.0.1", 1000),
         (1, "192.0.2.1", 2000), (1, "192.0.2.2", 3000)),
        ("message", (1, "first", 1), (1, "updated", 2), (1, "again", 3)),
        ("log", (1, 1, "new"), (1, 2, "updated"), (1, 3, "again")),
    ],
)
def test_create_after_update(entity, initial, updated, recreated):
    """Создание существующего ID после обновления заменяет одну запись."""
    create = getattr(data_layer, f"create_{entity}")
    update = getattr(data_layer, f"update_{entity}")
    get_by_id = getattr(data_layer, f"get_{entity}_by_id")
    get_all = getattr(data_layer, f"get_all_{entity}s")
    create(*initial)
    update(*updated)
    assert list(create(*recreated)) == list(recreated)
    assert list(get_by_id(1)) == list(recreated)
    assert len(get_all()) == 1


def test_recent_messages_boundary():
    """Выборка включает точную границу и пропускает старые и чужие записи."""
    data_layer.create_account(1, "192.0.2.1", 3520)
    data_layer.create_account(2, "192.0.2.2", 3519.99)
    data_layer.create_account(3, "192.0.2.3", 4000)
    data_layer.create_message(1, "boundary", 1)
    data_layer.create_message(2, "old", 2)
    data_layer.create_message(3, "recent", 3)
    data_layer.create_message(4, "missing account", 99)
    assert data_layer.select_recent_messages(4000) == [
        ("192.0.2.1", "boundary"), ("192.0.2.3", "recent")
    ]
