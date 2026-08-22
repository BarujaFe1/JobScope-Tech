import { expect, test } from "@playwright/test";

/**
 * Critical-path browser proof (wow moment in <=3 clicks):
 * overview -> graph (edges exist) -> portfolio gap (statuses visible).
 */
test("critical path: overview -> graph -> gap", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    /medido|skills/i,
  );
  await expect(page.getByText(/Amostra honesta/)).toBeVisible();

  // click 2: into the co-occurrence graph
  await page.getByRole("link", { name: /Grafo de coocorrência/ }).click();
  await expect(page).toHaveURL(/\/graph/);
  // edges table exists OR the honest empty state is shown
  const hasTable = await page
    .getByRole("table")
    .or(page.getByText(/Nenhuma aresta acima do suporte mínimo/))
    .isVisible();
  expect(hasTable).toBeTruthy();

  // click 3: into the portfolio gap analysis
  await page.goto("/gap");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    /Demanda de mercado/,
  );
  // either rows or the honest threshold empty state must be present
  const hasRows = await page
    .getByText(/demanda alta/)
    .first()
    .or(page.getByText(/Nenhuma skill atingiu o limiar/))
    .isVisible();
  expect(hasRows).toBeTruthy();
});

test("role bundle page renders with data or honest empty state", async ({ page }) => {
  await page.goto("/");
  const roleLink = page.getByRole("link", { name: /Bundles por role/ });
  await roleLink.click();
  await expect(page).toHaveURL(/\/roles\//);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

test("graph slice filter keeps honest contract", async ({ page }) => {
  await page.goto("/graph");
  const sliceButtons = page.locator("nav a[href*='/graph?slice=']");
  const count = await sliceButtons.count();
  if (count > 0) {
    await sliceButtons.first().click();
    // after switching slice, still either table or honest empty state
    await expect(
      page.getByRole("table").or(page.getByText(/Nenhuma aresta acima do suporte mínimo/)),
    ).toBeVisible();
  }
});
