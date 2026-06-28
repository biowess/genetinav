import sqlite3
from datetime import datetime, timezone

from genetinav.db import initialize_schema
from genetinav.models import FavoriteRecord


class FavoritesManager:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        initialize_schema(self._conn)

    def add(self, gene_symbol: str, species: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        try:
            cursor = self._conn.execute(
                """
                INSERT INTO favorites (gene_symbol, species, added_at)
                VALUES (?, ?, ?)
                """,
                (gene_symbol, species, now),
            )
            self._conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor = self._conn.execute(
                """
                SELECT id FROM favorites
                WHERE gene_symbol = ? AND species = ?
                """,
                (gene_symbol, species),
            )
            return cursor.fetchone()["id"]

    def remove(self, gene_symbol: str, species: str) -> None:
        self._conn.execute(
            """
            DELETE FROM favorites
            WHERE gene_symbol = ? AND species = ?
            """,
            (gene_symbol, species),
        )
        self._conn.commit()

    def list(self, order: str = "alpha") -> list[FavoriteRecord]:
        if order == "alpha":
            order_by = "gene_symbol ASC"
        elif order == "recent":
            order_by = "added_at DESC"
        else:
            raise ValueError(f"Invalid order: {order}")

        cursor = self._conn.execute(
            f"""
            SELECT id, gene_symbol, species, added_at
            FROM favorites
            ORDER BY {order_by}
            """
        )
        
        return [
            FavoriteRecord(
                id=row["id"],
                gene_symbol=row["gene_symbol"],
                species=row["species"],
                added_at=row["added_at"],
            )
            for row in cursor
        ]

    def is_favorite(self, gene_symbol: str, species: str) -> bool:
        cursor = self._conn.execute(
            """
            SELECT 1 FROM favorites
            WHERE gene_symbol = ? AND species = ?
            """,
            (gene_symbol, species),
        )
        return cursor.fetchone() is not None
