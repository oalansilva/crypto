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


def _make_signal(*, signal_type: SignalType = SignalType.BUY, signal_id: str = "sig-1") -> Signal:
    return Signal(
        id=signal_id,
        type=signal_type,
        asset="BTCUSDT",
        confidence=80,
        target_price=110.0,
        stop_loss=90.0,
        entry_price=100.0,
        current_price=100.0,
        indicators=SignalIndicators(
            rsi=32.0,
            macd="bullish",
            bollinger_bands=BollingerBandsPayload(upper=120.0, middle=100.0, lower=80.0),
        ),
        breakdown=ConfidenceBreakdown(
            rsi_contribution=40.0,
            macd_contribution=20.0,
            sentiment_contribution=20.0,
            display_total=80.0,
        ),
        risk_profile=RiskProfile.moderate,
        created_at=datetime(2026, 7, 17, tzinfo=timezone.utc),
    )


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
    def __init__(self, existing=None):
        self.existing = existing
        self.added = []
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def query(self, *_args, **_kwargs):
        return _FakeQuery(self.existing)

    def add(self, record):
        self.added.append(record)

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_save_signal_to_history_skips_existing(monkeypatch) -> None:
    session = _FakeSession(existing=SimpleNamespace(id="sig-1"))
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: True)

    writer.save_signal_to_history(_make_signal(), user_id="user-1")

    assert session.added == []
    assert session.committed is False
    assert session.closed is True


def test_save_signal_to_history_persists_buy_when_gate_passes(monkeypatch) -> None:
    session = _FakeSession(existing=None)
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
    assert session.added[0].id == "sig-buy"
    assert session.added[0].type == "BUY"
    assert session.committed is True
    assert session.closed is True


def test_save_signal_to_history_skips_when_quality_gate_fails(monkeypatch) -> None:
    session = _FakeSession(existing=None)
    monkeypatch.setattr(writer, "SessionLocal", lambda: session)
    monkeypatch.setattr(writer, "_passes_history_quality_gate", lambda *_args, **_kwargs: False)

    writer.save_signal_to_history(_make_signal(), user_id="user-1")

    assert session.added == []
    assert session.committed is False
    assert session.closed is True


@pytest.mark.parametrize(
    ("signal_type", "entry", "target", "stop", "expected"),
    [
        (SignalType.BUY, 100.0, 110.0, 90.0, 1.0),
        (SignalType.SELL, 100.0, 90.0, 110.0, 1.0),
        (SignalType.HOLD, 100.0, 110.0, 90.0, None),
    ],
)
def test_calculate_reward_risk(signal_type, entry, target, stop, expected) -> None:
    signal = _make_signal(signal_type=signal_type)
    signal = signal.model_copy(
        update={"entry_price": entry, "target_price": target, "stop_loss": stop}
    )
    assert writer._calculate_reward_risk(signal) == expected
