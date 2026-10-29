"""Apoio dos testes do card #1123: séries sintéticas e fonte de referência simulada (sem rede)."""

from __future__ import annotations

import io
import os
import uuid
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.services import benchmark_comparison as bench

HOLIDAYS = {(1, 1), (12, 25), (7, 4)}

IDENTITIES = {
    "BTC/USDT": {
        "symbol": "BTC/USDT",
        "asset_class": "crypto",
        "currency": "USDT",
        "asset_id": "binance:spot:BTC/USDT",
        "name": "BTC",
    },
    "SOL/USDT": {
        "symbol": "SOL/USDT",
        "asset_class": "crypto",
        "currency": "USDT",
        "asset_id": "binance:spot:SOL/USDT",
        "name": "SOL",
    },
    "PENGU/USDT": {
        "symbol": "PENGU/USDT",
        "asset_class": "crypto",
        "currency": "USDT",
        "asset_id": "binance:spot:PENGU/USDT",
        "name": "PENGU",
    },
    "SPY": {
        "symbol": "SPY",
        "asset_class": "etf",
        "currency": "USD",
        "asset_id": "binance:equity:SPY",
        "name": "SPDR S&P 500",
    },
    "QQQ": {
        "symbol": "QQQ",
        "asset_class": "etf",
        "currency": "USD",
        "asset_id": "binance:equity:QQQ",
        "name": "Invesco QQQ",
    },
    "NVDA": {
        "symbol": "NVDA",
        "asset_class": "stock",
        "currency": "USD",
        "asset_id": "binance:equity:NVDA",
        "name": "NVIDIA",
    },
    "CRCL": {
        "symbol": "CRCL",
        "asset_class": "stock",
        "currency": "USD",
        "asset_id": "binance:equity:CRCL",
        "name": "Circle",
    },
}


def crypto_frame(start: str, end: str, base: float = 100.0, step: float = 1.0) -> pd.DataFrame:
    index = pd.date_range(start, end, freq="D", tz="UTC")
    closes = [base + step * i for i in range(len(index))]
    return pd.DataFrame(
        {"open": closes, "high": closes, "low": closes, "close": closes, "volume": 1.0}, index=index
    )


def equity_frame(start: str, end: str, base: float = 50.0, step: float = 0.1) -> pd.DataFrame:
    days = [d for d in pd.bdate_range(start, end) if (d.month, d.day) not in HOLIDAYS]
    index = pd.DatetimeIndex(days).tz_localize("America/New_York").tz_convert("UTC")
    closes = [base + step * i for i in range(len(index))]
    return pd.DataFrame(
        {"open": closes, "high": closes, "low": closes, "close": closes, "volume": 1.0}, index=index
    )


def default_frames() -> dict[str, pd.DataFrame]:
    return {
        "BTC/USDT": crypto_frame("2017-08-17", "2026-10-27"),
        "SOL/USDT": crypto_frame("2020-08-11", "2026-10-27"),
        "PENGU/USDT": crypto_frame("2024-12-17", "2026-10-27"),
        "SPY": equity_frame("2003-01-02", "2026-10-27"),
        "QQQ": equity_frame("2003-01-02", "2026-10-27", base=30.0),
        "NVDA": equity_frame("2003-01-02", "2026-10-27", base=5.0, step=0.05),
        "CRCL": equity_frame("2025-06-05", "2026-10-27"),
    }


class FakeSource(bench.ReferenceSource):
    """Fonte de referência sem rede: conta coletas, leituras e congelamentos."""

    def __init__(self, frames: dict[str, pd.DataFrame] | None = None) -> None:
        super().__init__(timeout_seconds=5)
        self.frames = frames if frames is not None else default_frames()
        self.missing: set[str] = set()  # sem histórico guardado (coleta ao escolher)
        self.fail: set[str] = set()  # coleta falha sem nada guardado
        self.loads: list[str] = []
        self.freezes: list[tuple[str, str, str]] = []

    def identity(self, symbol: str) -> dict[str, Any]:
        sym = str(symbol).upper()
        return dict(IDENTITIES.get(sym) or {"symbol": sym, "asset_class": None})

    def has_history(self, symbol: str) -> bool:
        return symbol in self.frames and symbol not in self.missing

    def load(self, symbol, start=None, end=None, *, collect=True):
        self.loads.append(symbol)
        if symbol in self.fail:
            raise bench.BenchmarkCollectionError(
                f"Não foi possível coletar o histórico de {symbol} na Binance (tempo esgotado).",
                symbol=symbol,
                reason="tempo esgotado",
            )
        collected = symbol in self.missing
        self.missing.discard(symbol)
        return bench.LoadedReference(
            identity=self.identity(symbol),
            frame=self.frames.get(symbol, pd.DataFrame()),
            collected=collected,
        )

    def freeze(self, symbol, frame, start, end, owner_ref):
        sid = f"snap{len(self.freezes) + 1:04d}{uuid.uuid4().hex[:6]}"
        self.freezes.append((symbol, str(start), str(end)))
        return {
            "snapshot_id": sid,
            "version_label": "5",
            "data_version": 5,
            "content_sha256": "sha-" + sid,
            "source": "Binance Ações" if "/" not in symbol else "Binance Spot",
            "session": "rth" if "/" not in symbol else "24x7",
            "adjustment": "adjusted" if "/" not in symbol else "na",
        }

    def version_only(self, symbol):
        return {"snapshot_id": None, "version_label": "5"}


def trade(entry: str, exit_: str, profit: float) -> dict:
    return {
        "entry_time": f"{entry}T00:00:00Z",
        "exit_time": f"{exit_}T00:00:00Z",
        "exit_price": 1.0,
        "profit": profit,
    }


BTC_TRADES = [
    trade("2019-02-01", "2019-06-01", 0.50),
    trade("2019-09-01", "2020-01-10", -0.10),
    trade("2020-03-01", "2020-07-01", 0.80),
    trade("2020-09-01", "2021-04-01", 1.20),
    trade("2021-10-01", "2022-01-05", -0.05),
    trade("2022-03-01", "2022-08-01", 0.10),
    trade("2023-01-10", "2023-07-01", 0.60),
    trade("2023-10-01", "2024-03-01", 0.90),
    trade("2024-09-01", "2024-12-20", 0.30),
]


def btc_result(**extra) -> dict[str, Any]:
    return {
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "template_name": "multi_ma_crossover",
        "direction": "long",
        "asset": IDENTITIES["BTC/USDT"],
        "start_date": "2019-01-01",
        "end_date": "2024-12-31",
        "execution": {
            "precision_requested": "intrabar",
            "precision_effective": "intrabar_15m",
            "window": {
                "requested": {"start": "2019-01-01", "end": "2024-12-31"},
                "covered": {
                    "start": "2019-01-01T00:00:00+00:00",
                    "end": "2024-12-31T00:00:00+00:00",
                    "candles": 2192,
                },
            },
        },
        "trades": list(BTC_TRADES),
        **extra,
    }


def ensure_snapshot_table(db) -> None:
    from app.services.market_history.schema import SNAPSHOT_TABLE_SQL

    db.execute(text(SNAPSHOT_TABLE_SQL))
    db.execute(text("TRUNCATE execution_data_snapshots"))
    db.commit()


def insert_snapshot(db, sid: str, *, retain_until=None, pinned: bool = False) -> None:
    db.execute(
        text(
            "INSERT INTO execution_data_snapshots (snapshot_id, kind, owner_ref, series, segments, "
            "created_at, retain_until, pinned) VALUES (:id, 'test', NULL, '[]'::jsonb, '[]'::jsonb, now(), "
            ":ru, :p) ON CONFLICT (snapshot_id) DO NOTHING"
        ),
        {
            "id": sid,
            "ru": retain_until or pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=30),
            "p": pinned,
        },
    )
    db.commit()


def pinned(db, sid: str) -> bool | None:
    row = db.execute(
        text("SELECT pinned FROM execution_data_snapshots WHERE snapshot_id = :i"), {"i": sid}
    ).first()
    return None if row is None else bool(row.pinned)


def make_user(db, name: str, *, admin: bool = False):
    from app.models import User

    user = User(
        id=uuid.uuid4(),
        email=f"{name}@test.local",
        password_hash="x",
        name=name,
        role="admin" if admin else "user",
    )
    db.add(user)
    db.commit()
    return user


def client_for(db, routers: Iterable[Any], state: dict[str, Any]) -> TestClient:
    from app.database import get_db
    from app.middleware.authMiddleware import get_current_admin, get_current_user

    Session = sessionmaker(bind=db.get_bind())

    def _db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    def _admin():
        from fastapi import HTTPException

        if not state.get("admin", True):
            raise HTTPException(status_code=403, detail="Admin access required")
        return state["user"]

    app = FastAPI()
    for router in routers:
        app.include_router(router)
    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = lambda: state["user"]
    app.dependency_overrides[get_current_admin] = _admin
    return TestClient(app)


# --------------------------------------------------------------------------- planilhas do E2E

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "frontend/tests/e2e/fixtures/card-1123"
# Campos estáveis (sem data de gravação nem id de amostra) comparados com a planilha versionada.
STABLE = (
    "Name",
    "Symbol",
    "Rank global",
    "Candidato",
    "Campo",
    "Classe",
    "Moeda",
    "Fonte",
    "Sessão",
    "Ajuste",
    "Período pedido",
    "Referência",
    "Tipo de retorno da referência",
    "Situação da comparação",
    "Aviso de moeda",
    "Referência (extra)",
    "Situação da comparação (extra)",
)


def _sheets(content: bytes) -> dict[str, list[list[Any]]]:
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(content))
    return {ws.title: [[c.value for c in row] for row in ws.iter_rows()] for ws in wb.worksheets}


def _stable_view(sheets: dict[str, list[list[Any]]]) -> dict[str, Any]:
    view: dict[str, Any] = {}
    for title, rows in sheets.items():
        if not rows:
            view[title] = []
            continue
        header = rows[0]
        if title == "Contexto":
            keep = {
                "Classe",
                "Moeda",
                "Fonte",
                "Sessão",
                "Ajuste",
                "Referência",
                "Situação da comparação",
            }
            view[title] = [r[:1] + [r[1] if r[0] in keep else None, r[2]] for r in rows]
            continue
        idx = [i for i, h in enumerate(header) if h in STABLE]
        view[title] = [header] + [[r[i] for i in idx] for r in rows[1:]]
    return view


def sync_e2e_fixture(name: str, content: bytes) -> None:
    """Planilha servida pelo E2E de Playwright (tarefa 7.2): gerada pelo construtor real.

    ``C1123_WRITE_FIXTURES=1`` regrava o arquivo; sem a variável, o teste confere que a planilha
    versionada continua igual ao que o servidor monta hoje (cabeçalhos e campos estáveis).
    """

    path = FIXTURE_DIR / name
    if os.getenv("C1123_WRITE_FIXTURES") == "1":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return
    assert path.is_file(), f"planilha do E2E ausente: {path} (rode com C1123_WRITE_FIXTURES=1)"
    assert _stable_view(_sheets(path.read_bytes())) == _stable_view(_sheets(content))
