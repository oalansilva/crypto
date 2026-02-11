#!/usr/bin/env python3
"""
Teste E2E corrigido: cria run, conversa com Trader, aprova upstream
"""

import pytest

pytestmark = pytest.mark.e2e

import asyncio
import json
import subprocess
from playwright.async_api import async_playwright

BASE_URL = "http://31.97.92.212:5173"
API_URL = "http://localhost:8003/api"

async def test_upstream_approval_flow():
    print("🚀 Teste E2E: Upstream Approval Flow")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        try:
            # STEP 1: Navegar para /lab
            print("\n📍 STEP 1: Navegando para /lab...")
            await page.goto(f"{BASE_URL}/lab", wait_until="networkidle")
            await page.screenshot(path="/tmp/step1_lab_home.png")
            print("   ✅ Página carregada")
            print("   📸 Screenshot: /tmp/step1_lab_home.png")
            
            # STEP 2: Preencher mensagem e criar run
            print("\n📍 STEP 2: Criando novo run...")
            
            # Encontrar o textarea correto (pelo placeholder)
            textarea = page.locator('textarea[placeholder*="Ex.: Quero rodar"]')
            await textarea.fill("quero uma estrategia em ETH")
            print("   ✅ Mensagem preenchida: 'quero uma estrategia em ETH'")
            
            # Clicar em "Run Lab"
            run_btn = page.locator('button:has-text("Run Lab")')
            await run_btn.click()
            print("   ✅ Botão 'Run Lab' clicado")
            
            # Aguardar navegação para página do run
            await page.wait_for_url("**/lab/runs/**", timeout=15000)
            run_url = page.url
            run_id = run_url.split("/runs/")[-1]
            
            print(f"   ✅ Run criado!")
            print(f"      URL: {run_url}")
            print(f"      Run ID: {run_id}")
            
            await page.screenshot(path="/tmp/step2_run_created.png", full_page=True)
            print("   📸 Screenshot: /tmp/step2_run_created.png")
            
            # STEP 3: Aguardar primeira pergunta do Trader e responder
            print("\n📍 STEP 3: Conversando com Trader...")
            
            # Aguardar campo de mensagem aparecer
            await asyncio.sleep(5)
            
            # Procurar campo de input para mensagem upstream
            message_input = page.locator('textarea').first
            await message_input.wait_for(state="visible", timeout=15000)
            print("   ✅ Campo de mensagem encontrado")
            
            # Primeira resposta
            await message_input.fill("ETH/USDT qual timeframe tu considera o melhor?")
            
            # Procurar botão de enviar
            send_btn = page.locator('button:has-text("Enviar")').first
            await send_btn.click()
            print("   ✅ Enviado: 'ETH/USDT qual timeframe tu considera o melhor?'")
            
            # Aguardar resposta do Trader
            await asyncio.sleep(10)
            await page.screenshot(path="/tmp/step3_first_response.png", full_page=True)
            print("   📸 Screenshot: /tmp/step3_first_response.png")
            
            # Segunda resposta (timeframe)
            await message_input.fill("siga com 4H")
            await send_btn.click()
            print("   ✅ Enviado: 'siga com 4H'")
            
            # STEP 4: Aguardar strategy_draft
            print("\n📍 STEP 4: Aguardando strategy_draft...")
            
            max_wait = 40
            ready = False
            
            for i in range(max_wait):
                await asyncio.sleep(1)
                
                # Verificar via API
                result = subprocess.run(
                    ["curl", "-s", f"{API_URL}/lab/runs/{run_id}"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout)
                        ready_for_review = data.get("upstream", {}).get("ready_for_user_review", False)
                        
                        if ready_for_review:
                            ready = True
                            print(f"   ✅ Strategy draft pronto! (após {i+1}s)")
                            break
                    except:
                        pass
                
                if (i + 1) % 10 == 0:
                    print(f"   ⏳ Aguardando... ({i+1}/{max_wait}s)")
            
            if not ready:
                print(f"   ❌ TIMEOUT: draft não ficou pronto em {max_wait}s")
                await page.screenshot(path="/tmp/step4_timeout.png", full_page=True)
                return False
            
            # Recarregar página
            await page.reload(wait_until="networkidle")
            await asyncio.sleep(2)
            await page.screenshot(path="/tmp/step4_draft_ready.png", full_page=True)
            print("   📸 Screenshot: /tmp/step4_draft_ready.png")
            
            # STEP 5: Verificar botão de aprovação
            print("\n📍 STEP 5: Verificando botão de aprovação...")
            
            # Procurar botão
            approve_btn = page.locator('button:has-text("Aprovar")')
            count = await approve_btn.count()
            
            if count == 0:
                print("   ❌ Botão 'Aprovar' não encontrado")
                
                # Debug: listar todos os botões
                print("\n   🔍 DEBUG: Botões visíveis na página:")
                all_btns = page.locator('button:visible')
                btn_count = await all_btns.count()
                
                for i in range(min(btn_count, 10)):
                    try:
                        text = await all_btns.nth(i).inner_text()
                        print(f"      - '{text[:60]}'")
                    except:
                        pass
                
                return False
            
            print(f"   ✅ Botão encontrado! ({count} ocorrência(s))")
            
            # Verificar visibilidade
            is_visible = await approve_btn.first.is_visible()
            print(f"      Visível: {is_visible}")
            
            if not is_visible:
                print("   ❌ Botão não está visível")
                return False
            
            # STEP 6: Clicar em aprovar
            print("\n📍 STEP 6: Clicando em 'Aprovar'...")
            await approve_btn.first.click()
            print("   ✅ Botão clicado")
            
            # Aguardar processamento
            await asyncio.sleep(5)
            await page.screenshot(path="/tmp/step6_approved.png", full_page=True)
            print("   📸 Screenshot: /tmp/step6_approved.png")
            
            # STEP 7: Verificar progressão
            print("\n📍 STEP 7: Verificando progressão...")
            
            result = subprocess.run(
                ["curl", "-s", f"{API_URL}/lab/runs/{run_id}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                phase = data.get("phase", "")
                status = data.get("status", "")
                user_approved = data.get("upstream", {}).get("user_approved", False)
                
                print(f"\n   📊 Estado final:")
                print(f"      phase: {phase}")
                print(f"      status: {status}")
                print(f"      user_approved: {user_approved}")
                
                if user_approved and phase in ["execution", "trader_validation", "decision"]:
                    print("\n✅ TESTE PASSOU!")
                    print("   ✓ Upstream aprovado")
                    print("   ✓ Run progrediu para fase de execução")
                    return True
                else:
                    print("\n⚠️ TESTE INCOMPLETO")
                    print(f"   Esperado: user_approved=true e phase=execution")
                    print(f"   Obtido: user_approved={user_approved}, phase={phase}")
                    return False
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            
            try:
                await page.screenshot(path="/tmp/error.png", full_page=True)
                print("📸 Screenshot de erro: /tmp/error.png")
            except:
                pass
            
            import traceback
            traceback.print_exc()
            
            return False
        
        finally:
            await browser.close()

if __name__ == "__main__":
    print("\n")
    success = asyncio.run(test_upstream_approval_flow())
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("\n📸 Screenshots gerados:")
        print("   - /tmp/step1_lab_home.png")
        print("   - /tmp/step2_run_created.png")
        print("   - /tmp/step3_first_response.png")
        print("   - /tmp/step4_draft_ready.png")
        print("   - /tmp/step6_approved.png")
        exit(0)
    else:
        print("❌ TESTE FALHOU")
        print("\n📸 Verifique os screenshots para debug")
        exit(1)
