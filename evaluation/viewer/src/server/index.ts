import { serve } from "@hono/node-server";
import path from "node:path";
import { createApp } from "./app.js";

const RESULTS_DIR = path.resolve(import.meta.dirname, "../../../results");
const UPLOADS_DIR = path.resolve(import.meta.dirname, "../../../../annotation/uploads");

const app = createApp(RESULTS_DIR, UPLOADS_DIR);

const port = 3002;
console.log(`Viewer server running on http://0.0.0.0:${port}`);
serve({ fetch: app.fetch, hostname: "0.0.0.0", port });
