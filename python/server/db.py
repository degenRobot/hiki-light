import sqlite3

from server.types import ConvoMessage


def init_db(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute(
        """
				CREATE TABLE IF NOT EXISTS users (
        id STRING PRIMARY KEY,
				address STRING UNIQUE NOT NULL,
				name STRING NOT NULL
				)
			"""
    )
    cur.execute(
        """
				CREATE TABLE IF NOT EXISTS challenges (
        id STRING PRIMARY KEY,
				address STRING UNIQUE NOT NULL,
				nonce STRING NOT NULL,
        expires_at TIMESTAMP NOT NULL
				)
				"""
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
        id STRING PRIMARY KEY,
        address STRING NOT NULL,
        char_id STRING NOT NULL,
        sender STRING NOT NULL,
        message STRING NOT NULL,
        timestamp TIMESTAMP NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS summaries (
          id STRING PRIMARY KEY,
          address STRING NOT NULL,
          char_id STRING NOT NULL,
          summary STRING NOT NULL,
          convo_cutoff TIMESTAMP NOT NULL
        )
        """
    )


def get_sqlite_conn():
    con = sqlite3.connect("aiwaifus.sqlite", check_same_thread=False)
    return con


def get_nonce(con: sqlite3.Connection, address: str) -> tuple[str, int] | None:
    cur = con.cursor()
    cur.execute("SELECT nonce, expires_at FROM challenges WHERE address=?", (address,))
    return cur.fetchone()


def set_nonce(con: sqlite3.Connection, address: str, nonce: str):
    cur = con.cursor()
    expires_at = 60 * 5  # 5 minutes
    cur.execute(
        "INSERT OR REPLACE INTO challenges (id, address, nonce, expires_at) VALUES (?, ?, ?, ?)",
        (f"challlenge_{address}", address, nonce, expires_at),
    )
    con.commit()


def delete_nonce(con: sqlite3.Connection, address: str):
    cur = con.cursor()
    cur.execute("DELETE FROM challenges WHERE address=?", (address,))
    con.commit()


def signup_user(con: sqlite3.Connection, address: str, name: str | None):
    if name is None:
        name = "Anon"
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (id, address, name) VALUES (?, ?, ?)",
        (f"user_{address}", address, name),
    )
    con.commit()


def get_conversation(
    con: sqlite3.Connection, address: str, char_id: str, cutoff: int | None
) -> list[ConvoMessage]:
    if cutoff is None:
        cutoff = 0
    cur = con.cursor()
    cur.execute(
        "SELECT sender, message, timestamp FROM messages WHERE address=? AND char_id=? AND timestamp >= ?",
        (address, char_id, cutoff),
    )
    return [
        ConvoMessage(sender=sender, message=message, timestamp=timestamp)
        for sender, message, timestamp in cur.fetchall()
    ]


def set_conversation(
    con: sqlite3.Connection,
    address: str,
    char_id: str,
    messages: list[ConvoMessage],
):
    cur = con.cursor()

    for message in messages:
        cur.execute(
            "INSERT INTO messages (id, address, char_id, sender, message, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (
                f"message_{address}_{char_id}_{message.timestamp}_{message.sender}",
                address,
                char_id,
                message.sender,
                message.message,
                message.timestamp,
            ),
        )

    con.commit()


def get_summary(
    con: sqlite3.Connection, address: str, char_id: str
) -> tuple[str, int] | None:
    cur = con.cursor()
    cur.execute(
        "SELECT summary, convo_cutoff FROM summaries WHERE address=? AND char_id=?",
        (address, char_id),
    )
    return cur.fetchone()


def set_summary(
    con: sqlite3.Connection, address: str, char_id: str, summary: str, convo_cutoff: int
):
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO summaries (id, address, char_id, summary, convo_cutoff) VALUES (?, ?, ?, ?, ?)",
        (f"summary_{address}_{char_id}", address, char_id, summary, convo_cutoff),
    )
    con.commit()
