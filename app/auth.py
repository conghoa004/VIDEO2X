import base64
import hashlib
import hmac
import secrets
import time
from urllib.parse import quote

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


AUTH_COOKIE_NAME = "video2x_auth"
SESSION_MAX_AGE = 12 * 60 * 60


def create_session(request: Request) -> str:
    session_id = secrets.token_urlsafe(32)
    issued_at = int(time.time())
    payload = f"{issued_at}.{session_id}"
    digest = hmac.new(
        request.app.state.session_signing_key,
        payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    request.app.state.active_sessions.add(session_id)
    return f"{payload}.{signature}"


def _get_valid_session_id(request: Request):
    token = request.cookies.get(AUTH_COOKIE_NAME, "")
    try:
        issued_at_text, session_id, signature = token.split(".", 2)
        issued_at = int(issued_at_text)
    except (ValueError, TypeError):
        return None

    now = int(time.time())
    if issued_at > now or now - issued_at > SESSION_MAX_AGE:
        request.app.state.active_sessions.discard(session_id)
        return None

    payload = f"{issued_at}.{session_id}"
    digest = hmac.new(
        request.app.state.session_signing_key,
        payload.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    expected = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    if not hmac.compare_digest(signature, expected):
        return None

    if session_id not in request.app.state.active_sessions:
        return None
    return session_id


def is_authenticated(request: Request) -> bool:
    return _get_valid_session_id(request) is not None


def revoke_session(request: Request) -> None:
    session_id = _get_valid_session_id(request)
    if session_id is not None:
        request.app.state.active_sessions.discard(session_id)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path == "/login" or path == "/static" or path.startswith("/static/"):
            return await call_next(request)

        if is_authenticated(request):
            return await call_next(request)

        if path.startswith("/api/"):
            return JSONResponse(
                status_code=401,
                content={"detail": "Vui lòng đăng nhập để tiếp tục."},
            )

        target = path
        if request.url.query:
            target += f"?{request.url.query}"
        login_url = "/login?next=" + quote(target, safe="")
        return RedirectResponse(url=login_url, status_code=303)
