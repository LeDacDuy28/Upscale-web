# Phần C — Frontend & UX (`webapp/frontend`)

Thư mục khởi tạo cho team Frontend (**Ngô, Dũng, Đức**), xây dựng bằng React + Vite + TypeScript + Tailwind CSS bám theo `webapp/backend/openapi.json`.

## Chạy nhanh tại máy (Local Dev)

```bash
cd webapp/frontend
npm install
npm run dev
```

### Chạy độc lập không cần Backend (Mock Mode — Work item C2)
```bash
VITE_USE_MOCK=true npm run dev
```

## Các component đã dựng sẵn cho Phần C
- `src/api/client.ts` & `src/types/api.ts`: API client khớp 5 endpoint trong `openapi.json`.
- `src/components/Uploader.tsx` (C3): Kéo thả, xem trước, kiểm tra kích thước & dung lượng.
- `src/components/SettingsPanel.tsx` (C4): Chọn model, scale x2/x4, định dạng xuất & tính kích thước đầu ra.
- `src/components/JobProgress.tsx` (C5): Thanh tiến độ polling & hủy theo dõi.
- `src/components/CompareViewer.tsx` (C6): Slider kéo so sánh trước/sau & tải về.
- `src/components/AboutModel.tsx` (C7): Khung bảng kết quả model (chờ số liệu từ A11/A12).
