# Hướng dẫn đóng góp & Quy ước Git (CONTRIBUTING)

Tài liệu này quy định quy trình phối hợp giữa **3 phần (A: Model, B: Backend/Infra, C: Frontend/Docs)** theo đầu việc **B8** trong [PROJECT_PLAN.md](./PROJECT_PLAN.md).

## 1. Cấu trúc nhánh (Branching Strategy)

- `main`: Nhánh ổn định nhất (chỉ merge từ `dev` sau khi vượt qua các mốc M1–M4 và CI xanh). Không push trực tiếp vào `main`.
- `dev`: Nhánh tích hợp chung của cả nhóm. Mọi PR tính năng đều merge vào `dev`.
- `feature/<phan>-<ma-cong-viec>-<mo-ta>`: Nhánh làm việc cá nhân/nhóm nhỏ.
  - Ví dụ Phần A: `feature/A-A14-serve-engine`
  - Ví dụ Phần B: `feature/B-B3-redis-worker`
  - Ví dụ Phần C: `feature/C-C3-uploader-ui`

## 2. Quy tắc Pull Request & Code Review

1. **Tạo PR vào `dev`**, tiêu đề ghi rõ mã công việc (ví dụ: `[B2] Thêm validate magic bytes cho upload`).
2. **Review chéo bắt buộc:** Mỗi PR phải có **ít nhất 1 thành viên ở phần khác** duyệt để kiểm tra không làm vỡ hợp đồng giao tiếp giữa các phần:
   - Hợp đồng B ↔ C: `webapp/backend/openapi.json`
   - Hợp đồng A ↔ B: `serve/engine.py` (`upscale`) & cấu trúc `research/models/`
3. **CI phải xanh:** `pytest` (backend) và `npm run build` (frontend) không báo lỗi trước khi merge.

## 3. Quy tắc làm việc với dữ liệu & trọng số lớn

- **KHÔNG commit** dataset ảnh lớn, file `.pth`, `.onnx`, `.state` vào Git (đã cấu hình trong `.gitignore`).
- Trọng số model đã chốt được đẩy lên Hugging Face / GitHub Release và ghi nhận vào `research/experiments.md` + `model_card.md`.
- Không đặt đường dẫn tuyệt đối của máy cá nhân (`/storage/student12/...`, `/content/...`, `C:\Users\...`) trong code dùng chung; sử dụng biến môi trường trong `.env`.

## 4. Các mốc kiểm tra (Milestones)

- **M1 (29/11/2026):** Chốt `openapi.json`, đặc tả `serve/engine.py`, quy ước checkpoint, wireframe Figma.
- **M2 (27/12/2026):** Upload → upscale → so sánh → tải về chạy E2E qua Docker Compose.
- **M3 (10/01/2027):** Student KD hoàn tất, có bảng ablation & benchmark, thử nghiệm ONNX.
- **M4 (31/01/2027):** Đóng băng code trước 1 tuần, demo công khai, báo cáo & video.
