import { useEffect, useState } from "react";
import {
  fetchHealth,
  fetchJobStatus,
  fetchModels,
  getJobResultUrl,
  submitUpscaleJob,
} from "./api/client";
import { AboutModel } from "./components/AboutModel";
import { CompareViewer } from "./components/CompareViewer";
import { JobProgress } from "./components/JobProgress";
import { SettingsPanel } from "./components/SettingsPanel";
import { Uploader } from "./components/Uploader";
import type {
  HealthStatus,
  JobInfo,
  ModelOption,
  OutputFormat,
  SelectedImageMeta,
} from "./types/api";

export default function App() {
  const [models, setModels] = useState<ModelOption[]>([]);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [selectedModel, setSelectedModel] = useState("realesrgan_x4plus_student");
  const [scale, setScale] = useState(4);
  const [format, setFormat] = useState<OutputFormat>("png");
  const [imageMeta, setImageMeta] = useState<SelectedImageMeta | null>(null);
  const [error, setError] = useState("");
  const [activeJob, setActiveJob] = useState<JobInfo | null>(null);

  useEffect(() => {
    fetchModels().then(setModels).catch(() => {});
    fetchHealth().then(setHealth).catch(() => {});
  }, []);

  useEffect(() => {
    if (!activeJob) return;
    if (activeJob.status === "done" || activeJob.status === "failed") return;

    const timer = window.setInterval(async () => {
      try {
        const next = await fetchJobStatus(activeJob.job_id);
        setActiveJob(next);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Polling failed");
      }
    }, 600);

    return () => window.clearInterval(timer);
  }, [activeJob]);

  const handleSubmit = async () => {
    if (!imageMeta) return;
    setError("");
    try {
      const created = await submitUpscaleJob(imageMeta.file, selectedModel, scale, format);
      setActiveJob({
        job_id: created.job_id,
        status: created.status,
        progress: 0,
        model: selectedModel,
        scale,
        output_format: format,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start upscale job");
    }
  };

  const isRunning = activeJob?.status === "queued" || activeJob?.status === "processing";

  return (
    <div className="mx-auto min-h-screen max-w-5xl space-y-6 px-4 py-8">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Real-ESRGAN KD Image Upscaler
          </h1>
          <p className="text-sm text-slate-400">
            Nâng cấp độ phân giải ảnh dựa trên Advanced Degradation &amp; Knowledge Distillation
          </p>
        </div>
        {health && (
          <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300">
            API: {health.status} • {health.gpu_available ? "GPU" : "CPU"}
            {health.mock_engine ? " (Mock)" : ""}
          </span>
        )}
      </header>

      {error && (
        <div className="rounded-lg border border-rose-800 bg-rose-950/60 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Uploader
            selected={imageMeta}
            onSelect={(meta) => {
              setImageMeta(meta);
              setActiveJob(null);
            }}
            onError={setError}
          />
        </div>
        <div>
          <SettingsPanel
            models={models}
            selectedModel={selectedModel}
            scale={scale}
            format={format}
            imageMeta={imageMeta}
            disabled={isRunning}
            onModelChange={setSelectedModel}
            onScaleChange={setScale}
            onFormatChange={setFormat}
            onSubmit={handleSubmit}
          />
        </div>
      </div>

      {activeJob && (
        <JobProgress job={activeJob} onCancel={() => setActiveJob(null)} />
      )}

      {activeJob?.status === "done" && imageMeta && (
        <CompareViewer
          beforeUrl={imageMeta.previewUrl}
          afterUrl={getJobResultUrl(activeJob.job_id)}
          processingTimeMs={activeJob.processing_time_ms}
        />
      )}

      <AboutModel />
    </div>
  );
}
