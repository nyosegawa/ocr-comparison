import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createApp, ensureDirs, getImageDimensions, resolveDirs } from "./app.js";
import type { AppDirs } from "./app.js";
import { mkdtemp, writeFile, readFile, rm } from "node:fs/promises";
import path from "node:path";
import os from "node:os";

let tmpDir: string;
let dirs: AppDirs;

beforeEach(async () => {
  tmpDir = await mkdtemp(path.join(os.tmpdir(), "annotation-test-"));
  dirs = resolveDirs(tmpDir);
  await ensureDirs(dirs);
});

afterEach(async () => {
  await rm(tmpDir, { recursive: true, force: true });
});

// ---------------------------------------------------------------------------
// getImageDimensions
// ---------------------------------------------------------------------------

describe("getImageDimensions", () => {
  it("reads PNG dimensions", () => {
    // Minimal PNG with 100x50 dimensions
    const buf = Buffer.alloc(24, 0);
    buf[0] = 0x89; buf[1] = 0x50; buf[2] = 0x4e; buf[3] = 0x47; // PNG magic
    buf.writeUInt32BE(100, 16); // width
    buf.writeUInt32BE(50, 20); // height
    expect(getImageDimensions(buf)).toEqual({ width: 100, height: 50 });
  });

  it("returns 0x0 for unknown format", () => {
    const buf = Buffer.from([0x00, 0x01, 0x02, 0x03]);
    expect(getImageDimensions(buf)).toEqual({ width: 0, height: 0 });
  });
});

// ---------------------------------------------------------------------------
// GET /api/images
// ---------------------------------------------------------------------------

describe("GET /api/images", () => {
  it("returns empty array initially", async () => {
    const app = createApp(dirs);
    const res = await app.request("/api/images");
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual([]);
  });

  it("returns manifest entries", async () => {
    const entry = {
      id: "img_001",
      filename: "img_001.png",
      originalFilename: "img_001_original.png",
      path: "/uploads/img_001.png",
      originalPath: "/uploads/img_001_original.png",
      width: 100,
      height: 50,
      originalWidth: 200,
      originalHeight: 100,
      preprocessed: true,
      uploadedAt: "2026-01-01T00:00:00.000Z",
    };
    await writeFile(dirs.imagesManifest, JSON.stringify([entry]), "utf-8");

    const app = createApp(dirs);
    const res = await app.request("/api/images");
    const data = await res.json();
    expect(data).toHaveLength(1);
    expect((data as typeof entry[])[0].id).toBe("img_001");
  });
});

// ---------------------------------------------------------------------------
// DELETE /api/images/:id
// ---------------------------------------------------------------------------

describe("DELETE /api/images/:id", () => {
  it("returns 404 for nonexistent image", async () => {
    const app = createApp(dirs);
    const res = await app.request("/api/images/img_nonexistent", { method: "DELETE" });
    expect(res.status).toBe(404);
  });

  it("deletes image and cleans up files", async () => {
    // Set up manifest and files
    const entry = {
      id: "img_del",
      filename: "img_del.png",
      originalFilename: "img_del_original.png",
      path: "/uploads/img_del.png",
      originalPath: "/uploads/img_del_original.png",
      width: 10, height: 10, originalWidth: 10, originalHeight: 10,
      preprocessed: false,
      uploadedAt: "2026-01-01T00:00:00.000Z",
    };
    await writeFile(dirs.imagesManifest, JSON.stringify([entry]), "utf-8");
    await writeFile(path.join(dirs.uploadsDir, "img_del.png"), "fake");
    await writeFile(path.join(dirs.uploadsDir, "img_del_original.png"), "fake");
    await writeFile(path.join(dirs.annotationsDir, "img_del.json"), "{}");

    const app = createApp(dirs);
    const res = await app.request("/api/images/img_del", { method: "DELETE" });
    expect(res.status).toBe(200);

    // Manifest should be empty now
    const manifest = JSON.parse(await readFile(dirs.imagesManifest, "utf-8"));
    expect(manifest).toEqual([]);
  });
});

// ---------------------------------------------------------------------------
// GET /api/annotations/:imageId
// ---------------------------------------------------------------------------

describe("GET /api/annotations/:imageId", () => {
  it("returns 404 for nonexistent annotation", async () => {
    const app = createApp(dirs);
    const res = await app.request("/api/annotations/img_nonexistent");
    expect(res.status).toBe(404);
  });

  it("returns annotation data", async () => {
    const annData = { imageId: "img_ann", annotations: [{ id: "a1", text: "hello" }] };
    await writeFile(path.join(dirs.annotationsDir, "img_ann.json"), JSON.stringify(annData));

    const app = createApp(dirs);
    const res = await app.request("/api/annotations/img_ann");
    expect(res.status).toBe(200);
    const data = await res.json() as typeof annData;
    expect(data.imageId).toBe("img_ann");
    expect(data.annotations).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// PUT /api/annotations/:imageId
// ---------------------------------------------------------------------------

describe("PUT /api/annotations/:imageId", () => {
  it("rejects invalid body", async () => {
    const app = createApp(dirs);
    const res = await app.request("/api/annotations/img_test", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ invalid: true }),
    });
    expect(res.status).toBe(400);
  });

  it("creates new annotation file", async () => {
    const app = createApp(dirs);
    const annotations = [{ id: "a1", text: "test", rect: { x: 0, y: 0, w: 10, h: 10 } }];
    const res = await app.request("/api/annotations/img_new", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ annotations }),
    });
    expect(res.status).toBe(200);
    const data = await res.json() as { imageId: string; annotations: typeof annotations };
    expect(data.imageId).toBe("img_new");
    expect(data.annotations).toEqual(annotations);
  });

  it("updates existing annotation file preserving metadata", async () => {
    const existing = { imageId: "img_upd", imagePath: "/uploads/img_upd.png", width: 100, height: 50, annotations: [] };
    await writeFile(path.join(dirs.annotationsDir, "img_upd.json"), JSON.stringify(existing));

    const app = createApp(dirs);
    const newAnnotations = [{ id: "a1", text: "updated" }];
    const res = await app.request("/api/annotations/img_upd", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ annotations: newAnnotations }),
    });
    expect(res.status).toBe(200);
    const data = await res.json() as typeof existing & { annotations: typeof newAnnotations };
    expect(data.imagePath).toBe("/uploads/img_upd.png"); // preserved
    expect(data.annotations).toEqual(newAnnotations);
  });
});
