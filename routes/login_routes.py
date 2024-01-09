from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import  OAuth2PasswordRequestForm
from models import User, UserInDB
from authentication import search_user, auth_user, token
from passlib.context import CryptContext

login_router = APIRouter(prefix="/login", tags=["Log In"])
crypt = CryptContext(schemes="bcrypt")

@login_router.post("")
async def verify(form: OAuth2PasswordRequestForm = Depends()):
    
    user = search_user(form.username) #el username es el correo

    if not crypt.verify(form.password, user.password): 
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    return token(user.email)

#Obtener usuario actual
@login_router.get("/current_user")
async def me(user: User = Depends(auth_user)):
    return {"id" : user.id}
