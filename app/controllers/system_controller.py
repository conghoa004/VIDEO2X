from fastapi import APIRouter
from app.models.system import GPUInfo, SystemEnvInfo
from app.services.system_service import SystemService

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/gpu", response_model=GPUInfo)
async def get_gpu_status():
    """Lấy thông tin card đồ họa NVIDIA và VRAM."""
    return SystemService.get_gpu_info()


@router.get("/env", response_model=SystemEnvInfo)
async def get_env_status():
    """Lấy thông tin các công cụ phần mềm (video2x, ffmpeg, vulkan) và dung lượng đĩa."""
    return SystemService.get_env_info()
