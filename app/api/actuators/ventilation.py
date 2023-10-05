from fastapi import APIRouter

router = APIRouter()

@router.get("/actuators/ventilation")
def read_temperature():
    pass