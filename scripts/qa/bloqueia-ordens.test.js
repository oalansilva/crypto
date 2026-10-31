// Trava de ordem real: `node --test`. Página simulada; nada sai deste processo.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const test = require('node:test')
const vm = require('node:vm')

const codigo = fs.readFileSync(path.join(__dirname, 'bloqueia-ordens.js'), 'utf8')

function pagina() {
  const redeFetch = []
  const redeXhr = []

  class Xhr extends EventTarget {
    open(metodo, url) {
      this.metodo = metodo
      this.url = url
    }

    send() {
      redeXhr.push(`${this.metodo} ${this.url}`)
    }
  }

  const janela = {
    location: { href: 'https://dev.exemplo.test/monitor' },
    fetch: async (entrada, opcoes) => {
      redeFetch.push(`${(opcoes && opcoes.method) || (entrada && entrada.method) || 'GET'} ${(entrada && entrada.url) || entrada}`)
      return new Response('{}', { status: 200 })
    },
    XMLHttpRequest: Xhr,
  }
  vm.runInNewContext(codigo, { window: janela, URL, Response, Promise, Event, Object, JSON, String, setTimeout })
  return { janela, redeFetch, redeXhr }
}

const BLOQUEADOS = [
  ['POST', '/api/monitor/spot-market-orders'],
  ['post', '/api/monitor/spot-market-orders/'],
  ['POST', 'https://dev.exemplo.test/api/monitor/spot-market-orders'],
  ['POST', '//dev.exemplo.test/api//monitor/spot-market-orders'],
  ['POST', '/api/monitor/spot-market-orders?x=1'],
  ['POST', '/api/monitor/spot-stop-order'],
  ['DELETE', '/api/monitor/spot-stop-order'],
  ['POST', '/api/admin/users'],
  ['PUT', '/api/admin/users/42'],
  ['DELETE', '/api/admin/users/42'],
  ['POST', '/api/admin/users/42/suspend'],
  ['POST', '/api/admin/users/42/ban'],
  ['POST', '/api/admin/users/42/reactivate'],
  ['POST', '/api/monitor/spot%2Dmarket-orders'],
  ['POST', '/api/monitor/%73pot-market-orders'],
  ['POST', '/api/monitor%2Fspot-market-orders'],
  ['POST', '/api/monitor/spot-market-orders%2F'],
  ['DELETE', '/api/monitor/spot%2Dstop-order'],
  ['POST', '/api/admin/%75sers'],
  ['PUT', '/api/admin/users%2F42'],
  ['POST', '/api/monitor/spot-market-orders%'],
  ['DELETE', '/api/monitor/spot%ZZstop-order'],
]

const LIBERADOS = [
  ['POST', '/api/monitor/spot-market-orders/preview'],
  ['POST', '/api/monitor/spot-market-orders/eligibility'],
  ['GET', '/api/monitor/spot-market-orders/eligibility'],
  ['GET', '/api/monitor/spot-stop-order'],
  ['GET', '/api/admin/users'],
  ['GET', '/api/admin/users/42'],
  ['POST', '/api/admin/users-export'],
  ['POST', '/api/favorites'],
  ['DELETE', '/api/favorites/1'],
  ['POST', '/api/monitor/spot%2Dmarket-orders/preview'],
  ['GET', '/api/monitor/spot%2Dmarket-orders'],
  ['GET', '/api/monitor/spot-market-orders%'],
]

for (const [metodo, url] of BLOQUEADOS) {
  test(`fetch recusa ${metodo} ${url}`, async () => {
    const { janela, redeFetch } = pagina()
    const resposta = await janela.fetch(url, { method: metodo })
    assert.equal(resposta.status, 403)
    assert.match(await resposta.text(), /trava do teste/)
    assert.deepEqual(redeFetch, [])
  })

  test(`XMLHttpRequest recusa ${metodo} ${url}`, async () => {
    const { janela, redeXhr } = pagina()
    const xhr = new janela.XMLHttpRequest()
    const eventos = []
    for (const nome of ['readystatechange', 'load', 'loadend']) xhr.addEventListener(nome, () => eventos.push(nome))
    xhr.open(metodo, url)
    xhr.send('{}')
    await new Promise((pronto) => setTimeout(pronto, 5))
    assert.deepEqual(redeXhr, [])
    assert.equal(xhr.status, 403)
    assert.equal(xhr.readyState, 4)
    assert.match(xhr.responseText, /trava do teste/)
    assert.match(xhr.getAllResponseHeaders(), /content-type/)
    assert.deepEqual(eventos, ['readystatechange', 'load', 'loadend'])
  })
}

for (const [metodo, url] of LIBERADOS) {
  test(`fetch deixa passar ${metodo} ${url}`, async () => {
    const { janela, redeFetch } = pagina()
    const resposta = await janela.fetch(url, { method: metodo })
    assert.equal(resposta.status, 200)
    assert.equal(redeFetch.length, 1)
  })

  test(`XMLHttpRequest deixa passar ${metodo} ${url}`, () => {
    const { janela, redeXhr } = pagina()
    const xhr = new janela.XMLHttpRequest()
    xhr.open(metodo, url)
    xhr.send()
    assert.equal(redeXhr.length, 1)
  })
}

test('fetch com Request lê método e URL do objeto', async () => {
  const { janela, redeFetch } = pagina()
  const pedido = { url: 'https://dev.exemplo.test/api/monitor/spot-market-orders', method: 'POST' }
  assert.equal((await janela.fetch(pedido)).status, 403)
  assert.deepEqual(redeFetch, [])
})

test('fetch sem método é GET', async () => {
  const { janela, redeFetch } = pagina()
  await janela.fetch('/api/monitor/spot-market-orders')
  assert.equal(redeFetch.length, 1)
})

test('XMLHttpRequest reusado volta a passar depois de um envio recusado', () => {
  const { janela, redeXhr } = pagina()
  const xhr = new janela.XMLHttpRequest()
  xhr.open('POST', '/api/monitor/spot-market-orders')
  xhr.send()
  xhr.open('GET', '/api/monitor')
  xhr.send()
  assert.deepEqual(redeXhr, ['GET /api/monitor'])
})

test('URL inválida não quebra a página', async () => {
  const { janela, redeFetch } = pagina()
  await janela.fetch('http://[')
  assert.equal(redeFetch.length, 1)
})
