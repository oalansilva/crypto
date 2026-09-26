#!/usr/bin/env python3
"""Assessment B browser gate — card 994 rework 1. Isolated. Local proto, not file://."""
from __future__ import annotations

import hashlib
import http.server
import json
import os
import re
import socket
import socketserver
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-994-monitor-multiplos-timeframes")
PROTO = ROOT / "frontend/public/prototypes/card-994-monitor-multiplos-timeframes"
PUBLIC = ROOT / "frontend/public"
OUT = ROOT / ".impeccable/critique"
HTTPS_BASE = "https://dev.criptofarol.com.br/prototypes/card-994-monitor-multiplos-timeframes"
LIVE = "https://dev.criptofarol.com.br/monitor"
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux-arm64/chrome"
EXPECTED_INDEX = "f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b"
EXPECTED_INDEX_BYTES = 39552
DETECT_JS = ROOT / ".agents/skills/impeccable/scripts/detector/detect-antipatterns-browser.js"

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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def https_get(url: str) -> tuple[int, bytes, str]:
    req = Request(url, headers={"User-Agent": "assessment-B-994-rework"})
    with urlopen(req, timeout=30) as resp:
        body = resp.read()
        return resp.status, body, resp.geturl()


def copied_utf8_sum(text: str) -> tuple[int, int, int, int]:
    starts = text.count("COPIED:start")
    ends = text.count("COPIED:end")
    copied_incl = 0
    copied_excl = 0
    for m in re.finditer(r"COPIED:start(.*?)COPIED:end", text, flags=re.S):
        copied_incl += len(m.group(0).encode("utf-8"))
        copied_excl += len(m.group(1).encode("utf-8"))
    return starts, ends, copied_incl, copied_excl


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: A003
        return


def start_static(directory: Path, port: int) -> tuple[socketserver.TCPServer, threading.Thread]:
    handler = lambda *a, **k: QuietHandler(*a, directory=str(directory), **k)  # noqa: E731
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
    httpd.daemon_threads = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, t


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    payload: dict = {
        "card": 994,
        "utc": utc,
        "model": "Grok 4.6 (grok-4.6)",
        "role": "Assessment B",
        "proxy": "Assessment B → Grok 4.6 (grok-4.6)",
        "chrome": CHROME,
        "console": [],
        "pageerrors": [],
        "badhttp": [],
        "shots": [],
        "viewports": [],
        "digest": {},
        "copied": {},
        "live": {},
        "asserts": [],
        "dumps": {},
        "detector": {},
        "overlay": {},
        "served": {},
    }

    index_disk = (PROTO / "index.html").read_bytes()
    text = index_disk.decode("utf-8")
    starts, ends, copied_incl, copied_excl = copied_utf8_sum(text)
    payload["copied"] = {
        "index": {
            "pairs_start": starts,
            "pairs_end": ends,
            "utf8_sum_incl_markers": copied_incl,
            "utf8_sum_excl_markers": copied_excl,
            "total": len(index_disk),
            "delta_start": text.count("DELTA:start"),
        }
    }

    digest_rows = {}
    for name, url in [
        ("index.html", f"{HTTPS_BASE}/"),
        ("index.html#explicit", f"{HTTPS_BASE}/index.html"),
    ]:
        try:
            status, remote, final = https_get(url)
            digest_rows[name] = {
                "disk": sha256_bytes(index_disk),
                "https": sha256_bytes(remote),
                "bytes_disk": len(index_disk),
                "bytes_https": len(remote),
                "http": status,
                "identical": remote == index_disk,
                "url": final,
            }
        except Exception as e:
            digest_rows[name] = {"error": str(e), "disk": sha256_bytes(index_disk)}
    payload["digest"] = digest_rows

    extras = {}
    for extra in ["erro.html", "favorites.html", "filtro.html", "home.html", "inicio.html", "grafico.html"]:
        extras[extra] = (PROTO / extra).exists()
        try:
            st, body, u = https_get(f"{HTTPS_BASE}/{extra}")
            extras[f"{extra}_http"] = st
            extras[f"{extra}_bytes"] = len(body)
        except Exception as e:
            extras[f"{extra}_http"] = getattr(e, "code", None) or str(e)
    payload["extras"] = extras

    try:
        st, body, u = https_get(LIVE)
        payload["live"]["curl"] = {
            "status": st,
            "final": u,
            "bytes": len(body),
            "sha16": sha256_bytes(body)[:16],
        }
    except Exception as e:
        payload["live"]["curl"] = {"error": str(e)}

    det_proc = subprocess.run(
        [
            "node",
            str(ROOT / ".agents/skills/impeccable/scripts/detect.mjs"),
            "--json",
            str(PROTO / "index.html"),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    det_raw = (det_proc.stdout or "").strip()
    try:
        det_json = json.loads(det_raw) if det_raw else []
    except json.JSONDecodeError:
        det_json = {"parse_error": det_raw[:2000]}
    payload["detector"] = {
        "exit": det_proc.returncode,
        "findings": det_json if isinstance(det_json, list) else [],
        "raw_type": type(det_json).__name__,
        "stderr": (det_proc.stderr or "")[:500],
        "count": len(det_json) if isinstance(det_json, list) else None,
        "rule_names": sorted(
            {
                (f.get("rule") or f.get("id") or f.get("name") or "")
                for f in (det_json if isinstance(det_json, list) else [])
                if isinstance(f, dict)
            }
            - {""}
        ),
    }
    (OUT / "994-B-detector.json").write_text(
        json.dumps(payload["detector"], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    def rec(vid: str, ok: bool, detail="") -> dict:
        item = {"id": vid, "ok": bool(ok), "detail": detail if isinstance(detail, (str, int, float, bool, dict, list)) else str(detail)}
        payload["asserts"].append(item)
        return item

    disk_sha = sha256_bytes(index_disk)
    https_sha = digest_rows.get("index.html", {}).get("https")
    rec(
        "digest_index_expected",
        disk_sha == EXPECTED_INDEX and len(index_disk) == EXPECTED_INDEX_BYTES,
        disk_sha,
    )
    rec(
        "digest_disk_eq_https",
        https_sha == disk_sha and digest_rows.get("index.html", {}).get("identical") is True,
        {"disk": disk_sha, "https": https_sha, "stale": https_sha != disk_sha},
    )
    rec("copied_utf8_gt_0", copied_incl > 0 and starts == 9 and ends == 9, f"{starts}/{ends} incl={copied_incl} excl={copied_excl}")
    rec("no_extra_favorites_disk", not extras["favorites.html"] and not extras["erro.html"] and not extras["grafico.html"], extras)
    rec("html_absent_grafico_1d", "Gráfico 1d" not in text)
    rec("html_absent_tf_1d", "tf 1d" not in text)
    rec("html_absent_data_chart_tf", "data-chart-tf" not in text)
    rec("html_absent_aria_select_chart_tf", 'aria-label="Selecionar timeframe do gráfico"' not in text)
    rec("html_absent_estrategia_4h_button_copy", "Estratégia (4H)" not in text)
    rec("html_has_readonly_estrategia_dot_4h", 'data-testid="chart-strategy-tf"' in text and "Estratégia ·" in text)
    rec("html_has_tf_filter", 'id="tf-filter"' in text)
    rec("html_has_btc", "BTC/USDT" in text)
    rec("html_has_eth_witness", "ETH/USDT" in text)
    rec("html_th_grafico", "Gráfico</th>" in text)
    rec("html_landmark_7d_in_copied_comment", "7d" in text)
    rec("html_no_chart_timeframe_testid", "chart-timeframe" not in text)
    rec(
        "html_js_does_not_switch_chart_tf",
        "data-chart-tf" not in text
        and "chart-timeframe" not in text
        and "setChart" not in text
        and "initialTimeframe" not in text,
        "filter JS only",
    )
    rec("detector_exit_0_or_2", det_proc.returncode in (0, 2), det_proc.returncode)
    rec("detector_clean", isinstance(det_json, list) and len(det_json) == 0 and det_proc.returncode == 0, payload["detector"]["count"])
    rec("not_n_estados_gallery_source", "N estados" not in text)

    static_port = free_port()
    httpd, _thr = start_static(PUBLIC, static_port)
    local_base = f"http://127.0.0.1:{static_port}/prototypes/card-994-monitor-multiplos-timeframes"
    payload["served"] = {
        "mode": "local-static frontend/public",
        "url": f"{local_base}/",
        "port": static_port,
        "https_measured": True,
        "https_stale": https_sha != disk_sha,
        "reason": "prompt: serve disk locally even when HTTPS matches; Chrome /login is not evidence",
    }

    payload["overlay"]["live_server"] = {
        "skipped": True,
        "reason": "write fence: Assessment B may only write .impeccable/critique/**; live-server would touch .impeccable/live/. Overlay injects detector JS in-page from skill file.",
        "detect_js": str(DETECT_JS),
        "detect_js_exists": DETECT_JS.exists(),
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=CHROME,
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )

            live_ctx = browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
            live_page = live_ctx.new_page()
            live_page.goto(LIVE, wait_until="networkidle", timeout=30000)
            live_page.wait_for_timeout(600)
            live_url = live_page.url
            live_body = live_page.inner_text("body")[:400]
            live_table = live_page.locator("table.signals").count()
            payload["live"]["browser"] = {
                "url": live_url,
                "is_login": "/login" in live_url.lower(),
                "table_signals": live_table,
                "body_prefix": live_body.replace("\n", " | ")[:300],
            }
            rec(
                "live_monitor_not_used_as_clone_proof",
                True,
                f"url={live_url} login={('/login' in live_url.lower())} tables={live_table}",
            )
            rec("live_is_login_without_session", "/login" in live_url.lower(), live_url)
            rec("live_login_not_treated_as_monitor_landmarks", live_table == 0 or "/login" in live_url.lower(), live_table)
            live_ctx.close()

            overlay_done = False
            for vp_name, vp in VIEWPORTS.items():
                vp_failed: list[str] = []
                vp_asserts: list[dict] = []
                dumps: dict = {}

                def check(cid: str, ok: bool, detail="") -> None:
                    item = {
                        "id": cid,
                        "ok": bool(ok),
                        "detail": detail if isinstance(detail, (str, int, float, bool, dict, list)) else str(detail),
                    }
                    vp_asserts.append(item)
                    payload["asserts"].append({**item, "id": f"{vp_name}-{cid}"})
                    if not ok:
                        vp_failed.append(cid)

                context = browser.new_context(viewport=vp, color_scheme="dark")
                page = context.new_page()
                cons: list[str] = []
                impeccable_logs: list[str] = []
                perr: list[str] = []
                badhttp: list[str] = []
                page.on(
                    "console",
                    lambda msg: (
                        cons.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None,
                        impeccable_logs.append(f"{msg.type}: {msg.text}") if "impeccable" in (msg.text or "").lower() else None,
                    ),
                )
                page.on("pageerror", lambda exc: perr.append(str(exc)))
                page.on(
                    "response",
                    lambda resp: badhttp.append(f"{resp.status} {resp.url}")
                    if resp.status >= 400 and "favicon" not in resp.url and "/brand/" not in resp.url
                    else None,
                )

                page.goto(f"{local_base}/", wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(400)

                mutation = page.evaluate(
                    """() => {
                      const prev = document.title;
                      document.title = 'impeccable-mutation-preflight';
                      const s = document.createElement('script');
                      s.id = 'impeccable-preflight';
                      s.textContent = 'window.__impeccablePreflight = true';
                      document.documentElement.appendChild(s);
                      return {
                        title: document.title,
                        restored_possible: prev !== document.title,
                        script: !!document.getElementById('impeccable-preflight'),
                        flag: window.__impeccablePreflight === true
                      };
                    }"""
                )
                dumps["mutation_preflight"] = mutation
                mutation_ok = bool(mutation and mutation.get("script") and mutation.get("flag") and mutation.get("restored_possible"))
                check("mutation_available", mutation_ok, mutation)
                page.evaluate("() => { document.title = 'Monitor de sinais — Cripto Farol'; }")

                body = page.inner_text("body")
                html = page.content()
                thead_tc = " ".join(page.locator("table.signals thead").all_text_contents())
                table_count = page.locator("table.signals").count()
                sidebar_w = page.evaluate(
                    """() => {
                      const el = document.querySelector('.sidebar');
                      if (!el) return null;
                      const cs = getComputedStyle(el);
                      return {display: cs.display, width: cs.width, offsetWidth: el.offsetWidth};
                    }"""
                )
                overflow = page.evaluate(
                    "() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})"
                )
                pair_tf_btc = page.locator('[data-testid="monitor-pair-tf-btc"]').first.inner_text().strip()
                spark_btc = page.locator('svg.spark[aria-label="Minigráfico BTC 4h"]').count()
                spark_eth = page.locator('svg.spark[aria-label="Minigráfico ETH 1d"]').count()
                tf_options = page.locator("#tf-filter option").all_inner_texts()
                detail_tf = page.locator(".detail-timeframe").all_inner_texts()
                th_visible = page.locator("table.signals thead th").all_inner_texts()
                chart_subtitle = page.locator("#chart-subtitle").inner_text() if page.locator("#chart-subtitle").count() else ""
                visible_bars = page.locator("#visible-bars").inner_text() if page.locator("#visible-bars").count() else ""
                chart_tf_el = page.locator('[data-testid="chart-strategy-tf"]')
                chart_tf_text = chart_tf_el.inner_text().strip() if chart_tf_el.count() else ""
                chart_tf_tag = chart_tf_el.evaluate("el => el.tagName") if chart_tf_el.count() else None
                chart_tf_role = chart_tf_el.get_attribute("role") if chart_tf_el.count() else None

                btn_15m = page.get_by_role("button", name=re.compile(r"^15m$", re.I)).count()
                btn_1h = page.get_by_role("button", name=re.compile(r"^1h$", re.I)).count()
                btn_1d = page.get_by_role("button", name=re.compile(r"^1d$", re.I)).count()
                btn_estrategia_4h = page.get_by_role("button", name=re.compile(r"Estratégia\s*\(4H\)", re.I)).count()
                aria_select = page.locator('[aria-label="Selecionar timeframe do gráfico"]').count()
                data_chart_tf = page.locator("[data-chart-tf]").count()
                chart_tf_buttons = page.locator("[data-testid^='chart-timeframe']").count()

                shot = OUT / f"994-B-{vp_name}-{vp['width']}x{vp['height']}-index.png"
                page.screenshot(path=str(shot), full_page=True)
                payload["shots"].append(str(shot))

                dumps["index"] = {
                    "url": page.url,
                    "title": page.title(),
                    "lang": page.locator("html").get_attribute("lang"),
                    "table_count": table_count,
                    "thead": thead_tc,
                    "th_visible": th_visible,
                    "sidebar": sidebar_w,
                    "overflow": overflow,
                    "pair_tf_btc": pair_tf_btc,
                    "tf_options": tf_options,
                    "detail_tf": detail_tf,
                    "spark_btc": spark_btc,
                    "spark_eth": spark_eth,
                    "chart_subtitle": chart_subtitle,
                    "visible_bars": visible_bars,
                    "chart_tf_text": chart_tf_text,
                    "chart_tf_tag": chart_tf_tag,
                    "chart_tf_role": chart_tf_role,
                    "btn_15m": btn_15m,
                    "btn_1h": btn_1h,
                    "btn_1d": btn_1d,
                    "btn_estrategia_4h": btn_estrategia_4h,
                    "aria_select": aria_select,
                    "data_chart_tf": data_chart_tf,
                    "chart_tf_buttons": chart_tf_buttons,
                    "body": body[:3500],
                    "h1": page.locator("h1").first.inner_text() if page.locator("h1").count() else "",
                }

                check("index_local_proto_url", page.url.startswith(local_base) and "/login" not in page.url.lower(), page.url)
                check("lm_table_signals", table_count >= 1, table_count)
                check("not_chrome_only", table_count >= 1 and "Par / Estratégia" in html)
                for needle in LANDMARKS:
                    in_html = needle in html or needle in thead_tc
                    check(f"lm_{needle}", in_html, needle)
                check("happy_btc", "BTC/USDT" in body)
                check("happy_eth_witness", "ETH/USDT" in body)
                check("happy_strategy", "Tendência em Virada" in body)
                check("pair_tf_btc_4h", pair_tf_btc.lower() == "4h", pair_tf_btc)
                check("filter_has_todos", any("Todos" in o for o in tf_options), tf_options)
                check("filter_has_4h", any(o.strip() == "4h" for o in tf_options), tf_options)
                check("filter_has_1d", any(o.strip() == "1d" for o in tf_options), tf_options)
                check("spark_btc_4h", spark_btc >= 1, spark_btc)
                check("spark_eth_1d", spark_eth >= 1, spark_eth)
                check(
                    "col_grafico_visible",
                    any("gráfico" in t.casefold() for t in th_visible) or "Gráfico" in thead_tc,
                    th_visible,
                )
                check("ficha_one_tf", all(t.strip().lower() == "4h" for t in detail_tf if t.strip()), detail_tf)
                check("absent_grafico_1d_body", "Gráfico 1d" not in body)
                check("absent_tf_1d_body", "tf 1d" not in body)
                check("absent_grafico_1d_html", "Gráfico 1d" not in html)
                check("absent_tf_1d_html", "tf 1d" not in html)
                check("absent_data_chart_tf", data_chart_tf == 0, data_chart_tf)
                check("absent_aria_select_chart_tf", aria_select == 0, aria_select)
                check("absent_chart_tf_buttons", chart_tf_buttons == 0, chart_tf_buttons)
                check("absent_btn_15m", btn_15m == 0, btn_15m)
                check("absent_btn_1h", btn_1h == 0, btn_1h)
                check("absent_btn_1d_chart", btn_1d == 0, btn_1d)
                check("absent_btn_estrategia_4h", btn_estrategia_4h == 0, btn_estrategia_4h)
                check("absent_estrategia_4h_copy", "Estratégia (4H)" not in body and "Estratégia (4H)" not in html)
                check(
                    "present_chart_strategy_tf_readonly",
                    chart_tf_el.count() == 1
                    and "estratégia" in chart_tf_text.casefold()
                    and "4h" in chart_tf_text.casefold()
                    and "·" in chart_tf_text
                    and (chart_tf_tag or "").lower() == "p",
                    {"text": chart_tf_text, "tag": chart_tf_tag, "role": chart_tf_role},
                )
                check("chart_open_strategy_4h", "4h" in (chart_subtitle.casefold() + " " + visible_bars.casefold()), {"subtitle": chart_subtitle, "bars": visible_bars})
                check("chart_modal_present", page.locator('[data-testid="chart-modal"]').count() >= 1)
                check("default_em_portfolio", "Em portfólio" in body)
                antes = page.locator("button").filter(has_text=re.compile(r"^Antes$")).count()
                depois = page.locator("button").filter(has_text=re.compile(r"^Depois$")).count()
                check("zero_antes_depois_buttons", antes == 0 and depois == 0, f"antes={antes} depois={depois}")
                check(
                    "not_panel_antes_depois",
                    "ANTES" not in body and "DEPOIS" not in body,
                    "comment-only in source" if ("ANTES" in html or "DEPOIS" in html) else "absent",
                )
                check("not_n_estados_gallery", "N estados" not in body and "N estados" not in html)
                check("no_h_overflow", overflow["sw"] <= overflow["cw"] + 1, overflow)
                check("index_lang", (page.locator("html").get_attribute("lang") or "").lower().startswith("pt"))
                if vp_name == "desktop":
                    check("sidebar_224", bool(sidebar_w) and sidebar_w.get("offsetWidth") == 224, sidebar_w)

                page.select_option("#tf-filter", "4h")
                page.wait_for_timeout(200)
                btc_hidden = page.locator('[data-testid="monitor-row-btc-usdt"]').get_attribute("hidden")
                eth_hidden = page.locator('[data-testid="monitor-row-eth-usdt"]').get_attribute("hidden")
                eth_card_hidden = page.locator('.mobile-card[data-row-tf="1d"]').first.get_attribute("hidden")
                btc_card_hidden = page.locator('[data-testid="monitor-mobile-btc-usdt"]').get_attribute("hidden")
                dumps["filter_4h"] = {
                    "btc_hidden": btc_hidden,
                    "eth_hidden": eth_hidden,
                    "btc_card_hidden": btc_card_hidden,
                    "eth_card_hidden": eth_card_hidden,
                    "count": page.locator("#result-count").inner_text() if page.locator("#result-count").count() else "",
                    "pair_tf": page.locator('[data-testid="monitor-pair-tf-btc"]').first.inner_text().strip(),
                    "body_has_eth": "ETH/USDT" in page.inner_text("body"),
                    "body_has_btc": "BTC/USDT" in page.inner_text("body"),
                }
                shot = OUT / f"994-B-{vp_name}-{vp['width']}x{vp['height']}-filtro-4h.png"
                page.screenshot(path=str(shot), full_page=True)
                payload["shots"].append(str(shot))
                check("filter_4h_keeps_btc", btc_hidden is None, dumps["filter_4h"])
                check("filter_4h_hides_eth", eth_hidden is not None, dumps["filter_4h"])
                check("filter_4h_hides_eth_card", eth_card_hidden is not None, dumps["filter_4h"])
                check(
                    "filter_4h_pair_tf_still_4h",
                    page.locator('[data-testid="monitor-pair-tf-btc"]').first.inner_text().strip().lower() == "4h",
                )
                if vp_name == "mobile":
                    check("filter_4h_mobile_eth_not_in_body", "ETH/USDT" not in page.inner_text(".monitor-board"))
                    check("filter_4h_mobile_btc_in_body", "BTC/USDT" in page.inner_text(".monitor-board"))

                page.select_option("#tf-filter", "1d")
                page.wait_for_timeout(200)
                btc_hidden = page.locator('[data-testid="monitor-row-btc-usdt"]').get_attribute("hidden")
                eth_hidden = page.locator('[data-testid="monitor-row-eth-usdt"]').get_attribute("hidden")
                dumps["filter_1d"] = {
                    "btc_hidden": btc_hidden,
                    "eth_hidden": eth_hidden,
                    "count": page.locator("#result-count").inner_text() if page.locator("#result-count").count() else "",
                    "body_board": page.inner_text(".monitor-board")[:800],
                }
                shot = OUT / f"994-B-{vp_name}-{vp['width']}x{vp['height']}-filtro-1d.png"
                page.screenshot(path=str(shot), full_page=True)
                payload["shots"].append(str(shot))
                check("filter_1d_hides_btc", btc_hidden is not None, dumps["filter_1d"])
                check("filter_1d_keeps_eth", eth_hidden is None, dumps["filter_1d"])
                if vp_name == "mobile":
                    check("filter_1d_mobile_btc_not_in_board", "BTC/USDT" not in page.inner_text(".monitor-board"))
                    check("filter_1d_mobile_eth_in_board", "ETH/USDT" in page.inner_text(".monitor-board"))

                page.select_option("#tf-filter", "all")
                page.wait_for_timeout(200)
                btc_hidden = page.locator('[data-testid="monitor-row-btc-usdt"]').get_attribute("hidden")
                eth_hidden = page.locator('[data-testid="monitor-row-eth-usdt"]').get_attribute("hidden")
                dumps["filter_all"] = {"btc_hidden": btc_hidden, "eth_hidden": eth_hidden}
                check("filter_todos_shows_btc", btc_hidden is None, dumps["filter_all"])
                check("filter_todos_shows_eth", eth_hidden is None, dumps["filter_all"])

                # Chart stays read-only after list filter; no JS path to swap candles.
                check(
                    "chart_readonly_after_filter",
                    page.locator('[data-testid="chart-strategy-tf"]').count() == 1
                    and page.locator("[data-testid^='chart-timeframe']").count() == 0
                    and page.get_by_role("button", name=re.compile(r"Estratégia\s*\(4H\)", re.I)).count() == 0,
                )
                shot = OUT / f"994-B-{vp_name}-{vp['width']}x{vp['height']}-grafico-readonly.png"
                page.locator('[data-testid="chart-modal"]').screenshot(path=str(shot))
                payload["shots"].append(str(shot))

                overlay_status = "skipped"
                if mutation_ok and DETECT_JS.exists() and not overlay_done:
                    try:
                        page.add_script_tag(path=str(DETECT_JS))
                        page.wait_for_timeout(2800)
                        overlay_dom = page.evaluate(
                            """() => ({
                              overlays: document.querySelectorAll('.impeccable-overlay, [data-impeccable], #impeccable-overlay').length,
                              scripts: [...document.scripts].map(s => s.src || s.id).filter(Boolean),
                              windowKeys: Object.keys(window).filter(k => /impeccable/i.test(k)).slice(0, 20)
                            })"""
                        )
                        browser_findings = page.evaluate(
                            """() => {
                              if (typeof window.impeccableDetect !== 'function') return [];
                              const raw = window.impeccableDetect();
                              return Array.isArray(raw) ? raw.slice(0, 80) : raw;
                            }"""
                        )
                        overlay_status = "injected"
                        dumps["overlay"] = {
                            "status": overlay_status,
                            "via": "add_script_tag(path=detect-antipatterns-browser.js) after contract shots",
                            "dom": overlay_dom,
                            "logs": impeccable_logs[:40],
                            "findings_count": len(browser_findings) if isinstance(browser_findings, list) else None,
                            "rule_names": sorted(
                                {
                                    (f.get("rule") or f.get("id") or f.get("name") or "")
                                    for f in (browser_findings if isinstance(browser_findings, list) else [])
                                    if isinstance(f, dict)
                                }
                                - {""}
                            ),
                        }
                        payload["detector"]["browser"] = {
                            "count": dumps["overlay"]["findings_count"],
                            "rule_names": dumps["overlay"]["rule_names"],
                            "findings": browser_findings if isinstance(browser_findings, list) else [],
                        }
                        (OUT / "994-B-detector-browser.json").write_text(
                            json.dumps(payload["detector"]["browser"], indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8",
                        )
                        shot = OUT / f"994-B-{vp_name}-{vp['width']}x{vp['height']}-overlay.png"
                        page.screenshot(path=str(shot), full_page=True)
                        payload["shots"].append(str(shot))
                        overlay_done = True
                    except Exception as e:
                        overlay_status = "inject_failed"
                        dumps["overlay"] = {"status": overlay_status, "error": str(e)}
                elif not mutation_ok:
                    overlay_status = "fallback_no_mutation"
                    dumps["overlay"] = {"status": overlay_status, "reason": "Playwright evaluate could not mutate title/script"}
                elif not DETECT_JS.exists():
                    overlay_status = "fallback_detect_js_missing"
                    dumps["overlay"] = {"status": overlay_status, "reason": str(DETECT_JS)}
                else:
                    overlay_status = "injected_other_viewport_only"
                    dumps["overlay"] = {"status": overlay_status}

                check(
                    "overlay_path_declared",
                    overlay_status in {"injected", "injected_other_viewport_only", "fallback_no_mutation", "fallback_detect_js_missing", "inject_failed"},
                    overlay_status,
                )

                filtered_console = [e for e in cons if "favicon" not in e.lower() and "/brand/" not in e.lower()]
                check("console_zero", len(filtered_console) == 0, "; ".join(filtered_console)[:400])
                check("pageerror_zero", len(perr) == 0, "; ".join(perr)[:400])
                proto_bad = [h for h in badhttp if "prototypes/card-994" in h]
                check("badhttp_zero", len(proto_bad) == 0, "; ".join(proto_bad)[:400])

                payload["viewports"].append(
                    {
                        "viewport": f"{vp_name} {vp['width']}x{vp['height']}",
                        "pass": len(vp_failed) == 0,
                        "n": len(vp_asserts),
                        "failed": vp_failed,
                        "asserts": vp_asserts,
                        "dumps": dumps,
                    }
                )
                payload["console"].extend(filtered_console)
                payload["pageerrors"].extend(perr)
                payload["badhttp"].extend(badhttp)
                payload["overlay"].setdefault("viewports", {})[vp_name] = dumps.get("overlay")
                context.close()

            browser.close()
    finally:
        payload["overlay"]["stop"] = "live-server not started (write fence)"
        httpd.shutdown()
        httpd.server_close()

    stale_inspect = list(OUT.glob("994-B-*-inspecao-1d.png"))
    for pth in stale_inspect:
        pth.unlink()
    payload["removed_stale_inspect_pngs"] = [str(p) for p in stale_inspect]

    payload["failed_ids"] = [a["id"] for a in payload["asserts"] if not a["ok"]]
    payload["pass"] = len(payload["failed_ids"]) == 0
    (OUT / "994-B-gate.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {
        "pass": payload["pass"],
        "failed": payload["failed_ids"],
        "copied": payload["copied"],
        "digest_index": digest_rows.get("index.html"),
        "detector": {"exit": payload["detector"]["exit"], "count": payload["detector"]["count"], "rules": payload["detector"]["rule_names"]},
        "overlay": payload["overlay"],
        "served": payload["served"],
        "live": payload["live"],
        "shots": payload["shots"],
        "console": payload["console"],
        "pageerrors": payload["pageerrors"],
        "viewports": [
            {"viewport": v["viewport"], "pass": v["pass"], "failed": v["failed"]}
            for v in payload["viewports"]
        ],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not payload["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
