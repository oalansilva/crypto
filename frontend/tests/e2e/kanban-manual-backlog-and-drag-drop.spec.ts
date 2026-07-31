import { expect, test } from '@playwright/test'

test('Alan approves design by desktop drop and mobile long-press opens move sheet', async ({ page }) => {
  const changes = [
    {
      id: 'pending-card',
      title: 'Todo card',
      description: 'Starts in Todo',
      path: 'openspec/changes/pending-card/proposal',
      status: {
        PO: 'pending',
        DESIGN: 'pending',
        'Approval': 'pending',
        DEV: 'pending',
        QA: 'pending',
        'Homologation': 'pending',
      },
      archived: false,
      column: 'Todo',
    },
    {
      id: 'approved-card',
      title: 'Design awaiting approval',
      description: 'Ready for Alan review',
      path: 'openspec/changes/approved-card/proposal',
      status: {
        PO: 'approved',
        DESIGN: 'approved',
        'Approval': 'pending',
        DEV: 'pending',
        QA: 'pending',
        'Homologation': 'pending',
      },
      archived: false,
      column: 'Aprovação de Design',
      ui_impact: 'affected',
      design_ref: 'openspec/changes/approved-card/design.md',
      design_digest: 'design-sha-1',
      prototype_ref: 'frontend/public/prototypes/approved-card/index.html',
      prototype_digest: 'prototype-sha-1',
      design_critique_verdict: 'PASS',
    },
    {
      id: 'ready-existing-card',
      title: 'Ready existing card',
      description: 'Keeps Pronto para Dev non-empty',
      path: 'openspec/changes/dev-existing-card/proposal',
      status: {
        PO: 'approved',
        DESIGN: 'approved',
        'Approval': 'approved',
        DEV: 'pending',
        QA: 'pending',
        'Homologation': 'pending',
      },
      archived: false,
      column: 'Pronto para Dev',
    },
  ]

  const patchCalls: Array<{ changeId: string; status: string; authorization: string | null }> = []

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
    patchCalls.push({
      changeId: decodeURIComponent(changeId),
      status: payload.status || '',
      authorization: route.request().headers()['authorization'] || null,
    })

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
        status: payload.status || item?.column || 'Todo',
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
  const targetCard = page.getByRole('button', { name: /Open details for ready-existing-card/i })

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
    .poll(() => patchCalls.some((call) => call.changeId === 'approved-card' && call.status === 'Pronto para Dev'))
    .toBeTruthy()
  expect(patchCalls.find((call) => call.changeId === 'approved-card')?.authorization).toMatch(/^Bearer /)
  await expect(page.getByRole('status').filter({ hasText: 'Design aprovado' }).first()).toContainText('Design aprovado')

  await page.setViewportSize({ width: 390, height: 844 })
  await page.reload()

  await page.getByRole('tab', { name: /Pronto para Dev/i }).click()
  const mobileCard = page.getByRole('button', { name: /Open details for approved-card/i })
  await mobileCard.dispatchEvent('touchstart', {
    touches: [{ identifier: 1, clientX: 180, clientY: 360 }],
  })
  await page.waitForTimeout(520)
  await mobileCard.dispatchEvent('touchend', {
    changedTouches: [{ identifier: 1, clientX: 180, clientY: 360 }],
  })

  await expect(page.getByText('Mover card')).toBeVisible()
  await expect(page.locator('aside').getByText('Design awaiting approval')).toBeVisible()
})

test('drawer exposes design evidence and accessible approval reports authorization failure', async ({ page }) => {
  const changeId = 'design-auth-required'
  let authorization: string | undefined

  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      items: [
        {
          id: changeId,
          title: 'Design auth required',
          description: 'Alan must approve this exact evidence.',
          path: `openspec/changes/${changeId}/proposal`,
          status: {},
          archived: false,
          column: 'Aprovação de Design',
          ui_impact: 'affected',
          design_ref: `openspec/changes/${changeId}/design.md`,
          design_digest: 'design-digest-340',
          prototype_ref: `frontend/public/prototypes/${changeId}/index.html`,
          prototype_digest: 'prototype-digest-340',
          design_critique_verdict: 'PASS',
          design_delivered_at: '2026-07-31T12:00:00Z',
          design_approved_by: 'Alan',
          design_approved_at: '2026-07-30T12:00:00Z',
          approved_design_digest: 'old-design-digest',
          approved_prototype_digest: 'old-prototype-digest',
          design_approval_valid: false,
        },
        {
          id: 'backend-only-bypass',
          title: 'Backend only bypass',
          path: 'openspec/changes/backend-only-bypass/proposal',
          status: {},
          archived: false,
          column: 'Todo',
          ui_impact: 'none',
          ui_impact_justification: 'Apenas migração de índice PostgreSQL; nenhum consumidor visual.',
        },
      ],
    }),
  }))
  await page.route('**/api/workflow/kanban/changes/*/tasks?project_slug=crypto', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ change_id: changeId, path: `openspec/changes/${changeId}/tasks.md`, sections: [] }),
  }))
  await page.route('**/api/workflow/kanban/changes/*/comments?project_slug=crypto', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ change_id: changeId, items: [] }),
  }))
  await page.route(`**/api/workflow/projects/crypto/changes/${changeId}/tasks`, (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: '[]',
  }))
  await page.route(`**/api/workflow/projects/crypto/changes/${changeId}`, async (route) => {
    authorization = route.request().headers()['authorization']
    await route.fulfill({
      status: 403,
      contentType: 'application/json',
      body: JSON.stringify({ detail: { code: 'design_approval_forbidden', message: 'Somente Alan pode aprovar o design.' } }),
    })
  })

  await page.goto('/kanban')
  await page.getByRole('button', { name: `Open details for ${changeId}` }).click()

  const drawer = page.getByRole('complementary')
  await expect(drawer.getByText('Entrega de design')).toBeVisible()
  await expect(drawer.getByText('PASS', { exact: true })).toBeVisible()
  await expect(drawer.getByText('Obsoleta', { exact: true })).toBeVisible()
  await expect(drawer.getByRole('link', { name: `openspec/changes/${changeId}/design.md` })).toHaveAttribute(
    'href',
    `/openspec/changes/${changeId}/design`,
  )

  await drawer.getByRole('button', { name: 'Aprovar design' }).click()
  await expect(page.getByRole('alert').filter({ hasText: 'Somente Alan pode aprovar o design.' }).first()).toBeVisible()
  expect(authorization).toMatch(/^Bearer /)
  await expect(drawer.getByText('Etapa atual: Aprovação de Design')).toBeVisible()

  await drawer.getByRole('button', { name: 'Close panel' }).click()
  await page.getByRole('button', { name: 'Open details for backend-only-bypass' }).click()
  const bypassDrawer = page.getByRole('complementary')
  await expect(bypassDrawer.getByText('Sem impacto de UI')).toBeVisible()
  await expect(bypassDrawer.getByText('Apenas migração de índice PostgreSQL; nenhum consumidor visual.')).toBeVisible()
})

test('controlled rework requires a reason for desktop drag and mobile move actions', async ({ page }) => {
  const changes = [
    {
      id: 'approval-rework',
      title: 'Approval needs rework',
      path: 'openspec/changes/approval-rework/proposal',
      status: {},
      archived: false,
      column: 'Aprovação de Design',
    },
    {
      id: 'design-target',
      title: 'Design target',
      path: 'openspec/changes/design-target/proposal',
      status: {},
      archived: false,
      column: 'Design',
    },
    {
      id: 'review-rework',
      title: 'Review needs rework',
      path: 'openspec/changes/review-rework/proposal',
      status: {},
      archived: false,
      column: 'Code Review',
    },
    {
      id: 'qa-rework',
      title: 'QA needs rework',
      path: 'openspec/changes/qa-rework/proposal',
      status: {},
      archived: false,
      column: 'QA',
    },
    {
      id: 'development-target',
      title: 'Development target',
      path: 'openspec/changes/development-target/proposal',
      status: {},
      archived: false,
      column: 'Em desenvolvimento',
    },
  ]
  const patchCalls: Array<{ changeId: string; status: string; reworkReason?: string }> = []

  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: changes }),
  }))
  await page.route('**/api/workflow/projects/crypto/changes/*', async (route) => {
    if (route.request().method() !== 'PATCH') {
      await route.fallback()
      return
    }
    const changeId = decodeURIComponent(route.request().url().split('/').pop() || '')
    const payload = route.request().postDataJSON() as { status: string; rework_reason?: string }
    patchCalls.push({ changeId, status: payload.status, reworkReason: payload.rework_reason })
    const item = changes.find((candidate) => candidate.id === changeId)
    if (item) item.column = payload.status
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: changeId,
        project_id: 'crypto',
        change_id: changeId,
        title: item?.title || changeId,
        description: '',
        status: payload.status,
        created_at: '2026-07-31T12:00:00Z',
        updated_at: '2026-07-31T12:00:00Z',
      }),
    })
  })

  await page.goto('/kanban')
  await page.getByRole('tab', { name: 'Todas' }).click()

  const dragCard = async (sourceId: string, targetId: string) => {
    await page.getByRole('button', { name: `Open details for ${sourceId}` }).evaluate((element, id) => {
      const dt = new DataTransfer()
      dt.setData('application/x-kanban-change-id', id)
      dt.setData('text/plain', id)
      ;(window as typeof window & { __reworkDt?: DataTransfer }).__reworkDt = dt
      element.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
    }, sourceId)
    await page.getByRole('button', { name: `Open details for ${targetId}` }).evaluate((element) => {
      const dt = (window as typeof window & { __reworkDt?: DataTransfer }).__reworkDt
      element.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }))
    })
  }

  const confirmRework = async (reason: string) => {
    const dialog = page.getByRole('dialog', { name: 'Justificar retrabalho' })
    const reasonInput = dialog.getByLabel('Justificativa do retrabalho')
    await expect(reasonInput).toBeFocused()
    await reasonInput.fill('   ')
    await dialog.getByRole('button', { name: 'Confirmar retrabalho' }).click()
    await expect(dialog.getByRole('alert')).toContainText('Informe uma justificativa')
    await reasonInput.fill(reason)
    await dialog.getByRole('button', { name: 'Confirmar retrabalho' }).click()
    await expect(dialog).toBeHidden()
  }

  await dragCard('approval-rework', 'design-target')
  await expect(page.getByRole('dialog')).toContainText('Aprovação de Design → Design')
  expect(patchCalls).toHaveLength(0)
  await confirmRework('Ajustar hierarquia visual antes de nova aprovação.')

  await dragCard('review-rework', 'development-target')
  await expect(page.getByRole('dialog')).toContainText('Code Review → Em desenvolvimento')
  await confirmRework('Corrigir o achado bloqueante do review.')

  await dragCard('qa-rework', 'development-target')
  await expect(page.getByRole('dialog')).toContainText('QA → Em desenvolvimento')
  await confirmRework('Corrigir regressão encontrada no QA.')

  expect(patchCalls).toEqual([
    {
      changeId: 'approval-rework',
      status: 'Design',
      reworkReason: 'Ajustar hierarquia visual antes de nova aprovação.',
    },
    {
      changeId: 'review-rework',
      status: 'Em desenvolvimento',
      reworkReason: 'Corrigir o achado bloqueante do review.',
    },
    {
      changeId: 'qa-rework',
      status: 'Em desenvolvimento',
      reworkReason: 'Corrigir regressão encontrada no QA.',
    },
  ])

  const qaItem = changes.find((item) => item.id === 'qa-rework')!
  qaItem.column = 'QA'
  await page.setViewportSize({ width: 390, height: 844 })
  await page.reload()
  await page.getByRole('tab', { name: 'Entrega' }).click()
  await page.getByRole('tab', { name: /^QA/ }).click()

  const mobileCard = page.getByRole('button', { name: 'Open details for qa-rework' })
  await mobileCard.dispatchEvent('touchstart', {
    touches: [{ identifier: 1, clientX: 180, clientY: 360 }],
  })
  await page.waitForTimeout(520)
  await mobileCard.dispatchEvent('touchend', {
    changedTouches: [{ identifier: 1, clientX: 180, clientY: 360 }],
  })
  await page.getByRole('button', { name: /Em desenvolvimento\s+Mover/ }).click()
  await expect(page.getByRole('dialog')).toContainText('QA → Em desenvolvimento')
  await confirmRework('Motivo informado pelo fluxo mobile.')

  expect(patchCalls.at(-1)).toEqual({
    changeId: 'qa-rework',
    status: 'Em desenvolvimento',
    reworkReason: 'Motivo informado pelo fluxo mobile.',
  })
})

test('only PASS is a valid critique and bypass success is not reported as design approval', async ({ page }) => {
  const changes = [
    {
      id: 'blocked-design',
      title: 'Blocked design',
      path: 'openspec/changes/blocked-design/proposal',
      status: {},
      archived: false,
      column: 'Aprovação de Design',
      ui_impact: 'affected',
      design_ref: 'openspec/changes/blocked-design/design.md',
      design_digest: 'design-digest',
      prototype_ref: 'frontend/public/prototypes/blocked-design/index.html',
      prototype_digest: 'prototype-digest',
      design_critique_verdict: ' BLOCKED ',
    },
    {
      id: 'backend-bypass',
      title: 'Backend bypass',
      path: 'openspec/changes/backend-bypass/proposal',
      status: {},
      archived: false,
      column: 'Todo',
      ui_impact: 'none',
      ui_impact_justification: 'Mudança restrita ao índice do banco.',
    },
    {
      id: 'ready-target',
      title: 'Ready target',
      path: 'openspec/changes/ready-target/proposal',
      status: {},
      archived: false,
      column: 'Pronto para Dev',
    },
  ]
  let bypassPayload: { status?: string; rework_reason?: string } | null = null

  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ items: changes }),
  }))
  await page.route('**/api/workflow/kanban/changes/*/tasks?project_slug=crypto', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ change_id: 'blocked-design', path: '', sections: [] }),
  }))
  await page.route('**/api/workflow/kanban/changes/*/comments?project_slug=crypto', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ change_id: 'blocked-design', items: [] }),
  }))
  await page.route('**/api/workflow/projects/crypto/changes/blocked-design/tasks', (route) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: '[]',
  }))
  await page.route('**/api/workflow/projects/crypto/changes/*', async (route) => {
    if (route.request().method() === 'GET') {
      const id = decodeURIComponent(route.request().url().split('/').pop() || '')
      const item = changes.find((candidate) => candidate.id === id)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...item,
          id,
          project_id: 'crypto',
          change_id: id,
          description: '',
          status: item?.column || 'Todo',
          created_at: '2026-07-31T12:00:00Z',
          updated_at: '2026-07-31T12:00:00Z',
        }),
      })
      return
    }
    const id = decodeURIComponent(route.request().url().split('/').pop() || '')
    const payload = route.request().postDataJSON() as { status?: string; rework_reason?: string }
    if (id === 'backend-bypass') bypassPayload = payload
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id,
        project_id: 'crypto',
        change_id: id,
        title: 'Backend bypass',
        description: '',
        status: payload.status,
        created_at: '2026-07-31T12:00:00Z',
        updated_at: '2026-07-31T12:00:00Z',
      }),
    })
  })

  await page.goto('/kanban')
  await page.getByRole('button', { name: 'Open details for blocked-design' }).click()
  const drawer = page.getByRole('complementary')
  await expect(drawer.getByText('Entrega incompleta')).toBeVisible()
  await expect(drawer.getByText('veredito da crítica do Designer Agent igual a PASS')).toBeVisible()
  await expect(drawer.getByRole('button', { name: 'Aprovar design' })).toBeDisabled()
  await drawer.getByRole('button', { name: 'Close panel' }).click()

  const sourceCard = page.getByRole('button', { name: 'Open details for backend-bypass' })
  const targetCard = page.getByRole('button', { name: 'Open details for ready-target' })
  await sourceCard.evaluate((element) => {
    const dt = new DataTransfer()
    dt.setData('application/x-kanban-change-id', 'backend-bypass')
    dt.setData('text/plain', 'backend-bypass')
    ;(window as typeof window & { __bypassDt?: DataTransfer }).__bypassDt = dt
    element.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }))
  })
  await targetCard.evaluate((element) => {
    const dt = (window as typeof window & { __bypassDt?: DataTransfer }).__bypassDt
    element.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }))
  })

  await expect(page.getByRole('status').filter({ hasText: 'Card sem impacto de UI' }).first()).toContainText(
    'Card sem impacto de UI movido para Pronto para Dev.',
  )
  await expect(page.getByRole('status').filter({ hasText: 'Design aprovado' })).toHaveCount(0)
  expect(bypassPayload).toEqual({ status: 'Pronto para Dev' })
})
