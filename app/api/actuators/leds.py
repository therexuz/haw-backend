from fastapi import APIRouter

router = APIRouter()

@router.get("/actuators/led{id}")
def activate_leds():
    pass