import sqlite3
from datetime import datetime, timezone

from genetinav.db import initialize_schema
from genetinav.models import HistoryRecord


class HistoryManager:
    def __init__(self, conn: sqlite3.Connection, max_entries: int = 200):
        self.conn = conn
        self.max_entries = max_entries
        initialize_schema(self.conn)

    def add(self, gene_symbol: str, species: str, coordinates: str, window_size: int, cached: bool) -> int:
        viewed_at = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO history (gene_symbol, species, viewed_at, coordinates, window_size, cached)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (gene_symbol, species, viewed_at, coordinates, window_size, int(cached))
        )
        new_id = cursor.lastrowid
        self.conn.commit()

        self._prune()

        return new_id

    def _prune(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            DELETE FROM history
            WHERE id NOT IN (
                SELECT id FROM history
                ORDER BY viewed_at DESC
                LIMIT ?
            )
            """,
            (self.max_entries,)
        )
        self.conn.commit()

    def list(self, limit: int = 50, query: str | None = None) -> list[HistoryRecord]:
        cursor = self.conn.cursor()
        if query:
            cursor.execute(
                """
                SELECT * FROM history
                WHERE gene_symbol LIKE ?
                ORDER BY viewed_at DESC
                LIMIT ?
                """,
                (f"%{query}%", limit)
            )
        else:
            cursor.execute(
                """
                SELECT * FROM history
                ORDER BY viewed_at DESC
                LIMIT ?
                """,
                (limit,)
            )

        rows = cursor.fetchall()

        records = []
        for row in rows:
            record = HistoryRecord(
                id=row["id"],
                gene_symbol=row["gene_symbol"],
                species=row["species"],
                viewed_at=row["viewed_at"],
                coordinates=row["coordinates"],
                window_size=row["window_size"],
                cached=bool(row["cached"])
            )
            records.append(record)

        return records

    def delete(self, history_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM history WHERE id = ?", (history_id,))
        self.conn.commit()

    def clear(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM history")
        self.conn.commit()
