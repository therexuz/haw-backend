from fastapi import APIRouter

router = APIRouter()

@router.get("/sensors/pressure")
def read_pressure():
    pass