import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const viewerPath = path.resolve(__dirname, '../src/components/BackendLogViewer.tsx')

test('BackendLogViewer abre sessão vazia com cursor e faz polling incremental', async () => {
  const source = await readFile(viewerPath, 'utf8')

  // Base request single-flight cujo conteúdo é descartado (com Bearer via authFetch).
  assert.match(source, /from ['"]\.\.\/lib\/authFetch['"]/)
  assert.match(source, /await authFetch\(url\(undefined, undefined\)/)
  // Polls autenticados enviam after_offset e file_id.
  assert.match(source, /authFetch\(target/)
  assert.match(source, /url\(cursor\.nextOffset, cursor\.fileId\)/)
  assert.match(source, /after_offset/)
  assert.match(source, /file_id/)
  // Estado de espera.
  assert.match(source, /Aguardando eventos/)
  // Descarte de respostas obsoletas por sessão.
  assert.match(source, /session !== sessionRef\.current/)
  // Cancelamento no unmount.
  assert.match(source, /abortRef\.current\?\.abort\(\)/)
  // Limpeza de cursor/conteúdo ao abrir.
  assert.match(source, /cursorRef\.current = null/)
  assert.match(source, /setContent\(''\)/)
})

test('BackendLogViewer trata cursor_reset reiniciando a sessão sem erro permanente', async () => {
  const source = await readFile(viewerPath, 'utf8')
  assert.match(source, /data\.cursorReset/)
  assert.match(source, /startSession\(session\)/)
  assert.match(source, /setWaiting\(true\)/)
})

test('BackendLogViewer implementa autoscroll com pausa manual e retomada', async () => {
  const source = await readFile(viewerPath, 'utf8')
  assert.match(source, /SCROLL_THRESHOLD_PX = 24/)
  assert.match(source, /atBottomRef\.current/)
  assert.match(source, /Rolagem automática/)
  assert.match(source, /Rolagem pausada/)
  assert.match(source, /Ir para o fim/)
  assert.match(source, /requestAnimationFrame/)
})

test('BackendLogViewer preserva fechamento e acessibilidade do modal', async () => {
  const source = await readFile(viewerPath, 'utf8')
  assert.match(source, /e\.key === 'Escape'/)
  assert.match(source, /aria-modal="true"/)
  assert.match(source, /role="dialog"/)
  assert.match(source, /tabIndex=\{-1\}/)
  assert.match(source, /restore\?\.focus\(\)/)
  assert.match(source, /document\.body\.style\.overflow = 'hidden'/)
  assert.match(source, /pollInFlightRef\.current/)
})

test('BackendLogViewer mapeia 401/403 no banner existente com copy observável', async () => {
  const source = await readFile(viewerPath, 'utf8')
  assert.match(source, /authFetch/)
  assert.match(source, /HTTP 401 — faça login para ver logs/)
  assert.match(source, /HTTP 403 — apenas admin pode ver logs/)
  assert.match(source, /tailHttpErrorMessage/)
  // Banner amber existente — sem redesenho.
  assert.match(source, /text-amber-400/)
  assert.match(source, /\{error\}/)
})

test('BackendLogViewer para o poll após 401/403 terminal sem limpar o banner a cada tick', async () => {
  const source = await readFile(viewerPath, 'utf8')
  assert.match(source, /isTerminalAuthStatus/)
  assert.match(source, /stopPolling/)
  assert.match(source, /!stopPolling && openRef\.current/)
  // Não limpa erro no início do tick (evita banner piscando).
  assert.doesNotMatch(source, /pollInFlightRef\.current = true\n\s+const controller[\s\S]*?setError\(null\)\n\s+try/)
})
