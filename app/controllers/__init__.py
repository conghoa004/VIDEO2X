"""
Controllers Package (MVC - Controller)
Chứa các API router tiếp nhận yêu cầu từ client, điều phối qua service và trả về view/JSON.
"""
from app.controllers.home_controller import router as home_router
from app.controllers.video_controller import router as video_router
from app.controllers.task_controller import router as task_router
from app.controllers.system_controller import router as system_router

__all__ = [
    "home_router",
    "video_router",
    "task_router",
    "system_router"
]
