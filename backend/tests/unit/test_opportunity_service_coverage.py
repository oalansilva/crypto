from __future__ import annotations

import pandas as pd
import time
from uuid import uuid4

from app.database import SessionLocal
from app.models import FavoriteStrategy, User
from app.services.market_data_providers import CCXT_SOURCE, STOOQ_SOURCE
from app.services.opportunity_service import OpportunityService, _normalize_market_timeframe
from app.services import opportunity_service


def _sample_ohlcv():
    ts = pd.to_datetime(
        ["2026-04-20T00:00:00Z", "2026-04-21T00:00:00Z", "2026-04-22T00:00:00Z"],
        utc=True,
    )
    ts_values = (ts.astype("int64") // 1_000_000_000).astype("int64")
    return pd.DataFrame(
        {
            "timestamp": ts_values,
            "timestamp_utc": ts,
            "time": ts,
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [10, 10, 10],
        },
        index=ts,
    )


class _FakeComboStrategy:
    def __init__(
        self, *args, entry_logic: str = "", exit_logic: str = "", stop_loss: float = 0.0, **kwargs
    ):
        self.entry_logic = entry_logic
        self.exit_logic = exit_logic
        self.stop_loss = stop_loss

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["short"] = out["close"] * 0.9
        out["medium"] = out["close"] * 1.0
        out["long"] = out["close"] * 1.1
        return out

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(signal=0, signal_reason=pd.NA)


class _FailingProvider:
    def __init__(self):
        self.calls = 0

    def fetch_ohlcv(self, *_args, **_kwargs):
        self.calls += 1
        raise RuntimeError("provider-failed")


class _DelayAndReturnProvider:
    def __init__(self, delay_seconds: float, delayed_symbol: str):
        self.calls = 0
        self.delay_seconds = delay_seconds
        self.delayed_symbol = delayed_symbol

    def fetch_ohlcv(self, symbol: str, timeframe: str, since_str=None, until_str=None, limit=None):
        self.calls += 1
        if symbol == self.delayed_symbol:
            time.sleep(self.delay_seconds)
        return _sample_ohlcv()


class _MockProvider:
    def __init__(self, df):
        self.df = df
        self.calls = 0

    def fetch_ohlcv(self, *_args, **_kwargs):
        self.calls += 1
        return self.df.copy()


def _sample_favorite(
    symbol: str, timeframe: str, template="trend", data_source: str = STOOQ_SOURCE
):
    return {
        "id": 7,
        "name": "Test Favorite",
        "symbol": symbol,
        "timeframe": timeframe,
        "strategy_name": template,
        "parameters": {"data_source": data_source},
        "tier": 1,
        "notes": None,
    }


def _db_user(email: str) -> User:
    return User(
        id=uuid4(),
        email=email,
        password_hash="hash",
        name=email.split("@", 1)[0],
        status="active",
    )


def _db_favorite(
    user_id: str, symbol: str, name: str, tier: int | None = 1, notes: str | None = None
) -> FavoriteStrategy:
    return FavoriteStrategy(
        user_id=user_id,
        name=name,
        symbol=symbol,
        timeframe="1d",
        strategy_name="multi_ma_crossover",
        parameters={"data_source": CCXT_SOURCE, "ema_short": 9},
        metrics={},
        tier=tier,
        notes=notes,
    )


def test_normalize_market_timeframe():
    assert _normalize_market_timeframe("AAPL", "15m", STOOQ_SOURCE) == "1d"
    assert _normalize_market_timeframe("AAPL", "1d", STOOQ_SOURCE) == "1d"
    assert _normalize_market_timeframe("BTC/USDT", "4h", CCXT_SOURCE) == "4h"


def test_get_favorites_falls_back_to_admin_curated_rows(monkeypatch):
    monkeypatch.setattr(opportunity_service, "ADMIN_EMAILS", {"admin@example.com"})
    admin = _db_user("admin@example.com")
    common = _db_user("common@example.com")

    with SessionLocal() as db:
        db.add_all([admin, common])
        db.flush()
        admin_id = str(admin.id)
        common_id = str(common.id)
        db.add(_db_favorite(admin_id, "BTC/USDT", "Admin curated", tier=1))
        db.commit()

    service = OpportunityService()
    favorites = service.get_favorites(common_id, tier_filter="1")

    assert len(favorites) == 1
    assert favorites[0]["name"] == "Admin curated"
    assert favorites[0]["symbol"] == "BTC/USDT"


def test_get_favorites_keeps_user_rows_authoritative(monkeypatch):
    monkeypatch.setattr(opportunity_service, "ADMIN_EMAILS", {"admin@example.com"})
    admin = _db_user("admin@example.com")
    common = _db_user("common@example.com")

    with SessionLocal() as db:
        db.add_all([admin, common])
        db.flush()
        admin_id = str(admin.id)
        common_id = str(common.id)
        db.add_all(
            [
                _db_favorite(admin_id, "BTC/USDT", "Admin curated", tier=1),
                _db_favorite(common_id, "ETH/USDT", "Common own", tier=1),
            ]
        )
        db.commit()

    service = OpportunityService()
    favorites = service.get_favorites(common_id, tier_filter="1")

    assert len(favorites) == 1
    assert favorites[0]["name"] == "Common own"
    assert favorites[0]["symbol"] == "ETH/USDT"


def test_get_favorites_fallback_respects_tier_filter(monkeypatch):
    monkeypatch.setattr(opportunity_service, "ADMIN_EMAILS", {"admin@example.com"})
    admin = _db_user("admin@example.com")
    common = _db_user("common@example.com")

    with SessionLocal() as db:
        db.add_all([admin, common])
        db.flush()
        admin_id = str(admin.id)
        common_id = str(common.id)
        db.add_all(
            [
                _db_favorite(admin_id, "BTC/USDT", "Tier one", tier=1),
                _db_favorite(admin_id, "ETH/USDT", "Tier two", tier=2),
            ]
        )
        db.commit()

    service = OpportunityService()
    favorites = service.get_favorites(common_id, tier_filter="2")

    assert len(favorites) == 1
    assert favorites[0]["name"] == "Tier two"


def test_get_favorites_falls_back_when_user_rows_are_not_monitor_candidates(monkeypatch):
    monkeypatch.setattr(opportunity_service, "ADMIN_EMAILS", {"admin@example.com"})
    admin = _db_user("admin@example.com")
    common = _db_user("common@example.com")

    with SessionLocal() as db:
        db.add_all([admin, common])
        db.flush()
        admin_id = str(admin.id)
        common_id = str(common.id)
        db.add_all(
            [
                _db_favorite(common_id, "AAPL", "Common stock", tier=1),
                _db_favorite(admin_id, "BTC/USDT", "Admin curated", tier=1),
            ]
        )
        db.commit()

    service = OpportunityService()
    favorites = service.get_favorites(common_id, tier_filter="1")

    assert len(favorites) == 1
    assert favorites[0]["name"] == "Admin curated"
    assert favorites[0]["is_curated_fallback"] is True


def test_get_favorites_uses_configured_admin_email_order(monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", "second@example.com,first@example.com")
    first = _db_user("first@example.com")
    second = _db_user("second@example.com")
    common = _db_user("common@example.com")

    with SessionLocal() as db:
        db.add_all([first, second, common])
        db.flush()
        first_id = str(first.id)
        second_id = str(second.id)
        common_id = str(common.id)
        db.add_all(
            [
                _db_favorite(first_id, "BTC/USDT", "First admin", tier=1),
                _db_favorite(second_id, "ETH/USDT", "Second admin", tier=1),
            ]
        )
        db.commit()

    service = OpportunityService()
    favorites = service.get_favorites(common_id, tier_filter="1")

    assert len(favorites) == 1
    assert favorites[0]["name"] == "Second admin"
    assert favorites[0]["symbol"] == "ETH/USDT"


def test_get_opportunities_marks_curated_fallback_payload(monkeypatch):
    monkeypatch.setenv("ADMIN_EMAILS", "admin@example.com")
    admin = _db_user("admin@example.com")
    common = _db_user("common@example.com")

    with SessionLocal() as db:
        db.add_all([admin, common])
        db.flush()
        admin_id = str(admin.id)
        common_id = str(common.id)
        db.add(_db_favorite(admin_id, "BTC/USDT", "Admin curated", tier=1))
        db.commit()

    service = OpportunityService()
    provider = _MockProvider(_sample_ohlcv())
    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: CCXT_SOURCE
    )
    monkeypatch.setattr(opportunity_service, "_is_unsupported_symbol", lambda *_args: False)
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_args: provider)
    monkeypatch.setattr(
        service.combo_service,
        "get_template_metadata",
        lambda template_name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.1,
        },
    )
    monkeypatch.setattr(opportunity_service, "ComboStrategy", _FakeComboStrategy)
    monkeypatch.setattr(
        service.analyzer,
        "analyze",
        lambda *args, **kwargs: {
            "status": "WAIT",
            "badge": "neutral",
            "message": "ok",
            "distance": 0.5,
        },
    )

    out = service.get_opportunities(common_id, tier_filter="1")

    assert len(out) == 1
    assert out[0]["is_curated_fallback"] is True


def test_get_opportunities_ignores_stock_favorites_for_crypto_only_mvp(monkeypatch):
    service = OpportunityService(db_path=":memory:")
    favorite = _sample_favorite("AAPL", "4h", data_source=STOOQ_SOURCE)
    service.get_favorites = lambda *_args, **_kwargs: [favorite]

    stooq_provider = _FailingProvider()

    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: STOOQ_SOURCE
    )
    monkeypatch.setattr(
        opportunity_service, "get_market_data_provider", lambda *_args: stooq_provider
    )

    out = service.get_opportunities("user")

    assert out == []
    assert stooq_provider.calls == 0


def test_get_opportunities_fetch_error_for_ccxt_is_skipped(monkeypatch):
    service = OpportunityService(db_path=":memory:")
    favorite = _sample_favorite("BTC/USDT", "15m", data_source=CCXT_SOURCE)
    service.get_favorites = lambda *_args, **_kwargs: [favorite]

    provider = _FailingProvider()
    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: CCXT_SOURCE
    )
    monkeypatch.setattr(opportunity_service, "_is_unsupported_symbol", lambda *_args: False)
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_args: provider)

    out = service.get_opportunities("user")
    assert out == []


def test_get_opportunities_parallel_fetch_timeout_keeps_fast_strategies(monkeypatch):
    service = OpportunityService(db_path=":memory:")
    fast_favorite = _sample_favorite("BTC/USDT", "1h", data_source=CCXT_SOURCE)
    slow_favorite = _sample_favorite("ETH/USDT", "1h", data_source=CCXT_SOURCE)
    fast_favorite["id"] = 1
    slow_favorite["id"] = 2
    service.get_favorites = lambda *_args, **_kwargs: [fast_favorite, slow_favorite]

    provider = _DelayAndReturnProvider(delay_seconds=0.5, delayed_symbol="ETH/USDT")

    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: CCXT_SOURCE
    )
    monkeypatch.setattr(opportunity_service, "_is_unsupported_symbol", lambda *_args: False)
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_args: provider)
    monkeypatch.setenv("OPPORTUNITIES_MARKET_FETCH_TIMEOUT_SECONDS", "0.05")
    monkeypatch.setattr(
        service.combo_service,
        "get_template_metadata",
        lambda template_name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.1,
        },
    )
    monkeypatch.setattr(opportunity_service, "ComboStrategy", _FakeComboStrategy)
    monkeypatch.setattr(
        service.analyzer,
        "analyze",
        lambda *args, **kwargs: {
            "status": "HOLD",
            "badge": "info",
            "message": "ok",
            "distance": 0.5,
        },
    )

    out = service.get_opportunities("user")
    assert len(out) == 1
    assert out[0]["id"] == 1


def test_get_opportunities_ccxt_applies_continuity_fix(monkeypatch):
    service = OpportunityService(db_path=":memory:")
    favorite = _sample_favorite("BTC/USDT", "1h", data_source=CCXT_SOURCE)
    service.get_favorites = lambda *_args, **_kwargs: [favorite]

    provider = _MockProvider(_sample_ohlcv())
    fixed = {"called": False}

    def _fake_fix(df, timeframe):
        fixed["called"] = True
        return df

    monkeypatch.setattr(
        opportunity_service, "resolve_data_source_for_symbol", lambda *_args: CCXT_SOURCE
    )
    monkeypatch.setattr(opportunity_service, "_is_unsupported_symbol", lambda *_args: False)
    monkeypatch.setattr(opportunity_service, "get_market_data_provider", lambda *_args: provider)
    monkeypatch.setattr(
        service.combo_service,
        "get_template_metadata",
        lambda template_name: {
            "indicators": [],
            "entry_logic": "close > open",
            "exit_logic": "close < open",
            "stop_loss": 0.1,
        },
    )
    monkeypatch.setattr(opportunity_service, "ComboStrategy", _FakeComboStrategy)
    monkeypatch.setattr(
        service.analyzer,
        "analyze",
        lambda *args, **kwargs: {
            "status": "HOLD",
            "badge": "info",
            "message": "ok",
            "distance": 0.5,
        },
    )
    monkeypatch.setattr(opportunity_service, "_apply_crypto_continuity_fix", _fake_fix)

    out = service.get_opportunities("user")
    assert len(out) == 1
    assert fixed["called"] is True
    assert out[0]["timeframe"] == "1h"


def test_filter_by_tier_all_keeps_null_tier_favorites():
    service = OpportunityService(db_path=":memory:")
    favorites = [
        {
            "id": 1,
            "name": "A",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "strategy_name": "s1",
            "parameters": {},
            "tier": 1,
        },
        {
            "id": 2,
            "name": "B",
            "symbol": "ETH/USDT",
            "timeframe": "1d",
            "strategy_name": "s2",
            "parameters": {},
            "tier": None,
        },
    ]

    assert service._filter_by_tier(favorites, None) == favorites
    assert service._filter_by_tier(favorites, "all") == favorites


def test_filter_by_tier_none_returns_only_null_tier_favorites():
    service = OpportunityService(db_path=":memory:")
    favorites = [
        {
            "id": 1,
            "name": "A",
            "symbol": "BTC/USDT",
            "timeframe": "1d",
            "strategy_name": "s1",
            "parameters": {},
            "tier": 1,
        },
        {
            "id": 2,
            "name": "B",
            "symbol": "ETH/USDT",
            "timeframe": "1d",
            "strategy_name": "s2",
            "parameters": {},
            "tier": None,
        },
    ]

    filtered = service._filter_by_tier(favorites, "none")
    assert len(filtered) == 1
    assert filtered[0]["id"] == 2
