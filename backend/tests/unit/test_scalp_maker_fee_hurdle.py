"""Card #1025 — B: real maker fee in `_fee_terms`, cache and fallback."""

from __future__ import annotations

import time
import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import ScalpFill, ScalpUserState, UserExchangeCredential
from app.services import scalp_binance
from app.services.binance_spot_orders import BinanceOrderError
from app.services.scalp_service import (
    FALLBACK_FEE_BP,
    FEE_CACHE_TTL_SECONDS,
    _fee_terms,
    _live_fee_terms,
    invalidate_fee_cache,
    status_payload,
)
from app.services.scalp_window import entry_hurdle_bp, passes_entry_hurdle
from test_scalp_direcional_jev import FakeExchange, _add_key, _seed_stream_for_jev


@pytest.fixture(autouse=True)
def _scalp_stream_memory():
    _seed_stream_for_jev()
    yield
    from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory

    get_scalp_btcusdt_memory().reset_for_tests()


@pytest.fixture
def scalp_db(postgres_isolation, unit_database_url):
    from app.database import ensure_runtime_schema_migrations

    ensure_runtime_schema_migrations()
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    db.query(ScalpFill).delete()
    db.query(ScalpUserState).delete()
    db.query(UserExchangeCredential).delete()
    db.commit()
    try:
        yield db
    finally:
        db.query(ScalpFill).delete()
        db.query(ScalpUserState).delete()
        db.query(UserExchangeCredential).delete()
        db.commit()
        db.close()
        engine.dispose()


def _cred(api_key: str = "api-key", api_secret: str = "api-secret") -> SimpleNamespace:
    return SimpleNamespace(api_key=api_key, api_secret=api_secret)


def test_fee_terms_return_the_real_maker_rate_per_leg_and_bnb_state():
    user_id = str(uuid.uuid4())
    seen: list[tuple[str, str]] = []

    def fetcher(api_key: str, api_secret: str) -> tuple[Decimal, bool]:
        seen.append((api_key, api_secret))
        return Decimal("7.5"), True

    fee_bp, bnb_fee_active = _fee_terms(user_id, cred=_cred(), fetcher=fetcher)
    assert (fee_bp, bnb_fee_active) == (Decimal("7.5"), True)
    assert seen == [("api-key", "api-secret")]
    # Maker real por perna → hurdle = 2 × 7,5 + spread, na banda 12–16 bp.
    hurdle = entry_hurdle_bp(fee_bp, Decimal("0.1"))
    assert Decimal("12") <= hurdle <= Decimal("16")
    assert passes_entry_hurdle(Decimal("20"), fee_bp, Decimal("0.1")) is True


def test_fee_terms_without_bnb_keeps_the_hurdle_near_20_bp():
    user_id = str(uuid.uuid4())
    fee_bp, bnb_fee_active = _fee_terms(
        user_id, cred=_cred(), fetcher=lambda _k, _s: (Decimal("10"), False)
    )
    assert (fee_bp, bnb_fee_active) == (Decimal("10"), False)
    hurdle = entry_hurdle_bp(fee_bp, Decimal("0.1"))
    assert Decimal("20") <= hurdle < Decimal("21")


def test_fee_api_failure_falls_back_to_ten_bp_without_bnb():
    user_id = str(uuid.uuid4())

    def timeout(_key: str, _secret: str) -> tuple[Decimal, bool]:
        raise TimeoutError("account read timed out")

    fee_bp, bnb_fee_active = _fee_terms(user_id, cred=_cred(), fetcher=timeout)
    assert (fee_bp, bnb_fee_active) == (FALLBACK_FEE_BP, False)
    assert entry_hurdle_bp(fee_bp, Decimal("0.1")).quantize(Decimal("0.1")) == Decimal("20.1")


def test_fee_terms_non_positive_rate_also_falls_back():
    user_id = str(uuid.uuid4())
    fee_bp, bnb_fee_active = _fee_terms(
        user_id, cred=_cred(), fetcher=lambda _k, _s: (Decimal("0"), True)
    )
    assert (fee_bp, bnb_fee_active) == (FALLBACK_FEE_BP, False)


def test_fee_terms_are_cached_per_user_and_survive_the_cycle_count():
    user_id = str(uuid.uuid4())
    calls = {"n": 0}

    def fetcher(_key: str, _secret: str) -> tuple[Decimal, bool]:
        calls["n"] += 1
        return Decimal("7.5"), True

    for _ in range(200):
        assert _fee_terms(user_id, cred=_cred(), fetcher=fetcher) == (Decimal("7.5"), True)
    assert calls["n"] == 1, "the lookup is served from the per-user cache"
    assert FEE_CACHE_TTL_SECONDS > 0

    invalidate_fee_cache(user_id)
    assert _fee_terms(user_id, cred=_cred(), fetcher=fetcher) == (Decimal("7.5"), True)
    assert calls["n"] == 2


def test_fee_cache_expires_after_the_ttl(monkeypatch):
    user_id = str(uuid.uuid4())
    calls = {"n": 0}

    def fetcher(_key: str, _secret: str) -> tuple[Decimal, bool]:
        calls["n"] += 1
        return Decimal("7.5"), True

    clock = {"now": time.time()}
    monkeypatch.setattr("app.services.scalp_service.time.time", lambda: clock["now"])
    _fee_terms(user_id, cred=_cred(), fetcher=fetcher)
    clock["now"] += FEE_CACHE_TTL_SECONDS - 1
    _fee_terms(user_id, cred=_cred(), fetcher=fetcher)
    assert calls["n"] == 1
    clock["now"] += 2
    _fee_terms(user_id, cred=_cred(), fetcher=fetcher)
    assert calls["n"] == 2


def test_live_fee_terms_read_the_signed_account_and_bnb_burn(monkeypatch):
    paths: list[str] = []

    def fake_signed_request(*, method, path, api_key, api_secret, params=None, base_url=None):
        paths.append(path)
        if path == scalp_binance.ACCOUNT_PATH:
            return {"commissionRates": {"maker": "0.00075000", "taker": "0.00100000"}}
        if path == scalp_binance.BNB_BURN_PATH:
            return {"spotBNBBurn": True}
        raise AssertionError(f"unexpected path {path}")

    monkeypatch.setattr(scalp_binance, "signed_request", fake_signed_request)
    assert _live_fee_terms("key", "secret") == (Decimal("7.5"), True)
    assert paths == [scalp_binance.ACCOUNT_PATH, scalp_binance.BNB_BURN_PATH]


def test_live_fee_terms_failure_is_the_conservative_fallback(monkeypatch):
    user_id = str(uuid.uuid4())

    def boom(*, method, path, api_key, api_secret, params=None, base_url=None):
        raise BinanceOrderError("Binance recusou")

    monkeypatch.setattr(scalp_binance, "signed_request", boom)
    monkeypatch.setattr(
        "app.services.scalp_service._live_fee_terms",
        lambda api_key, api_secret: _live_fee_terms(api_key, api_secret),
    )
    fee_bp, bnb_fee_active = _fee_terms(user_id, cred=_cred(), fetcher=_live_fee_terms)
    assert (fee_bp, bnb_fee_active) == (Decimal("10"), False)


class _FeeExchange(FakeExchange):
    """Fake port that serves the signed fee reads without touching the network."""

    def __init__(self, fee_bp: Decimal = Decimal("7.5"), bnb_fee_active: bool = True) -> None:
        super().__init__()
        self.fee_bp = fee_bp
        self.bnb_fee_active = bnb_fee_active
        self.fee_calls = 0

    def fee_terms(self, api_key: str, api_secret: str) -> tuple[Decimal, bool]:
        self.fee_calls += 1
        return self.fee_bp, self.bnb_fee_active


def test_status_shows_the_fee_rate_in_use(scalp_db, monkeypatch):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = _FeeExchange()
    monkeypatch.setattr("app.services.scalp_service.LiveExchange", lambda: fx)
    from app.services.scalp_service import set_switch

    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    # The schema work above may outlive the 500 ms freshness window: reseed so
    # the status reaches the "ligado" copy that carries the rate in use.
    _seed_stream_for_jev()

    payload = status_payload(scalp_db, user_id)
    spread_bp = (Decimal("65010") - Decimal("65000")) / Decimal("65005") * Decimal("10000")
    assert payload["fee_bp"] == "7.5"
    assert payload["bnb_fee_active"] is True
    assert Decimal(payload["hurdle_bp"]) == entry_hurdle_bp(Decimal("7.5"), spread_bp)
    assert "com taxa 7,5 bp (BNB)" in payload["status_text"]
    assert payload["state"] == "on"

    # The status serves the rate already in use from the cache: no new signed read.
    calls_after_first = fx.fee_calls
    status_payload(scalp_db, user_id)
    assert fx.fee_calls == calls_after_first
