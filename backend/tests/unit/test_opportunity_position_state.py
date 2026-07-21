import pandas as pd

from app.services.opportunity_service import (
    _build_signal_history,
    _last_signal_index_and_position,
    _public_monitor_message,
    _public_monitor_status,
    _resolve_position_state,
    _signal_execution_price,
)


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


def test_resolve_position_state_keeps_holding_when_active_entry_has_no_later_exit_or_stop():
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


def test_resolve_position_state_does_not_hold_without_confirmed_entry():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=True,
        last_buy_pos=None,
        last_sell_pos=None,
        last_sell_reason=None,
        direction="long",
        last_price=0.74,
        stop_price=None,
    )

    assert is_holding is False
    assert is_stopped_out is False
    assert stop_breached_now is False


def test_resolve_position_state_uses_confirmed_signals_without_ma_specific_gate():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=False,
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


def test_resolve_position_state_keeps_short_holding_without_long_trend_gate():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=False,
        last_buy_pos=10,
        last_sell_pos=8,
        last_sell_reason="exit_logic",
        direction="short",
        last_price=95.0,
        stop_price=105.0,
    )

    assert is_holding is True
    assert is_stopped_out is False
    assert stop_breached_now is False


def test_resolve_position_state_marks_short_stopped_out_above_stop():
    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=False,
        last_buy_pos=10,
        last_sell_pos=None,
        last_sell_reason=None,
        direction="short",
        last_price=106.0,
        stop_price=105.0,
    )

    assert is_holding is False
    assert is_stopped_out is True
    assert stop_breached_now is True


def test_public_monitor_message_does_not_leak_long_hold_copy_for_short():
    message = _public_monitor_message(
        "HOLD",
        {"message": "Compra ativa. Acompanhe a proxima venda."},
        direction="short",
    )

    assert "Compra ativa" not in message
    assert message.startswith("Venda ativa")


def test_public_monitor_status_keeps_hold_when_exit_near_while_holding():
    assert _public_monitor_status(is_holding=True, raw_status="EXIT_NEAR") == "HOLD"
    assert _public_monitor_status(is_holding=True, raw_status="HOLDING") == "HOLD"
    assert _public_monitor_status(is_holding=False, raw_status="EXIT_NEAR") == "HOLD"
    assert _public_monitor_status(is_holding=True, raw_status="EXIT_SIGNAL") == "EXIT"
    assert _public_monitor_status(is_holding=False, raw_status="EXITED") == "EXIT"


def test_public_monitor_message_for_exit_near_hold_avoids_closed_position_copy():
    message = _public_monitor_message(
        "HOLD",
        {"status": "EXIT_NEAR", "distance": 0.51, "message": "EXIT: approaching crossunder"},
        direction="long",
    )

    assert "fora de posicao" not in message.lower()
    assert message.startswith("Compra ativa")
    assert "0.51%" in message


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


def test_signal_positions_use_generated_signal_frame_for_next_candle_exit():
    df_signals = pd.DataFrame(
        [
            {"open": 0.09081, "close": 0.09093, "signal": 1, "signal_reason": "entry"},
            {"open": 0.08774, "close": 0.09068, "signal": -1, "signal_reason": "exit_logic"},
        ],
        index=pd.to_datetime(["2026-04-24T00:00:00Z", "2026-05-05T00:00:00Z"], utc=True),
    )

    last_buy_idx, last_buy_pos = _last_signal_index_and_position(df_signals, 1)
    last_sell_idx, last_sell_pos = _last_signal_index_and_position(df_signals, -1)

    assert str(last_buy_idx) == "2026-04-24 00:00:00+00:00"
    assert str(last_sell_idx) == "2026-05-05 00:00:00+00:00"
    assert last_buy_pos == 0
    assert last_sell_pos == 1

    is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
        short_above_long=True,
        last_buy_pos=last_buy_pos,
        last_sell_pos=last_sell_pos,
        last_sell_reason="exit_logic",
        direction="long",
        last_price=0.09068,
        stop_price=0.08627,
    )
    signal_history = _build_signal_history(df_signals, df_signals)

    assert is_holding is False
    assert is_stopped_out is False
    assert stop_breached_now is False
    assert signal_history[-1]["type"] == "exit"
    assert signal_history[-1]["price"] == 0.08774
