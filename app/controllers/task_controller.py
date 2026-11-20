import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from app.models.video import ProcessingOptions, TaskProgress, TaskResult
from app.services.video2x_service import video2x_service

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

subscribers: list[asyncio.Queue] = []


async def broadcast_event(event_type: str, data: dict):
    """Gửi sự kiện đến toàn bộ client đang lắng nghe SSE."""
    dead_queues = []
    for q in subscribers:
        try:
            await q.put({"event": event_type, "data": data})
        except Exception:
            dead_queues.append(q)
    for dq in dead_queues:
        if dq in subscribers:
            subscribers.remove(dq)


@router.post("/start")
async def start_task(opt: ProcessingOptions, background_tasks: BackgroundTasks):
    """Khởi chạy tác vụ xử lý video."""
    if video2x_service.is_running:
        raise HTTPException(status_code=400, detail="Hiện đang có một tác vụ đang chạy. Hãy dừng nó trước khi chạy mới.")

    async def run_in_background():
        async for sse_item in video2x_service.run_task(opt):
            await broadcast_event(sse_item["event"], sse_item["data"])

    background_tasks.add_task(run_in_background)
    return {"status": "started", "message": "Đã khởi động tiến trình xử lý video!"}


@router.post("/abort")
async def abort_task():
    """Hủy tiến trình đang thực thi."""
    success = video2x_service.abort()
    if success:
        await broadcast_event("error", {"message": "Tiến trình đã bị người dùng hủy."})
        return {"status": "aborted", "message": "Đã gửi lệnh hủy tiến trình thành công!"}
    return {"status": "not_running", "message": "Không có tiến trình nào đang hoạt động."}


@router.get("/status", response_model=TaskProgress)
async def get_task_status():
    """Lấy trạng thái tiến độ hiện thời."""
    return video2x_service.latest_progress


@router.get("/stream")
async def sse_event_stream():
    """Server-Sent Events (SSE) stream tiến độ khung hình và log thời gian thực."""
    q: asyncio.Queue = asyncio.Queue()
    subscribers.append(q)

    async def event_generator() -> AsyncGenerator[str, None]:
        if video2x_service.is_running:
            cur = video2x_service.latest_progress.model_dump()
            yield f"event: progress\ndata: {json.dumps(cur)}\n\n"

        for log_line in list(video2x_service.log_history)[-30:]:
            yield f"event: log\ndata: {json.dumps({'text': log_line})}\n\n"

        try:
            while True:
                item = await q.get()
                ev_type = item.get("event", "message")
                ev_data = item.get("data", {})
                yield f"event: {ev_type}\ndata: {json.dumps(ev_data)}\n\n"
        except asyncio.CancelledError:
            if q in subscribers:
                subscribers.remove(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
