# Web Upscale Ảnh dựa trên Real-ESRGAN (Degradation + Knowledge Distillation)

Dự án Group Project (10 tuần) xây dựng ứng dụng web upscale ảnh (tương tự Upscayl) sử dụng model **Real-ESRGAN** cải tiến bằng **Advanced Degradation** và **Knowledge Distillation (Teacher → Student)** từ nghiên cứu `RealESRGAN_Degradation_KD`.


## Kiến trúc 3 phần trong Repository

```text
.
├── PROJECT_PLAN.md                 # Tài liệu kế hoạch dự án (bản chính thức để nhóm chỉnh sửa)
├── CONTRIBUTING.md                 # Quy ước nhánh (main/dev/feature/*) & Code Review
├── docker-compose.yml              # Triển khai full stack (nginx, api, worker, redis, frontend)
│
├── research/                       # [PHẦN A - LÕI MODEL] Code nghiên cứu RealESRGAN_Degradation_KD
│   ├── BasicSR/                    # Core BasicSR
│   ├── Real-ESRGAN/                # Teacher & Student KD training configs
│   ├── degradation/                # 3 phiên bản RealisticDegradationGenerator
│   ├── src/                        # Custom model & subset training
│   ├── tools/                      # Scripts tiền xử lý & tính PSNR/SSIM/NIQE
│   ├── models/                     # Thư mục đặt trọng số .pth & model_card.md (không commit trọng số)
│   └── experiments.md              # Nhật ký thí nghiệm & bảng ablation
│
├── serve/                          # [GIAO DIỆN CHUNG A ↔ B] Module inference dùng chung
│   └── engine.py                   # Hàm upscale(...) bọc RealESRGANer + mock fallback
│
├── webapp/
│   ├── backend/                    # [PHẦN B - BACKEND & WORKER] FastAPI + Redis/RQ Worker
│   │   ├── openapi.json            # Hợp đồng API 5 endpoint (chốt tuần 1)
│   │   ├── app/                    # API, validation (magic bytes), worker OOM retry, cleanup 1h
│   │   └── tests/                  # Pytest unit & integration tests
│   └── frontend/                   # [PHẦN C - FRONTEND & UX] React + Vite + TypeScript + Tailwind
│       └── src/                    # Uploader, SettingsPanel, JobProgress, CompareViewer, AboutModel
│
├── deploy/                         # Cấu hình Nginx reverse proxy & deploy scripts
└── docs/                           # Bản sao PROJECT_PLAN.md & Architecture Decision Records (ADRs)
```

---


## Chạy nhanh để phát triển

### 1. Chạy toàn bộ bằng Docker Compose
```bash
docker compose up --build
```
Truy cập web tại `http://localhost` (Nginx proxy qua Frontend `/` và Backend `/api/`).

### 2. Chạy riêng Backend (chế độ Mock khi chưa có GPU/weights)
```bash
cd webapp/backend
pip install -r requirements.txt
set USE_MOCK_ENGINE=1
uvicorn app.main:app --reload --port 8000
```

### 3. Chạy riêng Frontend
```bash
cd webapp/frontend
npm install
npm run dev
```
*(Nếu chưa chạy Backend, dùng `VITE_USE_MOCK=true npm run dev` để test giao diện với mock API).*

---

## Trích dẫn & Giấy phép

Dự án phát hành theo giấy phép [Apache 2.0](./LICENSE), kế thừa từ **Real-ESRGAN** và **BasicSR**:
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)
- [BasicSR](https://github.com/XPixelGroup/BasicSR)
