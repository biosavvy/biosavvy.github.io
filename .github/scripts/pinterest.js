const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
    ]
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });

  // Stealth: remove webdriver flag
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    window.chrome = { runtime: {} };
  });

  const page = await context.newPage();

  console.log('Navigating to Pinterest login...');
  try {
    await page.goto('https://www.pinterest.com/login/', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });
    console.log('Page loaded (domcontentloaded)');
  } catch (e) {
    console.log('Navigation issue (continuing anyway):', e.message);
  }

  // Wait for page to stabilize
  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'pinterest-01-login-page.png', fullPage: false });
  console.log('Screenshot 1: login page saved');
  console.log('Current URL:', page.url());

  // Try multiple selectors for email
  let emailInput = null;
  const emailSelectors = [
    'input[name="id"]',
    'input[type="email"]',
    'input[placeholder*="Email"]',
    'input[placeholder*="email"]',
    'input[data-test-id="register-email-input"]',
    '#email',
  ];
  for (const sel of emailSelectors) {
    try {
      emailInput = await page.$(sel);
      if (emailInput) { console.log(`Email found via: ${sel}`); break; }
    } catch (_) {}
  }

  if (emailInput) {
    await emailInput.click();
    await page.waitForTimeout(500);
    await emailInput.fill(process.env.PIN_EMAIL);
    console.log('Email filled');
  } else {
    console.log('Email input not found, dumping page HTML snippet...');
    const html = await page.content();
    console.log('Page title:', await page.title());
    console.log('HTML length:', html.length);
    // Save for debugging
    require('fs').writeFileSync('pinterest-debug.html', html);
    await page.screenshot({ path: 'pinterest-error-no-email.png' });
    await browser.close();
    process.exit(1);
  }

  // Try multiple selectors for password
  let pwdInput = null;
  const pwdSelectors = [
    'input[name="password"]',
    'input[type="password"]',
    'input[placeholder*="Password"]',
    'input[placeholder*="password"]',
    '#password',
  ];
  for (const sel of pwdSelectors) {
    try {
      pwdInput = await page.$(sel);
      if (pwdInput) { console.log(`Password found via: ${sel}`); break; }
    } catch (_) {}
  }

  if (pwdInput) {
    await pwdInput.fill(process.env.PIN_PASSWORD);
    console.log('Password filled');
  } else {
    console.log('Password input not found');
    await page.screenshot({ path: 'pinterest-error-no-password.png' });
    await browser.close();
    process.exit(1);
  }

  // Click login button
  let loginBtn = null;
  const btnSelectors = [
    'button[type="submit"]',
    '[data-testid="signup-login-button"]',
    'button:has-text("Log in")',
    'button:has-text("Log in")',
    'button div:has-text("Log in") >> ..',
    '[data-test-id="register-password-submit"]',
  ];
  for (const sel of btnSelectors) {
    try {
      loginBtn = await page.$(sel);
      if (loginBtn) { console.log(`Login button found via: ${sel}`); break; }
    } catch (_) {}
  }

  if (loginBtn) {
    await loginBtn.click();
    console.log('Login button clicked');
  } else {
    await page.keyboard.press('Enter');
    console.log('Pressed Enter to submit');
  }

  // Wait for SPA navigation
  try {
    await page.waitForURL('**/homefeed**', { timeout: 15000 });
    console.log('Navigated to homefeed!');
  } catch (_) {
    try {
      await page.waitForURL('**/login**', { timeout: 5000 });
      console.log('Still on login page (may need verification)');
    } catch (_) {
      console.log('URL change check done');
    }
  }

  await page.waitForTimeout(5000);
  await page.screenshot({ path: 'pinterest-02-after-login.png', fullPage: false });
  console.log('Screenshot 2: after login saved');
  console.log('Current URL:', page.url());
  console.log('Page title:', await page.title());

  await browser.close();
  console.log('Done');
})();
