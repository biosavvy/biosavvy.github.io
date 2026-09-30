const { chromium } = require('playwright');

const BOARDS = [
  { name: 'Pain Relief & Recovery', description: 'Science-backed pain relief devices: back stretchers, TENS units, red light therapy, posture correctors & more' },
  { name: 'Better Sleep', description: 'Sleep aid devices, therapy mattresses & tools for deeper, more restful sleep' },
  { name: 'Oral Care & Dental Health', description: 'Water flossers, oral irrigators & dental wellness essentials' },
  { name: 'Home Health & Wellness', description: 'Air quality monitors, wellness products & healthy home essentials' },
  { name: 'Healthy Kitchen', description: 'Portable blenders, juicers & nutrition tools for healthy living' },
];

async function login(page) {
  console.log('Logging in...');
  await page.goto('https://www.pinterest.com/login/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);

  const emailInput = await page.$('input[type="email"]');
  await emailInput.fill(process.env.PIN_EMAIL);
  const pwdInput = await page.$('input[type="password"]');
  await pwdInput.fill(process.env.PIN_PASSWORD);
  await page.click('button[type="submit"]');

  await page.waitForURL('**/homefeed**', { timeout: 20000 }).catch(() =>
    page.waitForURL('**/business/**', { timeout: 10000 }).catch(() => {})
  );
  await page.waitForTimeout(3000);
  console.log('Logged in. URL:', page.url());
}

async function createBoardViaNav(page, board) {
  // Navigate to the "Create" page via URL
  console.log(`Creating board: "${board.name}"`);

  // Try going directly to board create URL
  await page.goto('https://www.pinterest.com/board/create/', {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  }).catch(() => console.log('Direct URL failed, trying nav...'));

  await page.waitForTimeout(3000);
  await page.screenshot({ path: `pinterest-create-board-page.png`, fullPage: false });

  // Look for name input
  const nameInput = await page.$('input[placeholder*="Name"]')
    || await page.$('input[placeholder*="Board name"]')
    || await page.$('input[type="text"]')
    || (await page.$$('input')).find(i => true);

  if (nameInput) {
    // Find the right input (first text input that's visible)
    const inputs = await page.$$('input[type="text"], input[placeholder], input:not([type])');
    let targetInput = null;
    for (const inp of inputs) {
      const isVisible = await inp.isVisible().catch(() => false);
      if (isVisible) { targetInput = inp; break; }
    }
    if (!targetInput) targetInput = inputs[0];

    await targetInput.fill(board.name);
    console.log('  Name filled');
  }

  // Look for description textarea
  const descInput = await page.$('textarea');
  if (descInput) {
    await descInput.fill(board.description);
    console.log('  Description filled');
  }

  // Look for privacy toggle - set to public
  const privacyToggle = await page.$('[data-test-id="keep-board-secret"]');
  if (privacyToggle) {
    const isChecked = await privacyToggle.isChecked().catch(() => false);
    if (isChecked) {
      await privacyToggle.click();
      console.log('  Set to public');
    }
  }

  // Click Create/Save
  const createBtn = await page.$('button:has-text("Create")')
    || await page.$('button:has-text("Next")')
    || await page.$('[data-test-id="board-creator-save-button"]');

  if (createBtn) {
    await createBtn.click();
    console.log('  Create button clicked');
    await page.waitForTimeout(3000);
  }

  await page.screenshot({ path: `pinterest-board-done-${board.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}.png`, fullPage: false });
}

async function createBoardViaPlusButton(page, board) {
  // Go to homefeed and use the + button
  await page.goto('https://www.pinterest.com/homefeed/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  // Look for + button (create button in top nav)
  const plusBtn = await page.$('[data-test-id="create-button"]')
    || await page.$('button[aria-label*="Create"]')
    || await page.$('div[aria-label*="Create"]');

  if (plusBtn) {
    await plusBtn.click();
    await page.waitForTimeout(2000);

    // Look for "Board" option in dropdown
    const boardOption = await page.$('text=Board')
      || await page.$('[data-test-id="board-creator"]');
    if (boardOption) {
      await boardOption.click();
      await page.waitForTimeout(2000);
    }
  }

  // Fill name
  const nameInput = await page.$('input[placeholder*="Name"]') || await page.$('input[type="text"]');
  if (nameInput) {
    await nameInput.fill(board.name);
    console.log('  Name filled');
  }

  // Fill description
  const descInput = await page.$('textarea');
  if (descInput) {
    await descInput.fill(board.description);
    console.log('  Description filled');
  }

  // Create
  const createBtn = await page.$('button:has-text("Create")');
  if (createBtn) {
    await createBtn.click();
    console.log('  Created');
    await page.waitForTimeout(3000);
  }
}

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
  await login(page);

  // First, try to explore the page structure
  console.log('\n=== Exploring page structure ===');
  await page.goto('https://www.pinterest.com/homefeed/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'pinterest-homefeed.png', fullPage: false });

  // Try to find all interactive elements
  const snapshot = await page.accessibility.snapshot();
  const createRelated = [];
  function findCreate(node) {
    if (node.name && (node.name.toLowerCase().includes('create') || node.name.includes('+'))) {
      createRelated.push({ name: node.name, role: node.role });
    }
    if (node.children) node.children.forEach(findCreate);
  }
  if (snapshot) findCreate(snapshot);
  console.log('Create-related elements:', JSON.stringify(createRelated));

  // Create boards
  console.log('\n=== Creating Boards ===');
  for (const board of BOARDS) {
    try {
      await createBoardViaNav(page, board);
    } catch (e) {
      console.log(`Error with ${board.name}: ${e.message}`);
      // Retry with alternative method
      try {
        await createBoardViaPlusButton(page, board);
      } catch (e2) {
        console.log(`Alternative also failed: ${e2.message}`);
      }
    }
  }

  console.log('\n=== Final screenshot ===');
  await page.goto('https://www.pinterest.com/biosavvy/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'pinterest-profile-final.png', fullPage: false });

  await browser.close();
  console.log('Done');
})();
