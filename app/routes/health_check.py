import logging
import time
from enum import Enum

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from app.config import settings
from app.database.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


class StatusEnum(str, Enum):
    STATUS_UP = "UP"
    STATUS_DOWN = "DOWN"


class StatusMessage(BaseModel):
    status: StatusEnum
    error: str | None


class ServiceStatus(StatusMessage):
    version: str


class Health(BaseModel):
    service: ServiceStatus
    core_payments_database: StatusMessage


async def db_health(session: AsyncSession, response: Response, name: str):
    try:
        start: float = time.perf_counter()

        await session.execute(text("SELECT 1"))
        elapsed_time: float = time.perf_counter() - start

        if elapsed_time > 1:
            logger.info(
                "%s health check took longer than 1 second: %s",
                name,
                elapsed_time,
            )

        return {"status": StatusEnum.STATUS_UP}

    except Exception as exception:
        logger.warning("%s health check failed", name, exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {"status": StatusEnum.STATUS_DOWN, "error": str(exception)}


@router.get(
    "/livenessz",
    summary="Service health check.",
    response_description="Service health status",
    response_model=Health,
)
@router.get(
    "/readyz",
    summary="Service health check.",
    response_description="Service health status",
    response_model=Health,
)
async def health(response: Response, db: AsyncSession = Depends(get_db)):
    """
    Returns a health check for this service and its dependencies.
    """

    db_status = await db_health(db, response, "core_payments_database")
    return {
        "service": {
            "status": StatusEnum.STATUS_UP,
            "version": settings.release_version,
        },
        "core_payments_database": db_status,
    }
