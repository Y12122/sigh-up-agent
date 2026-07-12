import { expect, test } from "@playwright/test";

test("employee reviews a risky registration case", async ({ page }) => {
  await page.goto("/");
  await page.getByText("HK-20260712-001").click();
  await expect(page.getByRole("heading", { name: "恒星贸易有限公司" })).toBeVisible();
  await expect(page.getByText("OCR 置信度 72%")).toBeVisible();
  await expect(page.getByRole("button", { name: /退回补件/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /复核通过/ })).toBeVisible();
});

test("customer reviews and confirms the current registration version", async ({ page }) => {
  await page.goto("/");
  await page.getByText("客户上传端").click();
  await expect(page.getByText("还需补交 2 项")).toBeVisible();
  await page.getByRole("button", { name: "保存并继续" }).click();
  const confirm = page.getByRole("button", { name: /确认注册信息/ });
  await expect(confirm).toBeDisabled();
  await page.getByRole("checkbox").check();
  await confirm.click();
  await expect(page.getByText("注册信息已确认")).toBeVisible();
});

test("customer flow fits the mobile viewport", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "mobile", "mobile-only layout check");
  await page.goto("/");
  await page.getByText("客户上传端").click();
  await expect(page.getByRole("heading", { name: "材料上传" })).toBeVisible();
  const widths = await page.locator("html").evaluate((element) => ({ scroll: element.scrollWidth, client: element.clientWidth }));
  expect(widths.scroll).toBe(widths.client);
  await page.screenshot({ path: "test-results/mobile-customer.png", fullPage: true });
});
