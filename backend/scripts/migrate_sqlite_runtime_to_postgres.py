from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import (
    AutoBacktestRun,
    BacktestResult,
    BacktestRun,
    ComboTemplate,
    FavoriteStrategy,
    MonitorPreference,
    OptimizationResult,
    PortfolioSnapshot,
    SystemPreference,
    User,
    UserExchangeCredential,
)
from app.models_signal_history import SignalHistory


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQLITE_PATH = PROJECT_ROOT / "backend" / "backtest.db"
JSON_COLUMNS_BY_TABLE: dict[str, set[str]] = {
    "favorite_strategies": {"parameters", "metrics"},
    "combo_templates": {"template_data", "optimization_schema"},
    "backtest_runs": {"strategies", "params", "stop_pct", "take_pct"},
    "backtest_results": {"result_json", "metrics_summary"},
    "auto_backtest_runs": {"stage_1_result", "stage_2_result", "stage_3_result"},
    "optimization_results": {"params_json", "metrics_json"},
}


def _decode_nested_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            parsed = __import__("json").loads(value)
        except Exception:
            return value
        if isinstance(parsed, str):
            return _decode_nested_json(parsed)
        return parsed
    return value


def _load_sqlite_rows(table: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(SQLITE_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _normalize_payload(table_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    for column in JSON_COLUMNS_BY_TABLE.get(table_name, set()):
        if column in normalized:
            normalized[column] = _decode_nested_json(normalized[column])
    return normalized


def _copy_by_primary_key(session, table_name: str, model, rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> int:
    migrated = 0
    for payload in rows:
        payload = _normalize_payload(table_name, payload)
        filters = {field: payload[field] for field in key_fields}
        existing = session.query(model).filter_by(**filters).first()
        if existing is None:
            existing = model(**payload)
            session.add(existing)
        else:
            for key, value in payload.items():
                setattr(existing, key, value)
        migrated += 1
    session.commit()
    return migrated


def main() -> None:
    from app.database import DB_URL

    if DB_URL.startswith("sqlite:"):
        raise SystemExit(f"Main DB is still SQLite ({DB_URL}); aborting migration.")

    engine = create_engine(DB_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    table_plan: list[tuple[str, Any, tuple[str, ...]]] = [
        ("users", User, ("id",)),
        ("favorite_strategies", FavoriteStrategy, ("id",)),
        ("monitor_preferences", MonitorPreference, ("user_id", "symbol")),
        ("combo_templates", ComboTemplate, ("name",)),
        ("system_preferences", SystemPreference, ("key",)),
        ("user_exchange_credentials", UserExchangeCredential, ("user_id", "provider")),
        ("signal_history", SignalHistory, ("id",)),
        ("auto_backtest_runs", AutoBacktestRun, ("run_id",)),
        ("backtest_runs", BacktestRun, ("id",)),
        ("backtest_results", BacktestResult, ("run_id",)),
        ("portfolio_snapshots", PortfolioSnapshot, ("id",)),
    ]

    migrated_counts: list[tuple[str, int]] = []
    with SessionLocal() as session:
        for table_name, model, key_fields in table_plan:
            rows = _load_sqlite_rows(table_name)
            count = _copy_by_primary_key(session, table_name, model, rows, key_fields)
            migrated_counts.append((table_name, count))

        optimization_db = PROJECT_ROOT / "backend" / "data" / "jobs" / "results.db"
        if optimization_db.exists():
            conn = sqlite3.connect(str(optimization_db))
            conn.row_factory = sqlite3.Row
            try:
                rows = [dict(row) for row in conn.execute("SELECT * FROM optimization_results").fetchall()]
            finally:
                conn.close()
            count = _copy_by_primary_key(session, "optimization_results", OptimizationResult, rows, ("job_id", "result_index"))
            migrated_counts.append(("optimization_results", count))
        else:
            migrated_counts.append(("optimization_results", 0))

    print("Migration completed:")
    for table_name, count in migrated_counts:
        print(f"{table_name}: {count}")


if __name__ == "__main__":
    main()
