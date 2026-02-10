#!/usr/bin/env python3
"""
Teste visual simples: tira screenshot da página de um run
para verificar se a UI está funcionando
"""

import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://31.97.92.212:5173"

async def screenshot_lab_page():
    print("📸 Tirando screenshots da UI do Lab...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        try:
            # Screenshot 1: Página principal do Lab
            print("\n1️⃣ Navegando para /lab...")
            await page.goto(f"{BASE_URL}/lab", wait_until="networkidle")
            await page.screenshot(path="/tmp/lab_home.png", full_page=True)
            print("   ✅ Screenshot salvo: /tmp/lab_home.png")
            
            # Screenshot 2: Lista de runs
            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/lab_runs_list.png", full_page=True)
            print("   ✅ Screenshot salvo: /tmp/lab_runs_list.png")
            
            # Verificar se há runs na lista
            run_links = page.locator('a[href*="/lab/runs/"]')
            count = await run_links.count()
            print(f"   📊 Runs encontrados: {count}")
            
            if count > 0:
                # Clicar no primeiro run
                print("\n2️⃣ Abrindo primeiro run...")
                await run_links.first.click()
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                # Screenshot da página do run
                await page.screenshot(path="/tmp/lab_run_detail.png", full_page=True)
                print("   ✅ Screenshot salvo: /tmp/lab_run_detail.png")
                
                # Informações do run
                url = page.url
                run_id = url.split("/runs/")[-1] if "/runs/" in url else "unknown"
                print(f"   📍 Run ID: {run_id}")
                
                # Procurar botões relevantes
                print("\n3️⃣ Procurando elementos na página...")
                
                keywords = [
                    "Aprovar",
                    "executar",
                    "Trader",
                    "estratégia",
                    "upstream"
                ]
                
                for keyword in keywords:
                    elements = page.locator(f'text={keyword}i')
                    count = await elements.count()
                    if count > 0:
                        print(f"   ✅ '{keyword}': {count} ocorrência(s)")
            
            print("\n✅ Screenshots capturados com sucesso!")
            print("📂 Arquivos em /tmp/:")
            print("   - lab_home.png")
            print("   - lab_runs_list.png")
            print("   - lab_run_detail.png")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            return False
        
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(screenshot_lab_page())
    exit(0 if success else 1)
