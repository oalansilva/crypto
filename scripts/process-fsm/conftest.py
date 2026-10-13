"""Harness tests select their client explicitly, never inherit the invoking host."""
import pytest


@pytest.fixture(autouse=True)
def isolated_client_context(monkeypatch):
    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)
    monkeypatch.delenv("COVENANT_CLIENT", raising=False)
