from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from models import MuseumRoomType
from pydantic import BaseModel
from typing import List
from db import get_db

rooms_collection_name = "salas"

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])


class MuseumRoomInDB(BaseModel):
    room: MuseumRoomType
    _id: str


# Función de manejo de conexiones a la base de datos
def get_rooms_collection(db=Depends(get_db)):
    return db[rooms_collection_name]


# Ruta para crear una sala
@room_router.post("/create", response_model=MuseumRoomInDB)
def create_room(room: MuseumRoomType, rooms_collection=Depends(get_rooms_collection)):
    try:
        result = rooms_collection.insert_one(room.dict())

        # Obtener el ID asignado por MongoDB
        inserted_id = result.inserted_id

        # Devolver la sala creada junto con su ID
        return MuseumRoomInDB(room=room, _id=str(inserted_id))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al crear la sala")


# Obtener todas las salas
@room_router.get("/all", response_model=List[MuseumRoomInDB])
def get_all_rooms(rooms_collection=Depends(get_rooms_collection)):
    try:
        rooms = list(rooms_collection.find())
        # Convertir el _id a cadena y crear instancias de MuseumRoomInDB
        rooms_in_db = [MuseumRoomInDB(room=MuseumRoomType(**room), _id=str(room["_id"])) for room in rooms]
        return rooms_in_db
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al obtener las salas")


# Obtener detalles de una sala específica
@room_router.get("/{room_id}", response_model=MuseumRoomType)
def get_room(room_id: str, rooms_collection=Depends(get_rooms_collection)):
    room = rooms_collection.find_one({"_id": ObjectId(room_id)})
    if not room:
        raise HTTPException(status_code=404, detail="Sala no encontrada")

    # Convertir el _id a cadena
    room["_id"] = str(room["_id"])

    # Crear una instancia de MuseumRoomType con los datos encontrados
    return MuseumRoomType(**room)


# Ruta para actualizar una sala por su ID
@room_router.put("/update/{room_id}", response_model=MuseumRoomInDB)
def update_room(room_id: str, updated_room: MuseumRoomType, rooms_collection=Depends(get_rooms_collection)):
    try:
        # Verificar si la sala existe
        existing_room = rooms_collection.find_one({"_id": ObjectId(room_id)})
        if not existing_room:
            raise HTTPException(status_code=404, detail="Sala no encontrada")

        # Actualizar los campos de la sala
        rooms_collection.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": updated_room.dict(exclude_unset=True)},
        )

        # Obtener la sala actualizada
        updated_room_in_db = rooms_collection.find_one({"_id": ObjectId(room_id)})

        # Convertir el _id a cadena
        updated_room_in_db["_id"] = str(updated_room_in_db["_id"])

        return MuseumRoomInDB(room=MuseumRoomType(**updated_room_in_db), _id=updated_room_in_db["_id"])
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al actualizar la sala")


# Ruta para eliminar una sala por su ID
@room_router.delete("/delete/{room_id}", response_model=dict)
def delete_room(room_id: str, rooms_collection=Depends(get_rooms_collection)):
    try:
        # Verificar si la sala existe
        existing_room = rooms_collection.find_one({"_id": ObjectId(room_id)})
        if not existing_room:
            raise HTTPException(status_code=404, detail="Sala no encontrada")

        # Eliminar la sala
        result = rooms_collection.delete_one({"_id": ObjectId(room_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Error al eliminar la sala")

        return {"message": "Sala eliminada correctamente"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al eliminar la sala")
