import { expect, test } from '@playwright/test'

const AUTH_USER = {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  isAdmin: false,
}

async function mockAuthenticatedSession(page: any) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)

  await page.route('**/api/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  })
}

const mockedChangeId = 'kanban-visual-coordination'
const secondMockedChangeId = 'mobile-kanban-ui-rethink'

test('Kanban loads and shows a mocked change', async ({ page }) => {
  await mockAuthenticatedSession(page)
  await page.setViewportSize({ width: 390, height: 844 })
  const orderedIds = [mockedChangeId, secondMockedChangeId]
  // Mock the backend API used by the Kanban page.
  await page.route('**/api/workflow/kanban/changes**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: orderedIds.map((id, index) => ({
          id,
          title: id === mockedChangeId ? 'Kanban visual coordination' : 'Mobile Kanban UI rethink',
          card_number: id === mockedChangeId ? 41 : 42,
          path: `openspec/changes/${id}/proposal`,
          status: {
            PO: 'done',
            'Approval': 'approved',
            DEV: 'done',
            QA: 'in progress',
            'Homologation': 'not reviewed',
          },
          archived: false,
          column: 'QA',
          position: index,
        })),
      }),
    })
  })

  await page.route('**/api/workflow/kanban/changes/*/tasks?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        change_id: mockedChangeId,
        path: `openspec/changes/${mockedChangeId}/tasks.md`,
        sections: [
          {
            title: 'Tasks',
            items: [
              {
                text: 'Implement DB-backed task adapter',
                title: 'Story',
                code: 'story-1',
                checked: false,
                children: [
                  {
                    text: 'Keep Kanban checklist shape compatible',
                    title: 'Bug',
                    code: 'bug-1',
                    checked: true,
                  },
                ],
              },
            ],
          },
        ],
      }),
    })
  })

  await page.route('**/api/workflow/kanban/changes/*/comments?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ change_id: mockedChangeId, items: [] }),
    })
  })

  await page.route('**/api/workflow/projects/crypto/changes/*', async (route) => {
    if (route.request().method() !== 'PATCH') {
      await route.fallback()
      return
    }

    const payload = route.request().postDataJSON() as { status?: string; reorder?: 'up' | 'down' }
    const changeId = route.request().url().split('/').pop() || mockedChangeId
    const currentIndex = orderedIds.findIndex((id) => id === changeId)

    if (payload.reorder && currentIndex !== -1) {
      const swapIndex = payload.reorder === 'up' ? currentIndex - 1 : currentIndex + 1
      if (swapIndex >= 0 && swapIndex < orderedIds.length) {
        ;[orderedIds[currentIndex], orderedIds[swapIndex]] = [orderedIds[swapIndex], orderedIds[currentIndex]]
      }
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: `wf-${changeId}`,
        project_id: 'wf-project-1',
        change_id: changeId,
        title: changeId === mockedChangeId ? 'Kanban visual coordination' : 'Mobile Kanban UI rethink',
        status: payload.status || 'QA',
        card_number: changeId === mockedChangeId ? 41 : 42,
        created_at: '2026-03-11T00:00:00+00:00',
        updated_at: '2026-03-11T00:01:00+00:00',
      }),
    })
  })

  await page.goto('/kanban')

  await expect(page.getByText('Opportunity Board')).toBeVisible()
  await expect(page.getByRole('tab', { name: /QA 2/i })).toBeVisible()
  await page.getByRole('tab', { name: /DEV 0/i }).click()
  await expect(page.getByText('Current stage')).toBeVisible()
  await expect(page.locator('section').filter({ hasText: 'Current stage' }).getByText('DEV', { exact: true })).toBeVisible()
  await expect(page.getByText('Nenhum card nesta etapa.')).toBeVisible()

  await page.getByRole('tab', { name: /QA 2/i }).click()
  await expect(page.getByRole('button', { name: `Open details for ${mockedChangeId}` })).toBeVisible()
  await expect(page.getByRole('button', { name: `Open details for ${secondMockedChangeId}` })).toBeVisible()
  await expect(page.getByRole('button', { name: `Open details for ${mockedChangeId}` }).getByText('#41')).toBeVisible()
  await expect(page.getByRole('button', { name: `Open details for ${secondMockedChangeId}` }).getByText('#42')).toBeVisible()

  await page.getByRole('button', { name: 'Move down' }).first().click()
  await expect(page.getByRole('button', { name: `Open details for ${secondMockedChangeId}` }).first()).toBeVisible()

  // Open the details sheet to ensure the rest of the page can render using the mocked API.
  await page.getByRole('button', { name: `Open details for ${mockedChangeId}` }).click()
  await expect(page.getByText('Detalhes', { exact: true })).toBeVisible()
  const detailsSheet = page.getByRole('complementary')
  await expect(detailsSheet.getByText('#41')).toBeVisible()
  await expect(detailsSheet.getByRole('button', { name: 'Move up' })).toBeVisible()
  await expect(detailsSheet.getByRole('button', { name: 'Move down' })).toBeVisible()
  await expect(page.getByText('Tasks', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('Story:')).toBeVisible()
  await expect(page.getByText('Implement DB-backed task adapter')).toBeVisible()
  await expect(page.getByText('story-1')).toBeVisible()
  await expect(page.getByText('Bug:')).toBeVisible()
  await expect(page.getByText('Keep Kanban checklist shape compatible')).toBeVisible()
  await expect(page.getByText('bug-1')).toBeVisible()
  await expect(page.getByText('Comments', { exact: true })).toBeVisible()

})

test('Kanban normalizes legacy gate labels in board and drawer', async ({ page }) => {
  const mockedChangeId = 'legacy-approval-render'

  await mockAuthenticatedSession(page)
  await page.setViewportSize({ width: 390, height: 844 })

  await page.route('**/api/workflow/kanban/changes**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: mockedChangeId,
            title: 'Legacy gate render',
            card_number: 64,
          path: `openspec/changes/${mockedChangeId}/proposal`,
            status: {
              PO: 'done',
              DESIGN: 'done',
              ' Alan approval ': 'approved',
              DEV: 'in progress',
              QA: 'pending',
              ' Ready for homologation ': 'queued',
              ' Alan homologation ': 'pending',
            },
            archived: false,
            column: 'DEV',
            position: 0,
          },
        ],
      }),
    })
  })

  await page.route('**/api/workflow/kanban/changes/*/tasks?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        change_id: mockedChangeId,
        path: `openspec/changes/${mockedChangeId}/tasks.md`,
        sections: [],
      }),
    })
  })

  await page.route('**/api/workflow/kanban/changes/*/comments?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ change_id: mockedChangeId, items: [] }),
    })
  })

  await page.goto('/kanban')
  await page.getByRole('tab', { name: /DEV 1/i }).click()
  const card = page.getByRole('button', { name: `Open details for ${mockedChangeId}` })
  await expect(card).toBeVisible()
  await expect(card.getByText('Approval · approved')).toBeVisible()
  await expect(card.getByText('Ready for homologation · queued')).toBeVisible()

  await card.click()
  const detailsSheet = page.getByRole('complementary')
  await expect(detailsSheet.getByText('Stage atual: DEV')).toBeVisible()
  await expect(detailsSheet.getByText('Status', { exact: true })).toBeVisible()
  await expect(detailsSheet.getByText('Approval', { exact: true })).toBeVisible()
  await expect(detailsSheet.getByText('Homologation', { exact: true })).toBeVisible()
  await expect(detailsSheet.getByText('queued')).toBeVisible()
})
