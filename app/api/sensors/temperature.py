from fastapi import APIRouter

router = APIRouter()

@router.get("/sensors/temperature")
def read_temperature():
    pass