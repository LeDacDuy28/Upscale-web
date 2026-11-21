export type JobStatus = "queued" | "processing" | "done" | "failed";

export type OutputFormat = "png" | "jpg" | "webp";

export interface ModelOption {
  id: string;
  name: string;
  description: string;
  scales: number[];
  default_tile: number;
  weights_available: boolean;
}

export interface UpscaleCreateResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobInfo {
  job_id: string;
  status: JobStatus;
  progress: number;
  message?: string | null;
  model: string;
  scale: number;
  output_format: string;
  processing_time_ms?: number | null;
  error?: string | null;
}

export interface HealthStatus {
  status: string;
  app_env: string;
  gpu_available: boolean;
  mock_engine: boolean;
}

export interface SelectedImageMeta {
  file: File;
  previewUrl: string;
  width: number;
  height: number;
}
