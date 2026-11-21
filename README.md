# 🎬 Video2X AI Studio Web UI

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)
![Video2X](https://img.shields.io/badge/Video2X-v6.2.0%20(C%2B%2B)-ff69b4?logo=cplusplus&logoColor=white)
![Vulkan API](https://img.shields.io/badge/Vulkan-1.3-red?logo=vulkan&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3-38bdf8?logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

<p align="center">
  <b>Trạm xử lý, nâng cấp độ phân giải và làm mượt video bằng Trí Tuệ Nhân Tạo (AI Super-Resolution & Optical Flow Frame Interpolation)</b>
</p>
<p align="center">
  Giao diện Web hiện đại viết bằng <b>FastAPI</b>, <b>TailwindCSS</b> và <b>Lucide Icons</b> cho công cụ dòng lệnh C++ native <b>Video2X v6.2.0</b>.
</p>

[Tính Năng](#-tính-năng-nổi-bật) • [Mô Hình AI](#-bảng-so-sánh--lựa-chọn-mô-hình-ai) • [Cài Đặt Cục Bộ](#-cài-đặt-và-khởi-chạy-cục-bộ) • [Chạy Trên Kaggle/Colab](#-chạy-trên-cloud-kaggle--google-colab) • [Cấu Trúc](#-cấu-trúc-dự-án) • [Xử Lý Sự Cố](#-xử-lý-sự-cố-thường-gặp)

</div>

---

## 📖 Giới thiệu

**Video2X AI Studio Web UI** cung cấp giao diện trực quan, thân thiện trên trình duyệt để thay thế việc phải gõ các câu lệnh terminal phức tạp của `video2x`. 

Ứng dụng tích hợp sâu với **Video2X v6.2.0 (C++ native)**, **FFmpeg 7** và **Vulkan Graphics API**, cho phép người dùng dễ dàng phóng to video từ 480p/720p lên **1080p, 2K, 4K** hoặc nội suy tăng FPS từ **24/30 FPS lên 60/120 FPS** mượt mà trên cả máy tính cá nhân (Windows, Linux) lẫn nền tảng điện toán đám mây GPU miễn phí (Kaggle, Google Colab).

> [!NOTE]
> Ứng dụng là tầng giao diện điều khiển (Frontend + Backend Orchestrator) và không đóng gói sẵn binary của Video2X, FFmpeg hay driver GPU. Video2X CLI và FFmpeg cần được cài đặt trên môi trường máy chủ lưu trữ.

---

## ✨ Tính năng nổi bật

### 🧠 Bộ xử lý AI đa dạng & Mạnh mẽ
- **Real-ESRGAN (Deep Learning)**: Tái tạo chi tiết sắc nét cho Anime, hoạt hình 2D và cảnh quay đời thực với hệ số phóng to linh hoạt **2x, 3x, 4x**.
- **Anime4K (libplacebo GLSL Shaders)**: Upscale video hoạt hình thời gian thực với tốc độ siêu tốc, hỗ trợ tùy chỉnh độ phân giải xuất ra theo ý muốn.
- **RIFE (Optical Flow Frame Interpolation)**: Tăng độ mượt của chuyển động bằng thuật toán suy đoán khung hình trung gian (nâng 2x lên **60 FPS** hoặc 4x lên **120 FPS**).

### ⚡ Cấu hình nhanh 1-Click (Quick Presets)
- ✨ **Anime 4K (Nét Cao)**: Tự động kích hoạt `realesrgan-plus-anime` ở mức scale 4x kèm CRF tối ưu.
- ⚡ **Anime Siêu Tốc**: Chuyển ngay sang `libplacebo` với shader Anime4K v4 để xử lý nhanh nhất.
- 🎬 **Đời Thực 4K**: Áp dụng mô hình `realesrgan-plus` chuyên biệt khử nhiễu và làm nét phim người thật/phong cảnh.
- 🚀 **Tăng 60 FPS Mượt**: Thiết lập mô hình `rife-v4.6` nhân đôi tốc độ khung hình.

### 🎛️ Nạp video linh hoạt & Kiểm tra thông số tự động
- **Kéo & Thả (Drag & Drop)**: Tải video trực tiếp từ máy khách thông qua giao diện trình duyệt với thanh tiến trình tải lên dạng chunked.
- **Đường dẫn Server (Path Mode)**: Trỏ trực tiếp đến các file có sẵn trên máy chủ hoặc Kaggle Datasets mà không cần upload lại.
- **Tự động đọc Metadata**: Tích hợp `ffprobe` hiển thị tức thì độ phân giải, tốc độ khung hình (FPS), thời lượng, định dạng codec và dung lượng file.

### 📊 Giám sát thời gian thực & Xem trước kết quả
- **Tiến trình thời gian thực (SSE)**: Theo dõi tiến độ chính xác từng khung hình (`frame/total`), tỷ lệ `%`, tốc độ render (`FPS`), thời gian đã chạy (`elapsed`) và thời gian ước tính còn lại (`remaining`).
- **Terminal Logs Viewer**: Xem trực tiếp log xuất ra từ Video2X và FFmpeg kèm tính năng tự cuộn (Auto-scroll), sao chép và xóa log.
- **Trình phát video so sánh**: Phát video trực tiếp trên trình duyệt, chuyển đổi linh hoạt giữa video gốc và video sau khi upscale, tích hợp nút tải video thành phẩm.
- **Giám sát phần cứng**: Hiển thị trạng thái hoạt động của GPU NVIDIA (VRAM sử dụng/tổng dung lượng, nhiệt độ, công suất, % sử dụng), Vulkan API và dung lượng ổ cứng khả dụng.

### 🔒 An toàn & Truy cập từ xa dễ dàng
- **Bảo mật phiên làm việc**: Tự động sinh mật khẩu ngẫu nhiên 20 ký tự in trong console khi server khởi chạy; xác thực qua Signed Cookie (HMAC-SHA256, `HttpOnly`, hết hạn sau 12h).
- **Cloudflare Tunnel tích hợp sẵn**: Khởi tạo link HTTPS công khai miễn phí chỉ với flag `--share` (tự động kích hoạt khi chạy trên môi trường Kaggle).
- **Phím tắt nhanh**: Nhấn `Ctrl + Enter` để bắt đầu xử lý ngay.

---

## 📊 Bảng so sánh & Lựa chọn mô hình AI

| Bộ xử lý (`processor`) | Mô hình / Shader | Tỷ lệ phóng | Thích hợp nhất cho | Đặc điểm & Đánh giá |
| :--- | :--- | :---: | :--- | :--- |
| **`realesrgan`** | `realesr-animevideov3` | **2x, 3x, 4x** | Hoạt hình, Anime, Clip 2D | ⚡ Tốc độ xử lý nhanh, khung hình ổn định, chuyển động mượt mà (Rất khuyên dùng) |
| **`realesrgan`** | `realesrgan-plus-anime` | **4x** | Anime độ phân giải cao | 🎨 Độ sắc nét và chi tiết đường viền cực cao (tốn nhiều thời gian xử lý hơn) |
| **`realesrgan`** | `realesrgan-plus` | **4x** | Phim người đóng, phong cảnh đời thực | 📷 Tái tạo cấu trúc bề mặt, khử nhiễu nén video thực tế |
| **`libplacebo`** | `anime4k-v4-a` / `b` / `c` | **Tùy biến** | Anime từ 480p đến 1080p | 🚀 Chạy bằng GPU shader trực tiếp, tốc độ siêu nhanh (nhanh gấp nhiều lần Real-ESRGAN) |
| **`libplacebo`** | `anime4k-v4.1-gan` | **Tùy biến** | Anime cần phục hồi chi tiết | 🌟 Chất lượng shader tối đa của Anime4K |
| **`rife`** | `rife-v4.6` | **2x, 4x (FPS)** | Mọi thể loại video | 🏃 Nội suy chuyển động tân tiến nhất, tăng từ 24/30 FPS lên 60/120 FPS |
| **`rife`** | `rife-anime` | **2x, 4x (FPS)** | Anime có hoạt họa chuyển cảnh vẽ tay | 🎯 Tối ưu riêng để không bị biến dạng nét vẽ hoạt hình |

---

## 🎛️ Cấu hình nén xuất video (FFmpeg Encoder)

Bạn có thể tinh chỉnh các thông số nén video tại bảng **Cấu hình xuất file & FFmpeg (Nâng cao)** trong giao diện:

- **Bộ mã hóa (Codec)**:
  - `libx264`: Bộ mã hóa CPU H.264 tiêu chuẩn, đem lại chất lượng hình ảnh sắc nét và độ tương thích cao nhất trên mọi thiết bị.
  - `h264_nvenc`: Tận dụng nhân mã hóa phần cứng của GPU NVIDIA (NVENC), tăng tốc độ xuất video vượt trội.
  - `libx265`: Bộ mã hóa H.265/HEVC, tiết kiệm từ 30% - 50% dung lượng file so với H.264 ở cùng mức chất lượng.
- **Chỉ số chất lượng CRF (Constant Rate Factor)**:
  - `14 - 16`: Chất lượng gần như nguyên gốc (Near-lossless), dung lượng file lớn.
  - `18 - 20`: **Mức cân bằng lý tưởng nhất** giữa độ sắc nét và dung lượng lưu trữ.
  - `22 - 26`: Nén sâu hơn, file xuất ra nhẹ, phù hợp cho video dài.
- **Tốc độ nén (Preset)**: `slow` (khuyên dùng để nén chất lượng tốt nhất), `medium`, `fast`, `ultrafast`.
- **Pixel Format**: Giữ nguyên `yuv420p` để video phát trực tiếp được trên trình duyệt web và thiết bị di động.

---

## 💻 Yêu cầu hệ thống

Trước khi khởi chạy ứng dụng, hãy đảm bảo hệ thống đã cài đặt:

1. **Python**: Phiên bản `3.10` trở lên.
2. **Video2X CLI**: Khuyên dùng phiên bản **v6.2.0 C++** ([Tải về từ GitHub Releases](https://github.com/k4yt3x/video2x/releases)). Lệnh `video2x` phải gọi được trong terminal.
3. **FFmpeg & FFprobe**: Cần phiên bản FFmpeg tương thích (Video2X v6.2.0 yêu cầu FFmpeg 7 trên Linux). Cả `ffmpeg` và `ffprobe` phải có trong `PATH`.
4. **Vulkan Graphics Driver**: Driver card đồ họa hỗ trợ **Vulkan 1.3** (NVIDIA, AMD hoặc Intel).

Kiểm tra sự hiện diện của các công cụ bằng lệnh:
```bash
video2x --version
ffmpeg -version
ffprobe -version
```

---

## 🚀 Cài đặt và Khởi chạy cục bộ

### 1. Clone repository & Tạo môi trường ảo

```bash
git clone https://github.com/conghoa004/VIDEO2X.git
cd VIDEO2X
```

#### Trên Windows (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py --host 127.0.0.1 --port 7860
```

#### Trên Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py --host 127.0.0.1 --port 7860
```

### 2. Đăng nhập vào giao diện Web
1. Mở trình duyệt và truy cập: [http://127.0.0.1:7860](http://127.0.0.1:7860).
2. Kiểm tra cửa sổ dòng lệnh Terminal nơi đang chạy server, tìm đoạn thông báo:
   ```text
   =================================================================
   🔐 Mật khẩu đăng nhập Video2X (chỉ dùng cho lần chạy này):
      AbCdEf123456XyZ98760
   =================================================================
   ```
3. Sao chép mật khẩu 20 ký tự này dán vào màn hình đăng nhập để vào giao diện quản lý.

---

## ☁️ Chạy trên Cloud (Kaggle / Google Colab)

Nếu không có GPU rời đủ mạnh trên máy tính cá nhân, bạn có thể chạy hoàn toàn miễn phí trên **Kaggle** (tận dụng GPU NVIDIA Tesla T4 x2 hoặc P100):

1. Mở file [video2x-kaggle.ipynb](video2x-kaggle.ipynb) trong repo này và import vào **Kaggle Notebooks**.
2. Trong phần cài đặt của Notebook (bên phải):
   - **Accelerator**: Chọn **GPU T4 x2** (hoặc GPU P100).
   - **Internet**: Bật sang **ON** (bắt buộc).
3. Chạy các bước trong notebook:
   - Cài đặt tự động Video2X v6.2.0, PPA FFmpeg 7 và thư viện NVIDIA Vulkan (`libnvidia-gl-*`).
   - Khởi chạy Web UI kèm tham số chia sẻ qua Cloudflare Tunnel:
     ```bash
     python run.py --port 7860 --share
     ```
4. Terminal sẽ tự động in đường dẫn HTTPS công khai có đuôi `.trycloudflare.com` cùng mật khẩu đăng nhập ngẫu nhiên. Bạn có thể mở link này trên điện thoại hoặc máy tính bất kỳ để điều khiển.

---

## ⚙️ Các tham số dòng lệnh (`run.py`)

Runner `run.py` hỗ trợ các tùy chọn cấu hình linh hoạt:

| Tham số | Mặc định | Ý nghĩa |
| :--- | :---: | :--- |
| `--host` | `0.0.0.0` | Địa chỉ IP máy chủ lắng nghe. Dùng `127.0.0.1` nếu chỉ muốn truy cập cục bộ trên máy. |
| `--port` | `7860` | Cổng mạng HTTP của ứng dụng. |
| `--share` | Tắt (`False`) | Tự động tải `cloudflared` và tạo link HTTPS công khai (luôn tự kích hoạt nếu chạy trong môi trường Kaggle). |
| `--reload` | Tắt (`False`) | Bật chế độ tự động reload server khi chỉnh sửa code trong quá trình phát triển (mỗi lần reload sẽ sinh mật khẩu mới). |

Ví dụ mở cổng công khai trên mạng LAN nội bộ:
```bash
python run.py --host 0.0.0.0 --port 7860
```

---

## 📁 Cấu trúc dự án

Dự án được xây dựng theo mô hình kiến trúc chuẩn **MVC (Model - View - Controller)** kết hợp với tầng Service tách biệt:

```text
VIDEO2X/
├── app/
│   ├── auth.py                  # Middleware xác thực session, ký mã HMAC-SHA256
│   ├── main.py                  # Khởi tạo FastAPI app, lifespan sinh mật khẩu & đăng ký router
│   ├── controllers/             # Tầng Controllers tiếp nhận & điều phối Request
│   │   ├── auth_controller.py   # Xử lý đăng nhập / đăng xuất
│   │   ├── home_controller.py   # Render giao diện trang chủ index
│   │   ├── video_controller.py  # Xử lý Upload, ffprobe metadata, video streaming & download
│   │   ├── task_controller.py   # Bắt đầu/hủy tác vụ, broadcast Server-Sent Events (SSE)
│   │   └── system_controller.py # Cung cấp API thông tin GPU, Vulkan, Disk, Video2X
│   ├── models/                  # Tầng Models định nghĩa dữ liệu (Pydantic Schemas)
│   │   ├── system.py            # Schemas GPUInfo, SystemEnvInfo
│   │   └── video.py             # Schemas ProcessingOptions, TaskProgress, TaskResult
│   ├── services/                # Tầng Services xử lý logic nghiệp vụ nền
│   │   ├── ffmpeg_service.py    # Phân tích thông số video qua ffprobe JSON
│   │   ├── system_service.py    # Kiểm tra nvidia-smi, vulkaninfo, tự tạo nvidia_icd.json
│   │   └── video2x_service.py   # Tạo lệnh video2x CLI, theo dõi tiến trình & parse SSE log
│   └── views/                   # Tầng Views hiển thị giao diện người dùng
│       ├── static/              # CSS tùy biến & Client Javascript
│       └── templates/           # Jinja2 Templates (base.html, index.html, login.html)
├── workspace/                   # Thư mục lưu trữ video mặc định khi chạy cục bộ
│   ├── input/                   # Chứa video tải lên từ máy tính
│   └── output/                  # Chứa video thành phẩm đã xử lý
├── requirements.txt             # Danh sách thư viện Python phụ thuộc
├── run.py                       # CLI Runner điều khiển môi trường Vulkan & Cloudflare Tunnel
├── video2x-kaggle.ipynb         # Jupyter Notebook tối ưu cho môi trường Kaggle GPU
└── README.md                    # Tài liệu hướng dẫn sử dụng dự án
```

---

## ❓ Xử lý sự cố thường gặp (Troubleshooting)

### 1. Không tìm thấy mật khẩu đăng nhập ở đâu?
Mật khẩu gồm 20 ký tự được tự động sinh ngẫu nhiên và in trực tiếp ra cửa sổ dòng lệnh Terminal ngay khi server FastAPI bắt đầu khởi chạy. Nếu bạn khởi động lại server hoặc kích hoạt chế độ `--reload`, mật khẩu mới sẽ được tạo thay thế.

### 2. Báo lỗi `Không tìm thấy lệnh 'video2x'` hoặc `'ffmpeg'`
Hãy kiểm tra xem bạn đã cài đặt Video2X CLI và FFmpeg vào máy hay chưa. Mở terminal mới và gõ thử:
```bash
video2x --version
ffmpeg -version
```
Nếu lệnh không nhận diện được, hãy thêm thư mục chứa file binary của các chương trình này vào biến môi trường hệ thống (`PATH`).

### 3. Lỗi Vulkan: `Failed to create Vulkan instance` (thường gặp trên Linux/Kaggle)
Nguyên nhân do môi trường thiếu thư viện đồ họa Vulkan NVIDIA tương ứng với driver hiện tại. Trên Linux/Kaggle, hãy cài đặt gói `libnvidia-gl-<phiên_bản_driver>` tương ứng:
```bash
# Kiểm tra phiên bản driver từ nvidia-smi, ví dụ bản 535:
sudo apt-get install -y libnvidia-gl-535
```
Dự án đã tích hợp tính năng tự động phát hiện và sinh file cấu hình `/usr/share/vulkan/icd.d/nvidia_icd.json` trong `run.py`.

### 4. Thông báo `Exit code: 139 / Segmentation fault` sau khi xử lý xong
Nếu trong log bạn thấy thông báo:
```text
Video processed successfully
Output written to: ...
Segmentation fault (core dumped)
```
Bạn hoàn toàn có thể yên tâm: **Video đã được xử lý thành công 100% và file kết quả đã được lưu hoàn tất**. Hiện tượng mã thoát 139 (SIGSEGV) xuất hiện là do thư viện Vulkan driver giải phóng tài nguyên đồ họa lúc kết thúc tiến trình C++, ứng dụng Web UI đã được thiết kế để nhận diện và xác thực file video thành phẩm thay vì chỉ dựa vào mã thoát.

### 5. Video sau khi tải về không phát được trên trình duyệt
Một số trình duyệt không hỗ trợ trực tiếp các codec nâng cao như H.265 (HEVC) hoặc profile nén 10-bit nếu thiếu bộ giải mã phần cứng. Trong phần cài đặt nâng cao của ứng dụng, hãy chọn **Bộ mã hóa là `libx264`** và **Pixel format là `yuv420p`** để đảm bảo tương thích hoàn hảo nhất.

---

## 🤝 Đóng góp & Phát triển

Mọi đóng góp, báo lỗi (Issues) hoặc đề xuất tính năng mới (Pull Requests) đều rất được hoan nghênh:

1. Fork dự án trên GitHub.
2. Tạo nhánh tính năng mới (`git checkout -b feature/tinh-nang-moi`).
3. Commit các thay đổi (`git commit -m 'Thêm tính năng mới'`).
4. Push lên nhánh của bạn (`git push origin feature/tinh-nang-moi`).
5. Tạo một **Pull Request** mới.

---

## 📜 Giấy phép (License)

Dự án được phân phối dưới giấy phép mã nguồn mở **MIT License**. Chi tiết tham khảo mã nguồn Video2X gốc tại [k4yt3x/video2x](https://github.com/k4yt3x/video2x).
