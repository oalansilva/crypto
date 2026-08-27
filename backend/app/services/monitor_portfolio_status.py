from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models import MonitorPreference
from app.services.asset_classification import classify_asset_type
from app.services.binance_spot import BinanceConfigError, fetch_spot_balances_snapshot
from app.services.user_exchange_credentials import BINANCE_PROVIDER, get_user_exchange_credential


@dataclass(frozen=True)
class SymbolPortfolioStatus:
    in_portfolio: bool
    has_spot_position: bool
    derived_active: bool
    sync_failed: bool = False


def _base_asset(symbol: str) -> str:
    return str(symbol or "").split("/")[0].strip().upper()


def _wallet_holdings_by_asset(snapshot: dict[str, Any]) -> dict[str, float]:
    holdings: dict[str, float] = {}
    for row in snapshot.get("balances") or []:
        asset = str(row.get("asset") or "").strip().upper()
        if not asset:
            continue
        try:
            total = float(row.get("total") or 0)
        except (TypeError, ValueError):
            total = 0.0
        if total > 0:
            holdings[asset] = holdings.get(asset, 0.0) + total
    return holdings


def fetch_user_wallet_holdings(
    db: Session,
    user_id: str,
    *,
    min_usd: float = 1.0,
) -> tuple[dict[str, float], bool]:
    cred = get_user_exchange_credential(db, user_id, BINANCE_PROVIDER)
    if cred is None:
        return {}, True
    try:
        snapshot = fetch_spot_balances_snapshot(
            api_key=cred.api_key,
            api_secret=cred.api_secret,
            min_usd=min_usd,
        )
    except (BinanceConfigError, OSError, RuntimeError, ValueError, TypeError):
        return {}, False
    return _wallet_holdings_by_asset(snapshot), True


def resolve_portfolio_status_for_user(
    db: Session,
    user_id: str,
    symbols: list[str],
    *,
    wallet_holdings: dict[str, float] | None = None,
    binance_sync_ok: bool | None = None,
) -> dict[str, SymbolPortfolioStatus]:
    prefs = {
        row.symbol: row
        for row in db.query(MonitorPreference)
        .filter(MonitorPreference.user_id == user_id)
        .all()
    }
    binance_configured = get_user_exchange_credential(db, user_id, BINANCE_PROVIDER) is not None
    holdings = wallet_holdings
    sync_ok = binance_sync_ok
    if binance_configured and (holdings is None or sync_ok is None):
        fetched, fetched_ok = fetch_user_wallet_holdings(db, user_id, min_usd=1.0)
        if holdings is None:
            holdings = fetched
        if sync_ok is None:
            sync_ok = fetched_ok
    holdings = holdings or {}
    sync_ok = True if sync_ok is None else sync_ok

    result: dict[str, SymbolPortfolioStatus] = {}
    for raw_symbol in symbols:
        symbol = str(raw_symbol or "").strip().upper()
        if not symbol or symbol in result:
            continue
        manual = bool(getattr(prefs.get(symbol), "in_portfolio", False))
        derived_active = classify_asset_type(symbol) == "crypto" and binance_configured
        if not derived_active:
            result[symbol] = SymbolPortfolioStatus(
                in_portfolio=manual,
                has_spot_position=False,
                derived_active=False,
            )
            continue
        if not sync_ok:
            result[symbol] = SymbolPortfolioStatus(
                in_portfolio=False,
                has_spot_position=False,
                derived_active=True,
                sync_failed=True,
            )
            continue
        base = _base_asset(symbol)
        has_position = (holdings.get(base) or 0.0) > 0
        result[symbol] = SymbolPortfolioStatus(
            in_portfolio=has_position,
            has_spot_position=has_position,
            derived_active=True,
        )
    return result
