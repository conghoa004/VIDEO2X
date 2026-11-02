# 🎬 Video2X Cloud Runner (Kaggle & Google Colab)

> **Nâng cấp độ phân giải video (AI Video Upscaling) và tăng mượt khung hình (Frame Interpolation) hoàn toàn miễn phí trên Cloud GPU (NVIDIA Tesla T4 / P100).**

[![Kaggle](https://img.shields.io/badge/Kaggle-Notebook-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/code)
[![Google Colab](https://img.shields.io/badge/Google%20Colab-Ready-F9AB00?logo=googlecolab&logoColor=white)](https://colab.research.google.com/)
[![Video2X](https://img.shields.io/badge/Video2X-v6.2.0-red?logo=github)](https://github.com/k4yt3x/video2x)
[![GPU Accelerated](https://img.shields.io/badge/GPU-NVIDIA%20Vulkan-76B900?logo=nvidia&logoColor=white)](https://www.nvidia.com)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)

---

## 💡 Tổng quan

Kho lưu trữ này cung cấp các notebook chạy **[Video2X v6.2.0](https://github.com/k4yt3x/video2x)** (phiên bản C++ native tối ưu hiệu năng) trên nền tảng đám mây **Kaggle** và **Google Colab**. Bạn không cần sở hữu card đồ họa rời ở máy tính cá nhân nhưng vẫn có thể nâng cấp video lên **2K / 4K** với chất lượng cao nhất.

### ⚖️ So sánh Kaggle vs Google Colab

| Đặc điểm | Kaggle Notebooks (Khuyên dùng) | Google Colab (Bản Free) |
| :--- | :--- | :--- |
| **Phần cứng GPU** | **2x NVIDIA Tesla T4 (T4 x2)** hoặc P100 (15 - 16 GB VRAM) | 1x Tesla T4 (15 GB VRAM) |
| **Hạn mức miễn phí** | **30 giờ GPU / tuần** (rất hào phóng) | Giới hạn theo hạn ngạch động hàng ngày |
| **Độ ổn định phiên** | Chạy liên tục tới **12 tiếng**, ít bị disconnect đột ngột | Thường xuyên bị ngắt phiên nếu không tương tác |
| **Lưu trữ kết quả** | Tải trực tiếp từ tab **Output** hoặc lưu thành Dataset | Lưu tự động vào **Google Drive** |

---

## 📁 Các file trong dự án

* **[`video2x-kaggle.ipynb`](./video2x-kaggle.ipynb)** *(Bản chính)*: Notebook tối ưu cho Kaggle, hỗ trợ nạp video qua Kaggle Dataset hoặc đường dẫn direct, đã xử lý toàn bộ lỗi Vulkan và FFmpeg 7.
* **[`Video2X_Kaggle.ipynb`](./Video2X_Kaggle.ipynb)**: Bản Kaggle tích hợp thêm nút bấm chọn & tải file trực tiếp từ máy tính lên.
* **[`Video2X_Colab.ipynb`](./Video2X_Colab.ipynb)**: Bản chính thức dành cho Google Colab, mount trực tiếp với Google Drive.

---

## 🚀 Hướng dẫn nhanh trên Kaggle (3 phút)

### Bước 1: Tải Notebook lên Kaggle
1. Vào [kaggle.com/code](https://www.kaggle.com/code) ➡️ chọn **New Notebook**.
2. Chọn menu **File** ➡️ **Upload notebook** ➡️ tải lên file **[`video2x-kaggle.ipynb`](./video2x-kaggle.ipynb)**.

### Bước 2: Thiết lập cấu hình bắt buộc
Tại bảng điều khiển **Notebook Settings** (cột bên phải):
* **Accelerator:** Chọn **GPU T4 x2** (hoặc GPU P100).
* **Internet:** Gạt sang **ON** (bắt buộc để tải Video2X và model).

### Bước 3: Chạy từng bước
1. **Bước 0 & 1:** Chạy cell kiểm tra GPU và cài đặt môi trường (mất khoảng ~1.5 phút).
2. **Bước 2:** Nhập đường dẫn video nguồn vào `selected_input_file`:
   * *Từ Kaggle Dataset (Khuyên dùng cho video lớn):* `/kaggle/input/<tên-dataset>/video.mp4`
   * *Từ thư mục tải lên:* `/kaggle/working/input/video.mp4`
3. **Bước 3:** Điều chỉnh tham số (Model, Scale 2x/4x, CRF) và bấm chạy Upscale.
4. **Bước 4:** Vào tab **Output** (góc phải) ➡️ tải video đã hoàn thành về máy tính.

---

## 🎯 Cấu hình gợi ý theo từng thể loại Video

| Thể loại Video | Bộ xử lý (`PROCESSOR`) | Mô hình (`MODEL`) | Hệ số Scale | Mức CRF gợi ý | Ghi chú |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Anime / Phim hoạt hình 2D** | `realesrgan` | `realesr-animevideov3` | **2x / 4x** | `18 - 20` | ⚡ Tốc độ render nhanh nhất, chuyển động mượt, khử artifact tốt. |
| **Clip Lo-fi / Hoạt họa nét mảnh** | `realesrgan` | `realesrgan-plus-anime` | **4x** | `16 - 18` | 🎨 Chi tiết viền nét cực cao, màu sắc sắc sảo (chạy lâu hơn v3). |
| **Người thật / Cảnh quay đời thực** | `realesrgan` | `realesrgan-plus` | **4x** | `18 - 20` | 📷 Khử nhiễu ISO, tái tạo bề mặt da và chi tiết thực tế. |
| **Anime tập dài (cần tốc độ cao)** | `libplacebo` | `anime4k-v4-a` | Tự động | `20` | 🚀 Dùng shader GLSL thời gian thực, thời gian render nhanh gấp nhiều lần. |

---

## 🎛️ Ý nghĩa các tham số nén (FFmpeg)

* **`CRF` (Chất lượng nén video)**:
  * `16`: Chất lượng siêu nét (gần như lossless), bảo toàn tối đa viền hạt, file xuất ra khá nặng.
  * `18 - 20`: **Mức tối ưu được khuyên dùng** (cân bằng hoàn hảo giữa độ nét và dung lượng file).
  * `22 - 24`: Nén nhẹ, tiết kiệm dung lượng cho video thời lượng dài.
* **`PRESET`**: Giữ `slow` để thuật toán H.264 tối ưu hóa nén khung hình tốt nhất.
* **`PIXFMT`**: Luôn giữ `yuv420p` để đảm bảo tương thích mọi trình phát trên Windows, Mac, iOS, Android và trình duyệt.

---

## 🛠️ Các lỗi đã được xử lý sẵn (Troubleshooting)

Notebook trong repo này đã được viết mã để **tự động vá các lỗi đặc thù của Kaggle**:

1. **Lỗi thiếu FFmpeg 7 (`libavcodec.so.61: No such file or directory` - Exit 127):**
   * *Nguyên nhân:* Video2X v6.2.0 biên dịch dựa trên FFmpeg 7, trong khi Ubuntu 22.04 mặc định chỉ có FFmpeg 4.
   * *Khắc phục:* Bước 1 tự động thêm PPA `ubuntuhandbook1/ffmpeg7` và cập nhật bản FFmpeg mới nhất.

2. **Lỗi không nhận GPU (`Failed to create Vulkan instance` - Exit 255):**
   * *Nguyên nhân:* Docker của Kaggle mặc định chỉ cấp quyền CUDA, thiếu các thư viện đồ họa user-space Vulkan của NVIDIA.
   * *Khắc phục:* Bước 1 tự động dò phiên bản driver thực tế (`535`, `550`, `580`...) và cài đặt gói `libnvidia-gl` tương thích cùng file cấu hình `nvidia_icd.json`.

3. **Hiện tượng `Exit code: 139 / Segmentation fault (core dumped)` lúc kết thúc:**
   * *Bản chất:* Sau khi render xong 100% khung hình và file MP4 đã đóng hoàn tất, tiến trình gọi lệnh hủy Vulkan context lúc thoát (`exit(0)`) bị xung đột bộ nhớ trong môi trường container headless.
   * *Xác nhận:* **Video xuất ra đã hoàn chỉnh 100%**, không bị ảnh hưởng. Bạn có thể mở tab Output để xem và tải về sử dụng ngay.

---

## 📜 Giấy phép & Nguồn tham khảo

* [Video2X](https://github.com/k4yt3x/video2x) bởi [K4YT3X](https://github.com/k4yt3x) (ISC License).
* [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) bởi [Xintao Wang](https://github.com/xinntao).
* [Anime4K](https://github.com/bloc97/Anime4K) bởi [bloc97](https://github.com/bloc97).
