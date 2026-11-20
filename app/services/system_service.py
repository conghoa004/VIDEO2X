import os
import re
import json
import shutil
import pathlib
import subprocess
from app.models.system import GPUInfo, SystemEnvInfo


class SystemService:
    """Service kiểm tra phần cứng GPU, Vulkan và môi trường hệ thống."""

    @staticmethod
    def _ensure_vulkan_icd() -> str:
        """Đảm bảo file nvidia_icd.json tồn tại nếu đang chạy trên Linux có card NVIDIA."""
        icd_path = "/usr/share/vulkan/icd.d/nvidia_icd.json"
        if os.path.exists(icd_path):
            return icd_path

        # Tự động tạo nvidia_icd.json nếu có quyền ghi
        try:
            icd_dir = pathlib.Path("/usr/share/vulkan/icd.d")
            icd_dir.mkdir(parents=True, exist_ok=True)
            with open(icd_path, "w") as f:
                json.dump({
                    "file_format_version": "1.0.0",
                    "ICD": {
                        "library_path": "libGLX_nvidia.so.0",
                        "api_version": "1.3.0"
                    }
                }, f, indent=4)
            return icd_path
        except Exception:
            return ""

    @staticmethod
    def get_gpu_info() -> GPUInfo:
        """Lấy thông số GPU NVIDIA từ nvidia-smi."""
        gpu = GPUInfo()
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw", "--format=csv,noheader,nounits"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if res.returncode == 0 and res.stdout.strip():
                parts = [p.strip() for p in res.stdout.strip().split(",")]
                if len(parts) >= 7:
                    gpu.available = True
                    gpu.name = parts[0]
                    gpu.driver_ver = parts[1]
                    gpu.vram_total = f"{parts[2]} MB"
                    gpu.vram_used = f"{parts[3]} MB"
                    gpu.gpu_util = f"{parts[4]}%"
                    gpu.temperature = f"{parts[5]} °C"
                    gpu.power = f"{parts[6]} W"

            # Lưu lại raw output tóm tắt
            raw_res = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if raw_res.returncode == 0:
                gpu.raw_output = raw_res.stdout
        except Exception as e:
            gpu.raw_output = f"Lỗi truy vấn GPU: {e}"

        return gpu

    @classmethod
    def get_env_info(cls, base_path: str = "/kaggle/working") -> SystemEnvInfo:
        """Kiểm tra sự hiện diện của video2x, ffmpeg, vulkan và dung lượng đĩa."""
        env = SystemEnvInfo()

        # Kiểm tra video2x
        try:
            res = subprocess.run(["video2x", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                env.video2x = True
                env.video2x_ver = res.stdout.strip()
        except Exception:
            pass

        # Kiểm tra ffmpeg
        try:
            res = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                env.ffmpeg = True
                m = re.search(r"ffmpeg version ([\w\.\-]+)", res.stdout)
                env.ffmpeg_ver = m.group(1) if m else "Có sẵn"
        except Exception:
            pass

        # Kiểm tra Vulkan
        cls._ensure_vulkan_icd()
        env_vars = os.environ.copy()
        if os.path.exists("/usr/share/vulkan/icd.d/nvidia_icd.json"):
            env_vars["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/nvidia_icd.json"
        env_vars.setdefault("__NV_PRIME_RENDER_OFFLOAD", "1")
        env_vars.setdefault("__VK_LAYER_NV_optimus", "NVIDIA_only")

        if shutil.which("vulkaninfo") is None:
            env.vulkan = False
            env.vulkan_device = "Chưa cài vulkan-tools"
        else:
            try:
                res = subprocess.run(
                    ["vulkaninfo", "--summary"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5,
                    env=env_vars
                )
                if res.returncode == 0:
                    env.vulkan = True
                    m_dev = re.search(r"deviceName\s*=\s*(.+)", res.stdout)
                    env.vulkan_device = m_dev.group(1).strip() if m_dev else "Vulkan Device khả dụng"
                else:
                    env.vulkan = False
                    env.vulkan_device = "Thiếu driver Vulkan (libnvidia-gl)"
            except Exception:
                env.vulkan = False
                env.vulkan_device = "Lỗi kiểm tra Vulkan"

        # Dung lượng ổ cứng
        check_dir = base_path if os.path.exists(base_path) else "."
        try:
            total, used, free = shutil.disk_usage(check_dir)
            env.disk_free_gb = round(free / (1024**3), 2)
            env.disk_total_gb = round(total / (1024**3), 2)
        except Exception:
            pass

        env.os_name = "Linux" if os.name == "posix" else "Windows"
        return env
