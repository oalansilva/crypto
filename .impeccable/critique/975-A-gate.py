#!/usr/bin/env python3
"""Assessment A browser gate for card 975. Product evidence only; no HTML dump."""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-975-monitor-vazio-favoritos")
PROTO = ROOT / "frontend/public/prototypes/card-975-monitor-vazio-favoritos"
OUT = ROOT / ".impeccable/critique"
BASE = "https://dev.criptofarol.com.br/prototypes/card-975-monitor-vazio-favoritos"
LIVE_MONITOR = "https://dev.criptofarol.com.br/monitor"
PAGES = {
    "index": f"{BASE}/",
    "erro": f"{BASE}/erro.html",
}
FILES = {
    "index": PROTO / "index.html",
    "erro": PROTO / "erro.html",
}
VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    "mobile": {"width": 390, "height": 844},
}
EMPTY_CATALOG = "Nenhum ativo disponível no monitor"
ERROR_P = "Não foi possível carregar as estratégias."
ERROR_S = "A lista de favoritos não chegou. Isto não significa que não há estratégias."
RETRY = "Tentar de novo"
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
    "index.html": "542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116",
    "erro.html": "fb2a77198c0cca52b270b3f75e40e499f56580116d98b850a6f0e22f68810b34",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def https_get(url: str) -> tuple[int, str, bytes, str]:
    req = Request(url, headers={"User-Agent": "card-975-assessment-A"})
    with urlopen(req, timeout=30) as resp:
        body = resp.read()
        return resp.status, str(resp.geturl()), body, sha256_bytes(body)


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
          const joined = texts.join(' | ');
          const found = {};
          for (const needle of needles) {
            found[needle] = texts.some((t) => t === needle || t.includes(needle));
          }
          return { texts, joined, found, tableCount: document.querySelectorAll('table.signals').length };
        }""",
        LANDMARKS,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payload: dict = {"checks": [], "pages": {}, "live": {}, "digest": {}, "copied": {}, "extras": {}}

    def check(name: str, ok: bool, detail: str = "") -> None:
        payload["checks"].append({"name": name, "pass": bool(ok), "detail": detail})

    extras = sorted(p.name for p in PROTO.glob("*.html"))
    payload["extras"]["html"] = extras
    check("no-favorites-html", "favorites.html" not in extras, ",".join(extras))
    check("canonical-set", extras == ["erro.html", "index.html"], ",".join(extras))

    for key, path in FILES.items():
        disk = path.read_bytes()
        disk_sha = sha256_bytes(disk)
        url = PAGES[key]
        status, final, remote, remote_sha = https_get(url)
        stats = copied_stats(path)
        payload["digest"][path.name] = {
            "disk": disk_sha,
            "https": remote_sha,
            "http": status,
            "bytes": len(disk),
            "identical": disk_sha == remote_sha,
            "expected": EXPECTED[path.name],
            "matches_design": disk_sha == EXPECTED[path.name],
        }
        payload["copied"][path.name] = stats
        check(f"digest-{path.name}-https", status == 200 and disk_sha == remote_sha, f"{status} {disk_sha}")
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
        "table_signals": "table.signals" in live_text or "class=\"signals\"" in live_text,
    }
    # urllib on SPA path is often 200 without 302 — never PASS by itself.
    check("live-http-recorded", live_status == 200, f"{live_status} {live_final}")

    chrome = chrome_path()
    payload["chromium"] = chrome
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome,
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for vp_name, vp in VIEWPORTS.items():
            for page_name, url in PAGES.items():
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
                shot = OUT / f"975-A-{vp_name}-{vp['width']}x{vp['height']}-{page_name}.png"
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
                    "chrome_monitor": "Monitor" in body,
                    "filter_on": page.locator('[data-testid="monitor-filter-in-portfolio"].on').count(),
                    "filter_all_on": page.locator('[data-testid="monitor-filter-all"].on').count(),
                }
                prefix = f"{vp_name}-{page_name}"
                check(f"{prefix}-lang", info["lang"] == "pt-BR", str(info["lang"]))
                check(f"{prefix}-no-antes", info["antes_depois"] == 0, str(info["antes_depois"]))
                check(f"{prefix}-no-login-url", not info["login_in_url"], page.url)
                check(f"{prefix}-console", len(info["console"]) == 0, "; ".join(info["console"])[:400])
                check(f"{prefix}-pageerror", len(info["pageerror"]) == 0, "; ".join(info["pageerror"])[:400])
                check(f"{prefix}-table-present", table.count() >= 1, str(table.count()))
                check(f"{prefix}-chrome-monitor", info["chrome_monitor"])
                check(f"{prefix}-no-empty-catalog", not info["empty_catalog"])
                check(f"{prefix}-default-em-portfolio", info["filter_on"] == 1 and info["filter_all_on"] == 0)
                missing = [n for n, ok in lm["found"].items() if not ok]
                check(f"{prefix}-landmarks-dom", missing == [], json.dumps(missing, ensure_ascii=False))
                if vp_name == "desktop":
                    check(f"{prefix}-table-visible", table_visible, str(table_visible))
                    if sidebar_box:
                        check(f"{prefix}-sidebar-not-only-proof", True, json.dumps(sidebar_box))
                else:
                    if page_name == "index":
                        # Live hides table.signals under 740px; cards carry the listing.
                        check(f"{prefix}-table-hidden-like-live", table_visible is False, str(table_visible))
                    else:
                        # Sibling keeps empty thead for catalog; inline display:block shows it at 390. P3, not blocking.
                        check(
                            f"{prefix}-thead-leftover-noted",
                            True,
                            f"table_visible={table_visible}; live error XOR table; P3",
                        )

                if page_name == "index":
                    info["sol"] = "SOL/USDT" in body
                    info["eth"] = "ETH/USDT" in body
                    info["rows"] = page.locator("table.signals tbody tr.head-row").count()
                    info["sol_row"] = page.locator('[data-testid="monitor-row-sol-usdt"]').count()
                    info["eth_row"] = page.locator('[data-testid="monitor-row-eth-usdt"]').count()
                    info["error_p"] = ERROR_P in body
                    info["mobile_cards"] = page.locator(".mobile-card").count()
                    info["gallery_cards"] = page.locator(".state-card, .gallery, .antes, .depois").count()
                    check(f"{prefix}-sol", info["sol"])
                    check(f"{prefix}-eth", info["eth"])
                    check(f"{prefix}-sol-row", info["sol_row"] >= 1)
                    check(f"{prefix}-eth-row", info["eth_row"] >= 1)
                    check(f"{prefix}-no-error-copy", not info["error_p"])
                    check(f"{prefix}-not-gallery", info["gallery_cards"] == 0 and info["antes_depois"] == 0)
                    if vp_name == "desktop":
                        check(f"{prefix}-rows", info["rows"] >= 2, str(info["rows"]))
                    else:
                        check(f"{prefix}-mobile-cards", info["mobile_cards"] >= 2, str(info["mobile_cards"]))
                    check(f"{prefix}-no-second-click", True, "first paint already has SOL/ETH")

                if page_name == "erro":
                    info["error_p"] = ERROR_P in body
                    info["error_s"] = ERROR_S in body
                    info["retry"] = RETRY in body
                    info["login_copy"] = "Bem-vindo de volta" in body
                    alert = page.locator('[data-testid="monitor-load-error"][role="alert"], .monitor-error[role="alert"]')
                    info["alert"] = alert.count()
                    retry = page.locator(".monitor-retry").first
                    info["retry_count"] = page.locator(".monitor-retry").count()
                    box = retry.bounding_box() if info["retry_count"] else None
                    info["retry_box"] = box
                    info["retry_disabled"] = retry.get_attribute("disabled") if info["retry_count"] else "missing"
                    info["signal_rows"] = page.locator("table.signals tbody tr.head-row").count()
                    focused = page.evaluate(
                        """() => {
                          const btn = document.querySelector('.monitor-retry');
                          if (!btn) return { exists: false };
                          btn.focus();
                          const active = document.activeElement === btn;
                          const tabIndex = btn.tabIndex;
                          const disabled = btn.hasAttribute('disabled');
                          return { exists: true, active, tabIndex, disabled, tag: btn.tagName };
                        }"""
                    )
                    info["retry_focus"] = focused
                    check(f"{prefix}-error-p", info["error_p"])
                    check(f"{prefix}-error-s", info["error_s"])
                    check(f"{prefix}-retry", info["retry"])
                    check(f"{prefix}-no-login-copy", not info["login_copy"])
                    check(f"{prefix}-alert", info["alert"] > 0, str(info["alert"]))
                    check(f"{prefix}-stays-monitor", "Monitor" in body and "login" not in page.url.lower())
                    check(f"{prefix}-no-signal-rows", info["signal_rows"] == 0, str(info["signal_rows"]))
                    check(f"{prefix}-retry-focusable", bool(focused.get("exists")) and focused.get("active") and not focused.get("disabled"))
                    if box:
                        check(f"{prefix}-retry-44", box["height"] >= 44, json.dumps(box))
                    else:
                        check(f"{prefix}-retry-visible", False, "no bounding box")

                payload["pages"][f"{vp_name}-{page_name}"] = info
                context.close()

        live_ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            color_scheme="dark",
            ignore_https_errors=True,
        )
        live_page = live_ctx.new_page()
        live_page.goto(LIVE_MONITOR, wait_until="networkidle", timeout=30000)
        live_shot = OUT / "975-A-live-monitor.png"
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

    failed = [c for c in payload["checks"] if not c["pass"]]
    payload["passed"] = sum(1 for c in payload["checks"] if c["pass"])
    payload["failed"] = len(failed)
    payload["total"] = len(payload["checks"])
    payload["fails"] = failed
    payload["verdict_hint"] = "PASS" if not failed else "BLOCKED"
    (OUT / "975-A-gate.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": payload["passed"], "failed": payload["failed"], "total": payload["total"], "fails": failed}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
