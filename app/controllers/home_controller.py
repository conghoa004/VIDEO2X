from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Home"])


@router.get("/", response_class=HTMLResponse)
async def index_view(request: Request):
    """Hiển thị giao diện chính Single Page Application của Video2X."""
    templates = request.app.state.templates
    return templates.TemplateResponse("index.html", {"request": request})
