const { chromium } = require('playwright');
const fs = require('fs');

const BOARDS = [
  { name: 'Pain Relief & Recovery', description: 'Science-backed pain relief devices: back stretchers, TENS units, red light therapy, posture correctors & more' },
  { name: 'Better Sleep', description: 'Sleep aid devices, therapy mattresses & tools for deeper, more restful sleep' },
  { name: 'Oral Care & Dental Health', description: 'Water flossers, oral irrigators & dental wellness essentials' },
  { name: 'Home Health & Wellness', description: 'Air quality monitors, wellness products & healthy home essentials' },
  { name: 'Healthy Kitchen', description: 'Portable blenders, juicers & nutrition tools for healthy living' },
];

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });

  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    window.chrome = { runtime: {} };
  });

  const page = await context.newPage();

  // Login
  console.log('=== Logging in ===');
  await page.goto('https://www.pinterest.com/login/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);

  const emailInput = await page.$('input[type="email"]');
  await emailInput.fill(process.env.PIN_EMAIL);
  const pwdInput = await page.$('input[type="password"]');
  await pwdInput.fill(process.env.PIN_PASSWORD);
  await page.$('button[type="submit"]').then(b => b.click());

  await page.waitForURL('**/homefeed**', { timeout: 20000 }).catch(() =>
    page.waitForURL('**/business/**', { timeout: 10000 }).catch(() => {})
  );
  await page.waitForTimeout(3000);
  console.log('Logged in. URL:', page.url());

  // Navigate to boards page
  console.log('=== Creating Boards ===');
  await page.goto('https://www.pinterest.com/ideas/boards/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  // Try to find "Create board" button
  // Pinterest board creation: go to profile → Boards → Create
  await page.goto('https://www.pinterest.com/biosavvy/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'pinterest-profile.png', fullPage: false });
  console.log('Profile screenshot saved');

  // Click "Boards" tab
  const boardsTab = await page.$('text=Boards') || await page.$('[data-test-id="boards-tab"]');
  if (boardsTab) {
    await boardsTab.click();
    await page.waitForTimeout(2000);
    console.log('Clicked Boards tab');
  }

  // Create each board
  for (const board of BOARDS) {
    console.log(`\n--- Creating board: "${board.name}" ---`);

    // Look for "Create board" button
    let createBtn = await page.$('button:has-text("Create board")')
      || await page.$('[data-test-id="create-board-button"]')
      || await page.$('div:has-text("Create board")');

    if (!createBtn) {
      // Try the + button
      createBtn = await page.$('[data-test-id="board-creator"]')
        || await page.$('button:has-text("+")')
        || await page.$('a:has-text("Create board")');
    }

    if (createBtn) {
      await createBtn.click();
      await page.waitForTimeout(2000);
      console.log('Clicked create board button');
    } else {
      console.log('Create board button not found, trying alternative...');
      // Try navigating directly to create board
      await page.goto('https://www.pinterest.com/board/create/', { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);
    }

    // Fill board name
    const nameInput = await page.$('input[placeholder*="Name"]')
      || await page.$('input[placeholder*="name"]')
      || await page.$('input[name="boardName"]')
      || await page.$('input[data-test-id="board-name-input"]');

    if (nameInput) {
      await nameInput.fill(board.name);
      console.log('Board name filled');
    } else {
      console.log('Name input not found');
      await page.screenshot({ path: `pinterest-error-board-name.png` });
      continue;
    }

    // Fill description if there's a description field
    const descInput = await page.$('textarea[placeholder*="description"]')
      || await page.$('textarea[placeholder*="Description"]')
      || await page.$('textarea[data-test-id="board-description-input"]');

    if (descInput) {
      await descInput.fill(board.description);
      console.log('Description filled');
    }

    // Save/Create the board
    const saveBtn = await page.$('button:has-text("Create")')
      || await page.$('button:has-text("Save")')
      || await page.$('button[data-test-id="save-board-button"]')
      || await page.$('button[type="submit"]');

    if (saveBtn) {
      await saveBtn.click();
      console.log('Board saved!');
      await page.waitForTimeout(3000);
    } else {
      console.log('Save button not found');
    }

    await page.screenshot({ path: `pinterest-board-${board.name.replace(/\s+/g, '-').toLowerCase()}.png`, fullPage: false });
  }

  console.log('\n=== All boards done ===');
  await page.screenshot({ path: 'pinterest-boards-final.png', fullPage: false });

  await browser.close();
  console.log('Done');
})();
