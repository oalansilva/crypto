import { expect, test } from '@playwright/test'

test('desktop drop into non-empty column persists and mobile long-press opens move sheet', async ({ page }) => {
  const changes = [
    {
      id: 'pending-card',
      title: 'Pending card',
      description: 'Starts in pending',
      path: 'openspec/changes/pending-card/proposal',
      status: {
        PO: 'pending',
        DESIGN: 'pending',
        'Alan approval': 'pending',
        DEV: 'pending',
        QA: 'pending',
        'Homologation': 'pending',
      },
      archived: false,
      column: 'Pending',
    },
    {
      id: 'approved-card',
      title: 'Approved card',
      description: 'Ready for DEV',
      path: 'openspec/changes/approved-card/proposal',
      status: {
        PO: 'approved',
        DESIGN: 'approved',
        'Alan approval': 'pending',
        DEV: 'pending',
        QA: 'pending',
        'Homologation': 'pending',
      },
      archived: false,
      column: 'Alan approval',
    },
    {
      id: 'dev-existing-card',
      title: 'DEV existing card',
      description: 'Keeps DEV column non-empty',
      path: 'openspec/changes/dev-existing-card/proposal',
      status: {
        PO: 'approved',
        DESIGN: 'approved',
        'Alan approval': 'approved',
        DEV: 'pending',
        QA: 'pending',
        'Homologation': 'pending',
      },
      archived: false,
      column: 'DEV',
    },
  ]

  const patchCalls: Array<{ changeId: string; status: string }> = []

  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: changes }),
    })
  })

  await page.route('**/api/workflow/projects/crypto/changes/*', async (route) => {
    const changeId = route.request().url().split('/').pop() || ''
    const payload = route.request().postDataJSON() as { status?: string }
    patchCalls.push({ changeId: decodeURIComponent(changeId), status: payload.status || '' })

    const item = changes.find((candidate) => candidate.id === decodeURIComponent(changeId))
    if (item && payload.status) item.column = payload.status

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: changeId,
        project_id: 'crypto',
        change_id: decodeURIComponent(changeId),
        title: item?.title || changeId,
        description: item?.description || '',
        status: payload.status || item?.column || 'Pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }),
    })
  })

  await page.route('**/api/workflow/kanban/changes/*/tasks?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ change_id: 'x', path: 'openspec/changes/x/proposal', sections: [] }),
    })
  })

  await page.route('**/api/workflow/kanban/changes/*/comments?project_slug=crypto', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ change_id: 'x', items: [] }),
      })
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ item: { id: 'comment-1', change: 'x', author: 'qa', created_at: new Date().toISOString(), body: 'ok' } }),
    })
  })

  await page.goto('/kanban')

  const sourceCard = page.getByRole('button', { name: /Open details for approved-card/i })
  const targetCard = page.getByRole('button', { name: /Open details for dev-existing-card/i })

  await sourceCard.evaluate((element) => {
    const dt = new DataTransfer()
    dt.setData('application/x-kanban-change-id', 'approved-card')
    dt.setData('text/plain', 'approved-card')
    ;(window as typeof window & { __kanbanDt?: DataTransfer }).__kanbanDt = dt
    element.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
  })

  await targetCard.evaluate((element) => {
    const dt = (window as typeof window & { __kanbanDt?: DataTransfer }).__kanbanDt
    element.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }))
    element.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }))
  })

  await expect
    .poll(() => patchCalls.some((call) => call.changeId === 'approved-card' && call.status === 'DEV'))
    .toBeTruthy()

  await page.setViewportSize({ width: 390, height: 844 })
  await page.reload()

  await page.getByRole('tab', { name: /DEV/i }).click()
  const mobileCard = page.getByRole('button', { name: /Open details for approved-card/i })
  await mobileCard.dispatchEvent('touchstart', {
    touches: [{ identifier: 1, clientX: 180, clientY: 360 }],
  })
  await page.waitForTimeout(520)
  await mobileCard.dispatchEvent('touchend', {
    changedTouches: [{ identifier: 1, clientX: 180, clientY: 360 }],
  })

  await expect(page.getByText('Mover card')).toBeVisible()
  await expect(page.locator('aside').getByText('Approved card')).toBeVisible()
})
