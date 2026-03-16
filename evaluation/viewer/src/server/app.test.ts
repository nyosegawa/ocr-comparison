import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createApp } from "./app.js";
import { mkdtemp, writeFile, mkdir, rm } from "node:fs/promises";
import path from "node:path";
import os from "node:os";

let tmpDir: string;
let resultsDir: string;
let uploadsDir: string;

beforeEach(async () => {
  tmpDir = await mkdtemp(path.join(os.tmpdir(), "viewer-test-"));
  resultsDir = path.join(tmpDir, "results");
  uploadsDir = path.join(tmpDir, "uploads");
  await mkdir(resultsDir, { recursive: true });
  await mkdir(uploadsDir, { recursive: true });
});

afterEach(async () => {
  await rm(tmpDir, { recursive: true, force: true });
});

function makeApp() {
  return createApp(resultsDir, uploadsDir);
}

describe("GET /api/results", () => {
  it("returns empty array when no results", async () => {
    const app = makeApp();
    const res = await app.request("/api/results");
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual([]);
  });

  it("returns eval files sorted reverse chronologically", async () => {
    await writeFile(path.join(resultsDir, "eval_20260101_000000.json"), "{}");
    await writeFile(path.join(resultsDir, "eval_20260102_000000.json"), "{}");
    await writeFile(path.join(resultsDir, "other_file.json"), "{}"); // should be excluded

    const app = makeApp();
    const res = await app.request("/api/results");
    const data = await res.json();
    expect(data).toEqual(["eval_20260102_000000.json", "eval_20260101_000000.json"]);
  });
});

describe("GET /api/results/:filename", () => {
  it("returns result file content", async () => {
    const content = { timestamp: "2026-01-01", n_images: 5, models: [] };
    await writeFile(
      path.join(resultsDir, "eval_20260101_000000.json"),
      JSON.stringify(content),
    );

    const app = makeApp();
    const res = await app.request("/api/results/eval_20260101_000000.json");
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual(content);
  });

  it("rejects invalid filename (no eval_ prefix)", async () => {
    const app = makeApp();
    const res = await app.request("/api/results/malicious.json");
    expect(res.status).toBe(400);
  });

  it("rejects invalid filename (no .json suffix)", async () => {
    const app = makeApp();
    const res = await app.request("/api/results/eval_20260101.txt");
    expect(res.status).toBe(400);
  });

  it("returns 404 for nonexistent file", async () => {
    const app = makeApp();
    const res = await app.request("/api/results/eval_nonexistent.json");
    expect(res.status).toBe(404);
  });
});

describe("GET /api/results-all", () => {
  it("merges results from multiple files", async () => {
    const file1 = {
      n_images: 5,
      total_gt_chars: 100,
      models: [{ model: "model_a", score: 0.8 }],
    };
    const file2 = {
      n_images: 10,
      total_gt_chars: 200,
      models: [
        { model: "model_a", score: 0.9 }, // should override file1's model_a
        { model: "model_b", score: 0.7 },
      ],
    };

    await writeFile(path.join(resultsDir, "eval_20260101.json"), JSON.stringify(file1));
    await writeFile(path.join(resultsDir, "eval_20260102.json"), JSON.stringify(file2));

    const app = makeApp();
    const res = await app.request("/api/results-all");
    const data = await res.json() as { n_images: number; total_gt_chars: number; models: { model: string; score: number }[] };

    expect(data.n_images).toBe(10);
    expect(data.total_gt_chars).toBe(200);
    expect(data.models).toHaveLength(2);

    const modelA = data.models.find((m) => m.model === "model_a");
    expect(modelA?.score).toBe(0.9); // later file wins
  });

  it("returns empty when no files", async () => {
    const app = makeApp();
    const res = await app.request("/api/results-all");
    const data = await res.json() as { models: unknown[] };
    expect(data.models).toEqual([]);
  });
});

describe("GET /api/images/:filename", () => {
  it("rejects path traversal", async () => {
    const app = makeApp();
    const res = await app.request("/api/images/../../../etc/passwd");
    // Hono normalizes the path, so the regex rejects "passwd" (no img_ prefix)
    expect([400, 404]).toContain(res.status);
  });

  it("rejects filename without img_ prefix", async () => {
    const app = makeApp();
    const res = await app.request("/api/images/malicious.png");
    expect(res.status).toBe(400);
  });

  it("accepts valid image filename", async () => {
    // Create a fake PNG file (minimal valid header)
    const pngHeader = Buffer.from([
      0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
      // IHDR chunk
      0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52,
      0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    ]);
    await writeFile(path.join(uploadsDir, "img_12345.png"), pngHeader);

    const app = makeApp();
    const res = await app.request("/api/images/img_12345.png");
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toBe("image/png");
  });

  it("accepts original image filename", async () => {
    await writeFile(path.join(uploadsDir, "img_12345_original.jpg"), Buffer.from([0xff, 0xd8]));

    const app = makeApp();
    const res = await app.request("/api/images/img_12345_original.jpg");
    expect(res.status).toBe(200);
    expect(res.headers.get("Content-Type")).toBe("image/jpeg");
  });

  it("returns 404 for nonexistent image", async () => {
    const app = makeApp();
    const res = await app.request("/api/images/img_99999.png");
    expect(res.status).toBe(404);
  });
});
