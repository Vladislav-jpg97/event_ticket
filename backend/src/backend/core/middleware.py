from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis
from backend.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in settings.exclude_paths:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        redis_key = f"global_rate:{client_ip}"

        redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

        try:
            current_requests = await redis_client.incr(redis_key)
            if current_requests == 1:
                await redis_client.expire(redis_key, settings.window)

            if current_requests > settings.limit:
                return JSONResponse(
                    status_code=429,
                    content={"error": "rate_limit_exceeded"}
                )
        finally:
            await redis_client.aclose()

        response = await call_next(request)
        return response