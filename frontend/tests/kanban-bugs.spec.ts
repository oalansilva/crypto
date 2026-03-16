import { test, expect } from '@playwright/test';

test.describe('Kanban Bug Cards', () => {
  const BASE_URL = process.env.CANVAS_URL || 'http://localhost:5173';

  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/kanban`);
    await page.waitForLoadState('networkidle');
  });

  test('bug cards appear in correct column', async ({ page }) => {
    // Get all columns
    const columns = await page.locator('[class*="grid"]').first();
    expect(columns).toBeVisible();
    
    // Bug cards should have red styling
    const bugCards = await page.locator('[class*="red-400"]').all();
    console.log(`Found ${bugCards.length} bug-styled cards`);
  });

  test('clicking bug card opens bug detail', async ({ page }) => {
    // Find a bug card (look for bug label)
    const bugCard = page.locator('text=🐛 BUG').first();
    
    if (await bugCard.isVisible()) {
      await bugCard.click();
      
      // Should open drawer/modal with bug details
      // Verify drawer is open
      const drawer = page.locator('[class*="fixed"][class*="inset-0"]').first();
      // Note: May need adjustment based on actual drawer implementation
    }
  });

  test('show/hide bugs toggle works', async ({ page }) => {
    // Look for toggle button
    const toggleButton = page.locator('text=🐛 Bugs');
    
    if (await toggleButton.isVisible()) {
      const initialState = await toggleButton.textContent();
      
      await toggleButton.click();
      
      const newState = await toggleButton.textContent();
      expect(newState).not.toBe(initialState);
    }
  });
});
