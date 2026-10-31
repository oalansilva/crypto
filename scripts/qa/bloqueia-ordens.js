// Trava do navegador do teste no DEV (#1144, D11). Entra por `--init-script`, antes do código da página.
// Recusa com 403 local o envio de ordem à Binance, o stop e as escritas em usuários. A prévia continua
// testável. É barreira cooperativa só neste navegador: não muda o produto e não vale fora dele.
(() => {
  const CORPO = JSON.stringify({ detail: 'bloqueado pela trava do teste no DEV' })

  const caminho = (url) => {
    const texto = new URL(String(url), window.location.href).pathname
    const decodificado = texto.split('/').map((segmento) => decodeURIComponent(segmento)).join('/')
    return decodificado.replace(/\/{2,}/g, '/').replace(/\/+$/, '')
  }

  const bloqueado = (metodo, url) => {
    const verbo = String(metodo || 'GET').toUpperCase()
    let rota
    try {
      rota = caminho(url)
    } catch {
      return verbo === 'POST' || verbo === 'DELETE' // rota ilegível não passa como inofensiva
    }
    if (rota === '/api/monitor/spot-market-orders') return verbo === 'POST'
    if (rota === '/api/monitor/spot-stop-order') return verbo === 'POST' || verbo === 'DELETE'
    if (rota === '/api/admin/users' || rota.startsWith('/api/admin/users/')) {
      return verbo === 'POST' || verbo === 'PUT' || verbo === 'DELETE' || verbo === 'PATCH'
    }
    return false
  }

  const fetchOriginal = window.fetch
  if (typeof fetchOriginal === 'function') {
    window.fetch = function fetchComTrava(entrada, opcoes) {
      const metodo = (opcoes && opcoes.method) || (entrada && entrada.method) || 'GET'
      const url = entrada && typeof entrada === 'object' && 'url' in entrada ? entrada.url : entrada
      if (bloqueado(metodo, url)) {
        return Promise.resolve(new Response(CORPO, { status: 403, headers: { 'Content-Type': 'application/json' } }))
      }
      return fetchOriginal.call(this, entrada, opcoes)
    }
  }

  const prototipo = window.XMLHttpRequest && window.XMLHttpRequest.prototype
  if (prototipo) {
    const abrir = prototipo.open
    const enviar = prototipo.send
    prototipo.open = function abrirComTrava(metodo, url, ...resto) {
      this.__travaOrdem = bloqueado(metodo, url)
      return abrir.call(this, metodo, url, ...resto)
    }
    prototipo.send = function enviarComTrava(...args) {
      if (!this.__travaOrdem) return enviar.apply(this, args)
      const resposta = { readyState: 4, status: 403, statusText: 'Forbidden', responseText: CORPO, response: CORPO }
      for (const [nome, value] of Object.entries(resposta)) {
        Object.defineProperty(this, nome, { configurable: true, value })
      }
      this.getAllResponseHeaders = () => 'content-type: application/json\r\n'
      setTimeout(() => {
        for (const evento of ['readystatechange', 'load', 'loadend']) this.dispatchEvent(new Event(evento))
      }, 0)
      return undefined
    }
  }
})()
