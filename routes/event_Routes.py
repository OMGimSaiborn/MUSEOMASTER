from fastapi import APIRouter, HTTPException, Depends
from pymongo import MongoClient
from fastapi.responses import JSONResponse
from bson import json_util
from models import Event
from pymongo.collection import Collection
from bson import ObjectId
from typing import List
from pydantic import BaseModel, Field
from db import get_db

events_collection_name = "eventos"
employees_collection_name = "empleados"

event_router = APIRouter(prefix="", tags=["Events"])

class EventInDB(BaseModel):
    event: Event
    _id: ObjectId

class EventResponse(Event):
    organizer_id: str = Field(..., alias="_id")

class DeletedEventResponse(BaseModel):
    title: str
    description: str
    date: str
    location: str
    organizer_id: str

# Funciones de manejo de conexiones a la base de datos
def get_events_collection(db=Depends(get_db)):
    return db[events_collection_name]

def get_employees_collection(db=Depends(get_db)):
    return db[employees_collection_name]

# Obtener todos los eventos
@event_router.get("/all", response_model=List[Event])
async def get_all_events(events_collection=Depends(get_events_collection)):
    events = list(events_collection.find())
    for event in events:
        event['organizer_id'] = str(event['organizer_id'])
    return events

# Obtener detalles de un evento específico
@event_router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, events_collection=Depends(get_events_collection)):
    # Buscar un evento específico por su ID en la colección MongoDB
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Convertir el _id a cadena
    event["_id"] = str(event["_id"])

    return EventResponse(**event)

# Crear evento
@event_router.post("/", response_model=EventResponse)
async def create_event(
    event: Event,
    events_collection=Depends(get_events_collection),
    employees_collection=Depends(get_employees_collection)
):
    try:
        event_data = event.dict()
        event_data["organizer_id"] = ObjectId(event.organizer_id)  # Convierte a ObjectId

        result = events_collection.insert_one(event_data)
        event_id = result.inserted_id

        created_event_details = events_collection.find_one({"_id": ObjectId(event_id)})

        organizer_id = str(created_event_details["organizer_id"])  # Convertir a cadena

        employees_associated = employees_collection.find({"_id": {"$in": [ObjectId(organizer_id)]}})
        
        for employee in employees_associated:
            print(f"Processing employee: {employee['_id']}")
            if "event_info" not in employee:
                print("Initializing event_info for employee")
                employees_collection.update_one(
                    {"_id": employee["_id"]},
                    {"$set": {"event_info": []}}
                )

            event_info = {
                "event_id": ObjectId(event_id),  # Cambio aquí
                "name": created_event_details["title"],
                "date": created_event_details["date"]
            }
            print(f"Adding event_info to employee: {event_info}")
            employees_collection.update_one(
                {"_id": employee["_id"]},
                {"$push": {"event_info": event_info}}
            )

        created_event_response = {
            **created_event_details,
            "organizer_id": organizer_id,
            "id": str(event_id),  # Agregamos el campo 'id'
        }
        return EventResponse(**created_event_response)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al crear el evento")

# Eliminar un evento
@event_router.delete("/{event_id}", response_model=DeletedEventResponse)
async def delete_event(
    event_id: str, 
    events_collection: Collection = Depends(get_events_collection),
    employees_collection: Collection = Depends(get_employees_collection)
):
    try:
        event = events_collection.find_one_and_delete({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        # Convert the organizer_id to string
        event["organizer_id"] = str(event["organizer_id"])

        # Return the deleted event details
        return event
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al eliminar el evento")

# Actualizar un evento
@event_router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    updated_event: Event,
    events_collection: Collection = Depends(get_events_collection),
    employees_collection: Collection = Depends(get_employees_collection)
):
    try:
        # Verificar si el evento existe
        existing_event = events_collection.find_one({"_id": ObjectId(event_id)})
        if not existing_event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        # Filtrar los campos que no son None del diccionario de datos actualizado
        updated_event_data = {k: v for k, v in updated_event.dict().items() if v is not None}
        # Convertir el ID del organizador a ObjectId
        updated_event_data["organizer_id"] = ObjectId(updated_event.organizer_id)

        # Actualizar el evento en la base de datos
        update_result = events_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": updated_event_data}
        )

        # Verificar si se actualizó al menos un documento
        if update_result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No se actualizó ningún documento")

        # Obtener detalles actualizados del evento
        updated_event_details = events_collection.find_one({"_id": ObjectId(event_id)})
        organizer_id = str(updated_event_details["organizer_id"])

        # Actualizar información del evento en empleados asociados
        employees_associated = employees_collection.find({"_id": {"$in": [ObjectId(organizer_id)]}})
        for employee in employees_associated:
            event_info = {
                "event_id": ObjectId(event_id),
                "name": updated_event_details["title"],
                "date": updated_event_details["date"]
            }
            employees_collection.update_one(
                {"_id": employee["_id"]},
                {"$set": {"organizer_id": organizer_id, "event_info": event_info}}
            )

        # Devolver detalles del evento actualizado
        updated_event_response = {
            **updated_event_details,
            "organizer_id": organizer_id,
            "id": event_id,
        }
        return EventResponse(**updated_event_response)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error al actualizar el evento: {str(e)}")