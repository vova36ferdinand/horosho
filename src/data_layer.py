"""In-memory data layer for accounts, messages, and logs."""

TIME_LIMIT_MINUTES = 8
SECONDS_IN_MINUTE = 60

ACCOUNTS = []
MESSAGES = []
LOGS = []


# Создаю аккаунт
def create_account(uid: int, ip: str, ts: float) -> list:
    """Create an account or update an existing account."""
    for account in ACCOUNTS:
        if account[0] == uid:
            account[1] = ip
            account[2] = ts
            return account

    new_account = [uid, ip, ts]
    ACCOUNTS.append(new_account)
    return new_account


# Даёт список всех аккаунтов
def get_all_accounts() -> list:
    """Return all accounts."""
    return ACCOUNTS


# Находит запись аккаунта по uID
def get_account_by_id(uid: int) -> list | tuple | None:
    """Return an account by ID, or None if it does not exist."""
    for account in ACCOUNTS:
        if account[0] == uid:
            return account
    return None


# Обновляем запись аккаунта по uID
def update_account(uid: int, ip: str, timestamp: float) -> tuple | None:
    """Update an account by ID."""
    for index, account in enumerate(ACCOUNTS):
        if account[0] == uid:
            updated = (uid, ip, timestamp)
            ACCOUNTS[index] = updated
            return updated
    return None


def create_message(msg_id: int, text: str, account: int) -> list:
    """Создает сообщение или обновляет существующее по msg_id."""
    # или messages
    for message in MESSAGES:
        if message[0] == msg_id:
            message[1] = text
            message[2] = account
            return message

    new_message = [msg_id, text, account]
    MESSAGES.append(new_message)
    return new_message


# Даёт список всех сообщений
def get_all_messages() -> list:
    """Return all messages."""
    return MESSAGES


# Ищет сообщение по его ID
def get_message_by_id(uid: int) -> list | tuple | None:
    """Return a message by ID, or None if it does not exist."""
    for message in MESSAGES:
        if message[0] == uid:
            return message
    return None


# Редактирует сообщение
def update_message(
    uid: int, argument: str, account: int
) -> tuple | None:
    """Update a message by ID."""
    for index, message in enumerate(MESSAGES):
        if message[0] == uid:
            updated = (uid, argument, account)
            MESSAGES[index] = updated
            return updated
    return None


def create_log(log_id: int, info: str, status: int) -> list:
    """Создает лог или обновляет существующий по log_id."""
    # или logs
    for log_entry in LOGS:
        if log_entry[0] == log_id:
            log_entry[1] = info
            log_entry[2] = status
            return log_entry

    new_log = [log_id, info, status]
    LOGS.append(new_log)
    return new_log


# Даёт список всех логов
def get_all_logs() -> list:
    """Return all logs."""
    return LOGS


# Находит запись лога по ID
def get_log_by_id(uid: int) -> list | tuple | None:
    """Return a log by ID, or None if it does not exist."""
    for log_entry in LOGS:
        if log_entry[0] == uid:
            return log_entry
    return None


# Обновляет данные лога по ID
def update_log(uid: int, message: int, status: str) -> tuple | None:
    """Update a log by ID."""
    for index, log_entry in enumerate(LOGS):
        if log_entry[0] == uid:
            updated = (uid, message, status)
            LOGS[index] = updated
            return updated
    return None


# Выполняет выборку по формуле реляционной алгебры
def select_recent_messages(now_timestamp: float) -> list:
    """Return messages linked to accounts active in the last eight minutes."""
    threshold = now_timestamp - TIME_LIMIT_MINUTES * SECONDS_IN_MINUTE
    result = []
    for message in MESSAGES:
        account_id = message[2]
        account = get_account_by_id(account_id)
        if account is not None and account[2] >= threshold:
            result.append((account[1], message[1]))
    return result
