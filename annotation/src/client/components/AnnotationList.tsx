import { useEffect, useRef } from "react";
import type { Annotation } from "../types";

interface Props {
  annotations: Annotation[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onUpdateText: (id: string, text: string) => void;
  onDelete: (id: string) => void;
}

export function AnnotationList({
  annotations,
  selectedId,
  onSelect,
  onUpdateText,
  onDelete,
}: Props) {
  const selectedRef = useRef<HTMLDivElement>(null);

  // Scroll to selected annotation
  useEffect(() => {
    if (selectedId && selectedRef.current) {
      selectedRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [selectedId]);

  if (annotations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400 p-4 text-center">
        <p className="text-sm">
          画像上でドラッグして
          <br />
          矩形を描画してください
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 p-3 overflow-y-auto">
      {annotations.map((ann, i) => {
        const isSelected = ann.id === selectedId;
        return (
          <div
            key={ann.id}
            ref={isSelected ? selectedRef : null}
            className={`rounded-lg border p-3 transition-colors cursor-pointer ${
              isSelected
                ? "border-amber-400 bg-amber-50 shadow-sm"
                : "border-gray-200 bg-white hover:border-gray-300"
            }`}
            onClick={() => onSelect(ann.id)}
          >
            <div className="flex items-center justify-between mb-2">
              <span
                className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold text-white ${
                  isSelected ? "bg-amber-500" : "bg-blue-500"
                }`}
              >
                {i + 1}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(ann.id);
                }}
                className="text-gray-400 hover:text-red-500 text-xs px-1.5 py-0.5 rounded hover:bg-red-50 transition-colors"
              >
                削除
              </button>
            </div>
            <input
              type="text"
              value={ann.text}
              onChange={(e) => onUpdateText(ann.id, e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.nativeEvent.isComposing) {
                  e.currentTarget.blur();
                }
              }}
              placeholder="テキストを入力..."
              className={`w-full border rounded-md px-2.5 py-1.5 text-sm outline-none transition-colors ${
                isSelected
                  ? "border-amber-300 focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                  : "border-gray-200 focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              }`}
              autoFocus={isSelected && ann.text === ""}
            />
            <div className="text-[10px] text-gray-400 mt-1.5 font-mono">
              ({ann.rect.x}, {ann.rect.y}) {ann.rect.w}&times;{ann.rect.h}
            </div>
          </div>
        );
      })}
    </div>
  );
}
