import React from "react";
import type { JobInfo } from "../types/api";

interface JobProgressProps {
  job: JobInfo;
  onCancel: () => void;
}

export const JobProgress: React.FC<JobProgressProps> = ({ job, onCancel }) => {
  return (
    <div className="space-y-3 rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-200">
          Trạng thái: <span className="uppercase text-indigo-400">{job.status}</span>
        </span>
        <span className="font-mono text-slate-300">{job.progress}%</span>
      </div>

      <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full bg-indigo-500 transition-all duration-300"
          style={{ width: `${job.progress}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>{job.message || "Đang chờ xử lý..."}</span>
        {(job.status === "queued" || job.status === "processing") && (
          <button
            type="button"
            onClick={onCancel}
            className="text-rose-400 hover:text-rose-300"
          >
            Hủy theo dõi
          </button>
        )}
      </div>

      {job.error && (
        <p className="rounded-lg bg-rose-950/60 p-2.5 text-xs text-rose-300">
          Lỗi: {job.error}
        </p>
      )}
    </div>
  );
};
