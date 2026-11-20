from typing import Optional
from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    """Thông tin chi tiết về file video."""
    exists: bool = False
    filename: str = "Chưa chọn file"
    filepath: str = ""
    size_mb: float = 0.0
    resolution: str = "Không xác định"
    width: Optional[int] = None
    height: Optional[int] = None
    fps: str = "N/A"
    fps_val: Optional[float] = None
    duration: str = "N/A"
    duration_val: Optional[float] = None
    codec_name: str = "N/A"


class ProcessingOptions(BaseModel):
    """Tham số cấu hình xử lý video với Video2X."""
    # Nguồn video
    input_file: str = Field(..., description="Đường dẫn file video đầu vào")
    
    # Chế độ xử lý: 'realesrgan', 'libplacebo', 'rife'
    task_mode: str = Field(default="realesrgan", description="Chế độ xử lý: realesrgan | libplacebo | rife")
    
    # Real-ESRGAN options
    realesrgan_model: str = Field(default="realesr-animevideov3", description="Mô hình Real-ESRGAN")
    scale_factor: int = Field(default=4, ge=2, le=4, description="Hệ số phóng to (2, 3, 4)")
    
    # Anime4K (libplacebo) options
    shader_name: str = Field(default="anime4k-v4-a", description="Tên shader Anime4K")
    target_width: int = Field(default=0, ge=0, description="Chiều rộng xuất ra (0 = auto)")
    target_height: int = Field(default=0, ge=0, description="Chiều cao xuất ra (0 = auto)")
    
    # RIFE (Frame interpolation) options
    rife_model: str = Field(default="rife-v4.6", description="Mô hình RIFE")
    frame_rate_mul: int = Field(default=2, ge=2, le=4, description="Hệ số nhân FPS (2 hoặc 4)")
    
    # Cấu hình FFmpeg Encoder
    codec: str = Field(default="libx264", description="Bộ mã hóa: libx264 | h264_nvenc | libx265")
    preset: str = Field(default="slow", description="Tốc độ nén: ultrafast | fast | medium | slow | veryslow")
    crf: int = Field(default=18, ge=12, le=32, description="Chỉ số chất lượng CRF (càng thấp càng nét)")
    pixfmt: str = Field(default="yuv420p", description="Định dạng pixel (yuv420p tương thích cao nhất)")
    bitrate: int = Field(default=0, ge=0, description="Bitrate cụ thể (0 = dùng CRF)")


class TaskProgress(BaseModel):
    """Trạng thái tiến độ thực thi theo thời gian thực."""
    is_running: bool = False
    current_frame: int = 0
    total_frames: int = 0
    percent: float = 0.0
    fps: float = 0.0
    elapsed: str = "00:00:00"
    remaining: str = "00:00:00"
    status_text: str = "Sẵn sàng"
    latest_log: str = ""


class TaskResult(BaseModel):
    """Kết quả hoàn thành của tác vụ."""
    success: bool = False
    exit_code: Optional[int] = None
    output_filepath: str = ""
    output_filename: str = ""
    duration_seconds: float = 0.0
    input_meta: Optional[VideoMetadata] = None
    output_meta: Optional[VideoMetadata] = None
    message: str = ""
