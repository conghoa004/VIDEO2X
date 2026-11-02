# 🎬 Video2X on Cloud (Kaggle & Google Colab)

Bộ công cụ và hướng dẫn tối ưu để chạy **[Video2X v6.2.0](https://github.com/k4yt3x/video2x)** (phiên bản C++ native hiệu năng cao) trên nền tảng đám mây **Kaggle** và **Google Colab**, tận dụng sức mạnh GPU miễn phí (**NVIDIA Tesla T4 / P100**) để nâng cấp độ phân giải video (AI Video Upscaling) và làm mượt khung hình (Frame Interpolation).

---

## 📌 Giới thiệu dự án

**Video2X** là giải pháp mã nguồn mở hàng đầu trong lĩnh vực nâng cấp chất lượng video bằng AI (Super-Resolution). Phiên bản 6.x được viết lại hoàn toàn bằng **C/C++**, truyền khung hình trực tiếp qua RAM/VRAM bằng **Vulkan API** và **ncnn** mà không tốn dung lượng ổ cứng để trích xuất ảnh tạm.

Kho lưu trữ này cung cấp các notebook Jupyter được cấu hình sẵn, khắc phục triệt để các rào cản môi trường container trên **Kaggle** (như lỗi thiếu driver đồ họa Vulkan, xung đột phiên bản FFmpeg 7, và quản lý file đầu ra).

---

## 📁 Cấu trúc thư mục

| File | Nền tảng | Mô tả |
| :--- | :---: | :--- |
| **[`video2x-kaggle.ipynb`](./video2x-kaggle.ipynb)** | **Kaggle** | Bản notebook tối ưu hóa cho Kaggle, hỗ trợ nhập đường dẫn Dataset, cấu hình nén chất lượng cao, đã kiểm nghiệm thực tế trên Tesla T4 x2. |
| **[`Video2X_Kaggle.ipynb`](./Video2X_Kaggle.ipynb)** | **Kaggle** | Bản notebook Kaggle tích hợp giao diện Widget tải file trực tiếp từ máy tính lên. |
| **[`Video2X_Colab.ipynb`](./Video2X_Colab.ipynb)** | **Google Colab** | Bản notebook chính thức cho Google Colab, liên kết trực tiếp với Google Drive. |

---

## ⚡ Các tính năng nổi bật

* 🚀 **Tận dụng GPU đám mây miễn phí:** Chạy mượt mà trên NVIDIA Tesla T4 x2 hoặc P100 (15 - 16 GB VRAM).
* 🎨 **Mô hình AI đa dạng:**
  * **Real-ESRGAN** (`realesr-animevideov3`, `realesrgan-plus-anime`, `realesrgan-plus`): Phóng to video 2x, 3x, 4x cho cả Anime lẫn video đời thực.
  * **Anime4K (libplacebo)**: Sử dụng shader GLSL siêu tốc cho hoạt hình/anime.
  * **RIFE**: Tăng tốc độ khung hình (ví dụ 24fps/30fps lên 60fps/120fps).
* 🛠️ **Đã fix sẵn các lỗi môi trường trên Kaggle:**
  * ✅ Tự động thêm PPA và cài đặt **FFmpeg 7** (`libavcodec.so.61`).
  * ✅ Tự động nhận diện Driver NVIDIA và cài đặt thư viện đồ họa user-space (`libnvidia-gl-*`) để kích hoạt Vulkan.
  * ✅ Xử lý thông minh cảnh báo `Exit code: 139 (SIGSEGV)` lúc tắt chương trình.

---

## 🚀 Hướng dẫn sử dụng nhanh trên Kaggle

### 1. Khởi tạo Notebook
1. Truy cập [Kaggle Code](https://www.kaggle.com/code) ➡️ Chọn **New Notebook**.
2. Trên thanh menu, chọn **File** ➡️ **Upload notebook** ➡️ Chọn file **[`video2x-kaggle.ipynb`](./video2x-kaggle.ipynb)**.

### 2. Cài đặt môi trường bắt buộc (Notebook Settings)
Ở bảng điều khiển bên phải màn hình:
* **Accelerator:** Chọn **GPU T4 x2** (hoặc **GPU P100**).
* **Internet:** Gạt toggle sang **ON** (bắt buộc để tải Video2X và model AI).

### 3. Thực thi từng bước

```
[Bước 0: Check GPU] ➡️ [Bước 1: Cài đặt môi trường] ➡️ [Bước 2: Nạp video] ➡️ [Bước 3: Upscale] ➡️ [Bước 4: Tải về]
```

* **Bước 0:** Kiểm tra thông tin GPU NVIDIA và Driver Version.
* **Bước 1:** Cài đặt Video2X v6.2.0, FFmpeg 7 và cấu hình Vulkan ICD (~1 - 2 phút).
* **Bước 2:** Chỉ định đường dẫn video nguồn (từ Kaggle Dataset hoặc thư mục `/kaggle/working/input/`).
* **Bước 3:** Điều chỉnh tham số (Model, Scale, CRF) và bấm chạy.
* **Bước 4:** Tải video kết quả tại thư mục `/kaggle/working/output/` thông qua tab **Output** ở góc phải.

---

## 🎛️ Bảng tra cứu mô hình & Tham số tối ưu

### 1. Lựa chọn Model AI

| Bộ xử lý (`PROCESSOR`) | Mô hình (`MODEL`) | Hệ số Scale | Thích hợp cho | Đặc điểm |
| :--- | :--- | :---: | :--- | :--- |
| **`realesrgan`** | `realesr-animevideov3` | 2x, 3x, 4x | Hoạt hình, Anime, 2D | ⚡ Tốc độ nhanh nhất, chuyển động mượt mà (Khuyên dùng) |
| **`realesrgan`** | `realesrgan-plus-anime` | 4x | Anime độ nét cao | 🎨 Độ chi tiết và độ sắc nét cao nhất cho nét vẽ hoạt hình |
| **`realesrgan`** | `realesrgan-plus` | 4x | Người thật, phong cảnh | 📷 Khử nhiễu và khôi phục bề mặt ảnh chụp thực tế |
| **`libplacebo`** | `anime4k-v4-a / b / c` | Tùy biến | Phim hoạt hình 720p/1080p | ⚡ Chạy qua GLSL shader theo thời gian thực, tốc độ cực nhanh |

### 2. Tinh chỉnh FFmpeg Encoder

* **`CRF` (Chất lượng hình ảnh)**:
  * `16`: Chất lượng studio, cực nét (gần như lossless), file xuất ra nặng hơn.
  * `18 - 20`: **Mức cân bằng lý tưởng** giữa chất lượng hình ảnh sắc nét và dung lượng file vừa phải.
  * `22 - 24`: Dung lượng nhẹ, phù hợp cho video dài hoặc kết nối mạng chậm.
* **`PRESET`**: `slow` (khuyên dùng để thuật toán nén đạt hiệu quả cao nhất) hoặc `medium`.
* **`PIXFMT`**: Nên giữ `yuv420p` để đảm bảo tương thích với mọi trình duyệt, thiết bị điện thoại, TV.

---

## ❓ Xử lý sự cố thường gặp (Troubleshooting)

### 1. `error while loading shared libraries: libavcodec.so.61` (Exit code: 127)
* **Nguyên nhân:** Video2X v6.2.0 được biên dịch liên kết với FFmpeg 7, trong khi Ubuntu 22.04 mặc định chỉ có FFmpeg 4.
* **Khắc phục:** Đã được tích hợp sẵn trong **Bước 1** (tự động thêm PPA `ppa:ubuntuhandbook1/ffmpeg7`).

### 2. `Failed to create Vulkan instance` (Exit code: 255)
* **Nguyên nhân:** Container của Kaggle mặc định chỉ mount thư viện CUDA (`libcuda.so`), thiếu thư viện đồ họa Vulkan NVIDIA (`libGLX_nvidia.so.0` / `libnvidia-gl-*`).
* **Khắc phục:** Đoạn script ở **Bước 1** sẽ tự động nhận diện Driver Version của Kaggle và cài đặt đúng gói `libnvidia-gl-<version>` tương ứng.

### 3. `Exit code: 139 / Segmentation fault (core dumped)` sau khi hoàn thành
* **Nguyên nhân:** Sau khi video đã render xong 100% và FFmpeg đã đóng file, tiến trình C++ gọi hàm hủy `vkDestroyDevice()` trong môi trường headless container phát sinh lỗi giải phóng bộ nhớ lúc thoát.
* **Kết luận:** **Video của bạn đã hoàn thành 100% và file không bị ảnh hưởng.** Bạn chỉ cần vào tab **Output** và tải video về máy sử dụng bình thường.

---

## 📜 Bản quyền & Tham khảo

* **Video2X:** Được phát triển bởi [K4YT3X](https://github.com/k4yt3x) và cộng đồng theo giấy phép [ISC License](https://github.com/k4yt3x/video2x/blob/master/LICENSE).
* **Real-ESRGAN:** Phát triển bởi [xinntao/Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN).
* **Anime4K:** Phát triển bởi [bloc97/Anime4K](https://github.com/bloc97/Anime4K).

