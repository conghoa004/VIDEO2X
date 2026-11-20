from typing import Optional
from pydantic import BaseModel


class GPUInfo(BaseModel):
    """Thông tin trạng thái GPU NVIDIA."""
    available: bool = False
    name: str = "Không tìm thấy GPU"
    driver_ver: str = "N/A"
    cuda_ver: str = "N/A"
    vram_total: str = "N/A"
    vram_used: str = "N/A"
    gpu_util: str = "0%"
    temperature: str = "N/A"
    power: str = "N/A"
    raw_output: str = ""


class SystemEnvInfo(BaseModel):
    """Thông tin các công cụ môi trường hệ thống."""
    video2x: bool = False
    video2x_ver: str = "Chưa cài đặt"
    ffmpeg: bool = False
    ffmpeg_ver: str = "Chưa cài đặt"
    vulkan: bool = False
    vulkan_device: str = "Chưa nhận diện"
    os_name: str = "Linux / Windows"
    disk_free_gb: float = 0.0
    disk_total_gb: float = 0.0
