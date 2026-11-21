# ADR-0001: Kiến trúc 3 tầng bất đồng bộ (React + FastAPI + Redis/GPU Worker)

- **Trạng thái:** Đề xuất (Accepted for Group Project)
- **Ngày:** 2026-11-21
- **Phạm vi:** Toàn hệ thống `RealESRGAN_Degradation_KD` Web Upscaler

## 1. Bối cảnh (Context)

Nhóm xây dựng ứng dụng web upscale ảnh (PNG/JPG/WebP, ảnh 1080p → 4K) sử dụng model Real-ESRGAN cải tiến (Degradation nâng cao + Knowledge Distillation Teacher → Student).
Thao tác suy luận mạng neural trên GPU/CPU mất từ vài giây đến vài chục giây mỗi ảnh và tiêu tốn nhiều VRAM. Nếu xử lý đồng bộ ngay trong HTTP request của API:
- Kết nối HTTP dễ bị timeout (504 Gateway Timeout).
- Một request ảnh 4K có thể gây tràn bộ nhớ (OOM) làm sập toàn bộ tiến trình API phục vụ người dùng khác.
- Khó mở rộng số lượng tiến trình xử lý khi nhiều người dùng upload đồng thời.

## 2. Quyết định (Decision)

Áp dụng mô hình **Modular Monolith + Async Worker Queue** chia 3 phần tách biệt trong cùng repository:

1. **Phần A (`research/` + `serve/`):** Giữ nguyên toàn bộ code nghiên cứu, huấn luyện, đánh giá trong `research/` và đóng gói giao diện suy luận chuẩn hóa tại `serve/engine.py` (`upscale(...)`).
2. **Phần B (`webapp/backend/` + `deploy/`):**
   - `FastAPI` đảm nhiệm xác thực upload (magic bytes, giới hạn kích thước/dung lượng), quản lý trạng thái job và phát sinh OpenAPI contract (`openapi.json`).
   - `Redis + RQ` làm hàng đợi job bất đồng bộ.
   - `Worker` tách riêng để chạy `serve.engine.upscale`, hỗ trợ tự giảm `tile` khi gặp CUDA OOM và tự dọn dẹp file sau 1 giờ.
3. **Phần C (`webapp/frontend/` + `docs/`):**
   - `React + Vite + TypeScript + Tailwind CSS` tiêu thụ API theo hợp đồng `openapi.json`, hỗ trợ chế độ mock (`VITE_USE_MOCK=true`) để phát triển song song trước khi Backend hoàn thiện.

## 3. Hệ quả & Đánh đổi (Consequences)

- **Tích cực:**
  - Ba nhóm thành viên (A, B, C) phát triển song song sau khi chốt 3 giao diện ở tuần 1 (`openapi.json`, `serve.engine.upscale`, quy ước tên checkpoint).
  - API nhẹ, phản hồi tức thì `job_id`, dễ scale thêm GPU worker độc lập.
  - Có sẵn cơ chế fallback (`USE_MOCK_ENGINE=1`) giúp chạy CI/CD và demo UI không cần GPU.
- **Tiêu cực / Ràng buộc:**
  - Phức tạp hơn khi cấu hình Docker Compose (cần `nginx`, `api`, `worker`, `redis`).
  - Cần cơ chế polling hoặc SSE để cập nhật tiến độ xử lý lên giao diện.
