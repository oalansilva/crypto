"""Testes da canonicalização do digest da prova OOS (card #504)."""

from __future__ import annotations

import pytest

from app.services.oos_promotion_proof import (
    issue_oos_promotion_proof,
    promotion_payload,
    verify_oos_promotion_proof,
)


def _payload() -> dict:
    return {
        "template_name": "multi_ma_crossover",
        "symbol": "BTCUSDT",
        "timeframe": "1d",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "period_type": "all",
        "parameters": {"fast": 7, "slow": 25},
        "metrics": {
            "trades": [8953.0, 1.5],
            "total_return": 12.25,
            "sharpe": 0.8,
        },
        "oos_metrics": {"trades": 23, "sharpe": 0.32},
        "oos_verdict": {"go": False, "reason": "poucos trades"},
    }


def _browser_roundtrip(payload: dict) -> dict:
    """Simula o round-trip JSON do browser: floats integrais viram ints."""
    import json

    rebuilt = json.loads(json.dumps(payload))

    def walk(value):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, dict):
            return {key: walk(item) for key, item in value.items()}
        if isinstance(value, list):
            return [walk(item) for item in value]
        return value

    return walk(rebuilt)


class TestCanonicalDigest:
    def test_digest_round_trip_float_integral_in_nested_structures(self):
        payload = _payload()
        digest_issue = _digest(payload)
        rebuilt = _browser_roundtrip(payload)
        assert rebuilt["metrics"]["trades"][0] == 8953
        assert _digest(rebuilt) == digest_issue

    def test_float_fractional_preserved_and_changes_digest(self):
        payload = _payload()
        digest_issue = _digest(payload)
        changed = dict(payload)
        changed["metrics"] = dict(payload["metrics"])
        changed["metrics"]["trades"] = [8953.5, 1.5]
        assert _digest(changed) != digest_issue

    def test_real_content_change_invalidates(self):
        payload = _payload()
        digest_issue = _digest(payload)
        changed = dict(payload)
        changed["metrics"] = dict(payload["metrics"])
        changed["metrics"]["sharpe"] = 0.9
        assert _digest(changed) != digest_issue

    def test_none_strings_bools_preserved(self):
        payload = {
            "a": None,
            "b": "texto",
            "c": True,
            "d": False,
            "e": {"f": None, "g": [None, "x", True]},
        }
        assert _digest(payload) == _digest(payload)
        assert _digest({"a": None}) != _digest({"a": 0})
        assert _digest({"c": True}) != _digest({"c": 1})
        assert _digest({"b": "x"}) != _digest({"b": "y"})
        assert _digest({"b": "1"}) != _digest({"b": 1})

    def test_negative_zero_canonicalized_to_int(self):
        assert _digest({"v": -0.0}) == _digest({"v": 0})

    def test_list_order_is_significant(self):
        assert _digest({"v": [1, 2]}) != _digest({"v": [2, 1]})


class TestProofEndToEnd:
    def test_emitted_float_integral_accepted_with_int_round_trip(self):
        payload = _payload()
        proof = issue_oos_promotion_proof(payload)
        rebuilt = _browser_roundtrip(payload)
        assert verify_oos_promotion_proof(proof, rebuilt)

    def test_different_content_rejected(self):
        payload = _payload()
        proof = issue_oos_promotion_proof(payload)
        changed = dict(payload)
        changed["metrics"] = dict(payload["metrics"])
        changed["metrics"]["sharpe"] = 0.9
        assert not verify_oos_promotion_proof(proof, changed)

    def test_expired_proof_rejected(self):
        payload = _payload()
        proof = _expired_proof(payload)
        assert not verify_oos_promotion_proof(proof, payload)

    def test_tampered_proof_rejected(self):
        payload = _payload()
        proof = issue_oos_promotion_proof(payload)
        assert not verify_oos_promotion_proof(proof + "x", payload)

    def test_nonexistent_proof_rejected(self):
        assert not verify_oos_promotion_proof("nada", _payload())


def _digest(payload: dict) -> str:
    from app.services.oos_promotion_proof import _canonical_digest

    return _canonical_digest(payload)


def _expired_proof(payload: dict) -> str:
    import os
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.services.oos_promotion_proof import _canonical_digest

    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "purpose": "oos-favorite-promotion",
            "digest": _canonical_digest(payload),
            "iat": now - timedelta(hours=7),
            "exp": now - timedelta(hours=1),
        },
        os.getenv("JWT_SECRET", "dev-secret-change-in-production"),
        algorithm="HS256",
    )
