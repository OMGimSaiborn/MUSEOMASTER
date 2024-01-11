from fastapi import Depends, APIRouter
from models import User
from authentication import auth_user

current_user_router = APIRouter(prefix="/user", tags=["Current User"])

@current_user_router.get("")
async def me(user: User = Depends(auth_user)):
    return {"id" : user.id}