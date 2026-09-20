#!/usr/bin/env python3
"""Assessment B browser gate — card 995. Isolated. Worktree HTTP + HTTPS 404 note."""
from __future__ import annotations

import hashlib
import http.server
import json
import re
import socketserver
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-995-monitor-retry-rede")
PUBLIC = ROOT / "frontend/public"
PROTO = PUBLIC / "prototypes/card-995-monitor-retry-rede"
OUT = ROOT / ".impeccable/critique"
CANONICAL = "https://dev.criptofarol.com.br/prototypes/card-995-monitor-retry-rede"
LIVE = "https://dev.criptofarol.com.br/monitor"
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux-arm64/chrome"
EXPECTED = {
    "index.html": ("5c80aa4a01efa5fab1ca1a56cdc3461e0213b22d3bfd1056fa7762407c617b9a", 31568),
    "carga.html": ("00f523eb23752b39ab27e439ccfad82b00da98097a671c5878696060209e5fd4", 23657),
    "erro.html": ("86d863acbb9318dfe9d5439a6e91d5fc5d1d6fde9a57065e1c464b69d40f6223", 24773),
    "sessao.html": ("7879cd2630a22d2929db07cdfc7c0da5e1ba4f37e22261782a3ac7547d09c584", 4933),
}

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}

EMPTY_CATALOG = "Nenhum ativo disponível no monitor"
TOAST = "Não foi possível carregar preferências do monitor."
ERROR_P = "Não foi possível carregar as estratégias."
ERROR_S = "A lista de favoritos não chegou. Isto não significa que não há estratégias."
RETRY = "Tentar de novo"
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def https_get(url: str) -> tuple[int, bytes, str]:
    req = Request(url, headers={"User-Agent": "assessment-B-995"})
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.status, resp.read(), resp.geturl()
    except HTTPError as exc:
        return exc.code, exc.read(), url


def copied_utf8_sum(text: str) -> tuple[int, int, int]:
    starts = text.count("COPIED:start")
    ends = text.count("COPIED:end")
    copied = 0
    for m in re.finditer(r"COPIED:start(.*?)COPIED:end", text, flags=re.S):
        copied += len(m.group(0).encode("utf-8"))
    return starts, ends, copied


def kpi_zero_as_truth(page) -> bool:
    return page.evaluate(
        """() => {
          const vals = [...document.querySelectorAll('.kpi-val')];
          return vals.some((el) => (el.textContent || '').trim() === '0'
            && !el.hasAttribute('data-kpi-pending'));
        }"""
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    payload: dict = {
        "card": 995,
        "utc": utc,
        "chrome": CHROME,
        "canonical": CANONICAL + "/",
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
    }

    disk = {name: (PROTO / name).read_bytes() for name in EXPECTED}
    for name, data in disk.items():
        starts, ends, copied = copied_utf8_sum(data.decode("utf-8"))
        payload["copied"][name] = {
            "pairs_start": starts,
            "pairs_end": ends,
            "utf8_sum_incl_markers": copied,
            "total": len(data),
            "generated": len(data) - copied,
            "delta_start": data.decode("utf-8").count("DELTA:start"),
        }

    digest_rows = {}
    https_urls = {
        "index.html": f"{CANONICAL}/",
        "index.html#explicit": f"{CANONICAL}/index.html",
        "carga.html": f"{CANONICAL}/carga.html",
        "erro.html": f"{CANONICAL}/erro.html",
        "sessao.html": f"{CANONICAL}/sessao.html",
    }
    for label, url in https_urls.items():
        status, remote, final = https_get(url)
        disk_name = label.split("#")[0]
        digest_rows[label] = {
            "disk": sha256_bytes(disk[disk_name]),
            "https": sha256_bytes(remote),
            "bytes_disk": len(disk[disk_name]),
            "bytes_https": len(remote),
            "http": status,
            "identical": remote == disk[disk_name],
            "url": final,
        }
    payload["digest"] = digest_rows

    extras = {}
    for extra in ["favorites.html", "monitor.html", "inicio.html", "home.html", "carteira.html", "filtro.html"]:
        extras[extra] = (PROTO / extra).exists()
        st, body, _u = https_get(f"{CANONICAL}/{extra}")
        extras[f"{extra}_http"] = st
        extras[f"{extra}_bytes"] = len(body)
    payload["extras"] = extras

    st, body, u = https_get(LIVE)
    payload["live"]["curl"] = {
        "status": st,
        "final": u,
        "bytes": len(body),
        "sha16": sha256_bytes(body)[:16],
    }

    def rec(vid: str, ok: bool, detail="") -> dict:
        item = {"id": vid, "ok": bool(ok), "detail": detail}
        payload["asserts"].append(item)
        return item

    for name, (sha, nbytes) in EXPECTED.items():
        rec(
            f"digest_{name}_expected",
            sha256_bytes(disk[name]) == sha and len(disk[name]) == nbytes,
            sha256_bytes(disk[name]),
        )
    rec(
        "https_canonical_404_documented",
        digest_rows["index.html"]["http"] == 404,
        f"http={digest_rows['index.html']['http']} bytes={digest_rows['index.html']['bytes_https']}",
    )
    rec("copied_index_gt_0", payload["copied"]["index.html"]["utf8_sum_incl_markers"] > 0)
    rec(
        "copied_index_pairs_7",
        payload["copied"]["index.html"]["pairs_start"] == 7
        and payload["copied"]["index.html"]["pairs_end"] == 7,
        f"{payload['copied']['index.html']['pairs_start']}/{payload['copied']['index.html']['pairs_end']}",
    )
    rec("no_extra_favorites_disk", not extras["favorites.html"] and not extras["inicio.html"])

    httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}/prototypes/card-995-monitor-retry-rede"
    payload["local_base"] = base
    pages = {
        "index": f"{base}/",
        "carga": f"{base}/carga.html",
        "erro": f"{base}/erro.html",
        "sessao": f"{base}/sessao.html",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        live_ctx = browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
        live_page = live_ctx.new_page()
        live_page.goto(LIVE, wait_until="networkidle", timeout=30000)
        live_page.wait_for_timeout(800)
        live_url = live_page.url
        live_body = live_page.inner_text("body")[:400]
        payload["live"]["browser"] = {
            "url": live_url,
            "is_login": "/login" in live_url.lower(),
            "body_prefix": live_body.replace("\n", " | ")[:300],
        }
        rec("live_monitor_not_used_as_clone_proof", True, f"url={live_url}")
        rec("live_is_login_without_session", "/login" in live_url.lower(), live_url)
        live_ctx.close()

        https_ctx = browser.new_context(viewport={"width": 1440, "height": 900}, color_scheme="dark")
        https_page = https_ctx.new_page()
        https_page.goto(CANONICAL + "/", wait_until="domcontentloaded", timeout=30000)
        https_page.wait_for_timeout(400)
        https_shot = OUT / "995-B-https-404-canonical.png"
        https_page.screenshot(path=str(https_shot), full_page=True)
        payload["shots"].append(str(https_shot))
        payload["https_browser"] = {
            "url": https_page.url,
            "title": https_page.title(),
            "body": https_page.inner_text("body")[:500],
        }
        rec(
            "https_browser_is_404_not_empty_snapshot",
            "Protótipo não encontrado" in https_page.inner_text("body"),
            https_page.title(),
        )
        https_ctx.close()

        for vp_name, vp in VIEWPORTS.items():
            vp_failed: list[str] = []
            vp_asserts: list[dict] = []
            dumps: dict = {}

            def check(cid: str, ok: bool, detail="") -> None:
                item = {"id": cid, "ok": bool(ok), "detail": detail}
                vp_asserts.append(item)
                payload["asserts"].append({"id": f"{vp_name}-{cid}", **item})
                if not ok:
                    vp_failed.append(cid)

            context = browser.new_context(viewport=vp, color_scheme="dark")
            page = context.new_page()
            cons: list[str] = []
            perr: list[str] = []
            badhttp: list[str] = []
            page.on(
                "console",
                lambda msg: cons.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None,
            )
            page.on("pageerror", lambda exc: perr.append(str(exc)))
            page.on(
                "response",
                lambda resp: badhttp.append(f"{resp.status} {resp.url}")
                if resp.status >= 400 and "favicon" not in resp.url
                else None,
            )

            # --- index (feliz) ---
            page.goto(pages["index"], wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(500)
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
            shot = OUT / f"995-B-{vp_name}-{vp['width']}x{vp['height']}-index.png"
            page.screenshot(path=str(shot), full_page=True)
            payload["shots"].append(str(shot))
            dumps["index"] = {
                "url": page.url,
                "title": page.title(),
                "lang": page.locator("html").get_attribute("lang"),
                "table_count": table_count,
                "thead": thead_tc,
                "sidebar": sidebar_w,
                "overflow": overflow,
                "kpi_zero_truth": kpi_zero_as_truth(page),
                "refresh_mode": page.locator("[data-testid=monitor-refresh]").get_attribute("data-load-mode")
                if page.locator("[data-testid=monitor-refresh]").count()
                else None,
                "body": body[:2500],
            }
            check("index_proto_url", "/prototypes/card-995-monitor-retry-rede" in page.url and "/login" not in page.url.lower(), page.url)
            check("lm_table_signals", table_count >= 1, table_count)
            check("not_chrome_only", table_count >= 1 and "Par / Estratégia" in html)
            for needle in LANDMARKS:
                check(f"lm_{needle}", needle in html or needle in thead_tc, needle)
            check("happy_sol", "SOL/USDT" in body)
            check("happy_eth", "ETH/USDT" in body)
            check("absent_empty_catalog", EMPTY_CATALOG not in body)
            check("absent_empty_in_html", EMPTY_CATALOG not in html)
            check("index_not_error_p", ERROR_P not in body)
            check("index_not_toast", TOAST not in body and TOAST not in html)
            check("index_not_loading", LOADING not in body)
            check("index_not_retry", RETRY not in body)
            check("index_kpi_not_zero_truth", not kpi_zero_as_truth(page))
            check("index_refresh_recompute", dumps["index"]["refresh_mode"] == "recompute", dumps["index"]["refresh_mode"])
            antes = page.locator("button").filter(has_text=re.compile(r"^Antes$")).count()
            depois = page.locator("button").filter(has_text=re.compile(r"^Depois$")).count()
            check("zero_antes_depois_buttons", antes == 0 and depois == 0, f"antes={antes} depois={depois}")
            check(
                "not_panel_antes_depois",
                "ANTES" not in body and "DEPOIS" not in body,
                "comment-only in source" if ("ANTES" in html or "DEPOIS" in html) else "absent",
            )
            check("not_n_estados_gallery", "N estados" not in body and "N estados" not in html)
            check("default_em_portfolio", "Em portfólio" in body)
            check("default_todos_present", "Todos" in body)
            check("no_h_overflow", overflow["sw"] <= overflow["cw"] + 1, overflow)
            check("index_lang", (page.locator("html").get_attribute("lang") or "").lower().startswith("pt"))
            check("index_atualizar", "Atualizar" in body)

            # --- carga ---
            page.goto(pages["carga"], wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(400)
            body = page.inner_text("body")
            html = page.content()
            overflow = page.evaluate(
                "() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})"
            )
            shot = OUT / f"995-B-{vp_name}-{vp['width']}x{vp['height']}-carga.png"
            page.screenshot(path=str(shot), full_page=True)
            payload["shots"].append(str(shot))
            dumps["carga"] = {
                "url": page.url,
                "loading": LOADING in body,
                "kpi_zero_truth": kpi_zero_as_truth(page),
                "pending": page.locator("[data-kpi-pending]").count(),
                "role_status": page.locator("[role=status]").count(),
                "overflow": overflow,
                "body": body[:2000],
            }
            check("carga_proto_url", page.url.endswith("/carga.html"), page.url)
            check("carga_loading", LOADING in body)
            check("carga_not_error_p", ERROR_P not in body)
            check("carga_not_retry", RETRY not in body)
            check("carga_not_toast", TOAST not in body and TOAST not in html)
            check("carga_not_empty", EMPTY_CATALOG not in body)
            check("carga_kpi_not_zero_truth", not kpi_zero_as_truth(page))
            check("carga_pending_kpis", page.locator("[data-kpi-pending]").count() >= 4, page.locator("[data-kpi-pending]").count())
            check("carga_role_status", page.locator("[role=status]").count() >= 1)
            check("carga_chrome_monitor", "Monitor" in body)
            check("carga_no_h_overflow", overflow["sw"] <= overflow["cw"] + 1, overflow)

            # --- erro ---
            page.goto(pages["erro"], wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(400)
            body = page.inner_text("body")
            html = page.content()
            table_count = page.locator("table.signals").count()
            thead_tc = " ".join(page.locator("table.signals thead").all_text_contents())
            retry_box = None
            retry_mode = None
            if page.locator(".monitor-retry").count():
                retry_box = page.locator(".monitor-retry").first.evaluate(
                    "el => { const r = el.getBoundingClientRect(); return {w: r.width, h: r.height, text: el.textContent, href: el.getAttribute('href')}; }"
                )
                retry_mode = page.locator(".monitor-retry").first.get_attribute("data-load-mode")
            overflow = page.evaluate(
                "() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})"
            )
            shot = OUT / f"995-B-{vp_name}-{vp['width']}x{vp['height']}-erro.png"
            page.screenshot(path=str(shot), full_page=True)
            payload["shots"].append(str(shot))
            dumps["erro"] = {
                "url": page.url,
                "table_count": table_count,
                "thead": thead_tc,
                "retry_box": retry_box,
                "retry_mode": retry_mode,
                "kpi_zero_truth": kpi_zero_as_truth(page),
                "role_alert": page.locator("[role=alert]").count(),
                "overflow": overflow,
                "body": body[:2500],
            }
            check("erro_proto_url", page.url.endswith("/erro.html") and "/login" not in page.url.lower(), page.url)
            check("erro_copy_p", ERROR_P in body)
            check("erro_copy_s", ERROR_S in body)
            check("erro_retry", RETRY in body)
            check("erro_no_empty_catalog", EMPTY_CATALOG not in body)
            check("erro_no_empty_in_html", EMPTY_CATALOG not in html)
            check("erro_chrome_monitor", "Monitor" in body)
            check("erro_table_signals", table_count >= 1, table_count)
            for needle in LANDMARKS:
                check(f"erro_lm_{needle}", needle in html or needle in thead_tc, needle)
            check("erro_not_login", "/login" not in page.url.lower(), page.url)
            check("erro_kpi_not_zero_truth", not kpi_zero_as_truth(page))
            check("erro_retry_reread", retry_mode == "reread", retry_mode)
            check("erro_retry_href_index", bool(retry_box) and retry_box.get("href") == "index.html", retry_box)
            check("erro_role_alert", page.locator("[role=alert]").count() >= 1)
            if retry_box:
                check("erro_retry_height_44", retry_box["h"] >= 44, retry_box)

            # --- sessao ---
            page.goto(pages["sessao"], wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(400)
            body = page.inner_text("body")
            html = page.content()
            overflow = page.evaluate(
                "() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})"
            )
            shot = OUT / f"995-B-{vp_name}-{vp['width']}x{vp['height']}-sessao.png"
            page.screenshot(path=str(shot), full_page=True)
            payload["shots"].append(str(shot))
            dumps["sessao"] = {
                "url": page.url,
                "overflow": overflow,
                "body": body[:2000],
            }
            check("sessao_proto_url", page.url.endswith("/sessao.html"), page.url)
            check("sessao_login", "Bem-vindo de volta" in body and "Entrar" in body)
            check("sessao_not_error_p", ERROR_P not in body)
            check("sessao_not_retry", RETRY not in body)
            check("sessao_lang", (page.locator("html").get_attribute("lang") or "").lower().startswith("pt"))
            check("sessao_no_h_overflow", overflow["sw"] <= overflow["cw"] + 1, overflow)
            check("sessao_email_label", page.locator("label[for=email]").count() >= 1)
            check("sessao_password_label", page.locator("label[for=password]").count() >= 1)

            filtered_console = [e for e in cons if "favicon" not in e.lower()]
            check("console_zero", len(filtered_console) == 0, "; ".join(filtered_console)[:400])
            check("pageerror_zero", len(perr) == 0, "; ".join(perr)[:400])
            proto_bad = [h for h in badhttp if "prototypes/card-995" in h]
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
            context.close()

        browser.close()

    httpd.shutdown()
    payload["failed_ids"] = [a["id"] for a in payload["asserts"] if not a["ok"]]
    payload["pass"] = len(payload["failed_ids"]) == 0
    (OUT / "995-B-gate.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {
        "pass": payload["pass"],
        "failed": payload["failed_ids"],
        "copied": payload["copied"],
        "digest": {k: {"http": v.get("http"), "identical": v.get("identical"), "bytes_https": v.get("bytes_https"), "disk": v.get("disk")} for k, v in digest_rows.items()},
        "live": payload["live"],
        "https_browser": payload.get("https_browser"),
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
