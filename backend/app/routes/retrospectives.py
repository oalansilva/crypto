"""Retrospective routes — GET endpoints for viewing auto-retrospectives."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.retrospective_service import (
    RETRO_DIR,
    classification_badge,
    list_retrospectives as _list_retrospectives,
    retrospective_file_path,
)

router = APIRouter(prefix="/api/retrospectives", tags=["retrospectives"])

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class RetrospectiveSummary(BaseModel):
    slug: str
    card_id: Optional[int] = None
    feature_name: str
    date: str
    classification: str
    filename: str


class RetrospectiveListResponse(BaseModel):
    retrospectives: list[RetrospectiveSummary]
    total: int
    page: int
    per_page: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Simple HTML template for rendering markdown-like content
_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Retrospective — {title}</title>
  <style>
    :root {{
      --retro-success: #10b981;
      --retro-warning: #f59e0b;
      --retro-danger: #ef4444;
      --retro-bg-success: #d1fae5;
      --retro-bg-warning: #fef3c7;
      --retro-bg-danger: #fee2e2;
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #e2e8f0;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; padding: 2rem; }}
    .container {{ max-width: 900px; margin: 0 auto; }}
    h1, h2, h3 {{ color: #f8fafc; margin-top: 1.5em; margin-bottom: 0.5em; }}
    h1 {{ font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
    th, td {{ padding: 0.5rem 0.75rem; text-align: left; border: 1px solid var(--border); }}
    th {{ background: var(--card-bg); color: var(--text-muted); font-weight: 600; }}
    tr:nth-child(even) td {{ background: rgba(255,255,255,0.02); }}
    .badge {{
      display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px;
      font-size: 0.875rem; font-weight: 600;
    }}
    .badge-success {{ background: var(--retro-bg-success); color: var(--retro-success); }}
    .badge-warning {{ background: var(--retro-bg-warning); color: var(--retro-warning); }}
    .badge-danger {{ background: var(--retro-bg-danger); color: var(--retro-danger); }}
    .meta {{ display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; margin: 0.5rem 0; color: var(--text-muted); font-size: 0.875rem; }}
    hr {{ border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }}
    .footer {{ margin-top: 2rem; color: var(--text-muted); font-size: 0.75rem; text-align: center; }}
    a {{ color: #60a5fa; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    ul {{ padding-left: 1.5rem; }}
    li {{ margin: 0.25rem 0; }}
    strong {{ color: #f8fafc; }}
    p {{ margin: 0.5rem 0; }}
    .back-link {{ margin-bottom: 1rem; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="back-link">
      <a href="/api/retrospectives">&larr; Voltar ao Histórico</a>
    </div>
    <div id="content">{content}</div>
    <div class="footer">Gerado automaticamente por auto-retrospective</div>
  </div>
</body>
</html>
"""


def _badge_html(cls: str) -> str:
    """Return HTML badge for a classification."""
    labels = {
        "sem_problemas": ("🟢 Sem Problemas", "badge-success"),
        "com_ressalvas": ("🟡 Com Ressalvas", "badge-warning"),
        "problemática": ("🔴 Problemática", "badge-danger"),
    }
    label, cls_name = labels.get(cls, (cls, "badge-success"))
    return f'<span class="badge {cls_name}">{label}</span>'


def _markdown_to_html(text: str) -> str:
    """Convert simple markdown to HTML."""
    import re

    # Escape HTML
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Headers
    text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Tables (simple)
    lines = text.split("\n")
    in_table = False
    result_lines = []
    for line in lines:
        if line.startswith("|") and "---" not in line:
            if not in_table:
                result_lines.append("<table>")
                in_table = True
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if any("Campo" in c or "Stage" in c or "Indicador" in c for c in cols):
                result_lines.append("<thead>")
                result_lines.append("<tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr>")
                result_lines.append("</thead>")
                result_lines.append("<tbody>")
            else:
                result_lines.append("<tr>" + "".join(f"<td>{c}</td>" for c in cols) + "</tr>")
        elif in_table:
            result_lines.append("</tbody></table>")
            in_table = False
            result_lines.append(line)
        else:
            result_lines.append(line)

    if in_table:
        result_lines.append("</tbody></table>")

    text = "\n".join(result_lines)

    # Horizontal rule
    text = re.sub(r"^---$", "<hr>", text, flags=re.MULTILINE)

    # Paragraphs
    paragraphs = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block.startswith("<h") or block.startswith("<table") or block.startswith("<hr"):
            paragraphs.append(block)
        else:
            # Convert line breaks in block
            block = block.replace("\n", "<br>")
            paragraphs.append(f"<p>{block}</p>")

    return "\n".join(paragraphs)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("", response_model=RetrospectiveListResponse)
def list_retrospectives(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
):
    """List all retrospectives with pagination."""
    return _list_retrospectives(page=page, per_page=per_page)


@router.get("/{slug}")
def get_retrospective(
    slug: str,
    format: Literal["markdown", "html"] = Query(default="html"),
):
    """Get a specific retrospective by slug (change_id).

    The slug is the change_id portion of the filename (date-change_id.md).
    Query param format=markdown|html (default: html).
    """
    # Find the file
    filepath = retrospective_file_path(slug)
    if not filepath:
        raise HTTPException(status_code=404, detail="Retrospective não encontrada")

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler retrospectiva: {e}")

    if format == "markdown":
        return {"slug": slug, "content": content, "format": "markdown"}

    # HTML format
    # Extract title
    import re

    title_match = re.search(r"^# 📋 Retrospective — (.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else slug

    # Determine classification for badge
    classification = "sem_problemas"
    if "🟡" in content:
        classification = "com_ressalvas"
    elif "🔴" in content:
        classification = "problemática"

    # Extract meta line
    meta_match = re.search(r"\*\*Card:\*\* #(\d+)", content)
    card_str = f"Card #{meta_match.group(1)}" if meta_match else ""

    date_match = re.search(r"\*\*Data:\*\* (\d{4}-\d{2}-\d{2})", content)
    date_str = date_match.group(1) if date_match else ""

    badge_html = _badge_html(classification)

    meta_html = f'<div class="meta"><span>{card_str}</span><span>Data: {date_str}</span><span>{badge_html}</span></div>'

    # Convert markdown to HTML
    body_html = _markdown_to_html(content)

    # Remove the header line (already displayed as title)
    body_html = re.sub(r"<h1>.*?</h1>", "", body_html, count=1)

    html_content = f'<div class="meta">{meta_html}</div>' + body_html

    html = _HTML_TEMPLATE.format(title=title, content=html_content)

    return {"slug": slug, "content": html, "format": "html"}
