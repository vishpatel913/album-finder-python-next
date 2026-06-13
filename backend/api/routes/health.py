from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.dependencies import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(session: Session = Depends(get_session)) -> dict[str, str]:
    # session.exec(select(Artist).limit(1))
    return {"status": "ready"}
