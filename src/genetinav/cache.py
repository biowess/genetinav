import datetime
import sqlite3

from genetinav.db import get_connection, initialize_schema
from genetinav.utils.errors import CacheError

class CacheManager:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        initialize_schema(self.conn)

    def set(self, key: str, response_data: str, ttl_seconds: int | None = None) -> None:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            created_at = now.isoformat()
            
            if ttl_seconds is not None:
                expires_at = (now + datetime.timedelta(seconds=ttl_seconds)).isoformat()
            else:
                expires_at = None
                
            self.conn.execute(
                """
                INSERT INTO cache (key, response_data, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    response_data=excluded.response_data,
                    created_at=excluded.created_at,
                    expires_at=excluded.expires_at
                """,
                (key, response_data, created_at, expires_at)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise CacheError(f"Cache read/write failed: {e}") from e

    def get(self, key: str) -> str | None:
        try:
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            cursor = self.conn.execute(
                "SELECT response_data, expires_at FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
                
            expires_at = row["expires_at"]
            if expires_at is not None and expires_at <= now_iso:
                self.delete(key)
                return None
                
            return row["response_data"]
        except sqlite3.Error as e:
            raise CacheError(f"Cache read/write failed: {e}") from e

    def clear(self) -> None:
        try:
            self.conn.execute("DELETE FROM cache")
            self.conn.commit()
        except sqlite3.Error as e:
            raise CacheError(f"Cache read/write failed: {e}") from e

    def delete(self, key: str) -> None:
        try:
            self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            self.conn.commit()
        except sqlite3.Error as e:
            raise CacheError(f"Cache read/write failed: {e}") from e
