const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  console.log('Navigating to Pinterest login...');
  await page.goto('https://www.pinterest.com/login/', { waitUntil: 'networkidle', timeout: 30000 });
  await page.screenshot({ path: 'pinterest-01-login-page.png', fullPage: false });
  console.log('Screenshot 1: login page saved');

  // Fill email
  const emailInput = await page.$('input[name="id"]') || await page.$('input[type="email"]') || await page.$('input[placeholder*="Email"]');
  if (emailInput) {
    await emailInput.fill(process.env.PIN_EMAIL);
    console.log('Email filled');
  } else {
    console.log('Email input not found');
    await page.screenshot({ path: 'pinterest-error-no-email.png' });
    await browser.close();
    process.exit(1);
  }

  // Fill password
  const pwdInput = await page.$('input[name="password"]') || await page.$('input[type="password"]');
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
  const loginBtn = await page.$('button[type="submit"]') || await page.$('[data-testid="signup-login-button"]') || await page.$('button:has-text("Log in")');
  if (loginBtn) {
    await loginBtn.click();
    console.log('Login button clicked');
  } else {
    // Try pressing Enter
    await page.keyboard.press('Enter');
    console.log('Pressed Enter to submit');
  }

  // Wait for navigation or error
  try {
    await page.waitForNavigation({ waitUntil: 'networkidle', timeout: 15000 });
  } catch (e) {
    console.log('Navigation timeout (may be SPA):', e.message);
  }

  // Wait a bit for any redirect
  await page.waitForTimeout(3000);
  await page.screenshot({ path: 'pinterest-02-after-login.png', fullPage: false });
  console.log('Screenshot 2: after login saved');
  console.log('Current URL:', page.url());
  console.log('Page title:', await page.title());

  await browser.close();
  console.log('Done');
})();
