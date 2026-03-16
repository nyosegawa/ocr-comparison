import { Hono } from "hono";
import { cors } from "hono/cors";
import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";

export function createApp(resultsDir: string, uploadsDir: string) {
  const app = new Hono();

  app.use("*", cors());

  // List all result files
  app.get("/api/results", async (c) => {
    const files = (await readdir(resultsDir))
      .filter((f) => f.startsWith("eval_") && f.endsWith(".json"))
      .sort()
      .reverse();
    return c.json(files);
  });

  // Get a specific result file
  app.get("/api/results/:filename", async (c) => {
    const filename = c.req.param("filename");
    if (!filename.startsWith("eval_") || !filename.endsWith(".json")) {
      return c.json({ error: "Invalid filename" }, 400);
    }
    const filepath = path.join(resultsDir, filename);
    try {
      const data = await readFile(filepath, "utf-8");
      return c.json(JSON.parse(data));
    } catch {
      return c.json({ error: "Not found" }, 404);
    }
  });

  // Get all results merged
  app.get("/api/results-all", async (c) => {
    const files = (await readdir(resultsDir))
      .filter((f) => f.startsWith("eval_") && f.endsWith(".json"))
      .sort();

    const modelMap = new Map<string, unknown>();
    let nImages = 0;
    let totalGtChars = 0;

    for (const f of files) {
      const raw = await readFile(path.join(resultsDir, f), "utf-8");
      const data = JSON.parse(raw);
      nImages = Math.max(nImages, data.n_images ?? 0);
      totalGtChars = Math.max(totalGtChars, data.total_gt_chars ?? 0);
      for (const m of data.models ?? []) {
        // Later file wins (files are sorted chronologically)
        modelMap.set((m as { model: string }).model, m);
      }
    }

    return c.json({ n_images: nImages, total_gt_chars: totalGtChars, models: [...modelMap.values()] });
  });

  // Serve uploaded images
  app.get("/api/images/:filename", async (c) => {
    const filename = c.req.param("filename");
    if (!/^img_\d+(?:_original)?\.\w+$/.test(filename)) {
      return c.json({ error: "Invalid filename" }, 400);
    }
    const filepath = path.join(uploadsDir, filename);
    try {
      await stat(filepath);
      const data = await readFile(filepath);
      const ext = path.extname(filename).toLowerCase();
      const mime =
        ext === ".png" ? "image/png" :
        ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" :
        "application/octet-stream";
      return new Response(data, { headers: { "Content-Type": mime, "Cache-Control": "public, max-age=86400" } });
    } catch {
      return c.json({ error: "Not found" }, 404);
    }
  });

  return app;
}
