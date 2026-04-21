# ============================================================================
# UnityAssetsManager - data_manager.py
# ============================================================================
# Description: Data manager (AssetDataManager) for CSV and SQLite sources.
# Version: 1.2.18
# ============================================================================

import sqlite3
import pandas as pd
import logging
import warnings
from pathlib import Path
from datetime import datetime
from .config import config

logger = logging.getLogger(__name__)


class AssetDataManager:
    """Gestionnaire de données assets avec cache et filtrage côté serveur"""

    _instance: "AssetDataManager | None" = None
    _df: pd.DataFrame | None = None
    _loaded_at: datetime | None = None
    _source_type: str | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def detect_source_type(path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in ['.db', '.sqlite', '.sqlite3']:
            return 'sqlite'
        return 'csv'

    @staticmethod
    def list_sqlite_tables(db_path: Path) -> list[str]:
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            logger.error(f"Erreur listing tables SQLite: {e}")
            return []

    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        if not force_reload and self._df is not None and self._loaded_at is not None:
            age = (datetime.now() - self._loaded_at).total_seconds()
            if age < config.cache_ttl_seconds:
                return self._df

        try:
            if config.data_path is None:
                return pd.DataFrame()

            data_path = Path(config.data_path)
            if not data_path.exists():
                return pd.DataFrame()

            self._source_type = self.detect_source_type(data_path)

            if self._source_type == 'sqlite':
                conn = sqlite3.connect(str(data_path))
                tables = self.list_sqlite_tables(data_path)
                table_name = config.db_table if config.db_table in tables else (tables[0] if tables else None)
                if not table_name:
                    return pd.DataFrame()

                # OPTIMIZATION: For large SQLite, we might NOT want to load everything in memory.
                # But currently apply_filter_stack uses Pandas.
                # For now, we still load everything if we want to keep current filtering logic.
                # TODO: Implement SQL-based filtering for SQLite source.
                self._df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                conn.close()
            else:
                # CSV logic
                with warnings.catch_warnings():
                    if not config.show_parser_warnings:
                        warnings.simplefilter('ignore', pd.errors.ParserWarning)
                    try:
                        self._df = pd.read_csv(
                            data_path, sep=None, engine='python', dtype_backend='numpy_nullable', on_bad_lines='warn', encoding='utf-8'
                        )
                    except UnicodeDecodeError:
                        self._df = pd.read_csv(
                            data_path, sep=None, engine='python', dtype_backend='numpy_nullable', on_bad_lines='warn', encoding='latin-1'
                        )

            self._loaded_at = datetime.now()
            return self._df
        except Exception as e:
            logger.error(f"❌ Erreur chargement: {e}")
            return pd.DataFrame()

    def get_data(self) -> pd.DataFrame:
        if self._df is None:
            return self.load_data()
        return self._df

    def reload(self):
        self.load_data(force_reload=True)


dm = AssetDataManager()
