"""Recusa estruturada de ativos nas análises (card #1117, decisão 14).

``refusal_for_symbols`` devolve ``None`` quando todos os símbolos podem rodar, ou
o ``detail`` de um HTTP 422 com ``code``, classe/estado, ativos e mensagem em
português. Mensagens dizem "fora" e o motivo, no mesmo tom da interface.
"""

from __future__ import annotations

import logging
from typing import Any, Iterable

from sqlalchemy.exc import SQLAlchemyError

from app.services.asset_catalog_adapters import CLASS_CRYPTO, CLASS_ETF, CLASS_STOCK
from app.services.asset_catalog_service import (
    DISCOVERY_EQUITY_REASON,
    EQUITY_UNSUPPORTED_MESSAGE,
    STATE_LABELS,
    AssetCheck,
    check_assets,
)

logger = logging.getLogger(__name__)

CODE_CLASS_NOT_SUPPORTED = "asset_class_not_supported"
CODE_NOT_SELECTABLE = "asset_not_selectable"
CODE_NOT_IN_CATALOG = "asset_not_in_catalog"

CLASS_LABEL = {CLASS_CRYPTO: "Cripto", CLASS_STOCK: "Ação", CLASS_ETF: "ETF"}


def _dedupe(symbols: Iterable[str]) -> list[str]:
    return list(
        dict.fromkeys(str(s or "").strip().upper() for s in symbols if str(s or "").strip())
    )


def _class_refusal(checks: list[AssetCheck]) -> dict[str, Any]:
    classes = sorted({c.asset_class or "stock_etf" for c in checks})
    names = ", ".join(
        f"{c.symbol} ({CLASS_LABEL.get(c.asset_class or '', 'Ação ou ETF')})" for c in checks[:5]
    )
    rest = len(checks) - 5
    if rest > 0:
        names += f" e mais {rest}"
    return {
        "code": CODE_CLASS_NOT_SUPPORTED,
        "asset_class": classes[0],
        "asset_classes": classes,
        "assets": [
            {
                "symbol": c.symbol,
                "asset_id": c.asset_id,
                "asset_class": c.asset_class or "stock_etf",
            }
            for c in checks
        ],
        "message": f"{EQUITY_UNSUPPORTED_MESSAGE} Fora da análise: {names}.",
    }


def _marked_refusal(checks: list[AssetCheck]) -> dict[str, Any]:
    first = checks[0]
    parts = []
    for check in checks[:5]:
        label = STATE_LABELS.get(check.state or "", check.state or "")
        reason = (check.state_reason or "").strip()
        parts.append(f"{check.symbol} ({label}{': ' + reason.rstrip('.') if reason else ''})")
    rest = len(checks) - 5
    names = "; ".join(parts) + (f"; e mais {rest}" if rest > 0 else "")
    return {
        "code": CODE_NOT_SELECTABLE,
        "state": first.state,
        "reason": first.state_reason,
        "assets": [
            {
                "symbol": c.symbol,
                "asset_id": c.asset_id,
                "asset_class": c.asset_class,
                "state": c.state,
                "state_label": STATE_LABELS.get(c.state or "", c.state),
                "reason": c.state_reason,
            }
            for c in checks
        ],
        "message": (
            "Ativo marcado pela Binance não entra em análise nova (suspenso, fora de mercado, "
            f"sem negociação, sem regras ou removido). Fora da análise: {names}."
        ),
    }


def _missing_refusal(checks: list[AssetCheck]) -> dict[str, Any]:
    names = ", ".join(c.symbol for c in checks[:5]) + (
        f" e mais {len(checks) - 5}" if len(checks) > 5 else ""
    )
    return {
        "code": CODE_NOT_IN_CATALOG,
        "assets": [{"symbol": c.symbol} for c in checks],
        "message": f"Não está no catálogo da Binance: {names}.",
    }


def refusal_for_symbols(
    symbols: Iterable[str],
    *,
    new_analysis: bool,
    single_scope: bool = False,
    batch_scope: bool = False,
) -> dict[str, Any] | None:
    """Detail 422 estruturado, ou None se nada impede a análise.

    ``single_scope=True`` (card #1119, decisão 2): o pedido é o backtest de **1 ativo**
    (``POST /backtest`` ou ``POST /optimize`` com ``run_scope == "single"``). Com exatamente
    um símbolo, ação e ETF passam; ativo marcado pela Binance segue recusado (#1117) e ação/ETF
    de lote (mais de um símbolo) continua com ``asset_class_not_supported``.

    ``batch_scope=True`` (card #1120, decisão 3): o pedido é o lote multiclasse. Ação e ETF passam
    com qualquer número de símbolos; ativo marcado e símbolo fora do catálogo seguem recusados
    (``new_analysis=True``). A Descoberta não usa este escopo e segue recusando ação/ETF.

    ``new_analysis=False`` (backtest, usado também para reabrir resultados salvos)
    só recusa ação e ETF; pausados, removidos e fora do catálogo continuam
    abrindo. ``new_analysis=True`` (otimização e lote) também recusa ativo
    marcado e símbolo desconhecido. Sem lista válida da classe, o símbolo com
    ``/`` passa como antes: a falha da Binance nunca bloqueia a análise de
    cripto por conta própria.
    """
    unique = _dedupe(symbols)
    if not unique:
        return None
    try:
        checks = check_assets(unique)
    except SQLAlchemyError:
        logger.exception("Catálogo indisponível ao validar ativos; validação por formato")
        checks = [AssetCheck(symbol=s, found=False, catalog_unavailable=True) for s in unique]

    unsupported: list[AssetCheck] = []
    marked: list[AssetCheck] = []
    missing: list[AssetCheck] = []
    equity_passes = batch_scope or (single_scope and len(unique) == 1)
    for check in checks:
        is_crypto = "/" in check.symbol
        if check.found:
            if check.asset_class in (CLASS_STOCK, CLASS_ETF):
                if equity_passes:
                    # ação/ETF de 1 ativo ou de lote não reabre resultado salvo: ativo marcado não roda
                    if not check.selectable:
                        marked.append(check)
                    continue
                unsupported.append(check)
            elif new_analysis and not check.selectable:
                marked.append(check)
            continue
        if not is_crypto:
            if check.catalog_unavailable:
                unsupported.append(check)  # sem catálogo de ações, ticker segue sem análise
            else:
                missing.append(check)
            continue
        if new_analysis and not check.catalog_unavailable:
            missing.append(check)

    if unsupported:
        return _class_refusal(unsupported)
    if marked:
        return _marked_refusal(marked)
    if missing:
        return _missing_refusal(missing)
    return None


def discovery_symbol_reasons(symbols: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Motivo por símbolo para o Preflight da Descoberta (decisões 6 e 14).

    Devolve só os símbolos que ficam fora: ação e ETF (a Descoberta ainda não os aceita),
    ativo marcado pela Binance (estado e motivo) e ativo fora do catálogo. Sem lista válida
    da classe, nada é inventado: cripto segue pelo formato, como antes.
    """
    unique = _dedupe(symbols)
    if not unique:
        return {}
    try:
        checks = check_assets(unique)
    except SQLAlchemyError:
        logger.exception("Catálogo indisponível no Preflight; seguindo pelo formato do símbolo")
        return {}
    reasons: dict[str, dict[str, Any]] = {}
    for check in checks:
        is_crypto = "/" in check.symbol
        if check.found and not check.selectable:
            label = STATE_LABELS.get(check.state or "", check.state or "")
            detail = (check.state_reason or "").strip().rstrip(".")
            reasons[check.symbol] = {
                "asset_class": check.asset_class,
                "state": check.state,
                "reason": f"{label} na Binance"
                + (f" ({detail})" if detail else "")
                + "; não entra em análise nova",
                "kind": "marked",
            }
        elif check.found and check.asset_class in (CLASS_STOCK, CLASS_ETF):
            reasons[check.symbol] = {
                "asset_class": check.asset_class,
                "state": check.state,
                "reason": DISCOVERY_EQUITY_REASON,
                "kind": "class",
            }
        elif not check.found and not check.catalog_unavailable:
            reasons[check.symbol] = {
                "asset_class": CLASS_CRYPTO if is_crypto else None,
                "state": None,
                "reason": "ativo fora do catálogo da Binance",
                "kind": "missing",
            }
    return reasons
