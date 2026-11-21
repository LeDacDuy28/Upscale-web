import React from "react";
import type { ModelOption, OutputFormat, SelectedImageMeta } from "../types/api";

interface SettingsPanelProps {
  models: ModelOption[];
  selectedModel: string;
  scale: number;
  format: OutputFormat;
  imageMeta: SelectedImageMeta | null;
  disabled: boolean;
  onModelChange: (id: string) => void;
  onScaleChange: (scale: number) => void;
  onFormatChange: (fmt: OutputFormat) => void;
  onSubmit: () => void;
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({
  models,
  selectedModel,
  scale,
  format,
  imageMeta,
  disabled,
  onModelChange,
  onScaleChange,
  onFormatChange,
  onSubmit,
}) => {
  const currentModel = models.find((m) => m.id === selectedModel) || models[0];
  const targetSize = imageMeta
    ? `${imageMeta.width * scale} × ${imageMeta.height * scale} px`
    : "—";

  return (
    <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <h2 className="text-base font-semibold text-slate-100">Cài đặt Upscale</h2>

      <div>
        <label className="mb-1 block text-xs font-medium text-slate-400">Model</label>
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          disabled={disabled}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
        >
          {models.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
        {currentModel && (
          <p className="mt-1 text-xs text-slate-400">{currentModel.description}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-400">Tỷ lệ (Scale)</label>
          <div className="flex gap-2">
            {(currentModel?.scales || [2, 4]).map((s) => (
              <button
                key={s}
                type="button"
                disabled={disabled}
                onClick={() => onScaleChange(s)}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition ${
                  scale === s
                    ? "border-indigo-500 bg-indigo-600 text-white"
                    : "border-slate-700 bg-slate-950 text-slate-300 hover:border-slate-500"
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-1 block text-xs font-medium text-slate-400">Định dạng xuất</label>
          <select
            value={format}
            onChange={(e) => onFormatChange(e.target.value as OutputFormat)}
            disabled={disabled}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100"
          >
            <option value="png">PNG (Lossless / Alpha)</option>
            <option value="jpg">JPG</option>
            <option value="webp">WebP</option>
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between rounded-lg bg-slate-950/70 px-3 py-2 text-xs text-slate-300">
        <span>Kích thước đầu ra dự kiến:</span>
        <span className="font-semibold text-indigo-400">{targetSize}</span>
      </div>

      <button
        type="button"
        disabled={disabled || !imageMeta}
        onClick={onSubmit}
        className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        Bắt đầu Upscale
      </button>
    </div>
  );
};
