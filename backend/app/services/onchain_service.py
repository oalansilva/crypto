# file: backend/app/services/onchain_service.py
"""
Onchain signal service — fetches DeFiLlama + GitHub data, composes BUY/SELL/HOLD signals.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import requests

from app.database import SessionLocal
from app.models_onchain import OnchainSignal, OnchainSignalHistory, sao_paulo_now


SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOP_CHAINS = ["ethereum", "solana", "arbitrum", "base", "matic"]

# Map chain slug → DeFiLlama chain identifier and GitHub repo
CHAIN_META: dict[str, dict[str, str]] = {
    "ethereum":  {"defillama": "ethereum",  "github": "ethereum/go-ethereum"},
    "solana":    {"defillama": "solana",     "github": "solana-labs/solana"},
    "arbitrum":  {"defillama": "arbitrum",   "github": "arbitrum/arbos"},
    "base":      {"defillama": "base",       "github": "base-org/base"},
    "matic":     {"defillama": "matic",      "github": "matic-network/libp2p"},
}

# Scoring weights (must sum to 1.0)
WEIGHTS = {
    "tvl":              0.25,
    "active_addresses": 0.20,
    "exchange_flow":     0.20,
    "github_commits":    0.15,
    "github_stars":      0.10,
    "github_issues":     0.10,
}

# Proxy min/max ranges for normalisation (updated dynamically as data arrives)
NORM_RANGES: dict[str, tuple[float, float]] = {
    "tvl":              (1e6,   1e10),   # $1M – $10B
    "active_addresses": (100,   1e7),    # 100 – 10M
    "exchange_flow":     (-1e9, 1e9),    # -$1B – $1B
    "github_commits":    (0,     5000),   # 0 – 5000/month
    "github_stars":      (0,     5e5),    # 0 – 500k
    "github_issues":     (0,     5000),   # 0 – 5000 open
}

HTTP_TIMEOUT = 10

# ---------------------------------------------------------------------------
# In-memory cache (5-min TTL)
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[float, dict]] = {}  # key → (expires_at, data)


def _cache_get(key: str) -> dict | None:
    if key in _cache:
        expires, data = _cache[key]
        if time.time() < expires:
            return data
        del _cache[key]
    return None


def _cache_set(key: str, data: dict, ttl: int = 300) -> None:
    _cache[key] = (time.time() + ttl, data)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class OnchainMetrics:
    token: str
    chain: str
    tvl: float | None
    active_addresses: float | None
    exchange_flow: float | None
    github_commits: int | None
    github_stars: int | None
    github_prs: int | None
    github_issues: int | None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(SAO_PAULO_TZ))


@dataclass
class SignalResult:
    signal: str          # BUY | SELL | HOLD
    confidence: int      # 0-100
    breakdown: dict[str, float]
    metrics: OnchainMetrics
    timestamp: datetime


# ---------------------------------------------------------------------------
# External API fetchers
# ---------------------------------------------------------------------------


def _defillama_tvl(chain: str) -> tuple[float | None, float | None]:
    """Return (tvl, active_addresses_estimate) for a chain from DeFiLlama."""
    cached = _cache_get(f"defillama_{chain}")
    if cached:
        return cached["tvl"], cached.get("active_addresses")

    meta = CHAIN_META.get(chain.lower(), {})
    dl_chain = meta.get("defillama", chain.lower())

    url = f"https://api.llama.fi/chains"
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        chains_data = resp.json()
        if isinstance(chains_data, list):
            for item in chains_data:
                if isinstance(item, dict) and item.get("slug", "").lower() == dl_chain.lower():
                    tvl = item.get("tvl")
                    # DeFiLlama doesn't expose active addresses directly;
                    # use a proxy: TVL per chain as proxy for ecosystem size
                    active_addresses = item.get("chain_bridge_count", tvl)
                    result = {"tvl": tvl, "active_addresses": active_addresses}
                    _cache_set(f"defillama_{chain}", result)
                    return tvl, active_addresses
    except Exception as e:
        print(f"[onchain] DeFiLlama error for {chain}: {e}")

    return None, None


def _defillama_exchange_flow(chain: str) -> float | None:
    """Return exchange flow (inflow - outflow) for a chain. Positive = net inflow (sell pressure)."""
    # DeFiLlama public API doesn't expose real-time flow data.
    # For MVP: use 7-day change in TVL as proxy for net flow direction.
    cached = _cache_get(f"defillama_flow_{chain}")
    if cached:
        return cached.get("flow")

    meta = CHAIN_META.get(chain.lower(), {})
    dl_chain = meta.get("defillama", chain.lower())

    url = f"https://api.llama.fi/charts/{dl_chain}"
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) >= 2:
            current_tvl = data[-1].get("tvl", 0)
            older_tvl = data[0].get("tvl", 0)
            flow = current_tvl - older_tvl if current_tvl and older_tvl else 0
            result = {"flow": flow}
            _cache_set(f"defillama_flow_{chain}", result)
            return flow
    except Exception as e:
        print(f"[onchain] DeFiLlama flow error for {chain}: {e}")

    return None


def _github_metrics(repo: str) -> dict[str, int | None]:
    """Return {stars, issues, prs, commits_30d} from GitHub public API."""
    cached = _cache_get(f"github_{repo}")
    if cached:
        return cached

    headers = {"Accept": "application/vnd.github.v3+json"}
    result: dict[str, int | None] = {
        "stars": None,
        "issues": None,
        "prs": None,
        "commits_30d": None,
    }

    # Repo metadata
    url = f"https://api.github.com/repos/{repo}"
    try:
        resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            result["stars"] = data.get("stargazers_count")
            result["issues"] = data.get("open_issues_count")
    except Exception as e:
        print(f"[onchain] GitHub metadata error for {repo}: {e}")

    # Commit activity (last 4 weeks)
    commits_url = f"https://api.github.com/repos/{repo}/commits"
    try:
        resp = requests.get(
            commits_url,
            headers=headers,
            params={"since": (datetime.now(timezone.utc).timestamp() - 30 * 86400)},
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code == 200:
            result["commits_30d"] = len(resp.json())
    except Exception as e:
        print(f"[onchain] GitHub commits error for {repo}: {e}")

    _cache_set(f"github_{repo}", result)
    return result


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _normalize(value: float | None, key: str) -> float:
    if value is None:
        return 0.0
    mn, mx = NORM_RANGES.get(key, (0.0, 1.0))
    if mx == mn:
        return 0.0
    normalized = (value - mn) / (mx - mn)
    return max(0.0, min(1.0, normalized))


# ---------------------------------------------------------------------------
# Score composition
# ---------------------------------------------------------------------------


def _compose_signal(metrics: OnchainMetrics) -> SignalResult:
    """Compute BUY/SELL/HOLD signal from onchain metrics."""

    raw = {
        "tvl":              metrics.tvl or 0,
        "active_addresses": metrics.active_addresses or 0,
        "exchange_flow":    metrics.exchange_flow or 0,
        "github_commits":   metrics.github_commits or 0,
        "github_stars":     metrics.github_stars or 0,
        "github_issues":    metrics.github_issues or 0,
    }

    # Normalise
    norm = {k: _normalize(raw[k], k) for k in WEIGHTS}

    # Weighted score (0–1)
    score = sum(WEIGHTS[k] * norm[k] for k in WEIGHTS)

    # Breakdown (contribution of each metric)
    breakdown = {k: round(WEIGHTS[k] * norm[k] * 100, 1) for k in WEIGHTS}

    # Signal logic
    exchange_flow = raw["exchange_flow"]
    addr_change = norm["active_addresses"]  # proxy for growth
    tvl_change = norm["tvl"]

    if exchange_flow > 0 and addr_change > 0.5 and tvl_change > 0.5:
        signal = "BUY"
    elif exchange_flow < -0.2 and addr_change < 0.4 and tvl_change < 0.4:
        signal = "SELL"
    else:
        signal = "HOLD"

    confidence = int(round(score * 100))

    return SignalResult(
        signal=signal,
        confidence=confidence,
        breakdown=breakdown,
        metrics=metrics,
        timestamp=metrics.fetched_at,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def fetch_onchain_metrics(token: str, chain: str) -> OnchainMetrics:
    """Fetch all onchain metrics for a given token+chain."""
    chain = chain.lower()
    meta = CHAIN_META.get(chain, {})
    github_repo = meta.get("github", "")

    tvl, active_addresses = _defillama_tvl(chain)
    exchange_flow = _defillama_exchange_flow(chain)

    github = _github_metrics(github_repo) if github_repo else {}

    return OnchainMetrics(
        token=token.upper(),
        chain=chain,
        tvl=tvl,
        active_addresses=active_addresses,
        exchange_flow=exchange_flow,
        github_commits=github.get("commits_30d"),
        github_stars=github.get("stars"),
        github_prs=github.get("prs"),
        github_issues=github.get("issues"),
    )


def compose_onchain_signal(token: str, chain: str) -> SignalResult:
    """Fetch metrics and compute signal for token+chain."""
    metrics = fetch_onchain_metrics(token, chain)
    return _compose_signal(metrics)


def save_onchain_signal(token: str, chain: str, result: SignalResult) -> OnchainSignal:
    """Persist latest metrics snapshot to onchain_signals table."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        sig_id = f"{token.upper()}_{chain.lower()}_{int(time.time())}"
        now = sao_paulo_now()

        existing = db.query(OnchainSignal).filter(
            OnchainSignal.token == token.upper(),
            OnchainSignal.chain == chain.lower(),
        ).first()

        if existing:
            existing.tvl = result.metrics.tvl
            existing.active_addresses = result.metrics.active_addresses
            existing.exchange_flow = result.metrics.exchange_flow
            existing.github_commits = result.metrics.github_commits
            existing.github_stars = result.metrics.github_stars
            existing.github_prs = result.metrics.github_prs
            existing.github_issues = result.metrics.github_issues
            existing.updated_at = now
            saved = existing
        else:
            saved = OnchainSignal(
                id=sig_id,
                token=token.upper(),
                chain=chain.lower(),
                tvl=result.metrics.tvl,
                active_addresses=result.metrics.active_addresses,
                exchange_flow=result.metrics.exchange_flow,
                github_commits=result.metrics.github_commits,
                github_stars=result.metrics.github_stars,
                github_prs=result.metrics.github_prs,
                github_issues=result.metrics.github_issues,
                created_at=now,
                updated_at=now,
            )
            db.add(saved)

        # Always record history
        history_id = str(uuid.uuid4())
        history = OnchainSignalHistory(
            id=history_id,
            token=token.upper(),
            chain=chain.lower(),
            signal_type=result.signal,
            confidence=result.confidence,
            breakdown=json.dumps(result.breakdown),
            status="ativo",
            tvl=result.metrics.tvl,
            active_addresses=result.metrics.active_addresses,
            exchange_flow=result.metrics.exchange_flow,
            github_commits=result.metrics.github_commits,
            github_stars=result.metrics.github_stars,
            github_prs=result.metrics.github_prs,
            github_issues=result.metrics.github_issues,
            created_at=result.timestamp,
            updated_at=now,
        )
        db.add(history)

        db.commit()
        db.refresh(saved)
        return saved
    except Exception as e:
        db.rollback()
        print(f"[onchain] save error: {e}")
        raise
    finally:
        db.close()


def get_onchain_history(
    token: str | None = None,
    chain: str | None = None,
    signal_type: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[OnchainSignalHistory], int]:
    """Return paginated onchain signal history."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        q = db.query(OnchainSignalHistory).filter(OnchainSignalHistory.archived == "no")
        if token:
            q = q.filter(OnchainSignalHistory.token == token.upper())
        if chain:
            q = q.filter(OnchainSignalHistory.chain == chain.lower())
        if signal_type:
            q = q.filter(OnchainSignalHistory.signal_type == signal_type.upper())

        total = q.count()
        rows = (
            q.order_by(OnchainSignalHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return rows, total
    finally:
        db.close()


def get_onchain_performance() -> dict[str, Any]:
    """Compute hit-rate and avg confidence from onchain signal history."""
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        rows = (
            db.query(OnchainSignalHistory)
            .filter(
                OnchainSignalHistory.archived == "no",
                OnchainSignalHistory.status.in_(["disparado", "expirado", "ativo"]),
            )
            .all()
        )

        total = len(rows)
        if total == 0:
            return {"total_signals": 0, "win_rate": 0.0, "avg_confidence": 0.0, "expired_rate": 0.0}

        disparados = [r for r in rows if r.status == "disparado"]
        winners = [
            r
            for r in disparados
            if getattr(r, "outcome_24h", None) in ("win", "WIN", "buy", "BUY")
        ]
        win_rate = round(len(winners) / len(disparados) * 100, 2) if disparados else 0.0

        expirados = [r for r in rows if r.status == "expirado"]
        expired_rate = round(len(expirados) / total * 100, 2)

        avg_confidence = round(sum(r.confidence for r in rows) / total, 2)

        return {
            "total_signals": total,
            "win_rate": win_rate,
            "avg_confidence": avg_confidence,
            "expired_rate": expired_rate,
            "by_signal_type": {
                st: {
                    "count": sum(1 for r in rows if r.signal_type == st),
                    "avg_confidence": round(
                        sum(r.confidence for r in rows if r.signal_type == st)
                        / max(1, sum(1 for r in rows if r.signal_type == st)),
                        2,
                    ),
                }
                for st in ("BUY", "SELL", "HOLD")
            },
        }
    finally:
        db.close()
