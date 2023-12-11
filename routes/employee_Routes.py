from fastapi import APIRouter, HTTPException, Depends
from pymongo.collection import Collection
from models import Employee
from bson import ObjectId
from pydantic import BaseModel 
from db import get_db

employee_collection_name = "empleados"
event_collection_name = "eventos"

employee_router = APIRouter(prefix="/employees", tags=["Employees"])

class EmployeeInDB(BaseModel):
    employee: Employee
    _id: ObjectId

# Funciones de manejo de conexiones a la base de datos
def get_employees_collection(db=Depends(get_db)) -> Collection:
    return db[employee_collection_name]

def get_events_collection(db=Depends(get_db)) -> Collection:
    return db[event_collection_name]

# Crear empleado
@employee_router.post("/create", response_model=EmployeeInDB)
def create_employee(
    employee: Employee,
    employees_collection: Collection = Depends(get_employees_collection),
):
    try:
        employee_data = employee.dict()

        existing_employee = employees_collection.find_one({"name": employee_data["name"]})
        if existing_employee:
            raise HTTPException(status_code=400, detail="Employee with this name already exists")

        result = employees_collection.insert_one(employee_data)
        employee_id = result.inserted_id

        created_employee = EmployeeInDB(employee=employee, _id=str(employee_id))

        return created_employee
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al crear el empleado")

# Actualizar empleado
@employee_router.put("/{employee_id}")
def update_employee(
    employee_id: str,
    employee: Employee,
    employees_collection: Collection = Depends(get_employees_collection),
    events_collection: Collection = Depends(get_events_collection),
):
    try:
        employee_data = employee.dict()

        # Obtener el empleado actual
        existing_employee = employees_collection.find_one({"_id": ObjectId(employee_id)})
        if not existing_employee:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        print(f"Updating employee: {existing_employee['_id']} - {existing_employee['name']}")

        # Obtener los eventos organizados por el antiguo empleado
        events_organized = list(events_collection.find({"organizer_id": ObjectId(employee_id)}))

        print(f"Events organized by the old employee: {events_organized}")

        # Eliminar la información del evento antiguo del antiguo empleado
        for event in events_organized:
            employees_collection.update_one(
                {"_id": ObjectId(employee_id)},
                {"$pull": {"event_info": {"event_id": str(event["_id"])}}}
            )

        print(f"Event info removed from the old employee: {existing_employee['event_info']}")

        # Actualizar la información del empleado
        result = employees_collection.update_one(
            {"_id": ObjectId(employee_id)},
            {"$set": employee_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        print(f"Employee information updated: {employee_data}")

        # Obtener el ID del nuevo organizador
        new_organizer_id = ObjectId(employee_data.get("organizer_id"))

        # Obtener los eventos organizados por el nuevo organizador
        new_events_organized = list(events_collection.find({"organizer_id": new_organizer_id}))

        print(f"Events organized by the new employee: {new_events_organized}")

        # Construir la lista de event_info con los IDs de los eventos para el nuevo organizador
        new_employee_event_info = [{"event_id": str(event["_id"]), "name": event["title"], "date": event["date"]} for event in new_events_organized]

        # Agregar la información del evento actualizado al nuevo organizador
        employees_collection.update_one(
            {"_id": new_organizer_id},
            {"$set": {"event_info": new_employee_event_info}}
        )

        print(f"Event info added to the new employee: {new_employee_event_info}")

        updated_employee = employees_collection.find_one({"_id": ObjectId(employee_id)})

        return {"name": updated_employee["name"], "event_info": updated_employee["event_info"]}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al actualizar el empleado")


# Obtener todos los empleados
@employee_router.get("/all")
def read_employees(employees_collection: Collection = Depends(get_employees_collection)):
    try:
        employees = employees_collection.find()
        return [Employee(**employee) for employee in employees]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al obtener los empleados")

# Mostrar un empleado específico
@employee_router.get("/{employee_id}")
def read_employee(
    employee_id: str,
    employees_collection: Collection = Depends(get_employees_collection),
):
    try:
        employee = employees_collection.find_one({"_id": ObjectId(employee_id)})

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        # Convertir el _id a cadena y crear un objeto Employee
        employee["_id"] = str(employee["_id"])
        return Employee(**employee)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al obtener el empleado")
    
    # Eliminar empleado
@employee_router.delete("/{employee_id}")
def delete_employee(
    employee_id: str,
    employees_collection: Collection = Depends(get_employees_collection),
):
    try:
        # Verificar si el empleado existe
        existing_employee = employees_collection.find_one({"_id": ObjectId(employee_id)})
        if not existing_employee:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        # Eliminar el empleado
        result = employees_collection.delete_one({"_id": ObjectId(employee_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Error al eliminar el empleado")

        return {"message": "Empleado eliminado correctamente"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error al eliminar el empleado")