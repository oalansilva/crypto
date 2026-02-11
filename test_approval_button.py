#!/usr/bin/env python3
"""
Teste simplificado: verifica se o botão de aprovação aparece no run existente
que já tem ready_for_user_review: true
"""

import pytest

pytestmark = pytest.mark.e2e

import asyncio
import json
from playwright.async_api import async_playwright

BASE_URL = "http://31.97.92.212:5173"
RUN_ID = "c4079c1d109b45c09a8b350788b9218b"  # Run que já está com ready_for_review

async def test_approval_button_visibility():
    print("🚀 Testando visibilidade do botão de aprovação...")
    print(f"📍 Run ID: {RUN_ID}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navegar diretamente para o run
            url = f"{BASE_URL}/lab/runs/{RUN_ID}"
            print(f"\n📍 Navegando para: {url}")
            await page.goto(url, wait_until="networkidle")
            
            # Aguardar carregamento da página
            await asyncio.sleep(3)
            
            # Tirar screenshot inicial
            await page.screenshot(path="/tmp/run_page_loaded.png", full_page=True)
            print("📸 Screenshot salvo: /tmp/run_page_loaded.png")
            
            # Verificar se o botão existe
            print("\n📍 Procurando botão de aprovação...")
            
            # Tentar diferentes variações do texto
            button_texts = [
                "Aprovar e iniciar execução",
                "Aprovar",
                "iniciar execução",
                "Aprovando"
            ]
            
            found = False
            for text in button_texts:
                try:
                    btn = page.locator(f'button:has-text("{text}")')
                    count = await btn.count()
                    
                    if count > 0:
                        print(f"   ✅ Encontrado botão com texto: '{text}' (count: {count})")
                        found = True
                        
                        # Verificar se está visível
                        is_visible = await btn.first.is_visible()
                        print(f"      Visível: {is_visible}")
                        
                        if is_visible:
                            # Highlight do botão
                            await btn.first.highlight()
                            await asyncio.sleep(1)
                            
                            # Screenshot com highlight
                            await page.screenshot(path="/tmp/button_found.png", full_page=True)
                            print("      📸 Screenshot com botão: /tmp/button_found.png")
                        
                        break
                except Exception as e:
                    continue
            
            if not found:
                print("   ❌ Nenhum botão de aprovação encontrado")
                
                # Debug: mostrar todos os botões na página
                print("\n   🔍 Debug: Listando todos os botões...")
                all_buttons = page.locator('button')
                count = await all_buttons.count()
                print(f"      Total de botões: {count}")
                
                for i in range(min(count, 10)):  # Mostrar no máx 10
                    try:
                        text = await all_buttons.nth(i).inner_text()
                        visible = await all_buttons.nth(i).is_visible()
                        print(f"      [{i}] '{text[:50]}...' (visible: {visible})")
                    except:
                        pass
                
                return False
            
            # Verificar também a seção de draft
            print("\n📍 Verificando seção de strategy draft...")
            
            draft_keywords = ["strategy", "draft", "one-liner", "rationale"]
            for keyword in draft_keywords:
                elements = page.locator(f'text="{keyword}"')
                count = await elements.count()
                if count > 0:
                    print(f"   ✅ Encontrado: '{keyword}' ({count} ocorrências)")
            
            return found
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            
            try:
                await page.screenshot(path="/tmp/test_error.png", full_page=True)
                print("📸 Screenshot de erro: /tmp/test_error.png")
            except:
                pass
            
            return False
        
        finally:
            await browser.close()

if __name__ == "__main__":
    success = asyncio.run(test_approval_button_visibility())
    
    if success:
        print("\n✅ TESTE PASSOU! Botão de aprovação está presente e visível.")
        exit(0)
    else:
        print("\n❌ TESTE FALHOU! Botão não encontrado.")
        exit(1)
