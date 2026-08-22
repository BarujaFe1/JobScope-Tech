import { copyFileSync, existsSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const webRoot = resolve(here, "..");
const repoData = resolve(webRoot, "../../data/public/market_snapshot.json");
const target = join(webRoot, "src", "data", "market_snapshot.json");

if (!existsSync(repoData)) {
  console.error(`snapshot source not found: ${repoData}`);
  process.exit(1);
}

copyFileSync(repoData, target);
const { size, mtime } = statSync(repoData);
console.log(`synced market_snapshot.json (${size} bytes, generated ${mtime.toISOString()})`);
