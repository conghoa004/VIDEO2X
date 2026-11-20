import os
import re
import time
import shlex
import asyncio
import pathlib
import subprocess
from typing import AsyncGenerator, Optional, List
from collections import deque

from app.models.video import ProcessingOptions, TaskProgress, TaskResult
from app.services.ffmpeg_service import FFmpegService


class Video2XService:
    """Service quản lý tiến trình thực thi Video2X và stream log/tiến độ thời gian thực."""

    def __init__(self, output_dir: Optional[pathlib.Path] = None):
        if output_dir:
            self.output_dir = output_dir
        elif os.path.exists("/kaggle/working"):
            self.output_dir = pathlib.Path("/kaggle/working/output")
        else:
            self.output_dir = pathlib.Path("./workspace/output")
            
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_process: Optional[subprocess.Popen] = None
        self.is_aborted: bool = False
        self.is_running: bool = False
        
        # Buffer lưu log gần nhất cho client kết nối sau
        self.log_history: deque = deque(maxlen=500)
        self.latest_progress: TaskProgress = TaskProgress()
        self.latest_result: Optional[TaskResult] = None

    def abort(self) -> bool:
        """Hủy tiến trình đang chạy."""
        self.is_aborted = True
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                time.sleep(1)
                if self.current_process.poll() is None:
                    self.current_process.kill()
                self.is_running = False
                self.log_history.append("[ABORT] Tiến trình đã bị hủy bởi người dùng.")
                return True
            except Exception as e:
                self.log_history.append(f"[ABORT ERROR] Không thể hủy tiến trình: {e}")
                return False
        return False

    def build_command(self, opt: ProcessingOptions, output_file: pathlib.Path) -> List[str]:
        """Tạo danh sách đối số dòng lệnh cho video2x."""
        cmd = [
            "video2x",
            "--input", str(opt.input_file),
            "--output", str(output_file),
            "--codec", opt.codec,
            "--log-level", "info",
            "-e", f"preset={opt.preset}",
            "-e", f"crf={opt.crf}"
        ]

        if opt.bitrate > 0:
            cmd.extend(["--bit-rate", str(opt.bitrate)])

        if opt.pixfmt != "auto":
            cmd.extend(["--pix-fmt", opt.pixfmt])

        if opt.task_mode == "realesrgan":
            cmd.extend([
                "--processor", "realesrgan",
                "--realesrgan-model", opt.realesrgan_model,
                "--scaling-factor", str(opt.scale_factor)
            ])
        elif opt.task_mode == "libplacebo":
            cmd.extend([
                "--processor", "libplacebo",
                "--libplacebo-shader", opt.shader_name
            ])
            if opt.target_width > 0:
                cmd.extend(["--width", str(opt.target_width)])
            if opt.target_height > 0:
                cmd.extend(["--height", str(opt.target_height)])
        elif opt.task_mode == "rife":
            cmd.extend([
                "--processor", "rife",
                "--rife-model", opt.rife_model,
                "--frame-rate-mul", str(opt.frame_rate_mul)
            ])

        return cmd

    async def run_task(self, opt: ProcessingOptions) -> AsyncGenerator[dict, None]:
        """
        Khởi chạy tiến trình video2x và yield các sự kiện theo thời gian thực (SSE format).
        Yields dict: {"event": "progress"|"log"|"complete"|"error", "data": {...}}
        """
        self.is_aborted = False
        self.is_running = True
        self.latest_progress = TaskProgress(is_running=True, status_text="Đang chuẩn bị...")
        self.latest_result = None
        self.log_history.clear()

        input_path = pathlib.Path(opt.input_file)
        if not input_path.exists():
            self.is_running = False
            err_msg = f"File đầu vào không tồn tại: {opt.input_file}"
            yield {"event": "error", "data": {"message": err_msg}}
            return

        input_meta = FFmpegService.get_metadata(str(input_path))

        timestamp = int(time.time())
        suffix = input_path.suffix if input_path.suffix else ".mp4"
        out_filename = f"{input_path.stem}_v2x_{timestamp}{suffix}"
        output_file = self.output_dir / out_filename

        cmd = self.build_command(opt, output_file)
        cmd_str = " ".join(shlex.quote(c) for c in cmd)

        start_log = f"🚀 Khởi chạy: {cmd_str}\n" + "-" * 60
        self.log_history.append(start_log)
        yield {"event": "log", "data": {"text": start_log}}

        env = os.environ.copy()
        if os.path.exists("/usr/share/vulkan/icd.d/nvidia_icd.json"):
            env["VK_ICD_FILENAMES"] = "/usr/share/vulkan/icd.d/nvidia_icd.json"
            env["__NV_PRIME_RENDER_OFFLOAD"] = "1"
            env["__VK_LAYER_NV_optimus"] = "NVIDIA_only"

        start_time = time.time()
        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env
            )
        except FileNotFoundError:
            self.is_running = False
            err_msg = "Không tìm thấy lệnh 'video2x'. Hãy đảm bảo Video2X đã được cài đặt."
            self.log_history.append(err_msg)
            yield {"event": "error", "data": {"message": err_msg}}
            return
        except Exception as e:
            self.is_running = False
            err_msg = f"Lỗi khởi chạy tiến trình: {e}"
            self.log_history.append(err_msg)
            yield {"event": "error", "data": {"message": err_msg}}
            return

        progress_regex = re.compile(
            r"frame=(\d+)/(\d+)\s*\(([\d\.]+)%\);\s*fps=([\d\.]+);\s*elapsed=([^;]+);\s*remaining=([^\r\n]+)"
        )

        loop = asyncio.get_running_loop()
        last_progress_yield = 0

        while True:
            if self.is_aborted:
                yield {"event": "error", "data": {"message": "Tiến trình đã bị người dùng hủy."}}
                break

            line = await loop.run_in_executor(None, self.current_process.stdout.readline)
            if not line and self.current_process.poll() is not None:
                break

            if line:
                line_str = line.strip()
                m = progress_regex.search(line_str)
                if m:
                    current_frame = int(m.group(1))
                    total_frames = int(m.group(2))
                    percent = float(m.group(3))
                    fps_val = float(m.group(4))
                    elapsed = m.group(5)
                    remaining = m.group(6)

                    self.latest_progress = TaskProgress(
                        is_running=True,
                        current_frame=current_frame,
                        total_frames=total_frames,
                        percent=percent,
                        fps=fps_val,
                        elapsed=elapsed,
                        remaining=remaining,
                        status_text=f"Đang xử lý: {percent:.1f}% ({current_frame}/{total_frames})",
                        latest_log=line_str
                    )

                    now = time.time()
                    if now - last_progress_yield > 0.3:
                        last_progress_yield = now
                        yield {"event": "progress", "data": self.latest_progress.model_dump()}
                else:
                    self.log_history.append(line_str)
                    yield {"event": "log", "data": {"text": line_str}}

        exit_code = self.current_process.poll()
        self.is_running = False
        duration = round(time.time() - start_time, 2)

        # Kiểm tra file đầu ra thành công
        is_success = output_file.exists() and output_file.stat().st_size > 10240

        if is_success:
            out_meta = FFmpegService.get_metadata(str(output_file))
            result = TaskResult(
                success=True,
                exit_code=exit_code,
                output_filepath=str(output_file.resolve()),
                output_filename=output_file.name,
                duration_seconds=duration,
                input_meta=input_meta,
                output_meta=out_meta,
                message=f"Xử lý hoàn tất trong {duration}s!"
            )
            self.latest_result = result
            yield {"event": "complete", "data": result.model_dump()}
        else:
            fail_msg = f"Tiến trình kết thúc với mã lỗi: {exit_code}"
            yield {"event": "error", "data": {"message": fail_msg, "exit_code": exit_code}}


# Global singleton service instance
video2x_service = Video2XService()
