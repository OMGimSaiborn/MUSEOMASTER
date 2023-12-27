from fastapi import APIRouter, Depends, HTTPException, Request 
from bson import ObjectId
from pymongo.collection import Collection
from db import get_db
from models import Colaborator, ColaboratorID
from typing import List
from datetime import datetime

colabs_collection_name = "colaboradores"

colabs_router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"])

def get_colabs_collection(db=Depends(get_db)):
    return db[colabs_collection_name]
 
#Todas los colaboradores
@colabs_router.get("/all", response_model=List[Colaborator])
async def get_all(colabs_collection = Depends(get_colabs_collection)):
    result = list(colabs_collection.find())
    return result

#Listado por area
@colabs_router.get("/list_area/{area}",response_model=List[ColaboratorID])
async def get_list_area(area: str,colabs_collection = Depends(get_colabs_collection)):
    result = list(colabs_collection.find({"area": {"$elemMatch": {"$eq": area}}}))
    if not result:
        raise HTTPException(status_code=404, detail="Este area no tiene registros")
    for item in result:
        item["id"] = str(item["_id"])
    return result


@colabs_router.post("/create")
async def create_colab(colab: Colaborator, colabs_collection = Depends(get_colabs_collection)):
    colab_time = Colaborator(
        name = colab.name,
        email = colab.email,
        institution= colab.institution,
        area= colab.area,
        date_added= datetime.now()
    )
    item_dict = colab_time.model_dump()
    result = colabs_collection.insert_one(item_dict)
   
    return {"inserted_id": str(result.inserted_id)}

@colabs_router.put("/modify/{colab_id}")
async def update_colab(colab_id: str, colab: Colaborator, colabs_collection: Collection = Depends(get_colabs_collection)):
    item_dict = colab.model_dump()
    result = colabs_collection.update_one({"_id": ObjectId(colab_id)}, {"$set": item_dict})
    if result.modified_count > 0:
        return {"message": "Colaborador actualizado"}
    else:
        raise HTTPException(status_code=404, detail="Colaborador Inexistente")

@colabs_router.delete("/delete/{colab_id}")
async def delete_colab(colab_id: str, colab_collection: Collection = Depends(get_colabs_collection)):
    result = colab_collection.delete_one({"_id": ObjectId(colab_id)})
    if result.deleted_count > 0:
        return {"message": "Colaborador Eliminado"}
    else:
        raise HTTPException(status_code=404, detail="Colaborador Inexistente")
