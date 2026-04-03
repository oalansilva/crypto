import { expect, test } from '@playwright/test'

test('Kanban drawer edits title/description and cancels card without losing identity', async ({ page }) => {
  const mockedChangeId = 'alterar-dados-dos-cards'
  let currentColumn = 'DEV'
  let currentTitle = 'alterar dados dos cards'
  let currentDescription = 'Editar título e descrição mantendo o histórico.'
  const patchPayloads: Array<{ title?: string; description?: string; status?: string; cancel_archive?: boolean }> = []

  await page.setViewportSize({ width: 390, height: 844 })

  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: mockedChangeId,
            title: currentTitle,
            description: currentDescription,
            path: `openspec/changes/${mockedChangeId}/proposal`,
            status: {
              PO: 'approved',
              DESIGN: 'approved',
              'Approval': 'approved',
              DEV: 'in progress',
              QA: 'pending',
              'Homologation': 'pending',
            },
            archived: currentColumn === 'Archived',
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
        sections: [{ title: 'Tasks', items: [] }],
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

    const payload = route.request().postDataJSON() as { title?: string; description?: string; status?: string; cancel_archive?: boolean }
    patchPayloads.push(payload)
    currentTitle = payload.title ?? currentTitle
    currentDescription = payload.description ?? currentDescription
    currentColumn = payload.status ?? currentColumn

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'wf-change-edit-1',
        project_id: 'wf-project-1',
        change_id: mockedChangeId,
        title: currentTitle,
        description: currentDescription,
        status: currentColumn,
        created_at: '2026-03-14T00:00:00+00:00',
        updated_at: '2026-03-14T00:01:00+00:00',
      }),
    })
  })

  await page.goto('/kanban')
  await page.getByRole('tab', { name: /DEV 1/i }).click()
  await page.getByRole('button', { name: `Open details for ${mockedChangeId}` }).click()

  await expect(page.getByText('Detalhes', { exact: true })).toBeVisible()
  await expect(page.getByRole('complementary').getByText(mockedChangeId, { exact: true })).toBeVisible()
  await expect(page.getByText('Stage atual: DEV')).toBeVisible()

  const titleInput = page.getByPlaceholder('Título do card')
  const descriptionInput = page.getByPlaceholder('Descrição do card')

  await titleInput.fill('Alterar dados dos cards com drawer')
  await descriptionInput.fill('Agora dá para editar e cancelar sem perder id nem histórico.')
  await page.getByRole('button', { name: 'Salvar' }).click()

  await expect(titleInput).toHaveValue('Alterar dados dos cards com drawer')
  await expect(descriptionInput).toHaveValue('Agora dá para editar e cancelar sem perder id nem histórico.')
  await expect(page.getByRole('complementary').getByText('Alterar dados dos cards com drawer', { exact: true })).toBeVisible()
  expect(patchPayloads[0]).toEqual({
    title: 'Alterar dados dos cards com drawer',
    description: 'Agora dá para editar e cancelar sem perder id nem histórico.',
  })

  page.once('dialog', async (dialog) => {
    expect(dialog.message()).toContain(mockedChangeId)
    await dialog.accept()
  })
  await page.getByRole('button', { name: 'Cancelar card' }).click()

  await expect(page.getByRole('button', { name: 'Já cancelado' })).toBeVisible()
  expect(patchPayloads[1]).toEqual({ status: 'Archived', cancel_archive: true })

  await page.getByRole('button', { name: 'Close panel' }).click()
  const archivedTab = page.getByRole('tab', { name: /Archived 1/i })
  await archivedTab.click()
  await expect(archivedTab).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByRole('button', { name: `Open details for ${mockedChangeId}` })).toBeVisible()
})
