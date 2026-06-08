import assert from 'node:assert/strict'
import fs from 'node:fs'
import test from 'node:test'
import vm from 'node:vm'

const landingHtml = fs.readFileSync(new URL('../public/prototypes/cripto-farol-landing/index.html', import.meta.url), 'utf8')
const script = landingHtml.match(/<script>\n([\s\S]*)\n\s*<\/script>\s*<\/body>/)?.[1]

assert.ok(script, 'landing inline script should be extractable')

function makeElement(tagName = 'div') {
  const listeners = new Map()
  return {
    tagName,
    textContent: '',
    className: '',
    disabled: false,
    value: '',
    async: false,
    crossOrigin: '',
    src: '',
    type: '',
    parentNode: {
      insertBefore() {},
    },
    addEventListener(eventName, handler) {
      listeners.set(eventName, handler)
    },
    dispatch(eventName, event = {}) {
      return listeners.get(eventName)?.(event)
    },
    querySelector(selector) {
      if (selector === "button[type='submit']") return submitButton
      return null
    },
  }
}

const submitButton = makeElement('button')

function createHarness({ posthogConfig = undefined, fetchOk = true, fetchRejectMessage = undefined } = {}) {
  const storage = new Map()
  const captures = []
  const insertedScripts = []
  const form = makeElement('form')
  const message = makeElement('p')

  form.elements = {
    name: { value: 'Alan' },
    email: { value: 'alan@example.com' },
    profile: { value: 'Iniciante' },
    pain: { value: 'texto livre que não deve ir ao PostHog' },
  }
  form.reset = () => {}

  const document = {
    referrer: 'https://instagram.com/path?token=secret#frag',
    createElement(tagName) {
      const element = makeElement(tagName)
      insertedScripts.push(element)
      return element
    },
    getElementsByTagName() {
      return [
        {
          parentNode: {
            insertBefore(element) {
              insertedScripts.push(element)
            },
          },
        },
      ]
    },
    querySelector(selector) {
      if (selector === '[data-lead-form]') return form
      if (selector === '[data-form-message]') return message
      return null
    },
  }

  const window = {
    location: {
      href: 'https://dev.criptofarol.com.br/prototypes/cripto-farol-landing/?utm_source=instagram&utm_medium=social&utm_campaign=beta&token=secret',
      protocol: 'https:',
      hostname: 'dev.criptofarol.com.br',
      pathname: '/prototypes/cripto-farol-landing/',
    },
    localStorage: {
      getItem(key) {
        return storage.get(key) ?? null
      },
      setItem(key, value) {
        storage.set(key, value)
      },
    },
    CRIPTOFAROL_POSTHOG: posthogConfig,
  }

  const context = {
    URL,
    URLSearchParams,
    FormData: class FakeFormData {
      constructor(targetForm) {
        this.targetForm = targetForm
      }
      get(name) {
        return this.targetForm.elements[name]?.value ?? null
      }
    },
    Error,
    Array,
    Object,
    String,
    Promise,
    document,
    window,
    fetch: async () => {
      if (fetchRejectMessage) throw new Error(fetchRejectMessage)
      return { ok: fetchOk }
    },
    console,
  }
  context.globalThis = context

  vm.runInNewContext(script, context)

  if (Array.isArray(window.posthog)) {
    for (const queuedCall of window.posthog) {
      if (queuedCall[0] === 'capture') {
        captures.push({ eventName: queuedCall[1], properties: queuedCall[2] ?? {} })
      }
    }
  }

  if (window.posthog?.capture) {
    const originalCapture = window.posthog.capture
    window.posthog.capture = (eventName, properties = {}) => {
      captures.push({ eventName, properties })
      return originalCapture.call(window.posthog, eventName, properties)
    }
  }

  return { captures, form, insertedScripts, window }
}

test('legacy landing keeps PostHog disabled when runtime config has no key', () => {
  const { window, insertedScripts } = createHarness()

  assert.equal(window.posthog, undefined)
  assert.equal(insertedScripts.length, 0)
})

test('legacy landing captures safe funnel events without PII when PostHog is configured', async () => {
  const { captures, form, insertedScripts } = createHarness({
    posthogConfig: { key: 'ph_test_key', host: 'https://eu.i.posthog.com' },
  })

  await form.dispatch('submit', { preventDefault() {} })

  assert.deepEqual(
    captures.map((capture) => capture.eventName),
    ['landing_pageview', 'lead_form_submit_started', 'lead_form_submit_accepted'],
  )

  for (const capture of captures) {
    assert.equal(capture.properties.email, undefined)
    assert.equal(capture.properties.name, undefined)
    assert.equal(capture.properties.whatsapp, undefined)
    assert.equal(capture.properties.profile, undefined)
    assert.equal(capture.properties.pain, undefined)
    assert.equal(capture.properties.utm_source, 'instagram')
    assert.equal(capture.properties.referrer, undefined)
    assert.equal(capture.properties.referrer_domain, 'instagram.com')
    assert.equal(capture.properties.landing_path, '/prototypes/cripto-farol-landing/?utm_source=instagram&utm_medium=social&utm_campaign=beta')
  }

  assert.ok(insertedScripts.some((scriptEl) => scriptEl.src === 'https://eu-assets.i.posthog.com/static/array.js'))
})

test('legacy landing captures submit failure event without PII', async () => {
  const { captures, form } = createHarness({
    posthogConfig: { key: 'ph_test_key' },
    fetchOk: false,
  })

  await form.dispatch('submit', { preventDefault() {} })

  assert.equal(captures.at(-1).eventName, 'lead_form_submit_failed')
  assert.equal(captures.at(-1).properties.failure, 'submit_failed')
  assert.equal(captures.at(-1).properties.email, undefined)
})

test('legacy landing bounds unexpected submit failure reason before analytics capture', async () => {
  const sensitiveMessage = 'https://example.com/reset/SECRET_TOKEN?email=alan@example.com'
  const { captures, form } = createHarness({
    posthogConfig: { key: 'ph_test_key' },
    fetchRejectMessage: sensitiveMessage,
  })

  await form.dispatch('submit', { preventDefault() {} })

  assert.equal(captures.at(-1).eventName, 'lead_form_submit_failed')
  assert.equal(captures.at(-1).properties.failure, 'network_or_runtime_error')
  assert.notEqual(captures.at(-1).properties.failure, sensitiveMessage)
})
