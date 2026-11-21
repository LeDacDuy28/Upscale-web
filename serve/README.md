# Serve Engine (`serve/engine.py`) — Giao diện chung giữa Phần A & Phần B

Module này hiện thực đầu việc **A14** trong [PROJECT_PLAN.md](../PROJECT_PLAN.md): cung cấp một điểm gọi thống nhất `serve.engine.upscale(...)` để Backend Worker (Phần B) và CLI dùng chung mà không phụ thuộc vào script nghiên cứu rời rạc trong `research/`.

## 1. Contract hàm `upscale`

```python
from serve.engine import upscale, list_available_models

output_img, meta = upscale(
    image="path/to/input.png",           # str | Path | np.ndarray
    output_path="path/to/output.png",    # Optional
    model_name="realesrgan_x4plus_student",
    scale=4.0,
    tile=256,
    fp16=True,
    progress_callback=lambda pct, msg: print(f"{pct}% - {msg}"),
)
```

### Hỗ trợ định dạng
- Ảnh 8-bit RGB, Grayscale (`L`), RGBA (kênh alpha giữ nguyên), và ảnh 16-bit.
- Khi chưa có file trọng số `.pth` trong `research/models/` hoặc đặt `USE_MOCK_ENGINE=1`, engine tự động fallback sang chế độ mock (`INTER_CUBIC`) để Phần B & C phát triển và kiểm thử pipeline end-to-end ngay từ tuần 1.

## 2. Quy ước thư mục trọng số (Work item A10)

Đặt file trọng số theo cấu trúc:
```text
research/models/
├── realesrgan_x4plus_student/v1/net_g_ema.pth
├── realesrgan_x4plus_teacher/v1/net_g_ema.pth
└── realesrgan_x4plus_original/v1/RealESRGAN_x4plus.pth
```
Có thể ghi đè đường dẫn gốc chứa trọng số qua biến môi trường `MODELS_DIR`.
