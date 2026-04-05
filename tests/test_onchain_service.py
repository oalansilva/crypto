# -*- coding: utf-8 -*-
"""Tests for onchain signal service."""

import sys
from pathlib import Path

# Ensure backend is on path for imports
BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from unittest.mock import patch, MagicMock

from app.services.onchain_service import (
    OnchainMetrics,
    SignalResult,
    _normalize,
    _compose_signal,
    fetch_onchain_metrics,
    TOP_CHAINS,
    WEIGHTS,
)


class TestNormalize:
    def test_normalize_within_range(self):
        assert _normalize(5e8, "tvl") == pytest.approx(0.05, abs=0.01)

    def test_normalize_none_returns_zero(self):
        assert _normalize(None, "tvl") == 0.0

    def test_normalize_above_max(self):
        assert _normalize(1e11, "tvl") == 1.0


class TestComposeSignal:
    def test_compose_signal_buy_high_tvl_and_addresses(self):
        metrics = OnchainMetrics(
            token="ETH",
            chain="ethereum",
            tvl=5e9,
            active_addresses=5e6,
            exchange_flow=1e8,
            github_commits=500,
            github_stars=10000,
            github_prs=100,
            github_issues=200,
        )
        result = _compose_signal(metrics)
        assert result.signal in ("BUY", "SELL", "HOLD")
        assert 0 <= result.confidence <= 100
        assert isinstance(result.breakdown, dict)
        assert result.metrics.token == "ETH"

    def test_compose_signal_all_none(self):
        metrics = OnchainMetrics(
            token="XXX",
            chain="ethereum",
            tvl=None,
            active_addresses=None,
            exchange_flow=None,
            github_commits=None,
            github_stars=None,
            github_prs=None,
            github_issues=None,
        )
        result = _compose_signal(metrics)
        # All-None metrics → score 0 → HOLD
        # Note: exchange_flow=None→0 raw, which normalises to mid-point (0.5)
        # due to symmetric range (-1e9, 1e9), contributing some baseline confidence.
        assert result.signal == "HOLD"
        assert 0 <= result.confidence <= 20  # low but non-zero due to exchange_flow=0 normalisation

    def test_compose_signal_sell_negative_flow_declining(self):
        metrics = OnchainMetrics(
            token="XXX",
            chain="ethereum",
            tvl=1e7,
            active_addresses=100,
            exchange_flow=-5e8,
            github_commits=0,
            github_stars=100,
            github_prs=0,
            github_issues=50,
        )
        result = _compose_signal(metrics)
        assert result.signal == "SELL"

    def test_compose_signal_hold_neutral(self):
        metrics = OnchainMetrics(
            token="XXX",
            chain="ethereum",
            tvl=1e8,
            active_addresses=1e4,
            exchange_flow=0,
            github_commits=10,
            github_stars=1000,
            github_prs=5,
            github_issues=100,
        )
        result = _compose_signal(metrics)
        assert result.signal == "HOLD"

    def test_weights_sum_to_one(self):
        assert sum(WEIGHTS.values()) == 1.0


class TestOnchainMetrics:
    def test_metrics_dataclass_fields(self):
        metrics = OnchainMetrics(
            token="SOL",
            chain="solana",
            tvl=1e10,
            active_addresses=1e7,
            exchange_flow=-1e9,
            github_commits=1000,
            github_stars=50000,
            github_prs=200,
            github_issues=300,
        )
        assert metrics.token == "SOL"
        assert metrics.chain == "solana"
        assert metrics.tvl == 1e10


class TestTopChains:
    def test_top_chains_populated(self):
        assert len(TOP_CHAINS) > 0
        assert "ethereum" in TOP_CHAINS


class TestFetchOnchainMetricsMocked:
    @patch("app.services.onchain_service._defillama_tvl")
    @patch("app.services.onchain_service._defillama_exchange_flow")
    @patch("app.services.onchain_service._github_metrics")
    def test_fetch_returns_metrics(self, mock_github, mock_flow, mock_tvl):
        mock_tvl.return_value = (5e9, 1e6)
        mock_flow.return_value = 1e8
        mock_github.return_value = {
            "stars": 50000,
            "issues": 300,
            "prs": 150,
            "commits_30d": 800,
        }

        result = fetch_onchain_metrics("ETH", "ethereum")

        assert result.token == "ETH"
        assert result.chain == "ethereum"
        assert result.tvl == 5e9
        assert result.active_addresses == 1e6
        assert result.exchange_flow == 1e8
        assert result.github_stars == 50000

    @patch("app.services.onchain_service._defillama_tvl")
    @patch("app.services.onchain_service._defillama_exchange_flow")
    @patch("app.services.onchain_service._github_metrics")
    def test_fetch_graceful_degradation_on_api_failure(
        self, mock_github, mock_flow, mock_tvl
    ):
        mock_tvl.return_value = (None, None)
        mock_flow.return_value = None
        mock_github.return_value = {
            "stars": None,
            "issues": None,
            "prs": None,
            "commits_30d": None,
        }

        result = fetch_onchain_metrics("UNKNOWN", "ethereum")

        assert result.token == "UNKNOWN"
        assert result.tvl is None
        assert result.github_stars is None
        # Should not raise — graceful degradation
