"""Tuple records for the Account, Message and Feedback relations."""

TIME_LIMIT_MINUTES = 8
SECONDS_IN_MINUTE = 60

ACCOUNTS = []
MESSAGES = []
FEEDBACKS = []


def _save_record(table: list, record: tuple, create: bool) -> tuple | None:
    """Replace a tuple by ID, optionally inserting a missing record."""
    for index, existing in enumerate(table):
        if existing[0] == record[0]:
            table[index] = record
            return record
    if create:
        table.append(record)
        return record
    return None


def _get_record(table: list, uid: int) -> tuple | None:
    """Return a tuple by ID, or None if the record is missing."""
    for record in table:
        if record[0] == uid:
            return record
    return None


def create_account(uid: int, timestamp: int, ip: str) -> tuple:
    """Create account records using the variant 15 schema."""
    return _save_record(ACCOUNTS, (uid, timestamp, ip), True)


def get_all_accounts() -> list:
    """Get all account records using the variant 15 schema."""
    return ACCOUNTS


def get_account_by_id(uid: int) -> tuple | None:
    """Get by id account records using the variant 15 schema."""
    return _get_record(ACCOUNTS, uid)


def update_account(uid: int, timestamp: int, ip: str) -> tuple | None:
    """Update account records using the variant 15 schema."""
    return _save_record(ACCOUNTS, (uid, timestamp, ip), False)


def create_message(
    uid: int, timestamp: int, argument: str, account: int,
    completed: int
) -> tuple:
    """Create message records using the variant 15 schema."""
    return _save_record(
        MESSAGES, (uid, timestamp, argument, account, completed), True
    )


def get_all_messages() -> list:
    """Get all message records using the variant 15 schema."""
    return MESSAGES


def get_message_by_id(uid: int) -> tuple | None:
    """Get by id message records using the variant 15 schema."""
    return _get_record(MESSAGES, uid)


def update_message(
    uid: int, timestamp: int, argument: str, account: int,
    completed: int
) -> tuple | None:
    """Update message records using the variant 15 schema."""
    return _save_record(
        MESSAGES, (uid, timestamp, argument, account, completed), False
    )


def create_feedback(
    uid: int, timestamp: int, result: str, status: str, failure: str,
    message: int
) -> tuple:
    """Create feedback records using the variant 15 schema."""
    return _save_record(
        FEEDBACKS, (uid, timestamp, result, status, failure, message), True
    )


def get_all_feedbacks() -> list:
    """Get all feedback records using the variant 15 schema."""
    return FEEDBACKS


def get_feedback_by_id(uid: int) -> tuple | None:
    """Get by id feedback records using the variant 15 schema."""
    return _get_record(FEEDBACKS, uid)


def update_feedback(
    uid: int, timestamp: int, result: str, status: str, failure: str,
    message: int
) -> tuple | None:
    """Update feedback records using the variant 15 schema."""
    return _save_record(
        FEEDBACKS, (uid, timestamp, result, status, failure, message), False
    )


def _full_outer_join_accounts_messages() -> list:
    """Join on A.uid = M.account, filling unmatched sides with None."""
    joined = []
    matched_messages = set()
    for account in ACCOUNTS:
        matches = [message for message in MESSAGES
                   if account[0] == message[3]]
        for message in matches:
            joined.append((account, message))
            matched_messages.add(message[0])
        if not matches:
            joined.append((account, None))
    joined.extend((None, message) for message in MESSAGES
                  if message[0] not in matched_messages)
    return joined


def select_recent_messages(now_timestamp: float) -> list:
    """Apply variant 15 selection and distinct projection to a full join."""
    threshold = now_timestamp - TIME_LIMIT_MINUTES * SECONDS_IN_MINUTE
    result = []
    seen = set()
    for account, message in _full_outer_join_accounts_messages():
        if account is None or account[1] is None or account[1] < threshold:
            continue
        row = (account[2], message[2] if message is not None else None)
        if row not in seen:
            result.append(row)
            seen.add(row)
    return result
