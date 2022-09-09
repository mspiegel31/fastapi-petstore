from asyncio.exceptions import TimeoutError
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.config import settings
from app.routes import health_check

app = FastAPI(
    title="payment-stats-service",
    description="fastapi",
    version=settings.release_version,
)


@app.on_event("startup")
async def startup():
    app.description = Path("docs/main.md").read_text()


@app.on_event("shutdown")
async def shutdown():
    # Add repo specific shutdown commands here
    pass


@app.exception_handler(TimeoutError)
async def db_timeout_error(request: Request, exc: TimeoutError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "timed out waiting for the database query results",
        },
    )


app.include_router(health_check.router, tags=["health"])
# app.include_router(v1.router, prefix="/v1", tags=["API v1"])
