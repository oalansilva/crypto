from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.routes import system_preferences


def _session_factory(tmp_path: Path):
    db_file = tmp_path / "system_preferences_test.db"
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_admin_can_put_get_and_delete_system_preferences(tmp_path: Path):
    SessionLocal = _session_factory(tmp_path)
    with SessionLocal() as db:
        created = system_preferences.put_system_preferences(
            system_preferences.SystemPreferencesPayload(
                signal_history_min_confidence=78,
                signal_history_min_reward_risk=2.4,
                signal_history_max_reward_risk=4.5,
                signal_history_min_rsi=28,
                signal_history_max_rsi=36,
                signal_history_allow_neutral_macd=True,
                signal_history_allow_buy=True,
                signal_history_allow_sell=False,
                signal_history_allow_conservative=False,
                signal_history_allow_moderate=True,
                signal_history_allow_aggressive=True,
            ),
            admin_user_id="admin-user",
            db=db,
        )
        status = system_preferences.get_system_preferences(_admin_user_id="admin-user", db=db)
        deleted = system_preferences.delete_system_preferences(_admin_user_id="admin-user", db=db)
        empty = system_preferences.get_system_preferences(_admin_user_id="admin-user", db=db)

    assert created.signal_history_min_confidence == 78
    assert created.signal_history_min_reward_risk == 2.4
    assert created.signal_history_max_reward_risk == 4.5
    assert created.signal_history_min_rsi == 28
    assert created.signal_history_max_rsi == 36
    assert created.signal_history_allow_neutral_macd is True
    assert created.signal_history_allow_buy is True
    assert created.signal_history_allow_sell is False
    assert created.signal_history_allow_conservative is False
    assert created.signal_history_allow_moderate is True
    assert created.signal_history_allow_aggressive is True
    assert status.signal_history_min_confidence == 78
    assert status.signal_history_min_reward_risk == 2.4
    assert status.signal_history_max_reward_risk == 4.5
    assert status.signal_history_min_rsi == 28
    assert status.signal_history_max_rsi == 36
    assert status.signal_history_allow_neutral_macd is True
    assert status.signal_history_allow_buy is True
    assert status.signal_history_allow_sell is False
    assert status.signal_history_allow_conservative is False
    assert status.signal_history_allow_moderate is True
    assert status.signal_history_allow_aggressive is True
    assert deleted["message"] == "System preferences cleared"
    assert empty.signal_history_min_confidence == 78
    assert empty.signal_history_min_reward_risk == 2.4
    assert empty.signal_history_max_reward_risk == 4.5
    assert empty.signal_history_min_rsi == 28
    assert empty.signal_history_max_rsi == 36
    assert empty.signal_history_allow_neutral_macd is True
    assert empty.signal_history_allow_buy is True
    assert empty.signal_history_allow_sell is False
    assert empty.signal_history_allow_conservative is False
    assert empty.signal_history_allow_moderate is True
    assert empty.signal_history_allow_aggressive is True
