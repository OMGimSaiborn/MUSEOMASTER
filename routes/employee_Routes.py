from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from bson import json_util
from models import BookingEmployee
from bson import ObjectId

app = APIRouter()

# Configura la conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["MUSEOMASTER"]
collection_employees = db["employees"]


# Ruta para eliminar un empleado
@app.delete("/delete_employee/{employee_id}")
async def delete_employee(employee_id: str):
    result = collection_employees.delete_one({"_id": ObjectId(employee_id)})

    if result.deleted_count > 0:
        return {"message": f"Empleado con ID {employee_id} eliminado exitosamente"}
    else:
        raise HTTPException(status_code=404, detail=f"No se encontró un empleado con ID {employee_id}")


