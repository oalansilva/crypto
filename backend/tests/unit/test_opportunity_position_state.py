import pandas as pd

from app.services.opportunity_service import _resolve_position_state, _signal_execution_price


def test_resolve_position_state_marks_stopped_out_when_exit_happened_after_buy():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=True,
        last_buy_pos=10,
        last_sell_pos=14,
        last_sell_reason="stop_loss",
        direction="long",
        last_price=2078.75,
        stop_price=2049.78,
    )

    assert is_holding is False
    assert is_stopped_out is True
    assert stop_breached_now is False


def test_resolve_position_state_marks_stopped_out_when_price_is_below_stop():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=True,
        last_buy_pos=10,
        last_sell_pos=None,
        last_sell_reason=None,
        direction="long",
        last_price=2000.0,
        stop_price=2049.78,
    )

    assert is_holding is False
    assert is_stopped_out is True
    assert stop_breached_now is True


def test_resolve_position_state_keeps_holding_when_no_exit_or_stop():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=True,
        last_buy_pos=10,
        last_sell_pos=8,
        last_sell_reason="exit_logic",
        direction="long",
        last_price=2078.75,
        stop_price=2049.78,
    )

    assert is_holding is True
    assert is_stopped_out is False
    assert stop_breached_now is False


def test_signal_execution_price_uses_signal_candle_open():
    df = pd.DataFrame(
        [
            {"open": 70556.74, "close": 71336.53},
            {"open": 71336.53, "close": 68820.31},
        ],
        index=pd.to_datetime(["2026-03-25T00:00:00Z", "2026-03-26T00:00:00Z"], utc=True),
    )

    entry_price = _signal_execution_price(df, df.index[0], direction="entry")

    assert entry_price == 70556.74


def test_resolve_position_state_treats_exit_logic_as_normal_exit_not_stop():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=True,
        last_buy_pos=10,
        last_sell_pos=14,
        last_sell_reason="exit_logic",
        direction="long",
        last_price=2078.75,
        stop_price=2049.78,
    )

    assert is_holding is False
    assert is_stopped_out is False
    assert stop_breached_now is False
