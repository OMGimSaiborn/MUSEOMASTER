from fastapi import APIRouter, HTTPException, Depends
from pymongo.collection import Collection
from models import Employee, EmployeeInDB, EmployeeCreateResponse
from bson import ObjectId
from db import get_db
from typing import List

employee_collection_name = "empleados"
event_collection_name = "eventos"

employee_router = APIRouter(prefix="/employees", tags=["Employees"])

def get_employees_collection(db=Depends(get_db)) -> Collection:
    return db[employee_collection_name]

def get_events_collection(db=Depends(get_db)) -> Collection:
    return db[event_collection_name]

#Crear empleado
@employee_router.post("/create", response_model=EmployeeCreateResponse)
def create_employee(
    employee: Employee,
    employees_collection: Collection = Depends(get_employees_collection),
):
    try:
        existing_employee = employees_collection.find_one({"name": employee.name})
        if existing_employee:
            raise HTTPException(
                status_code=400,
                detail=f"Employee with name '{employee.name}' already exists"
            )
        result = employees_collection.insert_one(employee.dict())
        employee_id = result.inserted_id
        created_employee = EmployeeInDB(_id=str(employee_id), **employee.dict())
        success_message = f"Employee '{employee.name}' created successfully."
        return EmployeeCreateResponse(message=success_message, employee=created_employee)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error creating employee")

# Obtener todos los empleados
@employee_router.get("/all", response_model=List[EmployeeInDB])
def get_all_employees(employees_collection: Collection = Depends(get_employees_collection)):
    try:
        employees = employees_collection.find()
        return [EmployeeInDB(**employee) for employee in employees]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error obteniendo empleados")

# Obtener detalles de un empleado específico
@employee_router.get("/{employee_id}", response_model=EmployeeInDB)
def get_employee(
    employee_id: str,
    employees_collection: Collection = Depends(get_employees_collection),
):
    try:
        employee_data = employees_collection.find_one({"_id": ObjectId(employee_id)})

        if not employee_data:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        employee_data["_id"] = str(employee_data["_id"])
        return EmployeeInDB(**employee_data)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error obteniendo empleado")

#Actualizar empleado
@employee_router.put("/{employee_id}", response_model=EmployeeInDB)
def update_employee(
    employee_id: str,
    updated_employee: Employee,
    employees_collection: Collection = Depends(get_employees_collection),
    events_collection: Collection = Depends(get_events_collection),
):
    try:
        existing_employee = employees_collection.find_one({"_id": ObjectId(employee_id)})
        if not existing_employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        result = employees_collection.update_one(
            {"_id": ObjectId(employee_id)},
            {"$set": updated_employee.dict()},
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Employee not found")
        updated_employee_data = employees_collection.find_one({"_id": ObjectId(employee_id)})
        updated_employee_data["_id"] = str(updated_employee_data["_id"])

        return EmployeeInDB(**updated_employee_data)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error updating employee")

#Borrar empleado
@employee_router.delete("/{employee_id}", response_model=dict)
def delete_employee(
    employee_id: str,
    employees_collection: Collection = Depends(get_employees_collection),
):
    try:
        existing_employee = employees_collection.find_one({"_id": ObjectId(employee_id)})
        if not existing_employee:
            raise HTTPException(status_code=404, detail="Employee not found")

        result = employees_collection.delete_one({"_id": ObjectId(employee_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Error deleting employee")

        return {"message": "Employee deleted successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error deleting employee")
