from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime
from db import get_db
from models import AccessBinnacle

binnacle_router = APIRouter(prefix="/bitacora", tags=["Bitacoras"])

#Crear bitacoras
@binnacle_router.post("/crearBitacora")
async def create_access_binnacle(item: AccessBinnacle, db: Collection = Depends(get_db)):
    binnacles_collection = db["binnacles"]
    item_dict = item.model_dump()
    result = binnacles_collection.insert_one(item_dict)
    print("inserted_id: ",str(result.inserted_id))
    return {"inserted_id": str(result.inserted_id)}

#Devolver bitacoras
@binnacle_router.get("/getBitacora/{employee_name}")
async def get_access_binnacle(employee_name: str, db: Collection = Depends(get_db)):
    id_employee = db.empleados.find_one({"name": employee_name}, {"_id": 1})
    #result = db.binnacle.find()
    result = db.binnacles.find({"employee_id": id_employee})
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Binnacle not found")

#Devolver bitacora especifica
@binnacle_router.get("/bitacoras_all/{employee_name}")
async def get_access_binnacle(binnacle_id: str, db: Collection = Depends(get_db)):
    #id_employee = db.empleados.find_one({"name": employee_name}, {"_id": 1})
    #result = db.binnacle.find()
    result = db.binnacles.find({"_id": binnacle_id})
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Binnacle not found")

#Actualizar bitaoras
@binnacle_router.put("/modificarBitacora/{binnacle_id}")
async def update_access_binnacle(binnacle_id: str, item: AccessBinnacle, db: Collection = Depends(get_db)):
    result = db.update_one({"_id": ObjectId(binnacle_id)}, {"$set": item.dict()})
    if result.modified_count > 0:
        return {"message": "Binnacle updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Binnacle not found")

#Borrar bitacoras
@binnacle_router.delete("/borrarBitacora/{binnacle_id}")
async def delete_access_binnacle(binnacle_id: str, db: Collection = Depends(get_db)):
    result = db.delete_one({"_id": ObjectId(binnacle_id)})
    if result.deleted_count > 0:
        return {"message": "Binnacle deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Binnacle not found")
