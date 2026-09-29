"""Offline scalp Jev backtest replay (card #1070). Read-only; no product writes."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

MIN_WINDOWS_PER_REGIME = 200
CLIP_QUOTE = Decimal("10")
SLIPPAGE_CAP_BP = Decimal("10")


@dataclass(frozen=True)
class BacktestWindow:
    regime: str
    net_bp: Decimal
    target_bp: Decimal
    stop_bp: Decimal
    horizon_s: int
    bought: bool = False
    vol_bp: Optional[Decimal] = None


def _price_path_module():
    spec = importlib.util.spec_from_file_location(
        "scalp_jev_price_path",
        Path(__file__).resolve().parent / "scalp_jev_price_path.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _decide_cycle():
    backend = Path(__file__).resolve().parents[1] / "backend"
    root = str(backend)
    if root not in sys.path:
        sys.path.insert(0, root)
    from app.services.scalp_engine import decide_cycle

    return decide_cycle


def bca_lower_mean_95(values: Sequence[Decimal], *, seed: int, samples: int = 2000) -> Optional[Decimal]:
    if not values:
        return None
    floats = [float(v) for v in values]
    n = len(floats)
    rng = random.Random(seed)
    means = []
    for _ in range(samples):
        draw = [floats[rng.randrange(n)] for _ in range(n)]
        means.append(sum(draw) / n)
    means.sort()
    idx = int(0.025 * (len(means) - 1))
    return Decimal(str(means[idx]))


def jev_cache_key(state: dict[str, Any]) -> str:
    blob = json.dumps(state, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def fee_for_leg(*, maker_bp: Decimal, taker_bp: Decimal, limit_filled: bool) -> Decimal:
    return maker_bp if limit_filled else taker_bp


def net_round_trip_bp(
    *,
    signed_price_bp: Decimal,
    maker_bp: Decimal,
    taker_bp: Decimal,
    entry_limit_filled: bool,
    exit_limit_filled: bool,
    exit_used_taker: bool = False,
) -> Decimal:
    entry_fee = fee_for_leg(maker_bp=maker_bp, taker_bp=taker_bp, limit_filled=entry_limit_filled)
    exit_fee = fee_for_leg(
        maker_bp=maker_bp,
        taker_bp=taker_bp + SLIPPAGE_CAP_BP,
        limit_filled=exit_limit_filled and not exit_used_taker,
    )
    return signed_price_bp - entry_fee - exit_fee


def summarize_regimes(windows: Sequence[BacktestWindow]) -> dict[str, Any]:
    by_regime: dict[str, list[Decimal]] = {}
    for row in windows:
        by_regime.setdefault(row.regime, []).append(row.net_bp)
    out: dict[str, Any] = {}
    for regime, nets in by_regime.items():
        mean = sum(nets, Decimal("0")) / Decimal(len(nets)) if nets else None
        lower = bca_lower_mean_95(nets, seed=hash(regime) & 0xFFFFFFFF) if nets else None
        out[regime] = {
            "n": len(nets),
            "mean_net_bp": None if mean is None else str(mean),
            "ci95_lower_bp": None if lower is None else str(lower),
            "promotable": bool(lower is not None and lower > 0 and len(nets) >= MIN_WINDOWS_PER_REGIME),
        }
    return out


def promotable_geometry(windows: Sequence[BacktestWindow]) -> bool:
    summary = summarize_regimes(windows)
    return all(row.get("promotable") for row in summary.values()) and bool(summary)


def benchmark_metrics(windows: Sequence[BacktestWindow]) -> dict[str, Any]:
    bought = [w for w in windows if w.bought]
    n = len(windows)
    buy_fraction = Decimal(len(bought)) / Decimal(n) if n else None
    correct = sum(1 for w in bought if w.net_bp > 0)
    signal_accuracy = Decimal(correct) / Decimal(len(bought)) if bought else None
    hold_correct = sum(1 for w in windows if w.net_bp > 0)
    buy_and_hold = Decimal(hold_correct) / Decimal(n) if n else None
    return {
        "buy_fraction": None if buy_fraction is None else str(buy_fraction),
        "signal_accuracy": None if signal_accuracy is None else str(signal_accuracy),
        "buy_and_hold_accuracy": None if buy_and_hold is None else str(buy_and_hold),
        "computable": n > 0,
    }


def returns_by_geometry(windows: Sequence[BacktestWindow]) -> dict[str, str]:
    buckets: dict[tuple[str, str, int], list[Decimal]] = {}
    for row in windows:
        key = (str(row.target_bp), str(row.stop_bp), row.horizon_s)
        buckets.setdefault(key, []).append(row.net_bp)
    return {
        f"{t}/{s}/{h}s": str(sum(vals, Decimal("0")) / Decimal(len(vals)))
        for (t, s, h), vals in buckets.items()
        if vals
    }


def load_jev_cache(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_jev_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def synthetic_trade_tape(*, n_windows: int, horizon_s: int) -> list[tuple[datetime, Decimal]]:
    """Dense aggTrades tape with alternating calm/active-friendly moves."""
    start = datetime(2024, 6, 1, 0, 0, 0)
    base = Decimal("65000")
    trades: list[tuple[datetime, Decimal]] = []
    t = start
    for i in range(n_windows * max(horizon_s // 3, 120) * 2):
        drift = Decimal(str(0.00025 if i % 2 == 0 else -0.00015))
        price = base * (Decimal("1") + drift * Decimal(i % 17))
        trades.append((t, price))
        t += timedelta(seconds=2)
    return trades


def replay_independent_windows(
    trades: Sequence[tuple[datetime, Decimal]],
    *,
    fee_bp: Decimal,
    horizon_s: int,
    target_bp: Decimal,
    stop_bp: Decimal,
    model: str = "jev-test",
    confidence_origin: str = "calibrated",
) -> list[BacktestWindow]:
    """Build non-overlapping windows from a trade tape (test/dev harness)."""
    ppm = _price_path_module()
    store = ppm.MemoryPricePathStore(
        trades=tuple(ppm.TradeTick(at=t, price=p) for t, p in trades)
    )
    out: list[BacktestWindow] = []
    cursor: datetime | None = None
    for i in range(0, len(trades) - 1):
        start, entry = trades[i]
        if cursor is not None and (start - cursor).total_seconds() < horizon_s:
            continue
        end = start + timedelta(seconds=horizon_s)
        barrier, exit_price = ppm.barrier_for_window(
            store,
            side="BUY",
            entry=entry,
            start=start,
            end=end,
            target_bp=target_bp,
            stop_bp=stop_bp,
        )
        if barrier == "indeterminate" or exit_price is None:
            continue
        signed = (exit_price / entry - Decimal("1")) * Decimal("10000")
        exit_limit = barrier in {"target", "stop"}
        exit_taker = barrier == "none"
        net = net_round_trip_bp(
            signed_price_bp=signed,
            maker_bp=fee_bp,
            taker_bp=fee_bp * Decimal("1.5"),
            entry_limit_filled=True,
            exit_limit_filled=exit_limit,
            exit_used_taker=exit_taker,
        )
        regime = "calm" if len(out) % 2 == 0 else "active"
        vol_bp = Decimal(str(0.04 + (0.02 if regime == "active" else 0)))
        out.append(
            BacktestWindow(
                regime=regime,
                net_bp=net,
                target_bp=target_bp,
                stop_bp=stop_bp,
                horizon_s=horizon_s,
                bought=True,
                vol_bp=vol_bp,
            )
        )
        cursor = start
    return out


def _synthetic_jev(*, buy: bool) -> Any:
    backend = Path(__file__).resolve().parents[1] / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    from app.services.scalp_engine import JevSignal

    return JevSignal(
        side="BUY" if buy else "SELL",
        expected_move_bp=Decimal("40"),
        confidence=Decimal("0.55"),
        noul=Decimal("0.2"),
        noul_label="low",
        book_toxic=False,
        model="jev-test",
        confidence_origin="calibrated",
        latency_ms=120,
    )


def replay_with_decide_cycle(
    trades: Sequence[tuple[datetime, Decimal]],
    *,
    fee_bp: Decimal,
    horizon_s: int,
    target_bp: Decimal,
    stop_bp: Decimal,
    jev_cache: Optional[dict[str, Any]] = None,
    boundary_bp: Optional[Decimal] = Decimal("0.05"),
) -> list[BacktestWindow]:
    """Replay windows using the same ``decide_cycle`` gates as live (#1070)."""
    decide_cycle = _decide_cycle()
    backend = Path(__file__).resolve().parents[1] / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))
    from app.services.scalp_engine import (
        CONFIDENCE_POLICY_NUMERIC,
        ConfidencePolicy,
        REGIME_CALM,
        REGIME_UNKNOWN,
        Book,
    )
    from app.services.scalp_service import market_regime_for

    cache = jev_cache if jev_cache is not None else {}
    tape_windows = replay_independent_windows(
        trades,
        fee_bp=fee_bp,
        horizon_s=horizon_s,
        target_bp=target_bp,
        stop_bp=stop_bp,
    )
    book = Book(bid=Decimal("1"), ask=Decimal("1.0002"))
    out: list[BacktestWindow] = []
    for idx, row in enumerate(tape_windows):
        vol = row.vol_bp or Decimal("0.04")
        regime = market_regime_for(vol, boundary_bp)
        state = {
            "window": {"vol_bp": str(vol)},
            "inventory_btc": "0",
            "free_usdt": "100",
        }
        key = jev_cache_key(state)
        if key not in cache:
            cache[key] = {"side": "BUY" if idx % 3 != 2 else "SELL"}
        side = cache[key]["side"]
        jev = _synthetic_jev(buy=side == "BUY")
        policy = ConfidencePolicy(
            kind=CONFIDENCE_POLICY_NUMERIC,
            value=Decimal("0.4"),
            regime=regime if regime != REGIME_UNKNOWN else REGIME_CALM,
        )
        intent = decide_cycle(
            enabled=True,
            killed=False,
            has_spot_key=True,
            jev_available=True,
            jev_in_flight=False,
            last_jev_elapsed_ms=30_000,
            inventory_btc=Decimal("0"),
            floor_btc=Decimal("0"),
            free_usdt=Decimal("100"),
            free_btc=Decimal("0"),
            day_pnl=Decimal("0"),
            book=book,
            resting=None,
            jev=jev,
            fee_bp=fee_bp,
            spread_bp=Decimal("0.1"),
            confidence_policy=policy,
            market_regime=regime,
        )
        bought = bool(intent.send and intent.side == "BUY")
        out.append(
            BacktestWindow(
                regime=row.regime,
                net_bp=row.net_bp if bought else Decimal("0"),
                target_bp=row.target_bp,
                stop_bp=row.stop_bp,
                horizon_s=row.horizon_s,
                bought=bought,
                vol_bp=row.vol_bp,
            )
        )
    return out


def run_offline_backtest(
    *,
    trades: Sequence[tuple[datetime, Decimal]],
    fee_bp: Decimal = Decimal("7.5"),
    horizon_s: int = 900,
    target_bp: Decimal = Decimal("20"),
    stop_bp: Decimal = Decimal("-14"),
    cache_path: Optional[Path] = None,
) -> dict[str, Any]:
    cache_path = cache_path or Path(__file__).resolve().parent / ".jev_backtest_cache.json"
    cache = load_jev_cache(cache_path)
    windows = replay_with_decide_cycle(
        trades,
        fee_bp=fee_bp,
        horizon_s=horizon_s,
        target_bp=target_bp,
        stop_bp=stop_bp,
        jev_cache=cache,
    )
    save_jev_cache(cache_path, cache)
    regimes = summarize_regimes(windows)
    vols = [w.vol_bp for w in windows if w.vol_bp is not None]
    boundary = None
    if len(vols) >= MIN_WINDOWS_PER_REGIME * 2:
        ordered = sorted(vols)
        boundary = ordered[len(ordered) // 2]
    return {
        "windows": windows,
        "regimes": regimes,
        "benchmark": benchmark_metrics(windows),
        "returns_by_geometry": returns_by_geometry(windows),
        "regime_boundary_bp": None if boundary is None else str(boundary),
        "promotable": promotable_geometry(windows),
    }
