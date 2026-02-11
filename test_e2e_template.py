#!/usr/bin/env python3
"""
TEMPLATE: Teste E2E genérico para funcionalidades do Crypto Lab

Como usar:
1. Copiar este arquivo: cp test_e2e_template.py test_e2e_<feature_name>.py
2. Ajustar as constantes no topo (BASE_URL, API_URL, etc.)
3. Implementar os steps do teste
4. Rodar: ./backend/.venv/bin/python test_e2e_<feature_name>.py

Estrutura padrão:
- STEP 1: Setup/navegação
- STEP 2-N: Interações principais
- STEP N+1: Validação final
- Screenshots salvos em /tmp/ para debug (NÃO enviados pro Telegram)
"""

import pytest

pytestmark = pytest.mark.e2e

import asyncio
import json
import subprocess
from playwright.async_api import async_playwright

# ==================== CONFIGURAÇÃO ====================

BASE_URL = "http://31.97.92.212:5173"
API_URL = "http://localhost:8003/api"

# Nome da feature (usado nos screenshots)
FEATURE_NAME = "example_feature"

# ==================== HELPERS ====================

def api_get(endpoint: str):
    """Helper para fazer GET na API local"""
    result = subprocess.run(
        ["curl", "-s", f"{API_URL}{endpoint}"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return None
    return None

async def wait_for_api_state(run_id: str, field_path: str, expected_value, max_wait: int = 40):
    """
    Aguarda um campo da API ter um valor esperado.
    
    Args:
        run_id: ID do run
        field_path: Caminho do campo (ex: "upstream.ready_for_user_review")
        expected_value: Valor esperado (ex: True)
        max_wait: Tempo máximo de espera em segundos
    
    Returns:
        bool: True se atingiu o valor esperado, False se timeout
    """
    for i in range(max_wait):
        await asyncio.sleep(1)
        
        data = api_get(f"/lab/runs/{run_id}")
        if not data:
            continue
        
        # Navegar pelo field_path (ex: "upstream.ready_for_user_review")
        current = data
        for key in field_path.split('.'):
            current = current.get(key, {})
            if current == {}:
                break
        
        if current == expected_value:
            print(f"   ✅ Campo '{field_path}' = {expected_value} (após {i+1}s)")
            return True
        
        if (i + 1) % 10 == 0:
            print(f"   ⏳ Aguardando {field_path}={expected_value}... ({i+1}/{max_wait}s)")
    
    print(f"   ❌ TIMEOUT: {field_path} não atingiu {expected_value} em {max_wait}s")
    return False

# ==================== TESTE PRINCIPAL ====================

async def test_feature():
    """
    Teste E2E principal.
    
    Retorna:
        bool: True se todos os steps passaram, False caso contrário
    """
    print(f"🚀 Teste E2E: {FEATURE_NAME}")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        try:
            # ==================== STEP 1: Setup ====================
            print("\n📍 STEP 1: Navegando para a página inicial...")
            
            await page.goto(f"{BASE_URL}/lab", wait_until="networkidle")
            await page.screenshot(path=f"/tmp/{FEATURE_NAME}_step1_home.png")
            print("   ✅ Página carregada")
            print(f"   📸 Screenshot: /tmp/{FEATURE_NAME}_step1_home.png")
            
            # ==================== STEP 2: Interação principal ====================
            print("\n📍 STEP 2: <Descreva a ação principal>...")
            
            # Exemplo: preencher um campo
            # input_field = page.locator('textarea[placeholder*="..."]')
            # await input_field.fill("texto de teste")
            # print("   ✅ Campo preenchido")
            
            # Exemplo: clicar em botão
            # button = page.locator('button:has-text("Confirmar")')
            # await button.click()
            # print("   ✅ Botão clicado")
            
            await page.screenshot(path=f"/tmp/{FEATURE_NAME}_step2_action.png")
            print(f"   📸 Screenshot: /tmp/{FEATURE_NAME}_step2_action.png")
            
            # ==================== STEP 3: Aguardar resultado ====================
            print("\n📍 STEP 3: Aguardando processamento...")
            
            # Exemplo: aguardar estado na API
            # run_id = "..."  # extrair do contexto
            # success = await wait_for_api_state(run_id, "status", "completed", max_wait=30)
            # if not success:
            #     return False
            
            await asyncio.sleep(2)  # Placeholder
            await page.screenshot(path=f"/tmp/{FEATURE_NAME}_step3_result.png")
            print(f"   📸 Screenshot: /tmp/{FEATURE_NAME}_step3_result.png")
            
            # ==================== STEP 4: Validação final ====================
            print("\n📍 STEP 4: Validando resultado...")
            
            # Exemplo: verificar elemento na UI
            # success_msg = page.locator('text="Sucesso"')
            # is_visible = await success_msg.is_visible()
            # if not is_visible:
            #     print("   ❌ Mensagem de sucesso não encontrada")
            #     return False
            
            # Exemplo: verificar via API
            # data = api_get("/endpoint")
            # if data.get("status") != "ok":
            #     print(f"   ❌ Status inesperado: {data.get('status')}")
            #     return False
            
            print("   ✅ Validação passou")
            
            # ==================== SUCESSO ====================
            print("\n✅ TESTE PASSOU!")
            print("   ✓ Todos os steps completados com sucesso")
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            
            try:
                await page.screenshot(path=f"/tmp/{FEATURE_NAME}_error.png", full_page=True)
                print(f"📸 Screenshot de erro: /tmp/{FEATURE_NAME}_error.png")
            except:
                pass
            
            import traceback
            traceback.print_exc()
            
            return False
        
        finally:
            await browser.close()

# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    print("\n")
    success = asyncio.run(test_feature())
    
    print("\n" + "=" * 60)
    if success:
        print(f"✅ TESTE {FEATURE_NAME.upper()} PASSOU!")
        print("\n📸 Screenshots gerados em /tmp/")
        exit(0)
    else:
        print(f"❌ TESTE {FEATURE_NAME.upper()} FALHOU")
        print("\n📸 Verifique os screenshots em /tmp/ para debug")
        exit(1)
