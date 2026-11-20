import os
import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.controllers import home_router, video_router, task_router, system_router

# Đường dẫn thư mục gốc của app
APP_DIR = pathlib.Path(__file__).parent.resolve()
TEMPLATES_DIR = APP_DIR / "views" / "templates"
STATIC_DIR = APP_DIR / "views" / "static"

def create_app() -> FastAPI:
    """Khởi tạo và cấu hình ứng dụng FastAPI theo mô hình MVC."""
    app = FastAPI(
        title="Video2X AI Studio Web UI",
        description="Giao diện Web AI Video Super-Resolution & Interpolation xây dựng bằng FastAPI, TailwindCSS và Lucide Icons",
        version="1.0.0"
    )

    # Cấu hình Jinja2 Templates (Views)
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.state.templates = templates

    # Mount Static Files (CSS, JS)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Đăng ký Controllers
    app.include_router(home_router)
    app.include_router(video_router)
    app.include_router(task_router)
    app.include_router(system_router)

    return app


app = create_app()
