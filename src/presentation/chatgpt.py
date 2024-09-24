from fastapi import APIRouter

router = APIRouter(prefix="/auth/tg", tags=["auth"])



@router.post("/")
async def auth_tg_user(

):
    ...