import { serve } from "@hono/node-server";
import path from "node:path";
import { createApp, ensureDirs, resolveDirs } from "./app.js";

const ROOT = path.resolve(import.meta.dirname, "../..");
const dirs = resolveDirs(ROOT);

await ensureDirs(dirs);

const app = createApp(dirs);

const port = 3001;
console.log(`Server running on http://0.0.0.0:${port}`);
serve({ fetch: app.fetch, hostname: "0.0.0.0", port });
