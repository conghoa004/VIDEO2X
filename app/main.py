import os
import pathlib
import secrets
import string
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.auth import AuthenticationMiddleware
from app.controllers import auth_router, home_router, video_router, task_router, system_router

# Đường dẫn thư mục gốc của app
APP_DIR = pathlib.Path(__file__).parent.resolve()
TEMPLATES_DIR = APP_DIR / "views" / "templates"
STATIC_DIR = APP_DIR / "views" / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    alphabet = string.ascii_letters + string.digits
    password = "".join(secrets.choice(alphabet) for _ in range(20))
    app.state.login_password = password
    app.state.session_signing_key = secrets.token_bytes(32)
    app.state.active_sessions = set()

    print("\n" + "=" * 65)
    print("🔐 Mật khẩu đăng nhập Video2X (chỉ dùng cho lần chạy này):")
    print(f"   {password}")
    print("=" * 65 + "\n", flush=True)
    yield


def create_app() -> FastAPI:
    """Khởi tạo và cấu hình ứng dụng FastAPI theo mô hình MVC."""
    app = FastAPI(
        lifespan=lifespan,
        title="Video2X AI Studio Web UI",
        description="Giao diện Web AI Video Super-Resolution & Interpolation xây dựng bằng FastAPI, TailwindCSS và Lucide Icons",
        version="1.0.0"
    )

    # Cấu hình Jinja2 Templates (Views)
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.state.templates = templates

    app.add_middleware(AuthenticationMiddleware)

    # Mount Static Files (CSS, JS)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Đăng ký Controllers
    app.include_router(auth_router)
    app.include_router(home_router)
    app.include_router(video_router)
    app.include_router(task_router)
    app.include_router(system_router)

    return app


app = create_app()
