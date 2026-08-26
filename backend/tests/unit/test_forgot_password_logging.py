"""Forgot-password INFO não vaza e-mail, token nem link (card #686)."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import MagicMock

import app.routes.auth as auth_routes


def test_forgot_password_info_omits_email_token_and_link(caplog):
    email = "reset-user@example.com"
    user = SimpleNamespace(email=email)
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = user

    with caplog.at_level(logging.INFO, logger=auth_routes.logger.name):
        response = auth_routes.forgot_password(
            auth_routes.ForgotPasswordRequest(email=email),
            db=db,
        )

    assert "reset link" in response.message.lower() or "If the email exists" in response.message
    info_text = "\n".join(
        record.getMessage() for record in caplog.records if record.levelno == logging.INFO
    )
    assert info_text, "expected at least one INFO log for existing user"
    assert email not in info_text
    assert "simulated-token" not in info_text
    assert "token=" not in info_text
    assert "reset-password" not in info_text
    assert "http://" not in info_text
    assert "https://" not in info_text
