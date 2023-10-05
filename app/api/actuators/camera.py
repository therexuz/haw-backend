from fastapi import APIRouter

router = APIRouter()

@router.get("/actuators/camera")
def activate_camera():
    pass