# Nhật ký thí nghiệm (Experiments Log — Phần A)

Theo **Quy tắc phối hợp** trong [PROJECT_PLAN.md](../PROJECT_PLAN.md), mỗi lần chạy huấn luyện Teacher, Student KD hoặc Ablation đều phải ghi lại config, commit, iteration và kết quả đo đạc vào bảng dưới đây (kèm log TensorBoard).

## Bảng theo dõi thí nghiệm

| Ngày | Thành viên | Loại | Model / Kiến trúc | Config YAML | Commit | Iter | Set5 (PSNR/SSIM/NIQE) | Set14 (PSNR/SSIM/NIQE) | RealSR (PSNR/SSIM/NIQE) | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-21 | *(mẫu)* | Baseline | `RealESRGAN_x4plus` (gốc, 64/23/32) | — | — | — | — | — | — | Đối chiếu gốc |
| — | — | Teacher | Fine-tune `x4plus` + Adv Degradation | `Real-ESRGAN/options/finetune_realesrgan_x4plus_pairdata.yml` | — | 575k | — | — | — | Checkpoint hiện có |
| — | — | Student (No KD) | `RRDBNet` 48/16/24 | — | — | — | — | — | — | Ablation A8 |
| — | — | Student (Output KD) | `RRDBNet` 48/16/24 (w=0.7) | — | — | — | — | — | — | Ablation A8 |
| — | — | Student (Full KD) | `RRDBNet` 48/16/24 (out=0.7, feat=0.5) | `Real-ESRGAN/options/finetune_realesrgan_x4plus_pairdata_student.yml` | — | 500k→600k | — | — | — | Student chính |

## Benchmark tốc độ & VRAM (Work item A12)

| Model | Tile | 512×512 (ms / VRAM) | 1080p (ms / VRAM) | 4K (ms / VRAM) | Ghi chú |
| --- | --- | --- | --- | --- | --- |
| `realesrgan_x4plus_student` | 0 / 256 / 512 | — | — | — | Chọn tile mặc định cho web |
| `realesrgan_x4plus_teacher` | 0 / 256 / 512 | — | — | — | — |
