from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Home"])


@router.get("/", response_class=HTMLResponse)
async def index_view(request: Request):
    """Hiển thị giao diện chính Single Page Application của Video2X."""
    templates = request.app.state.templates
    try:
        # Starlette >= 0.28.0 (Modern FastAPI)
        return templates.TemplateResponse(request=request, name="index.html")
    except TypeError:
        try:
            return templates.TemplateResponse(request, "index.html")
        except TypeError:
            # Legacy Starlette (< 0.28.0)
            return templates.TemplateResponse("index.html", {"request": request})
