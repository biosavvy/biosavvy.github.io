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
  console.log('Step 1: Navigate to login page...');
  await page.goto('https://www.pinterest.com/login/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '01-login-page.png', fullPage: false });

  // Close any modals first (signup modal, cookie banner, etc.)
  console.log('Checking for modals/popups...');
  const closeButtons = await page.$$('button[aria-label="Close"], button[aria-label="close"], [data-test-id="close-button"], .modalClose, button:has-text("×"), button:has-text("✕")');
  for (const btn of closeButtons) {
    try {
      if (await btn.isVisible()) {
        await btn.click();
        console.log('Closed a modal/popup');
        await page.waitForTimeout(500);
      }
    } catch (e) {}
  }

  await page.screenshot({ path: '02-after-close-modals.png', fullPage: false });

  // Fill email
  const emailSelectors = ['input[name="id"]', 'input[type="email"]', 'input[placeholder*="Email"]', 'input[placeholder*="email"]'];
  let emailInput = null;
  for (const sel of emailSelectors) {
    try {
      emailInput = await page.$(sel);
      if (emailInput && await emailInput.isVisible()) {
        console.log('Email input found via:', sel);
        break;
      }
    } catch (e) { emailInput = null; }
  }

  if (!emailInput) {
    console.log('ERROR: Could not find email input');
    await browser.close();
    process.exit(1);
  }

  await emailInput.fill(process.env.PIN_EMAIL);
  console.log('Email filled:', process.env.PIN_EMAIL);

  // Fill password
  const pwdSelectors = ['input[name="password"]', 'input[type="password"]', 'input[placeholder*="Password"]'];
  let pwdInput = null;
  for (const sel of pwdSelectors) {
    try {
      pwdInput = await page.$(sel);
      if (pwdInput && await pwdInput.isVisible()) {
        console.log('Password input found via:', sel);
        break;
      }
    } catch (e) { pwdInput = null; }
  }

  if (!pwdInput) {
    console.log('ERROR: Could not find password input');
    await page.screenshot({ path: '02-error-no-pwd.png', fullPage: false });
    await browser.close();
    process.exit(1);
  }

  await pwdInput.fill(process.env.PIN_PASSWORD);
  console.log('Password filled');

  // Click submit button
  let submitBtn = null;
  const btnSelectors = ['button[type="submit"]', '[data-testid="signup-login-button"]', '[data-test-id="register-password-submit"]', 'button:has-text("Log in")', 'button:has-text("Log in")'];
  for (const sel of btnSelectors) {
    try {
      submitBtn = await page.$(sel);
      if (submitBtn && await submitBtn.isVisible()) {
        console.log('Submit button found via:', sel);
        break;
      }
    } catch (e) { submitBtn = null; }
  }

  if (submitBtn) {
    await submitBtn.click();
    console.log('Submit button clicked');
  } else {
    await page.keyboard.press('Enter');
    console.log('Pressed Enter to submit');
  }

  // Wait for login to complete - check URL changes
  console.log('Waiting for login to complete...');
  let loginSuccess = false;

  // Wait up to 20 seconds for navigation away from login page
  for (let i = 0; i < 20; i++) {
    await page.waitForTimeout(1000);
    const url = page.url();
    if (!url.includes('/login') && !url.includes('/signup')) {
      console.log('Navigation detected! URL:', url);
      loginSuccess = true;
      break;
    }
    if (i % 5 === 0) {
      console.log(`Still waiting... (${i}s) URL:`, url);
    }
  }

  await page.waitForTimeout(3000);
  await page.screenshot({ path: '03-after-login.png', fullPage: false });
  console.log('Final URL:', page.url());

  if (!loginSuccess) {
    // Check for error messages
    const errorMsg = await page.$eval('[data-test-id="toast-primary-text"], .error, [class*="error"]', el => el.textContent).catch(() => null);
    if (errorMsg) console.log('Error message:', errorMsg);

    // Check for CAPTCHA
    const hasCaptcha = await page.$('.g-recaptcha, [data-recaptcha], iframe[src*="recaptcha"], iframe[src*="hcaptcha"]').catch(() => null);
    if (hasCaptcha) console.log('CAPTCHA detected!');

    console.log('Login failed!');
    await browser.close();
    process.exit(1);
  }

  console.log('Login successful!');

  // === STEP 2: Navigate to business hub ===
  console.log('\nStep 2: Navigate to business hub...');
  await page.goto('https://www.pinterest.com/business/hub/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '04-business-hub.png', fullPage: false });

  // === STEP 3: Create boards ===
  console.log('\nStep 3: Creating boards...');
  let createdCount = 0;

  for (const board of BOARDS) {
    console.log(`\n--- Creating: "${board.name}" ---`);

    try {
      await page.goto('https://www.pinterest.com/board/create/', {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });
      await page.waitForTimeout(5000);

      // Check if login session expired
      const currentUrl = page.url();
      if (currentUrl.includes('/login')) {
        console.log('ERROR: Login session expired at board creation');
        await page.screenshot({ path: `05-error-${board.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}.png`, fullPage: false });
        break;
      }

      await page.screenshot({ path: `05-create-${board.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}-before.png`, fullPage: false });

      // Find and fill name input
      const inputs = await page.$$eval('input, textarea', els =>
        els.map(e => ({
          type: e.type || '',
          placeholder: e.placeholder || '',
          name: e.name || '',
          id: e.id || '',
          visible: e.offsetParent !== null || e.getBoundingClientRect().height > 0
        }))
      );
      console.log('Inputs:', JSON.stringify(inputs));

      // Fill name - try multiple selectors
      let nameFilled = false;
      const nameSelectors = [
        'input[type="text"]:not([name="searchBoxInput"])',
        'input[placeholder*="Name"]',
        'input[placeholder*="name"]',
        'input[placeholder*="board"]',
        'input[placeholder*="Board"]',
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
