import { expect, test } from '@playwright/test'

const mockedChangeId = 'kanban-visual-coordination'

test('Kanban loads and shows a mocked change', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  let currentColumn = 'QA'
  // Mock the backend API used by the Kanban page.
  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: mockedChangeId,
            title: 'Kanban visual coordination',
            path: 'docs/coordination/kanban-visual-coordination.md',
            status: {
              PO: 'done',
              'Alan approval': 'approved',
              DEV: 'done',
              QA: 'in progress',
              'Alan homologation': 'not reviewed',
            },
            archived: false,
            column: currentColumn,
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

    const payload = route.request().postDataJSON() as { status?: string }
    currentColumn = payload.status || currentColumn

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'wf-change-1',
        project_id: 'wf-project-1',
        change_id: mockedChangeId,
        title: 'Kanban visual coordination',
        status: currentColumn,
        created_at: '2026-03-11T00:00:00+00:00',
        updated_at: '2026-03-11T00:01:00+00:00',
      }),
    })
  })

  await page.goto('/kanban')

  await expect(page.getByText('Opportunity Board')).toBeVisible()
  await expect(page.getByRole('tab', { name: /QA 1/i })).toBeVisible()
  await page.getByRole('tab', { name: /DEV 0/i }).click()
  await expect(page.getByText('Current stage')).toBeVisible()
  await expect(page.locator('section').filter({ hasText: 'Current stage' }).getByText('DEV', { exact: true })).toBeVisible()
  await expect(page.getByText('Nenhum card nesta etapa.')).toBeVisible()

  await page.getByRole('tab', { name: /QA 1/i }).click()
  await expect(page.getByRole('button', { name: `Open details for ${mockedChangeId}` })).toBeVisible()

  // Open the details sheet to ensure the rest of the page can render using the mocked API.
  await page.getByRole('button', { name: `Open details for ${mockedChangeId}` }).click()
  await expect(page.getByText('Detalhes', { exact: true })).toBeVisible()
  await expect(page.getByText('Tasks', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('Story:')).toBeVisible()
  await expect(page.getByText('Implement DB-backed task adapter')).toBeVisible()
  await expect(page.getByText('story-1')).toBeVisible()
  await expect(page.getByText('Bug:')).toBeVisible()
  await expect(page.getByText('Keep Kanban checklist shape compatible')).toBeVisible()
  await expect(page.getByText('bug-1')).toBeVisible()
  await expect(page.getByText('Comments')).toBeVisible()

})
