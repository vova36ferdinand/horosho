"""Independent SQL oracle for the variant 15 relational expression."""

import sqlite3


def selection_oracle(accounts, messages, now_timestamp):
    """Filter a full outer join and project distinct IP/text pairs."""
    with sqlite3.connect(":memory:") as connection:
        connection.execute(
            "CREATE TABLE accounts (uid INT, timestamp INT, ip TEXT)"
        )
        connection.execute(
            "CREATE TABLE messages (uid INT, timestamp INT, argument TEXT, "
            "account INT, completed INT)"
        )
        connection.executemany("INSERT INTO accounts VALUES (?, ?, ?)",
                               accounts)
        connection.executemany("INSERT INTO messages VALUES (?, ?, ?, ?, ?)",
                               messages)
        rows = connection.execute(
            "SELECT DISTINCT ip, argument FROM ("
            "SELECT a.timestamp, a.ip, m.argument FROM accounts a "
            "LEFT JOIN messages m ON a.uid = m.account "
            "UNION ALL "
            "SELECT NULL, NULL, m.argument FROM messages m "
            "LEFT JOIN accounts a ON a.uid = m.account WHERE a.uid IS NULL"
            ") WHERE timestamp >= ?", (now_timestamp - 8 * 60,)
        ).fetchall()
    return set(rows)
