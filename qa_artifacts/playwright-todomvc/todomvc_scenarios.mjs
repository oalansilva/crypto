import fs from 'node:fs/promises';
import path from 'node:path';
import playwright from '../../frontend/node_modules/@playwright/test/index.js';

const baseUrl = 'https://demo.playwright.dev/todomvc/';
const outputDir = path.resolve('qa_artifacts/playwright-todomvc');
const { chromium } = playwright;

async function ensureDir() {
  await fs.mkdir(outputDir, { recursive: true });
}

async function newPage(browser) {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 960 },
  });
  const page = await context.newPage();
  await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
  await page.waitForSelector('.new-todo');
  return { context, page };
}

async function addTodo(page, text) {
  await page.locator('.new-todo').fill(text);
  await page.locator('.new-todo').press('Enter');
}

const scenarios = [
  {
    name: 'success_add_todo',
    type: 'success',
    async run(page) {
      await addTodo(page, 'Buy milk');
      await page.waitForSelector('.todo-list li');
      const count = await page.locator('.todo-list li').count();
      const text = await page.locator('.todo-list li .view label').textContent();
      if (count !== 1 || text?.trim() !== 'Buy milk') {
        throw new Error(`Expected one todo "Buy milk", got count=${count}, text=${text}`);
      }
    },
  },
  {
    name: 'success_complete_and_filter_completed',
    type: 'success',
    async run(page) {
      await addTodo(page, 'Ship release');
      await addTodo(page, 'Write notes');
      await page.locator('.todo-list li').first().locator('.toggle').check();
      await page.getByRole('link', { name: 'Completed' }).click();
      const items = page.locator('.todo-list li');
      const count = await items.count();
      const visibleTexts = [];
      for (let index = 0; index < count; index += 1) {
        const item = items.nth(index);
        if (await item.isVisible()) {
          visibleTexts.push((await item.locator('.view label').textContent())?.trim() ?? '');
        }
      }
      if (visibleTexts.length !== 1 || visibleTexts[0] !== 'Ship release') {
        throw new Error(`Expected completed list to show only "Ship release", got visible=${JSON.stringify(visibleTexts)}`);
      }
    },
  },
  {
    name: 'success_edit_todo',
    type: 'success',
    async run(page) {
      await addTodo(page, 'Old title');
      await page.locator('.todo-list li label').dblclick();
      await page.locator('.todo-list li .edit').fill('Updated title');
      await page.locator('.todo-list li .edit').press('Enter');
      await page.waitForTimeout(200);
      const text = await page.locator('.todo-list li .view label').textContent();
      if (text?.trim() !== 'Updated title') {
        throw new Error(`Expected updated title, got text=${text}`);
      }
    },
  },
  {
    name: 'negative_empty_submission_ignored',
    type: 'negative',
    async run(page) {
      await page.locator('.new-todo').press('Enter');
      const count = await page.locator('.todo-list li').count();
      if (count !== 0) {
        throw new Error(`Expected no todos after empty submission, got count=${count}`);
      }
    },
  },
  {
    name: 'negative_clear_completed_hidden_without_completed_items',
    type: 'negative',
    async run(page) {
      await addTodo(page, 'Active task');
      const clearCompleted = page.getByRole('button', { name: 'Clear completed' });
      if (await clearCompleted.isVisible().catch(() => false)) {
        throw new Error('Expected "Clear completed" button to stay hidden with no completed items');
      }
    },
  },
  {
    name: 'negative_empty_edit_removes_todo',
    type: 'negative',
    async run(page) {
      await addTodo(page, 'Disposable');
      await page.locator('.todo-list li label').dblclick();
      await page.locator('.todo-list li .edit').fill('');
      await page.locator('.todo-list li .edit').press('Enter');
      await page.waitForTimeout(200);
      const count = await page.locator('.todo-list li').count();
      if (count !== 0) {
        throw new Error(`Expected todo deletion after empty edit, got count=${count}`);
      }
    },
  },
  {
    name: 'failure_empty_submission_creates_todo',
    type: 'failure',
    async run(page) {
      await page.locator('.new-todo').press('Enter');
      const count = await page.locator('.todo-list li').count();
      if (count !== 1) {
        throw new Error(`Intentional failure: expected one todo after empty submission, got count=${count}`);
      }
    },
  },
  {
    name: 'failure_completed_filter_shows_active_item',
    type: 'failure',
    async run(page) {
      await addTodo(page, 'Ship release');
      await addTodo(page, 'Write notes');
      await page.locator('.todo-list li').first().locator('.toggle').check();
      await page.getByRole('link', { name: 'Completed' }).click();
      const text = await page.locator('.todo-list li .view label').textContent();
      if (text?.trim() !== 'Write notes') {
        throw new Error(`Intentional failure: expected completed filter to show "Write notes", got text=${text}`);
      }
    },
  },
];

async function main() {
  await ensureDir();
  const browser = await chromium.launch({
    headless: true,
  });

  const results = [];

  for (const scenario of scenarios) {
    const { context, page } = await newPage(browser);
    const screenshotPath = path.join(outputDir, `${scenario.name}.png`);
    try {
      await scenario.run(page);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      results.push({ name: scenario.name, type: scenario.type, status: 'passed', screenshot: screenshotPath });
    } catch (error) {
      await page.screenshot({ path: screenshotPath, fullPage: true });
      results.push({
        name: scenario.name,
        type: scenario.type,
        status: 'failed',
        screenshot: screenshotPath,
        error: error instanceof Error ? error.message : String(error),
      });
    } finally {
      await context.close();
    }
  }

  await browser.close();

  const reportPath = path.join(outputDir, 'report.json');
  await fs.writeFile(reportPath, `${JSON.stringify(results, null, 2)}\n`);

  const failures = results.filter((result) => result.status === 'failed');
  if (failures.length > 0) {
    console.error(JSON.stringify({ status: 'failed', failures }, null, 2));
    process.exitCode = 1;
    return;
  }

  console.log(JSON.stringify({ status: 'passed', results }, null, 2));
}

await main();
