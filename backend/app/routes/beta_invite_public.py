"""Public entry surface of the invite flow (card #689, D3).

``GET /beta-invite/<token>`` serves the password-definition form for the
invited address (pre-filled and locked by the invite) and ``POST`` of the same
route consumes the invite once and defines the owner's password.  This is a
new surface of the invite flow itself -- never a catalog route
(``/monitor``, ``/favorites``, ``/combo/*``) and never the ``landing`` surface.
"""

from __future__ import annotations

import html
import logging

from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.beta_access import BETA_ACCESS_APP_URL
from app.services.beta_invites import (
    SOURCE_INVITE_LINK,
    STATE_EMAIL_MISMATCH,
    STATE_MESSAGES,
    STATE_STATUS_CODES,
    STATE_VALID,
    InviteConsumptionError,
    classify_invite,
    consume_invite,
    find_invite_by_token,
    normalize_email,
    record_invite_refusal,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["beta-invite"])

MIN_PASSWORD_LENGTH = 8
MAX_NAME_LENGTH = 120

_PAGE_STYLE = """
:root { color-scheme: light dark; }
body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  background: #0b1220; color: #f3f6fc; display: flex; min-height: 100vh;
  align-items: center; justify-content: center; padding: 24px; }
main { width: 100%; max-width: 420px; background: #131c2f; border: 1px solid #24314d;
  border-radius: 16px; padding: 28px; box-shadow: 0 18px 40px rgba(0,0,0,.35); }
h1 { font-size: 1.25rem; margin: 0 0 8px; }
p { line-height: 1.5; margin: 0 0 16px; color: #c3cee3; }
label { display: block; font-size: .85rem; margin: 14px 0 6px; color: #c3cee3; }
input { width: 100%; box-sizing: border-box; padding: 11px 12px; border-radius: 10px;
  border: 1px solid #2f3d5c; background: #0e1626; color: #f3f6fc; font-size: 1rem; }
input[readonly] { opacity: .8; }
button { width: 100%; margin-top: 20px; padding: 12px; border: 0; border-radius: 10px;
  background: #3b82f6; color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer; }
button:hover { background: #2f6fd8; }
a { color: #7fb0ff; }
.alert { border-radius: 10px; padding: 12px; margin: 0 0 16px; font-size: .95rem; }
.alert-error { background: #3a1620; border: 1px solid #7f2233; color: #ffd7de; }
.alert-ok { background: #12291f; border: 1px solid #1f6b48; color: #d3f7e4; }
"""


def _page(*, title: str, body: str, status_code: int = 200) -> HTMLResponse:
    document = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{html.escape(title)}</title>
<style>{_PAGE_STYLE}</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>"""
    return HTMLResponse(content=document, status_code=status_code)


def _refusal_page(state: str, message: str | None = None) -> HTMLResponse:
    detail = html.escape(message or STATE_MESSAGES.get(state, "Convite inválido."))
    body = (
        "<h1>Convite indisponível</h1>"
        f'<p class="alert alert-error" role="alert">{detail}</p>'
        f'<p><a href="{html.escape(BETA_ACCESS_APP_URL)}">Ir para a página de entrada</a></p>'
    )
    return _page(
        title="Convite indisponível",
        body=body,
        status_code=STATE_STATUS_CODES.get(state, 400),
    )


def _form_page(
    *,
    token: str,
    bound_email: str,
    error: str | None = None,
) -> HTMLResponse:
    escaped_email = html.escape(bound_email)
    error_block = (
        f'<p class="alert alert-error" role="alert">{html.escape(error)}</p>' if error else ""
    )
    body = f"""<h1>Defina sua senha</h1>
<p>Este convite é de uso único e pertence a <strong>{escaped_email}</strong>.</p>
{error_block}
<form method="post" action="/beta-invite/{html.escape(token)}">
  <label for="name">Nome (opcional)</label>
  <input id="name" name="name" type="text" maxlength="{MAX_NAME_LENGTH}" autocomplete="name">
  <label for="email">E-mail do convite</label>
  <input id="email" name="email" type="email" value="{escaped_email}" readonly aria-readonly="true" required>
  <label for="password">Nova senha</label>
  <input id="password" name="password" type="password" minlength="{MIN_PASSWORD_LENGTH}" autocomplete="new-password" required>
  <label for="passwordConfirm">Confirme a nova senha</label>
  <input id="passwordConfirm" name="passwordConfirm" type="password" minlength="{MIN_PASSWORD_LENGTH}" autocomplete="new-password" required>
  <button type="submit">Definir senha e entrar</button>
</form>"""
    return _page(title="Defina sua senha", body=body)


def _success_page(*, email: str) -> HTMLResponse:
    body = (
        "<h1>Acesso liberado</h1>"
        '<p class="alert alert-ok" role="status">'
        f"Sua senha foi definida para {html.escape(email)}.</p>"
        f'<p><a href="{html.escape(BETA_ACCESS_APP_URL)}">Entrar agora</a></p>'
    )
    return _page(title="Acesso liberado", body=body)


@router.get("/beta-invite/{token}", response_class=HTMLResponse)
def beta_invite_form(token: str, db: Session = Depends(get_db)):
    invite = find_invite_by_token(db, token)
    bound_email = normalize_email(invite.email) if invite else ""
    state = classify_invite(db, invite, email=bound_email or None)
    if state != STATE_VALID:
        record_invite_refusal(
            db,
            invite=invite,
            email=bound_email,
            state=state,
            source=SOURCE_INVITE_LINK,
        )
        db.commit()
        return _refusal_page(state)
    return _form_page(token=token, bound_email=bound_email)


@router.post("/beta-invite/{token}", response_class=HTMLResponse)
async def beta_invite_consume(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    # The form is a plain HTML urlencoded POST.  The body is parsed here so the
    # surface needs no extra runtime dependency (python-multipart is not part of
    # the backend requirements).
    raw_body = (await request.body()).decode("utf-8", "replace")
    fields = {
        key: values[0]
        for key, values in parse_qs(raw_body, keep_blank_values=True).items()
        if values
    }
    email = fields.get("email", "")
    password = fields.get("password", "")
    password_confirm = fields.get("passwordConfirm", "")
    name = fields.get("name") or None

    invite = find_invite_by_token(db, token)
    bound_email = normalize_email(invite.email) if invite else ""

    if normalize_email(email) != bound_email or not bound_email:
        state = STATE_EMAIL_MISMATCH if bound_email else classify_invite(db, invite, email=None)
        record_invite_refusal(
            db,
            invite=invite,
            email=email,
            state=state,
            source=SOURCE_INVITE_LINK,
        )
        db.commit()
        return _refusal_page(state)

    if len(password) < MIN_PASSWORD_LENGTH:
        return _form_page(
            token=token,
            bound_email=bound_email,
            error=f"A senha precisa ter pelo menos {MIN_PASSWORD_LENGTH} caracteres.",
        )
    if password != password_confirm:
        return _form_page(
            token=token,
            bound_email=bound_email,
            error="As duas senhas não conferem.",
        )

    try:
        consumption = consume_invite(
            db,
            token=token,
            email=bound_email,
            password=password,
            name=name,
            source=SOURCE_INVITE_LINK,
        )
    except InviteConsumptionError as exc:
        logger.info("Beta invite consumption refused: %s", exc.state)
        return _refusal_page(exc.state, exc.message)

    db.commit()
    return _success_page(email=normalize_email(consumption.user.email))
