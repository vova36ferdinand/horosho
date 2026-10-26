"""Проверки команд меню и обработки пользовательского ввода."""

import pytest

import repl


@pytest.mark.parametrize(
    "choice,operation,answers,arguments",
    [
        ("1", "create_account", ["1", "127.0.0.1"], (1, "127.0.0.1", 4000)),
        ("2", "get_all_accounts", [], ()),
        ("3", "get_account_by_id", ["1"], (1,)),
        ("4", "update_account", ["1", "192.0.2.1"], (1, "192.0.2.1", 4000)),
        ("5", "create_message", ["2", "Привет", "1"], (2, "Привет", 1)),
        ("6", "get_all_messages", [], ()),
        ("7", "get_message_by_id", ["2"], (2,)),
        ("8", "update_message", ["2", "Новый текст", "1"],
         (2, "Новый текст", 1)),
        ("9", "create_log", ["3", "2", "ok"], (3, 2, "ok")),
        ("10", "get_all_logs", [], ()),
        ("11", "get_log_by_id", ["3"], (3,)),
        ("12", "update_log", ["3", "2", "done"], (3, 2, "done")),
        ("13", "select_recent_messages", [], (4000,)),
    ],
)
def test_menu_command(monkeypatch, capsys, choice, operation, answers,
                      arguments):
    """Каждая команда вызывает нужную операцию с введёнными аргументами."""
    inputs = iter(answers)
    calls = []
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr(repl.time, "time", lambda: 4000)
    monkeypatch.setattr(
        repl, operation, lambda *args: calls.append(args) or "результат"
    )
    repl.execute_command(choice)
    assert calls == [arguments]
    assert "результат" in capsys.readouterr().out


def test_unknown_command(capsys):
    """Неизвестная команда выводит понятную ошибку."""
    repl.execute_command("99")
    assert "Неверный код команды!" in capsys.readouterr().out


def test_invalid_id(monkeypatch, capsys):
    """Нечисловой ID не завершает меню исключением."""
    monkeypatch.setattr("builtins.input", lambda prompt: "abc")
    repl.execute_command("1")
    assert "Ошибка ввода данных:" in capsys.readouterr().out


def test_repl_continues_until_exit(monkeypatch, capsys):
    """После ошибочной команды меню принимает следующую и завершает цикл."""
    answers = iter([" 99 ", " 0 "])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    repl.run_repl()
    assert "Неверный код команды!" in capsys.readouterr().out
