from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from typing import List
from bson import ObjectId
from pydantic import BaseModel
from models import Employee
from event_routes import collection_events

# Configura la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["MUSEOMASTER"]
collection_employees = db["empleados"]

app = APIRouter()

class EmployeeInDB(BaseModel):
    employee: Employee
    _id: ObjectId

# Crear empleado
@app.post("/", response_model=Employee, tags=["employees"])
async def create_employee(employee: Employee):
    employee_data = employee.dict()

    existing_employee = collection_employees.find_one({"name": employee_data["name"]})
    if existing_employee:
        raise HTTPException(status_code=400, detail="Employee with this name already exists")

    result = collection_employees.insert_one(employee_data)
    employee_id = result.inserted_id

    created_employee = Employee(name=employee_data["name"], _id=str(employee_id), event_info=[])
    
    return created_employee

#Actualizar empleado
@app.put("/{employee_id}", response_model=Employee, tags=["employees"])
async def update_employee(employee_id: str, employee: Employee):
    employee_data = employee.dict()

    result = collection_employees.update_one(
        {"_id": ObjectId(employee_id)},
        {"$set": employee_data}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")

    events_organized = list(collection_events.find({"organizer_id": employee_id}))

    updated_employee_data = {"event_info": []}
    for event in events_organized:
        event_info = {
            "name": event["title"],
            "date": event["date"]
        }
        updated_employee_data["event_info"].append(event_info)

    collection_employees.update_one(
        {"_id": ObjectId(employee_id)},
        {"$push": {"event_info": {"$each": updated_employee_data["event_info"]}}}
    )

    updated_employee = collection_employees.find_one({"_id": ObjectId(employee_id)})

    return {"name": updated_employee["name"], "event_info": updated_employee["event_info"]}

#Mostrar todos los empleados
@app.get("/", response_model=List[Employee], tags=["employees"])
async def read_employees():
    employees = collection_employees.find()
    return [Employee(**employee) for employee in employees]

# Mostrar un empleado específico
@app.get("/{employee_id}", response_model=Employee, tags=["employees"])
async def read_employee(employee_id: str):
    employee = collection_employees.find_one({"_id": ObjectId(employee_id)})

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Convertir el _id a cadena y crear un objeto Employee
    employee["_id"] = str(employee["_id"])
    return Employee(**employee)

#Borrar empleado especifico
@app.delete("/{employee_id}", response_model=Employee, tags=["employees"])
async def delete_employee(employee_id: str):
    # Buscar eventos en los que el empleado es organizador
    events_organized = list(collection_events.find({"organizer_id": employee_id}))

    result = collection_employees.delete_one({"_id": ObjectId(employee_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    for event in events_organized:
        collection_events.delete_one({"_id": event["_id"]})

    return {"message": "Empleado y eventos eliminados exitosamente"}
