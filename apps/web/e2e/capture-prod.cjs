/* Capture production screenshots for README/LinkedIn evidence. */
const { chromium } = require("@playwright/test");

const BASE = process.env.PROD_URL || "https://jobscope-signal-graph-baruja-fe.vercel.app";
const OUT = process.argv[2] || "assets/screenshots";

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const shots = [
    ["", "01-overview.png"],
    ["/graph", "02-graph.png"],
    ["/gap", "03-gap.png"],
    ["/roles/data_analyst", "04-role-bundle.png"],
  ];
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });

  for (const [route, file] of shots) {
    await page.goto(BASE + route, { waitUntil: "networkidle" });
    await page.waitForTimeout(600);
    await page.screenshot({ path: `${OUT}/${file}`, fullPage: true });
    console.log(`captured ${file}`);
  }

  console.log(errors.length ? `CONSOLE ERRORS:\n${errors.join("\n")}` : "console: no errors");
  await browser.close();
  if (errors.length) process.exit(1);
})();
