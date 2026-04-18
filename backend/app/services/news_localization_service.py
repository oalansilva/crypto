from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from typing import Any

import httpx

from app.database import SessionLocal
from app.services.system_preferences_service import MINIMAX_API_KEY_KEY, get_system_preference_value

logger = logging.getLogger(__name__)

MINIMAX_BASE_URL = str(os.getenv("MINIMAX_BASE_URL") or "https://api.minimax.io/v1").rstrip("/")
MINIMAX_MODEL = str(os.getenv("MINIMAX_MODEL") or "MiniMax-M2.7").strip()
REQUEST_TIMEOUT_SECONDS = float(os.getenv("MINIMAX_TIMEOUT_SECONDS") or "45")
LOCALIZATION_CACHE_TTL_SECONDS = float(os.getenv("AI_DASHBOARD_NEWS_CACHE_TTL_SECONDS") or "900")

_LOCALIZATION_CACHE: dict[str, Any] = {
    "fingerprint": tuple(),
    "localized_by_id": {},
    "expires_at": 0.0,
}
_CACHE_LOCK = asyncio.Lock()
_REFRESH_TASK: asyncio.Task | None = None


def _get_minimax_api_key() -> str:
    db = SessionLocal()
    try:
        stored = get_system_preference_value(db, MINIMAX_API_KEY_KEY)
    finally:
        db.close()
    return stored or str(os.getenv("MINIMAX_API_KEY") or "").strip()


def _fallback_summary(title: str, source: str) -> str:
    normalized_title = str(title or "").strip()
    normalized_source = str(source or "").strip()
    if not normalized_title:
        return "Resumo indisponível no momento."
    if normalized_source:
        return f"Resumo automático indisponível. Fonte original: {normalized_source}."
    return "Resumo automático indisponível."


def _extract_json_object(raw_content: str) -> str:
    text = str(raw_content or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _parse_localized_content(raw_content: str) -> tuple[str, str]:
    text = _extract_json_object(raw_content)
    if not text:
        return "", ""

    try:
        parsed = json.loads(text)
        return (
            str(parsed.get("title_pt") or "").strip(),
            str(parsed.get("summary_pt") or "").strip(),
        )
    except Exception:
        pass

    title_match = re.search(r"TITLE_PT:\s*(.+)", text, re.IGNORECASE)
    summary_match = re.search(r"SUMMARY_PT:\s*(.+)", text, re.IGNORECASE | re.DOTALL)
    if title_match or summary_match:
        return (
            str(title_match.group(1) if title_match else "").strip(),
            str(summary_match.group(1) if summary_match else "").strip(),
        )

    lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
    if not lines:
        return "", ""
    if len(lines) == 1:
        return "", lines[0]
    return lines[0], " ".join(lines[1:])


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
            logger.warning("MiniMax background refresh failed: %r", exc)

    try:
        _REFRESH_TASK = asyncio.create_task(_runner())
    except RuntimeError:
        logger.debug("MiniMax background refresh skipped: no running event loop")


async def localize_news_items(news_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate titles and generate short Portuguese summaries using MiniMax when configured."""

    items = [item for item in news_items if isinstance(item, dict)]
    if not items:
        return []

    minimax_api_key = _get_minimax_api_key()
    if not minimax_api_key:
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

    prompt = (
        "Voce eh um editor financeiro em portugues do Brasil. "
        "Traduza o titulo para portugues e escreva um resumo curto em portugues, "
        "em no maximo 2 frases, sem inventar fatos e sem mencionar traducao. "
        "Responda somente com duas linhas neste formato exato:\n"
        "TITLE_PT: <titulo em portugues>\n"
        "SUMMARY_PT: <resumo em portugues>"
    )
    retry_prompt = (
        "Voce deve responder obrigatoriamente com exatamente duas linhas, sem markdown e sem cercas de codigo.\n"
        "Linha 1: TITLE_PT: <titulo em portugues do Brasil>\n"
        "Linha 2: SUMMARY_PT: <resumo em portugues do Brasil em ate 2 frases>\n"
        "Nao deixe nenhum dos dois campos vazio e nao invente fatos."
    )

    async def _request_localization(
        item_id: str,
        title: str,
        source: str,
        sentiment: str,
        related_asset: Any,
        client: httpx.AsyncClient,
        instruction: str,
    ) -> tuple[str, str]:
        body = {
            "model": MINIMAX_MODEL,
            "messages": [
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "id": item_id,
                            "title": title,
                            "source": source,
                            "sentiment": sentiment,
                            "related_asset": related_asset,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "temperature": 0.1,
            "max_tokens": 220,
        }
        response = await client.post(
            f"{MINIMAX_BASE_URL}/text/chatcompletion_v2",
            headers={
                "Authorization": f"Bearer {minimax_api_key}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("choices") or []
        message = (candidates[0] or {}).get("message") or {}
        content = message.get("content")
        if isinstance(content, list):
            text_parts = [str(part.get("text") or "") for part in content if isinstance(part, dict)]
            content = "\n".join(part for part in text_parts if part)
        return _parse_localized_content(str(content or ""))

    async def _localize_one(item: dict[str, Any], client: httpx.AsyncClient) -> dict[str, str]:
        item_id = str(item.get("id") or "")
        title = str(item.get("title") or "")
        source = str(item.get("source") or "")
        sentiment = str(item.get("sentiment") or "")
        related_asset = item.get("related_asset")

        try:
            parsed_title, parsed_summary = await _request_localization(
                item_id=item_id,
                title=title,
                source=source,
                sentiment=sentiment,
                related_asset=related_asset,
                client=client,
                instruction=prompt,
            )
            if not parsed_title or not parsed_summary:
                retry_title, retry_summary = await _request_localization(
                    item_id=item_id,
                    title=title,
                    source=source,
                    sentiment=sentiment,
                    related_asset=related_asset,
                    client=client,
                    instruction=retry_prompt,
                )
                parsed_title = parsed_title or retry_title
                parsed_summary = parsed_summary or retry_summary
            return {
                "id": item_id,
                "title_pt": parsed_title or title,
                "summary_pt": parsed_summary or _fallback_summary(title, source),
            }
        except Exception as exc:
            logger.warning("MiniMax news localization failed for %s: %r", item_id, exc)
            return {
                "id": item_id,
                "title_pt": title,
                "summary_pt": _fallback_summary(title, source),
            }

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        localized_items = await asyncio.gather(*[_localize_one(item, client) for item in items])

    return localized_items
