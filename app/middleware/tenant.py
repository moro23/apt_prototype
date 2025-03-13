from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from config.logger import log


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.url.netloc
        url_components = host.split('.')

        if len(url_components) < 2:
            subdomain = "public"
        else:
            subdomain = url_components[0]

        request.state.schema = subdomain
        log.debug(f"schema extracted from incoming url: {subdomain}")
        response = await call_next(request)
        return response
