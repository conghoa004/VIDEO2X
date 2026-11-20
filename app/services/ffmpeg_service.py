import os
import json
import pathlib
import subprocess
from typing import Optional
from app.models.video import VideoMetadata


class FFmpegService:
    """Service trích xuất metadata và xử lý các thao tác video cơ bản."""

    @staticmethod
    def get_metadata(video_path: str) -> VideoMetadata:
        """Trích xuất chi tiết metadata từ file video thông qua ffprobe."""
        meta = VideoMetadata(
            exists=False,
            filename=os.path.basename(video_path) if video_path else "",
            filepath=video_path or ""
        )
        
        if not video_path:
            return meta
            
        path = pathlib.Path(video_path)
        if not path.exists() or not path.is_file():
            return meta

        meta.exists = True
        meta.filename = path.name
        meta.filepath = str(path.resolve())
        meta.size_mb = round(path.stat().st_size / (1024 * 1024), 2)

        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,duration,codec_name",
                "-of", "json",
                str(path)
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                if "streams" in data and len(data["streams"]) > 0:
                    s = data["streams"][0]
                    w = s.get("width")
                    h = s.get("height")
                    if w and h:
                        meta.width = int(w)
                        meta.height = int(h)
                        meta.resolution = f"{w} × {h}"

                    meta.codec_name = s.get("codec_name", "N/A")

                    fps_raw = s.get("r_frame_rate", "")
                    if "/" in fps_raw:
                        num, den = map(float, fps_raw.split("/"))
                        if den > 0:
                            fps_calc = num / den
                            meta.fps_val = round(fps_calc, 2)
                            meta.fps = f"{fps_calc:.2f} FPS"

                    dur = s.get("duration")
                    if dur:
                        dur_float = float(dur)
                        meta.duration_val = round(dur_float, 2)
                        meta.duration = f"{dur_float:.1f}s"
        except Exception:
            pass

        return meta
