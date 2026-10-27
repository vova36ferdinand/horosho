"""Interactive menu tests using the actual variant 15 data operations."""

import pytest

import data_layer
import repl


@pytest.mark.parametrize(
    "choice,answers,expected",
    [
        ("1", ["4", "4000", "192.0.2.4"], "(4, 4000, '192.0.2.4')"),
        ("2", [], "[(1, 4000, '192.0.2.1')]"),
        ("3", ["1"], "(1, 4000, '192.0.2.1')"),
        ("4", ["1", "3000", "192.0.2.9"], "(1, 3000, '192.0.2.9')"),
        ("5", ["4", "4000", "new", "1", "0"], "(4, 4000, 'new', 1, 0)"),
        ("6", [], "[(2, 1000, 'hello', 1, 0)]"),
        ("7", ["2"], "(2, 1000, 'hello', 1, 0)"),
        ("8", ["2", "4000", "new", "1", "1"], "(2, 4000, 'new', 1, 1)"),
        ("9", ["4", "4000", "ok", "sent", "", "2"],
         "(4, 4000, 'ok', 'sent', '', 2)"),
        ("10", [], "[(3, 1000, 'ok', 'sent', '', 2)]"),
        ("11", ["3"], "(3, 1000, 'ok', 'sent', '', 2)"),
        ("12", ["3", "4000", "ok", "done", "", "2"],
         "(3, 4000, 'ok', 'done', '', 2)"),
        ("13", [], "[('192.0.2.1', 'hello')]"),
    ],
)
@pytest.mark.usefixtures("empty_data")
def test_menu_command(monkeypatch, capsys, choice, answers, expected):
    """All thirteen menu items use complete records and the right operation."""
    data_layer.create_account(1, 4000, "192.0.2.1")
    data_layer.create_message(2, 1000, "hello", 1, 0)
    data_layer.create_feedback(3, 1000, "ok", "sent", "", 2)
    inputs = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
    monkeypatch.setattr(repl.time, "time", lambda: 4000)
    repl.execute_command(choice)
    assert expected in capsys.readouterr().out


def test_unknown_command(capsys):
    """Unknown commands produce a useful message."""
    repl.execute_command("99")
    assert "Неверный код команды!" in capsys.readouterr().out


def test_invalid_id(monkeypatch, capsys):
    """An invalid number does not escape the menu as an exception."""
    monkeypatch.setattr("builtins.input", lambda prompt: "abc")
    repl.execute_command("1")
    assert "Ошибка ввода данных:" in capsys.readouterr().out


def test_repl_continues_until_exit(monkeypatch, capsys):
    """The REPL accepts another command after an input error."""
    answers = iter([" 99 ", " 0 "])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    repl.run_repl()
    assert "Неверный код команды!" in capsys.readouterr().out
