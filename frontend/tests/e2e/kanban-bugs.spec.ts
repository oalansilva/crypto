import { expect, test } from '@playwright/test'

const AUTH_USER = {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  isAdmin: false,
}

const storyId = 'monitor-table-redesign'
const bugId = 'monitor-table-redesign-bug-a1b2c3'

async function setupKanbanBugMocks(page: any) {
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

  await page.route('**/api/workflow/kanban/changes**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: storyId,
            title: 'Monitor table redesign',
            card_number: 99,
            path: `openspec/changes/${storyId}/proposal`,
            status: { PO: 'done', DEV: 'done', QA: 'in progress' },
            archived: false,
            column: 'DEV',
            position: 0,
            item_type: 'story',
            has_bugs: true,
          },
          {
            id: bugId,
            title: 'Cards hidden after table redesign',
            description: 'E2E must expand table rows before asserting card controls.',
            card_number: 1001,
            path: `openspec/changes/${storyId}/bugs/${bugId}`,
            status: { PO: 'done', DEV: 'in progress', QA: 'pending' },
            archived: false,
            column: 'DEV',
            position: 1,
            item_type: 'bug',
            parent_story_title: 'Monitor table redesign',
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
        change_id: storyId,
        path: `openspec/changes/${storyId}/tasks.md`,
        sections: [{ title: 'Tasks', items: [] }],
      }),
    })
  })

  await page.route('**/api/workflow/kanban/changes/*/comments?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ change_id: storyId, items: [] }),
    })
  })
}

test.describe('Kanban Bug Cards', () => {
  test.beforeEach(async ({ page }) => {
    await setupKanbanBugMocks(page)
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/kanban')
    await page.getByRole('tab', { name: /DEV 2/i }).click()
  })

  test('bug cards appear in the board with bug label and parent story', async ({ page }) => {
    const bugCard = page.getByRole('button', { name: `Open details for ${bugId}` })

    await expect(bugCard).toBeVisible()
    await expect(bugCard.getByText('🐛 BUG')).toBeVisible()
    await expect(bugCard.getByText('Story: Monitor table redesign')).toBeVisible()
    await expect(bugCard.getByText('Cards hidden after table redesign')).toBeVisible()
  })

  test('clicking bug card opens bug detail', async ({ page }) => {
    await page.getByRole('button', { name: `Open details for ${bugId}` }).click()

    const detailsSheet = page.getByRole('complementary')
    await expect(detailsSheet.getByText('Detalhes', { exact: true })).toBeVisible()
    await expect(detailsSheet.getByText(bugId, { exact: true })).toBeVisible()
    await expect(detailsSheet.getByText('Stage atual: DEV')).toBeVisible()
  })

  test('show/hide bugs toggle works', async ({ page }) => {
    const bugCard = page.getByRole('button', { name: `Open details for ${bugId}` })
    const toggleButton = page.getByRole('button', { name: '🐛 Bugs On' })

    await expect(bugCard).toBeVisible()
    await toggleButton.click()

    await expect(page.getByRole('button', { name: '🐛 Bugs Off' })).toBeVisible()
    await expect(bugCard).toHaveCount(0)

    await page.getByRole('button', { name: '🐛 Bugs Off' }).click()
    await expect(bugCard).toBeVisible()
  })
})
