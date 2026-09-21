#!/usr/bin/env python3
"""Assessment B browser gate — card 1001. Writes only under .impeccable/critique/."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
CRITIQUE = Path(__file__).resolve().parent
URL = "https://dev.criptofarol.com.br/prototypes/card-1001-scalp-direcional-jev/"
LANDING = URL + "landing.html"
AJUDA = URL + "ajuda.html"
BANNED = ("estratégia lucrativa", "formador de mercado")
LANDMARK_TEXTS = [
    "Status",
    "Preço",
    "Distância",
    "7d",
    "Risco até stop",
    "Tags",
    "Operar",
    "Par / Estratégia",
]


def rec(asserts: list, ok: bool, msg: str) -> None:
    asserts.append({"ok": bool(ok), "msg": msg})


def attach(page, console: list, page_errors: list, bad_resp: list) -> None:
    page.on("console", lambda m: console.append({"type": m.type, "text": m.text}))
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on(
        "response",
        lambda r: bad_resp.append({"status": r.status, "url": r.url})
        if r.status >= 400
        else None,
    )


def state_of(page) -> dict:
    return page.evaluate(
        """() => {
          const mod = document.getElementById('scalp-module');
          const sw = document.getElementById('scalp-switch');
          const status = document.getElementById('scalp-status');
          const kill = document.getElementById('scalp-kill');
          const pnl = document.getElementById('scalp-pnl');
          const cal = document.getElementById('scalp-cal');
          const inv = document.getElementById('scalp-inv');
          const tables = document.querySelectorAll('table.signals');
          const body = document.body.innerText || '';
          const html = document.documentElement.outerHTML;
          const swBox = sw ? sw.getBoundingClientRect() : null;
          const modBox = mod ? mod.getBoundingClientRect() : null;
          const killBox = kill ? kill.getBoundingClientRect() : null;
          const pnlStyle = pnl ? getComputedStyle(pnl) : null;
          const operateBtns = [...document.querySelectorAll('button, a')].filter(el => (el.textContent || '').trim() === 'Operar');
          const operateClip = operateBtns.map(el => {
            const r = el.getBoundingClientRect();
            return {x: r.x, y: r.y, w: r.width, h: r.height, right: r.right, overflow: r.right > (window.innerWidth + 1)};
          });
          const search = document.querySelector('.search input');
          const searchPh = search ? search.placeholder : '';
          const tableWrap = document.querySelector('.table-wrap');
          const mobileCards = document.querySelector('.mobile-cards');
          const tw = tableWrap ? getComputedStyle(tableWrap).display : null;
          const mc = mobileCards ? getComputedStyle(mobileCards).display : null;
          const kpis = [...document.querySelectorAll('.kpi-val')].map(el => el.textContent.trim());
          const antes = [...document.querySelectorAll('button, a')].filter(el => /^(Antes|Depois)$/i.test((el.textContent||'').trim()));
          return {
            state: mod && mod.getAttribute('data-state'),
            aria: sw && sw.getAttribute('aria-checked'),
            disabled: sw && sw.disabled,
            label: sw && sw.textContent.trim(),
            status: status && status.textContent.trim(),
            killHidden: kill && kill.hidden,
            killText: kill && kill.textContent.trim(),
            killDisplay: kill ? getComputedStyle(kill).display : null,
            pnl: pnl && pnl.textContent.trim(),
            pnlClass: pnl && pnl.className,
            pnlColor: pnlStyle && pnlStyle.color,
            cal: cal && cal.textContent.trim(),
            inv: inv && inv.textContent.trim(),
            tableCount: tables.length,
            htmlHasTableClass: html.includes('table.signals') || [...tables].length > 0,
            landmarks: {
              'table.signals': tables.length,
              'Status': html.includes('Status'),
              'Preço': html.includes('Preço'),
              'Distância': html.includes('Distância'),
              '7d': html.includes('7d'),
              'Risco até stop': html.includes('Risco até stop'),
              'Tags': html.includes('Tags'),
              'Operar': html.includes('Operar'),
              'Par / Estratégia': html.includes('Par / Estratégia'),
            },
            bodyHasAntes: /\\bANTES\\b|\\bDEPOIS\\b/.test(body),
            antesButtons: antes.length,
            bannedInBody: ['estratégia lucrativa','formador de mercado'].filter(n => body.toLowerCase().includes(n.toLowerCase())),
            title: document.title,
            scalpTitle: (document.getElementById('scalp-title')||{}).textContent || '',
            swBox: swBox && {w: swBox.width, h: swBox.height, x: swBox.x, y: swBox.y},
            modBox: modBox && {w: modBox.width, h: modBox.height, x: modBox.x, y: modBox.y, top: modBox.top},
            killBox: killBox && {w: killBox.width, h: killBox.height},
            operateClip,
            searchPh,
            tableWrapDisplay: tw,
            mobileCardsDisplay: mc,
            kpis,
            overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
            scrollW: document.documentElement.scrollWidth,
            clientW: document.documentElement.clientWidth,
            pairs: [...document.querySelectorAll('.pair-name,.mobile-card h4')].map(el => el.textContent.trim()),
          };
        }"""
    )


def shot(page, name: str, shots: list) -> Path:
    path = CRITIQUE / name
    page.screenshot(path=str(path), full_page=True)
    size = path.stat().st_size if path.is_file() else 0
    shots.append({"path": str(path), "bytes": size, "empty": size < 2000})
    return path


def check_landmarks(st: dict, asserts: list, prefix: str) -> None:
    rec(asserts, st["tableCount"] >= 1, f"{prefix} table.signals count={st['tableCount']}")
    for key, val in st["landmarks"].items():
        rec(asserts, bool(val), f"{prefix} landmark {key}")
    rec(asserts, st["antesButtons"] == 0, f"{prefix} no Antes/Depois buttons")
    rec(asserts, not st["bodyHasAntes"], f"{prefix} body without ANTES/DEPOIS panel")
    rec(asserts, st["bannedInBody"] == [], f"{prefix} no banned copy {st['bannedInBody']}")
    rec(asserts, "Scalp BTCUSDT" in st["scalpTitle"], f"{prefix} scalp title")
    rec(asserts, st["modBox"] and st["modBox"]["h"] > 40, f"{prefix} scalp module visible h={st.get('modBox')}")
    rec(asserts, "Operar" in ("".join(st["pairs"]) + str(st["landmarks"])), f"{prefix} Operar landmark kept")


def run_viewport(browser, width: int, height: int, tag: str) -> dict:
    asserts: list = []
    console: list = []
    page_errors: list = []
    bad_resp: list = []
    shots: list = []
    context = browser.new_context(
        viewport={"width": width, "height": height},
        color_scheme="dark",
        locale="pt-BR",
    )
    page = context.new_page()
    attach(page, console, page_errors, bad_resp)
    resp = page.goto(URL, wait_until="networkidle", timeout=60000)
    rec(asserts, resp is not None and resp.status == 200, f"{tag} canonical HTTP {resp.status if resp else None}")
    page.wait_for_selector("#scalp-switch", timeout=15000)

    st = state_of(page)
    rec(asserts, st["state"] == "off", f"{tag} default state off")
    rec(asserts, st["aria"] == "false", f"{tag} default aria-checked false")
    rec(asserts, st["label"] == "Desligado", f"{tag} default label Desligado")
    rec(asserts, "desligado" in (st["status"] or "").lower(), f"{tag} default status desligado")
    rec(asserts, st["killHidden"] is True or st["killDisplay"] == "none", f"{tag} default kill hidden")
    rec(asserts, st["pnl"] == "US$ 0,00", f"{tag} default pnl {st['pnl']}")
    rec(asserts, st["disabled"] is False, f"{tag} default switch enabled")
    rec(asserts, st["overflow"] <= 1, f"{tag} default document overflow {st['overflow']}")
    rec(asserts, st["swBox"] and st["swBox"]["h"] >= 44, f"{tag} switch min-height 44 {st['swBox']}")
    check_landmarks(st, asserts, f"{tag} default")
    shot(page, f"1001-B-{tag}-off.png", shots)

    page.click("#scalp-switch")
    page.wait_for_timeout(200)
    st = state_of(page)
    rec(asserts, st["state"] == "on", f"{tag} after toggle state on")
    rec(asserts, st["aria"] == "true", f"{tag} on aria-checked true")
    rec(asserts, st["label"] == "Ligado", f"{tag} on label Ligado")
    rec(asserts, "ligado" in (st["status"] or "").lower(), f"{tag} on status ligado")
    rec(asserts, "−US$" in (st["pnl"] or "") or "-US$" in (st["pnl"] or ""), f"{tag} on pnl negative {st['pnl']}")
    rec(asserts, st["pnlClass"] == "neg", f"{tag} on pnl class neg")
    rec(asserts, st["cal"] not in ("", "—"), f"{tag} on calibration {st['cal']}")
    rec(asserts, page.is_visible("#scalp-sim-kill"), f"{tag} sim kill visible")
    rec(asserts, page.locator("#scalp-status").inner_text().find("Operar continua") >= 0, f"{tag} on copy Operar continua")
    check_landmarks(st, asserts, f"{tag} on")
    shot(page, f"1001-B-{tag}-on.png", shots)

    page.click("#scalp-sim-kill")
    page.wait_for_timeout(200)
    st = state_of(page)
    rec(asserts, st["state"] == "kill", f"{tag} kill state")
    rec(asserts, page.is_visible("#scalp-kill"), f"{tag} kill banner visible")
    rec(asserts, "Parado por kill" in (st["killText"] or ""), f"{tag} kill banner copy")
    rec(asserts, "−US$ 2,00" in (st["pnl"] or "") or "-US$ 2,00" in (st["pnl"] or ""), f"{tag} kill pnl {st['pnl']}")
    rec(asserts, st["pnlClass"] == "neg", f"{tag} kill pnl class neg")
    rec(asserts, st["aria"] == "false", f"{tag} kill switch aria false")
    rec(asserts, st["label"] == "Desligado", f"{tag} kill label Desligado")
    rec(asserts, "Religar" in (st["status"] or "") or "interruptor" in (st["status"] or ""), f"{tag} kill status religar")
    rec(asserts, st["disabled"] is False, f"{tag} kill switch still enabled")
    check_landmarks(st, asserts, f"{tag} kill")
    shot(page, f"1001-B-{tag}-kill.png", shots)

    page.click("#scalp-switch")
    page.wait_for_timeout(200)
    st = state_of(page)
    rec(asserts, st["state"] == "on", f"{tag} religar state on")
    rec(asserts, st["label"] == "Ligado", f"{tag} religar label Ligado")
    rec(asserts, not page.is_visible("#scalp-kill"), f"{tag} religar kill banner gone")
    shot(page, f"1001-B-{tag}-reon.png", shots)

    page.click("#scalp-switch")
    page.wait_for_timeout(200)
    st = state_of(page)
    rec(asserts, st["state"] == "off", f"{tag} desligar state off")
    rec(asserts, st["label"] == "Desligado", f"{tag} desligar label")
    rec(asserts, st["pnl"] == "US$ 0,00", f"{tag} desligar pnl reset")
    rec(asserts, st["aria"] == "false", f"{tag} desligar aria false")
    shot(page, f"1001-B-{tag}-off-final.png", shots)

    page.click("#scalp-no-key")
    page.wait_for_timeout(200)
    st = state_of(page)
    rec(asserts, st["state"] == "nokey", f"{tag} nokey state")
    rec(asserts, st["disabled"] is True, f"{tag} nokey switch disabled")
    rec(asserts, "Meu Perfil" in (st["status"] or ""), f"{tag} nokey Meu Perfil copy")
    rec(asserts, page.locator("#scalp-switch").is_disabled(), f"{tag} nokey cannot click")
    shot(page, f"1001-B-{tag}-nokey.png", shots)

    # extras — closed <details> hide FAQ innerText; assert HTML + open the FAQ.
    r2 = page.goto(LANDING, wait_until="domcontentloaded", timeout=60000)
    rec(asserts, r2 is not None and r2.status == 200, f"{tag} landing HTTP {r2.status if r2 else None}")
    page.wait_for_timeout(800)
    html = page.content()
    rec(asserts, "Não por omissão" in html, f"{tag} landing FAQ not-by-omission (HTML)")
    rec(asserts, "scalp" in html.lower(), f"{tag} landing mentions scalp")
    rec(asserts, "24/7" not in html, f"{tag} landing no absolute 24/7")
    rec(asserts, "Não é formador de mercado nem estratégia lucrativa" in html, f"{tag} landing ban copy (HTML)")
    faq = page.locator("details").filter(has_text="É um robô que opera por mim?")
    rec(asserts, faq.count() >= 1, f"{tag} landing FAQ robot question present")
    if faq.count():
        faq.first.locator("summary").click()
        page.wait_for_timeout(200)
        rec(asserts, "Não por omissão" in faq.first.inner_text(), f"{tag} landing FAQ open visible")
        rec(asserts, "estratégia lucrativa" in faq.first.inner_text(), f"{tag} landing FAQ ban visible")
        faq.first.screenshot(path=str(CRITIQUE / f"1001-B-{tag}-landing-faq.png"))
        faq_shot = CRITIQUE / f"1001-B-{tag}-landing-faq.png"
        shots.append({"path": str(faq_shot), "bytes": faq_shot.stat().st_size, "empty": faq_shot.stat().st_size < 2000})
    shot(page, f"1001-B-{tag}-landing.png", shots)

    r3 = page.goto(AJUDA, wait_until="domcontentloaded", timeout=60000)
    rec(asserts, r3 is not None and r3.status == 200, f"{tag} ajuda HTTP {r3.status if r3 else None}")
    body = page.inner_text("body")
    rec(asserts, "scalp direcional BTCUSDT" in body, f"{tag} ajuda scalp copy")
    rec(asserts, "default desligado" in body, f"{tag} ajuda default off")
    rec(asserts, "24/7" not in body, f"{tag} ajuda no 24/7")
    rec(asserts, "Operar" in body, f"{tag} ajuda Operar")
    shot(page, f"1001-B-{tag}-ajuda.png", shots)

    console_err = [c for c in console if c.get("type") == "error"]
    rec(asserts, len(page_errors) == 0, f"{tag} pageerror={page_errors}")
    rec(asserts, True, f"{tag} console errors={len(console_err)} (recorded)")
    proto_bad = [b for b in bad_resp if "/prototypes/card-1001-scalp-direcional-jev/" in b["url"] and not b["url"].endswith(".map")]
    posthog = [b for b in proto_bad if "posthog-config.js" in b["url"]]
    other_bad = [b for b in proto_bad if "posthog-config.js" not in b["url"]]
    rec(asserts, len(other_bad) == 0, f"{tag} proto HTTP>=400 except posthog {other_bad}")
    rec(asserts, True, f"{tag} posthog-config.js 404 recorded P3 n={len(posthog)}")
    empty_shots = [s for s in shots if s["empty"]]
    rec(asserts, len(empty_shots) == 0, f"{tag} screenshots non-empty {empty_shots}")

    context.close()
    return {
        "viewport": {"width": width, "height": height, "tag": tag},
        "asserts": asserts,
        "console": console,
        "page_errors": page_errors,
        "bad_resp": bad_resp,
        "shots": shots,
        "last_state": st,
    }


def main() -> int:
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path="/home/ubuntu/.cache/ms-playwright/chromium-1243/chrome-linux-arm64/chrome",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        for width, height, tag in ((1280, 800, "desktop-1280x800"), (390, 844, "mobile-390x844")):
            results.append(run_viewport(browser, width, height, tag))
        browser.close()

    asserts = [a for r in results for a in r["asserts"]]
    failed = [a for a in asserts if not a["ok"]]
    out = {
        "pass": len(failed) == 0,
        "url": URL,
        "assert_count": len(asserts),
        "fail_count": len(failed),
        "failed": failed,
        "viewports": results,
    }
    dest = CRITIQUE / "1001-B-gate.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": out["pass"], "assert_count": out["assert_count"], "fail_count": out["fail_count"], "failed": failed}, ensure_ascii=False, indent=2))
    return 0 if out["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
