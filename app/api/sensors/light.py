from fastapi import APIRouter

router = APIRouter()

@router.get("/sensors/light")
def read_light():
    pass