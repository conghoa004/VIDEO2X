"""
Models Package (MVC - Model)
Chứa các Pydantic model định nghĩa cấu trúc dữ liệu cho video, tiến trình, và hệ thống.
"""
from app.models.video import VideoMetadata, ProcessingOptions, TaskProgress, TaskResult
from app.models.system import GPUInfo, SystemEnvInfo

__all__ = [
    "VideoMetadata",
    "ProcessingOptions",
    "TaskProgress",
    "TaskResult",
    "GPUInfo",
    "SystemEnvInfo"
]
