import { useState, useEffect, useCallback, useRef } from "react";
import { AnnotationCanvas } from "./components/AnnotationCanvas";
import { AnnotationList } from "./components/AnnotationList";
import type { Annotation, ImageInfo, Rect } from "./types";

function generateId(): string {
  return Math.random().toString(36).slice(2, 10);
}

export function App() {
  const [images, setImages] = useState<ImageInfo[]>([]);
  const [currentImageId, setCurrentImageId] = useState<string | null>(null);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [uploadQueue, setUploadQueue] = useState<
    { name: string; status: "pending" | "processing" | "done" | "error" }[]
  >([]);
  const [draggingOver, setDraggingOver] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dragCounterRef = useRef(0);

  const currentImage = images.find((img) => img.id === currentImageId) ?? null;

  // Fetch image list
  const fetchImages = useCallback(async () => {
    const res = await fetch("/api/images");
    const data: ImageInfo[] = await res.json();
    setImages(data);
  }, []);

  useEffect(() => {
    fetchImages();
  }, [fetchImages]);

  // Fetch annotations when image changes
  useEffect(() => {
    if (!currentImageId) {
      setAnnotations([]);
      return;
    }

    let cancelled = false;
    (async () => {
      const res = await fetch(`/api/annotations/${currentImageId}`);
      if (res.ok && !cancelled) {
        const data = await res.json();
        setAnnotations(data.annotations ?? []);
        setDirty(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [currentImageId]);

  // Auto-save with debounce
  useEffect(() => {
    if (!dirty || !currentImageId) return;

    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(async () => {
      setSaving(true);
      await fetch(`/api/annotations/${currentImageId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ annotations }),
      });
      setSaving(false);
      setDirty(false);
    }, 800);

    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    };
  }, [annotations, dirty, currentImageId]);

  const uploading = uploadQueue.length > 0;

  // Upload files (shared by file input and DnD)
  const uploadFiles = useCallback(async (files: FileList | File[]) => {
    const imageFiles = Array.from(files).filter((f) =>
      f.type.startsWith("image/"),
    );
    if (imageFiles.length === 0) return;

    const queue = imageFiles.map((f) => ({
      name: f.name,
      status: "pending" as const,
    }));
    setUploadQueue(queue);

    let lastId: string | null = null;
    for (let i = 0; i < imageFiles.length; i++) {
      setUploadQueue((prev) =>
        prev.map((item, j) =>
          j === i ? { ...item, status: "processing" } : item,
        ),
      );

      const formData = new FormData();
      formData.append("file", imageFiles[i]);
      try {
        const res = await fetch("/api/images", {
          method: "POST",
          body: formData,
        });
        if (res.ok) {
          const newImage: ImageInfo = await res.json();
          setImages((prev) => [...prev, newImage]);
          lastId = newImage.id;
          setUploadQueue((prev) =>
            prev.map((item, j) =>
              j === i ? { ...item, status: "done" } : item,
            ),
          );
        } else {
          setUploadQueue((prev) =>
            prev.map((item, j) =>
              j === i ? { ...item, status: "error" } : item,
            ),
          );
        }
      } catch {
        setUploadQueue((prev) =>
          prev.map((item, j) =>
            j === i ? { ...item, status: "error" } : item,
          ),
        );
      }
    }
    if (lastId) setCurrentImageId(lastId);
    // Keep the queue visible briefly so user sees completion
    setTimeout(() => setUploadQueue([]), 1500);
  }, []);

  // File input handler
  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) await uploadFiles(e.target.files);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Drag and drop handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current++;
    if (e.dataTransfer.types.includes("Files")) {
      setDraggingOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current--;
    if (dragCounterRef.current === 0) {
      setDraggingOver(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current = 0;
    setDraggingOver(false);
    if (e.dataTransfer.files.length > 0) {
      await uploadFiles(e.dataTransfer.files);
    }
  };

  // Create annotation from drawn rectangle
  const handleCreateRect = useCallback((rect: Rect) => {
    const now = new Date().toISOString();
    const ann: Annotation = {
      id: generateId(),
      rect,
      text: "",
      createdAt: now,
      updatedAt: now,
    };
    setAnnotations((prev) => [...prev, ann]);
    setSelectedId(ann.id);
    setDirty(true);
  }, []);

  // Update annotation text
  const handleUpdateText = useCallback((id: string, text: string) => {
    setAnnotations((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, text, updatedAt: new Date().toISOString() } : a,
      ),
    );
    setDirty(true);
  }, []);

  // Delete annotation
  const handleDeleteAnnotation = useCallback(
    (id: string) => {
      setAnnotations((prev) => prev.filter((a) => a.id !== id));
      if (selectedId === id) setSelectedId(null);
      setDirty(true);
    },
    [selectedId],
  );

  // Delete image
  const handleDeleteImage = useCallback(async () => {
    if (!currentImageId) return;
    setDeleteConfirmOpen(true);
  }, [currentImageId]);

  const executeDeleteImage = useCallback(async () => {
    setDeleteConfirmOpen(false);
    if (!currentImageId) return;

    // Save pending annotations first
    if (dirty) {
      await fetch(`/api/annotations/${currentImageId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ annotations }),
      });
    }

    const res = await fetch(`/api/images/${currentImageId}`, {
      method: "DELETE",
    });
    if (!res.ok) return;

    const idx = images.findIndex((img) => img.id === currentImageId);
    const remaining = images.filter((img) => img.id !== currentImageId);
    setImages(remaining);

    // Switch to adjacent image
    if (remaining.length === 0) {
      setCurrentImageId(null);
    } else if (idx >= remaining.length) {
      setCurrentImageId(remaining[remaining.length - 1].id);
    } else {
      setCurrentImageId(remaining[idx].id);
    }
    setSelectedId(null);
    setDirty(false);
  }, [currentImageId, images, dirty, annotations]);

  // Manual save
  const handleSave = async () => {
    if (!currentImageId) return;
    setSaving(true);
    await fetch(`/api/annotations/${currentImageId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ annotations }),
    });
    setSaving(false);
    setDirty(false);
  };

  // Image navigation
  const currentIndex = images.findIndex((img) => img.id === currentImageId);
  const canPrev = currentIndex > 0;
  const canNext = currentIndex < images.length - 1;

  // Preload adjacent images for instant switching
  useEffect(() => {
    for (const offset of [-1, 1]) {
      const idx = currentIndex + offset;
      if (idx >= 0 && idx < images.length) {
        const img = new Image();
        img.src = images[idx].path;
      }
    }
  }, [currentIndex, images]);

  const goToImage = useCallback(
    (id: string) => {
      if (dirty && currentImageId) {
        fetch(`/api/annotations/${currentImageId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ annotations }),
        });
      }
      setCurrentImageId(id);
      setSelectedId(null);
    },
    [dirty, currentImageId, annotations],
  );

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const inInput =
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT";

      // Escape: deselect (works even in input)
      if (e.key === "Escape") {
        if (inInput) {
          (target as HTMLInputElement).blur();
        }
        setSelectedId(null);
        return;
      }

      // Skip shortcuts when typing in input
      if (inInput) return;

      // Delete/Backspace: delete selected annotation
      if ((e.key === "Delete" || e.key === "Backspace") && selectedId) {
        e.preventDefault();
        handleDeleteAnnotation(selectedId);
        return;
      }

      // Arrow left/right: navigate images
      if (e.key === "ArrowLeft" && canPrev) {
        e.preventDefault();
        goToImage(images[currentIndex - 1].id);
        return;
      }
      if (e.key === "ArrowRight" && canNext) {
        e.preventDefault();
        goToImage(images[currentIndex + 1].id);
        return;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    selectedId,
    handleDeleteAnnotation,
    canPrev,
    canNext,
    currentIndex,
    images,
    goToImage,
  ]);

  return (
    <div
      className="h-screen flex flex-col bg-gray-50 relative"
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* Delete confirmation dialog */}
      {deleteConfirmOpen && (
        <div className="absolute inset-0 z-50 bg-black/40 flex items-center justify-center">
          <div className="bg-white rounded-xl shadow-2xl p-6 w-96 mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0">
                <span className="text-red-600 text-lg">!</span>
              </div>
              <div>
                <h3 className="text-base font-semibold text-gray-900">
                  画像を削除しますか？
                </h3>
                <p className="text-sm text-gray-500 mt-0.5">
                  この操作は取り消せません
                </p>
              </div>
            </div>
            {currentImage && (
              <div className="bg-gray-50 rounded-lg p-3 mb-4 text-sm text-gray-600">
                <div className="font-medium text-gray-700 truncate">
                  {currentImage.filename}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {currentImage.width}&times;{currentImage.height}
                  {annotations.length > 0 &&
                    ` / ${annotations.length}件のアノテーション`}
                </div>
              </div>
            )}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirmOpen(false)}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                キャンセル
              </button>
              <button
                onClick={executeDeleteImage}
                className="px-4 py-2 text-sm text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors"
              >
                削除する
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Drag overlay */}
      {draggingOver && (
        <div className="absolute inset-0 z-50 bg-blue-500/10 border-4 border-dashed border-blue-500 rounded-lg flex items-center justify-center pointer-events-none">
          <div className="bg-white rounded-xl px-8 py-6 shadow-lg text-center">
            <div className="text-4xl mb-2">+</div>
            <div className="text-lg font-semibold text-blue-700">
              画像をドロップしてアップロード
            </div>
            <div className="text-sm text-gray-500 mt-1">
              複数ファイル対応
            </div>
          </div>
        </div>
      )}

      {/* Upload progress */}
      {uploadQueue.length > 0 && (
        <div className="absolute bottom-12 right-4 z-40 bg-white rounded-lg shadow-lg border border-gray-200 p-3 w-72">
          <div className="text-sm font-semibold text-gray-700 mb-2">
            画像処理中...
            <span className="font-normal text-gray-400 ml-1">
              {uploadQueue.filter((q) => q.status === "done").length}/
              {uploadQueue.length}
            </span>
          </div>
          <div className="flex flex-col gap-1.5 max-h-48 overflow-y-auto">
            {uploadQueue.map((item, i) => (
              <div
                key={i}
                className="flex items-center gap-2 text-xs"
              >
                <span className="shrink-0 w-4 text-center">
                  {item.status === "done" && (
                    <span className="text-green-500">&#10003;</span>
                  )}
                  {item.status === "processing" && (
                    <span className="text-blue-500 animate-spin inline-block">&#9696;</span>
                  )}
                  {item.status === "pending" && (
                    <span className="text-gray-300">&#9675;</span>
                  )}
                  {item.status === "error" && (
                    <span className="text-red-500">&#10007;</span>
                  )}
                </span>
                <span
                  className={`truncate ${
                    item.status === "processing"
                      ? "text-blue-700 font-medium"
                      : item.status === "done"
                        ? "text-gray-400"
                        : item.status === "error"
                          ? "text-red-500"
                          : "text-gray-500"
                  }`}
                >
                  {item.name}
                </span>
                {item.status === "processing" && (
                  <span className="text-blue-400 ml-auto shrink-0">前処理中</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-2.5 bg-white border-b border-gray-200 shrink-0">
        <h1 className="text-base font-bold text-gray-800 mr-2">
          OCR Annotation
        </h1>

        {/* Image selector */}
        <select
          value={currentImageId ?? ""}
          onChange={(e) => e.target.value && goToImage(e.target.value)}
          className="border border-gray-300 rounded-md px-2.5 py-1.5 text-sm bg-white min-w-[200px]"
        >
          <option value="">画像を選択...</option>
          {images.map((img) => (
            <option key={img.id} value={img.id}>
              {img.filename}
            </option>
          ))}
        </select>

        {/* Delete image */}
        <button
          onClick={handleDeleteImage}
          disabled={!currentImageId}
          className="px-2 py-1.5 text-sm text-gray-500 border border-gray-300 rounded-md hover:text-red-600 hover:border-red-300 hover:bg-red-50 disabled:opacity-30 disabled:hover:text-gray-500 disabled:hover:border-gray-300 disabled:hover:bg-white transition-colors"
          title="画像を削除"
        >
          削除
        </button>

        {/* Navigation */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => canPrev && goToImage(images[currentIndex - 1].id)}
            disabled={!canPrev}
            className="px-2 py-1.5 text-sm border border-gray-300 rounded-md disabled:opacity-30 hover:bg-gray-50 transition-colors"
          >
            &larr;
          </button>
          <span className="text-xs text-gray-500 min-w-[60px] text-center">
            {currentImageId
              ? `${currentIndex + 1} / ${images.length}`
              : `${images.length} 枚`}
          </span>
          <button
            onClick={() => canNext && goToImage(images[currentIndex + 1].id)}
            disabled={!canNext}
            className="px-2 py-1.5 text-sm border border-gray-300 rounded-md disabled:opacity-30 hover:bg-gray-50 transition-colors"
          >
            &rarr;
          </button>
        </div>

        {/* Original / Preprocessed toggle */}
        {currentImage?.preprocessed && (
          <button
            onClick={() => setShowOriginal((v) => !v)}
            className={`px-2.5 py-1.5 text-xs rounded-md border transition-colors ${
              showOriginal
                ? "bg-amber-50 border-amber-300 text-amber-700"
                : "bg-green-50 border-green-300 text-green-700"
            }`}
          >
            {showOriginal ? "原画像" : "補正済み"}
          </button>
        )}

        <div className="flex-1" />

        {/* Upload */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileInput}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {uploading ? "アップロード中..." : "画像追加"}
        </button>

        {/* Save */}
        <button
          onClick={handleSave}
          disabled={!dirty || saving}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-30 transition-colors"
        >
          {saving ? "保存中..." : dirty ? "保存" : "保存済み"}
        </button>
      </header>

      {/* Main content */}
      <div className="flex flex-1 min-h-0">
        {/* Canvas area */}
        <div className="flex-1 min-w-0 h-full">
          <AnnotationCanvas
            imageSrc={
              currentImage
                ? showOriginal
                  ? currentImage.originalPath
                  : currentImage.path
                : null
            }
            annotations={annotations}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onCreateRect={handleCreateRect}
            onDropFiles={uploadFiles}
          />
        </div>

        {/* Sidebar */}
        <div className="w-72 border-l border-gray-200 bg-white flex flex-col shrink-0">
          <div className="px-3 py-2.5 border-b border-gray-200 flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-700">
              Annotations
            </span>
            <span className="text-xs text-gray-400">
              {annotations.length} 件
            </span>
          </div>
          <div className="flex-1 overflow-y-auto">
            <AnnotationList
              annotations={annotations}
              selectedId={selectedId}
              onSelect={setSelectedId}
              onUpdateText={handleUpdateText}
              onDelete={handleDeleteAnnotation}
            />
          </div>
        </div>
      </div>

      {/* Status bar */}
      <footer className="flex items-center gap-4 px-4 py-1.5 bg-white border-t border-gray-200 text-xs text-gray-500 shrink-0">
        {currentImage && (
          <>
            <span>{currentImage.filename}</span>
            <span>
              {showOriginal
                ? `${currentImage.originalWidth}\u00d7${currentImage.originalHeight}`
                : `${currentImage.width}\u00d7${currentImage.height}`}
            </span>
            {currentImage.preprocessed && (
              <span className="text-green-600">
                {showOriginal ? "原画像表示中" : "補正済み"}
              </span>
            )}
          </>
        )}
        <span>Annotations: {annotations.length}</span>
        <span className="text-gray-300">|</span>
        <span className="text-gray-400">
          Esc: 選択解除 / Del: 削除 / &larr;&rarr;: 画像切替
        </span>
        <div className="flex-1" />
        {dirty && <span className="text-amber-600">未保存の変更あり</span>}
        {saving && <span className="text-blue-600">保存中...</span>}
      </footer>
    </div>
  );
}
