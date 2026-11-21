# Video2X Web UI

Giao diện web viết bằng FastAPI để chọn video, cấu hình và theo dõi tác vụ của chương trình dòng lệnh `video2x`. Ứng dụng không kèm binary Video2X hoặc FFmpeg; các model chọn trong giao diện được chuyển cho binary Video2X đã cài trên máy.

## Chức năng

- Đăng nhập bằng mật khẩu ngẫu nhiên được tạo mỗi lần server khởi động.
- Tải video lên từ trình duyệt hoặc chọn video theo đường dẫn trên máy chủ.
- Đọc thông tin video bằng `ffprobe`.
- Chọn một trong các chế độ xử lý có trong giao diện:
  - **Real-ESRGAN:** `realesr-animevideov3`, `realesrgan-plus-anime`, `realesrgan-plus`.
  - **Anime4K / libplacebo:** các shader Anime4K được liệt kê trong giao diện.
  - **RIFE:** nội suy khung hình với các model được liệt kê, hệ số 2x hoặc 4x.
- Cấu hình codec, preset, CRF, bitrate và pixel format.
- Theo dõi log và tiến độ qua SSE; xem trước, so sánh thông tin và tải video đầu ra.
- Xem thông tin môi trường như GPU, Vulkan, FFmpeg và Video2X.

Ứng dụng chỉ chạy **một tác vụ xử lý video tại một thời điểm**. Tùy chọn thực tế còn phụ thuộc phiên bản Video2X, model, Vulkan driver và các codec FFmpeg có trên máy.

## Yêu cầu

- Python 3.10 trở lên.
- Video2X CLI (giao diện hiện nhắm tới Video2X 6.2.0), lệnh `video2x` phải chạy được từ terminal.
- FFmpeg và `ffprobe` phải có trong `PATH`.
- Môi trường Vulkan phù hợp với Video2X và GPU/driver tương thích.
- Để chọn `h264_nvenc`, cần NVIDIA GPU/driver và bản FFmpeg có hỗ trợ NVENC. Các lựa chọn khác cũng phụ thuộc codec được biên dịch vào FFmpeg.
- Trình duyệt cần truy cập Internet để tải Tailwind CSS, Lucide Icons và font dùng từ CDN.

Kiểm tra các lệnh trước khi chạy app:

```bash
video2x --version
ffmpeg -version
ffprobe -version
```

## Cài đặt và chạy cục bộ

Clone repo, tạo môi trường ảo và cài các thư viện Python:

### Windows PowerShell

```powershell
git clone https://github.com/conghoa004/VIDEO2X.git
cd VIDEO2X
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py --host 127.0.0.1 --port 7860
```

### Linux

```bash
git clone https://github.com/conghoa004/VIDEO2X.git
cd VIDEO2X
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py --host 127.0.0.1 --port 7860
```

Mở [http://127.0.0.1:7860](http://127.0.0.1:7860). Khi server khởi động, terminal sẽ in mật khẩu đăng nhập. Nhập mật khẩu đó tại trang đăng nhập.

> `requirements.txt` chỉ cài các thư viện Python của giao diện web. Cần cài Video2X CLI và FFmpeg riêng; cấu hình Vulkan/driver và khả năng truy cập model phụ thuộc vào cài đặt Video2X trên máy.

## Đăng nhập

- Mỗi lần khởi động server được tạo một mật khẩu ngẫu nhiên 20 ký tự chữ và số. Mật khẩu chỉ được in trong terminal, không hiển thị trên trang web.
- Mật khẩu mới được tạo sau khi khởi động lại server; các phiên đăng nhập cũ cũng hết hiệu lực.
- Phiên đăng nhập dùng cookie HttpOnly và tự hết hạn sau 12 giờ. Có nút **Đăng xuất** trên thanh điều hướng.
- App dùng một mật khẩu chung, không có tài khoản hoặc phân quyền người dùng.
- Các trang và API yêu cầu đăng nhập; file tĩnh của giao diện được phục vụ công khai.

## Dùng trên mạng nội bộ hoặc qua Cloudflare Tunnel

Để cho phép thiết bị khác trong mạng truy cập, bind server vào mọi giao diện mạng:

```bash
python run.py --host 0.0.0.0 --port 7860
```

Sau đó truy cập bằng địa chỉ IP của máy chủ và cổng `7860`. Việc truy cập còn phụ thuộc firewall và cấu hình mạng.

Có thể tạo Cloudflare Quick Tunnel bằng:

```bash
python run.py --port 7860 --share
```

Trên Kaggle, `run.py` tự bật tunnel khi phát hiện thư mục `/kaggle`; không cần truyền `--share`. Tunnel cần Internet. Nếu chưa có `cloudflared`, runner sẽ thử tải binary vào thư mục chạy hiện tại. Giữ riêng URL và mật khẩu nếu không muốn người khác truy cập app.

Trên Google Colab hoặc môi trường khác, dùng `--share` nếu muốn tạo tunnel. Runner không tự cài Video2X, FFmpeg hay các gói hệ thống GPU cho Kaggle/Colab.

## Quy trình xử lý video

1. Khởi động server, lấy mật khẩu từ terminal và đăng nhập.
2. Chọn **Tải lên** để gửi video từ máy đang dùng trình duyệt, hoặc chọn chế độ đường dẫn để trỏ tới file mà server có thể đọc.
3. Chọn Real-ESRGAN, Anime4K hoặc RIFE và chỉnh các thông số cần thiết.
4. Bấm **Bắt đầu xử lý**. Tiến độ và log được cập nhật trong trang.
5. Khi hoàn tất, xem trước và tải kết quả về.

Đường dẫn lưu mặc định:

| Môi trường | Video tải lên | Video đầu ra |
| --- | --- | --- |
| Chạy cục bộ | `./workspace/input` | `./workspace/output` |
| Kaggle | `/kaggle/working/input` | `/kaggle/working/output` |

Các đường dẫn cục bộ tính từ thư mục làm việc hiện tại. File đầu ra dùng tên video nguồn kèm hậu tố `_v2x_<timestamp>` và giữ phần mở rộng của video nguồn. Khả năng xem trước phụ thuộc định dạng và codec mà trình duyệt hỗ trợ.

## Tùy chọn dòng lệnh

`run.py` hỗ trợ các tùy chọn sau:

| Tùy chọn | Mặc định | Mô tả |
| --- | --- | --- |
| `--host` | `0.0.0.0` | Địa chỉ bind của server. Dùng `127.0.0.1` để chỉ truy cập từ máy đang chạy app. |
| `--port` | `7860` | Cổng HTTP. |
| `--share` | Tắt | Tải/chạy Cloudflare Tunnel và in URL công khai. Tự bật khi phát hiện Kaggle. |
| `--reload` | Tắt | Bật tự tải lại khi phát triển; mỗi lần app khởi động lại sẽ tạo mật khẩu mới. |

Chạy `python run.py --help` để xem trợ giúp.

## Cấu trúc dự án

```text
app/
├── auth.py                         # Phiên đăng nhập và middleware bảo vệ route
├── main.py                         # Tạo FastAPI app, lifespan và đăng ký router
├── controllers/
│   ├── auth_controller.py          # Đăng nhập và đăng xuất
│   ├── home_controller.py          # Trang chính
│   ├── video_controller.py         # Tải lên, probe, stream và tải video
│   ├── task_controller.py          # Chạy/hủy tác vụ và SSE
│   └── system_controller.py        # API thông tin hệ thống
├── models/                         # Schema Pydantic
├── services/                       # Tích hợp Video2X, FFmpeg và hệ thống
└── views/
    ├── templates/
    │   ├── base.html
    │   ├── index.html
    │   └── login.html
    └── static/
        └── js/app.js
run.py                              # CLI runner, cấu hình Vulkan và tunnel
requirements.txt                    # Thư viện Python
video2x-kaggle.ipynb                # Notebook Kaggle
```

## Xử lý sự cố

- **Không thấy mật khẩu:** xem terminal nơi chạy `python run.py`; mật khẩu được in khi ứng dụng FastAPI bắt đầu.
- **Không tìm thấy Video2X/FFmpeg:** xác nhận `video2x`, `ffmpeg` và `ffprobe` chạy được từ cùng terminal dùng để khởi động app.
- **Lỗi Vulkan hoặc GPU:** kiểm tra driver, Vulkan runtime và model tương ứng. App không tự cài những thành phần này.
- **Không truy cập được Cloudflare URL:** kiểm tra kết nối Internet và log của `cloudflared`; Quick Tunnel là địa chỉ tạm thời.
- **Video đầu ra không phát trong trình duyệt:** thử tải file về và mở bằng trình phát hỗ trợ codec của file.

Các thư viện Python được liệt kê trong [requirements.txt](requirements.txt).
