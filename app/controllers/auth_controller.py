import secrets

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.auth import (
    AUTH_COOKIE_NAME,
    SESSION_MAX_AGE,
    create_session,
    is_authenticated,
    revoke_session,
)


router = APIRouter(tags=["Authentication"])


def _safe_next(value: str) -> str:
    if (
        not value.startswith("/")
        or value.startswith("//")
        or "\\" in value
        or any(ord(char) < 32 for char in value)
    ):
        return "/"
    return value


def _render_login(request: Request, next_url: str, error: str = ""):
    templates = request.app.state.templates
    context = {"request": request, "next": next_url, "error": error}
    try:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context=context,
            status_code=401 if error else 200,
        )
    except TypeError:
        return templates.TemplateResponse(
            "login.html",
            context,
            status_code=401 if error else 200,
        )


def _secure_cookie(request: Request) -> bool:
    return request.url.scheme == "https"


@router.get("/login")
async def login_page(request: Request, next: str = "/"):
    next_url = _safe_next(next)
    if is_authenticated(request):
        return RedirectResponse(url=next_url, status_code=303)
    return _render_login(request, next_url)


@router.post("/login")
async def login_submit(
    request: Request,
    password: str = Form(...),
    next: str = Form("/"),
):
    next_url = _safe_next(next)
    expected = request.app.state.login_password
    if not secrets.compare_digest(
        password.encode("utf-8"),
        expected.encode("utf-8"),
    ):
        return _render_login(request, next_url, "Mật khẩu không đúng. Vui lòng thử lại.")

    response = RedirectResponse(url=next_url, status_code=303)
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=create_session(request),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        secure=_secure_cookie(request),
        samesite="lax",
        path="/",
    )
    return response


@router.post("/logout")
async def logout(request: Request):
    revoke_session(request)
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=_secure_cookie(request),
        samesite="lax",
        path="/",
    )
    return response
