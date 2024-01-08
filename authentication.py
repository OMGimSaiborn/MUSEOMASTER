import os
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pydantic import BaseModel
from pymongo.collection import Collection
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from db import get_db
from models import User, UserInDB
from dotenv import load_dotenv

load_dotenv()


algorithm = os.getenv("ALGORITHM")
duarion = os.getenv("ACCES_TOKEN_DURATION")
secret = os.getenv("SECRET")

login_router = APIRouter(prefix="/bitacora", tags=["Bitacoras"])

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
        email = jwt.decode(token, secret, algorithm).get("sub")
        if email is None:
            raise exception
        
    except JWTError:
        raise exception
    return search_user(email)