from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from db import get_db
from routes.room_routes import get_rooms_collection
from routes.event_routes import get_events_collection
from routes.employee_routes import get_employees_collection

calendar_router = APIRouter(prefix="/calendar", tags=["Calendar"])

# Funciones de manejo de conexiones a la base de datos
def get_all_dates_collection(db=Depends(get_db)):
    return db["all_dates"]

# Obtener todas las fechas relacionadas (mantenimiento de sala, eventos, capacitaciones, etc.)
@calendar_router.get("/all_dates", response_model=dict)
def get_all_dates(
    rooms_collection=Depends(get_rooms_collection),
    events_collection=Depends(get_events_collection),
    employees_collection=Depends(get_employees_collection),
    all_dates_collection=Depends(get_all_dates_collection),
):
    try:
        # Obtener fechas de mantenimiento de sala
        room_dates = list(rooms_collection.find({}, {"_id": 0, "maintenance": 1}))
        # Obtener fechas de eventos
        event_dates = list(events_collection.find({}, {"_id": 0, "date": 1}))
        # Obtener fechas de capacitaciones de empleados
        employee_training_dates = list(
            employees_collection.find({}, {"_id": 0, "formacion": 1})
        )
        # Puedes agregar más tipos de fechas según sea necesario

        # Consolidar y devolver todas las fechas
        all_dates = {
            "room_maintenance_dates": room_dates,
            "event_dates": event_dates,
            "employee_training_dates": employee_training_dates,
            # Agregar más categorías según sea necesario
        }

        # Guardar las fechas en una colección adicional (opcional)
        all_dates_collection.insert_one(all_dates)

        return all_dates
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Error al obtener las fechas relacionadas"
        )
