import { Hono } from "hono";
import { cors } from "hono/cors";
import { serveStatic } from "@hono/node-server/serve-static";
import { readFile, writeFile, mkdir, unlink } from "node:fs/promises";
import { existsSync } from "node:fs";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import path from "node:path";

const execFileAsync = promisify(execFile);

export interface AppDirs {
  root: string;
  uploadsDir: string;
  dataDir: string;
  annotationsDir: string;
  imagesManifest: string;
  preprocessScript: string;
}

export function resolveDirs(root: string): AppDirs {
  return {
    root,
    uploadsDir: path.join(root, "uploads"),
    dataDir: path.join(root, "data"),
    annotationsDir: path.join(root, "data", "annotations"),
    imagesManifest: path.join(root, "data", "images.json"),
    preprocessScript: path.join(root, "scripts", "preprocess.py"),
  };
}

export async function ensureDirs(dirs: AppDirs) {
  for (const dir of [dirs.uploadsDir, dirs.dataDir, dirs.annotationsDir]) {
    if (!existsSync(dir)) await mkdir(dir, { recursive: true });
  }
  if (!existsSync(dirs.imagesManifest)) {
    await writeFile(dirs.imagesManifest, "[]", "utf-8");
  }
}

interface ImageEntry {
  id: string;
  filename: string;
  originalFilename: string;
  path: string;
  originalPath: string;
  width: number;
  height: number;
  originalWidth: number;
  originalHeight: number;
  preprocessed: boolean;
  uploadedAt: string;
}

async function readManifest(manifestPath: string): Promise<ImageEntry[]> {
  const data = await readFile(manifestPath, "utf-8");
  return JSON.parse(data);
}

async function writeManifest(manifestPath: string, entries: ImageEntry[]) {
  await writeFile(manifestPath, JSON.stringify(entries, null, 2), "utf-8");
}

async function preprocessImage(
  preprocessScript: string,
  inputPath: string,
  outputPath: string,
): Promise<{ width: number; height: number; originalWidth: number; originalHeight: number }> {
  const { stdout, stderr } = await execFileAsync("python3", [
    preprocessScript,
    inputPath,
    outputPath,
  ]);
  if (stderr) console.error("[preprocess stderr]", stderr);
  const meta = JSON.parse(stdout.trim());
  return {
    width: meta.width,
    height: meta.height,
    originalWidth: meta.original_width,
    originalHeight: meta.original_height,
  };
}

export function getImageDimensions(buffer: Buffer): { width: number; height: number } {
  // PNG
  if (buffer[0] === 0x89 && buffer[1] === 0x50 && buffer[2] === 0x4e && buffer[3] === 0x47) {
    return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
  }
  // JPEG
  if (buffer[0] === 0xff && buffer[1] === 0xd8) {
    let offset = 2;
    while (offset < buffer.length - 1) {
      if (buffer[offset] !== 0xff) break;
      const marker = buffer[offset + 1];
      if (marker >= 0xc0 && marker <= 0xc3) {
        return { height: buffer.readUInt16BE(offset + 5), width: buffer.readUInt16BE(offset + 7) };
      }
      const segLen = buffer.readUInt16BE(offset + 2);
      offset += 2 + segLen;
    }
  }
  return { width: 0, height: 0 };
}

export function createApp(dirs: AppDirs) {
  const app = new Hono();

  app.use("*", cors());

  // Serve uploaded images (original + preprocessed)
  app.use("/uploads/*", serveStatic({ root: dirs.root }));

  // --- Image API ---

  app.get("/api/images", async (c) => {
    const images = await readManifest(dirs.imagesManifest);
    return c.json(images);
  });

  app.post("/api/images", async (c) => {
    const body = await c.req.parseBody();
    const file = body["file"];

    if (!(file instanceof File)) {
      return c.json({ error: "No file provided" }, 400);
    }

    const ext = path.extname(file.name) || ".png";
    const id = `img_${Date.now()}`;

    // Save original
    const originalFilename = `${id}_original${ext}`;
    const originalPath = path.join(dirs.uploadsDir, originalFilename);
    const buffer = Buffer.from(await file.arrayBuffer());
    await writeFile(originalPath, buffer);

    // Preprocess → save as PNG
    const processedFilename = `${id}.png`;
    const processedPath = path.join(dirs.uploadsDir, processedFilename);

    let dims: { width: number; height: number; originalWidth: number; originalHeight: number };
    let preprocessed = false;

    try {
      dims = await preprocessImage(dirs.preprocessScript, originalPath, processedPath);
      preprocessed = true;
      console.log(`[preprocess] ${file.name}: ${dims.originalWidth}x${dims.originalHeight} → ${dims.width}x${dims.height}`);
    } catch (err) {
      console.error(`[preprocess] Failed for ${file.name}, using original:`, err);
      // Fallback: copy original as processed
      await writeFile(processedPath, buffer);
      const fallback = getImageDimensions(buffer);
      dims = {
        width: fallback.width,
        height: fallback.height,
        originalWidth: fallback.width,
        originalHeight: fallback.height,
      };
    }

    const entry: ImageEntry = {
      id,
      filename: processedFilename,
      originalFilename,
      path: `/uploads/${processedFilename}`,
      originalPath: `/uploads/${originalFilename}`,
      width: dims.width,
      height: dims.height,
      originalWidth: dims.originalWidth,
      originalHeight: dims.originalHeight,
      preprocessed,
      uploadedAt: new Date().toISOString(),
    };

    const images = await readManifest(dirs.imagesManifest);
    images.push(entry);
    await writeManifest(dirs.imagesManifest, images);

    const annotationData = {
      imageId: id,
      imagePath: entry.path,
      originalPath: entry.originalPath,
      width: dims.width,
      height: dims.height,
      annotations: [],
    };
    await writeFile(
      path.join(dirs.annotationsDir, `${id}.json`),
      JSON.stringify(annotationData, null, 2),
      "utf-8",
    );

    return c.json(entry, 201);
  });

  app.delete("/api/images/:id", async (c) => {
    const id = c.req.param("id");
    const images = await readManifest(dirs.imagesManifest);
    const image = images.find((img) => img.id === id);
    if (!image) return c.json({ error: "Not found" }, 404);

    // Remove both original and processed files
    for (const filename of [image.filename, image.originalFilename]) {
      try {
        await unlink(path.join(dirs.uploadsDir, filename));
      } catch {
        // file may not exist
      }
    }

    try {
      await unlink(path.join(dirs.annotationsDir, `${id}.json`));
    } catch {
      // may not exist
    }

    const updated = images.filter((img) => img.id !== id);
    await writeManifest(dirs.imagesManifest, updated);

    return c.json({ ok: true });
  });

  // --- Annotation API ---

  app.get("/api/annotations/:imageId", async (c) => {
    const imageId = c.req.param("imageId");
    const filepath = path.join(dirs.annotationsDir, `${imageId}.json`);

    if (!existsSync(filepath)) {
      return c.json({ error: "Not found" }, 404);
    }

    const data = await readFile(filepath, "utf-8");
    return c.json(JSON.parse(data));
  });

  app.put("/api/annotations/:imageId", async (c) => {
    const imageId = c.req.param("imageId");
    const filepath = path.join(dirs.annotationsDir, `${imageId}.json`);
    const body = await c.req.json();

    if (!body.annotations || !Array.isArray(body.annotations)) {
      return c.json({ error: "Invalid data" }, 400);
    }

    let existing: Record<string, unknown> = {};
    if (existsSync(filepath)) {
      existing = JSON.parse(await readFile(filepath, "utf-8"));
    }

    const updated = {
      ...existing,
      imageId,
      annotations: body.annotations,
    };

    await writeFile(filepath, JSON.stringify(updated, null, 2), "utf-8");
    return c.json(updated);
  });

  return app;
}
