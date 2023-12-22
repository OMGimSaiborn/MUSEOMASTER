from fastapi import APIRouter, HTTPException, Depends
from models import Event, EventResponse, SuccessResponse, DeletedEventResponse
from pymongo.collection import Collection
from typing import List
from bson import ObjectId
from db import get_db
from datetime import datetime

events_collection_name = "eventos"
employees_collection_name = "empleados"

event_router = APIRouter(prefix="/events", tags=["Events"])

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
    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    event["_id"] = str(event["_id"])

    return EventResponse(**event)

# Crear evento
@event_router.post("/", response_model=SuccessResponse) 
async def create_event(
    event: Event,
    events_collection=Depends(get_events_collection),
    employees_collection=Depends(get_employees_collection),
):
    try:
        event_data = event.dict()
        event_data["organizer_id"] = ObjectId(event.organizer_id)  

        event_data["date"] = datetime.combine(event_data["date"], datetime.min.time())

        result = events_collection.insert_one(event_data)
        event_id = result.inserted_id

        created_event_details = events_collection.find_one({"_id": ObjectId(event_id)})

        organizer_id = str(created_event_details["organizer_id"])

        employees_associated = employees_collection.find({"_id": {"$in": [ObjectId(organizer_id)]}})
        for employee in employees_associated:
            if "event_info" not in employee:
                employees_collection.update_one(
                    {"_id": employee["_id"]},
                    {"$set": {"event_info": []}}
                )

            event_info = {
                "event_id": ObjectId(event_id),
                "name": created_event_details["title"],
                "date": created_event_details["date"]
            }

            employees_collection.update_one(
                {"_id": employee["_id"]},
                {"$push": {"event_info": event_info}}
            )

        success_message = f" El Evento '{created_event_details['title']}' se creo correctamente."

        return SuccessResponse(message=success_message)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al crear el evento")

# Eliminar un evento
@event_router.delete("/{event_id}", response_model=SuccessResponse)
async def delete_event(
    event_id: str, 
    events_collection: Collection = Depends(get_events_collection),
    employees_collection: Collection = Depends(get_employees_collection)
):
    try:
        event = events_collection.find_one_and_delete({"_id": ObjectId(event_id)})
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        organizer_id = str(event["organizer_id"])

        # Mensaje de éxito
        success_message = f"Evento '{event['title']}' eliminado correctamente."

        return SuccessResponse(message=success_message)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al eliminar el evento")

# Actualizar un evento
@event_router.put("/{event_id}", response_model=SuccessResponse)
async def update_event(
    event_id: str,
    updated_event: Event,
    events_collection: Collection = Depends(get_events_collection),
    employees_collection: Collection = Depends(get_employees_collection)
):
    try:
        existing_event = events_collection.find_one({"_id": ObjectId(event_id)})
        if not existing_event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        updated_event_data = {k: v for k, v in updated_event.dict().items() if v is not None}

        updated_event_data["organizer_id"] = ObjectId(updated_event.organizer_id)

        updated_event_data["date"] = datetime.combine(updated_event_data["date"], datetime.min.time())

        update_result = events_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": updated_event_data}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No se actualizó ningún documento")

        updated_event_details = events_collection.find_one({"_id": ObjectId(event_id)})
        organizer_id = str(updated_event_details["organizer_id"])

        employees_associated = employees_collection.find({"_id": {"$in": [ObjectId(organizer_id)]}})
        for employee in employees_associated:
            event_info_list = employee.get("event_info", [])

            event_info_list = [event_info for event_info in event_info_list if event_info["event_id"] != ObjectId(event_id)]

            event_info_list.append({
                "event_id": ObjectId(event_id),
                "name": updated_event_details["title"],
                "date": updated_event_details["date"]
            })

            employees_collection.update_one(
                {"_id": employee["_id"]},
                {"$set": {"event_info": event_info_list}}
            )

        success_message = f"El Evento '{updated_event_data['title']}' se actualizó correctamente."
        return SuccessResponse(message=success_message)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error al actualizar el evento: {str(e)}")