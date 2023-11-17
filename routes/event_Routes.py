from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from typing import List
from bson import ObjectId
from pydantic import BaseModel
from models import Event

# Configura la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["MUSEOMASTER"]
collection_events = db["eventos"]
collection_employees = db["empleados"]

app = APIRouter()

class EventInDB(BaseModel):
    event: Event
    _id: ObjectId

# Obtener todos los eventos
@app.get("/events/all", response_model=List[Event])
async def get_all_events():
    events = list(collection_events.find())
    return events

# Obtener detalles de un evento específico
@app.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    # Buscar un evento específico por su ID en la colección MongoDB
    event = collection_events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event

# Crear evento
@app.post("/events/", response_model=Event)
async def create_event(event: Event):
    event_data = event.dict()
    event_data["organizer_id"] = ObjectId(event.organizer_id)  # Convierte a ObjectId

    result = collection_events.insert_one(event_data)
    event_id = result.inserted_id

    created_event_details = collection_events.find_one({"_id": ObjectId(event_id)})

    organizer_id = ObjectId(created_event_details["organizer_id"])

    employees_associated = collection_employees.find({"_id": {"$in": [organizer_id]}})
    for employee in employees_associated:
        if "event_info" not in employee:
            collection_employees.update_one(
                {"_id": employee["_id"]},
                {"$set": {"event_info": []}}
            )

        event_info = {
            "name": created_event_details["title"],
            "date": created_event_details["date"]
        }
        collection_employees.update_one(
            {"_id": employee["_id"]},
            {"$push": {"event_info": event_info}}
        )

    return {**event.dict(), "organizer_id": str(event_data["organizer_id"]), "id": str(event_id)}


# Actualizar la información de un evento
@app.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: str, updated_event: Event):
    result = collection_events.update_one({"_id": ObjectId(event_id)}, {"$set": updated_event.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    updated_event_details = collection_events.find_one({"_id": ObjectId(event_id)})
    organizer_id = ObjectId(updated_event_details["organizer_id"])

    employees_associated = collection_employees.find({"_id": {"$in": [organizer_id]}})
    for employee in employees_associated:
        if "event_info" not in employee:
            collection_employees.update_one(
                {"_id": employee["_id"]},
                {"$set": {"event_info": []}}
            )

        event_info = {
            "name": updated_event_details["title"],  # Cambiado a "name" en lugar de "title"
            "date": updated_event_details["date"]
        }
        collection_employees.update_one(
            {"_id": employee["_id"]},
            {"$push": {"event_info": event_info}}
        )

    return updated_event

# Eliminar un evento
@app.delete("/events/{event_id}", response_model=Event)
async def delete_event(event_id: str):
    event = collection_events.find_one_and_delete({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event
