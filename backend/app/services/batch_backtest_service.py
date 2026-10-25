"""Lote de backtests multiclasse (card #1120).

Cada ativo da seleção (cripto, ação ou ETF) passa pelo caminho do backtest individual do #1119:
coleta do histórico, otimização lendo só o que foi guardado e gravação do melhor resultado como
favorito com a nota "gerado em lote". O estado do lote e de cada ativo vive no PostgreSQL
(``batch_backtest_store``), com pausa, retomada e encerramento que valem ao fim da etapa em curso.

Estados por ativo (decisão 8): ``queued``, ``collecting``, ``optimizing``, ``success``,
``success_daily``, ``insufficient``, ``rejected``, ``failed``, ``skipped``, ``out``, ``not_run``.
Só ``success`` e ``success_daily`` gravam favorito; problema de um ativo nunca para os outros.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Callable

from app.database import SessionLocal
from app.models import FavoriteStrategy
from app.models_batch_backtest import ITEM_FINAL_STATES
from app.services import batch_backtest_legacy
from app.services.batch_backtest_plan import (
    PLAN_OUT,
    build_plan,
)
from app.services.batch_backtest_store import get_batch_backtest_store, utcnow_naive
from app.services.combo_optimizer import ComboOptimizer
from app.services.equity_backtest import (
    CODE_HISTORY_UNAVAILABLE,
    EquityRunError,
    prepare_equity_history,
)
from app.services.favorite_uniqueness import find_existing_favorite, lock_and_find_duplicate
from app.services.market_data_providers import (
    BINANCE_EQUITY_SOURCE,
    CCXT_SOURCE,
    BinanceEquityMarketDataProvider,
)
from app.services.market_history import force_unified
from app.services.opportunity_service import _is_unsupported_symbol

logger = logging.getLogger(__name__)

STATE_COLLECTING = "collecting"
STATE_OPTIMIZING = "optimizing"
RESUME_NOTE = "histórico coletado; otimiza ao retomar, na mesma amostra."
ALREADY_FAVORITE = "Já está nos favoritos com o mesmo período e direção."
_CRYPTO_DEFAULT_START = "2017-01-01"


# ---------------------------------------------------------------- API do serviço


def _metrics_with_source_trades(
    best_metrics: dict[str, Any], trades: list[dict[str, Any]] | None
) -> dict[str, Any]:
    metrics = dict(best_metrics or {})
    metrics["trades"] = trades if isinstance(trades, list) else []
    return metrics


def get_batch_progress(job_id: str) -> dict[str, Any] | None:
    """Estado atual do lote (com ``items`` e ``totals`` nos lotes novos), ou ``None``."""

    job = get_batch_backtest_store().get_job(job_id, include_items=True)
    return _public_job(job)


def get_active_batch(user_id: str | None) -> dict[str, Any] | None:
    """O lote não final mais recente do usuário (decisão 10)."""

    return _public_job(get_batch_backtest_store().active_job(user_id))


def get_paused_batch(user_id: str | None) -> dict[str, Any] | None:
    return get_batch_backtest_store().paused_job(user_id)


def _public_job(job: dict[str, Any] | None) -> dict[str, Any] | None:
    if job is None:
        return None
    out = dict(job)
    plan = out.pop("plan", None)
    out.pop("payload", None)
    out.pop("user_id", None)
    if isinstance(plan, dict):
        out["config"] = plan.get("config")
    if isinstance(out.get("items"), list):
        for item in out["items"]:
            extra = item.pop("extra", None) or {}
            item["collect_kind"] = extra.get("collect_kind")
            item["needs_collection"] = extra.get("needs_collection") or []
    return out


def create_batch_job(
    job_id: str, *, user_id: str | None, payload: dict[str, Any], plan: dict[str, Any]
) -> dict[str, Any]:
    """Cria o lote com um item por ativo: "Fora" já decidido no plano, o resto "Na fila"."""

    items = []
    for planned in plan["items"]:
        out = planned["plan"] == PLAN_OUT
        items.append(
            {
                "symbol": planned["symbol"],
                "asset_class": planned.get("asset_class"),
                "currency": planned.get("currency"),
                "state": "out" if out else "queued",
                "reason": planned.get("reason") if out else None,
                "progress": None,
                "extra": {
                    "asset_id": planned.get("asset_id"),
                    "data_source": planned.get("data_source"),
                    "collect_kind": planned.get("collect_kind"),
                    "needs_collection": planned.get("needs_collection"),
                    "collect_note": planned.get("collect_note"),
                    "covered_until": planned.get("covered_until"),
                    "out_kind": planned.get("out_kind"),
                },
            }
        )
    return get_batch_backtest_store().create_job(
        job_id, user_id=user_id, payload=payload, plan=plan, items=items
    )


def init_batch_job(job_id: str, total: int) -> None:
    """Cria o lote só com o total (formato sem itens)."""

    get_batch_backtest_store().init_job(job_id, total)


def request_pause_batch(job_id: str) -> bool:
    """Pede a pausa: vale ao fim da etapa em curso do ativo atual."""

    store = get_batch_backtest_store()
    if not store.is_durable(job_id):
        return batch_backtest_legacy.request_pause_legacy(job_id)
    return store.request_pause(job_id)


def request_cancel_batch(job_id: str) -> bool:
    """Pede o encerramento: vale ao fim da etapa em curso; o que terminou e os favoritos ficam."""

    store = get_batch_backtest_store()
    if not store.is_durable(job_id):
        return batch_backtest_legacy.request_cancel_legacy(job_id)
    return store.request_cancel(job_id)


def request_resume_batch(job_id: str) -> bool:
    """Põe o lote pausado de volta na fila, no mesmo id (a rota enfileira a tarefa)."""

    return get_batch_backtest_store().request_resume(job_id)


# ---------------------------------------------------------------- limiar de "Insuficiente"

_PERIOD_KEY = re.compile(
    r"(period|length|window|lookback|ema|sma|wma|\bma\d|slow|fast|long|signal)", re.IGNORECASE
)


def minimum_candles(template_name: str, custom_ranges: dict[str, Any] | None) -> int:
    """Candles que a estratégia precisa para aquecer os indicadores: maior período + 1.

    Lido do esquema de otimização do template (maior ``max`` dos parâmetros de período) ou dos
    intervalos personalizados do pedido. Sem período conhecido, não exige mais que o otimizador.
    """

    try:
        from app.services.combo_service import ComboService

        metadata = ComboService().get_template_metadata(template_name) or {}
    except Exception:  # o limiar nunca derruba o lote
        metadata = {}
    schema = metadata.get("optimization_schema") or {}
    params = schema.get("parameters") if isinstance(schema.get("parameters"), dict) else schema
    longest = 0
    for name, config in (params or {}).items():
        if not isinstance(config, dict) or not _PERIOD_KEY.search(str(name)):
            continue
        custom = (custom_ranges or {}).get(name) or {}
        top = custom.get("max", config.get("max"))
        try:
            longest = max(longest, int(float(top)))
        except (TypeError, ValueError):
            continue
    return longest + 1 if longest >= 2 else 0


# ---------------------------------------------------------------- execução


class BatchStopped(Exception):
    """O lote parou (pausa ou encerramento) ao fim de uma etapa."""

    def __init__(self, cancelled: bool) -> None:
        super().__init__("cancelled" if cancelled else "paused")
        self.cancelled = cancelled


def run_batch_backtest(job_id: str, payload: dict[str, Any], task_id: str | None = None) -> None:
    """Executa (ou retoma) o lote: ativo por ativo, pulando o que já terminou."""

    store = get_batch_backtest_store()
    if not store.is_durable(job_id):
        batch_backtest_legacy.run_legacy_batch_backtest(job_id, payload)
        return
    if not store.claim(job_id, task_id):
        logger.info("Batch %s: já assumido, pausado ou final; nada a fazer", job_id[:8])
        return
    BatchRunner(job_id, store=store).run()


class BatchRunner:
    def __init__(
        self,
        job_id: str,
        *,
        store: Any = None,
        optimizer_factory: Callable[[], ComboOptimizer] = ComboOptimizer,
    ) -> None:
        self.job_id = job_id
        self.store = store or get_batch_backtest_store()
        self._optimizer_factory = optimizer_factory
        job = self.store.get_job(job_id) or {}
        self.payload: dict[str, Any] = dict(job.get("payload") or {})
        self.user_id = self.payload.get("user_id") or job.get("user_id")
        self.template_name = self.payload["template_name"]
        self.timeframe = self.payload.get("timeframe", "1d")
        direction = self.payload.get("direction", "long")
        self.direction = direction if direction in ("long", "short") else "long"
        self.base_elapsed = float(job.get("elapsed_sec") or 0.0)
        self.segment_start = time.time()
        self.durations: list[float] = []

    # -- andamento ---------------------------------------------------------------------

    def _elapsed(self) -> float:
        return self.base_elapsed + (time.time() - self.segment_start)

    def _estimate(self) -> float | None:
        if not self.durations:
            return None
        pending = sum(
            1 for i in self.store.list_items(self.job_id) if i["state"] not in ITEM_FINAL_STATES
        )
        return (sum(self.durations) / len(self.durations)) * pending if pending else None

    def _progress(self, **changes: Any) -> None:
        self.store.update_job(self.job_id, elapsed_sec=self._elapsed(), **changes)

    def _set_item(self, item: dict[str, Any], **changes: Any) -> None:
        self.store.update_item(self.job_id, item["position"], **changes)
        item.update(changes)

    def _stop_flag(self) -> str | None:
        job = self.store.get_job(self.job_id) or {}
        if job.get("cancel_requested"):
            return "cancel"
        if job.get("pause_requested"):
            return "pause"
        return None

    def _checkpoint(self) -> None:
        flag = self._stop_flag()
        if flag:
            raise BatchStopped(cancelled=flag == "cancel")

    # -- laço --------------------------------------------------------------------------

    def run(self) -> None:
        job = self.store.get_job(self.job_id) or {}
        if not job.get("started_at"):
            self.store.update_job(self.job_id, started_at=utcnow_naive().isoformat())
            self._replan()
        self.store.update_job(self.job_id, last_error=None)
        try:
            for item in self.store.list_items(self.job_id):
                if item["state"] in ITEM_FINAL_STATES:
                    continue
                self._checkpoint()
                began = time.time()
                self._progress(current_symbol=item["symbol"], current_stage=None)
                final = self._run_item(item)
                self.store.refresh_counters(self.job_id)
                if final:
                    self.durations.append(time.time() - began)
                self._progress(estimated_remaining_sec=self._estimate())
        except BatchStopped as stop:
            self.store.finish_stop(self.job_id, cancelled=stop.cancelled)
            self._progress()
            logger.info("Batch %s %s", self.job_id[:8], "cancelled" if stop.cancelled else "paused")
            return
        self.store.refresh_counters(self.job_id)
        self.store.update_job(
            self.job_id,
            status="completed",
            pause_requested=False,
            cancel_requested=False,
            estimated_remaining_sec=None,
            current_symbol=None,
            current_stage=None,
            finished_at=utcnow_naive().isoformat(),
            elapsed_sec=self._elapsed(),
        )
        job = self.store.get_job(self.job_id) or {}
        logger.info(
            "Batch %s completed: %d succeeded, %d failed, %d skipped",
            self.job_id[:8],
            job.get("succeeded", 0),
            job.get("failed", 0),
            job.get("skipped", 0),
        )

    def _replan(self) -> None:
        """O plano é recalculado ao começar (a cobertura pode ter mudado) e gravado no lote."""

        try:
            plan = build_plan(self.payload, page=self.payload.get("page"))
        except Exception:  # sem plano novo, vale o do pedido
            logger.exception("Batch %s: plano não pôde ser recalculado", self.job_id[:8])
            return
        by_symbol = {p["symbol"]: p for p in plan["items"]}
        for item in self.store.list_items(self.job_id):
            planned = by_symbol.get(item["symbol"])
            if planned is None or item["state"] not in ("queued", "out"):
                continue
            extra = dict(item.get("extra") or {})
            extra.update(
                data_source=planned.get("data_source"),
                collect_kind=planned.get("collect_kind"),
                needs_collection=planned.get("needs_collection"),
                collect_note=planned.get("collect_note"),
                covered_until=planned.get("covered_until"),
                out_kind=planned.get("out_kind"),
            )
            if planned["plan"] == PLAN_OUT:
                self.store.update_item(
                    self.job_id,
                    item["position"],
                    state="out",
                    reason=planned.get("reason"),
                    extra=extra,
                    finished_at=utcnow_naive(),
                )
            else:
                self.store.update_item(
                    self.job_id,
                    item["position"],
                    state="queued",
                    reason=None,
                    extra=extra,
                    finished_at=None,
                )
        total = sum(1 for p in plan["items"] if p["plan"] != PLAN_OUT)
        self.store.update_job(self.job_id, plan=plan, total=total)

    # -- um ativo ----------------------------------------------------------------------

    def _run_item(self, item: dict[str, Any]) -> bool:
        """Roda um ativo. Devolve ``True`` quando o ativo terminou (qualquer estado final)."""

        symbol = item["symbol"]
        equity = "/" not in symbol
        extra = dict(item.get("extra") or {})
        data_source = (
            BINANCE_EQUITY_SOURCE if equity else (self.payload.get("data_source") or CCXT_SOURCE)
        )
        if not equity and str(data_source).lower() in {"", "binance", "crypto", "default"}:
            data_source = CCXT_SOURCE
        self._set_item(item, started_at=item.get("started_at") or utcnow_naive())

        if _is_unsupported_symbol(symbol):
            logger.info("Batch: skip %s (unsupported / excluded)", symbol)
            return self._finish(item, "skipped", "Símbolo excluído da análise; nada foi executado.")

        db = SessionLocal()
        try:
            if self._existing(db, symbol, data_source, item) is not None:
                logger.info("Batch: skip %s (already in favorites)", symbol)
                return self._finish(item, "skipped", ALREADY_FAVORITE)
        finally:
            db.close()

        start, end = self.payload.get("start_date"), self.payload.get("end_date")
        deep = bool(self.payload.get("deep_backtest", True))
        collection_note = None
        # (a) coleta
        if not extra.get("collected"):
            self._set_item(
                item,
                state=STATE_COLLECTING if extra.get("collect_kind") != "none" else STATE_OPTIMIZING,
                progress=None,
            )
            self._progress(current_stage="coletando histórico")
            try:
                collection_note = self._collect(item, equity, start, end, deep)
            except EquityRunError as exc:
                return self._collect_error(item, exc)
            except Exception as exc:
                logger.exception("Batch: coleta de %s falhou: %s", symbol, exc)
                return self._finish(
                    item,
                    "failed",
                    f"Coleta falhou: {exc}. Nenhum favorito gravado.",
                    error=str(exc),
                )
            extra["collected"] = True
            extra["collection"] = collection_note
            self._set_item(item, extra=extra)
        else:
            collection_note = extra.get("collection")
        # a pausa ou o encerramento valem aqui: a coleta terminou, a otimização ainda não começou
        flag = self._stop_flag()
        if flag:
            self._set_item(
                item,
                state="queued",
                progress=RESUME_NOTE,
                extra=extra,
            )
            raise BatchStopped(cancelled=flag == "cancel")

        # (b) otimização, sem nova coleta
        self._set_item(item, state=STATE_OPTIMIZING, progress=None)
        self._progress(current_stage="otimizando")
        try:
            result = self._optimize(symbol, equity, data_source, start, end, deep, collection_note)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            logger.exception("Batch backtest failed for %s: %s", symbol, exc)
            return self._finish(
                item, "failed", f"Erro na execução: {exc}. Nenhum favorito gravado.", error=str(exc)
            )
        return self._conclude(item, result, equity, data_source)

    def _existing(self, db: Any, symbol: str, data_source: str, item: dict[str, Any]) -> Any:
        return find_existing_favorite(
            db,
            user_id=self.user_id,
            strategy_name=self.template_name,
            symbol=symbol,
            timeframe=self.timeframe,
            period_type=self.payload.get("period_type"),
            start_date=self.payload.get("start_date"),
            end_date=self.payload.get("end_date"),
            direction=self.direction,
            data_source=data_source,
            asset={"symbol": symbol, "asset_class": item.get("asset_class")},
        )

    # -- etapas ------------------------------------------------------------------------

    def _collect(
        self, item: dict[str, Any], equity: bool, start: Any, end: Any, deep: bool
    ) -> dict[str, Any] | None:
        symbol = item["symbol"]

        def on_progress(role: str, tf: str, page: int, total: int | None) -> None:
            label = f"{tf} do intrabar" if role == "intraday" else tf
            text = f"{label} · página {page}" + (f" de {total}" if total else "")
            if item.get("state") != STATE_COLLECTING:
                self.store.update_item(self.job_id, item["position"], state=STATE_COLLECTING)
                item["state"] = STATE_COLLECTING
            self.store.update_item(self.job_id, item["position"], progress=text)
            self._progress(current_stage=f"coletando {text}")

        if equity:
            prep = prepare_equity_history(
                symbol, self.timeframe, start, end, intrabar=deep, on_progress=on_progress
            )
            return prep.collection
        _collect_crypto_history(symbol, self.timeframe, start, end, on_progress)
        return None

    def _optimize(
        self,
        symbol: str,
        equity: bool,
        data_source: str,
        start: Any,
        end: Any,
        deep: bool,
        collection_note: dict[str, Any] | None,
    ) -> dict[str, Any]:
        optimizer = self._optimizer_factory()
        if equity:
            # Coleta feita: a otimização lê só o guardado, sem nova ida à Binance (como no #1119).
            optimizer._provider = BinanceEquityMarketDataProvider(ensure=False)
            optimizer.collection_note = collection_note
        # O lote liga o caminho unificado por ativo: a cripto também congela a amostra (decisão 11).
        with force_unified():
            return optimizer.run_optimization(
                template_name=self.template_name,
                symbol=symbol,
                timeframe=self.timeframe,
                data_source=data_source,
                start_date=start,
                end_date=end,
                custom_ranges=self.payload.get("custom_ranges"),
                deep_backtest=deep,
                job_id=self.job_id,
                direction=self.direction,
                split_train_ratio=self.payload.get("split_train_ratio"),
            )

    # -- desfecho ----------------------------------------------------------------------

    def _finish(
        self,
        item: dict[str, Any],
        state: str,
        reason: str | None,
        *,
        error: str | None = None,
        favorite_id: int | None = None,
        execution: dict[str, Any] | None = None,
        snapshot_id: str | None = None,
    ) -> bool:
        self._set_item(
            item,
            state=state,
            reason=reason,
            progress=None,
            favorite_id=favorite_id,
            execution=execution,
            snapshot_id=snapshot_id,
            finished_at=utcnow_naive(),
        )
        job = self.store.get_job(self.job_id) or {}
        if error is not None:
            errors = list(job.get("errors") or [])
            errors.append({"symbol": item["symbol"], "error": error})
            self.store.update_job(self.job_id, errors=errors)
        elif state in ("rejected", "insufficient"):
            reasons = list(job.get("skipped_reasons") or [])
            reasons.append({"symbol": item["symbol"], "reason": state, "details": reason})
            self.store.update_job(self.job_id, skipped_reasons=reasons)
        return True

    def _collect_error(self, item: dict[str, Any], exc: EquityRunError) -> bool:
        reason = str((exc.extra or {}).get("reason") or "")
        no_candles = (
            exc.code == CODE_HISTORY_UNAVAILABLE
            and not (exc.extra or {}).get("error_code")
            and "não tem candles" in reason
        )
        if no_candles:
            return self._finish(
                item,
                "insufficient",
                f"Dados insuficientes: {reason}. Nenhum favorito gravado.",
            )
        return self._finish(
            item, "failed", f"{exc.message} Nenhum favorito gravado.", error=exc.message
        )

    def _conclude(
        self, item: dict[str, Any], result: dict[str, Any], equity: bool, data_source: str
    ) -> bool:
        symbol = item["symbol"]
        snapshot_id = result.get("snapshot_id")
        execution = result.get("execution") if isinstance(result.get("execution"), dict) else None

        needed = minimum_candles(self.template_name, self.payload.get("custom_ranges"))
        covered = ((execution or {}).get("window") or {}).get("covered") or {}
        candles = covered.get("candles")
        if needed and candles is not None and int(candles) < needed:
            self._expire(snapshot_id)
            return self._finish(
                item,
                "insufficient",
                f"Dados insuficientes: a janela coberta tem {int(candles)} candles de "
                f"{self.timeframe} e a estratégia precisa de pelo menos {needed}. "
                "Nenhum favorito gravado.",
                execution=execution,
            )

        # Walk-forward (card #470): candidato NO-GO/ERROR no holdout não é salvo.
        oos_verdict = result.get("oos_verdict")
        if isinstance(oos_verdict, dict) and (
            str(oos_verdict.get("status") or "").strip().upper() != "GO"
        ):
            reasons = oos_verdict.get("reasons") or ["veredito não-GO no holdout"]
            status = str(oos_verdict.get("status") or "UNKNOWN").strip().upper()
            self._expire(snapshot_id)
            return self._finish(
                item,
                "rejected",
                f"Reprovado no walk-forward ({status} no holdout): "
                f"{'; '.join(str(r) for r in reasons[:5])}. Nenhum favorito gravado.",
                execution=execution,
            )

        try:
            favorite_id = self._save_favorite(item, result, data_source, execution, snapshot_id)
        except Exception as exc:
            logger.exception("Batch: failed to save favorite for %s: %s", symbol, exc)
            self._expire(snapshot_id)
            return self._finish(
                item,
                "failed",
                f"Não foi possível gravar o favorito: {exc}. Nenhum favorito gravado.",
                error=f"save favorite: {exc}",
            )
        if favorite_id is None:
            self._expire(snapshot_id)
            return self._finish(item, "skipped", ALREADY_FAVORITE)
        daily = bool(
            execution
            and execution.get("precision_requested") == "intrabar"
            and execution.get("precision_effective") != "intrabar_15m"
        )
        return self._finish(
            item,
            "success_daily" if daily else "success",
            None,
            favorite_id=favorite_id,
            execution=execution,
            snapshot_id=snapshot_id,
        )

    @staticmethod
    def _expire(snapshot_id: str | None) -> None:
        if not snapshot_id:
            return
        try:
            from app.database import engine
            from app.services.market_history import snapshots as history_snapshots

            history_snapshots.expire(engine, snapshot_id)
        except Exception:  # pragma: no cover - a limpeza nunca esconde o resultado
            logger.exception("Batch: amostra %s não pôde ser liberada", snapshot_id)

    def _save_favorite(
        self,
        item: dict[str, Any],
        result: dict[str, Any],
        data_source: str,
        execution: dict[str, Any] | None,
        snapshot_id: str | None,
    ) -> int | None:
        symbol = item["symbol"]
        best_params = result.get("best_parameters") or result.get("parameters") or {}
        metrics = _metrics_with_source_trades(
            result.get("best_metrics") or {}, result.get("trades")
        )
        metrics["analysis_candles"] = (
            result.get("candles") if isinstance(result.get("candles"), list) else []
        )
        metrics["analysis_indicator_data"] = (
            result.get("indicator_data") if isinstance(result.get("indicator_data"), dict) else {}
        )
        if isinstance(result.get("strategy_transparency"), dict):
            metrics["analysis_strategy_transparency"] = result["strategy_transparency"]
        metrics["analysis_execution_mode"] = result.get("execution_mode")
        oos_verdict = result.get("oos_verdict")
        if isinstance(oos_verdict, dict):
            metrics["oos_metrics"] = result.get("oos_metrics")
            metrics["oos_verdict"] = oos_verdict
        # Identidade, precisão efetiva e convenções (decisão 12) e o lote de origem.
        asset = result.get("asset") if isinstance(result.get("asset"), dict) else None
        conventions = (
            result.get("conventions") if isinstance(result.get("conventions"), dict) else None
        )
        provenance = (
            result.get("data_provenance")
            if isinstance(result.get("data_provenance"), dict)
            else None
        )
        if provenance is not None and snapshot_id:
            provenance = {**provenance, "snapshot_id": snapshot_id}
        # Fonte única: as chaves ``analysis_*`` (o refresh diário só atualiza essas); favoritos antigos
        # com as chaves sem prefixo seguem lidos como fallback.
        metrics.update(
            data_provenance=provenance,
            batch_id=self.job_id,
            analysis_asset=asset,
            analysis_execution=execution,
            analysis_conventions=conventions,
        )

        parameters = dict(best_params)
        parameters["direction"] = self.direction
        parameters["data_source"] = data_source
        equity = "/" not in symbol
        period_type = self.payload.get("period_type")
        start, end = self.payload.get("start_date"), self.payload.get("end_date")

        db = SessionLocal()
        try:
            if lock_and_find_duplicate(
                db,
                user_id=self.user_id,
                strategy_name=self.template_name,
                symbol=symbol,
                timeframe=self.timeframe,
                period_type=period_type,
                start_date=start,
                end_date=end,
                parameters=parameters,
                data_source=data_source,
                asset=asset,
            ):
                db.rollback()
                logger.info("Batch: skip %s (created concurrently)", symbol)
                return None
            favorite = FavoriteStrategy(
                user_id=self.user_id,
                name=f"{self.template_name} - {symbol} {self.timeframe} (batch)",
                symbol=symbol,
                timeframe=self.timeframe,
                strategy_name=self.template_name,
                parameters=parameters,
                metrics=metrics,
                notes=f"gerado em lote ({self.job_id[:8]})",
                # Ação/ETF sem nível de estrela até o #1122 (decisão 12).
                tier=None if equity else 3,
                start_date=start,
                end_date=end,
                period_type=period_type,
                snapshot_id=snapshot_id,
            )
            db.add(favorite)
            db.flush()
            if snapshot_id:
                from app.services.market_history import snapshots as history_snapshots

                history_snapshots.pin(db, snapshot_id)
            db.commit()
            db.refresh(favorite)
            logger.info("Batch: saved favorite for %s (id=%s)", symbol, favorite.id)
            return int(favorite.id)
        finally:
            db.close()


def _collect_crypto_history(
    symbol: str,
    timeframe: str,
    start: Any,
    end: Any,
    on_progress: Callable[[str, str, int, int | None], None],
) -> None:
    """Coleta a série cripto do tempo gráfico pelo ``HistoryService`` (o que já está guardado fica)."""

    from app.services.market_history.facade import get_history_service, spec_for_request

    service = get_history_service()
    series = service.resolve(spec_for_request(symbol=symbol, timeframe=timeframe))

    def relay(_series: Any, page: int, total: int | None) -> None:
        on_progress("candles", series.physical_timeframe, page, total)

    outcome = service.ensure(series, start or _CRYPTO_DEFAULT_START, end, on_progress=relay)
    if outcome.status == "failed":
        # Como o carregador de hoje: segue com o histórico guardado; sem nada guardado, a execução falha.
        logger.warning(
            "Batch: coleta de %s %s falhou (%s); seguindo com o histórico guardado",
            symbol,
            timeframe,
            outcome.error_code,
        )
