#!/usr/bin/env python3
"""Régua read-only de avaliação das chamadas Jev — Card A do #1025.

Lê o log de diagnóstico do #1015 (``SCALP_JEV_LOG_FILE`` /
``backend/scalp_jev_diagnostic.log``) e junta o realizado a 900 s do OHLCV já
existente (``app.services.ohlcv_storage``).  É **read-only**: não escreve
produto, estado do scalp nem base de dados nova, e não precisa do loop do
scalp a correr (só lê o ficheiro de log e o repositório OHLCV já existente).

O relatório agrega:

* previsão vs realizado em janelas **não sobrepostas** de 900 s;
* acerto das barreiras +35 bp / −28 bp (percurso high/low dos candles);
* segmentação por regime (calmo vs activo): pela **fronteira configurada** de σ
  da janela (``vol_bp``) — a mesma que a decisão usa — e, como referência, pela
  mediana da amostra e pelo predicado do gate de regime
  (``expected_move_bp >= entry_hurdle_bp × 1,5``);
* por faixa de confiança (largura 0,1) e por regime, ``n``, ``n`` com preço,
  **acurácia** (fracção de ciclos com realização assinada positiva) e
  **retorno líquido** (bp) — a acurácia é **reportada**, nunca critério de
  escolha do limiar;
* por regime, a **curva do limiar** sobre a **população elegível** (ciclos de
  janela não sobreposta com resposta que passam `hold`, `jev_late`, `hurdle`,
  `regime` e `toxic_book`) com o nº de ciclos que cada limiar deixa passar, a
  **cobertura**, o ganho esperado e o **retorno líquido esperado**
  (``ganho esperado × cobertura``); o limiar do regime é o ``argmax`` do
  retorno líquido esperado;
* expectancy líquida por bucket de ``score`` e de ``confidence`` e a curva de
  calibração (``confidence`` → |realizado|).

Card #1030: o custo é o round-trip da **taxa real por perna** da conta,
registada com a origem (conta vs fallback conservador); o regime sem amostra
suficiente aparece **fechado** (não opera); se a confiança **não separar**
ciclos bons de ruins o limiar fica **desligado**; a **homogeneidade** da
amostra (versão do modelo e origem da confiança) é declarada e, sem ela, nenhum
limiar é proposto; o **valor em uso** de `CONFIDENCE_MIN` é preservado e
reportado (nunca reescrito por um relatório insuficiente).

Amostra insuficiente é **declarada** (por bucket, por regime e no total) em vez
de concluída — e nesse caso nenhum limiar de confiança é proposto e
`EXIT_TARGET_BP`/`EXIT_STOP_BP`/`HOLD_AFTER_FILL_S` mantêm os valores de produto
(salvo a geometria derivada quando a amostra chega). A régua continua
**read-only** e sem o loop do scalp.

Uso (do worktree do card, venv do source)::

    /srv/apps/dev/criptofarol/source/backend/.venv/bin/python \
        scripts/scalp_jev_eval.py --out <relatorio.md>

O OHLCV é lido com ``DATABASE_URL`` do ambiente; sem ela (ou sem cobertura de
candles para a janela do log) o realizado é declarado indisponível e a amostra
fica insuficiente por falta de preço — nunca se inventa realização.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DEFAULT_LOG_PATH = BACKEND / "scalp_jev_diagnostic.log"

SYMBOL = "BTCUSDT"
# O store OHLCV já existente guarda o par no formato do universo Binance.
OHLCV_SYMBOL = "BTC/USDT"
OHLCV_TIMEFRAMES = ("1m", "5m", "15m", "1h")
HORIZON_S = 900
TARGET_BP = Decimal("35")
STOP_BP = Decimal("-28")
# Taxa maker **por perna** em bp — a mesma unidade de `_fee_terms` (#1025 B).
# O default é o fallback conservador de `_fee_terms` (10 bp/perna → 20 bp de
# round-trip). A banda 12–16 bp do #1015 pressupõe o desconto BNB (≈7,5 bp por
# perna → 15 bp); usa-se `--fee-bp 7.5` nesse caso. Custo e predicado de regime
# usam sempre `2 × taxa` (nunca uma taxa já somada).
DEFAULT_FEE_BP = Decimal("10")
REGIME_SLACK = Decimal("1.5")
# Tecto de conclusão (P3): abaixo disto o relatório declara insuficiência.
MIN_NON_OVERLAPPING_WINDOWS = 30
MIN_BUCKET_TRADES = 20
CONFIDENCE_BUCKET_WIDTH = Decimal("0.1")

# Card #1030: reply-fed gates, in evaluation order (the #1028 ``GATE_ORDER``),
# and the subset that defines the eligible population of a regime — every
# reply-fed gate **except** the confidence gate being calibrated.
GATE_ORDER = ("jev_late", "hold", "low_confidence", "hurdle", "regime", "toxic_book")
ELIGIBILITY_GATES = ("jev_late", "hold", "hurdle", "regime", "toxic_book")
# The late gate is a pure constant of the decision (#1025/#1028).
JEV_LATE_MS = 1500
# Market regime of the window σ (``vol_bp``) against the single configured
# boundary: calm below it, active at or above it.
REGIME_CALM = "calm"
REGIME_ACTIVE = "active"
REGIME_UNKNOWN = "unknown"
# Confidence policy of a regime (mirrors the pure engine of the decision).
CONFIDENCE_POLICY_NUMERIC = "numeric"
CONFIDENCE_POLICY_OFF = "off"
CONFIDENCE_POLICY_CLOSED = "closed"
CONFIDENCE_GATE_OFF = frozenset({"none", "off", "disabled"})
# Value in use while no sufficient report opens a regime (#1025 product
# default). Preserved and reported, never rewritten by the ruler.
DEFAULT_CONFIDENCE_IN_USE = Decimal("0.7")
# Card #1030: the single σ boundary (bp) shared with the decision is read from
# the same configuration the decision uses when the CLI flag is not given.
REGIME_BOUNDARY_ENV = "SCALP_REGIME_BOUNDARY_BP"
# A cycle record carries no call id: it is matched to the return record it
# followed in the same cycle by the timestamp distance (the record is written
# milliseconds after the reply).
CYCLE_JOIN_TOLERANCE_S = 5.0
# Candidatos de alvo/stop (bp) avaliados na derivação da geometria. O par de
# produto (+35/−28) entra primeiro: em empate, a geometria de produto prevalece.
GEOMETRY_TARGET_CANDIDATES_BP = (
    Decimal("20"),
    Decimal("25"),
    Decimal("30"),
    Decimal("35"),
    Decimal("50"),
)
GEOMETRY_STOP_CANDIDATES_BP = (
    Decimal("-14"),
    Decimal("-20"),
    Decimal("-28"),
    Decimal("-35"),
)
_OHLCV_MAX_1M_CANDLES = 20160  # 14 dias de candles de 1 min

EntryRe = re.compile(r"\sscalp jev call entry id=(\S+) state=(\{.*\}) questions=")
ReturnRe = re.compile(r"\sscalp jev call return id=(\S+) (.*)$")
RefusalRe = re.compile(r"\sscalp cycle refused user=(\S+) skip_reason=(\S+)")
# Card #1030: the cycle record (refused or sent) carries the registered verdict
# of every reply-fed gate and the regime/policy fields; the #1015 prefix and the
# ``user=``/``skip_reason=`` adjacency are preserved.
CycleRe = re.compile(r"\sscalp cycle (?:refused|sent) user=(\S+) skip_reason=(\S+)(.*)$")
KVRe = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)")
TimestampRe = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) ")


def _dec(value: Any, default: str = "0") -> Decimal:
    try:
        if value is None:
            return Decimal(default)
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def _token(value: Any) -> Optional[str]:
    """Optional single-token record field (``None``/``None`` string → ``None``)."""
    if value in (None, "None"):
        return None
    return str(value)


def _window_vol_bp(fields: dict[str, str], decision: "Decision") -> Optional[Decimal]:
    """σ of the window the decision used (card #1030).

    Prefers the value the return record carried (the same features the decision
    read) and falls back to the window snapshot of the entry record.
    """
    raw = fields.get("window_vol_bp")
    if raw is None and decision.window:
        raw = decision.window.get("vol_bp")
    if raw is None:
        return None
    try:
        decimal = Decimal(str(raw))
    except Exception:
        return None
    return decimal if decimal.is_finite() else None


def _parse_stamp(raw: str) -> Optional[datetime]:
    try:
        return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S,%f")
    except ValueError:
        return None


def _naive(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    return value.replace(tzinfo=None) if value.tzinfo is not None else value


@dataclass
class Decision:
    """One Jev consult joined to its window snapshot (entry) and reply (return)."""

    call_id: str
    at: datetime
    side: Optional[str] = None
    confidence: Decimal = Decimal("0")
    score: Optional[float] = None
    expected_move_bp: Decimal = Decimal("0")
    latency_ms: Optional[int] = None
    status: Optional[str] = None
    book_toxic: bool = False
    noul: Optional[Decimal] = None
    entry_mid: Optional[Decimal] = None
    spread_bp: Decimal = Decimal("0")
    window: dict[str, Any] = field(default_factory=dict)
    # Card #1030: the return record states the version that answered and the
    # origin of the confidence; ``vol_bp`` is the σ of the window the decision
    # used and ``returned_at`` joins that record to its cycle record.
    model: Optional[str] = None
    confidence_origin: Optional[str] = None
    vol_bp: Optional[Decimal] = None
    returned_at: Optional[datetime] = None
    # Card #1030: registered verdicts of the reply-fed gates (#1028 record),
    # when a cycle record was matched to this decision; ``None`` falls back to
    # the pure #1025 predicates reconstructed from the reply.
    gate_verdicts: Optional[dict[str, str]] = None
    verdict_source: str = "reconstructed"


@dataclass
class Realized:
    """Realized outcome of one decision at the 900 s horizon."""

    price: Optional[Decimal]
    signed_bp: Optional[Decimal]
    abs_bp: Optional[Decimal]
    barrier: str  # "target" | "stop" | "none" | "unknown"


def parse_log(path: Path) -> tuple[list[Decision], dict[str, int], int]:
    """Parse entry/return/refusal records. Read-only; never raises on bad lines.

    Card #1030: the same pass also reads the cycle records (refused/sent) so a
    decision can carry the **registered** verdicts of its reply-fed gates
    (#1028) instead of only the reconstructed #1025 predicates.
    """
    decisions: dict[str, Decision] = {}
    order: list[str] = []
    refusals: dict[str, int] = {}
    cycles: list[dict[str, Any]] = []
    malformed = 0
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if not line.strip():
            continue
        stamp_match = TimestampRe.match(line)
        stamp = _parse_stamp(stamp_match.group(1)) if stamp_match else None
        entry = EntryRe.search(line)
        if entry is not None and stamp is not None:
            call_id, raw_state = entry.group(1), entry.group(2)
            try:
                state = json.loads(raw_state)
            except json.JSONDecodeError:
                malformed += 1
                continue
            touch = state.get("touch") or {}
            window = state.get("window") or {}
            decision = decisions.get(call_id) or Decision(call_id=call_id, at=stamp)
            decision.at = stamp
            decision.entry_mid = _dec(touch.get("mid")) if touch.get("mid") else None
            decision.spread_bp = _dec(touch.get("spread_bp"))
            decision.window = window if isinstance(window, dict) else {}
            if call_id not in decisions:
                order.append(call_id)
            decisions[call_id] = decision
            continue
        returned = ReturnRe.search(line)
        if returned is not None and stamp is not None:
            call_id, rest = returned.group(1), returned.group(2)
            fields = dict(KVRe.findall(rest))
            decision = decisions.get(call_id) or Decision(call_id=call_id, at=stamp)
            decision.side = None if fields.get("side") in (None, "None") else fields.get("side")
            decision.confidence = _dec(fields.get("confidence"))
            decision.expected_move_bp = _dec(fields.get("expected_move_bp"))
            decision.latency_ms = (
                int(fields["latency_ms"]) if fields.get("latency_ms", "").isdigit() else None
            )
            decision.status = fields.get("status")
            decision.book_toxic = str(fields.get("book_toxic", "")).lower() == "true"
            decision.noul = _dec(fields["noul"]) if "noul" in fields else None
            decision.returned_at = stamp
            decision.model = _token(fields.get("model"))
            decision.confidence_origin = _token(fields.get("confidence_origin"))
            decision.vol_bp = _window_vol_bp(fields, decision)
            if fields.get("score") not in (None, "None"):
                try:
                    decision.score = float(fields["score"])
                except ValueError:
                    decision.score = None
            if call_id not in decisions:
                order.append(call_id)
            decisions[call_id] = decision
            continue
        refusal = RefusalRe.search(line)
        if refusal is not None:
            token = refusal.group(2)
            refusals[token] = refusals.get(token, 0) + 1
        cycle = CycleRe.search(line)
        if cycle is not None and stamp is not None:
            fields = dict(KVRe.findall(cycle.group(3)))
            registered = {gate: fields[gate] for gate in GATE_ORDER if gate in fields}
            if registered:
                cycles.append(
                    {
                        "at": stamp,
                        "verdicts": registered,
                        "confidence": (
                            _dec(fields["confidence"]) if "confidence" in fields else None
                        ),
                    }
                )
    parsed = [decisions[call_id] for call_id in order]
    _attach_registered_verdicts(parsed, cycles)
    return parsed, refusals, malformed


def _attach_registered_verdicts(decisions: list[Decision], cycles: list[dict[str, Any]]) -> None:
    """Match each cycle record to the return record of the same cycle (#1030).

    The cycle record carries no call id, so it is matched to the latest return
    record at or before its timestamp within ``CYCLE_JOIN_TOLERANCE_S``,
    preferring an equal confidence value when both carry one. The registered
    verdicts are the authority; a decision without a match keeps the
    reconstructed #1025 predicates (``verdict_source="reconstructed"``).
    """
    if not decisions or not cycles:
        return
    ordered = [decision for decision in decisions if decision.returned_at is not None]
    for cycle in sorted(cycles, key=lambda item: item["at"]):
        within: list[Decision] = []
        for decision in ordered:
            returned_at = decision.returned_at
            if returned_at is None or returned_at > cycle["at"]:
                continue
            if (cycle["at"] - returned_at).total_seconds() <= CYCLE_JOIN_TOLERANCE_S:
                within.append(decision)
        if not within:
            continue
        cycle_confidence = cycle["confidence"]
        matching = [d for d in within if cycle_confidence is None or d.confidence == cycle_confidence]
        best = max(matching or within, key=lambda d: d.returned_at or cycle["at"])
        best.gate_verdicts = dict(cycle["verdicts"])
        best.verdict_source = "registered"


class CandleSeries:
    """Read-only view over already-stored OHLCV candles.

    ``timestamp_utc`` is the candle **open** time: a candle covers
    ``[stamp, stamp + step)``.  Every accessor indexes by that covered
    interval, so the ruler only reads candles that were already **closed** at
    the horizon and never counts the boundary candle (correção N5).
    """

    def __init__(
        self, candles: Sequence[dict[str, Any]], *, step: Optional[timedelta] = None
    ) -> None:
        self.candles: list[tuple[datetime, Decimal, Decimal, Decimal, Decimal]] = []
        for row in candles:
            raw = row.get("timestamp_utc")
            if not raw:
                continue
            try:
                stamp = datetime.fromisoformat(str(raw)).replace(tzinfo=None)
            except ValueError:
                continue
            self.candles.append(
                (
                    stamp,
                    _dec(row.get("open")),
                    _dec(row.get("high")),
                    _dec(row.get("low")),
                    _dec(row.get("close")),
                )
            )
        self.candles.sort(key=lambda item: item[0])
        if step is not None:
            self.step = step
        else:
            gaps = sorted(
                {
                    later[0] - earlier[0]
                    for earlier, later in zip(self.candles, self.candles[1:])
                    if later[0] > earlier[0]
                }
            )
            self.step = gaps[0] if gaps else timedelta(minutes=1)

    def __len__(self) -> int:
        return len(self.candles)

    @property
    def span(self) -> Optional[tuple[datetime, datetime]]:
        if not self.candles:
            return None
        return self.candles[0][0], self.candles[-1][0]

    def last_closed(self, moment: datetime) -> Optional[tuple[datetime, Decimal]]:
        """``(open_time, close)`` of the last candle closed at or before ``moment``."""
        found: Optional[tuple[datetime, Decimal]] = None
        for stamp, _open, _high, _low, close in self.candles:
            if stamp + self.step <= moment:
                found = (stamp, close)
            else:
                break
        return found

    def price_at(self, moment: datetime) -> Optional[Decimal]:
        """Close of the last candle already **closed** at ``moment``.

        Returns ``None`` when the stored coverage ends well before ``moment``
        (a live log can outrun the OHLCV store): a stale candle is never
        reported as the realized price of a later horizon.
        """
        found = self.last_closed(moment)
        if found is None:
            return None
        stamp, close = found
        if moment - (stamp + self.step) > self.step:
            return None
        return close

    def path(self, start: datetime, end: datetime) -> list[tuple[Decimal, Decimal]]:
        """(high, low) of the candles fully **inside** ``[start, end]``.

        A candle only counts when it opened at/after ``start`` (no pre-decision
        movement leaks in) and closed at/before ``end`` (the boundary candle is
        not counted before it closes).
        """
        return [
            (high, low)
            for stamp, _open, high, low, _close in self.candles
            if stamp >= start and stamp + self.step <= end
        ]


def load_candles(*, need_from: datetime, need_to: datetime) -> tuple[CandleSeries, str]:
    """Read the existing OHLCV store (no writes, no new table).

    Picks the finest timeframe already stored that covers the log window; when
    no stored timeframe reaches the window the realized side is declared
    unavailable (never invented).
    """
    if str(BACKEND) not in sys.path:
        sys.path.insert(0, str(BACKEND))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from app.services.ohlcv_storage import MarketOhlcvRepository
    except Exception as exc:  # pragma: no cover - environment without DB settings
        return CandleSeries([]), f"OHLCV indisponível (import: {type(exc).__name__})"
    try:
        repo = MarketOhlcvRepository()
    except Exception as exc:
        return CandleSeries([]), f"OHLCV indisponível (repo: {type(exc).__name__})"
    if not repo.enabled:
        return CandleSeries([]), "OHLCV desativado (sem DATABASE_URL)"
    latest_by_timeframe: dict[str, Optional[datetime]] = {}
    try:
        for timeframe in OHLCV_TIMEFRAMES:
            latest_by_timeframe[timeframe] = _naive(
                repo.get_latest_candle_time(OHLCV_SYMBOL, timeframe)
            )
    except Exception as exc:
        return CandleSeries([]), f"OHLCV falhou na leitura ({type(exc).__name__})"
    need_to_naive = _naive(need_to) or need_to
    need_from_naive = _naive(need_from) or need_from
    chosen: Optional[str] = None
    partial = False
    for timeframe in OHLCV_TIMEFRAMES:
        latest = latest_by_timeframe.get(timeframe)
        if latest is not None and latest >= need_to_naive:
            chosen = timeframe
            break
    if chosen is None:
        # A live log outruns the OHLCV store: keep the finest timeframe that
        # at least reaches the log start and let the per-window pricing
        # declare the windows the store does not cover (partial sample, E2).
        for timeframe in OHLCV_TIMEFRAMES:
            latest = latest_by_timeframe.get(timeframe)
            if latest is not None and latest >= need_from_naive:
                chosen = timeframe
                partial = True
                break
    if chosen is None:
        detail = ", ".join(
            f"{tf}: {'—' if latest_by_timeframe.get(tf) is None else latest_by_timeframe[tf].isoformat(sep=' ')}"
            for tf in OHLCV_TIMEFRAMES
        )
        return (
            CandleSeries([]),
            f"OHLCV {OHLCV_SYMBOL} sem candles que cubram a janela até "
            f"{need_to_naive.isoformat(sep=' ')} (último por timeframe — {detail})",
        )
    minutes = int((need_to_naive - need_from_naive).total_seconds() // 60) + 60
    step_minutes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}[chosen]
    limit = max(1, min(_OHLCV_MAX_1M_CANDLES, minutes // step_minutes + 2))
    try:
        candles = repo.read_recent_candles(OHLCV_SYMBOL, chosen, limit)
    except Exception as exc:
        return CandleSeries([]), f"OHLCV falhou na leitura ({type(exc).__name__})"
    if not candles:
        return CandleSeries([]), f"OHLCV sem candles {OHLCV_SYMBOL} {chosen}"
    note = (
        f"OHLCV {OHLCV_SYMBOL} {chosen} (granularidade {step_minutes} min): "
        f"{len(candles)} candles (limit={limit})"
    )
    if partial:
        latest = latest_by_timeframe.get(chosen)
        note += (
            "; cobertura parcial da janela: o último candle "
            f"{'—' if latest is None else latest.isoformat(sep=' ')} não chega ao fim "
            f"{need_to_naive.isoformat(sep=' ')}"
        )
    return CandleSeries(candles, step=timedelta(minutes=step_minutes)), note


def _barrier_for(
    *,
    side: Optional[str],
    entry: Decimal,
    path: Sequence[tuple[Decimal, Decimal]],
    target_bp: Decimal = TARGET_BP,
    stop_bp: Decimal = STOP_BP,
) -> str:
    """First barrier touched, mirrored by side.

    For a BUY the target sits above the entry and the stop below it; for a
    SELL (short) the geometry is **mirrored**: the target sits below the entry
    and the stop above it (correção E1 — the SELL column was corrupt because
    the levels were not mirrored). The stop counts first on an ambiguous
    candle.
    """
    if side not in {"BUY", "SELL"} or entry <= 0 or not path:
        return "unknown"
    if side == "BUY":
        target = entry * (Decimal("1") + target_bp / Decimal("10000"))
        stop = entry * (Decimal("1") + stop_bp / Decimal("10000"))
    else:
        target = entry * (Decimal("1") - target_bp / Decimal("10000"))
        stop = entry * (Decimal("1") - stop_bp / Decimal("10000"))
    for high, low in path:
        if side == "BUY":
            hit_stop = low <= stop
            hit_target = high >= target
        else:
            hit_stop = high >= stop
            hit_target = low <= target
        if hit_stop:
            return "stop"
        if hit_target:
            return "target"
    return "none"


def realized_for(decision: Decision, series: CandleSeries) -> Realized:
    if decision.entry_mid is None or decision.entry_mid <= 0:
        return Realized(None, None, None, "unknown")
    end = decision.at + timedelta(seconds=HORIZON_S)
    price = series.price_at(end)
    path = series.path(decision.at, end)
    barrier = _barrier_for(side=decision.side, entry=decision.entry_mid, path=path)
    if price is None or price <= 0:
        return Realized(None, None, None, barrier)
    move_bp = (price / decision.entry_mid - Decimal("1")) * Decimal("10000")
    if decision.side == "SELL":
        signed = -move_bp
    elif decision.side == "BUY":
        signed = move_bp
    else:
        signed = None
    return Realized(price, signed, abs(move_bp), barrier)


def non_overlapping(decisions: Iterable[Decision]) -> list[Decision]:
    """Greedy non-overlapping 900 s windows (first decision per window wins)."""
    accepted: list[Decision] = []
    last_at: Optional[datetime] = None
    for decision in sorted(decisions, key=lambda item: item.at):
        if last_at is None or (decision.at - last_at).total_seconds() >= HORIZON_S:
            accepted.append(decision)
            last_at = decision.at
    return accepted


def hurdle_bp(*, fee_bp: Decimal, spread_bp: Decimal) -> Decimal:
    return Decimal("2") * fee_bp + spread_bp


def regime_gate_predicate(*, decision: Decision, fee_bp: Decimal) -> bool:
    """True when the forecast clears `entry_hurdle_bp × 1,5` (active regime)."""
    return (
        decision.expected_move_bp
        >= hurdle_bp(fee_bp=fee_bp, spread_bp=decision.spread_bp) * REGIME_SLACK
    )


def _stats(rows: Sequence[tuple[Decision, Realized]], *, fee_bp: Decimal) -> dict[str, Any]:
    with_price = [(d, r) for d, r in rows if r.signed_bp is not None]
    signed = [r.signed_bp for _d, r in with_price if r.signed_bp is not None]
    realized_abs = [r.abs_bp for _d, r in rows if r.abs_bp is not None]
    barriers = [r.barrier for _d, r in rows]
    round_trip = Decimal("2") * fee_bp
    expectancy = (sum(signed, Decimal("0")) / Decimal(len(signed)) - round_trip) if signed else None
    # Card #1030: accuracy is reported, never the criterion that picks a
    # threshold — the direction was right when the realized signed return at the
    # horizon is positive.
    positive = [value for value in signed if value > 0]
    return {
        "n": len(rows),
        "n_priced": len(signed),
        "n_positive": len(positive),
        "accuracy": (Decimal(len(positive)) / Decimal(len(signed))) if signed else None,
        "n_target": barriers.count("target"),
        "n_stop": barriers.count("stop"),
        "n_none": barriers.count("none"),
        "n_unknown": barriers.count("unknown"),
        "mean_signed_bp": (sum(signed, Decimal("0")) / Decimal(len(signed))) if signed else None,
        "expectancy_net_bp": expectancy,
        "abs_realized_p50": (
            Decimal(str(statistics.median([float(value) for value in realized_abs])))
            if realized_abs
            else None
        ),
    }


def _fmt(value: Optional[Decimal], places: str = "0.01") -> str:
    if value is None:
        return "—"
    return str(Decimal(value).quantize(Decimal(places)))


def _bucket_rows(
    rows: Sequence[tuple[Decision, Realized]], *, key, fee_bp: Decimal
) -> list[tuple[str, dict[str, Any]]]:
    groups: dict[str, list[tuple[Decision, Realized]]] = {}
    for decision, realized in rows:
        label = key(decision)
        if label is None:
            continue
        groups.setdefault(label, []).append((decision, realized))
    return [(label, _stats(group, fee_bp=fee_bp)) for label, group in sorted(groups.items())]


def score_bucket(decision: Decision) -> Optional[str]:
    if decision.score is None:
        return None
    index = max(0, min(9, int(decision.score)))
    return f"score {index}"


def _band_label(floor: Decimal) -> str:
    """Confidence band label for a band's lower edge (width 0,1)."""
    if floor >= Decimal("1"):
        return "[1.0, ∞)"
    return f"[{_fmt(floor, '0.1')}, {_fmt(floor + CONFIDENCE_BUCKET_WIDTH, '0.1')})"


def confidence_bucket(decision: Decision) -> Optional[str]:
    if decision.confidence < 0:
        return None
    return _band_label(confidence_floor(decision.confidence))


def confidence_floor(confidence: Decimal) -> Decimal:
    """Lower edge of the confidence band that contains ``confidence``."""
    low = (confidence / CONFIDENCE_BUCKET_WIDTH).to_integral_value(rounding="ROUND_FLOOR")
    return max(Decimal("0"), low) * CONFIDENCE_BUCKET_WIDTH


def market_regime(decision: Decision, boundary_bp: Optional[Decimal]) -> Optional[str]:
    """Market regime of a decision: σ of its window against the boundary (#1030)."""
    if decision.vol_bp is None or boundary_bp is None:
        return None
    if not decision.vol_bp.is_finite():
        return None
    return REGIME_ACTIVE if decision.vol_bp >= boundary_bp else REGIME_CALM


def passes_other_gates(decision: Decision, *, fee_bp: Decimal) -> bool:
    """Does the reply pass every reply-fed gate **except** confidence? (#1030)

    The registered verdicts of the #1028 record are the authority; when the
    decision has no matched cycle record, the pure #1025 predicates are
    reconstructed from the reply (same rules the decision applies).
    """
    registered = decision.gate_verdicts
    if registered:
        return all(registered.get(gate) == "pass" for gate in ELIGIBILITY_GATES)
    return (
        decision.side in {"BUY", "SELL"}
        and decision.latency_ms is not None
        and decision.latency_ms <= JEV_LATE_MS
        and decision.expected_move_bp > hurdle_bp(fee_bp=fee_bp, spread_bp=decision.spread_bp)
        and regime_gate_predicate(decision=decision, fee_bp=fee_bp)
        and not decision.book_toxic
    )


def eligible_population(
    rows: Sequence[tuple[Decision, Realized]], *, fee_bp: Decimal
) -> tuple[list[tuple[Decision, Realized]], dict[str, int]]:
    """Priced cycles that pass the other reply-fed gates (#1030).

    Returns the eligible rows and how many verdicts came from the registered
    #1028 record vs from the reconstructed #1025 predicates.
    """
    eligible: list[tuple[Decision, Realized]] = []
    sources = {"registered": 0, "reconstructed": 0}
    for decision, realized in rows:
        if realized.signed_bp is None:
            continue
        if not passes_other_gates(decision, fee_bp=fee_bp):
            continue
        eligible.append((decision, realized))
        source = "registered" if decision.gate_verdicts else "reconstructed"
        sources[source] = sources.get(source, 0) + 1
    return eligible, sources


def threshold_curve(
    eligible: Sequence[tuple[Decision, Realized]], *, fee_bp: Decimal
) -> list[dict[str, Any]]:
    """Coverage and expected net return of every candidate threshold (#1030).

    Candidate thresholds are 0 (accept everything) and the lower edge of each
    confidence band present in the eligible population. For each candidate:
    how many cycles it lets pass, the coverage, the expected gain (mean net
    return of the passing cycles) and the expected net return ``gain ×
    coverage``, where the net return of a cycle is its realized signed bp minus
    the round-trip cost ``2 × fee per leg``.
    """
    total = len(eligible)
    if total == 0:
        return []
    round_trip = Decimal("2") * fee_bp
    nets = [(decision, realized.signed_bp - round_trip) for decision, realized in eligible]
    band_counts: dict[Decimal, int] = {}
    for decision, _realized in eligible:
        floor = confidence_floor(decision.confidence)
        band_counts[floor] = band_counts.get(floor, 0) + 1
    candidates = sorted({Decimal("0")} | set(band_counts))
    curve: list[dict[str, Any]] = []
    for threshold in candidates:
        passing = [value for decision, value in nets if decision.confidence >= threshold]
        n_pass = len(passing)
        coverage = Decimal(n_pass) / Decimal(total)
        gain = (sum(passing, Decimal("0")) / Decimal(n_pass)) if n_pass else None
        expected = (gain * coverage) if gain is not None else Decimal("0")
        band_n = band_counts.get(threshold, 0)
        curve.append(
            {
                "threshold": str(threshold),
                "band": _band_label(threshold),
                "n_pass": n_pass,
                "coverage": str(coverage),
                "expected_gain_bp": None if gain is None else str(gain),
                "expected_net_bp": str(expected),
                "band_n_priced": band_n,
                "sufficient": band_n >= MIN_BUCKET_TRADES,
            }
        )
    return curve


def _homogeneity(
    eligible: Sequence[tuple[Decision, Realized]]
) -> tuple[bool, list[str], list[str], int]:
    """Version/origin homogeneity of the sample (#1030, decision 7).

    Returns ``(homogeneous, models, origins, excluded_windows)`` where
    ``excluded_windows`` counts the eligible cycles that do not share the
    dominant ``(model, confidence_origin)`` pair.
    """
    models = sorted({(decision.model or "unknown") for decision, _ in eligible})
    origins = sorted({(decision.confidence_origin or "unknown") for decision, _ in eligible})
    homogeneous = len(models) <= 1 and len(origins) <= 1
    excluded = 0
    if eligible and not homogeneous:
        counts: dict[tuple[str, str], int] = {}
        for decision, _ in eligible:
            pair = (decision.model or "unknown", decision.confidence_origin or "unknown")
            counts[pair] = counts.get(pair, 0) + 1
        dominant = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
        excluded = sum(
            1
            for decision, _ in eligible
            if (decision.model or "unknown", decision.confidence_origin or "unknown") != dominant
        )
    return homogeneous, models, origins, excluded


def regime_analysis(
    eligible: Sequence[tuple[Decision, Realized]],
    *,
    fee_bp: Decimal,
    boundary_bp: Optional[Decimal],
    labels: dict[str, str],
) -> dict[str, Any]:
    """One regime's report: bands, threshold curve, choice, separation (#1030).

    A regime is **closed** when its eligible priced population is below the
    ruler's minimum, when no contributing band reaches the minimum sample, or
    when the sample is not homogeneous. An open regime whose confidence does
    not separate good from bad cycles (no threshold with a strictly positive
    expected net return strictly better than accepting everything) is
    **turned off**.
    """
    stats = _stats(eligible, fee_bp=fee_bp)
    curve = threshold_curve(eligible, fee_bp=fee_bp)
    sufficient = [row for row in curve if row["sufficient"]]
    chosen = None
    if sufficient:
        chosen = max(
            sufficient,
            key=lambda row: (Decimal(row["expected_net_bp"]), -Decimal(row["threshold"])),
        )
    at_zero = next((row for row in curve if Decimal(row["threshold"]) == 0), None)
    expected_zero = Decimal(at_zero["expected_net_bp"]) if at_zero else Decimal("0")
    homogeneous, models, origins, excluded = _homogeneity(eligible)

    closed_reasons: list[str] = []
    if boundary_bp is None:
        closed_reasons.append("fronteira de regime ausente")
    elif stats["n_priced"] < MIN_NON_OVERLAPPING_WINDOWS:
        closed_reasons.append(
            f"população elegível com preço {stats['n_priced']} "
            f"< mínimo de {MIN_NON_OVERLAPPING_WINDOWS}"
        )
    elif not sufficient:
        closed_reasons.append(
            f"nenhuma faixa contribuinte com {MIN_BUCKET_TRADES}+ trades com preço"
        )
    elif not homogeneous:
        closed_reasons.append("amostra não homogénea (versão/origem misturadas)")

    separates: Optional[bool]
    if closed_reasons:
        policy = CONFIDENCE_POLICY_CLOSED
        separates = None
    else:
        best = Decimal(chosen["expected_net_bp"])
        separates = best > 0 and best > expected_zero
        policy = CONFIDENCE_POLICY_NUMERIC if separates else CONFIDENCE_POLICY_OFF

    band_rows = _bucket_rows(eligible, key=confidence_bucket, fee_bp=fee_bp)
    return {
        "label": labels.get("regime", REGIME_UNKNOWN),
        "sample": stats,
        "bands": band_rows,
        "curve": curve,
        "chosen": chosen,
        "expected_net_accept_all_bp": str(expected_zero),
        "separates": separates,
        "policy": policy,
        "closed": policy == CONFIDENCE_POLICY_CLOSED,
        "closed_reasons": closed_reasons,
        "homogeneous": homogeneous,
        "models": models,
        "origins": origins,
        "excluded_windows": excluded,
    }


def _threshold_table(curve: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| limiar | faixa contribuinte | n que passam | cobertura | ganho esperado (bp) | retorno líq. esperado (bp) | amostra da faixa | suficiente |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not curve:
        lines.append("| — | — | 0 | 0 | — | — | 0 | não |")
        return lines
    for row in curve:
        lines.append(
            f"| {row['threshold']} | {row['band']} | {row['n_pass']} | "
            f"{_fmt(Decimal(row['coverage']) * Decimal('100'), '0.1')}% | "
            f"{_fmt(None if row['expected_gain_bp'] is None else Decimal(row['expected_gain_bp']))} | "
            f"{_fmt(Decimal(row['expected_net_bp']))} | {row['band_n_priced']} | "
            f"{'sim' if row['sufficient'] else 'não'} |"
        )
    return lines


def _regime_lines(analysis: dict[str, Any]) -> list[str]:
    label = analysis["label"]
    stats = analysis["sample"]
    lines = [f"#### Regime {label}", ""]
    lines.append(
        f"- amostra elegível: {stats['n']} ciclo(s), **{stats['n_priced']} com preço** "
        f"(acurácia {_fmt((stats['accuracy'] or Decimal('0')) * Decimal('100'), '0.1')}%, "
        f"retorno líq. médio {_fmt(stats['expectancy_net_bp'])} bp)"
    )
    lines.append(
        f"- homogeneidade: {'homogénea' if analysis['homogeneous'] else 'NÃO homogénea'}"
        f" (modelos: {', '.join(analysis['models']) or '—'}; origens: "
        f"{', '.join(analysis['origins']) or '—'}; janelas excluídas: "
        f"{analysis['excluded_windows']})"
    )
    lines.append(
        f"- aceitar tudo (limiar 0) dá retorno líquido esperado de "
        f"{_fmt(Decimal(analysis['expected_net_accept_all_bp']))} bp"
    )
    if analysis["closed"]:
        lines.append(
            "- **regime fechado** (não opera): "
            + "; ".join(analysis["closed_reasons"])
        )
    elif analysis["separates"]:
        chosen = analysis["chosen"]
        lines.append(
            f"- **separa** ciclos bons de ruins: limiar `{chosen['threshold']}` "
            f"(faixa {chosen['band']}, {chosen['band_n_priced']} trades com preço) — "
            f"deixa passar {chosen['n_pass']} ciclo(s) com cobertura de "
            f"{_fmt(Decimal(chosen['coverage']) * Decimal('100'), '0.1')}% e retorno líquido "
            f"esperado de {_fmt(Decimal(chosen['expected_net_bp']))} bp"
        )
        lines.append(f"- política do regime: `{analysis['policy']}`")
    else:
        lines.append(
            "- **a confiança não separa** ciclos bons de ruins nesta amostra: o limiar é "
            "**desligado** e a decisão passa a previsão × custo × regime"
        )
        lines.append(f"- política do regime: `{analysis['policy']}`")
    lines.append("")
    lines.append("Faixas de confiança (acurácia **reportada**, nunca critério de escolha):")
    lines.append("")
    lines.extend(_bucket_table("Por `confidence` (elegível do regime)", analysis["bands"]))
    lines.append("Curva do limiar (ganho esperado × cobertura):")
    lines.append("")
    lines.extend(_threshold_table(analysis["curve"]))
    lines.append("")
    return lines


def _bucket_table(title: str, rows: list[tuple[str, dict[str, Any]]]) -> list[str]:
    lines = [
        f"#### {title}",
        "",
        "| bucket | n | n com preço | acurácia | retorno líq. (bp) | alvo | stop | sem barreira | insuficiente |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for label, stats in rows:
        insufficient = "sim" if stats["n_priced"] < MIN_BUCKET_TRADES else "não"
        accuracy = stats.get("accuracy")
        lines.append(
            f"| {label} | {stats['n']} | {stats['n_priced']} | "
            f"{_fmt(None if accuracy is None else Decimal(accuracy) * Decimal('100'), '0.1')}% | "
            f"{_fmt(stats['expectancy_net_bp'])} | "
            f"{stats['n_target']} | {stats['n_stop']} | {stats['n_none']} | {insufficient} |"
        )
    if not rows:
        lines.append("| — | 0 | 0 | — | — | 0 | 0 | 0 | sim |")
    lines.append("")
    return lines


def _geometry_expectancy(
    rows: Sequence[tuple[Decision, Realized]],
    paths: dict[str, Sequence[tuple[Decimal, Decimal]]],
    *,
    target_bp: Decimal,
    stop_bp: Decimal,
    fee_bp: Decimal,
) -> tuple[Optional[Decimal], int]:
    """Net expectancy of a candidate geometry over the priced windows."""
    pnls: list[Decimal] = []
    for decision, realized in rows:
        path = paths.get(decision.call_id)
        if path is None or decision.entry_mid is None or decision.entry_mid <= 0:
            continue
        barrier = _barrier_for(
            side=decision.side,
            entry=decision.entry_mid,
            path=path,
            target_bp=target_bp,
            stop_bp=stop_bp,
        )
        if barrier == "target":
            pnls.append(target_bp)
        elif barrier == "stop":
            pnls.append(stop_bp)
        elif barrier == "none" and realized.signed_bp is not None:
            pnls.append(realized.signed_bp)
    if not pnls:
        return None, 0
    gross = sum(pnls, Decimal("0")) / Decimal(len(pnls))
    return gross - Decimal("2") * fee_bp, len(pnls)


def _derive_geometry(
    rows: Sequence[tuple[Decision, Realized]],
    paths: dict[str, Sequence[tuple[Decimal, Decimal]]],
    *,
    fee_bp: Decimal,
) -> Optional[tuple[Decimal, Decimal, Decimal]]:
    """Best candidate geometry with positive net expectancy, or ``None``.

    Evaluated only on a sufficient sample (``MIN_NON_OVERLAPPING_WINDOWS``
    priced windows); the product geometry (+35/−28) is tried first so a tie
    keeps it. Without a candidate that clears the round-trip cost the ruler
    declares the geometry not derived.
    """
    if len(rows) < MIN_NON_OVERLAPPING_WINDOWS:
        return None
    candidates = [(TARGET_BP, STOP_BP)] + [
        (target, stop)
        for target in GEOMETRY_TARGET_CANDIDATES_BP
        for stop in GEOMETRY_STOP_CANDIDATES_BP
    ]
    best: Optional[tuple[Decimal, Decimal, Decimal]] = None
    for target_bp, stop_bp in candidates:
        expectancy, n = _geometry_expectancy(
            rows, paths, target_bp=target_bp, stop_bp=stop_bp, fee_bp=fee_bp
        )
        if expectancy is None or n < MIN_NON_OVERLAPPING_WINDOWS:
            continue
        if best is None or expectancy > best[2]:
            best = (target_bp, stop_bp, expectancy)
    if best is None or best[2] <= 0:
        return None
    return best


def _break_even_hit_rate(*, target_bp: Decimal, stop_bp: Decimal, fee_bp: Decimal) -> Decimal:
    """Target hit rate a barrier pair needs just to pay the round-trip cost."""
    risk = abs(stop_bp)
    gain = abs(target_bp)
    if gain + risk <= 0:
        return Decimal("1")
    return (Decimal("2") * fee_bp + risk) / (gain + risk)


def build_report(
    *,
    log_path: Path,
    decisions: list[Decision],
    refusals: dict[str, int],
    malformed: int,
    series: CandleSeries,
    ohlcv_note: str,
    fee_bp: Decimal,
    # Card #1030: the single σ boundary shared with the decision; absent keeps
    # both regimes closed (fail closed). The fee source and the value in use are
    # declared so the report never hides them.
    regime_boundary_bp: Optional[Decimal] = None,
    fee_source: str = "fallback",
    confidence_in_use: Optional[Decimal] = DEFAULT_CONFIDENCE_IN_USE,
) -> tuple[str, dict[str, Any]]:
    # Card #1030: the conservative fallback while the real per-leg fee of the
    # account was not given is a **defect of the report**, never a neutral
    # number (spec ``scalp-jev-net-return-ruler``).
    fee_is_fallback = fee_source == "fallback"
    realized = [(decision, realized_for(decision, series)) for decision in decisions]
    windows = non_overlapping(decisions)
    window_ids = {decision.call_id for decision in windows}
    realized_windows = [(d, r) for d, r in realized if d.call_id in window_ids]
    # Card #1030: eligible population per regime (priced cycles that pass every
    # reply-fed gate except confidence), the threshold curve of each regime and
    # the policy the ruler proposes for it (numeric / off / closed).
    eligible_all, verdict_sources = eligible_population(realized_windows, fee_bp=fee_bp)
    regime_labels = {
        REGIME_CALM: (
            f"calmo (vol_bp < {_fmt(regime_boundary_bp)})"
            if regime_boundary_bp is not None
            else "calmo"
        ),
        REGIME_ACTIVE: (
            f"activo (vol_bp ≥ {_fmt(regime_boundary_bp)})"
            if regime_boundary_bp is not None
            else "activo"
        ),
    }
    regime_analyses = {
        regime: regime_analysis(
            [(d, r) for d, r in eligible_all if market_regime(d, regime_boundary_bp) == regime],
            fee_bp=fee_bp,
            boundary_bp=regime_boundary_bp,
            labels={"regime": regime_labels[regime]},
        )
        for regime in (REGIME_CALM, REGIME_ACTIVE)
    }
    homogeneous_all, models_all, origins_all, excluded_all = _homogeneity(eligible_all)
    # Percurso high/low de cada janela não sobreposta — usado para reavaliar as
    # barreiras de cada candidato de geometria (E4).
    paths = {
        decision.call_id: series.path(decision.at, decision.at + timedelta(seconds=HORIZON_S))
        for decision in windows
    }
    span = None
    if decisions:
        span = (min(d.at for d in decisions), max(d.at for d in decisions))
    # Card #1030: ``None`` means the single gate was explicitly removed
    # (#1025 C): the value in use is reported as ``off``, never rewritten.
    confidence_in_use_token = "off" if confidence_in_use is None else _fmt(confidence_in_use)
    summary: dict[str, Any] = {
        "log": str(log_path),
        "calls_returned": sum(1 for d in decisions if d.status is not None),
        "calls_entered": sum(1 for d in decisions if d.entry_mid is not None),
        "malformed_records": malformed,
        "windows_raw": len(decisions),
        "windows_non_overlapping": len(windows),
        "min_non_overlapping_windows": MIN_NON_OVERLAPPING_WINDOWS,
        "min_bucket_trades": MIN_BUCKET_TRADES,
        "ohlcv": ohlcv_note,
        "ohlcv_candles": len(series),
        "refusals": dict(sorted(refusals.items())),
        "insufficient": True,
        "confidence_max": str(max((d.confidence for d in decisions), default=Decimal("0"))),
        "insufficient_reasons": [],
        # Card #1030: fee used and its source; the single σ boundary shared with
        # the decision (``None`` = absent, both regimes closed); the value in use
        # preserved when no sufficient report opens a regime.
        "fee_bp": str(fee_bp),
        "fee_source": fee_source,
        "fee_source_defect": fee_is_fallback,
        "regime_boundary_bp": None if regime_boundary_bp is None else str(regime_boundary_bp),
        "confidence_in_use": confidence_in_use_token,
        "eligible_population": {"n": len(eligible_all), "verdict_sources": verdict_sources},
        "homogeneity": {
            "homogeneous": homogeneous_all,
            "models": models_all,
            "origins": origins_all,
            "excluded_windows": excluded_all,
        },
        "regimes": {
            regime: {
                "label": analysis["label"],
                "sample": analysis["sample"],
                "bands": {label: stats for label, stats in analysis["bands"]},
                "curve": analysis["curve"],
                "chosen": analysis["chosen"],
                "expected_net_accept_all_bp": analysis["expected_net_accept_all_bp"],
                "separates": analysis["separates"],
                "policy": analysis["policy"],
                "closed": analysis["closed"],
                "closed_reasons": analysis["closed_reasons"],
                "homogeneous": analysis["homogeneous"],
                "models": analysis["models"],
                "origins": analysis["origins"],
                "excluded_windows": analysis["excluded_windows"],
            }
            for regime, analysis in regime_analyses.items()
        },
        "suggested_exit_target_bp": None,
        "suggested_exit_stop_bp": None,
        # A geometria é derivada da régua **só** com amostra suficiente (>= 30
        # janelas com preço) e um candidato com expectancy líquida positiva;
        # sem isso, os valores actuais são *defaults de produto* explicitamente
        # não derivados (E4).
        "exit_geometry_derived": False,
        "product_exit_target_bp": str(TARGET_BP),
        "product_exit_stop_bp": str(STOP_BP),
    }
    reasons: list[str] = summary["insufficient_reasons"]
    if not decisions:
        reasons.append("log ausente/vazio: nenhuma chamada Jev registada")
    if malformed:
        reasons.append(f"{malformed} registo(s) `call entry` ilegível(is)")
    if not series:
        reasons.append(f"realizado indisponível: {ohlcv_note}")
    if len(windows) < MIN_NON_OVERLAPPING_WINDOWS:
        reasons.append(
            f"{len(windows)} janela(s) não sobreposta(s) de {HORIZON_S} s "
            f"< mínimo de {MIN_NON_OVERLAPPING_WINDOWS}"
        )
    insufficient_regimes = False
    stats_all = _stats(realized_windows, fee_bp=fee_bp)
    if stats_all["n_priced"] < MIN_NON_OVERLAPPING_WINDOWS:
        # E2: a insuficiência tem de olhar a contagem de janelas **com preço**
        # (`n_priced`), não só a lista de candles — com cobertura parcial
        # (OHLCV que não chega ao fim da janela) a lista pode existir e a
        # amostra não ter preço nenhum.
        reasons.append(
            f"{stats_all['n_priced']} janela(s) com preço (`n_priced`) "
            f"< mínimo de {MIN_NON_OVERLAPPING_WINDOWS}"
        )

    # Regime segmentation: window sigma (vol_bp) median split and gate predicate.
    vol_values = [
        _dec(d.window.get("vol_bp"))
        for d, _r in realized_windows
        if d.window.get("vol_bp") is not None
    ]
    sigma_mid = (
        Decimal(str(statistics.median([float(v) for v in vol_values]))) if vol_values else None
    )
    by_sigma: list[tuple[str, dict[str, Any]]] = []
    if sigma_mid is not None:
        calm = [(d, r) for d, r in realized_windows if _dec(d.window.get("vol_bp")) < sigma_mid]
        active = [(d, r) for d, r in realized_windows if _dec(d.window.get("vol_bp")) >= sigma_mid]
        by_sigma = [
            (f"calmo (vol_bp < {_fmt(sigma_mid)})", _stats(calm, fee_bp=fee_bp)),
            (f"activo (vol_bp ≥ {_fmt(sigma_mid)})", _stats(active, fee_bp=fee_bp)),
        ]
        insufficient_regimes = any(
            stats["n_priced"] < MIN_BUCKET_TRADES for _label, stats in by_sigma
        )
    by_predicate = [
        (
            "calmo (previsão < hurdle × 1,5)",
            _stats(
                [
                    (d, r)
                    for d, r in realized_windows
                    if not regime_gate_predicate(decision=d, fee_bp=fee_bp)
                ],
                fee_bp=fee_bp,
            ),
        ),
        (
            "activo (previsão ≥ hurdle × 1,5)",
            _stats(
                [
                    (d, r)
                    for d, r in realized_windows
                    if regime_gate_predicate(decision=d, fee_bp=fee_bp)
                ],
                fee_bp=fee_bp,
            ),
        ),
    ]

    score_rows = _bucket_rows(realized_windows, key=score_bucket, fee_bp=fee_bp)
    confidence_rows = _bucket_rows(realized_windows, key=confidence_bucket, fee_bp=fee_bp)
    # E2: uma amostra só é suficiente quando as **janelas com preço**
    # (`n_priced`) chegam ao mínimo, não apenas as janelas não sobrepostas.
    sample_sufficient = (
        len(windows) >= MIN_NON_OVERLAPPING_WINDOWS
        and stats_all["n_priced"] >= MIN_NON_OVERLAPPING_WINDOWS
    )
    # E4: com amostra suficiente a régua volta a **derivar** a geometria
    # alvo/stop das barreiras reais — candidatos avaliados por expectancy
    # líquida com a taxa maker **por perna** (round-trip = 2 × taxa). Sem
    # candidato que pague o round-trip, ou sem amostra, `suggested_exit_*`
    # fica a `None` e a geometria são os defaults de produto, explicitamente
    # não derivados.
    if sample_sufficient:
        geometry = _derive_geometry(realized_windows, paths, fee_bp=fee_bp)
        if geometry is not None:
            target_bp, stop_bp, expectancy = geometry
            summary["suggested_exit_target_bp"] = str(target_bp)
            summary["suggested_exit_stop_bp"] = str(stop_bp)
            summary["exit_geometry_derived"] = True
            summary["exit_geometry_expectancy_bp"] = str(expectancy)
            summary["exit_geometry_break_even_hit_rate"] = str(
                _break_even_hit_rate(target_bp=target_bp, stop_bp=stop_bp, fee_bp=fee_bp)
            )
    summary["insufficient"] = bool(reasons)
    summary["insufficient_regimes"] = insufficient_regimes
    summary["stats"] = stats_all

    lines: list[str] = []
    lines.append("# Card A — régua Jev (read-only)")
    lines.append("")
    lines.append(f"- log: `{log_path}`")
    lines.append(f"- OHLCV: {ohlcv_note}")
    if span is not None:
        minutes = (span[1] - span[0]).total_seconds() / 60.0
        lines.append(
            f"- janela do log: {span[0].isoformat(sep=' ')} → {span[1].isoformat(sep=' ')} "
            f"({minutes:.1f} min)"
        )
    lines.append(
        f"- chamadas: {summary['calls_entered']} com janela / {summary['calls_returned']} com retorno"
        + (f" ({malformed} ilegíveis)" if malformed else "")
    )
    lines.append(
        f"- janelas de {HORIZON_S} s: {summary['windows_raw']} decisões, "
        f"**{summary['windows_non_overlapping']} não sobrepostas**"
    )
    lines.append(f"- confiança máxima observada: {summary['confidence_max']}")
    lines.append(
        f"- custo por round-trip considerado: 2 × {_fmt(fee_bp)} bp = {_fmt(2 * fee_bp)} bp"
    )
    lines.append(
        f"- taxa maker por perna: {_fmt(fee_bp)} bp (origem: **{fee_source}**)"
        + (
            " — **defeito do relatório**: a taxa real por perna da conta não foi "
            "fornecida; o retorno líquido usa o fallback conservador e é uma estimativa."
            if fee_is_fallback
            else ""
        )
    )
    lines.append(
        "- fronteira de regime (σ, bp): "
        + (
            _fmt(regime_boundary_bp)
            if regime_boundary_bp is not None
            else "**ausente** — ambos os regimes fechados (falha fechada)"
        )
    )
    lines.append(
        f"- valor em uso preservado: `CONFIDENCE_MIN` = {confidence_in_use_token} "
        "— reportado, nunca reescrito por um relatório insuficiente"
    )
    lines.append("")
    lines.append("## Previsão vs realizado (janelas não sobrepostas)")
    lines.append("")
    lines.append(
        "| n | n com preço | alvo +35 bp | stop −28 bp | sem barreira | média assinada (bp) | expectancy líq. (bp) | |realizado| p50 (bp) |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    lines.append(
        f"| {stats_all['n']} | {stats_all['n_priced']} | {stats_all['n_target']} | "
        f"{stats_all['n_stop']} | {stats_all['n_none']} | {_fmt(stats_all['mean_signed_bp'])} | "
        f"{_fmt(stats_all['expectancy_net_bp'])} | {_fmt(stats_all['abs_realized_p50'])} |"
    )
    lines.append("")
    lines.append("## Regime")
    lines.append("")
    lines.extend(_bucket_table("Por σ da janela (`vol_bp`)", by_sigma))
    lines.extend(
        _bucket_table(
            "Pelo predicado do gate (`expected_move_bp ≥ entry_hurdle_bp × 1,5`)", by_predicate
        )
    )
    lines.append("## Limiar por regime (retorno líquido esperado × cobertura)")
    lines.append("")
    lines.append(
        "População elegível (passa `hold`, `jev_late`, `hurdle`, `regime` e `toxic_book`): "
        f"**{len(eligible_all)}** ciclo(s) com preço — veredictos registados "
        f"{verdict_sources.get('registered', 0)}, reconstruídos "
        f"{verdict_sources.get('reconstructed', 0)}."
    )
    lines.append(
        "Homogeneidade da amostra elegível: "
        f"{'homogénea' if homogeneous_all else '**NÃO homogénea**'} "
        f"(modelos: {', '.join(models_all) or '—'}; origens: {', '.join(origins_all) or '—'}; "
        f"janelas excluídas: {excluded_all}). Sem homogeneidade não é proposto limiar."
    )
    lines.append("")
    for regime in (REGIME_CALM, REGIME_ACTIVE):
        lines.extend(_regime_lines(regime_analyses[regime]))
    lines.append("## Buckets")
    lines.append("")
    lines.extend(_bucket_table("Por `score` de `expected_move_bp`", score_rows))
    lines.extend(_bucket_table("Por `confidence`", confidence_rows))
    lines.append("## Curva de calibração (`confidence` → |realizado|)")
    lines.append("")
    lines.append("| confidence | n | |realizado| p50 (bp) | |realizado| médio (bp) |")
    lines.append("| --- | --- | --- | --- |")
    for label, stats in confidence_rows:
        rows = [
            r.abs_bp
            for d, r in realized_windows
            if confidence_bucket(d) == label and r.abs_bp is not None
        ]
        mean_abs = Decimal(str(statistics.mean([float(v) for v in rows]))) if rows else None
        lines.append(
            f"| {label} | {len(rows)} | {_fmt(stats['abs_realized_p50'])} | {_fmt(mean_abs)} |"
        )
    lines.append("")
    lines.append("## Recusas registadas no log")
    lines.append("")
    if refusals:
        lines.append("| skip_reason | n |")
        lines.append("| --- | --- |")
        for token, count in sorted(refusals.items()):
            lines.append(f"| {token} | {count} |")
    else:
        lines.append("Sem recusas registadas.")
    lines.append("")
    lines.append("## Declaração / gate")
    lines.append("")
    policy_lines = [
        f"- regime `{regime}`: política `{regime_analyses[regime]['policy']}`"
        + (
            f" — limiar {regime_analyses[regime]['chosen']['threshold']}"
            if regime_analyses[regime]["policy"] == CONFIDENCE_POLICY_NUMERIC
            else (
                " — desligado (a confiança não separa; decisão por previsão × custo × regime)"
                if regime_analyses[regime]["policy"] == CONFIDENCE_POLICY_OFF
                else " — fechado (não opera): "
                + "; ".join(regime_analyses[regime]["closed_reasons"])
            )
        )
        for regime in (REGIME_CALM, REGIME_ACTIVE)
    ]
    if reasons:
        lines.append("**Amostra insuficiente** — nenhum limiar ou geometria é proposto:")
        lines.append("")
        for reason in reasons:
            lines.append(f"- {reason}")
        if insufficient_regimes:
            lines.append(f"- buckets/regimes com menos de {MIN_BUCKET_TRADES} trades com preço")
        lines.append("")
        lines.append(
            "Consequência: o valor em uso de `CONFIDENCE_MIN` "
            f"({confidence_in_use_token}) é **preservado e reportado**; as políticas por "
            "regime ficam `fechado` (o bot **não opera**) enquanto o relatório for insuficiente. "
            "`EXIT_TARGET_BP`/`EXIT_STOP_BP` mantêm os valores actuais e `HOLD_AFTER_FILL_S` "
            "fica nos 900 s de produto. O motivo fica registado na evidência."
        )
    else:
        lines.append("Amostra suficiente na régua: proposta")
        lines.append("")
        if summary["exit_geometry_derived"]:
            target_bp = Decimal(summary["suggested_exit_target_bp"])
            stop_bp = Decimal(summary["suggested_exit_stop_bp"])
            break_even = Decimal(summary["exit_geometry_break_even_hit_rate"])
            expectancy = Decimal(summary["exit_geometry_expectancy_bp"])
            lines.append(
                f"- geometria: `EXIT_TARGET_BP` = {_fmt(target_bp)} e `EXIT_STOP_BP` = "
                f"{_fmt(stop_bp)} — **derivada** da amostra (candidato com expectancy líquida "
                f"de {_fmt(expectancy)} bp e hit-rate de break-even "
                f"{_fmt(break_even * Decimal('100'))}% com a taxa maker de {_fmt(fee_bp)} bp/perna)"
            )
        else:
            lines.append(
                f"- geometria: `EXIT_TARGET_BP` = {_fmt(TARGET_BP)} e `EXIT_STOP_BP` = "
                f"{_fmt(STOP_BP)} são **defaults de produto** (`EXIT_TARGET_BP`/`EXIT_STOP_BP`), "
                "**não derivados desta régua** — nenhum candidato de barreira paga o "
                "round-trip com esta amostra"
            )
        lines.append("- `HOLD_AFTER_FILL_S` = 900 s (valor de produto, fora da recalibração)")
    lines.append("")
    lines.append("### Política de confiança por regime (card #1030)")
    lines.append("")
    lines.extend(policy_lines)
    lines.append(
        "- nenhum valor numérico é adoptado sem relatório suficiente; reverter = repor a "
        "configuração por regime"
    )
    lines.append("")
    return "\n".join(lines), summary


def _confidence_in_use(raw: Optional[str]) -> Optional[Decimal]:
    """The single ``CONFIDENCE_MIN`` value in use, reported (card #1030).

    Reads the CLI value or ``SCALP_CONFIDENCE_MIN`` with the same fail-closed
    rules as the decision: absent falls to the product default, a turned-off
    token is reported as ``off`` (``None``) and an invalid value falls to the
    product default. Never a proposal — the value is preserved.
    """
    candidate = raw if raw is not None else os.getenv("SCALP_CONFIDENCE_MIN")
    if candidate is None or not str(candidate).strip():
        return DEFAULT_CONFIDENCE_IN_USE
    token = str(candidate).strip()
    if token.lower() in CONFIDENCE_GATE_OFF:
        return None
    try:
        value = Decimal(token)
    except Exception:
        return DEFAULT_CONFIDENCE_IN_USE
    if not value.is_finite() or value < 0 or value > 1:
        return DEFAULT_CONFIDENCE_IN_USE
    return value


def _non_negative_boundary(raw: Optional[str]) -> Optional[Decimal]:
    """Parse a σ boundary (bp) with the decision's fail-closed rules."""
    if raw is None or not str(raw).strip():
        return None
    try:
        value = Decimal(str(raw).strip())
    except Exception:
        return None
    if not value.is_finite() or value < 0:
        return None
    return value


def _regime_boundary_bp(raw: Optional[str]) -> Optional[Decimal]:
    """The single σ boundary (bp) shared with the decision (card #1030).

    Uses the CLI value when given; otherwise reads ``SCALP_REGIME_BOUNDARY_BP``
    — the same configuration the decision consumes — with the same fail-closed
    rules. When both are present and diverge the CLI value wins and the
    divergence is warned explicitly: the ruler never silently segments a
    population the bot does not trade. Absent/invalid keeps both regimes closed.
    """
    flag = None if raw is None else str(raw).strip()
    env_raw = (os.getenv(REGIME_BOUNDARY_ENV) or "").strip()
    if flag:
        value = _non_negative_boundary(flag)
        env_value = _non_negative_boundary(env_raw)
        if env_raw and env_value != value:
            print(
                f"AVISO: --regime-boundary-bp={flag} diverge de "
                f"{REGIME_BOUNDARY_ENV}={env_raw} (a decisão usa {env_raw}); "
                "a régua usa o valor do flag.",
                file=sys.stderr,
            )
        return value
    return _non_negative_boundary(env_raw)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--log",
        default=None,
        help="log de diagnóstico do #1015 (default: SCALP_JEV_LOG_FILE ou backend/scalp_jev_diagnostic.log)",
    )
    parser.add_argument("--fee-bp", default=str(DEFAULT_FEE_BP), help="taxa maker por perna em bp")
    parser.add_argument(
        "--fee-source",
        choices=("account", "fallback"),
        default="fallback",
        help="origem da taxa: conta real ou fallback conservador (default)",
    )
    parser.add_argument(
        "--regime-boundary-bp",
        default=None,
        help="fronteira única de regime (σ da janela, bp) partilhada com a decisão "
        "(default: SCALP_REGIME_BOUNDARY_BP)",
    )
    parser.add_argument(
        "--confidence-in-use",
        default=None,
        help="valor em uso de CONFIDENCE_MIN (default: SCALP_CONFIDENCE_MIN ou 0.7)",
    )
    parser.add_argument("--json", action="store_true", help="imprime também o sumário JSON")
    parser.add_argument("--out", default=None, help="grava o relatório markdown neste caminho")
    args = parser.parse_args(argv)

    log_path = Path(args.log or os.getenv("SCALP_JEV_LOG_FILE") or DEFAULT_LOG_PATH)
    fee_bp = _dec(args.fee_bp, str(DEFAULT_FEE_BP))
    # Card #1030: the flag, else the boundary the decision uses (env), else
    # absent → both regimes closed (fail closed).
    regime_boundary_bp = _regime_boundary_bp(args.regime_boundary_bp)
    confidence_in_use = _confidence_in_use(args.confidence_in_use)

    def _build(decisions, refusals, malformed, series, ohlcv_note):
        return build_report(
            log_path=log_path,
            decisions=decisions,
            refusals=refusals,
            malformed=malformed,
            series=series,
            ohlcv_note=ohlcv_note,
            fee_bp=fee_bp,
            regime_boundary_bp=regime_boundary_bp,
            fee_source=args.fee_source,
            confidence_in_use=confidence_in_use,
        )

    if not log_path.exists():
        series, ohlcv_note = CandleSeries([]), "OHLCV não consultado (log ausente)"
        report, summary = _build([], {}, 0, series, ohlcv_note)
        report = f"> **Log ausente**: `{log_path}` não existe.\n\n" + report
    else:
        decisions, refusals, malformed = parse_log(log_path)
        if decisions:
            need_from = min(d.at for d in decisions)
            need_to = max(d.at for d in decisions) + timedelta(seconds=HORIZON_S)
        else:
            need_from = need_to = datetime.utcnow()
        series, ohlcv_note = load_candles(need_from=need_from, need_to=need_to)
        report, summary = _build(decisions, refusals, malformed, series, ohlcv_note)

    print(report)
    if args.json:
        print("```json")
        print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
        print("```")
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
