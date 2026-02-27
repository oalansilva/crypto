import { expect, test } from '@playwright/test'

const mockedChangeId = 'kanban-visual-coordination'

test('Kanban loads and shows a mocked change', async ({ page }) => {
  // Mock the backend API used by the Kanban page.
  await page.route('**/api/coordination/changes', async (route) => {
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
            column: 'QA',
          },
        ],
      }),
    })
  })

  await page.route('**/api/coordination/changes/*/tasks', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        change_id: mockedChangeId,
        path: `openspec/changes/${mockedChangeId}/tasks.md`,
        sections: [
          {
            title: '3. QA',
            items: [{ text: 'Minimal E2E test: Kanban loads and shows a mocked change', checked: false }],
          },
        ],
      }),
    })
  })

  await page.route('**/api/coordination/changes/*/comments', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ change_id: mockedChangeId, items: [] }),
    })
  })

  await page.goto('/kanban')

  await expect(page.getByRole('heading', { name: 'Kanban' })).toBeVisible()
  await expect(page.getByText(mockedChangeId, { exact: true })).toBeVisible()

  // Open the details panel to ensure the rest of the page can render using the mocked API.
  await page.getByRole('button', { name: `Open details for ${mockedChangeId}` }).click()
  await expect(page.getByText('Detalhes')).toBeVisible()
  await expect(page.getByText('Tasks')).toBeVisible()
  await expect(page.getByText('Comments')).toBeVisible()
})
