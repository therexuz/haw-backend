from fastapi import APIRouter

router = APIRouter()

@router.get("/sensors/air_quality")
def read_air_quality():
    pass