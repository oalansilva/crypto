#!/usr/bin/env python3
"""Assessment A browser gate — card 994 rework 1. Product evidence only."""
from __future__ import annotations

import hashlib
import http.server
import json
import os
import re
import socket
import threading
from functools import partial
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-994-monitor-multiplos-timeframes")
PUBLIC = ROOT / "frontend/public"
PROTO = PUBLIC / "prototypes/card-994-monitor-multiplos-timeframes"
OUT = ROOT / ".impeccable/critique"
LIVE_MONITOR = "https://dev.criptofarol.com.br/monitor"
DEV_PROTO = "https://dev.criptofarol.com.br/prototypes/card-994-monitor-multiplos-timeframes/"
EXPECTED = "f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b"
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}
LANDMARKS = [
    "Status",
    "Preço",
    "Distância",
    "Tags",
    "Operar",
    "Par / Estratégia",
]
FORBIDDEN_VISIBLE = ["Gráfico 1d", "tf 1d"]
SELECTOR_NEEDLES = [
    "Selecionar timeframe do gráfico",
    "Estratégia (4H)",
    "data-chart-tf",
    "chart-timeframe",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def https_get(url: str) -> tuple[int, str, bytes, str]:
    req = Request(url, headers={"User-Agent": "card-994-assessment-A-rework"})
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
        "pairs_ok": starts == ends and starts == 9,
        "copied_utf8": copied,
        "bytes": len(text.encode("utf-8")),
        "has_7d_copied": "7d" in text,
        "visible_th_grafico": bool(re.search(r"<th[^>]*>Gráfico</th>", text)),
        "has_tf_filter": 'id="tf-filter"' in text,
        "has_readonly": "Estratégia ·" in text,
        "no_data_chart_tf": "data-chart-tf" not in text,
        "no_role_group": 'role="group"' not in text,
        "no_select_tf": "Selecionar timeframe do gráfico" not in text,
        "no_estrategia_4H_btn": "Estratégia (4H)" not in text,
        "no_grafico_1d": "Gráfico 1d" not in text,
        "no_tf_1d": "tf 1d" not in text,
        "no_15m": "15m" not in text,
    }


def chrome_path() -> str:
    for candidate in (
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        os.path.expanduser("~/.cache/ms-playwright/chromium-1243/chrome-linux-arm64/chrome"),
        os.path.expanduser("~/.cache/ms-playwright/chromium-1148/chrome-linux/chrome"),
    ):
        if os.path.exists(candidate):
            return candidate
    raise FileNotFoundError("chromium not found")


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_local_server() -> tuple[str, threading.Thread, http.server.ThreadingHTTPServer]:
    port = free_port()
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(PUBLIC))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{port}/prototypes/card-994-monitor-multiplos-timeframes/", thread, httpd


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
          const hasGrafico = texts.some((t) => t === 'Gráfico' || t.includes('Gráfico'));
          const has7dVisible = texts.some((t) => t === '7d' || t.includes('7d'));
          return {
            texts,
            found,
            tableCount: document.querySelectorAll('table.signals').length,
            hasGrafico,
            has7dVisible,
            sparkColPresent: hasGrafico || has7dVisible,
          };
        }""",
        LANDMARKS,
    )


def selector_probe(page) -> dict:
    return page.evaluate(
        """() => {
          const buttons = Array.from(document.querySelectorAll('button, [role="button"]'))
            .map((el) => (el.textContent || '').replace(/\\s+/g, ' ').trim())
            .filter(Boolean);
          const groups = Array.from(document.querySelectorAll('[role="group"]')).map((el) => ({
            label: el.getAttribute('aria-label') || '',
            text: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 120),
          }));
          return {
            dataChartTf: document.querySelectorAll('[data-chart-tf]').length,
            roleGroup: groups,
            chartTfButtons: document.querySelectorAll('[data-testid^="chart-timeframe"], [aria-label="Selecionar timeframe do gráfico"]').length,
            selectTfLabel: Array.from(document.querySelectorAll('[aria-label]')).map((el) => el.getAttribute('aria-label')).filter((v) => v && v.includes('timeframe do gráfico')),
            buttonHits: buttons.filter((t) => ['15m', '1h', '1d', 'Estratégia (4H)', 'Estratégia (4h)'].includes(t)),
            readonly: (document.querySelector('[data-testid="chart-strategy-tf"]') || {}).textContent || '',
            bars: (document.querySelector('#visible-bars') || {}).textContent || '',
            subtitle: (document.querySelector('#chart-subtitle') || {}).textContent || '',
            tfFilter: document.querySelector('#tf-filter') ? true : false,
            tfFilterOptions: Array.from(document.querySelectorAll('#tf-filter option')).map((o) => o.textContent.trim()),
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
    check("canonical-set", extras == ["index.html"], ",".join(extras))

    path = PROTO / "index.html"
    disk = path.read_bytes()
    disk_sha = sha256_bytes(disk)
    stats = copied_stats(path)
    payload["copied"]["index.html"] = stats
    check("digest-disk-expected", disk_sha == EXPECTED, disk_sha)
    check("copied-pairs-9", stats["pairs_ok"] and stats["copied_utf8"] > 0, json.dumps(stats))
    check("column-not-deleted", stats["visible_th_grafico"] and stats["has_7d_copied"], json.dumps(stats))
    check("html-no-chart-selector", stats["no_data_chart_tf"] and stats["no_role_group"] and stats["no_select_tf"] and stats["no_estrategia_4H_btn"] and stats["no_15m"])
    check("html-list-filter", stats["has_tf_filter"])
    check("html-readonly-label", stats["has_readonly"])
    check("html-no-grafico-1d", stats["no_grafico_1d"] and stats["no_tf_1d"])

    try:
        status, final, remote, remote_sha = https_get(DEV_PROTO)
        payload["digest"]["https"] = {
            "http": status,
            "final": final,
            "sha256": remote_sha,
            "bytes": len(remote),
            "identical": remote_sha == disk_sha,
        }
        check("digest-https-recorded", status == 200, f"{status} {remote_sha}")
        check("digest-https-vs-disk", remote_sha == disk_sha, f"https={remote_sha} disk={disk_sha}")
    except Exception as exc:  # noqa: BLE001
        payload["digest"]["https_error"] = str(exc)
        check("digest-https-recorded", False, str(exc))

    payload["digest"]["disk"] = {"sha256": disk_sha, "bytes": len(disk), "expected": EXPECTED}

    live_status, live_final, live_body, _ = https_get(LIVE_MONITOR)
    live_text = live_body.decode("utf-8", errors="replace")
    payload["live"] = {
        "requested": LIVE_MONITOR,
        "http": live_status,
        "final": live_final,
        "bytes": len(live_body),
        "table_signals": "table.signals" in live_text or 'class="signals"' in live_text,
    }
    check("live-http-recorded", live_status == 200, f"{live_status} {live_final} {len(live_body)}B")

    local_url, _thread, httpd = start_local_server()
    payload["served"] = local_url
    chrome = chrome_path()
    payload["chromium"] = chrome

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=chrome,
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            for vp_name, vp in VIEWPORTS.items():
                console_errors: list[str] = []
                page_errors: list[str] = []
                context = browser.new_context(viewport=vp, color_scheme="dark")
                page = context.new_page()
                page.on(
                    "console",
                    lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None,
                )
                page.on("pageerror", lambda exc: page_errors.append(str(exc)))
                page.goto(local_url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(350)
                body = page.inner_text("body")
                shot = OUT / f"994-A-{vp_name}-{vp['width']}x{vp['height']}-index.png"
                page.screenshot(path=str(shot), full_page=False)
                overflow_x = page.evaluate(
                    "() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
                )
                lm = th_landmarks(page)
                probe = selector_probe(page)
                table = page.locator("table.signals")
                table_visible = table.first.is_visible() if table.count() else False
                sidebar = page.locator("aside.sidebar")
                sidebar_box = sidebar.first.bounding_box() if sidebar.count() else None
                pair_tf = page.locator('[data-testid="monitor-pair-tf-btc"]').inner_text()
                close_box = page.locator(".chart-modal-close").first.bounding_box()
                readonly_box = page.locator('[data-testid="chart-strategy-tf"]').first.bounding_box()
                forbidden_hits = {needle: visible_text_count(page, needle) for needle in FORBIDDEN_VISIBLE}
                selector_visible = {needle: visible_text_count(page, needle) for needle in ["15m", "Estratégia (4H)", "Selecionar timeframe do gráfico"]}
                info: dict = {
                    "url": page.url,
                    "title": page.title(),
                    "h1": page.locator("h1").first.inner_text() if page.locator("h1").count() else "",
                    "lang": page.locator("html").get_attribute("lang"),
                    "screenshot": shot.name,
                    "overflow_x": overflow_x,
                    "antes_depois": visible_text_count(page, "ANTES") + visible_text_count(page, "DEPOIS"),
                    "console": [e for e in console_errors if "favicon" not in e.lower() and "brand/" not in e.lower()],
                    "pageerror": page_errors,
                    "table_count": table.count(),
                    "table_visible": table_visible,
                    "landmarks": lm,
                    "sidebar_box": sidebar_box,
                    "pair_tf": pair_tf,
                    "probe": probe,
                    "forbidden": forbidden_hits,
                    "selector_visible": selector_visible,
                    "btc": "BTC/USDT" in body,
                    "strategy": "Médias Móveis: Tendência em Virada" in body,
                    "eth": "ETH/USDT" in body,
                    "readonly_label": "Estratégia ·" in body and "4h" in (probe.get("readonly") or ""),
                    "dialog": page.locator('[data-testid="chart-modal"][role="dialog"]').count(),
                    "filter_label": page.locator("#tf-filter").get_attribute("aria-label"),
                    "nav": page.locator("aside[aria-label='Navegação principal']").count(),
                    "close_box": close_box,
                    "readonly_box": readonly_box,
                    "mobile_cards": page.locator(".mobile-card").count(),
                    "gallery": page.locator(".state-card, .gallery, .antes, .depois").count(),
                    "in_portfolio_on": "on" in (page.locator('[data-testid="monitor-filter-in-portfolio"]').get_attribute("class") or ""),
                }
                prefix = f"{vp_name}-index"
                check(f"{prefix}-lang", info["lang"] == "pt-BR", str(info["lang"]))
                check(f"{prefix}-no-antes", info["antes_depois"] == 0, str(info["antes_depois"]))
                check(f"{prefix}-console", len(info["console"]) == 0, "; ".join(info["console"])[:400])
                check(f"{prefix}-pageerror", len(info["pageerror"]) == 0, "; ".join(info["pageerror"])[:400])
                check(f"{prefix}-table-present", table.count() >= 1, str(table.count()))
                check(f"{prefix}-h1-monitor", "Monitor de sinais" in info["h1"], info["h1"])
                check(f"{prefix}-not-gallery", info["gallery"] == 0)
                check(f"{prefix}-btc", info["btc"])
                check(f"{prefix}-strategy", info["strategy"])
                check(f"{prefix}-eth-witness", info["eth"])
                check(f"{prefix}-pair-tf-4h", pair_tf.strip() == "4h", pair_tf)
                check(
                    f"{prefix}-filter-options",
                    probe["tfFilter"]
                    and any("Todos" in t for t in probe["tfFilterOptions"])
                    and any("4h" in t for t in probe["tfFilterOptions"])
                    and any("1d" in t for t in probe["tfFilterOptions"]),
                    json.dumps(probe["tfFilterOptions"], ensure_ascii=False),
                )
                check(f"{prefix}-no-grafico-1d", forbidden_hits["Gráfico 1d"] == 0)
                check(f"{prefix}-no-tf-1d", forbidden_hits["tf 1d"] == 0)
                check(f"{prefix}-readonly-estrategia-4h", info["readonly_label"], probe.get("readonly"))
                check(f"{prefix}-no-data-chart-tf", probe["dataChartTf"] == 0, str(probe["dataChartTf"]))
                check(f"{prefix}-no-role-group", probe["roleGroup"] == [], json.dumps(probe["roleGroup"], ensure_ascii=False))
                check(f"{prefix}-no-chart-tf-buttons", probe["chartTfButtons"] == 0 and probe["buttonHits"] == [], json.dumps(probe["buttonHits"]))
                check(f"{prefix}-no-select-tf-label", probe["selectTfLabel"] == [], json.dumps(probe["selectTfLabel"]))
                check(f"{prefix}-selector-needles-invisible", all(v == 0 for v in selector_visible.values()), json.dumps(selector_visible, ensure_ascii=False))
                check(f"{prefix}-chart-dialog", info["dialog"] == 1)
                check(f"{prefix}-spark-btc-4h", page.locator('svg[aria-label="Minigráfico BTC 4h"]').count() >= 1)
                check(f"{prefix}-nav", info["nav"] == 1)
                check(f"{prefix}-filter-aria", info["filter_label"] == "Timeframe")
                check(f"{prefix}-default-in-portfolio", info["in_portfolio_on"])
                missing = [n for n, ok in lm["found"].items() if not ok]
                check(f"{prefix}-landmarks-dom", missing == [], json.dumps(missing, ensure_ascii=False))
                check(f"{prefix}-coluna-grafico", lm["hasGrafico"] is True and lm["has7dVisible"] is False, json.dumps(lm["texts"], ensure_ascii=False))
                if vp_name == "desktop":
                    check(f"{prefix}-table-visible", table_visible, str(table_visible))
                    if sidebar_box:
                        check(f"{prefix}-sidebar-224", abs(sidebar_box["width"] - 224) < 2, json.dumps(sidebar_box))
                    check(f"{prefix}-overflow-x", overflow_x is False, str(overflow_x))
                else:
                    check(f"{prefix}-table-hidden-like-live", table_visible is False, str(table_visible))
                    check(f"{prefix}-mobile-cards", info["mobile_cards"] >= 2, str(info["mobile_cards"]))
                    check(f"{prefix}-overflow-x", overflow_x is False, str(overflow_x))
                    mobile_btc_tf = page.locator('[data-testid="monitor-mobile-btc-usdt"] .pair-tf').inner_text()
                    check(f"{prefix}-mobile-btc-4h", mobile_btc_tf.strip() == "4h", mobile_btc_tf)

                page.select_option("#tf-filter", "4h")
                page.wait_for_timeout(200)
                btc_hidden = page.locator('[data-testid="monitor-row-btc-usdt"]').get_attribute("hidden")
                eth_hidden = page.locator('[data-testid="monitor-row-eth-usdt"]').get_attribute("hidden")
                check(f"{vp_name}-filter-4h-btc-visible", btc_hidden is None, str(btc_hidden))
                check(f"{vp_name}-filter-4h-eth-hidden", eth_hidden is not None, str(eth_hidden))
                if vp_name == "mobile":
                    check(
                        f"{vp_name}-filter-4h-eth-card-hidden",
                        page.locator('article.mobile-card[data-row-tf="1d"]').first.get_attribute("hidden") is not None,
                    )
                filter_shot = OUT / f"994-A-{vp_name}-{vp['width']}x{vp['height']}-filter-4h.png"
                page.screenshot(path=str(filter_shot), full_page=False)
                info["filter_4h_shot"] = filter_shot.name

                page.select_option("#tf-filter", "1d")
                page.wait_for_timeout(200)
                btc_hidden_1d = page.locator('[data-testid="monitor-row-btc-usdt"]').get_attribute("hidden")
                eth_hidden_1d = page.locator('[data-testid="monitor-row-eth-usdt"]').get_attribute("hidden")
                check(f"{vp_name}-filter-1d-btc-hidden", btc_hidden_1d is not None, str(btc_hidden_1d))
                check(f"{vp_name}-filter-1d-eth-visible", eth_hidden_1d is None, str(eth_hidden_1d))
                filter_1d_shot = OUT / f"994-A-{vp_name}-{vp['width']}x{vp['height']}-filter-1d.png"
                page.screenshot(path=str(filter_1d_shot), full_page=False)
                info["filter_1d_shot"] = filter_1d_shot.name

                page.select_option("#tf-filter", "all")
                page.wait_for_timeout(150)
                check(
                    f"{vp_name}-filter-all-both",
                    page.locator('[data-testid="monitor-row-btc-usdt"]').get_attribute("hidden") is None
                    and page.locator('[data-testid="monitor-row-eth-usdt"]').get_attribute("hidden") is None,
                )

                page.locator('[data-testid="chart-modal"]').click()
                page.wait_for_timeout(150)
                page.locator(".chart-stage").click()
                page.wait_for_timeout(150)
                open_chart = page.locator(".row-action", has_text="Abrir Gráfico")
                clicked_open = False
                for i in range(open_chart.count()):
                    btn = open_chart.nth(i)
                    if btn.is_visible():
                        btn.click()
                        clicked_open = True
                        break
                check(f"{vp_name}-open-chart-visible-click", clicked_open)
                page.wait_for_timeout(200)
                after_click = selector_probe(page)
                check(f"{vp_name}-click-chart-no-data-chart-tf", after_click["dataChartTf"] == 0)
                check(f"{vp_name}-click-chart-no-role-group", after_click["roleGroup"] == [])
                check(
                    f"{vp_name}-click-chart-no-tf-buttons",
                    after_click["chartTfButtons"] == 0 and after_click["buttonHits"] == [],
                    json.dumps(after_click["buttonHits"]),
                )
                check(
                    f"{vp_name}-click-chart-readonly-stays",
                    "Estratégia" in (after_click.get("readonly") or "") and "4h" in (after_click.get("readonly") or ""),
                    after_click.get("readonly"),
                )
                check(f"{vp_name}-click-chart-filter-intact", after_click["tfFilter"] is True)
                check(f"{vp_name}-click-keeps-list-4h", page.locator('[data-testid="monitor-pair-tf-btc"]').inner_text().strip() == "4h")
                click_shot = OUT / f"994-A-{vp_name}-{vp['width']}x{vp['height']}-chart-click.png"
                page.screenshot(path=str(click_shot), full_page=False)
                info["chart_click_shot"] = click_shot.name
                info["after_click"] = after_click
                payload["pages"][f"{vp_name}-index"] = info
                context.close()

            live_ctx = browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
            live_page = live_ctx.new_page()
            live_page.goto(LIVE_MONITOR, wait_until="networkidle", timeout=30000)
            live_shot = OUT / "994-A-live-monitor.png"
            live_page.screenshot(path=str(live_shot), full_page=False)
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
    (OUT / "994-A-gate.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": payload["passed"], "failed": payload["failed"], "total": payload["total"], "fails": failed}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
