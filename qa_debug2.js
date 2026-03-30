const { chromium } = require('playwright');

const BASE_URL = 'http://72.60.150.140:5173';

async function debug() {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1024, height: 768 } });
  const page = await ctx.newPage();
  
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(2000);
  
  // List all buttons on the page
  const buttons = await page.$$('button');
  console.log('Total buttons:', buttons.length);
  for (const btn of buttons) {
    const text = await btn.textContent();
    const ariaLabel = await btn.getAttribute('aria-label');
    const className = await btn.getAttribute('class');
    const rect = await btn.boundingBox();
    console.log('Button:', { text: text?.trim(), ariaLabel, className: className?.substring(0, 100), rect });
  }
  
  // Check for header specifically
  const header = await page.$('header');
  if (header) {
    console.log('\nHeader found');
    const headerButtons = await header.$$('button');
    console.log('Header buttons:', headerButtons.length);
    for (const btn of headerButtons) {
      const text = await btn.textContent();
      const ariaLabel = await btn.getAttribute('aria-label');
      const rect = await btn.boundingBox();
      console.log('  Header button:', { text: text?.trim(), ariaLabel, rect });
    }
  }
  
  // Check for any logout/sair element
  const sair = await page.$('text=/sair/i');
  console.log('\nSair text element:', sair ? 'found' : 'not found');
  
  // Check what's in the viewport - maybe scroll needed
  const scrollY = await page.evaluate(() => window.scrollY);
  console.log('Scroll Y:', scrollY);
  
  await browser.close();
}

debug().catch(console.error);
