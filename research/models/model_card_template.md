# Model Card: `<model_name>` (`<version>`)

## 1. Thông tin chung
- **Tên model:** `<realesrgan_x4plus_student / teacher>`
- **Phiên bản:** `v1`
- **Kiến trúc:** `RRDBNet` (`num_in_ch=3`, `num_out_ch=3`, `num_feat=48`, `num_block=16`, `num_grow_ch=24`, `scale=4`)
- **Trọng số nguồn (Hugging Face / GitHub Release):** `<URL>`
- **Giấy phép:** Apache 2.0 (kiểm tra điều khoản dataset trước khi thương mại hóa)

## 2. Huấn luyện & Knowledge Distillation
- **Degradation generator:** `<phiên bản RealisticDegradationGenerator_* đã chốt ở A1>`
- **Dataset:** `<DIV2K+ / RealSR / Unsplash + seed>`
- **Loss & Hyperparameters:** `<L1, Perceptual, GAN, Output KD, Feature KD, total_iter>`

## 3. Kết quả đánh giá
| Tập dữ liệu | PSNR (↑) | SSIM (↑) | NIQE (↓) |
| --- | --- | --- | --- |
| Set5 | — | — | — |
| Set14 | — | — | — |
| RealSR | — | — | — |

## 4. Benchmark hiệu năng
- **GPU kiểm thử:** `<Tên GPU>`
- **Tile khuyến nghị:** `256`
- **Thời gian trung bình (1080p, fp16):** `— ms`
- **VRAM đỉnh:** `— GB`
