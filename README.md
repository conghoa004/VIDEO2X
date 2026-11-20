# 🎬 Video2X AI Studio (FastAPI + TailwindCSS MVC Web UI)

> **Giao diện Web AI chuyên nghiệp xây dựng theo kiến trúc MVC chuẩn mực (FastAPI, TailwindCSS CDN, Lucide Icons) hỗ trợ nâng cấp độ phân giải video (Super-Resolution) và làm mượt khung hình (Frame Interpolation) trên Cloud GPU (Kaggle / Colab) và máy trạm Local.**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TailwindCSS](https://img.shields.io/badge/Frontend-TailwindCSS-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Lucide Icons](https://img.shields.io/badge/Icons-Lucide%20Icons-F56565?logo=lucide&logoColor=white)](https://lucide.dev/)
[![Kaggle](https://img.shields.io/badge/Kaggle-1--Click%20Ready-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/code)
[![Video2X](https://img.shields.io/badge/Video2X-v6.2.0-red?logo=github)](https://github.com/k4yt3x/video2x)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)

---

## 🏛️ Kiến trúc phần mềm chuẩn MVC (Model - View - Controller)

Toàn bộ ứng dụng web được tổ chức khoa học, phân tách rõ ràng giữa **Mô hình dữ liệu (Model)**, **Giao diện hiển thị (View)**, **Bộ điều hướng xử lý (Controller)** và **Dịch vụ nghiệp vụ (Service)**:

```text
D:\WORK_SPACE\VIDEO2X\
├── app/
│   ├── __init__.py
│   ├── main.py                     # Entry point khởi tạo FastAPI app, cấu hình Jinja2 & Static
│   ├── models/                     # [M] MODEL: Định nghĩa Pydantic schemas
│   │   ├── __init__.py
│   │   ├── video.py                # VideoMetadata, ProcessingOptions, TaskProgress, TaskResult
│   │   └── system.py               # GPUInfo, SystemEnvInfo
│   ├── controllers/                # [C] CONTROLLER: Xử lý Request & Router API
│   │   ├── __init__.py
│   │   ├── home_controller.py      # Render giao diện Single Page Application (GET /)
│   │   ├── video_controller.py     # Upload, đọc thông số (ffprobe), stream video, tải về
│   │   ├── task_controller.py      # Bắt đầu, hủy tiến trình, Server-Sent Events (SSE) stream
│   │   └── system_controller.py    # Kiểm tra GPU (nvidia-smi), Vulkan, ổ cứng
│   ├── services/                   # SERVICE: Xử lý nghiệp vụ & kết nối CLI
│   │   ├── __init__.py
│   │   ├── video2x_service.py      # Chạy tiến trình CLI, parse regex frame=X/Y, quản lý hủy
│   │   ├── ffmpeg_service.py       # Trích xuất thông số (độ phân giải, fps, thời lượng)
│   │   └── system_service.py       # Đọc thông số phần cứng NVIDIA, Vulkan ICD
│   └── views/                      # [V] VIEW: Giao diện người dùng
│       ├── templates/
│       │   ├── base.html           # Layout chuẩn tích hợp TailwindCSS CDN & Lucide Icons CDN
│       │   └── index.html          # Dashboard giao diện hiện đại (Dark slate theme)
│       └── static/
│           ├── css/
│           │   └── style.css       # Hiệu ứng glow, thanh cuộn terminal, animation
│           └── js/
│               └── app.js          # Reactive controller (Kéo thả, SSE live logs/progress)
├── run.py                          # CLI Runner & tự động cấu hình Cloudflare Tunnel (--share)
├── requirements.txt                # FastAPI, Uvicorn, Jinja2, Aiofiles...
├── .gitignore                      # Cấu hình bỏ qua file tạm, cache, video output, venv
└── video2x-kaggle.ipynb            # Notebook phiên bản chạy lệnh truyền thống
```

---

## 🎨 Điểm nổi bật về Công nghệ & Giao diện

1. **⚡ Backend hiệu năng cao (FastAPI & Asyncio):**
   * Sử dụng **Server-Sent Events (SSE)** tại `/api/tasks/stream` để truyền tiến độ khung hình (`frame=96/192`, `1.05 FPS`, thời gian còn lại) và streaming log theo thời gian thực mà không gây nghẽn luồng.
   * Hỗ trợ phát video trực tiếp với Range Requests trên trình duyệt.
2. **💎 Frontend hiện đại (TailwindCSS CDN & Lucide Icons chính thống):**
   * Tích hợp CDN chính hãng từ [TailwindCSS](https://cdn.tailwindcss.com) và thư viện icon vector [Lucide Icons](https://lucide.dev) (`unpkg.com/lucide`).
   * Giao diện Dark Glassmorphism lấy tone màu xanh thẫm Slate 950 sang trọng, thanh tiến trình hiển thị hiệu ứng `progress-glow`.
3. **🧠 Hỗ trợ trọn vẹn các thuật toán của Video2X v6.2.0:**
   * **Real-ESRGAN:** `realesr-animevideov3` (Anime 2x/3x/4x), `realesrgan-plus-anime` (Siêu nét 4x), `realesrgan-plus` (Người thật 4x).
   * **Anime4K (libplacebo):** Shader GLSL siêu tốc (`anime4k-v4-a`, `anime4k-v4.1-gan`...).
   * **RIFE (Frame Interpolation):** Nhân đôi hoặc nhân 4 FPS (30 FPS ➡️ 60 / 120 FPS).
   * **Tùy chỉnh nén FFmpeg:** Codec `libx264` / `h264_nvenc`, thanh trượt `CRF` (14 - 28), `Preset`, `Pixel Format` (`yuv420p`).

---

## 🚀 Khởi chạy Web UI

### 1. Khởi chạy trên Cloud GPU (Kaggle / Google Colab) với Link công khai
Chỉ cần chạy lệnh sau trên terminal hoặc cell notebook:
```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Khởi chạy server FastAPI kèm đường dẫn Public HTTPS qua Cloudflare Tunnel:
python run.py --share --port 7860
```
Terminal sẽ in ra đường link HTTPS công khai dạng:
```text
=================================================================
🚀 GIAO DIỆN WEB CÔNG KHAI ĐÃ SẴN SÀNG:
👉 https://xxxx.trycloudflare.com
=================================================================
```
Bạn chỉ cần nhấp vào link để mở Web UI trên bất kỳ trình duyệt máy tính hoặc điện thoại nào!

---

### 2. Khởi chạy Cục bộ (Local Machine)
Nếu máy tính của bạn có card NVIDIA:
```bash
# 1. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 2. Khởi chạy Web UI tại http://localhost:7860
python run.py

# (Tùy chọn) Mở link công khai qua Internet:
python run.py --share
```

# 2. Khởi chạy server FastAPI
python run.py --port 7860

# 3. Mở public tunnel ra ngoài internet (tùy chọn)
python run.py --port 7860 --share
```

Truy cập trên trình duyệt: `http://127.0.0.1:7860`.

---

## 📜 Bản quyền & Tham khảo

* **Video2X:** Bản quyền thuộc về [K4YT3X](https://github.com/k4yt3x) (ISC License).
* **FastAPI:** Bản quyền thuộc về [Sebastián Ramírez (tiangolo)](https://github.com/tiangolo/fastapi).
* **TailwindCSS:** [Tailwind Labs](https://tailwindcss.com/).
* **Lucide Icons:** [Lucide Project](https://lucide.dev/).
