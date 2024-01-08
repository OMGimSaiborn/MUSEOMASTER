from fastapi import FastAPI, Depends, HTTPException, APIRouter
from pymongo import MongoClient
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

login_router = APIRouter(prefix="/auth", tags=["Log In"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes="bcrypt")

def get_employees_collection(db=Depends(get_db)):
    return db["empleados"]

        
def search_user(employee_email: str):
    db = get_db()
    for items in db:
        print("----")
        print(items)
        
        
    
    employees_collection = db["empleados"]
#def search_user(employee_email: str):
    print(employee_email)
    try:
        employee_data = employees_collection.find_one({"email": employee_email}, {"name": 1, "email": 1, "password": 1})
        print(employee_data)
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
        email = jwt.decode(token, SECRET, ALGORITHM).get("sub")
        if email is None:
            raise exception
        
    except JWTError:
        print("Error en auth_user")
        raise exception
    return search_user(email)

#search = search_user(form.username)

#Login
@login_router.post("/login")
#async def create_access_binnacle(user: UserInDB = Depends(form)):
async def verify(form: OAuth2PasswordRequestForm = Depends()):
    #, search= Depends(search_user)
    """you can't use Depends in your own functions, it has to be in FastAPI functions, mainly routes. You can, however, use Depends in your own functions when that function is also a dependency, so could can have a chain of functions.

Eg, a route uses Depends to resolve a 'getcurrentuser', which also uses Depends to resolve 'getdb', and the whole chain will be resolved. But if you then call 'getcurrentuser' without using Depends, it won't be able to resolve 'getdb'.

What I do is get the DB session from the route and then pass it down through every layer and function. I believe this is also better design."""
    
    user = search_user(form.username) #el username es el correo
    
    if not crypt.verify(form.password, user.password): 
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    expire = datetime.utcnow() + timedelta(minutes=ACCES_TOKEN_DURATION)
    
    access_token = {
        "sub" : user.email,
        "exp" : expire,
    }
    
    return {"access_token":jwt.encode(access_token,SECRET ,algorithm=ALGORITHM), "token_type": "bearer"}

#Obtener usuario actual
@login_router.get("/current_user")
async def me(user: User = Depends(auth_user)):
    return user

"""
Encontrar alguna manera de enviar parámetros a una función dentro de depends.

"""