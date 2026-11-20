import os
import aiofiles
import pathlib
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.models.video import VideoMetadata
from app.services.ffmpeg_service import FFmpegService

router = APIRouter(prefix="/api/video", tags=["Video"])

if os.path.exists("/kaggle/working"):
    INPUT_DIR = pathlib.Path("/kaggle/working/input")
    OUTPUT_DIR = pathlib.Path("/kaggle/working/output")
else:
    INPUT_DIR = pathlib.Path("./workspace/input")
    OUTPUT_DIR = pathlib.Path("./workspace/output")

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ProbeRequest(BaseModel):
    filepath: str


@router.post("/upload", response_model=VideoMetadata)
async def upload_video(file: UploadFile = File(...)):
    """Tiếp nhận tải lên file video từ máy người dùng và lưu vào thư mục input."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Tên file không hợp lệ.")

    dest_path = INPUT_DIR / file.filename

    async with aiofiles.open(dest_path, "wb") as out_file:
        while content := await file.read(1024 * 1024):  # 1MB buffer
            await out_file.write(content)

    meta = FFmpegService.get_metadata(str(dest_path))
    return meta


@router.post("/probe", response_model=VideoMetadata)
async def probe_video_path(req: ProbeRequest):
    """Trích xuất metadata của file video có sẵn trên đường dẫn server (như Kaggle Dataset)."""
    clean_path = req.filepath.strip()
    path = pathlib.Path(clean_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Không tìm thấy file: {clean_path}")

    meta = FFmpegService.get_metadata(str(path))
    return meta


@router.get("/stream/{filename}")
async def stream_video(filename: str, type: str = Query(default="output", pattern="^(input|output)$")):
    """Phát video trực tiếp với hỗ trợ xem trước trên trình duyệt."""
    target_dir = OUTPUT_DIR if type == "output" else INPUT_DIR
    target_path = target_dir / filename

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="Video không tồn tại.")

    return FileResponse(
        path=str(target_path),
        media_type="video/mp4",
        filename=filename
    )


@router.get("/download/{filename}")
async def download_video(filename: str, type: str = Query(default="output", pattern="^(input|output)$")):
    """Tải file video về máy tính cá nhân dưới dạng attachment."""
    target_dir = OUTPUT_DIR if type == "output" else INPUT_DIR
    target_path = target_dir / filename

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="File không tồn tại.")

    return FileResponse(
        path=str(target_path),
        filename=filename,
        media_type="application/octet-stream"
    )
