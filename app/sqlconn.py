import sqlite3
from typing import Dict, Any, Optional


class DatabaseConnection:
    def __init__(self, db_path: str = "goodreads.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self):
        """Open connection/cursor if not already open."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, timeout=5)
            self.connection.execute("PRAGMA foreign_keys = ON;")
            self.cursor = self.connection.cursor()

    def disconnect(self):
        """Close connection and reset state."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def _row_to_dict(self, row: Optional[tuple]) -> Optional[Dict[str, Any]]:
        """Convert a DB row tuple to dict using cursor column metadata."""
        if row is None:
            return None
        assert self.cursor is not None
        columns = [d[0] for d in self.cursor.description]
        return dict(zip(columns, row))

    def Query(self, sql: str, params: tuple = (), fetch: str = "none", return_type: str = "dict"):
        if fetch not in ("none", "one", "all"):
            raise ValueError("fetch must be 'none', 'one', or 'all'")
        if return_type not in ("dict", "df"):
            raise ValueError("return_type must be 'dict' or 'df'")

        self.connect()
        assert self.connection is not None
        assert self.cursor is not None
        try:
            self.cursor.execute(sql, params)

            if fetch == "none":
                self.connection.commit()
                return {"rowcount": self.cursor.rowcount, "lastrowid": self.cursor.lastrowid}

            if fetch == "one":
                row = self.cursor.fetchone()
                row_dict = self._row_to_dict(row)
                if return_type == "dict":
                    return row_dict
                import pandas as pd
                return pd.DataFrame([row_dict]) if row_dict is not None else pd.DataFrame()

            rows = self.cursor.fetchall()
            data = [self._row_to_dict(r) for r in rows]
            if return_type == "dict":
                return data
            import pandas as pd
            return pd.DataFrame(data)

        except sqlite3.Error:
            if self.connection:
                self.connection.rollback()
            raise
        finally:
            self.disconnect()


# Global instance for convenient import/use:
db = DatabaseConnection("goodreads.db")