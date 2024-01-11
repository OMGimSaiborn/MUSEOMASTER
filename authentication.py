from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from contextlib import contextmanager
from datetime import datetime, timedelta
from db import get_db
from models import User, UserInDB
from dotenv import load_dotenv
import os

load_dotenv()

algoritmo = os.getenv("ALGORITHM")
duration = int(os.getenv("ACCES_TOKEN_DURATION"))
secret = os.getenv("SECRET")

oauth2 = OAuth2PasswordBearer(tokenUrl="auth")

crypt = CryptContext(schemes="bcrypt")

        
def search_user(employee_email: str):    
    with contextmanager(get_db)() as db:  # execute until yield. Session is yielded value
        employees_collection = db["empleados"]
        try:
            employee_data = employees_collection.find_one({"email": employee_email}, {"name": 1, "email": 1, "password": 1})
            if not employee_data:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            employee_data["id"] = str(employee_data["_id"]) #CUIDADDOADOJD KON
            return UserInDB(**employee_data)
        except Exception as e:
            print("Error en search user",e)
            raise HTTPException(status_code=500, detail="Error obteniendo empleado")

async def auth_user(token : str = Depends(oauth2)):
    exception = HTTPException(status_code=401, detail="Credenciales inválidas")
    
    try: 
        email = jwt.decode(token, secret, algoritmo).get("sub")
        if email is None:
            raise exception
        
    except JWTError:
        print("Error en auth_user")
        raise exception
    return search_user(email)

def token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=duration)
    
    access_token = {
        "sub" : email,
        "exp" : expire,
    }
    return {"access_token":jwt.encode(access_token,secret ,algorithm=algoritmo), "token_type": "bearer"}