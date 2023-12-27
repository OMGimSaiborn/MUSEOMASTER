from fastapi import APIRouter, Depends, HTTPException, Request 
from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime
from db import get_db
from models import AccessBinnacle, CheckIn, CheckOut,BinnacleId
from typing import List

binnacles_collection_name = "binnacles"

binnacle_router = APIRouter(prefix="/bitacora", tags=["Bitacoras"])

def get_binnacles_collection(db=Depends(get_db)):
    return db[binnacles_collection_name]
 
#Todas las bitacoras
@binnacle_router.get("/all", response_model=List[AccessBinnacle])
async def get_all(binnacles_collection = Depends(get_binnacles_collection)):
    binnacles = list(binnacles_collection.find())
    return binnacles

#Listado por empleado
@binnacle_router.get("/list_employee/{employee_id}",response_model=List[BinnacleId])
async def get_list_employee(employee_id: str,binnacles_collection = Depends(get_binnacles_collection)):
    binnacles = list(binnacles_collection.find({"employee_id": employee_id}))
    if not binnacles:
        raise HTTPException(status_code=404, detail="Este empleado no tiene registros")
    for item in binnacles:
        item["id"] = str(item["_id"])
    return binnacles

#Listado por locacion
@binnacle_router.get("/list_location/{location}",response_model=List[BinnacleId])
async def get_list_location(location: str,binnacles_collection = Depends(get_binnacles_collection)):
    binnacles = list(binnacles_collection.find({"location": location}))
    if not binnacles:
        raise HTTPException(status_code=404, detail="Este lugar no tiene registros")
    for item in binnacles:
        item["id"] = str(item["_id"])
    return binnacles

#CheckIn
@binnacle_router.post("/CheckIn")
async def checkin(binnacle: CheckIn, binnacles_collection = Depends(get_binnacles_collection)):
    #Aquí debería de agregar automáticamente el employee_id
    item_dict = binnacle.model_dump()
    result = binnacles_collection.insert_one(item_dict)
   
    return {"inserted_id": str(result.inserted_id)}

#CheckOut
@binnacle_router.put("/CheckOut/{binnacle_id}")
async def checkout(binnacle_id: str,binnacle: CheckOut, binnacles_collection = Depends(get_binnacles_collection)):
    item_dict = binnacle.model_dump()
    result = binnacles_collection.update_one({"_id":ObjectId(binnacle_id)},{"$set":item_dict})
    if not result:
        raise HTTPException(status_code=404, detail="Bitacora Inexistente")
    return {"id": binnacle_id}

#Actualizar bitacoras
@binnacle_router.put("/modify/{binnacle_id}")
async def update_binnacle(binnacle_id: str, binnacle: AccessBinnacle, binnacles_collection: Collection = Depends(get_binnacles_collection)):
    item_dict = binnacle.model_dump()
    result = binnacles_collection.update_one({"_id": ObjectId(binnacle_id)}, {"$set": item_dict})
    if result.modified_count > 0:
        return {"message": "Binnacle updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Bitacora Inexistente")

#Borrar bitacoras
@binnacle_router.delete("/delete/{binnacle_id}")
async def delete_binnacle(binnacle_id: str, binnacles_collection: Collection = Depends(get_binnacles_collection)):
    result = binnacles_collection.delete_one({"_id": ObjectId(binnacle_id)})
    if result.deleted_count > 0:
        return {"message": "Binnacle deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Bitacora Inexistente")
