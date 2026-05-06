from __future__ import annotations

from backend.scripts.cleanup_beta_test_users import (
    build_summary,
    mask_email,
    parse_allowed_emails,
)


def test_parse_allowed_emails_defaults_to_alan_accounts():
    assert parse_allowed_emails(None) == {
        "o.alan.silva@gmail.com",
        "o2.alan.silva@gmail.com",
    }


def test_parse_allowed_emails_accepts_repeated_and_comma_separated_values():
    assert parse_allowed_emails(["A@Example.com,b@example.com", " c@example.com "]) == {
        "a@example.com",
        "b@example.com",
        "c@example.com",
    }


def test_mask_email_hides_local_part_but_preserves_domain():
    assert mask_email("visitor@example.com") == "vi***r@example.com"
    assert mask_email("x@example.com") == "x***@example.com"


def test_build_summary_classifies_allowed_and_unauthorized_active_users():
    rows = [
        {
            "id": "1",
            "email": "o.alan.silva@gmail.com",
            "status": "active",
            "is_banned": False,
        },
        {
            "id": "2",
            "email": "test@example.com",
            "status": "active",
            "is_banned": False,
        },
        {
            "id": "3",
            "email": "old-test@example.com",
            "status": "banned",
            "is_banned": True,
        },
    ]

    summary = build_summary(rows, {"o.alan.silva@gmail.com", "o2.alan.silva@gmail.com"})

    assert summary["total_users"] == 3
    assert summary["allowed_users"] == 1
    assert summary["unauthorized_users"] == 2
    assert summary["unauthorized_active"] == 1
    assert summary["unauthorized_active_masked"] == ["te***t@example.com"]
    assert summary["allowed_missing"] == ["o2***a@gmail.com"]
