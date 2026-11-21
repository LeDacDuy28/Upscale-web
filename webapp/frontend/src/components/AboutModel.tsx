import React from "react";

export const AboutModel: React.FC = () => {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
      <h2 className="mb-2 text-base font-semibold text-slate-100">
        Về Model: Real-ESRGAN (Advanced Degradation + Knowledge Distillation)
      </h2>
      <p className="mb-4 text-xs text-slate-400">
        Bảng đối chiếu số liệu từ Work item A11 & A12 (cập nhật sau khi hoàn tất benchmark Set5, Set14, RealSR).
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="border-b border-slate-800 text-slate-400">
            <tr>
              <th className="py-2 pr-4">Model</th>
              <th className="py-2 pr-4">Kiến trúc RRDBNet</th>
              <th className="py-2 pr-4">PSNR (Set14 / RealSR)</th>
              <th className="py-2 pr-4">NIQE (↓)</th>
              <th className="py-2">Thời gian 1080p</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/70">
            <tr>
              <td className="py-2 pr-4 font-medium">RealESRGAN_x4plus (Gốc)</td>
              <td className="py-2 pr-4">64 feat / 23 block / 32 grow</td>
              <td className="py-2 pr-4">—</td>
              <td className="py-2 pr-4">—</td>
              <td className="py-2">—</td>
            </tr>
            <tr>
              <td className="py-2 pr-4 font-medium">Teacher (Adv Degradation)</td>
              <td className="py-2 pr-4">64 feat / 23 block / 32 grow</td>
              <td className="py-2 pr-4">—</td>
              <td className="py-2 pr-4">—</td>
              <td className="py-2">—</td>
            </tr>
            <tr>
              <td className="py-2 pr-4 font-medium text-indigo-400">Student (KD)</td>
              <td className="py-2 pr-4">48 feat / 16 block / 24 grow</td>
              <td className="py-2 pr-4">—</td>
              <td className="py-2 pr-4">—</td>
              <td className="py-2">—</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
};
