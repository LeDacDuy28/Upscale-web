import React, { useRef, useState } from "react";
import type { SelectedImageMeta } from "../types/api";

interface UploaderProps {
  selected: SelectedImageMeta | null;
  onSelect: (meta: SelectedImageMeta) => void;
  onError: (message: string) => void;
}

const MAX_FILE_BYTES = 20 * 1024 * 1024;
const ALLOWED_TYPES = new Set(["image/png", "image/jpeg", "image/webp"]);

export const Uploader: React.FC<UploaderProps> = ({ selected, onSelect, onError }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (file: File) => {
    if (!ALLOWED_TYPES.has(file.type)) {
      onError("Định dạng không hợp lệ. Vui lòng chọn ảnh PNG, JPG hoặc WebP.");
      return;
    }
    if (file.size > MAX_FILE_BYTES) {
      onError("Dung lượng ảnh vượt quá giới hạn 20 MB.");
      return;
    }

    const previewUrl = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      if (Math.max(img.width, img.height) > 4096) {
        URL.revokeObjectURL(previewUrl);
        onError("Kích thước ảnh vượt quá giới hạn 4096 px.");
        return;
      }
      onError("");
      onSelect({ file, previewUrl, width: img.width, height: img.height });
    };
    img.onerror = () => {
      URL.revokeObjectURL(previewUrl);
      onError("Không thể đọc dữ liệu ảnh.");
    };
    img.src = previewUrl;
  };

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file) handleFile(file);
      }}
      onClick={() => inputRef.current?.click()}
      className={`cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition ${
        dragging
          ? "border-indigo-400 bg-indigo-950/30"
          : "border-slate-700 bg-slate-900/60 hover:border-slate-500"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />

      {selected ? (
        <div className="space-y-3">
          <img
            src={selected.previewUrl}
            alt="Preview"
            className="mx-auto max-h-56 rounded-lg object-contain"
          />
          <div className="text-sm text-slate-300">
            <span className="font-medium">{selected.file.name}</span> —{" "}
            {selected.width}×{selected.height} px (
            {(selected.file.size / 1024 / 1024).toFixed(2)} MB)
          </div>
          <p className="text-xs text-slate-400">Nhấn hoặc kéo thả ảnh khác để thay thế</p>
        </div>
      ) : (
        <div className="space-y-2 py-8">
          <p className="text-base font-medium text-slate-200">
            Kéo thả ảnh vào đây hoặc nhấn để chọn file
          </p>
          <p className="text-xs text-slate-400">
            Hỗ trợ PNG, JPG, WebP (hỗ trợ kênh alpha) • Tối đa 20 MB & 4096 px
          </p>
        </div>
      )}
    </div>
  );
};
