import { useEffect, useState } from "react";

interface ModelMeta {
  weightsUrl: string | null;
  license: string | null;
}

const MODEL_METADATA: Record<string, ModelMeta> = {
  "claude-4.6-opus": { weightsUrl: null, license: null },
  "gemini-3.1-pro-preview": { weightsUrl: null, license: null },
  "gpt-5.4-thinking": { weightsUrl: null, license: null },
  "hunyuan-ocr": { weightsUrl: "https://huggingface.co/tencent/HunyuanOCR", license: "Apache-2.0" },
  "deepseek-ocr": { weightsUrl: "https://huggingface.co/deepseek-ai/DeepSeek-OCR", license: "MIT" },
  "chandra": { weightsUrl: "https://pypi.org/project/chandra-ocr/", license: "Apache-2.0" },
  "nanonets-ocr-s": { weightsUrl: "https://huggingface.co/nanonets/Nanonets-OCR-s", license: "Apache-2.0" },
  "olmocr-2": { weightsUrl: "https://huggingface.co/allenai/olmOCR-2-7B-1025-FP8", license: "Apache-2.0" },
  "got-ocr-2.0": { weightsUrl: "https://huggingface.co/stepfun-ai/GOT-OCR2_0", license: "Apache-2.0" },
  "paddleocr": { weightsUrl: "https://github.com/PaddlePaddle/PaddleOCR", license: "Apache-2.0" },
  "yomitoku": { weightsUrl: "https://github.com/kotaro-kinoshita/yomitoku", license: "CC-BY-NC-SA-4.0" },
  "ndlocr-lite": { weightsUrl: "https://github.com/ndl-lab/ndlocr-lite", license: "CC-BY-4.0" },
  "ndlocr-v2": { weightsUrl: "https://github.com/ndl-lab/ndlocr_cli", license: "CC-BY-4.0" },
};

interface Metrics {
  hungarian_nls: number;
  boc_f1: number;
  boc_precision: number;
  boc_recall: number;
  cer: number;
  ned: number;
  edit_distance: number;
  gt_length: number;
}

interface Detail {
  image_id: string;
  gt_regions?: string[];
  ground_truth?: string;
  prediction: string;
  error: string | null;
  elapsed_sec: number;
  metrics: Metrics;
}

interface ModelResult {
  model: string;
  category: string;
  aggregated: Record<string, number>;
  details: Detail[];
}

interface AllResults {
  n_images: number;
  total_gt_chars: number;
  models: ModelResult[];
}

function scoreColor(value: number, invert = false) {
  const v = invert ? 1 - value : value;
  if (v >= 0.8) return "text-green-600";
  if (v >= 0.5) return "text-yellow-600";
  return "text-red-600";
}

function Leaderboard({ models }: { models: ModelResult[] }) {
  const sorted = [...models].sort(
    (a, b) =>
      (b.aggregated.hungarian_nls ?? 0) - (a.aggregated.hungarian_nls ?? 0),
  );

  return (
    <table className="w-full table-fixed text-sm">
      <thead>
        <tr className="border-b border-zinc-200 text-left text-xs text-zinc-500">
          <th className="py-2 pr-3">#</th>
          <th className="py-2 pr-3">Model</th>
          <th className="py-2 pr-3">Category</th>
          <th className="py-2 pr-3">Weights</th>
          <th className="py-2 pr-3">License</th>
          <th className="py-2 pr-3 text-right">NLS</th>
          <th className="py-2 pr-3 text-right">BoC-F1</th>
          <th className="py-2 pr-3 text-right">CER</th>
          <th className="py-2 pr-3 text-right">NED</th>
          <th className="py-2 text-right">Avg Time</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((m, i) => {
          const a = m.aggregated;
          const meta = MODEL_METADATA[m.model];
          const times = m.details
            .filter((d) => d.elapsed_sec != null && !d.error)
            .map((d) => d.elapsed_sec);
          const avgTime =
            times.length > 0
              ? times.reduce((s, t) => s + t, 0) / times.length
              : null;
          return (
            <tr key={m.model} className="border-b border-zinc-100">
              <td className="py-2 pr-3 font-bold text-zinc-400">{i + 1}</td>
              <td className="py-2 pr-3 font-medium">{m.model}</td>
              <td className="py-2 pr-3 text-zinc-500">{m.category}</td>
              <td className="py-2 pr-3 text-zinc-500">
                {meta?.weightsUrl ? (
                  <a
                    href={meta.weightsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 underline hover:text-blue-800"
                  >
                    Link
                  </a>
                ) : (
                  <span className="text-zinc-400">N/A</span>
                )}
              </td>
              <td className="py-2 pr-3 text-zinc-500">
                {meta?.license ?? <span className="text-zinc-400">N/A</span>}
              </td>
              <td
                className={`py-2 pr-3 text-right font-mono ${scoreColor(a.hungarian_nls ?? 0)}`}
              >
                {(a.hungarian_nls ?? 0).toFixed(4)}
              </td>
              <td className="py-2 pr-3 text-right font-mono">
                {(a.boc_f1 ?? 0).toFixed(4)}
              </td>
              <td
                className={`py-2 pr-3 text-right font-mono ${scoreColor(a.cer ?? 0, true)}`}
              >
                {(a.cer ?? 0).toFixed(4)}
              </td>
              <td className="py-2 pr-3 text-right font-mono">
                {(a.ned ?? 0).toFixed(4)}
              </td>
              <td className="py-2 text-right font-mono text-zinc-500">
                {avgTime != null ? `${avgTime.toFixed(1)}s` : "—"}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function ImageComparison({
  imageId,
  models,
}: {
  imageId: string;
  models: ModelResult[];
}) {
  const [activeTab, setActiveTab] = useState(models[0]?.model ?? "");

  // Get GT from first model's detail
  let gtText = "";
  for (const m of models) {
    const d = m.details.find((d) => d.image_id === imageId);
    if (d) {
      gtText = d.gt_regions?.join("\n") ?? d.ground_truth ?? "";
      break;
    }
  }

  const activeModel = models.find((m) => m.model === activeTab);
  const activeDetail = activeModel?.details.find(
    (d) => d.image_id === imageId,
  );
  const hasError = !!activeDetail?.error;

  return (
    <div className="overflow-hidden rounded-lg border border-zinc-200 bg-white">
      <div className="border-b border-zinc-200 bg-zinc-50 px-4 py-2">
        <h3 className="text-sm font-bold text-zinc-700">{imageId}</h3>
      </div>

      <div className="flex min-h-[300px]">
        {/* Left: Image */}
        <div className="flex w-2/5 shrink-0 items-center justify-center border-r border-zinc-200 bg-zinc-100 p-3">
          <img
            src={`/api/images/${imageId}.png`}
            alt={imageId}
            className="max-h-[500px] max-w-full rounded object-contain"
            loading="lazy"
          />
        </div>

        {/* Right: GT + Tabbed results */}
        <div className="flex min-w-0 flex-1 flex-col">
          {/* Right top: Ground Truth */}
          <div className="border-b border-zinc-200 p-3">
            <div className="mb-1 text-xs font-semibold tracking-wide text-green-700 uppercase">
              Ground Truth
            </div>
            <pre className="max-h-[150px] overflow-auto break-all whitespace-pre-wrap text-sm leading-relaxed">
              {gtText || "(empty)"}
            </pre>
          </div>

          {/* Right bottom: Tabs + Result */}
          <div className="flex min-h-0 flex-1 flex-col">
            {/* Tabs */}
            <div className="flex gap-0 overflow-x-auto border-b border-zinc-200">
              {models.map((m) => {
                const d = m.details.find((d) => d.image_id === imageId);
                const isError = !!d?.error;
                const isActive = m.model === activeTab;
                return (
                  <button
                    key={m.model}
                    onClick={() => setActiveTab(m.model)}
                    className={`shrink-0 border-b-2 px-3 py-2 text-xs font-medium transition-colors ${
                      isActive
                        ? "border-blue-500 bg-white text-blue-700"
                        : "border-transparent text-zinc-500 hover:bg-zinc-50 hover:text-zinc-700"
                    } ${isError ? "text-red-500" : ""}`}
                  >
                    {m.model}
                  </button>
                );
              })}
            </div>

            {/* Active tab content */}
            <div className="flex-1 overflow-auto p-3">
              {activeDetail ? (
                <>
                  {hasError ? (
                    <div className="mb-2 text-xs font-mono text-red-500">
                      ERROR
                    </div>
                  ) : (
                    <div className="mb-2 flex flex-wrap gap-3 text-xs font-mono text-zinc-500">
                      <span>
                        NLS=
                        <span className={scoreColor(activeDetail.metrics.hungarian_nls)}>
                          {activeDetail.metrics.hungarian_nls.toFixed(4)}
                        </span>
                      </span>
                      <span>
                        BoC-F1={activeDetail.metrics.boc_f1.toFixed(4)}
                      </span>
                      <span>
                        CER=
                        <span className={scoreColor(activeDetail.metrics.cer, true)}>
                          {activeDetail.metrics.cer.toFixed(4)}
                        </span>
                      </span>
                      <span>{activeDetail.elapsed_sec.toFixed(1)}s</span>
                    </div>
                  )}
                  <pre className="max-h-[300px] overflow-auto break-all whitespace-pre-wrap text-sm leading-relaxed">
                    {hasError
                      ? activeDetail.error
                      : activeDetail.prediction || "(empty)"}
                  </pre>
                </>
              ) : (
                <div className="text-sm text-zinc-400">
                  No result for this image
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function App() {
  const [data, setData] = useState<AllResults | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/results-all")
      .then((r) => r.json())
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="p-8 text-red-600">
        Error: {error}
      </div>
    );
  }

  if (!data) {
    return <div className="p-8 text-zinc-500">Loading...</div>;
  }

  if (!data.models.length) {
    return (
      <div className="p-8 text-zinc-500">
        No evaluation results found. Run an evaluation first.
      </div>
    );
  }

  // Collect image IDs
  const imageIds: string[] = [];
  for (const m of data.models) {
    for (const d of m.details) {
      if (!imageIds.includes(d.image_id)) imageIds.push(d.image_id);
    }
  }

  return (
    <div className="mx-auto max-w-6xl p-6">
      <h1 className="mb-1 text-xl font-bold">OCR Evaluation Results</h1>
      <p className="mb-6 text-sm text-zinc-500">
        {data.n_images} images, {data.total_gt_chars} GT chars,{" "}
        {data.models.length} models
      </p>

      <section className="mb-8 overflow-x-auto rounded-lg border border-zinc-200 bg-white p-4">
        <h2 className="mb-3 text-sm font-bold text-zinc-700 uppercase tracking-wide">
          Leaderboard
        </h2>
        <Leaderboard models={data.models} />
      </section>

      <h2 className="mb-3 text-sm font-bold text-zinc-700 uppercase tracking-wide">
        Per-Image Comparison
      </h2>
      <div className="space-y-4">
        {imageIds.map((iid) => (
          <ImageComparison key={iid} imageId={iid} models={data.models} />
        ))}
      </div>

      <footer className="mt-8 text-xs text-zinc-400">
        NLS = Region Match NLS (primary) · BoC-F1 = Bag-of-Characters F1 · CER
        = Character Error Rate · NED = Normalized Edit Distance
      </footer>
    </div>
  );
}
