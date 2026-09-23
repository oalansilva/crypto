#!/usr/bin/env python3
"""Régua read-only de avaliação das chamadas Jev — Card A do #1025.

Lê o log de diagnóstico do #1015 (``SCALP_JEV_LOG_FILE`` /
``backend/scalp_jev_diagnostic.log``) e junta o realizado a 900 s do OHLCV já
existente (``app.services.ohlcv_storage``).  É **read-only**: não escreve
produto, estado do scalp nem base de dados nova, e não precisa do loop do
scalp a correr (só lê o ficheiro de log e o repositório OHLCV já existente).

O relatório agrega:

* previsão vs realizado em janelas **não sobrepostas** de 900 s;
* segmentação por regime (calmo vs activo): por σ da janela (``vol_bp``) e pelo
  predicado do gate de regime (``expected_move_bp >= entry_hurdle_bp × 1,5``);
* acerto das barreiras +35 bp / −28 bp (percurso high/low dos candles);
* expectancy líquida por bucket de ``score`` e de ``confidence``;
* curva de calibração (``confidence`` → |realizado|).

Amostra insuficiente é **declarada** (por bucket, por regime e no total) em vez
de concluída — e nesse caso nenhum valor de `CONFIDENCE_MIN`,
`EXIT_TARGET_BP`, `EXIT_STOP_BP` ou `HOLD_AFTER_FILL_S` é proposto. Com amostra
suficiente a régua propõe `CONFIDENCE_MIN` (bucket positivo mais baixo) e a
**geometria** de alvo/stop derivada das barreiras reais da amostra (break-even
das barreiras + expectancy líquida por candidato, com a taxa maker **por
perna**); sem amostra, `EXIT_TARGET_BP` / `EXIT_STOP_BP` ficam como *defaults de
produto*, explicitamente não derivados.

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
KVRe = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)")
TimestampRe = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) ")


def _dec(value: Any, default: str = "0") -> Decimal:
    try:
        if value is None:
            return Decimal(default)
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


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


@dataclass
class Realized:
    """Realized outcome of one decision at the 900 s horizon."""

    price: Optional[Decimal]
    signed_bp: Optional[Decimal]
    abs_bp: Optional[Decimal]
    barrier: str  # "target" | "stop" | "none" | "unknown"


def parse_log(path: Path) -> tuple[list[Decision], dict[str, int], int]:
    """Parse entry/return/refusal records. Read-only; never raises on bad lines."""
    decisions: dict[str, Decision] = {}
    order: list[str] = []
    refusals: dict[str, int] = {}
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
    return [decisions[call_id] for call_id in order], refusals, malformed


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
    return {
        "n": len(rows),
        "n_priced": len(signed),
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


def confidence_bucket(decision: Decision) -> Optional[str]:
    if decision.confidence < 0:
        return None
    low = (decision.confidence / CONFIDENCE_BUCKET_WIDTH).to_integral_value(rounding="ROUND_FLOOR")
    low = max(Decimal("0"), low) * CONFIDENCE_BUCKET_WIDTH
    if low >= Decimal("1"):
        return "[1.0, ∞)"
    return f"[{_fmt(low, '0.1')}, {_fmt(low + CONFIDENCE_BUCKET_WIDTH, '0.1')})"


def _bucket_table(title: str, rows: list[tuple[str, dict[str, Any]]]) -> list[str]:
    lines = [
        f"#### {title}",
        "",
        "| bucket | n | n com preço | expectancy líq. (bp) | alvo | stop | sem barreira | insuficiente |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for label, stats in rows:
        insufficient = "sim" if stats["n_priced"] < MIN_BUCKET_TRADES else "não"
        lines.append(
            f"| {label} | {stats['n']} | {stats['n_priced']} | {_fmt(stats['expectancy_net_bp'])} | "
            f"{stats['n_target']} | {stats['n_stop']} | {stats['n_none']} | {insufficient} |"
        )
    if not rows:
        lines.append("| — | 0 | 0 | — | 0 | 0 | 0 | sim |")
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
) -> tuple[str, dict[str, Any]]:
    realized = [(decision, realized_for(decision, series)) for decision in decisions]
    windows = non_overlapping(decisions)
    window_ids = {decision.call_id for decision in windows}
    realized_windows = [(d, r) for d, r in realized if d.call_id in window_ids]
    # Percurso high/low de cada janela não sobreposta — usado para reavaliar as
    # barreiras de cada candidato de geometria (E4).
    paths = {
        decision.call_id: series.path(decision.at, decision.at + timedelta(seconds=HORIZON_S))
        for decision in windows
    }
    span = None
    if decisions:
        span = (min(d.at for d in decisions), max(d.at for d in decisions))
    summary: dict[str, Any] = {
        "log": str(log_path),
        "calls_returned": sum(1 for d in decisions if d.status is not None),
        "calls_entered": sum(1 for d in decisions if d.entry_mid is not None),
        "malformed_records": malformed,
        "windows_raw": len(decisions),
        "windows_non_overlapping": len(windows),
        "min_non_overlapping_windows": MIN_NON_OVERLAPPING_WINDOWS,
        "min_bucket_trades": MIN_BUCKET_TRADES,
        "fee_bp": str(fee_bp),
        "ohlcv": ohlcv_note,
        "ohlcv_candles": len(series),
        "refusals": dict(sorted(refusals.items())),
        "insufficient": True,
        "confidence_max": str(max((d.confidence for d in decisions), default=Decimal("0"))),
        "insufficient_reasons": [],
        "suggested_confidence_min": None,
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
    # Correção pós-CR (item 1): um bucket que a própria tabela marca
    # `insuficiente` (``n_priced < MIN_BUCKET_TRADES``) nunca pode originar um
    # limiar proposto — expectancy positiva de uma amostra curta não é leitura.
    positive = [
        (label, stats)
        for label, stats in confidence_rows
        if stats["n_priced"] >= MIN_BUCKET_TRADES
        and stats["expectancy_net_bp"] is not None
        and stats["expectancy_net_bp"] > 0
    ]
    confidence_max = Decimal(summary["confidence_max"])
    # E2: uma amostra só é suficiente quando as **janelas com preço**
    # (`n_priced`) chegam ao mínimo, não apenas as janelas não sobrepostas.
    sample_sufficient = (
        len(windows) >= MIN_NON_OVERLAPPING_WINDOWS
        and stats_all["n_priced"] >= MIN_NON_OVERLAPPING_WINDOWS
    )
    if positive and sample_sufficient:
        label = positive[0][0]
        threshold = Decimal(label.split(",")[0].strip("[ "))
        if threshold <= confidence_max:
            summary["suggested_confidence_min"] = str(threshold)
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
    if reasons:
        lines.append("**Amostra insuficiente** — nenhum limiar ou geometria é proposto:")
        lines.append("")
        for reason in reasons:
            lines.append(f"- {reason}")
        if insufficient_regimes:
            lines.append(f"- buckets/regimes com menos de {MIN_BUCKET_TRADES} trades com preço")
        lines.append("")
        lines.append(
            "Consequência (task 1.5): `CONFIDENCE_MIN` mantém o default actual, "
            "`EXIT_TARGET_BP`/`EXIT_STOP_BP` mantêm os valores actuais e "
            "`HOLD_AFTER_FILL_S` fica nos 900 s de produto. O motivo fica registado na evidência."
        )
    else:
        lines.append("Amostra suficiente na régua: proposta")
        lines.append("")
        if summary["suggested_confidence_min"] is not None:
            lines.append(f"- `CONFIDENCE_MIN` = {summary['suggested_confidence_min']}")
        else:
            lines.append(
                "- `CONFIDENCE_MIN`: nenhum bucket com "
                f"{MIN_BUCKET_TRADES}+ trades com preço tem expectancy líquida positiva "
                "— default de produto mantido"
            )
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
    return "\n".join(lines), summary


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
    parser.add_argument("--json", action="store_true", help="imprime também o sumário JSON")
    parser.add_argument("--out", default=None, help="grava o relatório markdown neste caminho")
    args = parser.parse_args(argv)

    import os

    log_path = Path(args.log or os.getenv("SCALP_JEV_LOG_FILE") or DEFAULT_LOG_PATH)
    fee_bp = _dec(args.fee_bp, str(DEFAULT_FEE_BP))

    if not log_path.exists():
        series, ohlcv_note = CandleSeries([]), "OHLCV não consultado (log ausente)"
        report, summary = build_report(
            log_path=log_path,
            decisions=[],
            refusals={},
            malformed=0,
            series=series,
            ohlcv_note=ohlcv_note,
            fee_bp=fee_bp,
        )
        report = f"> **Log ausente**: `{log_path}` não existe.\n\n" + report
    else:
        decisions, refusals, malformed = parse_log(log_path)
        if decisions:
            need_from = min(d.at for d in decisions)
            need_to = max(d.at for d in decisions) + timedelta(seconds=HORIZON_S)
        else:
            need_from = need_to = datetime.utcnow()
        series, ohlcv_note = load_candles(need_from=need_from, need_to=need_to)
        report, summary = build_report(
            log_path=log_path,
            decisions=decisions,
            refusals=refusals,
            malformed=malformed,
            series=series,
            ohlcv_note=ohlcv_note,
            fee_bp=fee_bp,
        )

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
