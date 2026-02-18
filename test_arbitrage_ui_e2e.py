#!/usr/bin/env python3
import asyncio

from playwright.async_api import async_playwright

BASE_URL = "http://31.97.92.212:5173"
FEATURE_NAME = "arbitrage_ui"


async def test_feature():
    print(f"🚀 Teste E2E: {FEATURE_NAME}")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            print("\n📍 STEP 1: Navegando para /arbitrage...")
            await page.goto(f"{BASE_URL}/arbitrage", wait_until="domcontentloaded")
            await page.screenshot(path=f"/tmp/{FEATURE_NAME}_step1_page.png")

            print("\n📍 STEP 2: Validando campos e tabela...")
            await page.locator('input[placeholder="USDT/USDC"]').wait_for(state="visible", timeout=15000)
            await page.locator('table').wait_for(state="visible", timeout=15000)
            await page.screenshot(path=f"/tmp/{FEATURE_NAME}_step2_table.png")

            print("\n✅ TESTE PASSOU!")
            return True
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            try:
                await page.screenshot(path=f"/tmp/{FEATURE_NAME}_error.png", full_page=True)
            except Exception:
                pass
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    success = asyncio.run(test_feature())
    print("\n" + "=" * 60)
    if success:
        print(f"✅ TESTE {FEATURE_NAME.upper()} PASSOU!")
        exit(0)
    print(f"❌ TESTE {FEATURE_NAME.upper()} FALHOU")
    exit(1)
