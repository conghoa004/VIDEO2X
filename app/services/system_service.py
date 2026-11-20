import os
import re
import shutil
import subprocess
from app.models.system import GPUInfo, SystemEnvInfo


class SystemService:
    """Service kiểm tra phần cứng GPU, Vulkan và môi trường hệ thống."""

    @staticmethod
    def get_gpu_info() -> GPUInfo:
        """Đọc và phân tích thông tin từ nvidia-smi."""
        gpu = GPUInfo()
        try:
            res = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                gpu.available = True
                gpu.raw_output = res.stdout

                m_driver = re.search(r"Driver Version:\s*([\d\.]+)", res.stdout)
                m_cuda = re.search(r"CUDA Version:\s*([\d\.]+)", res.stdout)
                if m_driver:
                    gpu.driver_ver = m_driver.group(1)
                if m_cuda:
                    gpu.cuda_ver = m_cuda.group(1)

                m_name = re.search(r"\|\s*\d+\s+([A-Za-z0-9\s]+?)\s+Off\s+\|", res.stdout)
                if m_name:
                    gpu.name = m_name.group(1).strip()

                m_vram = re.search(r"(\d+)MiB\s*/\s*(\d+)MiB", res.stdout)
                if m_vram:
                    gpu.vram_used = f"{int(m_vram.group(1)):,} MiB"
                    gpu.vram_total = f"{int(m_vram.group(2)):,} MiB"

                m_util = re.search(r"(\d+)%\s+Default", res.stdout)
                if m_util:
                    gpu.gpu_util = f"{m_util.group(1)}%"

                m_temp = re.search(r"(\d+)C\s+P", res.stdout)
                if m_temp:
                    gpu.temperature = f"{m_temp.group(1)}°C"
        except Exception as e:
            gpu.raw_output = f"Lỗi truy vấn GPU: {e}"

        return gpu

    @staticmethod
    def get_env_info(base_path: str = "/kaggle/working") -> SystemEnvInfo:
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
        try:
            res = subprocess.run(["vulkaninfo", "--summary"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                env.vulkan = True
                m_dev = re.search(r"deviceName\s*=\s*(.+)", res.stdout)
                env.vulkan_device = m_dev.group(1).strip() if m_dev else "Vulkan Device khả dụng"
        except Exception:
            pass

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
