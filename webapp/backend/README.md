# Phần B — Backend & Worker (`webapp/backend`)

Thư mục khởi tạo cho team Backend (**Hoàng, Thịnh, Thiên**), bám sát hợp đồng 5 endpoint trong [PROJECT_PLAN.md](../../PROJECT_PLAN.md) và `openapi.json`.

## Chạy nhanh tại máy (Local Dev)

```bash
cd webapp/backend
pip install -r requirements.txt
set USE_MOCK_ENGINE=1
uvicorn app.main:app --reload --port 8000
```

Truy cập tài liệu Swagger: `http://localhost:8000/docs`

## Chạy Test

```bash
cd webapp/backend
pytest -v
```

## Các đầu việc tiếp theo của Phần B
- **B1:** Chốt `openapi.json` cùng Phần C ở tuần 1.
- **B3–B4:** Kích hoạt `USE_REDIS_QUEUE=true` với `rq worker upscale` và bổ sung test OOM / timeout thực tế trên GPU.
- **B5–B6:** Bổ sung rate limit theo IP và scheduler dọn file định kỳ.
- **B9–B11:** Hoàn thiện Docker GPU worker (`nvidia/cuda`), CI GitHub Actions và deploy bản demo HTTPS.
