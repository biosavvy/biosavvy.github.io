const { chromium } = require('playwright');

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

  // === STEP 1: Login ===
  console.log('Logging in...');
  await page.goto('https://www.pinterest.com/login/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);

  await page.fill('input[type="email"]', process.env.PIN_EMAIL);
  await page.fill('input[type="password"]', process.env.PIN_PASSWORD);
  await page.click('button[type="submit"]');

  await page.waitForURL('**/homefeed**', { timeout: 20000 }).catch(() =>
    page.waitForURL('**/business/**', { timeout: 10000 }).catch(() => {})
  );
  await page.waitForTimeout(3000);
  console.log('Logged in. URL:', page.url());

  // === STEP 2: Navigate to profile and explore ===
  console.log('\n=== Exploring profile page ===');
  await page.goto('https://www.pinterest.com/biosavvy/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'pinterest-profile.png', fullPage: false });

  // Dump all button/role info
  const buttons = await page.$$eval('button, [role="button"], a', els =>
    els.filter(e => e.offsetParent !== null).map(e => ({
      text: e.textContent.trim().substring(0, 50),
      aria: e.getAttribute('aria-label') || '',
      dataTest: e.getAttribute('data-test-id') || '',
      tag: e.tagName
    })).filter(b => b.text || b.aria)
  );
  console.log('Interactive elements:', JSON.stringify(buttons, null, 2));

  // Try clicking "Boards" tab
  const boardsTab = await page.$('text=Boards') || await page.$('text=板块');
  if (boardsTab) {
    await boardsTab.click();
    await page.waitForTimeout(3000);
    console.log('Clicked Boards tab');
    await page.screenshot({ path: 'pinterest-boards-tab.png', fullPage: false });
  }

  // Dump elements on boards page
  const buttons2 = await page.$$eval('button, [role="button"], a', els =>
    els.filter(e => e.offsetParent !== null).map(e => ({
      text: e.textContent.trim().substring(0, 50),
      aria: e.getAttribute('aria-label') || '',
      dataTest: e.getAttribute('data-test-id') || '',
      tag: e.tagName
    })).filter(b => b.text || b.aria)
  );
  console.log('After boards tab:', JSON.stringify(buttons2, null, 2));

  // === STEP 3: Create boards via /board/create/ ===
  console.log('\n=== Creating boards ===');
  for (const board of BOARDS) {
    console.log(`\n--- "${board.name}" ---`);

    try {
      await page.goto('https://www.pinterest.com/board/create/', {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });
      await page.waitForTimeout(5000);
      await page.screenshot({ path: `pinterest-create-${board.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}.png`, fullPage: false });

      // Dump inputs
      const inputs = await page.$$eval('input, textarea', els =>
        els.map(e => ({
          type: e.type || e.tagName,
          placeholder: e.placeholder || '',
          name: e.name || '',
          visible: e.offsetParent !== null
        }))
      );
      console.log('Inputs found:', JSON.stringify(inputs));

      // Fill name
      const nameInputs = await page.$$('input[type="text"], input:not([type]), input[placeholder]');
      for (const inp of nameInputs) {
        const vis = await inp.isVisible();
        if (vis) {
          await inp.fill(board.name);
          console.log('  Name filled in input');
          break;
        }
      }

      // Fill description
      const textareas = await page.$$('textarea');
      for (const ta of textareas) {
        const vis = await ta.isVisible();
        if (vis) {
          await ta.fill(board.description);
          console.log('  Description filled');
          break;
        }
      }

      // Toggle privacy to public if needed
      try {
        const secretToggle = await page.$('[data-test-id="keep-board-secret"]');
        if (secretToggle) {
          const checked = await secretToggle.isChecked();
          if (checked) await secretToggle.click();
        }
      } catch (_) {}

      // Find and click Create/Next button
      const createBtns = await page.$$('button');
      for (const btn of createBtns) {
        const text = await btn.textContent().catch(() => '');
        if (text.includes('Create') || text.includes('Next') || text.includes('保存') || text.includes('创建')) {
          const vis = await btn.isVisible();
          if (vis) {
            await btn.click();
            console.log('  Clicked:', text.trim().substring(0, 30));
            break;
          }
        }
      }

      await page.waitForTimeout(4000);
      await page.screenshot({ path: `pinterest-after-${board.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}.png`, fullPage: false });
      console.log('  Done');

    } catch (e) {
      console.log('  Error:', e.message.substring(0, 100));
    }
  }

  // === STEP 4: Final profile screenshot ===
  console.log('\n=== Final state ===');
  await page.goto('https://www.pinterest.com/biosavvy/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'pinterest-profile-final.png', fullPage: false });

  await browser.close();
  console.log('Done');
})();
