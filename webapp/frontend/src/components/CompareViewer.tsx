import React, { useState } from "react";

interface CompareViewerProps {
  beforeUrl: string;
  afterUrl: string;
  processingTimeMs?: number | null;
}

export const CompareViewer: React.FC<CompareViewerProps> = ({
  beforeUrl,
  afterUrl,
  processingTimeMs,
}) => {
  const [split, setSplit] = useState(50);

  return (
    <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-base font-semibold text-slate-100">
            So sánh Trước / Sau (Before / After)
          </h2>
          {processingTimeMs != null && (
            <p className="text-xs text-slate-400">
              Thời gian xử lý: {(processingTimeMs / 1000).toFixed(2)}s
            </p>
          )}
        </div>
        <a
          href={afterUrl}
          download="upscaled.png"
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"
        >
          Tải ảnh kết quả
        </a>
      </div>

      <div className="relative mx-auto aspect-video w-full overflow-hidden rounded-lg border border-slate-800 bg-slate-950">
        <img
          src={afterUrl}
          alt="After upscale"
          className="h-full w-full object-contain"
        />
        <div
          className="absolute inset-0 overflow-hidden"
          style={{ clipPath: `inset(0 ${100 - split}% 0 0)` }}
        >
          <img
            src={beforeUrl}
            alt="Before upscale"
            className="h-full w-full object-contain"
          />
        </div>
        <div
          className="pointer-events-none absolute inset-y-0 w-0.5 bg-indigo-400"
          style={{ left: `${split}%` }}
        />
      </div>

      <div className="flex items-center gap-3 text-xs text-slate-400">
        <span>Ảnh gốc</span>
        <input
          type="range"
          min={0}
          max={100}
          value={split}
          onChange={(e) => setSplit(Number(e.target.value))}
          className="flex-1 accent-indigo-500"
        />
        <span>Sau upscale ({split}%)</span>
      </div>
    </div>
  );
};
