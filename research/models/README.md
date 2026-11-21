# Quy ước lưu trữ trọng số (Work item A10)

Không commit file `.pth`, `.onnx`, `.state` lên Git. Tải trọng số từ Google Drive / Hugging Face / GitHub Release và đặt đúng theo cấu trúc sau để `serve/engine.py` tự nhận diện:

```text
research/models/
├── realesrgan_x4plus_student/
│   └── v1/
│       ├── net_g_ema.pth
│       └── model_card.md
├── realesrgan_x4plus_teacher/
│   └── v1/
│       ├── net_g_ema.pth
│       └── model_card.md
└── realesrgan_x4plus_original/
    └── v1/
        ├── RealESRGAN_x4plus.pth
        └── model_card.md
```

Tham khảo mẫu `model_card_template.md` khi xuất bản phiên bản mới.
