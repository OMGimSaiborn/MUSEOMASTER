from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from pydantic import BaseModel
from models import Employee
from db import get_db

employee_collection_name = "empleados"

employee_router = APIRouter(prefix="/employees", tags=["Employees"])

class EmployeeInDB(BaseModel):
    employee: Employee
    _id: ObjectId

# Crear empleado
@employee_router.post("/", response_model=List)
async def create_employee(employee: Employee, db = Depends(get_db)):
  employee_data = employee.model_dump()
  print(employee_data)
  collection_employees = db[employee_collection_name]
  existing_employee = collection_employees.find_one({"name": employee_data["name"]})
  if existing_employee:
    raise HTTPException(status_code=400, detail="Employee with this name already exists")

  result = collection_employees.insert_one(employee_data)
  created_employee = collection_employees.find_one({"_id": ObjectId(result.inserted_id)})
  print('created_employee:', created_employee)

  

  return []
  employee_id = result.inserted_id
#   created_employee = Employee(name=employee_data["name"], _id=str(employee_id), event_info=[])
    
#   return created_employee

#Actualizar empleado
@employee_router.put("/{employee_id}", response_model=Employee)
async def update_employee(employee_id: str, employee: Employee, db = Depends(get_db)):
    employee_data = employee.model_dump()
    collection_employees = db[employee_collection_name]
    collection_events = db["eventos"]
    
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
@employee_router.get("/", response_model=List[Employee], tags=["Employees"])
async def read_employees(db = Depends(get_db)):
    collection_employees = db[employee_collection_name]
    employees = collection_employees.find()
    return [Employee(**employee) for employee in employees]

# Mostrar un empleado específico
@employee_router.get("/{employee_id}", response_model=Employee, tags=["Employees"])
async def read_employee(employee_id: str, db = Depends(get_db)):
    collection_employees = db[employee_collection_name]
    employee = collection_employees.find_one({"_id": ObjectId(employee_id)})

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Convertir el _id a cadena y crear un objeto Employee
    employee["_id"] = str(employee["_id"])
    return Employee(**employee)

#Borrar empleado especifico
@employee_router.delete("/{employee_id}", response_model=Employee, tags=["Employees"])
async def delete_employee(employee_id: str, db = Depends(get_db)):
    # Buscar eventos en los que el empleado es organizador
    collection_events = db["eventos"]
    events_organized = list(collection_events.find({"organizer_id": employee_id}))
    collection_employees = db[employee_collection_name]
    result = collection_employees.delete_one({"_id": ObjectId(employee_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    for event in events_organized:
        collection_events.delete_one({"_id": event["_id"]})

    return {"message": "Empleado y eventos eliminados exitosamente"}
