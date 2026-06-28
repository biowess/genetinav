from __future__ import annotations

import sqlite3
from pathlib import Path

from genetinav.utils.errors import DatabaseError


def get_db_path() -> Path:
    """Return the default database path, creating the parent directory if needed."""
    db_dir = Path.home() / ".genetinav"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "genetinav.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection to the SQLite database.

    If *db_path* is ``None``, the default path from :func:`get_db_path` is used.
    """
    if db_path is None:
        db_path = get_db_path()

    try:
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
    except sqlite3.OperationalError as exc:
        raise DatabaseError(
            "Unable to open the database. The file may be locked or corrupted."
        ) from exc

    conn.row_factory = sqlite3.Row

    try:
        conn.execute("PRAGMA foreign_keys = ON")
    except sqlite3.OperationalError as exc:
        conn.close()
        raise DatabaseError("Failed to enable foreign keys on the database.") from exc

    return conn


def initialize_schema(conn: sqlite3.Connection) -> None:
    """Create the application tables if they do not already exist."""
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                gene_symbol TEXT    NOT NULL,
                species     TEXT    NOT NULL,
                viewed_at   TEXT    NOT NULL,
                coordinates TEXT    NOT NULL,
                window_size INTEGER NOT NULL,
                cached      INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS favorites (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                gene_symbol TEXT    NOT NULL,
                species     TEXT    NOT NULL,
                added_at    TEXT    NOT NULL,
                UNIQUE(gene_symbol, species)
            );

            CREATE TABLE IF NOT EXISTS cache (
                key          TEXT PRIMARY KEY,
                response_data TEXT NOT NULL,
                created_at   TEXT NOT NULL,
                expires_at   TEXT
            );
            """
        )
    except sqlite3.OperationalError as exc:
        raise DatabaseError(
            "Failed to initialise the database schema. "
            "The database may be locked or the storage is full."
        ) from exc
