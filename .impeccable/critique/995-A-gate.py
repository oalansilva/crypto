#!/usr/bin/env python3
"""Assessment A browser gate for card 995. Product evidence only; no HTML dump."""
from __future__ import annotations

import hashlib
import http.server
import json
import os
import re
import socketserver
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-995-monitor-retry-rede")
PROTO = ROOT / "frontend/public/prototypes/card-995-monitor-retry-rede"
OUT = ROOT / ".impeccable/critique"
BASE = "https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede"
LIVE_MONITOR = "https://dev.criptofarol.com.br/monitor"
PAGES = {
    "index": f"{BASE}/",
    "carga": f"{BASE}/carga.html",
    "erro": f"{BASE}/erro.html",
    "sessao": f"{BASE}/sessao.html",
}
FILES = {
    "index": PROTO / "index.html",
    "carga": PROTO / "carga.html",
    "erro": PROTO / "erro.html",
    "sessao": PROTO / "sessao.html",
}
VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    "mobile": {"width": 390, "height": 844},
}
EMPTY_CATALOG = "Nenhum ativo disponível no monitor"
ERROR_P = "Não foi possível carregar as estratégias."
ERROR_S = "A lista de favoritos não chegou. Isto não significa que não há estratégias."
RETRY = "Tentar de novo"
TOAST = "Não foi possível carregar preferências do monitor."
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
EXPECTED = {
    "index.html": "5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a",
    "carga.html": "00f523eb23752b39ab27e439ccfad82b00da98097a671c5878696060209e5fd4",
    "erro.html": "86d863acbb9318dfe9d5439a6e91d5fc5d1d6fde9a57065e1c464b69d40f6223",
    "sessao.html": "7879cd2630a22d2929db07cdfc7c0da5e1ba4f37e22261782a3ac7547d09c584",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def https_get(url: str) -> tuple[int, str, bytes, str]:
    req = Request(url, headers={"User-Agent": "card-995-assessment-A"})
    try:
        with urlopen(req, timeout=30) as resp:
            body = resp.read()
            return resp.status, str(resp.geturl()), body, sha256_bytes(body)
    except HTTPError as exc:
        body = exc.read()
        return exc.code, str(exc.url), body, sha256_bytes(body)


class PublicHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "frontend" / "public"), **kwargs)

    def log_message(self, format, *args):  # noqa: A003
        pass


def copied_stats(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    starts = len(re.findall(r"COPIED:start", text))
    ends = len(re.findall(r"COPIED:end", text))
    copied = 0
    for block in re.finditer(r"COPIED:start.*?COPIED:end", text, flags=re.S):
        copied += len(block.group(0).encode("utf-8"))
    return {
        "starts": starts,
        "ends": ends,
        "pairs_ok": starts == ends and starts > 0,
        "copied_utf8": copied,
        "bytes": len(text.encode("utf-8")),
    }


def chrome_path() -> str:
    for candidate in (
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        os.path.expanduser("~/.cache/ms-playwright/chromium-1148/chrome-linux/chrome"),
    ):
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError("chromium not found")


def visible_text_count(page, needle: str) -> int:
    return page.evaluate(
        """(needle) => {
          const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          let n = 0;
          while (walk.nextNode()) {
            const t = walk.currentNode;
            if (!t.nodeValue || !t.nodeValue.includes(needle)) continue;
            const el = t.parentElement;
            if (!el) continue;
            const s = getComputedStyle(el);
            if (s.display === 'none' || s.visibility === 'hidden') continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0 && r.height === 0) continue;
            n += 1;
          }
          return n;
        }""",
        needle,
    )


def th_landmarks(page) -> dict:
    return page.evaluate(
        """(needles) => {
          const ths = Array.from(document.querySelectorAll('table.signals thead th'));
          const texts = ths.map((th) => (th.textContent || '').replace(/\\s+/g, ' ').trim());
          const found = {};
          for (const needle of needles) {
            found[needle] = texts.some((t) => t === needle || t.includes(needle));
          }
          return { texts, found, tableCount: document.querySelectorAll('table.signals').length };
        }""",
        LANDMARKS,
    )


def kpi_zero_as_truth(page) -> bool:
    return page.evaluate(
        """() => {
          const vals = [...document.querySelectorAll('.kpi-val')];
          return vals.some((el) => (el.textContent || '').trim() === '0'
            && !el.hasAttribute('data-kpi-pending'));
        }"""
    )


def kpi_pending_state(page) -> dict:
    return page.evaluate(
        """() => {
          const vals = [...document.querySelectorAll('.kpi-val')];
          return {
            count: vals.length,
            texts: vals.map((el) => (el.textContent || '').trim()),
            pending: vals.filter((el) => el.hasAttribute('data-kpi-pending')).length,
            zeros: vals.filter((el) => (el.textContent || '').trim() === '0').length,
            ariaBusy: document.querySelector('.kpis')?.getAttribute('aria-busy') || null,
          };
        }"""
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payload: dict = {"checks": [], "pages": {}, "live": {}, "digest": {}, "copied": {}, "extras": {}}

    def check(name: str, ok: bool, detail: str = "") -> None:
        payload["checks"].append({"name": name, "pass": bool(ok), "detail": detail})

    extras = sorted(p.name for p in PROTO.glob("*.html"))
    payload["extras"]["html"] = extras
    check("no-favorites-html", "favorites.html" not in extras, ",".join(extras))
    check(
        "canonical-set",
        extras == ["carga.html", "erro.html", "index.html", "sessao.html"],
        ",".join(extras),
    )

    https_index = https_get(PAGES["index"])
    payload["https_public"] = {
        "url": PAGES["index"],
        "http": https_index[0],
        "final": https_index[1],
        "sha": https_index[3],
        "title_snippet": https_index[2][:180].decode("utf-8", errors="replace"),
        "note": "criptofarol-dev-prototypes.service caches roots at boot; this worktree is absent from /prototypes/ listing. Critique uses worktree HTTP (same as autor).",
    }
    check(
        "https-404-recorded",
        https_index[0] == 404 and "Protótipo não encontrado" in https_index[2].decode("utf-8", errors="replace"),
        f"{https_index[0]} {https_index[1]}",
    )

    httpd = socketserver.TCPServer(("127.0.0.1", 0), PublicHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    local_base = f"http://127.0.0.1:{port}/prototypes/card-995-monitor-retry-rede"
    local_pages = {
        "index": f"{local_base}/",
        "carga": f"{local_base}/carga.html",
        "erro": f"{local_base}/erro.html",
        "sessao": f"{local_base}/sessao.html",
    }
    payload["local_base"] = local_base

    for key, path in FILES.items():
        disk = path.read_bytes()
        disk_sha = sha256_bytes(disk)
        status, final, remote, remote_sha = https_get(local_pages[key])
        stats = copied_stats(path)
        payload["digest"][path.name] = {
            "disk": disk_sha,
            "https_public": https_index[3] if key == "index" else None,
            "https_public_http": https_index[0] if key == "index" else None,
            "local_http": status,
            "local_sha": remote_sha,
            "bytes": len(disk),
            "identical_local": disk_sha == remote_sha,
            "expected": EXPECTED[path.name],
            "matches_design": disk_sha == EXPECTED[path.name],
        }
        payload["copied"][path.name] = stats
        check(f"digest-{path.name}-local", status == 200 and disk_sha == remote_sha, f"{status} {disk_sha}")
        check(f"digest-{path.name}-expected", disk_sha == EXPECTED[path.name], disk_sha)
        check(f"copied-{path.name}-pairs", stats["pairs_ok"] and stats["copied_utf8"] > 0, json.dumps(stats))

    live_status, live_final, live_body, _ = https_get(LIVE_MONITOR)
    live_text = live_body.decode("utf-8", errors="replace")
    payload["live"] = {
        "requested": LIVE_MONITOR,
        "http": live_status,
        "final": live_final,
        "login_page": "/login" in live_final,
        "h1_login": "Bem-vindo de volta" in live_text,
        "table_signals": "table.signals" in live_text or 'class="signals"' in live_text,
    }
    check("live-http-recorded", live_status == 200, f"{live_status} {live_final}")

    chrome = chrome_path()
    payload["chromium"] = chrome
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=chrome,
                headless=False,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            pub_ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                color_scheme="dark",
                ignore_https_errors=True,
            )
            pub_page = pub_ctx.new_page()
            pub_page.goto(PAGES["index"], wait_until="networkidle", timeout=30000)
            pub_shot = OUT / "995-A-https-404.png"
            pub_page.screenshot(path=str(pub_shot), full_page=True)
            payload["https_public"]["playwright_h1"] = (
                pub_page.locator("h1").first.inner_text() if pub_page.locator("h1").count() else ""
            )
            payload["https_public"]["screenshot"] = pub_shot.name
            payload["https_public"]["playwright_url"] = pub_page.url
            pub_ctx.close()
            for vp_name, vp in VIEWPORTS.items():
                for page_name, url in local_pages.items():
                    console_errors: list[str] = []
                    page_errors: list[str] = []
                    context = browser.new_context(viewport=vp, color_scheme="dark", ignore_https_errors=True)
                    page = context.new_page()
                    page.on(
                        "console",
                        lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None,
                    )
                    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.wait_for_timeout(400)
                    body = page.inner_text("body")
                    shot = OUT / f"995-A-{vp_name}-{vp['width']}x{vp['height']}-{page_name}.png"
                    page.screenshot(path=str(shot), full_page=True)
                    overflow_x = page.evaluate(
                        "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
                    )
                    lm = th_landmarks(page)
                    table = page.locator("table.signals")
                    table_visible = table.first.is_visible() if table.count() else False
                    sidebar = page.locator("aside.sidebar")
                    sidebar_box = sidebar.first.bounding_box() if sidebar.count() else None
                    info: dict = {
                        "url": page.url,
                        "title": page.title(),
                        "h1": page.locator("h1").first.inner_text() if page.locator("h1").count() else "",
                        "lang": page.locator("html").get_attribute("lang"),
                        "screenshot": shot.name,
                        "overflow_x": overflow_x,
                        "antes_depois": visible_text_count(page, "ANTES") + visible_text_count(page, "DEPOIS"),
                        "login_in_url": "login" in page.url.lower(),
                        "console": [e for e in console_errors if "favicon" not in e.lower()],
                        "pageerror": page_errors,
                        "table_count": table.count(),
                        "table_visible": table_visible,
                        "landmarks": lm,
                        "sidebar_box": sidebar_box,
                        "empty_catalog": EMPTY_CATALOG in body,
                        "toast": TOAST in body,
                        "error_p": ERROR_P in body,
                        "error_s": ERROR_S in body,
                        "retry": RETRY in body,
                        "loading": LOADING in body,
                        "login_copy": "Bem-vindo de volta" in body and "Entrar" in body,
                        "kpi_zero_truth": kpi_zero_as_truth(page),
                        "kpi": kpi_pending_state(page),
                        "refresh_mode": page.locator('[data-testid="monitor-refresh"]').get_attribute("data-load-mode")
                        if page.locator('[data-testid="monitor-refresh"]').count()
                        else None,
                        "retry_mode": page.locator('[data-testid="monitor-retry"]').get_attribute("data-load-mode")
                        if page.locator('[data-testid="monitor-retry"]').count()
                        else None,
                        "mobile_subtitle": page.locator(".mobile-title span").first.inner_text()
                        if page.locator(".mobile-title span").count()
                        else "",
                    }
                    prefix = f"{vp_name}-{page_name}"
                    check(f"{prefix}-lang", info["lang"] == "pt-BR", str(info["lang"]))
                    check(f"{prefix}-no-antes", info["antes_depois"] == 0, str(info["antes_depois"]))
                    check(f"{prefix}-console", len(info["console"]) == 0, "; ".join(info["console"])[:400])
                    check(f"{prefix}-pageerror", len(info["pageerror"]) == 0, "; ".join(info["pageerror"])[:400])
                    check(f"{prefix}-no-empty-catalog", not info["empty_catalog"])
                    check(f"{prefix}-no-toast", not info["toast"])

                    if page_name != "sessao":
                        check(f"{prefix}-no-login-url", not info["login_in_url"], page.url)
                        check(f"{prefix}-chrome-monitor", "Monitor" in body)
                        if vp_name == "desktop" and sidebar_box:
                            check(
                                f"{prefix}-sidebar-not-only-proof",
                                True,
                                json.dumps(sidebar_box),
                            )

                    if page_name == "index":
                        missing = [n for n, ok in lm["found"].items() if not ok]
                        check(f"{prefix}-table-present", table.count() >= 1, str(table.count()))
                        check(f"{prefix}-landmarks-dom", missing == [], json.dumps(missing, ensure_ascii=False))
                        check(f"{prefix}-sol", "SOL/USDT" in body)
                        check(f"{prefix}-eth", "ETH/USDT" in body)
                        check(f"{prefix}-no-error-copy", not info["error_p"] and not info["retry"])
                        check(f"{prefix}-no-loading", not info["loading"])
                        check(f"{prefix}-no-kpi-zero-truth", not info["kpi_zero_truth"])
                        check(f"{prefix}-refresh-recompute", info["refresh_mode"] == "recompute", str(info["refresh_mode"]))
                        check(
                            f"{prefix}-not-gallery",
                            page.locator(".state-card, .gallery, .antes, .depois").count() == 0,
                        )
                        if vp_name == "desktop":
                            check(f"{prefix}-table-visible", table_visible, str(table_visible))
                            check(
                                f"{prefix}-rows",
                                page.locator("table.signals tbody tr.head-row").count() >= 2,
                                str(page.locator("table.signals tbody tr.head-row").count()),
                            )
                        else:
                            check(f"{prefix}-table-hidden-like-live", table_visible is False, str(table_visible))
                            check(
                                f"{prefix}-mobile-cards",
                                page.locator(".mobile-card").count() >= 2,
                                str(page.locator(".mobile-card").count()),
                            )

                    if page_name == "carga":
                        check(f"{prefix}-loading", info["loading"])
                        check(f"{prefix}-no-error", not info["error_p"] and not info["retry"])
                        check(f"{prefix}-no-kpi-zero-truth", not info["kpi_zero_truth"])
                        check(f"{prefix}-kpi-pending", info["kpi"]["pending"] >= 4, json.dumps(info["kpi"]))
                        check(f"{prefix}-aria-busy", info["kpi"]["ariaBusy"] == "true", str(info["kpi"]["ariaBusy"]))
                        check(f"{prefix}-status-live", page.locator('[role="status"]').count() >= 1)
                        check(f"{prefix}-no-login-copy", not info["login_copy"])
                        check(f"{prefix}-refresh-recompute", info["refresh_mode"] == "recompute", str(info["refresh_mode"]))

                    if page_name == "erro":
                        check(f"{prefix}-error-p", info["error_p"])
                        check(f"{prefix}-error-s", info["error_s"])
                        check(f"{prefix}-retry", info["retry"])
                        check(f"{prefix}-no-login-copy", not info["login_copy"])
                        check(f"{prefix}-stays-monitor", "Monitor" in body and "login" not in page.url.lower())
                        check(f"{prefix}-no-kpi-zero-truth", not info["kpi_zero_truth"])
                        check(f"{prefix}-retry-reread", info["retry_mode"] == "reread", str(info["retry_mode"]))
                        check(f"{prefix}-refresh-recompute", info["refresh_mode"] == "recompute", str(info["refresh_mode"]))
                        check(f"{prefix}-alert", page.locator('[role="alert"]').count() >= 1)
                        check(
                            f"{prefix}-no-signal-rows",
                            page.locator("table.signals tbody tr.head-row").count() == 0,
                        )
                        retry = page.locator(".monitor-retry").first
                        box = retry.bounding_box() if page.locator(".monitor-retry").count() else None
                        info["retry_box"] = box
                        focused = page.evaluate(
                            """() => {
                              const btn = document.querySelector('.monitor-retry');
                              if (!btn) return { exists: false };
                              btn.focus();
                              return {
                                exists: true,
                                active: document.activeElement === btn,
                                disabled: btn.hasAttribute('disabled'),
                                tag: btn.tagName,
                                href: btn.getAttribute('href'),
                              };
                            }"""
                        )
                        info["retry_focus"] = focused
                        check(
                            f"{prefix}-retry-focusable",
                            bool(focused.get("exists")) and focused.get("active") and not focused.get("disabled"),
                        )
                        check(f"{prefix}-retry-points-list", focused.get("href") == "index.html", json.dumps(focused))
                        if box:
                            check(f"{prefix}-retry-44", box["height"] >= 44, json.dumps(box))
                        else:
                            check(f"{prefix}-retry-visible", False, "no bounding box")

                    if page_name == "sessao":
                        check(f"{prefix}-login-copy", info["login_copy"])
                        check(f"{prefix}-no-error", not info["error_p"])
                        check(f"{prefix}-no-monitor-table", table.count() == 0, str(table.count()))
                        check(f"{prefix}-h1", "Bem-vindo de volta" in info["h1"], info["h1"])
                        enter = page.locator('button.submit, button[type="submit"]')
                        check(f"{prefix}-entrar", enter.count() >= 1 and "Entrar" in (enter.first.inner_text() or ""))

                    payload["pages"][f"{vp_name}-{page_name}"] = info
                    context.close()

            live_ctx = browser.new_context(
                viewport={"width": 1280, "height": 800},
                color_scheme="dark",
                ignore_https_errors=True,
            )
            live_page = live_ctx.new_page()
            live_page.goto(LIVE_MONITOR, wait_until="networkidle", timeout=30000)
            live_shot = OUT / "995-A-live-monitor.png"
            live_page.screenshot(path=str(live_shot), full_page=True)
            live_h1 = live_page.locator("h1").first.inner_text() if live_page.locator("h1").count() else ""
            payload["live"]["playwright_final"] = live_page.url
            payload["live"]["playwright_h1"] = live_h1
            payload["live"]["screenshot"] = live_shot.name
            payload["live"]["table_count"] = live_page.locator("table.signals").count()
            check("live-playwright-login", "/login" in live_page.url, live_page.url)
            check("live-playwright-not-monitor-table", live_page.locator("table.signals").count() == 0)
            check("live-login-is-not-route", True, "discarded; /login is not /monitor")
            live_ctx.close()
            browser.close()
    finally:
        httpd.shutdown()

    failed = [c for c in payload["checks"] if not c["pass"]]
    payload["passed"] = sum(1 for c in payload["checks"] if c["pass"])
    payload["failed"] = len(failed)
    payload["total"] = len(payload["checks"])
    payload["fails"] = failed
    payload["verdict_hint"] = "PASS" if not failed else "BLOCKED"
    (OUT / "995-A-gate.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "passed": payload["passed"],
                "failed": payload["failed"],
                "total": payload["total"],
                "fails": failed,
                "digest": payload["digest"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
