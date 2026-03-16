import { useRef, useEffect, useState, useCallback } from "react";
import type { Annotation, Rect } from "../types";

interface Transform {
  scale: number;
  offsetX: number;
  offsetY: number;
}

interface DrawState {
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
}

interface Props {
  imageSrc: string | null;
  annotations: Annotation[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onCreateRect: (rect: Rect) => void;
  onDropFiles: (files: FileList | File[]) => void;
}

export function AnnotationCanvas({
  imageSrc,
  annotations,
  selectedId,
  onSelect,
  onCreateRect,
  onDropFiles,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const transformRef = useRef<Transform>({ scale: 1, offsetX: 0, offsetY: 0 });
  const drawStateRef = useRef<DrawState | null>(null);
  const annotationsRef = useRef(annotations);
  const selectedIdRef = useRef(selectedId);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });
  const [imageLoaded, setImageLoaded] = useState(false);
  const [localDragOver, setLocalDragOver] = useState(false);
  const localDragCounterRef = useRef(0);
  const rafRef = useRef(0);

  annotationsRef.current = annotations;
  selectedIdRef.current = selectedId;

  const computeTransform = useCallback(
    (cw: number, ch: number, img: HTMLImageElement | null): Transform => {
      if (!img || !cw || !ch) return { scale: 1, offsetX: 0, offsetY: 0 };
      const scaleX = cw / img.naturalWidth;
      const scaleY = ch / img.naturalHeight;
      const scale = Math.min(scaleX, scaleY);
      return {
        scale,
        offsetX: (cw - img.naturalWidth * scale) / 2,
        offsetY: (ch - img.naturalHeight * scale) / 2,
      };
    },
    [],
  );

  const toImageCoords = useCallback((dx: number, dy: number) => {
    const t = transformRef.current;
    return { x: (dx - t.offsetX) / t.scale, y: (dy - t.offsetY) / t.scale };
  }, []);

  const toDisplay = useCallback((rect: Rect) => {
    const t = transformRef.current;
    return {
      x: rect.x * t.scale + t.offsetX,
      y: rect.y * t.scale + t.offsetY,
      w: rect.w * t.scale,
      h: rect.h * t.scale,
    };
  }, []);

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const w = canvas.width / dpr;
    const h = canvas.height / dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Background
    ctx.fillStyle = "#f1f5f9";
    ctx.fillRect(0, 0, w, h);

    // Image
    const img = imageRef.current;
    if (img?.complete && img.naturalWidth > 0) {
      const t = transformRef.current;
      ctx.shadowColor = "rgba(0,0,0,0.12)";
      ctx.shadowBlur = 10;
      ctx.shadowOffsetY = 2;
      ctx.fillStyle = "#fff";
      ctx.fillRect(t.offsetX, t.offsetY, img.naturalWidth * t.scale, img.naturalHeight * t.scale);
      ctx.shadowColor = "transparent";
      ctx.shadowBlur = 0;
      ctx.shadowOffsetY = 0;
      ctx.drawImage(img, t.offsetX, t.offsetY, img.naturalWidth * t.scale, img.naturalHeight * t.scale);
    }

    // Annotations (non-selected first, then selected on top)
    const anns = annotationsRef.current;
    const selId = selectedIdRef.current;

    const drawOne = (ann: Annotation, idx: number) => {
      const d = toDisplay(ann.rect);
      const sel = ann.id === selId;

      ctx.fillStyle = sel ? "rgba(245,158,11,0.22)" : "rgba(59,130,246,0.10)";
      ctx.fillRect(d.x, d.y, d.w, d.h);

      if (sel) {
        ctx.strokeStyle = "rgba(245,158,11,0.35)";
        ctx.lineWidth = 6;
        ctx.strokeRect(d.x - 1, d.y - 1, d.w + 2, d.h + 2);
      }
      ctx.strokeStyle = sel ? "#f59e0b" : "#3b82f6";
      ctx.lineWidth = sel ? 2.5 : 1.5;
      ctx.strokeRect(d.x, d.y, d.w, d.h);

      if (sel) {
        const hs = 6;
        ctx.fillStyle = "#f59e0b";
        for (const [cx, cy] of [[d.x, d.y], [d.x + d.w, d.y], [d.x, d.y + d.h], [d.x + d.w, d.y + d.h]]) {
          ctx.fillRect(cx - hs / 2, cy - hs / 2, hs, hs);
        }
      }

      // Text label
      if (ann.text) {
        const fs = Math.max(12, Math.min(16, d.h * 0.35));
        ctx.font = `600 ${fs}px system-ui, sans-serif`;
        const m = ctx.measureText(ann.text);
        const px = 5, py = 3;
        const tw = m.width + px * 2, th = fs + py * 2;
        const tx = d.x, ty = d.y - th - 3 > 0 ? d.y - th - 3 : d.y + 3;

        ctx.fillStyle = sel ? "rgba(254,243,199,0.95)" : "rgba(219,234,254,0.95)";
        ctx.beginPath();
        ctx.roundRect(tx, ty, tw, th, 3);
        ctx.fill();
        ctx.strokeStyle = sel ? "rgba(245,158,11,0.5)" : "rgba(59,130,246,0.3)";
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillStyle = sel ? "#92400e" : "#1e40af";
        ctx.fillText(ann.text, tx + px, ty + py + fs * 0.85);
      }

      // Badge
      const br = Math.max(9, Math.min(13, d.h * 0.25));
      ctx.fillStyle = sel ? "#f59e0b" : "#3b82f6";
      ctx.beginPath();
      ctx.arc(d.x, d.y, br, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.fillStyle = "#fff";
      ctx.font = `700 ${br * 1.1}px system-ui, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(String(idx + 1), d.x, d.y);
      ctx.textAlign = "start";
      ctx.textBaseline = "alphabetic";
    };

    for (let i = 0; i < anns.length; i++) if (anns[i].id !== selId) drawOne(anns[i], i);
    for (let i = 0; i < anns.length; i++) if (anns[i].id === selId) drawOne(anns[i], i);

    // Drawing preview
    const ds = drawStateRef.current;
    if (ds) {
      const x = Math.min(ds.startX, ds.currentX);
      const y = Math.min(ds.startY, ds.currentY);
      const rw = Math.abs(ds.currentX - ds.startX);
      const rh = Math.abs(ds.currentY - ds.startY);
      ctx.fillStyle = "rgba(34,197,94,0.15)";
      ctx.fillRect(x, y, rw, rh);
      ctx.strokeStyle = "#16a34a";
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 4]);
      ctx.strokeRect(x, y, rw, rh);
      ctx.setLineDash([]);
    }
  }, [toDisplay]);

  const scheduleRender = useCallback(() => {
    cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(render);
  }, [render]);

  useEffect(() => {
    // Immediately clear old image so stale frame doesn't linger
    imageRef.current = null;
    setImageLoaded(false);
    scheduleRender();

    if (!imageSrc) return;
    const img = new Image();
    img.onload = () => { imageRef.current = img; setImageLoaded(true); };
    img.src = imageSrc;
  }, [imageSrc]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    transformRef.current = computeTransform(canvasSize.width, canvasSize.height, imageRef.current);
    scheduleRender();
  }, [canvasSize, imageLoaded, computeTransform, scheduleRender]);

  useEffect(() => { scheduleRender(); }, [annotations, selectedId, scheduleRender]);

  useEffect(() => {
    const el = containerRef.current;
    const c = canvasRef.current;
    if (!el || !c) return;
    const obs = new ResizeObserver((e) => {
      const { width, height } = e[0].contentRect;
      if (width > 0 && height > 0) {
        const dpr = window.devicePixelRatio || 1;
        c.width = width * dpr;
        c.height = height * dpr;
        setCanvasSize({ width, height });
      }
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => () => cancelAnimationFrame(rafRef.current), []);

  const hitTest = useCallback((dx: number, dy: number) => {
    const anns = annotationsRef.current;
    for (let i = anns.length - 1; i >= 0; i--) {
      const d = toDisplay(anns[i].rect);
      if (dx >= d.x && dx <= d.x + d.w && dy >= d.y && dy <= d.y + d.h) return anns[i];
    }
    return null;
  }, [toDisplay]);

  const pos = (e: React.MouseEvent) => {
    const r = canvasRef.current!.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    const p = pos(e);
    const hit = hitTest(p.x, p.y);
    if (hit) { onSelect(hit.id); return; }
    onSelect(null);
    drawStateRef.current = { startX: p.x, startY: p.y, currentX: p.x, currentY: p.y };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!drawStateRef.current) return;
    const p = pos(e);
    drawStateRef.current = { ...drawStateRef.current, currentX: p.x, currentY: p.y };
    scheduleRender();
  };

  const handleMouseUp = () => {
    const ds = drawStateRef.current;
    if (!ds) return;
    drawStateRef.current = null;
    if (Math.abs(ds.currentX - ds.startX) < 10 || Math.abs(ds.currentY - ds.startY) < 10) {
      scheduleRender(); return;
    }
    const tl = toImageCoords(Math.min(ds.startX, ds.currentX), Math.min(ds.startY, ds.currentY));
    const br = toImageCoords(Math.max(ds.startX, ds.currentX), Math.max(ds.startY, ds.currentY));
    const rect: Rect = { x: Math.round(tl.x), y: Math.round(tl.y), w: Math.round(br.x - tl.x), h: Math.round(br.y - tl.y) };
    const img = imageRef.current;
    if (img) {
      rect.x = Math.max(0, rect.x);
      rect.y = Math.max(0, rect.y);
      rect.w = Math.min(rect.w, img.naturalWidth - rect.x);
      rect.h = Math.min(rect.h, img.naturalHeight - rect.y);
    }
    if (rect.w > 0 && rect.h > 0) onCreateRect(rect);
    scheduleRender();
  };

  // DnD
  const dndEnter = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); localDragCounterRef.current++; if (e.dataTransfer.types.includes("Files")) setLocalDragOver(true); };
  const dndLeave = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); localDragCounterRef.current--; if (localDragCounterRef.current === 0) setLocalDragOver(false); };
  const dndOver = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); };
  const dndDrop = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); localDragCounterRef.current = 0; setLocalDragOver(false); if (e.dataTransfer.files.length > 0) onDropFiles(e.dataTransfer.files); };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full overflow-hidden"
      onDragEnter={dndEnter}
      onDragLeave={dndLeave}
      onDragOver={dndOver}
      onDrop={dndDrop}
    >
      <canvas
        ref={canvasRef}
        className={`absolute inset-0 w-full h-full ${imageSrc ? "cursor-crosshair" : ""}`}
        onMouseDown={imageSrc ? handleMouseDown : undefined}
        onMouseMove={imageSrc ? handleMouseMove : undefined}
        onMouseUp={imageSrc ? handleMouseUp : undefined}
        onMouseLeave={imageSrc ? handleMouseUp : undefined}
      />
      {!imageSrc && (
        <div
          className={`absolute inset-0 flex items-center justify-center transition-colors ${localDragOver ? "bg-blue-50 border-2 border-dashed border-blue-400" : "bg-gray-100"}`}
        >
          <div className="text-center text-gray-400">
            <div className="text-5xl mb-4 opacity-30">+</div>
            <p className="text-base mb-1">画像をドラッグ&ドロップ</p>
            <p className="text-sm">または上部の「画像追加」ボタンからアップロード</p>
          </div>
        </div>
      )}
    </div>
  );
}
