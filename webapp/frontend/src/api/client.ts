import type {
  HealthStatus,
  JobInfo,
  ModelOption,
  OutputFormat,
  UpscaleCreateResponse,
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const MOCK_MODELS: ModelOption[] = [
  {
    id: "realesrgan_x4plus_student",
    name: "Real-ESRGAN x4+ Student (KD)",
    description: "Model nhẹ (RRDBNet 48/16/24) chưng cất từ teacher, tối ưu tốc độ.",
    scales: [2, 4],
    default_tile: 256,
    weights_available: false,
  },
  {
    id: "realesrgan_x4plus_teacher",
    name: "Real-ESRGAN x4+ Teacher (Degradation)",
    description: "Model teacher fine-tune với degradation nâng cao (RRDBNet 64/23/32).",
    scales: [2, 4],
    default_tile: 256,
    weights_available: false,
  },
  {
    id: "realesrgan_x4plus_original",
    name: "Real-ESRGAN x4+ Original (Baseline)",
    description: "Model gốc đối chiếu.",
    scales: [2, 4],
    default_tile: 256,
    weights_available: false,
  },
];

const mockJobUrls = new Map<string, string>();
const mockJobStart = new Map<string, number>();

export async function fetchHealth(): Promise<HealthStatus> {
  if (USE_MOCK) {
    return { status: "ok", app_env: "mock", gpu_available: false, mock_engine: true };
  }
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error("Failed to check API health");
  return res.json();
}

export async function fetchModels(): Promise<ModelOption[]> {
  if (USE_MOCK) return MOCK_MODELS;
  const res = await fetch(`${API_BASE}/api/models`);
  if (!res.ok) throw new Error("Failed to fetch models");
  return res.json();
}

export async function submitUpscaleJob(
  file: File,
  model: string,
  scale: number,
  format: OutputFormat
): Promise<UpscaleCreateResponse> {
  if (USE_MOCK) {
    const jobId = `mock-${Date.now()}`;
    mockJobUrls.set(jobId, URL.createObjectURL(file));
    mockJobStart.set(jobId, Date.now());
    return { job_id: jobId, status: "queued" };
  }

  const form = new FormData();
  form.append("file", file);
  form.append("model", model);
  form.append("scale", String(scale));
  form.append("format", format);

  const res = await fetch(`${API_BASE}/api/upscale`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function fetchJobStatus(jobId: string): Promise<JobInfo> {
  if (USE_MOCK) {
    const started = mockJobStart.get(jobId) || Date.now();
    const elapsed = Date.now() - started;
    const progress = Math.min(100, Math.round((elapsed / 1200) * 100));
    return {
      job_id: jobId,
      status: progress >= 100 ? "done" : "processing",
      progress,
      message: progress >= 100 ? "Completed (Mock)" : "Processing mock tiles...",
      model: "realesrgan_x4plus_student",
      scale: 4,
      output_format: "png",
      processing_time_ms: progress >= 100 ? 1200 : null,
      error: null,
    };
  }

  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch job status");
  return res.json();
}

export function getJobResultUrl(jobId: string): string {
  if (USE_MOCK) {
    return mockJobUrls.get(jobId) || "";
  }
  return `${API_BASE}/api/jobs/${jobId}/result`;
}
