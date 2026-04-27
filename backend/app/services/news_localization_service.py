from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

LOCALIZATION_CACHE_TTL_SECONDS = float(os.getenv("AI_DASHBOARD_NEWS_CACHE_TTL_SECONDS") or "900")

_LOCALIZATION_CACHE: dict[str, Any] = {
    "fingerprint": tuple(),
    "localized_by_id": {},
    "expires_at": 0.0,
}
_CACHE_LOCK = asyncio.Lock()
_REFRESH_TASK: asyncio.Task | None = None


def _fallback_summary(title: str, source: str) -> str:
    normalized_title = str(title or "").strip()
    normalized_source = str(source or "").strip()
    if not normalized_title:
        return "Resumo indisponível no momento."
    if normalized_source:
        return f"Resumo automático indisponível. Fonte original: {normalized_source}."
    return "Resumo automático indisponível."


def _build_fingerprint(news_items: list[dict[str, Any]]) -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            str(item.get("id") or ""),
            str(item.get("title") or ""),
        )
        for item in news_items
        if isinstance(item, dict)
    )


def get_cached_localized_news(
    news_items: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, str]], bool]:
    fingerprint = _build_fingerprint(news_items)
    now = time.time()
    same_fingerprint = bool(fingerprint and _LOCALIZATION_CACHE.get("fingerprint") == fingerprint)
    localized_by_id = (_LOCALIZATION_CACHE.get("localized_by_id") or {}) if same_fingerprint else {}
    is_fresh = bool(same_fingerprint and float(_LOCALIZATION_CACHE.get("expires_at") or 0) > now)
    return dict(localized_by_id), is_fresh


async def _refresh_localized_news_cache(news_items: list[dict[str, Any]]) -> None:
    fingerprint = _build_fingerprint(news_items)
    localized_items = await localize_news_items(news_items)
    localized_by_id = {
        str(item.get("id") or ""): {
            "title_pt": str(item.get("title_pt") or ""),
            "summary_pt": str(item.get("summary_pt") or ""),
        }
        for item in localized_items
        if isinstance(item, dict)
    }
    async with _CACHE_LOCK:
        _LOCALIZATION_CACHE["fingerprint"] = fingerprint
        _LOCALIZATION_CACHE["localized_by_id"] = localized_by_id
        _LOCALIZATION_CACHE["expires_at"] = time.time() + LOCALIZATION_CACHE_TTL_SECONDS


def schedule_news_localization_refresh(news_items: list[dict[str, Any]]) -> None:
    global _REFRESH_TASK

    items = [item for item in news_items if isinstance(item, dict)]
    if not items:
        return

    localized_by_id, is_fresh = get_cached_localized_news(items)
    fingerprint = _build_fingerprint(items)
    if is_fresh and localized_by_id:
        return
    if _REFRESH_TASK and not _REFRESH_TASK.done():
        current_fingerprint = _LOCALIZATION_CACHE.get("fingerprint")
        if current_fingerprint == fingerprint:
            return

    async def _runner() -> None:
        try:
            await _refresh_localized_news_cache(items)
        except Exception as exc:
            logger.warning("News localization cache refresh failed: %r", exc)

    try:
        _REFRESH_TASK = asyncio.create_task(_runner())
    except RuntimeError:
        logger.debug("News localization cache refresh skipped: no running event loop")


async def localize_news_items(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return local news titles and fallback summaries without paid external services."""

    items = [item for item in news_items if isinstance(item, dict)]
    if not items:
        return []

    return [
        {
            "id": str(item.get("id") or ""),
            "title_pt": str(item.get("title") or ""),
            "summary_pt": _fallback_summary(
                str(item.get("title") or ""), str(item.get("source") or "")
            ),
        }
        for item in items
    ]
