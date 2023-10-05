from fastapi import APIRouter

router = APIRouter()

@router.get("/sensors/humidity")
def read_humidity():
    pass