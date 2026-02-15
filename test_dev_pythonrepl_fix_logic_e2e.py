#!/usr/bin/env python3
"""
Teste E2E mínimo para validar fluxo Lab após ajustes de lógica.
"""

import asyncio
import json
import subprocess

from playwright.async_api import async_playwright

BASE_URL = "http://31.97.92.212:5173"
API_URL = "http://localhost:8003/api"


async def test_dev_pythonrepl_fix_logic_flow():
    print("🚀 Teste E2E: Dev PythonREPL Logic Fix (fluxo mínimo)")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            print("\n📍 STEP 1: Abrindo /lab...")
            await page.goto(f"{BASE_URL}/lab", wait_until="networkidle")
            await page.screenshot(path="/tmp/step1_dev_pythonrepl_lab.png")
            print("   ✅ Página carregada")

            print("\n📍 STEP 2: Criando run...")
            textarea = page.locator('textarea[placeholder*="Ex.: Quero rodar"]')
            await textarea.fill("quero uma estrategia em BTC/USDT 1h")
            run_btn = page.locator('button:has-text("Run Lab")')
            await run_btn.click()

            await page.wait_for_url("**/lab/runs/**", timeout=15000)
            run_url = page.url
            run_id = run_url.split("/runs/")[-1]
            await page.screenshot(path="/tmp/step2_dev_pythonrepl_run.png", full_page=True)
            print(f"   ✅ Run criado: {run_id}")

            print("\n📍 STEP 3: Verificando run via API...")
            await asyncio.sleep(3)
            result = subprocess.run(["curl", "-s", f"{API_URL}/lab/runs/{run_id}"], capture_output=True, text=True)
            if result.returncode != 0:
                print("   ❌ Falha ao consultar run")
                return False
            data = json.loads(result.stdout or "{}")
            if not data.get("run_id"):
                print("   ❌ Run inválido")
                return False

            print("   ✅ Run consultado via API")
            await page.screenshot(path="/tmp/step3_dev_pythonrepl_api.png", full_page=True)
            return True
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    ok = asyncio.run(test_dev_pythonrepl_fix_logic_flow())
    raise SystemExit(0 if ok else 1)
