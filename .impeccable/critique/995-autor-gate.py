#!/usr/bin/env python3
"""Browser gate card-995 — desktop+mobile × carga/lista/erro/sessão."""
from __future__ import annotations

import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "frontend" / "public"
PROTO = "/prototypes/card-995-monitor-retry-rede"
SHOT_DIR = ROOT / ".impeccable" / "critique"
EVIDENCE = SHOT_DIR / "995-autor-gate.json"

PAGES = {
    "index": "",
    "carga": "/carga.html",
    "erro": "/erro.html",
    "sessao": "/sessao.html",
}
VIEWPORTS = (("desktop", 1280, 800), ("mobile", 390, 844))
FORBIDDEN_TOAST = "Não foi possível carregar preferências do monitor."
EMPTY_CATALOG = "Nenhum ativo disponível no monitor"
ERR_P = "Não foi possível carregar as estratégias."
ERR_S = "A lista de favoritos não chegou. Isto não significa que não há estratégias."
LOADING = "Carregando sinais..."
LANDMARKS = [
    "Status",
    "Preço",
    "Distância",
    "7d",
    "Risco até stop",
    "Tags",
    "Operar",
    "Par / Estratégia",
]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC), **kwargs)

    def log_message(self, format, *args):  # noqa: A003
        pass


def kpi_zero_as_truth(page) -> bool:
    return page.evaluate(
        """() => {
          const vals = [...document.querySelectorAll('.kpi-val')];
          return vals.some((el) => (el.textContent || '').trim() === '0'
            && !el.hasAttribute('data-kpi-pending'));
        }"""
    )


def main() -> int:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}{PROTO}"
    results = []
    fails = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/chromium-browser",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for page_id, suffix in PAGES.items():
            for name, w, h in VIEWPORTS:
                console_errors = []
                page_errors = []
                ctx = browser.new_context(
                    viewport={"width": w, "height": h},
                    color_scheme="dark",
                )
                page = ctx.new_page()
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.on("pageerror", lambda exc: page_errors.append(str(exc)))
                url = f"{base}{suffix}/" if suffix == "" else f"{base}{suffix}"
                if suffix == "":
                    url = f"{base}/"
                page.goto(url, wait_until="networkidle")
                body = page.inner_text("body")
                shot = SHOT_DIR / f"995-{page_id}-{name}-{w}x{h}.png"
                page.screenshot(path=str(shot), full_page=True)
                row = {
                    "page": page_id,
                    "viewport": f"{w}x{h}",
                    "url": url,
                    "toast": FORBIDDEN_TOAST in body,
                    "empty_catalog": EMPTY_CATALOG in body,
                    "err_p": ERR_P in body,
                    "err_s": ERR_S in body,
                    "retry": "Tentar de novo" in body,
                    "loading": LOADING in body,
                    "sol": "SOL/USDT" in body,
                    "eth": "ETH/USDT" in body,
                    "login": "Bem-vindo de volta" in body and "Entrar" in body,
                    "kpi_zero_truth": kpi_zero_as_truth(page),
                    "table": page.locator("table.signals").count(),
                    "landmarks_missing": [
                        lm for lm in LANDMARKS if lm not in page.content()
                    ] if page_id == "index" else [],
                    "console_errors": console_errors + page_errors,
                    "shot": shot.name,
                }
                expected_fail = []
                if row["toast"]:
                    expected_fail.append("toast")
                if row["empty_catalog"]:
                    expected_fail.append("empty_catalog")
                if row["console_errors"]:
                    expected_fail.append("console")
                if page_id == "index":
                    if not row["sol"] or not row["eth"]:
                        expected_fail.append("pairs")
                    if row["err_p"] or row["retry"] or row["loading"]:
                        expected_fail.append("error_or_loading_on_happy")
                    if row["table"] < 1:
                        expected_fail.append("table")
                    if row["landmarks_missing"]:
                        expected_fail.append("landmarks")
                    if row["kpi_zero_truth"]:
                        expected_fail.append("kpi_zero")
                elif page_id == "carga":
                    if not row["loading"]:
                        expected_fail.append("missing_loading")
                    if row["err_p"] or row["retry"]:
                        expected_fail.append("error_on_loading")
                    if row["kpi_zero_truth"]:
                        expected_fail.append("kpi_zero")
                elif page_id == "erro":
                    if not (row["err_p"] and row["err_s"] and row["retry"]):
                        expected_fail.append("missing_975")
                    if row["login"]:
                        expected_fail.append("login_on_error")
                    if row["kpi_zero_truth"]:
                        expected_fail.append("kpi_zero")
                elif page_id == "sessao":
                    if not row["login"]:
                        expected_fail.append("missing_login")
                    if row["err_p"]:
                        expected_fail.append("error_on_login")
                row["fails"] = expected_fail
                if expected_fail:
                    fails.append(f"{page_id}/{name}: {expected_fail}")
                results.append(row)
                ctx.close()
        browser.close()
    httpd.shutdown()
    payload = {"base": base, "fails": fails, "results": results}
    EVIDENCE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"fails": fails, "n": len(results), "evidence": str(EVIDENCE)}, ensure_ascii=False, indent=2))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
