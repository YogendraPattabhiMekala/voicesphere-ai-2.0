import { expect, test, type Page } from '@playwright/test';

const sections = [
  { label: 'Overview', path: '/' },
  { label: 'AI agents', path: '/ai-agents' },
  { label: 'Voice playground', path: '/voice-playground' },
  { label: 'Customers', path: '/customers' },
  { label: 'Orders', path: '/orders' },
  { label: 'Support tickets', path: '/support-tickets' },
  { label: 'Audit log', path: '/audit-log' },
];

async function installApiMocks(page: Page) {
  await page.addInitScript(() => localStorage.setItem('vs-token', 'navigation-test-token'));
  await page.route('**/api/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname;
    let body: unknown = {};
    if (pathname === '/api/auth/me') {
      body = {
        id: 7,
        name: 'Test Supervisor',
        email: 'supervisor@example.test',
        role: 'supervisor',
        organization_id: 1,
      };
    } else if (pathname === '/api/dashboard') {
      body = {
        organization: 'Northstar Retail',
        metrics: { customers: 2, orders: 2, open_tickets: 0, active_conversations: 0 },
        voice_mode: 'mock',
        demo_data: true,
      };
    } else if (pathname === '/api/agents' || pathname === '/api/customers' ||
               pathname === '/api/orders' || pathname === '/api/tickets' ||
               pathname === '/api/audit') {
      body = [];
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });
  });
}

test('all seven sections open directly and persist after reload', async ({ page }) => {
  await installApiMocks(page);
  for (const section of sections) {
    await page.goto(section.path);
    await expect(page).toHaveURL(new RegExp(`${section.path.replaceAll('/', '\\/')}$`));
    await expect(page.getByRole('heading', { level: 1, name: section.label, exact: true })).toBeVisible();
    await expect(page.locator('.sidebar nav').getByRole('button', { name: new RegExp(section.label, 'i') })).toHaveClass(/selected/);

    await page.reload();
    await expect(page).toHaveURL(new RegExp(`${section.path.replaceAll('/', '\\/')}$`));
    await expect(page.getByRole('heading', { level: 1, name: section.label, exact: true })).toBeVisible();
  }
});

test('sidebar navigation updates URLs and browser Back/Forward restores sections', async ({ page }) => {
  await installApiMocks(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 1, name: 'Overview', exact: true })).toBeVisible();

  for (const section of sections.slice(1)) {
    await page.locator('.sidebar nav').getByRole('button', { name: new RegExp(section.label, 'i') }).click();
    await expect(page).toHaveURL(new RegExp(`${section.path.replaceAll('/', '\\/')}$`));
    await expect(page.getByRole('heading', { level: 1, name: section.label, exact: true })).toBeVisible();
  }

  for (const section of [...sections].reverse().slice(1)) {
    await page.goBack();
    await expect(page.getByRole('heading', { level: 1, name: section.label, exact: true })).toBeVisible();
  }
  for (const section of sections.slice(1)) {
    await page.goForward();
    await expect(page.getByRole('heading', { level: 1, name: section.label, exact: true })).toBeVisible();
  }
});
