# Kanban UI Validation With Playwright

Use Playwright for visual or interaction validation of the standalone Kanban UI.

## Default URL

```bash
http://127.0.0.1:5174/
```

## When To Use

Use this flow when the task involves:
- responsive regressions
- drawer behavior
- search / locate card
- comments form
- create/edit card modal or drawer
- project selector behavior
- visual comparison between old and new Kanban behavior

## Standard Validation Flow

1. Desktop run
   - open the page
   - locate the target card
   - open the drawer
   - capture screenshot

2. Mobile run
   - resize to mobile width
   - repeat the same interaction
   - capture screenshot

## Recommended Pattern

On this server, prefer one single Playwright run that:
- sets viewport
- goes to the page
- performs the whole interaction
- saves a screenshot

Example:

```bash
/usr/local/bin/playwright-cli-headed run-code 'async page => {
  await page.setViewportSize({ width: 1440, height: 1400 });
  await page.goto("http://127.0.0.1:5174/", { waitUntil: "networkidle" });
  await page.screenshot({ path: "/tmp/kanban-desktop.png", fullPage: true });
}'
```

## Minimum Checks

- correct project selected
- card visible in expected column
- search by card number or id works
- drawer opens
- checklist renders
- comments area renders
- mobile layout remains usable
