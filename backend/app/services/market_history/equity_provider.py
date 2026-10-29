"""Adaptador do histórico de ações e ETFs da Binance (card #1118, decisão 7).

Rota pública do gráfico, sem credencial e sem contrato estável:
``/bapi/equity/v1/public/equity/kline/chart``. O adaptador fica isolado, valida
cada página antes de entregá-la e falha de forma visível quando a Binance muda
a resposta. Nenhuma página inválida vira dado.

Verificado em 23/10/2026 (tarefas 2.2 e 2.3):

* parâmetros: ``symbol`` (ticker), ``timeframe`` (``5T``, ``1H``, ``4H``,
  ``1D``...), ``limit`` (1000), ``endTime`` (ms) e ``adjustmentMode``;
* paginação retroativa por ``endTime = min(t) - 1``; ``startTime`` não tem a
  semântica da API Spot e não é usado; um ``endTime`` fora de fronteira de candle
  (``t`` ou ``t - 1``) volta com o erro de negócio 488006, por isso o cursor é
  sempre ``min(t) - 1``;
* ``adjustmentMode``: ``ADJUSTED`` e ``UNADJUSTED`` (outro nome volta 488011);
* ``sessionMode``: sem ele a rota devolve o dia estendido (04:00 a 19:55 de Nova York, tudo
  rotulado ``ETH``). Valores aceitos: ``DAY_EXTENDED``, ``PRE_MARKET``, ``POST_MARKET``,
  ``OVERNIGHT``, ``ALL`` e ``REGULAR_MARKET``; este devolve só o pregão regular (09:30 às
  15:55 no 5m, 78 candles por pregão, idênticos ao trecho regular do dia estendido). Qualquer
  outro valor volta com 488006. O ``1D`` recusa o parâmetro (488009) e já é o pregão
  regular. O 5m pede ``REGULAR_MARKET`` (uma página cobre 12,8 pregões em vez de 5,2); o
  filtro local do calendário continua sendo a autoridade;
* o ``1D`` traz o pregão regular (abertura, máxima e mínima iguais às do 5m regular
  agregado em 20 de 20 pregões, também nos dias em que pré/pós-mercado mudam a máxima ou a
  mínima do dia estendido), com ``t`` à meia-noite de Nova York e duração fixa de 24 h; o
  fechamento difere do último 5m em até US$ 0,21 (fechamento oficial) e o volume do 1D é de
  1,16 a 1,51 vezes a soma do 5m regular (outra medida de volume; não é a soma do 5m);
* ``ADJUSTED`` ajusta splits (NVDA 10:1, 10 jun. 2024, sem salto) e NÃO ajusta dividendos
  (SPY e AAPL: ``ADJUSTED`` == ``UNADJUSTED`` em todos os ex-dividendos de jun. 2024 a
  out. 2026): o rótulo da série é "ajustado por split".
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Protocol

import httpx

logger = logging.getLogger(__name__)

BAPI_BASE_URL = "https://www.binance.com"
KLINE_PATH = "/bapi/equity/v1/public/equity/kline/chart"
OK_CODE = "000000"
PAGE_LIMIT = 1000

# timeframe do produto -> (valor da Binance, duração do candle em ms)
NATIVE_TIMEFRAMES: dict[str, tuple[str, int]] = {
    "5m": ("5T", 300_000),
    "1d": ("1D", 86_400_000),
}

ADJUSTMENT_MODES = {"adjusted": "ADJUSTED", "raw": "UNADJUSTED"}
# Só o pregão regular no intradiário (verificado em 23/10/2026, tarefa 2.2); o 1D recusa o parâmetro.
REGULAR_SESSION_MODE = "REGULAR_MARKET"
SESSION_MODE_TIMEFRAMES = {"5m"}

_REQUIRED_BAR_FIELDS = ("t", "ct", "o", "h", "l", "c", "v")


class BinanceEquityError(Exception):
    """Base das falhas do adaptador. ``code`` é estável e vai para a cobertura."""

    code = "binance_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class BinanceBusinessError(BinanceEquityError):
    """Resposta com ``code`` diferente de ``000000``, mesmo em HTTP 200."""

    code = "binance_business_error"

    def __init__(self, business_code: str, message: str | None = None) -> None:
        super().__init__(
            message or f"A Binance recusou o pedido (erro de negócio {business_code}).",
            code="binance_business_error",
        )
        self.business_code = str(business_code)


class BinanceFormatChanged(BinanceEquityError):
    code = "binance_format_changed"

    def __init__(self, detail: str) -> None:
        super().__init__(f"formato da Binance mudou: {detail}", code="binance_format_changed")
        self.detail = detail


class BinanceRateLimited(BinanceEquityError):
    code = "binance_rate_limited"

    def __init__(self, status: int, retry_after: float | None) -> None:
        super().__init__(
            "Limite de requisições da Binance atingido"
            + (f"; tente de novo em {int(retry_after)} s." if retry_after else "."),
            code="binance_rate_limited",
        )
        self.status = status
        self.retry_after = retry_after


class BinanceUnavailable(BinanceEquityError):
    code = "binance_unavailable"

    def __init__(self, detail: str) -> None:
        super().__init__(f"Binance indisponível: {detail}", code="binance_unavailable")


class BinanceCircuitOpen(BinanceEquityError):
    code = "binance_circuit_open"

    def __init__(self, until_epoch: float) -> None:
        wait = max(0, int(until_epoch - time.time()))
        super().__init__(
            f"Coleta de ações em pausa por falhas seguidas da Binance; volta em {wait} s.",
            code="binance_circuit_open",
        )
        self.until_epoch = until_epoch


class UnsupportedTimeframe(BinanceEquityError):
    code = "timeframe_not_supported"


class RequestLimiter(Protocol):
    def acquire(self) -> None: ...

    def success(self) -> None: ...

    def throttled(self, retry_after: float | None, status: int) -> None: ...

    def failure(self, reason: str) -> None: ...


class NullLimiter:
    """Sem limite: só para testes que não tocam a rede."""

    def acquire(self) -> None:
        return None

    def success(self) -> None:
        return None

    def throttled(self, retry_after: float | None, status: int) -> None:
        return None

    def failure(self, reason: str) -> None:
        return None


@dataclass(frozen=True)
class EquityBar:
    t: int
    ct: int
    o: Decimal
    h: Decimal
    l: Decimal
    c: Decimal
    v: Decimal
    vw: Decimal | None = None
    n: int | None = None
    session: str | None = None


@dataclass
class EquityPage:
    symbol: str
    timeframe: str
    bars: list[EquityBar]
    end_time: int | None
    # Página vazia confirmada por uma segunda leitura: início do histórico na Binance.
    confirmed_empty: bool = False
    requests: int = 1

    @property
    def min_t(self) -> int | None:
        return self.bars[0].t if self.bars else None

    @property
    def max_t(self) -> int | None:
        return self.bars[-1].t if self.bars else None


_TICKER_RE = re.compile(r"^[A-Z0-9][A-Z0-9.\-]{0,15}$")


def _decimal(value: Any, field_name: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise BinanceFormatChanged(f"campo {field_name} não numérico")
    try:
        out = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise BinanceFormatChanged(f"campo {field_name} não numérico") from None
    if not out.is_finite():
        raise BinanceFormatChanged(f"campo {field_name} não numérico")
    return out


def _integer(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise BinanceFormatChanged(f"campo {field_name} não inteiro")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise BinanceFormatChanged(f"campo {field_name} não inteiro") from None
    if number != number.to_integral_value():
        raise BinanceFormatChanged(f"campo {field_name} não inteiro")
    return int(number)


def parse_page(
    payload: Any,
    *,
    timeframe: str,
    end_time: int | None,
    symbol: str | None = None,
) -> list[EquityBar]:
    """Valida a resposta inteira e devolve os candles ordenados (design, decisão 7).

    Tudo ou nada: qualquer irregularidade levanta e a página não é gravada.
    """

    if timeframe not in NATIVE_TIMEFRAMES:
        raise UnsupportedTimeframe(f"Timeframe {timeframe} não é coletado para ações e ETFs.")
    _, duration = NATIVE_TIMEFRAMES[timeframe]
    if not isinstance(payload, dict):
        raise BinanceFormatChanged("a resposta não é um objeto")
    if "code" not in payload:
        raise BinanceFormatChanged("resposta sem code")
    code = str(payload.get("code"))
    if code != OK_CODE:
        raise BinanceBusinessError(code)
    data = payload.get("data")
    if not isinstance(data, dict):
        raise BinanceFormatChanged("resposta sem data")
    bars = data.get("bars")
    if not isinstance(bars, list):
        raise BinanceFormatChanged("data.bars não é uma lista")
    echoed = data.get("symbol")
    if symbol is not None and echoed is not None and str(echoed).upper() != symbol.upper():
        raise BinanceFormatChanged(f"símbolo devolvido {echoed!r} difere do pedido {symbol!r}")

    out: list[EquityBar] = []
    for raw in bars:
        if not isinstance(raw, dict):
            raise BinanceFormatChanged("candle que não é um objeto")
        for name in _REQUIRED_BAR_FIELDS:
            if name not in raw or raw[name] is None:
                raise BinanceFormatChanged(f"candle sem o campo {name}")
        t = _integer(raw["t"], "t")
        ct = _integer(raw["ct"], "ct")
        o = _decimal(raw["o"], "o")
        h = _decimal(raw["h"], "h")
        low = _decimal(raw["l"], "l")
        c = _decimal(raw["c"], "c")
        v = _decimal(raw["v"], "v")
        if ct - t + 1 != duration:
            raise BinanceFormatChanged(
                f"duração do candle {ct - t + 1} ms difere de {duration} ms ({timeframe})"
            )
        if min(o, h, low, c) <= 0:
            raise BinanceFormatChanged("preço não positivo")
        if v < 0:
            raise BinanceFormatChanged("volume negativo")
        if low > min(o, c) or h < max(o, c) or low > h:
            raise BinanceFormatChanged("OHLC incoerente")
        vw = _decimal(raw["vw"], "vw") if raw.get("vw") is not None else None
        n = _integer(raw["n"], "n") if raw.get("n") is not None else None
        out.append(
            EquityBar(
                t=t,
                ct=ct,
                o=o,
                h=h,
                l=low,
                c=c,
                v=v,
                vw=vw,
                n=n,
                session=str(raw["session"]) if raw.get("session") is not None else None,
            )
        )
    stamps = [b.t for b in out]
    if stamps != sorted(stamps) or len(set(stamps)) != len(stamps):
        raise BinanceFormatChanged("candles fora de ordem ou repetidos")
    if end_time is not None and stamps and stamps[-1] > end_time:
        raise BinanceFormatChanged("candle depois do endTime pedido")
    return out


class BinanceEquityProvider:
    """Cliente da rota de gráfico de ações/ETFs, atrás de um limitador compartilhado."""

    source = "binance_equity"

    def __init__(
        self,
        *,
        limiter: RequestLimiter | None = None,
        client: httpx.Client | None = None,
        base_url: str = BAPI_BASE_URL,
        timeout: float = 20.0,
    ) -> None:
        self.limiter: RequestLimiter = limiter or NullLimiter()
        self._client = client
        self._owns_client = client is None
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _http(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=httpx.Timeout(self.timeout))
        return self._client

    def close(self) -> None:
        if self._client is not None and self._owns_client:
            self._client.close()
            self._client = None

    @staticmethod
    def _retry_after(response: httpx.Response) -> float | None:
        raw = response.headers.get("Retry-After")
        if raw is None:
            return None
        try:
            return max(0.0, float(raw))
        except ValueError:
            return None

    def _request(self, params: dict[str, Any]) -> Any:
        self.limiter.acquire()
        try:
            response = self._http().get(
                self.base_url + KLINE_PATH,
                params=params,
                headers={"Accept": "application/json"},
            )
        except httpx.HTTPError as exc:
            self.limiter.failure("network")
            raise BinanceUnavailable(str(exc) or exc.__class__.__name__) from exc
        status = response.status_code
        if status in (418, 429):
            retry_after = self._retry_after(response)
            self.limiter.throttled(retry_after, status)
            raise BinanceRateLimited(status, retry_after)
        if status >= 500:
            self.limiter.failure(f"http_{status}")
            raise BinanceUnavailable(f"HTTP {status}")
        try:
            payload = response.json()
        except ValueError:
            # HTTP 200 (ou 4xx) sem JSON: formato mudou, não é lista vazia.
            raise BinanceFormatChanged("a resposta não é JSON") from None
        self.limiter.success()
        return payload

    def fetch_page_once(
        self,
        symbol: str,
        timeframe: str,
        *,
        end_time: int | None = None,
        adjustment: str = "adjusted",
        limit: int = PAGE_LIMIT,
    ) -> EquityPage:
        ticker = str(symbol or "").strip().upper()
        if not _TICKER_RE.match(ticker):
            raise BinanceFormatChanged(f"símbolo inválido {symbol!r}")
        if timeframe not in NATIVE_TIMEFRAMES:
            raise UnsupportedTimeframe(f"Timeframe {timeframe} não é coletado para ações e ETFs.")
        mode = ADJUSTMENT_MODES.get(adjustment)
        if mode is None:
            raise UnsupportedTimeframe(
                f"Ajuste {adjustment} desconhecido.", code="adjustment_unknown"
            )
        params: dict[str, Any] = {
            "symbol": ticker,
            "timeframe": NATIVE_TIMEFRAMES[timeframe][0],
            "limit": int(limit),
            "adjustmentMode": mode,
        }
        if timeframe in SESSION_MODE_TIMEFRAMES:
            params["sessionMode"] = REGULAR_SESSION_MODE
        if end_time is not None:
            params["endTime"] = int(end_time)
        payload = self._request(params)
        bars = parse_page(payload, timeframe=timeframe, end_time=end_time, symbol=ticker)
        return EquityPage(symbol=ticker, timeframe=timeframe, bars=bars, end_time=end_time)

    def fetch_page(
        self,
        symbol: str,
        timeframe: str,
        *,
        end_time: int | None = None,
        adjustment: str = "adjusted",
        limit: int = PAGE_LIMIT,
        confirm_empty: bool = True,
    ) -> EquityPage:
        """Uma página; página vazia com ``000000`` é pedida de novo uma vez.

        Só depois da segunda leitura vazia a página sai com ``confirmed_empty``,
        o que a coleta interpreta como "a Binance não tem candles antes disso".
        """

        page = self.fetch_page_once(
            symbol, timeframe, end_time=end_time, adjustment=adjustment, limit=limit
        )
        if page.bars or not confirm_empty:
            return page
        again = self.fetch_page_once(
            symbol, timeframe, end_time=end_time, adjustment=adjustment, limit=limit
        )
        again.requests = 2
        again.confirmed_empty = not again.bars
        return again
