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

  // === STEP 1: Login via homepage modal ===
  console.log('Step 1: Navigate to homepage and login...');
  await page.goto('https://www.pinterest.com/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '01-homepage.png', fullPage: false });

  // Click "I already have an account" or "Log in" button
  let loginClicked = false;
  try {
    const alreadyHaveAccountBtn = await page.$('button:has-text("I already have an account")');
    if (alreadyHaveAccountBtn) {
      await alreadyHaveAccountBtn.click();
      console.log('Clicked "I already have an account"');
      loginClicked = true;
    }
  } catch (e) { console.log('Error clicking already have account:', e.message); }

  if (!loginClicked) {
    try {
      const loginBtn = await page.$('button:has-text("Log in")');
      if (loginBtn) {
        await loginBtn.click();
        console.log('Clicked "Log in"');
        loginClicked = true;
      }
    } catch (e) { console.log('Error clicking log in:', e.message); }
  }

  if (!loginClicked) {
    console.log('ERROR: Could not find login button');
    await browser.close();
    process.exit(1);
  }

  await page.waitForTimeout(2000);
  await page.screenshot({ path: '02-login-modal.png', fullPage: false });

  // Fill email and password in modal
  const emailInput = await page.$('input[placeholder="Email"], input[name="email"], input[type="email"]');
  const passwordInput = await page.$('input[placeholder="Password"], input[name="password"], input[type="password"]');

  if (!emailInput || !passwordInput) {
    console.log('ERROR: Could not find email/password inputs');
    console.log('Page URL:', page.url());
    await page.screenshot({ path: '02-error-no-inputs.png', fullPage: false });
    const html = await page.content();
    require('fs').writeFileSync('debug-login.html', html);
    await browser.close();
    process.exit(1);
  }

  await emailInput.fill(process.env.PIN_EMAIL);
  await passwordInput.fill(process.env.PIN_PASSWORD);
  console.log('Email and password filled');

  // Click Log in button in modal
  const submitBtn = await page.$('button:has-text("Log in")');
  if (submitBtn) {
    await submitBtn.click();
    console.log('Clicked Log in button');
  } else {
    await page.keyboard.press('Enter');
    console.log('Pressed Enter to submit');
  }

  // Wait for login to complete
  console.log('Waiting for login...');
  await page.waitForTimeout(8000);
  await page.screenshot({ path: '03-after-login.png', fullPage: false });
  console.log('URL after login:', page.url());

  // Check if still on login page
  const isOnLogin = page.url().includes('/login') || await page.$('input[placeholder="Email"]') !== null;
  if (isOnLogin) {
    console.log('WARNING: Still on login page. Login may have failed.');
    // Check for error messages
    const errorMsg = await page.$eval('[data-test-id="toast-primary-text"], .error, [class*="error"]', el => el.textContent).catch(() => null);
    if (errorMsg) console.log('Error message:', errorMsg);

    // Try CAPTCHA check
    const hasCaptcha = await page.$('.g-recaptcha, [data-recaptcha], iframe[src*="recaptcha"]').catch(() => null);
    if (hasCaptcha) console.log('CAPTCHA detected!');

    await page.screenshot({ path: '03-login-failed.png', fullPage: false });
    await browser.close();
    process.exit(1);
  }

  console.log('Login successful!');

  // === STEP 2: Navigate to business hub to verify ===
  console.log('\nStep 2: Check business hub...');
  await page.goto('https://www.pinterest.com/business/hub/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '04-business-hub.png', fullPage: false });

  // === STEP 3: Create boards ===
  console.log('\nStep 3: Creating boards...');
  let createdCount = 0;

  for (const board of BOARDS) {
    console.log(`\n--- Creating: "${board.name}" ---`);

    try {
      // Navigate to board creation URL
      await page.goto('https://www.pinterest.com/board/create/', {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });
      await page.waitForTimeout(5000);
      await page.screenshot({ path: `05-create-${board.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}-before.png`, fullPage: false });

      // Check we're on the create page, not login
      const currentUrl = page.url();
      if (currentUrl.includes('/login') || currentUrl.includes('pinterest.com/')) {
        // Check if login modal appeared
        const loginModal = await page.$('text=Welcome to Pinterest');
        if (loginModal) {
          console.log('Login session expired! Re-logging in...');
          await page.screenshot({ path: '05-login-expired.png', fullPage: false });
          await browser.close();
          process.exit(1);
        }
      }

      // Find and fill name input
      const inputs = await page.$$eval('input, textarea', els =>
        els.map(e => ({
          type: e.type || '',
          placeholder: e.placeholder || '',
          name: e.name || '',
          id: e.id || '',
          tagName: e.tagName,
          visible: e.offsetParent !== null || e.getBoundingClientRect().height > 0
        }))
      );
      console.log('Inputs:', JSON.stringify(inputs));

      // Fill name
      let nameFilled = false;
      const nameSelectors = [
        'input[type="text"]:not([name="searchBoxInput"])',
        'input[placeholder*="Name"]',
        'input[placeholder*="name"]',
        'input[placeholder*="board"]',
        'input[placeholder*="Board"]',
        'input[name="boardName"]',
      ];

      for (const sel of nameSelectors) {
        try {
          const inp = await page.$(sel);
          if (inp && await inp.isVisible()) {
            await inp.fill(board.name);
            console.log('Name filled via:', sel);
            nameFilled = true;
            break;
          }
        } catch (e) {}
      }

      if (!nameFilled) {
        // Fallback: try all visible text inputs
        const allInputs = await page.$$('input[type="text"], input:not([type])');
        for (const inp of allInputs) {
          const vis = await inp.isVisible();
          if (vis) {
            const placeholder = await inp.getAttribute('placeholder').catch(() => '');
            if (!placeholder.includes('Search') && !placeholder.includes('search')) {
              await inp.fill(board.name);
              console.log('Name filled in fallback input, placeholder:', placeholder);
              nameFilled = true;
              break;
            }
          }
        }
      }

      if (!nameFilled) {
        console.log('WARNING: Could not fill name input');
      }

      // Fill description
      const textarea = await page.$('textarea');
      if (textarea && await textarea.isVisible()) {
        await textarea.fill(board.description);
        console.log('Description filled');
      }

      // Click Create/Save button
      const createBtns = await page.$$('button');
      for (const btn of createBtns) {
        const text = await btn.textContent().catch(() => '');
        if ((text.includes('Create') || text.includes('Save') || text.includes('Next') ||
             text.includes('保存') || text.includes('创建')) && text.trim().length < 20) {
          const vis = await btn.isVisible();
          if (vis) {
            await btn.click();
            console.log('Clicked button:', text.trim());
            break;
          }
        }
      }

      await page.waitForTimeout(5000);
      await page.screenshot({ path: `06-create-${board.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}-after.png`, fullPage: false });
      createdCount++;
      console.log(`Board "${board.name}" done (${createdCount}/${BOARDS.length})`);

    } catch (e) {
      console.log('Error creating board:', e.message.substring(0, 100));
    }
  }

  // === STEP 4: Final check ===
  console.log(`\nStep 4: Final check - created ${createdCount}/${BOARDS.length} boards`);
  await page.goto('https://www.pinterest.com/biosavvy/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '07-final-profile.png', fullPage: false });

  await browser.close();
  console.log('Done');
})();
