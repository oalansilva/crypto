from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path
from typing import Any

from sqlalchemy import or_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
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
from app.workflow_database import (
    bootstrap_project_workflow_db,
    get_workflow_engine_for_url,
    get_workflow_sessionmaker_for_url,
    init_workflow_schema_for_url,
)
from app.workflow_models import (
    AgentRun,
    Change,
    Project,
    WorkItem,
    WorkItemDependency,
    WorkItemLock,
    WorkflowApproval,
    WorkflowComment,
    WorkflowHandoff,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAIN_SQLITE = PROJECT_ROOT / "backend" / "backtest.db"
DEFAULT_WORKFLOW_SQLITE = PROJECT_ROOT / "workflow.db"
DEFAULT_OPTIMIZATION_SQLITE = PROJECT_ROOT / "backend" / "data" / "jobs" / "results.db"

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


def _load_sqlite_rows(path: Path, table: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def migrate_main_sqlite_to_postgres(sqlite_path: Path, optimization_sqlite_path: Path | None) -> list[tuple[str, int]]:
    database_url = os.getenv("CRYPTO_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url or not database_url.lower().startswith("postgresql"):
        raise SystemExit("CRYPTO_DATABASE_URL or DATABASE_URL must point to PostgreSQL")

    engine = create_engine(database_url, pool_pre_ping=True)
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
            rows = _load_sqlite_rows(sqlite_path, table_name) if sqlite_path.exists() else []
            count = _copy_by_primary_key(session, table_name, model, rows, key_fields)
            migrated_counts.append((table_name, count))

        if optimization_sqlite_path and optimization_sqlite_path.exists():
            rows = _load_sqlite_rows(optimization_sqlite_path, "optimization_results")
            count = _copy_by_primary_key(
                session,
                "optimization_results",
                OptimizationResult,
                rows,
                ("job_id", "result_index"),
            )
            migrated_counts.append(("optimization_results", count))
        else:
            migrated_counts.append(("optimization_results", 0))

    return migrated_counts


def _row_payload(obj, *, exclude: set[str] | None = None) -> dict[str, Any]:
    exclude = exclude or set()
    return {
        column.name: getattr(obj, column.name)
        for column in obj.__table__.columns
        if column.name not in exclude
    }


def _resolve_target_project_urls(source_project: Project) -> tuple[str | None, str | None]:
    mapping = {
        "crypto": (
            os.getenv("CRYPTO_DATABASE_URL"),
            os.getenv("CRYPTO_WORKFLOW_DATABASE_URL"),
        ),
        "kanban": (
            os.getenv("KANBAN_DATABASE_URL"),
            os.getenv("KANBAN_WORKFLOW_DATABASE_URL"),
        ),
    }
    default_main, default_workflow = mapping.get(source_project.slug, (None, None))
    return (
        source_project.database_url or default_main,
        source_project.workflow_database_url or default_workflow,
    )


def migrate_workflow_source_to_registry_and_projects(source_workflow_url: str) -> dict[str, dict[str, int]]:
    registry_url = os.getenv("WORKFLOW_DATABASE_URL")
    if not registry_url or not registry_url.lower().startswith("postgresql"):
        raise SystemExit("WORKFLOW_DATABASE_URL must point to PostgreSQL")

    source_engine = get_workflow_engine_for_url(source_workflow_url)
    SourceSession = sessionmaker(autocommit=False, autoflush=False, bind=source_engine)
    registry_engine = get_workflow_engine_for_url(registry_url)
    RegistrySession = sessionmaker(autocommit=False, autoflush=False, bind=registry_engine)
    init_workflow_schema_for_url(registry_url)

    summaries: dict[str, dict[str, int]] = {}

    with SourceSession() as source_db, RegistrySession() as registry_db:
        source_projects = source_db.query(Project).order_by(Project.created_at.asc()).all()
        for source_project in source_projects:
            database_url, workflow_database_url = _resolve_target_project_urls(source_project)
            if not workflow_database_url:
                raise SystemExit(
                    f"Project '{source_project.slug}' has no target workflow database URL configured"
                )
            if not workflow_database_url.lower().startswith("postgresql"):
                raise SystemExit(
                    f"Project '{source_project.slug}' workflow database must point to PostgreSQL"
                )

            target_project = registry_db.query(Project).filter(Project.slug == source_project.slug).first()
            if target_project is None:
                target_project = Project(
                    id=source_project.id,
                    slug=source_project.slug,
                    name=source_project.name,
                    root_directory=source_project.root_directory,
                    database_url=database_url,
                    frontend_url=source_project.frontend_url,
                    backend_url=source_project.backend_url,
                    workflow_database_url=workflow_database_url,
                    tech_stack=source_project.tech_stack,
                    created_at=source_project.created_at,
                )
                registry_db.add(target_project)
            else:
                target_project.name = source_project.name
                target_project.root_directory = source_project.root_directory
                target_project.database_url = database_url or target_project.database_url
                target_project.frontend_url = source_project.frontend_url
                target_project.backend_url = source_project.backend_url
                target_project.workflow_database_url = workflow_database_url
                target_project.tech_stack = source_project.tech_stack
            registry_db.commit()
            registry_db.refresh(target_project)
            bootstrap_project_workflow_db(target_project)

            ProjectSession = get_workflow_sessionmaker_for_url(workflow_database_url)
            with ProjectSession() as project_db:
                init_workflow_schema_for_url(workflow_database_url)
                existing_project = project_db.query(Project).filter(Project.slug == target_project.slug).first()
                if existing_project is None:
                    project_db.add(
                        Project(
                            id=target_project.id,
                            slug=target_project.slug,
                            name=target_project.name,
                            root_directory=target_project.root_directory,
                            database_url=target_project.database_url,
                            frontend_url=target_project.frontend_url,
                            backend_url=target_project.backend_url,
                            workflow_database_url=target_project.workflow_database_url,
                            tech_stack=target_project.tech_stack,
                            created_at=target_project.created_at,
                        )
                    )
                    project_db.commit()

                source_changes = source_db.query(Change).filter(Change.project_id == source_project.id).all()
                change_ids = [row.id for row in source_changes]

                source_agent_runs = source_db.query(AgentRun).filter(AgentRun.change_pk.in_(change_ids)).all() if change_ids else []
                source_work_items = source_db.query(WorkItem).filter(WorkItem.change_pk.in_(change_ids)).all() if change_ids else []
                work_item_ids = [row.id for row in source_work_items]

                source_deps = (
                    source_db.query(WorkItemDependency)
                    .filter(
                        or_(
                            WorkItemDependency.work_item_id.in_(work_item_ids),
                            WorkItemDependency.depends_on_id.in_(work_item_ids),
                        )
                    )
                    .all()
                    if work_item_ids
                    else []
                )
                source_locks = source_db.query(WorkItemLock).filter(WorkItemLock.work_item_id.in_(work_item_ids)).all() if work_item_ids else []
                source_comments = (
                    source_db.query(WorkflowComment)
                    .filter(
                        or_(
                            WorkflowComment.change_pk.in_(change_ids),
                            WorkflowComment.work_item_id.in_(work_item_ids),
                        )
                    )
                    .all()
                    if change_ids or work_item_ids
                    else []
                )
                source_approvals = (
                    source_db.query(WorkflowApproval)
                    .filter(
                        or_(
                            WorkflowApproval.change_pk.in_(change_ids),
                            WorkflowApproval.work_item_id.in_(work_item_ids),
                        )
                    )
                    .all()
                    if change_ids or work_item_ids
                    else []
                )
                source_handoffs = (
                    source_db.query(WorkflowHandoff)
                    .filter(
                        or_(
                            WorkflowHandoff.change_pk.in_(change_ids),
                            WorkflowHandoff.work_item_id.in_(work_item_ids),
                        )
                    )
                    .all()
                    if change_ids or work_item_ids
                    else []
                )

                counts = {
                    "changes": 0,
                    "agent_runs": 0,
                    "work_items": 0,
                    "dependencies": 0,
                    "locks": 0,
                    "comments": 0,
                    "approvals": 0,
                    "handoffs": 0,
                }

                for row in source_changes:
                    payload = _row_payload(row)
                    payload["project_id"] = target_project.id
                    existing = project_db.query(Change).filter(Change.id == row.id).first()
                    if existing is None:
                        project_db.add(Change(**payload))
                    else:
                        for key, value in payload.items():
                            setattr(existing, key, value)
                    counts["changes"] += 1
                project_db.commit()

                for collection_name, model, rows in [
                    ("agent_runs", AgentRun, source_agent_runs),
                    ("work_items", WorkItem, source_work_items),
                    ("dependencies", WorkItemDependency, source_deps),
                    ("locks", WorkItemLock, source_locks),
                    ("comments", WorkflowComment, source_comments),
                    ("approvals", WorkflowApproval, source_approvals),
                    ("handoffs", WorkflowHandoff, source_handoffs),
                ]:
                    for row in rows:
                        payload = _row_payload(row)
                        existing = project_db.query(model).filter(model.id == row.id).first()
                        if existing is None:
                            project_db.add(model(**payload))
                        else:
                            for key, value in payload.items():
                                setattr(existing, key, value)
                        counts[collection_name] += 1
                    project_db.commit()

                summaries[source_project.slug] = counts

    return summaries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--main-sqlite",
        default=str(DEFAULT_MAIN_SQLITE),
        help="Path to legacy main SQLite database",
    )
    parser.add_argument(
        "--optimization-sqlite",
        default=str(DEFAULT_OPTIMIZATION_SQLITE),
        help="Path to legacy optimization SQLite database",
    )
    parser.add_argument(
        "--source-workflow-url",
        default=None,
        help="Legacy workflow DB URL. Example: sqlite:////path/to/workflow.db or postgresql+psycopg2://...",
    )
    args = parser.parse_args()

    main_sqlite = Path(args.main_sqlite)
    optimization_sqlite = Path(args.optimization_sqlite) if args.optimization_sqlite else None

    workflow_url = args.source_workflow_url
    if workflow_url is None:
        if DEFAULT_WORKFLOW_SQLITE.exists():
            workflow_url = f"sqlite:///{DEFAULT_WORKFLOW_SQLITE}"
        else:
            workflow_url = os.getenv("SOURCE_WORKFLOW_DATABASE_URL")

    print("Migrating main runtime data to PostgreSQL...")
    main_counts = migrate_main_sqlite_to_postgres(main_sqlite, optimization_sqlite)
    for table_name, count in main_counts:
        print(f"  {table_name}: {count}")

    if workflow_url:
        print(f"Migrating workflow data from {workflow_url}...")
        workflow_counts = migrate_workflow_source_to_registry_and_projects(workflow_url)
        for project_slug, counts in workflow_counts.items():
            print(f"  project={project_slug}")
            for key, value in counts.items():
                print(f"    {key}: {value}")
    else:
        print("No legacy workflow source configured; skipped workflow migration.")


if __name__ == "__main__":
    main()
