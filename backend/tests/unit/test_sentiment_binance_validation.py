from __future__ import annotations

import builtins
import io
import json
import sys
import types
from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workflow_database import WorkflowBase
from app.workflow_models import Change, Project, WorkItem, WorkItemState, WorkItemType
import app.services.binance_spot as binance_spot
import app.services.sentiment_service as sentiment_service
import app.services.workflow_validation_service as workflow_validation_service


@pytest.fixture
def workflow_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    WorkflowBase.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.mark.asyncio
async def test_sentiment_fetchers_and_market_aggregate_cover_success_and_fallback(monkeypatch):
    class FakeAsyncResponse:
        def __init__(self, payload=None, error: Exception | None = None):
            self._payload = payload or {}
            self._error = error

        def raise_for_status(self):
            if self._error:
                raise self._error

        def json(self):
            return self._payload

    class FakeAsyncClient:
        def __init__(self, response):
            self._response = response

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return self._response

    assert sentiment_service._classify(60) == "bullish"
    assert sentiment_service._classify(40) == "bearish"
    assert sentiment_service._classify(50) == "neutral"

    monkeypatch.setattr(
        sentiment_service.httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(FakeAsyncResponse({"data": [{"value": "72"}]})),
    )
    assert await sentiment_service._fetch_fear_greed() == 72

    monkeypatch.setattr(
        sentiment_service.httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(
            FakeAsyncResponse(error=httpx.HTTPError("fear-greed unavailable"))
        ),
    )
    assert await sentiment_service._fetch_fear_greed() == 50

    monkeypatch.setattr(
        sentiment_service.httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(FakeAsyncResponse({"coins": [{}] * 25})),
    )
    assert await sentiment_service._fetch_news_sentiment() == 80

    monkeypatch.setattr(
        sentiment_service.httpx,
        "AsyncClient",
        lambda timeout: FakeAsyncClient(
            FakeAsyncResponse(error=httpx.HTTPError("news unavailable"))
        ),
    )
    assert await sentiment_service._fetch_news_sentiment() == 50

    async def fake_to_thread(fn):
        assert fn is sentiment_service._analyze_reddit_sentiment
        return 120

    async def fake_fear_greed():
        return 90

    async def fake_news():
        return 150

    monkeypatch.setattr(sentiment_service.asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(sentiment_service, "_fetch_fear_greed", fake_fear_greed)
    monkeypatch.setattr(sentiment_service, "_fetch_news_sentiment", fake_news)

    result = await sentiment_service.get_market_sentiment()
    assert result.score == 100
    assert result.signal == "bullish"
    assert result.components == {"news": 150, "reddit": 120, "fear_greed": 90}


def test_reddit_sentiment_handles_missing_nltk_and_parses_titles(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "nltk.sentiment":
            raise ImportError("nltk unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert sentiment_service._analyze_reddit_sentiment() == 50

    fake_nltk = types.ModuleType("nltk")
    fake_sentiment = types.ModuleType("nltk.sentiment")

    class FakeSIA:
        def polarity_scores(self, title):
            if "moon" in title.lower():
                return {"compound": 0.6}
            return {"compound": -0.2}

    fake_sentiment.SentimentIntensityAnalyzer = lambda: FakeSIA()
    fake_nltk.sentiment = fake_sentiment
    monkeypatch.setitem(sys.modules, "nltk", fake_nltk)
    monkeypatch.setitem(sys.modules, "nltk.sentiment", fake_sentiment)
    monkeypatch.setattr(builtins, "__import__", real_import)

    payload = {
        "data": {
            "children": [
                {"data": {"title": "Bitcoin to the moon"}},
                {"data": {"title": "Market may dump"}},
            ]
        }
    }

    class FakeUrlResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(req, timeout):
        assert "reddit.com/r/" in req.full_url
        assert timeout == 8
        return FakeUrlResponse(json.dumps(payload).encode("utf-8"))

    import urllib.request

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert sentiment_service._analyze_reddit_sentiment() == 60


def test_binance_spot_helpers_signed_get_and_snapshot_filters(monkeypatch):
    monkeypatch.setenv("BINANCE_API_KEY", "  key ")
    monkeypatch.setenv("BINANCE_API_SECRET", " secret ")
    monkeypatch.setenv("BINANCE_BASE_URL", " https://example.invalid ")
    monkeypatch.setenv("BINANCE_HTTP_TIMEOUT_SECONDS", "not-an-int")
    monkeypatch.setenv("BINANCE_MAX_TRADE_SYMBOLS", "1")
    monkeypatch.setenv("BINANCE_TRADE_LOOKUPS_BUDGET_SECONDS", "1")

    assert binance_spot._get_env("BINANCE_API_KEY") == "key"
    assert binance_spot._get_int_env("BINANCE_HTTP_TIMEOUT_SECONDS", 10) == 10
    assert binance_spot._clamp_int(999, 1, 60) == 60

    captured_request: dict[str, object] = {}

    class JsonResponse(io.StringIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_urlopen(req, timeout):
        captured_request["url"] = req.full_url
        captured_request["headers"] = dict(req.header_items())
        captured_request["timeout"] = timeout
        return JsonResponse('{"ok": true}')

    monkeypatch.setattr(binance_spot.urllib.request, "urlopen", fake_urlopen)

    signed = binance_spot._signed_get(
        "https://example.invalid",
        "key",
        "secret",
        "/api/v3/account",
        {"timestamp": 123},
        timeout_s=9,
    )
    assert signed == {"ok": True}
    assert "signature=" in str(captured_request["url"])
    assert dict(captured_request["headers"]).get("X-mbx-apikey") == "key"
    assert captured_request["timeout"] == 9.0

    monkeypatch.delenv("BINANCE_API_KEY", raising=False)
    monkeypatch.delenv("BINANCE_API_SECRET", raising=False)
    with pytest.raises(binance_spot.BinanceConfigError, match="Missing Binance credentials"):
        binance_spot.fetch_spot_balances_snapshot(api_key="", api_secret="")

    signed_get_calls: list[tuple[str, int]] = []
    avg_cost_calls: list[str] = []

    def fake_signed_get(base_url, api_key, api_secret, path, params, *, timeout_s):
        signed_get_calls.append((path, timeout_s))
        return {
            "balances": [
                {"asset": "", "free": "1", "locked": "0"},
                {"asset": "BAD", "free": "oops", "locked": "0"},
                {"asset": "ZERO", "free": "0", "locked": "0"},
                {"asset": "DUST", "free": "0.001", "locked": "0"},
                {"asset": "NOPRICE", "free": "1", "locked": "0"},
                {"asset": "BBB", "free": "2", "locked": "0"},
                {"asset": "AAA", "free": "3", "locked": "1"},
            ]
        }

    def fake_compute_usdt_price(asset, _prices):
        return {
            "AAA": 100.0,
            "BBB": 5.0,
            "DUST": 1.0,
        }.get(asset)

    def fake_avg_cost(asset, **kwargs):
        avg_cost_calls.append(asset)
        assert kwargs["lookback_days"] == 30
        assert kwargs["api_key"] == "key"
        return {"AAA": 80.0}.get(asset)

    monkeypatch.setattr(binance_spot, "_signed_get", fake_signed_get)
    monkeypatch.setattr(binance_spot, "fetch_all_binance_prices", lambda: {"unused": 1.0})
    monkeypatch.setattr(binance_spot, "compute_usdt_price_for_asset", fake_compute_usdt_price)
    monkeypatch.setattr(binance_spot, "compute_avg_buy_cost_usdt", fake_avg_cost)
    monkeypatch.setattr(binance_spot.time, "time", lambda: 1_700_000_000.0)

    snapshot = binance_spot.fetch_spot_balances_snapshot(
        lookback_days=30,
        api_key="key",
        api_secret="secret",
    )
    assert signed_get_calls == [("/api/v3/account", 10)]
    assert avg_cost_calls == ["AAA"]
    assert snapshot["as_of"] == "2023-11-14T22:13:20Z"
    assert snapshot["total_usd"] == pytest.approx(410.0)
    assert [row["asset"] for row in snapshot["balances"]] == ["AAA", "BBB"]
    assert snapshot["balances"][0]["pnl_usd"] == pytest.approx(80.0)
    assert snapshot["balances"][0]["pnl_pct"] == pytest.approx(25.0)
    assert snapshot["balances"][1]["avg_cost_usdt"] is None
    assert snapshot["balances"][1]["pnl_usd"] is None
    assert snapshot["balances"][1]["pnl_pct"] is None


def test_workflow_validation_file_helpers_handoff_and_sync_discrepancies(
    monkeypatch, tmp_path, workflow_session
):
    monkeypatch.setattr(workflow_validation_service, "REPO_ROOT", tmp_path)

    archived_change = tmp_path / "openspec" / "changes" / "archive" / "2026-04-18-coverage-ratchet"
    archived_change.mkdir(parents=True)
    (archived_change / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
    (archived_change / "review-ptbr.md").write_text("# Review\n", encoding="utf-8")
    (archived_change / "tasks.md").write_text(
        "- [x] 1.1 Existing task\n- [ ] 1.2 Missing in DB\n",
        encoding="utf-8",
    )
    (archived_change / "meta.yaml").write_text("status: QA\n", encoding="utf-8")

    broken_change = tmp_path / "openspec" / "changes" / "broken-change"
    broken_change.mkdir(parents=True)
    (broken_change / "meta.yaml").write_text("status: [broken\n", encoding="utf-8")

    approval = workflow_validation_service.validate_approval_gate("coverage-ratchet")
    assert approval.is_valid is True
    assert approval.missing_files == []

    assert workflow_validation_service._get_change_status_from_meta("coverage-ratchet") == "QA"
    assert workflow_validation_service._get_change_status_from_meta("broken-change") is None
    assert workflow_validation_service._get_tasks_from_file("missing-change") == []
    assert workflow_validation_service._get_tasks_from_file("coverage-ratchet") == [
        {"code": "1.1", "description": "Existing task", "done": True},
        {"code": "1.2", "description": "Missing in DB", "done": False},
    ]

    validation_error = workflow_validation_service.ValidationError(
        "invalid_handoff",
        "Missing evidence",
        {"field": "evidence"},
    )
    assert validation_error.code == "invalid_handoff"
    assert validation_error.details["field"] == "evidence"

    handoff = workflow_validation_service.validate_handoff_comment(
        "status = done\nlink: https://example.invalid/pr/22\npending: qa"
    )
    assert handoff.is_valid is True
    assert handoff.errors == []

    project = Project(slug="crypto", name="Crypto")
    workflow_session.add(project)
    workflow_session.flush()

    change = Change(
        project_id=project.id,
        change_id="coverage-ratchet",
        title="Improve coverage",
        status="DEV",
    )
    workflow_session.add(change)
    workflow_session.flush()

    story = WorkItem(
        change_pk=change.id,
        type=WorkItemType.story,
        state=WorkItemState.active,
        title="1.1 Existing task",
    )
    workflow_session.add(story)
    workflow_session.flush()

    extra_story = WorkItem(
        change_pk=change.id,
        type=WorkItemType.story,
        state=WorkItemState.done,
        title="9.9 Extra task",
    )
    blocking_bug = WorkItem(
        change_pk=change.id,
        parent_id=story.id,
        type=WorkItemType.bug,
        state=WorkItemState.active,
        title="Blocking bug",
    )
    standalone_bug = WorkItem(
        change_pk=change.id,
        type=WorkItemType.bug,
        state=WorkItemState.active,
        title="Not a story",
    )
    workflow_session.add_all([extra_story, blocking_bug, standalone_bug])
    workflow_session.commit()

    closure = workflow_validation_service.validate_story_closure(workflow_session, story.id)
    assert closure.is_valid is False
    assert closure.blocking_bugs[0]["id"] == blocking_bug.id

    with pytest.raises(HTTPException) as not_found_exc:
        workflow_validation_service.validate_story_closure(workflow_session, "missing-story")
    assert not_found_exc.value.status_code == 404

    with pytest.raises(HTTPException) as not_story_exc:
        workflow_validation_service.validate_story_closure(workflow_session, standalone_bug.id)
    assert not_story_exc.value.status_code == 400

    sync = workflow_validation_service.verify_sync("coverage-ratchet", workflow_session)
    assert sync.is_synced is False
    assert sync.db_status == "DEV"
    assert sync.file_status == "QA"
    assert {item.type for item in sync.discrepancies} == {"status", "work_item"}
    assert any("1.2" in item.description for item in sync.discrepancies)
    assert any("9.9" in item.description for item in sync.discrepancies)
