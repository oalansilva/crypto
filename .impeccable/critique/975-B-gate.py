#!/usr/bin/env python3
"""Assessment B browser gate — card 975. Isolated. HTTPS only."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from playwright.sync_api import sync_playwright

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-975-monitor-vazio-favoritos")
PROTO = ROOT / "frontend/public/prototypes/card-975-monitor-vazio-favoritos"
OUT = ROOT / ".impeccable/critique"
BASE = "https://dev.criptofarol.com.br/prototypes/card-975-monitor-vazio-favoritos"
LIVE = "https://dev.criptofarol.com.br/monitor"
CHROME = "/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux-arm64/chrome"
EXPECTED_INDEX = "542974bc9333a62201dee9aef06c6cd4df3be7c372c31c6eea38f07e92142116"
EXPECTED_ERRO = "fb2a77198c0cca52b270b3f75e40e499f56580116d98b850a6f0e22f68810b34"
EXPECTED_INDEX_BYTES = 31012
EXPECTED_ERRO_BYTES = 24112

PAGES = {
    "index": f"{BASE}/",
    "erro": f"{BASE}/erro.html",
}
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}

EMPTY_CATALOG = "Nenhum ativo disponível no monitor"
ERROR_P = "Não foi possível carregar as estratégias."
ERROR_S = "A lista de favoritos não chegou. Isto não significa que não há estratégias."
RETRY = "Tentar de novo"
FILTER_EMPTY = "Não há resultado com estes filtros."
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def https_get(url: str) -> tuple[int, bytes, str]:
    req = Request(url, headers={"User-Agent": "assessment-B-975"})
    with urlopen(req, timeout=30) as resp:
        body = resp.read()
        return resp.status, body, resp.geturl()


def copied_utf8_sum(text: str) -> tuple[int, int, int]:
    starts = text.count("COPIED:start")
    ends = text.count("COPIED:end")
    copied = 0
    for m in re.finditer(r"COPIED:start(.*?)COPIED:end", text, flags=re.S):
        copied += len(m.group(0).encode("utf-8"))
    return starts, ends, copied


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    payload: dict = {
        "card": 975,
        "utc": utc,
        "chrome": CHROME,
        "url": PAGES["index"],
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

    index_disk = (PROTO / "index.html").read_bytes()
    erro_disk = (PROTO / "erro.html").read_bytes()
    starts, ends, copied = copied_utf8_sum(index_disk.decode("utf-8"))
    payload["copied"] = {
        "index": {
            "pairs_start": starts,
            "pairs_end": ends,
            "utf8_sum_incl_markers": copied,
            "total": len(index_disk),
        }
    }
    e_starts, e_ends, e_copied = copied_utf8_sum(erro_disk.decode("utf-8"))
    payload["copied"]["erro"] = {
        "pairs_start": e_starts,
        "pairs_end": e_ends,
        "utf8_sum_incl_markers": e_copied,
        "total": len(erro_disk),
    }

    digest_rows = {}
    for name, disk, url in [
        ("index.html", index_disk, PAGES["index"]),
        ("erro.html", erro_disk, PAGES["erro"]),
    ]:
        status, remote, final = https_get(url)
        digest_rows[name] = {
            "disk": sha256_bytes(disk),
            "https": sha256_bytes(remote),
            "bytes_disk": len(disk),
            "bytes_https": len(remote),
            "http": status,
            "identical": disk == remote,
            "url": final,
        }
    status, remote, final = https_get(f"{BASE}/index.html")
    digest_rows["index.html#explicit"] = {
        "https": sha256_bytes(remote),
        "bytes_https": len(remote),
        "http": status,
        "identical": remote == index_disk,
        "url": final,
    }
    payload["digest"] = digest_rows

    extras = {}
    for extra in ["filtro.html", "favorites.html", "home.html", "inicio.html"]:
        extras[extra] = (PROTO / extra).exists()
        try:
            st, body, u = https_get(f"{BASE}/{extra}")
            extras[f"{extra}_http"] = st
            extras[f"{extra}_bytes"] = len(body)
        except Exception as e:
            extras[f"{extra}_http"] = str(e)
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

    def rec(vid: str, ok: bool, detail="") -> dict:
        item = {"id": vid, "ok": bool(ok), "detail": detail}
        payload["asserts"].append(item)
        return item

    rec(
        "digest_index_expected",
        digest_rows["index.html"]["disk"] == EXPECTED_INDEX
        and digest_rows["index.html"]["identical"]
        and digest_rows["index.html"]["bytes_disk"] == EXPECTED_INDEX_BYTES,
        digest_rows["index.html"]["disk"],
    )
    rec(
        "digest_erro_expected",
        digest_rows["erro.html"]["disk"] == EXPECTED_ERRO
        and digest_rows["erro.html"]["identical"]
        and digest_rows["erro.html"]["bytes_disk"] == EXPECTED_ERRO_BYTES,
        digest_rows["erro.html"]["disk"],
    )
    rec("copied_utf8_gt_0", copied > 0 and starts == 7 and ends == 7, f"{starts}/{ends} sum={copied}")
    rec("no_extra_favorites_disk", not extras["favorites.html"] and not extras["filtro.html"])

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
        rec(
            "live_monitor_not_used_as_clone_proof",
            True,
            f"url={live_url} login={('/login' in live_url.lower())}",
        )
        rec("live_is_login_without_session", "/login" in live_url.lower(), live_url)
        live_ctx.close()

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

            page.goto(PAGES["index"], wait_until="networkidle", timeout=30000)
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
            shot = OUT / f"975-B-{vp_name}-{vp['width']}x{vp['height']}-index.png"
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
                "body": body[:2500],
                "h1": page.locator("h1").first.inner_text() if page.locator("h1").count() else "",
            }

            check("index_proto_url", page.url.startswith(BASE) and "/login" not in page.url.lower(), page.url)
            check("lm_table_signals", table_count >= 1, table_count)
            check("not_chrome_only", table_count >= 1 and "Par / Estratégia" in html)
            for needle in LANDMARKS:
                in_html = needle in html or needle in thead_tc
                check(f"lm_{needle}", in_html, needle)
            check("happy_sol", "SOL/USDT" in body)
            check("happy_eth", "ETH/USDT" in body)
            check("absent_empty_catalog", EMPTY_CATALOG not in body)
            check("absent_empty_in_html", EMPTY_CATALOG not in html)
            check("index_not_error_p", ERROR_P not in body)
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

            page.goto(PAGES["erro"], wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(400)
            body = page.inner_text("body")
            html = page.content()
            table_count = page.locator("table.signals").count()
            thead_tc = " ".join(page.locator("table.signals thead").all_text_contents())
            retry_box = None
            if page.locator(".monitor-retry").count():
                retry_box = page.locator(".monitor-retry").first.evaluate(
                    "el => { const r = el.getBoundingClientRect(); return {w: r.width, h: r.height, text: el.textContent}; }"
                )
            overflow = page.evaluate(
                "() => ({sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth})"
            )
            shot = OUT / f"975-B-{vp_name}-{vp['width']}x{vp['height']}-erro.png"
            page.screenshot(path=str(shot), full_page=True)
            payload["shots"].append(str(shot))

            dumps["erro"] = {
                "url": page.url,
                "title": page.title(),
                "table_count": table_count,
                "thead": thead_tc,
                "retry_box": retry_box,
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
            check("erro_no_filter_empty_as_catalog", FILTER_EMPTY not in body)
            if retry_box:
                check("erro_retry_min_height_note", True, retry_box)

            filtered_console = [e for e in cons if "favicon" not in e.lower()]
            check("console_zero", len(filtered_console) == 0, "; ".join(filtered_console)[:400])
            check("pageerror_zero", len(perr) == 0, "; ".join(perr)[:400])
            proto_bad = [h for h in badhttp if "prototypes/card-975" in h]
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

    payload["failed_ids"] = [a["id"] for a in payload["asserts"] if not a["ok"]]
    payload["pass"] = len(payload["failed_ids"]) == 0
    (OUT / "975-B-gate.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {
        "pass": payload["pass"],
        "failed": payload["failed_ids"],
        "copied": payload["copied"],
        "digest_index": digest_rows["index.html"],
        "digest_erro": digest_rows["erro.html"],
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
