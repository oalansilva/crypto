#!/usr/bin/env python3
"""
Script de investigação: inspeciona a estrutura da página /lab
para encontrar os seletores corretos
"""

import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://31.97.92.212:5173"

async def inspect_lab_page():
    print("🔍 Inspecionando estrutura da página /lab...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        try:
            await page.goto(f"{BASE_URL}/lab", wait_until="networkidle")
            await asyncio.sleep(2)
            
            print("\n📝 TEXTAREAS:")
            textareas = page.locator('textarea')
            count = await textareas.count()
            print(f"   Total: {count}")
            
            for i in range(count):
                try:
                    placeholder = await textareas.nth(i).get_attribute('placeholder')
                    name = await textareas.nth(i).get_attribute('name')
                    visible = await textareas.nth(i).is_visible()
                    print(f"   [{i}] placeholder='{placeholder}' name='{name}' visible={visible}")
                except Exception as e:
                    print(f"   [{i}] erro: {e}")
            
            print("\n🔘 BUTTONS:")
            buttons = page.locator('button')
            count = await buttons.count()
            print(f"   Total: {count}")
            
            for i in range(min(count, 15)):
                try:
                    text = await buttons.nth(i).inner_text()
                    visible = await buttons.nth(i).is_visible()
                    if visible and text.strip():
                        print(f"   [{i}] '{text.strip()[:50]}' visible={visible}")
                except:
                    pass
            
            print("\n📋 INPUTS:")
            inputs = page.locator('input[type="text"], input[type="checkbox"]')
            count = await inputs.count()
            print(f"   Total: {count}")
            
            for i in range(count):
                try:
                    input_type = await inputs.nth(i).get_attribute('type')
                    placeholder = await inputs.nth(i).get_attribute('placeholder')
                    name = await inputs.nth(i).get_attribute('name')
                    visible = await inputs.nth(i).is_visible()
                    print(f"   [{i}] type={input_type} placeholder='{placeholder}' name='{name}' visible={visible}")
                except Exception as e:
                    print(f"   [{i}] erro: {e}")
            
            # Screenshot
            await page.screenshot(path="/tmp/lab_page_inspection.png", full_page=True)
            print("\n📸 Screenshot salvo: /tmp/lab_page_inspection.png")
            
            # Tentar extrair o HTML relevante
            print("\n📄 HTML do form principal:")
            form_html = await page.locator('form, div[class*="lab"], main').first.inner_html()
            
            # Salvar HTML
            with open('/tmp/lab_page.html', 'w') as f:
                f.write(form_html)
            print("   HTML salvo: /tmp/lab_page.html")
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_lab_page())
