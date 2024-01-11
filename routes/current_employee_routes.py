from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from pymongo.collection import Collection
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from db import get_db
from models import User, UserInDB

ALGORITHM = "HS256"
ACCES_TOKEN_DURATION = 1 #minutes
SECRET = "hola"

current_user_router = APIRouter(prefix="/user", tags=["Current User"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes="bcrypt")

def get_employees_collection(db=Depends(get_db)) -> Collection:
    return db["empleados"]

def search_user(employee_email: str, employees_collection: Collection = Depends(get_employees_collection)):
    
    try:
        employee_data = employees_collection.find_one({"email": employee_email}, {"name": 1, "email": 1, "password": 1})

        if not employee_data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        employee_data["_id"] = str(employee_data["_id"])
        return UserInDB(**employee_data)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error obteniendo empleado")

async def auth_user(token : str = Depends(oauth2)):
    exception = HTTPException(status_code=401, detail="Credenciales inválidas")
    
    try: 
        email = jwt.decode(token, SECRET, ALGORITHM).get("sub")
        if email is None:
            raise exception
        
    except JWTError:
        raise exception
    return search_user(email)


@current_user_router.get("/")
async def me(user: User = Depends(auth_user)):
    return user