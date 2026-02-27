import { expect, test } from '@playwright/test'

const mockedSpecId = '07-strategy-lab-langgraph-v2'

test('Regression: /openspec list and detail pages still render', async ({ page }) => {
  await page.route('**/api/openspec/specs', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: mockedSpecId,
            path: `openspec/specs/${mockedSpecId}.md`,
            title: 'Mocked spec title',
            status: 'active',
            updated_at: '2026-02-27T00:00:00Z',
          },
        ],
      }),
    })
  })

  await page.route(`**/api/openspec/specs/${mockedSpecId}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: mockedSpecId,
        markdown: '# Hello OpenSpec\n\nThis is a mocked spec.',
      }),
    })
  })

  await page.goto('/openspec')

  await expect(page.getByRole('heading', { name: 'OpenSpec' })).toBeVisible()
  await expect(page.getByText('Mocked spec title')).toBeVisible()

  await page.getByRole('link', { name: 'Mocked spec title' }).click()
  await expect(page.getByText('# Hello OpenSpec')).toBeVisible()
})

test('Regression: /openspec/changes/<change>/<artifact> still renders', async ({ page }) => {
  const changeId = 'kanban-visual-coordination'
  const artifact = 'tasks.md'

  await page.route(`**/api/openspec/changes/${changeId}/${artifact}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        change_id: changeId,
        artifact,
        markdown: '## 3. QA\n\n- [x] 3.1 ...\n- [ ] 3.2 ...',
      }),
    })
  })

  await page.goto(`/openspec/changes/${changeId}/${artifact}`)

  await expect(page.getByText('Change', { exact: true })).toBeVisible()
  await expect(page.getByText(`changes/${changeId}/${artifact}`)).toBeVisible()
  await expect(page.getByText('## 3. QA')).toBeVisible()
})
