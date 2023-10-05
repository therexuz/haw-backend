from fastapi import APIRouter

router = APIRouter()

@router.get("/actuators/door")
def activate_door():
    pass