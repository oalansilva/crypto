from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.schemas.signal import (
    BollingerBandsPayload,
    ConfidenceBreakdown,
    RiskProfile,
    Signal,
    SignalIndicators,
    SignalType,
)
from app.services import signal_history_writer as writer
from app.services.signal_history_writer import HistoryQualityGateSettings


def _make_signal(
    *,
    signal_type: SignalType = SignalType.BUY,
    signal_id: str = "sig-1",
    confidence: int = 80,
    rsi: float = 32.0,
    macd: str = "bullish",
    risk_profile: RiskProfile = RiskProfile.moderate,
    entry_price: float | None = 100.0,
    target_price: float = 112.0,
    stop_loss: float = 90.0,
    created_at: datetime | None = None,
) -> Signal:
    return Signal(
        id=signal_id,
        type=signal_type,
        asset="BTCUSDT",
        confidence=confidence,
        target_price=target_price,
        stop_loss=stop_loss,
        entry_price=entry_price,
        current_price=100.0,
        indicators=SignalIndicators(
            rsi=rsi,
            macd=macd,
            bollinger_bands=BollingerBandsPayload(upper=120.0, middle=100.0, lower=80.0),
        ),
        breakdown=ConfidenceBreakdown(
            rsi_contribution=40.0,
            macd_contribution=20.0,
            sentiment_contribution=20.0,
            display_total=80.0,
        ),
        risk_profile=risk_profile,
        created_at=created_at or datetime(2026, 7, 17, tzinfo=timezone.utc),
    )


def _settings(**overrides) -> HistoryQualityGateSettings:
    base = dict(
        min_confidence=55,
        min_reward_risk=1.2,
        max_reward_risk=5.0,
        min_rsi=30.0,
        max_rsi=34.0,
        allow_neutral_macd=True,
        allow_buy=True,
        allow_sell=True,
        allow_conservative=True,
        allow_moderate=True,
        allow_aggressive=True,
    )
    base.update(overrides)
    return HistoryQualityGateSettings(**base)


class _FakeQuery:
    def __init__(self, result=None):
        self._result = result

    def filter(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def first(self):
        return self._result


class _FakeSession:
    def __init__(self, results=None):
        self._results = list(results or [None])
        self.added = []
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def query(self, *_args, **_kwargs):
        result = self._results.pop(0) if self._results else None
        return _FakeQuery(result)

    def add(self, record):
        self.added.append(record)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_save_signal_to_history_skips_existing(monkeypatch) -> None:
    session = _FakeSession(results=[SimpleNamespace(id="sig-1")])
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: True)

    writer.save_signal_to_history(_make_signal(), user_id="user-1")

    assert session.added == []
    assert session.committed is False
    assert session.closed is True


def test_save_signal_to_history_persists_buy_when_gate_passes(monkeypatch) -> None:
    session = _FakeSession(results=[None])
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: True)

    original_signal_history = writer.SignalHistory

    class _RecordingSignalHistory:
        id = original_signal_history.id
        user_id = original_signal_history.user_id
        archived = original_signal_history.archived
        asset = original_signal_history.asset
        risk_profile = original_signal_history.risk_profile
        type = original_signal_history.type
        status = original_signal_history.status
        created_at = original_signal_history.created_at

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    monkeypatch.setattr(writer, "SignalHistory", _RecordingSignalHistory)

    writer.save_signal_to_history(_make_signal(signal_id="sig-buy"), user_id="user-1")

    assert len(session.added) == 1
    saved = session.added[0].__dict__
    assert saved["id"] == "sig-buy"
    assert saved["type"] == "BUY"
    assert session.committed is True
    assert session.closed is True


def test_save_signal_to_history_skips_when_quality_gate_fails(monkeypatch) -> None:
    session = _FakeSession(results=[None])
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: False)

    writer.save_signal_to_history(_make_signal(), user_id="user-1")

    assert session.added == []
    assert session.committed is False
    assert session.closed is True


def test_save_signal_to_history_closes_open_buy_on_sell(monkeypatch) -> None:
    open_buy = SimpleNamespace(
        entry_price=100.0,
        status="ativo",
        exit_price=None,
        pnl=None,
        updated_at=None,
    )
    session = _FakeSession(results=[None, open_buy])
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(writer, "sao_paulo_now", lambda: datetime(2026, 7, 17, tzinfo=timezone.utc))

    writer.save_signal_to_history(
        _make_signal(signal_type=SignalType.SELL, target_price=90.0, stop_loss=110.0),
        user_id="user-1",
    )

    assert open_buy.status == "disparado"
    assert open_buy.exit_price == 100.0
    assert open_buy.pnl == 0.0
    assert session.committed is True
    assert session.closed is True


def test_save_signal_to_history_sell_without_user_is_noop(monkeypatch) -> None:
    session = _FakeSession(results=[None])
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: True)

    writer.save_signal_to_history(_make_signal(signal_type=SignalType.SELL), user_id=None)

    assert session.committed is False
    assert session.closed is True


def test_save_signal_to_history_sell_without_open_buy_is_noop(monkeypatch) -> None:
    session = _FakeSession(results=[None, None])
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: True)

    writer.save_signal_to_history(_make_signal(signal_type=SignalType.SELL), user_id="user-1")

    assert session.committed is False
    assert session.closed is True


def test_save_signal_to_history_rolls_back_on_error(monkeypatch) -> None:
    class _BoomSession(_FakeSession):
        def query(self, *_args, **_kwargs):
            raise RuntimeError("db down")

    session = _BoomSession()
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)

    writer.save_signal_to_history(_make_signal(), user_id="user-1")

    assert session.rolled_back is True
    assert session.closed is True


@pytest.mark.parametrize(
    ("signal_type", "entry", "target", "stop", "expected"),
    [
        (SignalType.BUY, 100.0, 112.0, 90.0, 1.2),
        (SignalType.SELL, 100.0, 88.0, 110.0, 1.2),
        (SignalType.HOLD, 100.0, 112.0, 90.0, None),
        (SignalType.BUY, None, 112.0, 90.0, None),
        (SignalType.BUY, 0.0, 112.0, 90.0, None),
        (SignalType.BUY, 100.0, 90.0, 90.0, None),
    ],
)
def test_calculate_reward_risk(signal_type, entry, target, stop, expected) -> None:
    signal = _make_signal(
        signal_type=signal_type,
        entry_price=entry,
        target_price=target,
        stop_loss=stop,
    )
    assert writer._calculate_reward_risk(signal) == expected


def test_convert_utc_to_sao_paulo_handles_naive_and_none() -> None:
    assert writer._convert_utc_to_sao_paulo(None) is None
    naive = datetime(2026, 7, 17, 12, 0, 0)
    converted = writer._convert_utc_to_sao_paulo(naive)
    assert converted is not None
    assert converted.tzinfo is not None


def test_get_history_quality_gate_settings_uses_preferences(monkeypatch) -> None:
    monkeypatch.setattr(writer, "get_system_preference_int", lambda *_a, **_k: 60)
    monkeypatch.setattr(writer, "get_system_preference_float", lambda *_a, **_k: 2.0)
    monkeypatch.setattr(writer, "get_system_preference_bool", lambda *_a, **_k: True)

    settings = writer._get_history_quality_gate_settings(db=SimpleNamespace())

    assert settings.min_confidence == 60
    assert settings.min_reward_risk == 2.0
    assert settings.allow_buy is True


def test_passes_history_quality_gate_uses_settings(monkeypatch) -> None:
    monkeypatch.setattr(
        writer,
        "_get_history_quality_gate_settings",
        lambda _db: _settings(min_reward_risk=1.0),
    )
    assert writer._passes_history_quality_gate(_make_signal(), db=SimpleNamespace()) is True


@pytest.mark.parametrize(
    ("signal_kwargs", "settings_kwargs", "expected"),
    [
        ({"signal_type": SignalType.HOLD}, {}, False),
        ({"signal_type": SignalType.BUY}, {"allow_buy": False}, False),
        ({"signal_type": SignalType.SELL}, {"allow_sell": False}, False),
        ({"risk_profile": RiskProfile.conservative}, {"allow_conservative": False}, False),
        ({"risk_profile": RiskProfile.moderate}, {"allow_moderate": False}, False),
        ({"risk_profile": RiskProfile.aggressive}, {"allow_aggressive": False}, False),
        ({"confidence": 40}, {}, False),
        ({"macd": "neutral"}, {"allow_neutral_macd": False}, False),
        ({"rsi": 20.0}, {}, False),
        ({"entry_price": None}, {}, False),
        ({"target_price": 112.0, "stop_loss": 90.0}, {"min_reward_risk": 1.2}, True),
    ],
)
def test_signal_passes_quality_gate(signal_kwargs, settings_kwargs, expected) -> None:
    signal = _make_signal(**signal_kwargs)
    assert writer._signal_passes_quality_gate(signal, _settings(**settings_kwargs)) is expected
