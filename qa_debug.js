const { chromium } = require('playwright');

const BASE_URL = 'http://72.60.150.140:5173';

async function debugQA() {
  const browser = await chromium.launch({ headless: true });

  // Check login page elements
  console.log('=== DEBUG: Login Page ===');
  const ctx = await browser.newContext({ viewport: { width: 1024, height: 768 } });
  const page = await ctx.newPage();
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(2000);
  
  const url = page.url();
  console.log('URL:', url);
  
  const html = await page.content();
  // Print first 3000 chars of body
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  if (bodyMatch) {
    console.log('Body (first 3000):', bodyMatch[1].substring(0, 3000));
  }
  
  // Get all inputs
  const inputs = await page.$$('input');
  console.log('Inputs found:', inputs.length);
  for (const inp of inputs) {
    const type = await inp.getAttribute('type');
    const name = await inp.getAttribute('name');
    const id = await inp.getAttribute('id');
    const placeholder = await inp.getAttribute('placeholder');
    console.log('  input:', { type, name, id, placeholder });
  }
  
  // Get all buttons
  const buttons = await page.$$('button');
  console.log('Buttons found:', buttons.length);
  for (const btn of buttons) {
    const text = await btn.textContent();
    const ariaLabel = await btn.getAttribute('aria-label');
    const className = await btn.getAttribute('class');
    console.log('  button:', { text: text?.trim(), ariaLabel, className });
  }
  
  await browser.close();
}

debugQA().catch(console.error);
