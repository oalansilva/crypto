"""Coluna extra do Decidir: outra referência por candidato, sem mexer no ranking (card #1123, decisão 10).

A escolha vale por varredura e por usuário (``discovery_reference_columns``, no máximo uma ativa por
``(sweep_id, actor)``). Cada célula é uma ``benchmark_comparisons`` com dono ``discovery_result``,
calculada uma vez num job da fila de lotes (#1120), em lotes de 25, com a mesma função
``benchmark_comparison.compute`` do resultado. Os trades de cada candidato são regenerados só da
amostra congelada dele; a cripto que nunca guardou amostra (sem ``MARKET_HISTORY_UNIFIED``) refaz
pelo caminho antigo, com as velas do cache local, e só vale se as métricas refeitas baterem com as
gravadas na varredura (``metrics_match``). Nenhum dado novo do candidato é buscado. Ler, recarregar ou exportar lê o que foi gravado. Ordem,
rank global, "Ordenar por" e elegibilidade não dependem desta coluna.
"""

from __future__ import annotations

import logging
import threading
import uuid
from datetime import date, datetime, timezone
from typing import Any, Callable, Iterable, Optional

from sqlalchemy.orm import Session

from app.models_benchmark import COLUMN_RUNNING, BenchmarkComparison, DiscoveryReferenceColumn
from app.services import benchmark_comparison as bench
from app.services.discovery_inputs import LegacyInputsUnavailable

logger = logging.getLogger(__name__)

BATCH_SIZE = 25
NOT_COMPUTED = ("insufficient_sample",)
REGENERATION_FAILED = "regeneration_failed"
# Cripto sem amostra (sem ``snapshot_id``) cujo refeito pelo caminho antigo falhou por erro inesperado:
# não há amostra para citar; o histórico não é insuficiente (a planilha usa "Sem comparação").
REGENERATION_FAILED_LEGACY_TEXT = (
    "Sem comparação: não foi possível refazer os trades do candidato com as velas guardadas no "
    "servidor."
)
# Candidato com métrica mas sem CAGR gravado (ex.: acima de ``CAGR_ABS_CEILING``): não entra no
# cálculo e, com a coluna concluída, a célula fecha sem número com este motivo.
NO_CAGR = "no_cagr"
NO_CAGR_TEXT = "Sem comparação: o candidato não tem CAGR gravado."
NO_CAGR_SHORT = "Sem CAGR gravado do candidato."
# Candidato que nunca guardou amostra (cripto da Descoberta sem ``MARKET_HISTORY_UNIFIED``): os trades
# são refeitos pelo caminho antigo com as velas do cache local e conferidos pelas métricas gravadas na
# varredura. Quando não dá para refazer igual, a célula fecha sem número com o motivo verdadeiro (nunca
# "vencida": essa amostra não existiu).
SAMPLE_UNAVAILABLE = "sample_unavailable"
METRICS_MISMATCH = "metrics_mismatch"
UNAVAILABLE_TEXTS = {
    METRICS_MISMATCH: (
        "Trades refeitos não batem com a varredura.",
        "Sem comparação: os trades refeitos com as velas guardadas no servidor não dão as mesmas "
        "métricas da varredura (trades, CAGR ou taxa de acerto), então não são os mesmos trades. "
        "Rode a varredura de novo para comparar.",
    ),
    "missing": (
        "Velas do candidato não estão mais guardadas.",
        "Sem comparação: as velas do candidato usadas na varredura não estão mais guardadas no "
        "servidor. Rode a varredura de novo para comparar.",
    ),
    "unrecorded": (
        "Varredura sem dados para refazer os trades.",
        "Sem comparação: a varredura não registrou a janela ou as métricas do candidato, então não dá "
        "para refazer os trades e conferir que são os mesmos. Rode a varredura de novo para comparar.",
    ),
}
# Conferência do refeito (decisão do Alan, "Conferir pelas métricas"): mesmo número de trades, mesma
# taxa de acerto e o mesmo CAGR na precisão em que a Descoberta o mostra. O CAGR gravado e o refeito
# são frações (0.123 = 12,3%) do recorte de treino do split, e a Descoberta mostra 1 casa decimal do
# percentual (``fmtPct``): 0.0005 é meia casa, então diferenças abaixo disso aparecem iguais na tela.
# A taxa de acerto é ``ganhos / trades`` com o mesmo número de trades: igual, salvo arredondamento
# binário do float.
CAGR_MATCH_TOLERANCE = 0.0005
WIN_RATE_MATCH_TOLERANCE = 1e-9


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _iso(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- consultas


def active_column(db: Session, sweep_id: str, actor: str) -> Optional[DiscoveryReferenceColumn]:
    return (
        db.query(DiscoveryReferenceColumn)
        .filter(
            DiscoveryReferenceColumn.sweep_id == sweep_id,
            DiscoveryReferenceColumn.actor == actor,
            DiscoveryReferenceColumn.active.is_(True),
        )
        .first()
    )


def pending_column(db: Session, sweep_id: str, actor: str) -> Optional[DiscoveryReferenceColumn]:
    """A escolha mais nova que ainda não virou a coluna (coletando ou falhou na coleta)."""

    row = (
        db.query(DiscoveryReferenceColumn)
        .filter(
            DiscoveryReferenceColumn.sweep_id == sweep_id,
            DiscoveryReferenceColumn.actor == actor,
            DiscoveryReferenceColumn.active.is_(False),
            DiscoveryReferenceColumn.deactivated_at.is_(None),
        )
        .order_by(DiscoveryReferenceColumn.created_at.desc())
        .first()
    )
    return row


def candidates(db: Session, sweep_id: str) -> list[Any]:
    from app.models_discovery import DiscoveryResult

    rows = db.query(DiscoveryResult).filter(DiscoveryResult.sweep_id == sweep_id).all()
    return [r for r in rows if r.dedup_state != "discarded"]


def computable(rows: Iterable[Any]) -> list[Any]:
    return [r for r in rows if r.eligibility not in NOT_COMPUTED and r.cagr is not None]


def column_cells(
    db: Session, column_id: str, result_ids: Optional[Iterable[str]] = None
) -> dict[str, dict[str, Any]]:
    query = db.query(BenchmarkComparison).filter(BenchmarkComparison.column_id == column_id)
    if result_ids is not None:
        ids = [str(i) for i in result_ids if i]
        if not ids:
            return {}
        query = query.filter(BenchmarkComparison.result_id.in_(ids))
    return {row.result_id: dict(row.payload) for row in query.all()}


def column_payload(column: Optional[DiscoveryReferenceColumn]) -> Optional[dict[str, Any]]:
    if column is None:
        return None
    ref = dict(column.reference or {})
    return {
        "id": column.id,
        "sweep_id": column.sweep_id,
        "reference": ref,
        "reference_snapshot_id": column.reference_snapshot_id,
        "reference_version": ref.get("version_label"),
        "status": column.status,
        "done": int(column.done or 0),
        "total": int(column.total or 0),
        "error": column.error,
        "active": bool(column.active),
        "created_at": _iso(column.created_at),
        "completed_at": _iso(column.completed_at),
    }


def cell_summary(
    payload: Optional[dict[str, Any]],
    *,
    eligibility: Optional[str] = None,
    column_done: bool = False,
) -> dict[str, Any]:
    """Resumo da célula para a página do leaderboard; sem número enquanto não foi gravada.

    Com a coluna concluída, a linha sem célula gravada é a que ficou fora de ``computable`` (sem
    CAGR gravado): fecha sem número com motivo próprio em vez de ficar "Calculando…".
    """

    if eligibility in NOT_COMPUTED:
        return {"state": "no_sample"}
    if not payload:
        if column_done:
            return {
                "state": "insufficient",
                "id": None,
                "reason_code": NO_CAGR,
                "reason": NO_CAGR_SHORT,
                "expired_at": None,
            }
        return {"state": "pending"}
    reason = payload.get("reason") or {}
    if payload.get("status") != "valid":
        return {
            "state": "insufficient",
            "id": payload.get("id"),
            "reason_code": reason.get("code"),
            "reason": reason.get("short") or reason.get("text"),
            "expired_at": reason.get("expired_at"),
        }
    return {
        "state": "valid",
        "id": payload.get("id"),
        "delta_cagr_pp": (payload.get("delta") or {}).get("cagr_pp"),
        "reference_cagr": (payload.get("reference_result") or {}).get("cagr"),
        "strategy_cagr": (payload.get("strategy") or {}).get("cagr"),
        "common_window": payload.get("common_window"),
        "currency_note": payload.get("currency_note"),
        "trades_out": (payload.get("strategy") or {}).get("trades_out"),
    }


def column_counts(cells: dict[str, dict[str, Any]], total: int) -> dict[str, Any]:
    counts = {
        "valid": 0,
        "short_overlap": 0,
        "no_overlap": 0,
        "no_history": 0,
        bench.SAMPLE_EXPIRED: 0,
        SAMPLE_UNAVAILABLE: 0,
        REGENERATION_FAILED: 0,
    }
    fx = False
    for payload in cells.values():
        if payload.get("status") == "valid":
            counts["valid"] += 1
            fx = fx or bool(payload.get("currency_note"))
        else:
            code = (payload.get("reason") or {}).get("code") or "no_overlap"
            counts[code] = counts.get(code, 0) + 1
    return {**counts, "computed": len(cells), "total": total, "currency_note": fx}


# --------------------------------------------------------------------------- amostras


def _states(db: Session, snapshot_ids: Iterable[Optional[str]]) -> dict[str, dict[str, Any]]:
    from app.services.market_history import snapshots

    try:
        return snapshots.states_for(db, snapshot_ids)
    except Exception:
        logger.warning("Estado das amostras indisponível", exc_info=True)
        return {}


def _pin_all(db: Session, snapshot_ids: Iterable[Optional[str]]) -> None:
    from app.services.market_history import snapshots

    for sid in {s for s in snapshot_ids if s}:
        try:
            with db.begin_nested():
                snapshots.pin(db, sid)
        except Exception:  # pragma: no cover
            logger.warning("Não foi possível fixar a amostra %s", sid, exc_info=True)


def _release_all(db: Session, snapshot_ids: Iterable[Optional[str]]) -> None:
    """Solta as fixações da coluna (GC em 30 dias), salvo as amostras que um favorito usa."""

    from sqlalchemy import text

    from app.services.market_history import snapshots

    for sid in {s for s in snapshot_ids if s}:
        try:
            nested = db.begin_nested()
            used = db.execute(
                text(
                    "SELECT 1 FROM favorite_strategies WHERE snapshot_id = :sid "
                    "UNION ALL SELECT 1 FROM favorite_strategies f JOIN benchmark_comparisons b "
                    "ON b.id = f.benchmark_comparison_id WHERE "
                    "CAST(b.payload AS jsonb) -> 'samples' -> 'reference' ->> 'snapshot_id' = :sid "
                    "LIMIT 1"
                ),
                {"sid": sid},
            ).first()
            if used is None:
                snapshots.release(db, sid)
            nested.commit()
        except Exception:  # pragma: no cover
            nested.rollback()
            logger.warning("Não foi possível soltar a amostra %s", sid, exc_info=True)


def _deactivate(db: Session, column: DiscoveryReferenceColumn) -> None:
    column.active = False
    column.deactivated_at = _now()
    rows = candidates(db, column.sweep_id)
    _release_all(db, [column.reference_snapshot_id, *[r.snapshot_id for r in rows]])


def _activate(db: Session, column: DiscoveryReferenceColumn) -> None:
    current = active_column(db, column.sweep_id, column.actor)
    if current is not None and current.id != column.id:
        _deactivate(db, current)
        db.flush()
    column.active = True
    column.deactivated_at = None
    rows = candidates(db, column.sweep_id)
    states = _states(db, [r.snapshot_id for r in rows])
    keep = [
        r.snapshot_id
        for r in rows
        if r.snapshot_id and (states.get(r.snapshot_id) or {}).get("state") != "expired"
    ]
    _pin_all(db, [column.reference_snapshot_id, *keep])


# --------------------------------------------------------------------------- escolha


def _catalog_refusal(db: Session, symbol: str) -> Optional[str]:
    """Ativo marcado no catálogo (#1117) não pode ser referência."""

    try:
        from app.models_asset_catalog import AssetCatalog

        query = db.query(AssetCatalog).filter(AssetCatalog.symbol == symbol)
        row = query.order_by(AssetCatalog.removed_at.isnot(None), AssetCatalog.asset_id).first()
    except Exception:
        return None
    if row is None:
        return None
    state = str(getattr(row, "state", "tradable") or "tradable")
    if state != "tradable":
        reason = getattr(row, "state_reason", None) or str(state)
        return f"{symbol} não pode ser escolhido como referência: {reason}"
    return None


def enqueue(column_id: str) -> None:
    """Fila de lotes (#1120); sem fila disponível, roda num thread do processo."""

    try:
        from app.tasks.benchmark_column_tasks import run_reference_column_task

        run_reference_column_task.delay(column_id)
        return
    except Exception as exc:
        logger.warning(
            "Fila indisponível para a coluna extra %s (%s); rodando no processo", column_id, exc
        )
    thread = threading.Thread(
        target=run_column, args=(column_id,), daemon=True, name=f"refcol-{column_id[:8]}"
    )
    thread.start()


def set_reference(
    db: Session,
    sweep_id: str,
    actor: str,
    symbol: Optional[str],
    *,
    enqueue_fn: Callable[[str], None] = None,
    source: Optional[bench.ReferenceSource] = None,
) -> tuple[dict[str, Any], int]:
    enqueue_fn = enqueue_fn or enqueue
    source = source or bench.get_reference_source()
    current = active_column(db, sweep_id, actor)
    wanted = str(symbol or "").strip().upper()
    # Escolhas pendentes antigas deixam de valer (o job delas para no próximo lote).
    for stale in (
        db.query(DiscoveryReferenceColumn)
        .filter(
            DiscoveryReferenceColumn.sweep_id == sweep_id,
            DiscoveryReferenceColumn.actor == actor,
            DiscoveryReferenceColumn.active.is_(False),
            DiscoveryReferenceColumn.deactivated_at.is_(None),
        )
        .all()
    ):
        stale.deactivated_at = _now()
    if not wanted:
        if current is not None:
            _deactivate(db, current)
        db.commit()
        return {"column": None, "pending": None}, 200
    refusal = _catalog_refusal(db, wanted)
    if refusal:
        db.rollback()
        return {"code": "reference_marked", "message": refusal}, 422
    recorded = (
        db.query(DiscoveryReferenceColumn)
        .filter(
            DiscoveryReferenceColumn.sweep_id == sweep_id,
            DiscoveryReferenceColumn.actor == actor,
            DiscoveryReferenceColumn.status == "done",
        )
        .order_by(DiscoveryReferenceColumn.completed_at.desc())
        .all()
    )
    for column in recorded:
        if str((column.reference or {}).get("symbol") or "").upper() == wanted:
            # Já gravada nesta varredura: reativa sem recalcular.
            _activate(db, column)
            db.commit()
            return {"column": column_payload(column), "pending": None, "reactivated": True}, 200
    try:
        identity = source.identity(wanted)
    except Exception:
        identity = {"symbol": wanted, "asset_class": None}
    if not identity.get("asset_class"):
        db.rollback()
        return {
            "code": "reference_not_in_catalog",
            "message": f"{wanted} não está no catálogo de ativos.",
        }, 422
    total = len(computable(candidates(db, sweep_id)))
    column = DiscoveryReferenceColumn(
        id=str(uuid.uuid4()),
        sweep_id=sweep_id,
        actor=actor,
        reference={
            "symbol": identity.get("symbol") or wanted,
            "asset_id": identity.get("asset_id"),
            "asset_class": identity.get("asset_class"),
            "currency": identity.get("currency"),
            "name": identity.get("name"),
            "return_kind": bench.return_kind_of(identity.get("asset_class")),
        },
        status="computing" if source.has_history(wanted) else "collecting",
        done=0,
        total=total,
        active=False,
        created_at=_now(),
    )
    db.add(column)
    db.commit()
    enqueue_fn(column.id)
    return {"column": column_payload(current), "pending": column_payload(column)}, 202


def retry(
    db: Session, sweep_id: str, actor: str, *, enqueue_fn: Callable[[str], None] = None
) -> tuple[dict[str, Any], int]:
    enqueue_fn = enqueue_fn or enqueue
    column = pending_column(db, sweep_id, actor)
    if column is None or column.status != "failed":
        # Falha no cálculo de uma coluna já ativa: retoma do que falta (as células gravadas ficam).
        column = active_column(db, sweep_id, actor)
        if column is None or column.status != "failed":
            return {
                "code": "nothing_to_retry",
                "message": "Não há coleta ou cálculo com falha para tentar de novo.",
            }, 409
    column.status = "collecting" if not column.active else "computing"
    column.error = None
    db.commit()
    enqueue_fn(column.id)
    return {
        "column": column_payload(active_column(db, sweep_id, actor)),
        "pending": column_payload(column),
    }, 202


def state(db: Session, sweep_id: str, actor: str) -> dict[str, Any]:
    """Estado, progresso e o que o seletor precisa para avisar antes da escolha (sem coletar)."""

    from app.services.market_history import snapshots

    rows = candidates(db, sweep_id)
    comp = computable(rows)
    states = _states(db, [r.snapshot_id for r in comp])
    col = active_column(db, sweep_id, actor)
    out_col = column_payload(col)
    if col is not None:
        out_col["counts"] = column_counts(column_cells(db, col.id), len(comp))
    legacy = legacy_samples(db, [r for r in comp if not r.snapshot_id])
    windows = []
    for r in comp:
        st = states.get(r.snapshot_id) if r.snapshot_id else None
        if r.snapshot_id:
            sample = (st or {}).get("state") or "expired"
        else:
            # Nunca teve amostra: ``legacy`` = refazível pelo caminho antigo (conferido pelas métricas
            # no job); ``unavailable`` = não dá para refazer (sem janela ou sem o cache local).
            sample = legacy.get(r.id, "unavailable")
        windows.append(
            {
                "result_id": r.id,
                "symbol": r.symbol,
                "asset_class": r.asset_class,
                "start": bench.iso_day(bench.to_day(r.start_at, r.asset_class)),
                "end": bench.iso_day(bench.to_day(r.end_at, r.asset_class)),
                "sample": sample,
                "retain_until": (st or {}).get("retain_until"),
            }
        )
    del snapshots
    return {
        "sweep_id": sweep_id,
        "column": out_col,
        "pending": column_payload(pending_column(db, sweep_id, actor)),
        "candidates": windows,
        "not_computed": len(rows) - len(comp),
        "min_days": bench.MIN_COMMON_DAYS,
    }


# --------------------------------------------------------------------------- leaderboard e planilha


def attach_to_leaderboard(
    db: Session, sweep_id: str, actor: str, rows: list[dict[str, Any]]
) -> Optional[dict[str, Any]]:
    """``reference_comparison`` por linha da página e o resumo da coluna (junção, sem cálculo)."""

    col = active_column(db, sweep_id, actor)
    pending = pending_column(db, sweep_id, actor)
    if col is None and pending is None:
        return None
    summary = {"column": column_payload(col), "pending": column_payload(pending)}
    if col is None:
        return summary
    all_cells = column_cells(db, col.id)
    total = len(computable(candidates(db, sweep_id)))
    summary["column"]["counts"] = column_counts(all_cells, total)
    for row in rows:
        payload = all_cells.get(str(row.get("result_id")))
        row["reference_comparison"] = cell_summary(
            payload, eligibility=row.get("eligibility"), column_done=col.status == "done"
        )
    return summary


def export_cells(
    db: Session, sweep_id: str, actor: str
) -> tuple[Optional[DiscoveryReferenceColumn], dict[str, dict[str, Any]]]:
    """Coluna ativa e concluída com as células gravadas (as 13 colunas "(extra)")."""

    col = active_column(db, sweep_id, actor)
    if col is None or col.status != "done":
        return col, {}
    return col, column_cells(db, col.id)


# --------------------------------------------------------------------------- job


def _is_crypto(result: Any) -> bool:
    from app.services import discovery_multiclass as multiclass

    return "/" in str(result.symbol or "") and (
        multiclass.class_of(result.symbol, result.asset_class) == "crypto"
    )


def _legacy_windows(db: Session, rows: Iterable[Any]) -> dict[str, tuple[Any, Any]]:
    """Janela pedida de cada candidato: a da combinação, senão a do ``snapshot`` da varredura (mesma
    regra do caminho com amostra, ``regenerate_trades``). Lê só ``start_date``/``end_date`` dos JSON
    (sem carregá-los inteiros); ``None`` onde a varredura não gravou datas (período relativo antigo).
    """

    from app.models_discovery import DiscoveryCombination, DiscoverySweep

    rows = list(rows)
    ids = list({r.combination_id for r in rows if r.combination_id is not None})
    snap = DiscoveryCombination.input_snapshot
    combos: dict[Any, tuple[Any, Any]] = {}
    for offset in range(0, len(ids), 500):
        for cid, start, end in (
            db.query(DiscoveryCombination.id, snap["start_date"], snap["end_date"])
            .filter(DiscoveryCombination.id.in_(ids[offset : offset + 500]))
            .all()
        ):
            combos[cid] = (
                start if isinstance(start, str) else None,
                end if isinstance(end, str) else None,
            )
    sweeps: dict[Any, tuple[Any, Any]] = {}
    sweep_ids = list({r.sweep_id for r in rows})
    if sweep_ids:
        sweep_snap = DiscoverySweep.snapshot
        for sid, start, end in (
            db.query(DiscoverySweep.id, sweep_snap["start_date"], sweep_snap["end_date"])
            .filter(DiscoverySweep.id.in_(sweep_ids))
            .all()
        ):
            sweeps[sid] = (
                start if isinstance(start, str) else None,
                end if isinstance(end, str) else None,
            )
    out: dict[str, tuple[Any, Any]] = {}
    for r in rows:
        start, end = combos.get(r.combination_id) or (None, None)
        sweep_start, sweep_end = sweeps.get(r.sweep_id) or (None, None)
        out[r.id] = (start or sweep_start, end or sweep_end)
    return out


def legacy_samples(db: Session, rows: Iterable[Any]) -> dict[str, str]:
    """Estado, antes da escolha, dos candidatos que nunca tiveram amostra (sem ler as velas).

    ``legacy``: cripto com janela determinável (gravada ou derivada do treino gravado no resultado) e o
    cache local presente (refazer e conferir pelas métricas acontece no job, mesmo sem versão das
    velas gravada); ``unavailable``: não dá para refazer. Ação/ETF sem amostra é sempre
    ``unavailable`` (o caminho antigo é só da cripto).
    """

    from app.services import discovery_inputs as di

    rows = list(rows)
    out: dict[str, str] = {}
    loader = None
    present: dict[tuple[str, str], bool] = {}
    crypto = [r for r in rows if _is_crypto(r)]
    windows = _legacy_windows(db, crypto)
    for r in rows:
        start, end = windows.get(r.id) or (None, None)
        derivable = r.start_at is not None and r.end_at is not None
        if not _is_crypto(r) or not ((start and end) or derivable):
            out[r.id] = "unavailable"
            continue
        key = (r.symbol, r.timeframe)
        if key not in present:
            try:
                loader = loader or di._legacy_loader()
                present[key] = di.legacy_cache_present(r.symbol, r.timeframe, loader=loader)
            except Exception:
                logger.warning("Cache local indisponível para %s", key, exc_info=True)
                present[key] = False
        out[r.id] = "legacy" if present[key] else "unavailable"
    return out


def unavailable_sample_payload(
    strategy: bench.StrategySide, reference: dict[str, Any], detail: str
) -> dict[str, Any]:
    """Célula do candidato que nunca teve amostra e não dá para refazer igual: sem número."""

    short, text = UNAVAILABLE_TEXTS.get(detail) or UNAVAILABLE_TEXTS["unrecorded"]
    payload = bench.compute(strategy, reference, bench.daily_closes(None, None))
    payload["common_window"] = None
    payload["reason"] = {"code": SAMPLE_UNAVAILABLE, "text": text, "short": short, "detail": detail}
    return payload


def _run_fixed(
    result: Any,
    inputs: dict[str, Any],
    start: Any,
    end: Any,
    *,
    equity: bool,
    optimizer_factory: Optional[Callable[[], Any]] = None,
) -> dict[str, Any]:
    """Os parâmetros do candidato, sem otimizar, com o template congelado na varredura.

    Devolve a saída inteira do otimizador (``trades``, ``best_metrics``, ``candles``).
    """

    from app.services.combo_service import ComboService
    from app.services.favorite_backtest_refresh_service import _fixed_optimization_ranges
    from app.tasks.discovery_tasks import DISCOVERY_SPLIT_TRAIN_RATIO

    if optimizer_factory is None:
        from app.services.combo_optimizer import ComboOptimizer

        optimizer_factory = ComboOptimizer
    frozen_metadata = inputs.get("template_metadata")
    parameters = result.parameters if isinstance(result.parameters, dict) else {}
    original = ComboService.get_template_metadata
    if frozen_metadata is not None:
        ComboService.get_template_metadata = lambda self, name: (
            frozen_metadata if name == result.template_id else original(self, name)
        )
    try:
        out = optimizer_factory().run_optimization(
            template_name=result.template_id,
            symbol=result.symbol,
            timeframe=result.timeframe,
            data_source="binance_equity" if equity else "ccxt",
            start_date=start,
            end_date=end,
            custom_ranges=_fixed_optimization_ranges(parameters),
            deep_backtest=True,
            direction=result.direction,
            split_train_ratio=DISCOVERY_SPLIT_TRAIN_RATIO,
        )
    finally:
        ComboService.get_template_metadata = original
    return out or {}


def _template_metadata(db: Session, result: Any) -> Any:
    from app.models_discovery import DiscoveryCombination

    return (
        db.query(DiscoveryCombination.input_snapshot["template_metadata"])
        .filter(DiscoveryCombination.id == result.combination_id)
        .scalar()
    )


def legacy_window(db: Session, result: Any, *, loader: Any = None) -> tuple[Any, Any]:
    """Janela do refeito: a pedida e gravada; senão (varredura antiga com período relativo), a
    derivada do treino gravado no resultado (``discovery_inputs.legacy_window_from_training``)."""

    from app.services import discovery_inputs as di
    from app.tasks.discovery_tasks import DISCOVERY_SPLIT_TRAIN_RATIO

    start, end = _legacy_windows(db, [result]).get(result.id) or (None, None)
    if start and end:
        return start, end
    if result.start_at is None or result.end_at is None:
        return None, None
    return di.legacy_window_from_training(
        result.symbol,
        result.timeframe,
        result.start_at,
        result.end_at,
        DISCOVERY_SPLIT_TRAIN_RATIO,
        loader=loader,
    )


def redone_metrics(out: dict[str, Any]) -> dict[str, Any]:
    """Trades, CAGR e taxa de acerto do refeito, na mesma grandeza que a varredura gravou.

    Mesmo cálculo do ``run_combination``: ``trades_count = len(trades)``, ``win_rate`` do
    ``best_metrics`` (fração do recorte de treino) e o CAGR das colunas de ranking
    (``_ensure_in_sample_ranking`` + ``_ranking_columns``: fração, ``None`` sem trades ou fora do teto).
    """

    from app.tasks.discovery_tasks import _ensure_in_sample_ranking, _ranking_columns

    trades = out.get("trades") or []
    best = dict(out.get("best_metrics") or {})
    _ensure_in_sample_ranking(best, trades, out.get("candles") or [])
    cagr, _calmar, _bh, _delta = _ranking_columns(best, len(trades))
    return {"trades_count": len(trades), "cagr": cagr, "win_rate": best.get("win_rate")}


def _close(recorded: Any, redone: Any, tolerance: float) -> bool:
    if recorded is None or redone is None:
        return recorded is None and redone is None
    try:
        return abs(float(recorded) - float(redone)) <= tolerance
    except (TypeError, ValueError):
        return False


def metrics_match(result: Any, redone: dict[str, Any]) -> bool:
    """O refeito tem as métricas gravadas: trades iguais, acerto igual, CAGR na tolerância."""

    return (
        result.trades_count == redone.get("trades_count")
        and _close(result.win_rate, redone.get("win_rate"), WIN_RATE_MATCH_TOLERANCE)
        and _close(result.cagr, redone.get("cagr"), CAGR_MATCH_TOLERANCE)
    )


def regenerate_legacy_trades(
    db: Session,
    result: Any,
    *,
    optimizer_factory: Optional[Callable[[], Any]] = None,
    loader: Any = None,
) -> list[dict[str, Any]]:
    """Cripto sem amostra: refaz pelo caminho antigo com as velas do cache e confere pelas métricas.

    Mesma janela (``legacy_window``), mesmos parâmetros, direção, template congelado e
    ``split_train_ratio`` da varredura, com o recorte do cache local (só leitura, sem rede).
    A versão das velas não é condição; o refeito só vale se ``metrics_match``. Senão levanta
    ``LegacyInputsUnavailable`` com o motivo verdadeiro (``missing``, ``unrecorded`` ou
    ``metrics_mismatch``) e a célula fecha sem número.
    """

    from app.services import discovery_inputs as di

    if not _is_crypto(result) or result.trades_count is None:
        raise di.LegacyInputsUnavailable(di.LEGACY_UNRECORDED)
    start, end = legacy_window(db, result, loader=loader)
    with di.legacy_frozen_inputs(result.symbol, result.timeframe, start, end, loader=loader):
        out = _run_fixed(
            result,
            {"template_metadata": _template_metadata(db, result)},
            start,
            end,
            equity=False,
            optimizer_factory=optimizer_factory,
        )
    redone = redone_metrics(out)
    if not metrics_match(result, redone):
        logger.info(
            "Candidato %s refeito pelo caminho antigo não bate com a varredura: gravado "
            "trades=%s cagr=%s win_rate=%s; refeito %s",
            result.id,
            result.trades_count,
            result.cagr,
            result.win_rate,
            redone,
        )
        raise di.LegacyInputsUnavailable(METRICS_MISMATCH)
    return out.get("trades") or []


def regenerate_trades(
    db: Session, result: Any, *, optimizer_factory: Optional[Callable[[], Any]] = None
) -> list[dict[str, Any]]:
    """Trades do candidato só da amostra congelada dele (mesmo caminho determinístico do favorito).

    Sem ``snapshot_id`` (cripto da Descoberta sem amostra durável), refaz pelo caminho antigo
    conferido pelas métricas (``regenerate_legacy_trades``).
    """

    if not result.snapshot_id:
        return regenerate_legacy_trades(db, result, optimizer_factory=optimizer_factory)

    from app.models_discovery import DiscoveryCombination, DiscoverySweep
    from app.services.market_history import snapshots
    from app.services.market_history.reproduction import frozen_environment

    from app.database import engine

    manifest = snapshots.validate(engine, result.snapshot_id)
    combination = (
        db.query(DiscoveryCombination)
        .filter(DiscoveryCombination.id == result.combination_id)
        .first()
    )
    inputs = (combination.input_snapshot if combination is not None else None) or {}
    sweep = db.query(DiscoverySweep).filter(DiscoverySweep.id == result.sweep_id).first()
    snap = sweep.snapshot if sweep is not None and isinstance(sweep.snapshot, dict) else {}
    start = inputs.get("start_date") or snap.get("start_date")
    end = inputs.get("end_date") or snap.get("end_date")
    equity = str(result.asset_class or "").lower() in ("stock", "etf") or "/" not in str(
        result.symbol
    )
    with frozen_environment(manifest):
        out = _run_fixed(
            result, inputs, start, end, equity=equity, optimizer_factory=optimizer_factory
        )
    return out.get("trades") or []


def _candidate_side(result: Any) -> bench.StrategySide:
    from app.services import discovery_multiclass as multiclass

    asset_class = multiclass.class_of(result.symbol, result.asset_class)
    return bench.strategy_side(
        symbol=result.symbol,
        asset={
            "asset_class": asset_class,
            "currency": multiclass.currency_of(result.symbol, asset_class),
        },
        window={"start": result.start_at, "end": result.end_at},
        trades=[],
        direction=result.direction,
        snapshot_id=result.snapshot_id,
        version_label=result.candle_version,
    )


def _union_window(rows: Iterable[Any]) -> tuple[Optional[date], Optional[date]]:
    starts, ends = [], []
    for r in rows:
        a, b = bench.to_day(r.start_at, r.asset_class), bench.to_day(r.end_at, r.asset_class)
        if a:
            starts.append(a)
        if b:
            ends.append(b)
    return (min(starts) if starts else None, max(ends) if ends else None)


def _superseded(db: Session, column_id: str) -> bool:
    db.expire_all()
    col = (
        db.query(DiscoveryReferenceColumn).filter(DiscoveryReferenceColumn.id == column_id).first()
    )
    return col is None or col.deactivated_at is not None


def run_column(
    column_id: str,
    *,
    db_factory: Callable[[], Session] = None,
    source: Optional[bench.ReferenceSource] = None,
    regenerate: Callable[[Session, Any], list[dict[str, Any]]] = None,
) -> None:
    if db_factory is None:
        from app.database import SessionLocal

        db_factory = SessionLocal
    source = source or bench.get_reference_source()
    regenerate = regenerate or regenerate_trades
    db = db_factory()
    try:
        column = (
            db.query(DiscoveryReferenceColumn)
            .filter(DiscoveryReferenceColumn.id == column_id)
            .first()
        )
        if column is None or column.deactivated_at is not None or column.status == "done":
            return
        ref = dict(column.reference or {})
        symbol = ref.get("symbol")
        rows = candidates(db, column.sweep_id)
        comp = computable(rows)
        union_start, union_end = _union_window(comp)
        # 1. coleta (decisão 6): falha sem nada guardado não grava nada e mantém a coluna anterior.
        try:
            loaded = source.load(
                symbol, bench.iso_day(union_start), bench.iso_day(union_end), collect=True
            )
        except bench.BenchmarkError as exc:
            column.status = "failed"
            column.error = exc.message
            db.commit()
            return
        if _superseded(db, column_id):
            return
        column = (
            db.query(DiscoveryReferenceColumn)
            .filter(DiscoveryReferenceColumn.id == column_id)
            .first()
        )
        identity = {**loaded.identity, "kind": "catalog"}
        closes = bench.daily_closes(loaded.frame, identity.get("asset_class"))
        # 2. amostra 1d da referência, congelada uma vez sobre a união das janelas.
        ref_sample: dict[str, Any]
        lo = max(union_start, closes.index[0]) if union_start and len(closes) else None
        hi = min(union_end, closes.index[-1]) if union_end and len(closes) else None
        if lo and hi and lo <= hi:
            ref_sample = source.freeze(
                symbol, loaded.frame, lo, hi, f"benchmark:column:{column_id}"
            )
        else:
            ref_sample = source.version_only(symbol)
        column.reference = {**ref, "version_label": ref_sample.get("version_label")}
        column.reference_snapshot_id = ref_sample.get("snapshot_id")
        column.status = "computing"
        column.total = len(comp)
        column.done = 0
        column.error = None
        _activate(db, column)
        db.commit()
        # 3. células, em lotes de 25; trocar de referência no meio para o job.
        states = _states(db, [r.snapshot_id for r in comp])
        existing = set(column_cells(db, column_id).keys())
        done = len(existing)
        for offset in range(0, len(comp), BATCH_SIZE):
            if _superseded(db, column_id):
                return
            for result in comp[offset : offset + BATCH_SIZE]:
                if result.id in existing:
                    continue
                strategy = _candidate_side(result)
                # Sem ``snapshot_id`` o candidato nunca teve amostra (não "venceu"): o ``regenerate``
                # refaz pelo caminho antigo conferido pelas métricas ou diz por que não dá.
                sample_state = (states.get(result.snapshot_id) or {}) if result.snapshot_id else {}
                if sample_state.get("state") == "expired":
                    payload = bench.expired_sample_payload(
                        strategy, identity, sample_state.get("retain_until")
                    )
                    payload["samples"] = {"strategy": None, "reference": ref_sample}
                else:
                    try:
                        strategy.trades = bench.closed_trades(regenerate(db, result))
                        payload = bench.build_payload(
                            strategy,
                            symbol,
                            source=source,
                            loaded=loaded,
                            reference_sample=ref_sample,
                        )
                    except LegacyInputsUnavailable as exc:
                        logger.info(
                            "Candidato %s sem amostra não refeito pelo caminho antigo: %s",
                            result.id,
                            exc.detail,
                        )
                        payload = unavailable_sample_payload(strategy, identity, exc.detail)
                        payload["samples"] = {"strategy": None, "reference": ref_sample}
                    except Exception as exc:
                        logger.warning("Trades do candidato %s não regenerados: %s", result.id, exc)
                        code = getattr(exc, "code", "")
                        if result.snapshot_id and str(code).startswith("frozen_input"):
                            payload = bench.expired_sample_payload(strategy, identity, None)
                        else:
                            payload = bench.compute(
                                strategy, identity, bench.daily_closes(None, None)
                            )
                            payload["reason"] = {
                                "code": REGENERATION_FAILED,
                                "text": (
                                    "Não foi possível refazer os trades do candidato a partir da amostra."
                                    if result.snapshot_id
                                    else REGENERATION_FAILED_LEGACY_TEXT
                                ),
                                "short": "Trades do candidato não refeitos.",
                            }
                        payload["samples"] = {"strategy": None, "reference": ref_sample}
                bench.persist(
                    db,
                    payload,
                    owner_kind="discovery_result",
                    user_id=column.actor,
                    trigger="choice",
                    result_id=result.id,
                    column_id=column_id,
                    commit=False,
                )
                done += 1
            column.done = done
            db.commit()
        if _superseded(db, column_id):
            return
        column = (
            db.query(DiscoveryReferenceColumn)
            .filter(DiscoveryReferenceColumn.id == column_id)
            .first()
        )
        column.status = "done"
        column.done = done
        column.completed_at = _now()
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Coluna extra %s falhou", column_id)
        try:
            column = (
                db.query(DiscoveryReferenceColumn)
                .filter(DiscoveryReferenceColumn.id == column_id)
                .first()
            )
            if column is not None and column.status != "done":
                column.status = "failed"
                column.error = f"Falha no cálculo da coluna: {exc}"
                db.commit()
        except Exception:  # pragma: no cover
            db.rollback()
    finally:
        db.close()


# --------------------------------------------------------------------------- promoção


def inherited_for_promotion(
    db: Session, sweep_id: str, actor: str, result_id: str
) -> Optional[dict[str, Any]]:
    """Célula gravada que o favorito promovido herda (mesma referência, mesma amostra, sem recálculo)."""

    col = active_column(db, sweep_id, actor)
    if col is None:
        return None
    payload = column_cells(db, col.id, [result_id]).get(str(result_id))
    if payload is None or payload.get("status") != "valid":
        return None
    return payload
